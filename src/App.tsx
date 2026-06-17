import { useEffect, useState, useMemo, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { listen } from "@tauri-apps/api/event";
import Dashboard from "./components/Dashboard";
import Overlay from "./components/Overlay";
import VignetteTest from "./components/VignetteTest";
import type { TaskKind } from "./probeTypes";
import "./App.css";

// Task C: session_meta の task_kind 宣言 (start 画面のセレクタ)。
const TASK_KINDS: { value: TaskKind; label: string }[] = [
  { value: "argumentative", label: "論述" },
  { value: "correspondence", label: "通信文" },
  { value: "creative", label: "創作" },
  { value: "vibe_coding", label: "vibe coding" },
];

interface CognitiveStateRaw {
  flow: number;
  incubation: number;
  stuck: number;
}

type InterventionAction = "none" | "nudge" | "wall" | "defer";

interface InterventionDecision {
  action: InterventionAction;
  need_score: number;
  opportunity_score: number;
  p_stuck: number;
  idle_ms: number;
  wall_accum_ms: number;
  reason: string;
  suppressed_by: string[];
}

const DEFAULT_INTERVENTION_DECISION: InterventionDecision = {
  action: "none",
  need_score: 0,
  opportunity_score: 0,
  p_stuck: 0,
  idle_ms: 0,
  wall_accum_ms: 0,
  reason: "safe_default",
  suppressed_by: [],
};

function App() {
  const [cognitiveState, setCognitiveState] = useState<CognitiveStateRaw>({
    flow: 0.80,
    incubation: 0.15,
    stuck: 0.05,
  });
  const [interventionDecision, setInterventionDecision] = useState<InterventionDecision>(
    DEFAULT_INTERVENTION_DECISION
  );
  const [isWallActive, setIsWallActive] = useState(false);
  const [isMonkMode, setIsMonkMode] = useState(false);
  // Overlay ウィンドウは start_session 時に動的生成されるため、
  // overlay なら最初からセッション開始済みとして扱う。
  const currentWindow = useMemo(() => getCurrentWindow(), []);
  const windowLabel = currentWindow.label;
  const [isStarted, setIsStarted] = useState(windowLabel === "overlay");
  const [keyboardIdleMs, setKeyboardIdleMs] = useState(0);
  const [hookActive, setHookActive] = useState<boolean | null>(null);
  const [startError, setStartError] = useState<string | null>(null);
  // Task C: session_meta 宣言 + ビネット導線。
  const [taskKind, setTaskKind] = useState<TaskKind>("argumentative");
  const [interventionEnabled, setInterventionEnabled] = useState(false);
  const [showVignette, setShowVignette] = useState(false);
  // v0.3 較正モード: 既定 ON。較正中はメイン画面からモデル出力 (推定状態/確率/GT) を隠し、
  // 主観回答 (criterion label) の測定独立性を守る。デバッグ/通常用途では OFF にできる。
  const [calibrationMode, setCalibrationMode] = useState(true);
  // Ref mirrors: setInterval 内からステート最新値を参照するため
  // (依存配列に含めるとintervalが破棄・再作成され、タイマー精度が低下する)
  const isWallActiveRef = useRef(isWallActive);
  const isMonkModeRef = useRef(isMonkMode);
  useEffect(() => { isWallActiveRef.current = isWallActive; }, [isWallActive]);
  useEffect(() => { isMonkModeRef.current = isMonkMode; }, [isMonkMode]);

  // D-1: currentWindow / windowLabel は isStarted 初期値算出のため上方で宣言済み

  // 2. Hook status: 継続的にポーリング（タップ無効化→自動復旧に追従）
  //    macOS では CGEventTap がスリープ復帰・権限変更時に無効化されることがある。
  //    バックエンドが自動復旧するため、フロントエンドも状態変化を継続監視する。
  //    旧実装では active 検知後にポーリングを停止していたが、inactive への遷移を
  //    検知できなかった。常時 3 秒間隔でポーリングを継続する。
  useEffect(() => {
    invoke<boolean>("get_hook_status")
      .then((active) => setHookActive(active))
      .catch(() => setHookActive(false));

    const interval = setInterval(() => {
      invoke<boolean>("get_hook_status")
        .then((active) => setHookActive(active))
        .catch(() => {});
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // 3. 統合ポーリング (500ms): cognitive state + keyboard idle + intervention decision
  //    単一の setInterval 内で Promise.all で並行取得し、同じブロック内で
  //    Rust 側の Opportunity 判定結果を UI に反映する。
  //    isWallActive/isMonkMode は Ref 経由で Rust に渡し、依存配列に含めない。
  //    これにより interval の破棄・再作成が発生せず、タイマー精度が向上する。
  useEffect(() => {
    if (!isStarted) return;

    const interval = setInterval(async () => {
      try {
        const [state, idle, decision] = await Promise.all([
          invoke<CognitiveStateRaw>("get_cognitive_state"),
          invoke<number>("get_keyboard_idle_ms"),
          invoke<InterventionDecision>("get_intervention_decision", {
            windowLabel,
            isMonkMode: isMonkModeRef.current,
            isWallActive: isWallActiveRef.current,
          }),
        ]);
        setCognitiveState(state);
        setKeyboardIdleMs(idle);
        setInterventionDecision(decision);

        if (decision.action === "wall" && !isWallActiveRef.current) {
          setIsWallActive(true);
        }
      } catch (e) {
        console.error("Failed to fetch state:", e);
        setCognitiveState({ flow: 1.0, incubation: 0.0, stuck: 0.0 });
        setInterventionDecision(DEFAULT_INTERVENTION_DECISION);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [isStarted, windowLabel]);

  // 4. Sensor Integration (Unlock Logic)
  //    Wall解除後にメインウィンドウをフォーカス:
  //    オーバーレイが透過に戻っても、ユーザーがクリックしないと
  //    メインウィンドウに操作が戻らないため、自動でフォーカスする。
  useEffect(() => {
    const unlisten = listen("sensor-accelerometer", (event) => {
      if (event.payload === "move") {
        setIsWallActive(false);
        // メインウィンドウ側でのみフォーカスを取り直す
        if (windowLabel !== "overlay") {
          currentWindow.setFocus().catch(() => {});
        }
      }
    });

    return () => {
      unlisten.then((f) => f());
    };
  }, [windowLabel, currentWindow]);

  // 5. Monk Mode: Dashboard のトグルから monk-mode-changed を受け取り isMonkMode を更新。
  //    両ウィンドウ(main/overlay)がこのイベントをリッスンし状態を同期する。
  //    Monk Mode ON 時は LV2 Wall タイマーが無効化される。
  useEffect(() => {
    const unlisten = listen("monk-mode-changed", (event) => {
      setIsMonkMode(event.payload as boolean);
    });

    return () => {
      unlisten.then((f) => f());
    };
  }, []);

  // 6-7. (削除) Overlay は start_session 時に Rust 側で動的生成されるため、
  // session-started イベント購読と window.show() は不要。

  // Render based on Window Label
  if (windowLabel === "overlay") {
    return (
      <Overlay
        interventionDecision={interventionDecision}
        isWallActive={isWallActive}
      />
    );
  }

  const handleQuit = () => {
    invoke("quit_app").catch(console.error);
  };

  const handleStart = async () => {
    setStartError(null);
    try {
      await invoke("start_session");
    } catch (e) {
      console.error("Failed to start session:", e);
      setStartError("セッション開始に失敗しました。アプリを再起動してください。");
      return;
    }
    // Task C: セッション開始宣言を記録 (track は較正スモークでは main 固定)。
    try {
      await invoke("record_session_meta", {
        track: "main",
        taskKind,
        monkMode: isMonkMode,
        interventionEnabled,
      });
    } catch (e) {
      console.error("record_session_meta failed:", e);
    }
    setIsStarted(true);
  };

  // Task C: 尺度理解テスト (ビネット) フロー
  if (!isStarted && showVignette) {
    return <VignetteTest onComplete={() => setShowVignette(false)} />;
  }

  // セッション未開始時はスタート画面を表示
  if (!isStarted) {
    return (
      <div className="start-screen">
        <img src="/doe.svg" alt="GSE Logo" className="start-logo" />
        <div className="start-header">
          <h1>Generative Struggle Engine</h1>
          <p className="start-description">
            キーストロークを解析し、介入判断に必要な作業状態をリアルタイムで推定します。
          </p>
        </div>

        {/* Task C: session_meta の task_kind 宣言 */}
        <div style={{ margin: "1rem 0" }}>
          <div style={{ fontSize: "0.85rem", marginBottom: "0.4rem" }}>今回の作業種別:</div>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "center" }}>
            {TASK_KINDS.map((tk) => (
              <button
                key={tk.value}
                onClick={() => setTaskKind(tk.value)}
                style={{
                  padding: "0.4rem 0.8rem",
                  cursor: "pointer",
                  borderRadius: "6px",
                  border: taskKind === tk.value ? "2px solid #4caf50" : "1px solid #888",
                  background: taskKind === tk.value ? "rgba(76,175,80,0.15)" : "transparent",
                }}
              >
                {tk.label}
              </button>
            ))}
          </div>
          <label style={{ display: "block", marginTop: "0.6rem", fontSize: "0.82rem" }}>
            <input
              type="checkbox"
              checked={interventionEnabled}
              onChange={(e) => setInterventionEnabled(e.target.checked)}
            />{" "}
            介入を有効にする (較正中は既定オフ)
          </label>
          <label style={{ display: "block", marginTop: "0.4rem", fontSize: "0.82rem" }}>
            <input
              type="checkbox"
              checked={calibrationMode}
              onChange={(e) => setCalibrationMode(e.target.checked)}
            />{" "}
            較正モード (モデル出力を非表示・既定オン)
          </label>
        </div>

        <button className="start-button" onClick={handleStart}>
          開始する
        </button>
        <button
          className="start-button"
          onClick={() => setShowVignette(true)}
          style={{ background: "transparent", border: "1px solid #888", marginTop: "0.5rem" }}
        >
          尺度理解テスト (初回)
        </button>
        {startError && (
          <p className="start-error" style={{ color: '#ff6b6b', marginTop: '0.5rem', fontSize: '0.9rem' }}>
            {startError}
          </p>
        )}
        <p className="start-hint">
          自然にタイピングを始めると、検知が動作します。
        </p>
      </div>
    );
  }

  // Default to Main Dashboard (較正モード時は blind/minimal 表示)
  return (
    <Dashboard cognitiveState={cognitiveState} onQuit={handleQuit} isMonkMode={isMonkMode} keyboardIdleMs={keyboardIdleMs} hookActive={hookActive} calibrationMode={calibrationMode} interventionEnabled={interventionEnabled} />
  );
}

export default App;
