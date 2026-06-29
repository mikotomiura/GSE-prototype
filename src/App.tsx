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
// Phase1 ロック: 較正は **論述 (argumentative) に固定**する。非論述を混ぜると C-index が
// タスク種別で交絡するため (Phase1 実行可否レビューのブロッカー #2)。Phase1 完了後に
// 他種別へ広げる時は下のコメントアウトを戻す (型 TaskKind は 4 種を保持・backend は不変)。
const TASK_KINDS: { value: TaskKind; label: string }[] = [
  { value: "argumentative", label: "論述" },
  // --- Phase1 較正中はロックのため非表示 (復活させる時はコメントを外す) ---
  // { value: "correspondence", label: "通信文" },
  // { value: "creative", label: "創作" },
  // { value: "vibe_coding", label: "vibe coding" },
];

// Phase 1 の 2 相プロトコル週セレクタ (tasklist #A / decisions FD2)。
// 介入有効化・較正モード・condition・label_pool を 1 つの選択にまとめ、不整合な組合せ
// (例: 介入 ON なのに calibration_blind プール) を構造的に表現不能にする。各 condition /
// label_pool 文字列は backend の Condition / LabelPool enum (logger.rs) と同期。
type PhaseWeek = "week1_blind" | "week2_intervention";

interface WeekConfig {
  value: PhaseWeek;
  label: string;
  description: string;
  /** session_meta.intervention_enabled。false で backend が全介入を gate (lib.rs safe_default)。 */
  interventionEnabled: boolean;
  /** 較正モード = モデル出力を非表示にし主観回答の測定独立性を守る。 */
  calibrationMode: boolean;
  /** backend Condition enum と同期 (blind_calibration / baseline)。 */
  condition: "blind_calibration" | "baseline";
  /** backend LabelPool enum と同期。X1 判定は calibration_blind のみ使用。 */
  labelPool: "calibration_blind" | "post_intervention";
}

const PHASE_WEEKS: WeekConfig[] = [
  {
    value: "week1_blind",
    label: "第1週 (blind 較正)",
    description: "介入は発火せず推定状態も非表示。X1 較正ラベルを収集 (calibration_blind)。",
    interventionEnabled: false,
    calibrationMode: true,
    condition: "blind_calibration",
    labelPool: "calibration_blind",
  },
  {
    value: "week2_intervention",
    label: "第2週 (介入)",
    description: "Wall + 2分タイマーが実発火。介入下のラベルを別プールで収集 (post_intervention)。",
    interventionEnabled: true,
    calibrationMode: false,
    condition: "baseline",
    labelPool: "post_intervention",
  },
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
  const [showVignette, setShowVignette] = useState(false);
  // Phase 1 の 2 相プロトコル週セレクタ (tasklist #A / FD2)。既定は第1週 (blind 較正)。
  // 介入有効化・較正モード・condition・label_pool はこの 1 選択から派生し、開始後はスタート
  // 画面を離れるためセッション中は変更できない (実質ロック)。
  const [phaseWeek, setPhaseWeek] = useState<PhaseWeek>("week1_blind");
  // phaseWeek は PhaseWeek 型で PHASE_WEEKS を必ず網羅するため find は非 undefined。
  // 黙った `?? PHASE_WEEKS[0]` フォールバックは（万一の不整合時に）week1 blind 較正へ
  // 静かに倒れて汚染を隠すため使わない。不変条件を型で表明し、破れれば下の分割代入で fail-loud に落とす（FD7 思想）。
  const weekConfig = PHASE_WEEKS.find((w) => w.value === phaseWeek)!;
  // 派生値: Dashboard 表示制御と session_meta 記録に使う。週セレクタが唯一の真実源。
  const { interventionEnabled, calibrationMode } = weekConfig;
  // Ref mirrors: setInterval 内からステート最新値を参照するため
  // (依存配列に含めるとintervalが破棄・再作成され、タイマー精度が低下する)
  const isWallActiveRef = useRef(isWallActive);
  const isMonkModeRef = useRef(isMonkMode);
  // Wall を「1 エピソードにつき 1 回だけ」起動するためのエッジ検出フラグ。
  // 解除 (sensor-accelerometer) 後も判定が "wall" のまま lingering する
  // (特に overlay は last_decision を読む) ため、これが無いと毎ポーリングで再起動してしまう。
  const wallHandledRef = useRef(false);
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

        // Wall は新エピソードの立ち上がり (非 wall → wall) でのみ起動する。
        // 解除後も判定が "wall" のまま続く (overlay は last_decision を読むため lingering)
        // ケースで毎回再発火していたのを、wallHandledRef のエッジ検出で防ぐ。
        if (decision.action === "wall") {
          if (!isWallActiveRef.current && !wallHandledRef.current) {
            wallHandledRef.current = true;
            setIsWallActive(true);
          }
        } else {
          // 判定が wall を離れたら次のエピソードを許可する (cooldown 明け等)。
          wallHandledRef.current = false;
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
    // Task C / tasklist #A: セッション開始宣言を記録 (track は較正スモークでは main 固定)。
    // condition / label_pool (WBS 0.11 / 0.4) は週セレクタ (weekConfig) が一括決定する。
    // 第1週=blind_calibration / calibration_blind (X1 判定はこのプールのみ使用)、
    // 第2週=baseline / post_intervention (合算せず別管理)。組合せは型で固定済み。
    // NOTE: Phase 2 AB/BA (a|b) と Phase 3 MRT (nudge|defer) の condition 配線は
    // それぞれの割付実装時に行う (本タスクは enum 凍結のみ。decisions CD8)。
    try {
      await invoke("record_session_meta", {
        track: "main",
        taskKind,
        monkMode: isMonkMode,
        interventionEnabled,
        condition: weekConfig.condition,
        labelPool: weekConfig.labelPool,
      });
    } catch (e) {
      // 週セレクタが運ぶ condition/label_pool は X1 プール分離 (FD3) の真値タグであり、
      // intervention_enabled は backend のグローバル介入ゲートを設定する。記録に失敗した
      // まま Dashboard へ進むと、タグ欠落かつ INTERVENTION_ENABLED が前セッションの値の
      // ままになり blind 較正が汚染されうる。ここで停止しユーザーに再開を促す。
      console.error("record_session_meta failed:", e);
      setStartError("セッション情報の記録に失敗しました。もう一度開始してください。");
      return;
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
          <div style={{ fontSize: "0.85rem", marginBottom: "0.4rem" }}>今回の作業種別（Phase1 は論述に固定）:</div>
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
          {/* tasklist #A: Phase 1 2 相プロトコルの週セレクタ。介入 ON/OFF・較正モード・
              condition・label_pool を 1 つの選択にまとめ、不整合な組合せを選べなくする。 */}
          <div style={{ marginTop: "1rem" }}>
            <div style={{ fontSize: "0.85rem", marginBottom: "0.4rem" }}>今回の実施週:</div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "center" }}>
              {PHASE_WEEKS.map((w) => (
                <button
                  key={w.value}
                  onClick={() => setPhaseWeek(w.value)}
                  aria-pressed={phaseWeek === w.value}
                  style={{
                    padding: "0.4rem 0.8rem",
                    cursor: "pointer",
                    borderRadius: "6px",
                    border: phaseWeek === w.value ? "2px solid #4caf50" : "1px solid #888",
                    background: phaseWeek === w.value ? "rgba(76,175,80,0.15)" : "transparent",
                  }}
                >
                  {w.label}
                </button>
              ))}
            </div>
            <p style={{ marginTop: "0.5rem", fontSize: "0.78rem", opacity: 0.8 }}>
              {weekConfig.description}
            </p>
          </div>
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
  // onBack: アプリを終了せずスタート画面へ戻る (作業種別の変更・尺度理解テスト・再開のため)。
  //   戻る瞬間に Wall が出ていたら overlay が残らないよう介入もクリアする。
  const handleBack = () => {
    setIsWallActive(false);
    setIsStarted(false);
  };
  return (
    <Dashboard cognitiveState={cognitiveState} onQuit={handleQuit} onBack={handleBack} isMonkMode={isMonkMode} keyboardIdleMs={keyboardIdleMs} hookActive={hookActive} calibrationMode={calibrationMode} interventionEnabled={interventionEnabled} />
  );
}

export default App;
