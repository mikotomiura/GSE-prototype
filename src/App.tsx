import { useEffect, useState, useMemo, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { listen, emit } from "@tauri-apps/api/event";
import Dashboard from "./components/Dashboard";
import Overlay from "./components/Overlay";
import "./App.css";

interface CognitiveStateRaw {
  flow: number;
  incubation: number;
  stuck: number;
}

// Lv1トリガー閾値: NudgeはOverlay.tsxで stuck>0.6 時に表示
// Lv2トリガー閾値: Wallは stuck>0.7 の累積時間が 30秒に達した際に表示 (advice.md §C)
// LV2_SLACK_THRESHOLD: 0.5 未満に落ちた場合のみ累積タイマーを減衰させる
const LV2_STUCK_THRESHOLD = 0.7;
const LV2_SLACK_THRESHOLD = 0.5;
const LV2_TIMER_MS = 30_000;

function App() {
  const [cognitiveState, setCognitiveState] = useState<CognitiveStateRaw>({
    flow: 0.80,
    incubation: 0.15,
    stuck: 0.05,
  });
  const [isWallActive, setIsWallActive] = useState(false);
  const [isMonkMode, setIsMonkMode] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [keyboardIdleMs, setKeyboardIdleMs] = useState(0);
  const [hookActive, setHookActive] = useState<boolean | null>(null);
  // advice.md §C: 累積タイマー (連続ではなく累積 30 秒で Wall 発動)
  const stuckAccumMsRef = useRef<number>(0);
  const lastStuckTickRef = useRef<number>(Date.now());
  // Ref mirrors: setInterval 内からステート最新値を参照するため
  // (依存配列に含めるとintervalが破棄・再作成され、タイマー精度が低下する)
  const isWallActiveRef = useRef(isWallActive);
  const isMonkModeRef = useRef(isMonkMode);
  useEffect(() => { isWallActiveRef.current = isWallActive; }, [isWallActive]);
  useEffect(() => { isMonkModeRef.current = isMonkMode; }, [isMonkMode]);

  // D-1: getCurrentWindow() を useMemo でメモ化し不要な再生成を防止
  const currentWindow = useMemo(() => getCurrentWindow(), []);
  const windowLabel = currentWindow.label;

  // 2. Hook status: マウント時に1回だけ取得（実行中に変わらない値）
  useEffect(() => {
    invoke<boolean>("get_hook_status")
      .then((active) => setHookActive(active))
      .catch(() => setHookActive(false)); // エラー時は悲観的に false（権限バナーを表示）
  }, []);

  // 3. 統合ポーリング (500ms): cognitive state + keyboard idle + Lv2 累積タイマー
  //    単一の setInterval 内で Promise.all で並行取得し、同じブロック内で
  //    Date.now() ベースの正確な elapsed を用いて Lv2 タイマーを更新する。
  //    isWallActive/isMonkMode は Ref 経由で参照し、依存配列に含めない。
  //    これにより interval の破棄・再作成が発生せず、タイマー精度が向上する。
  useEffect(() => {
    if (!isStarted) return;
    lastStuckTickRef.current = Date.now();

    const interval = setInterval(async () => {
      try {
        const [state, idle] = await Promise.all([
          invoke<CognitiveStateRaw>("get_cognitive_state"),
          invoke<number>("get_keyboard_idle_ms"),
        ]);
        setCognitiveState(state);
        setKeyboardIdleMs(idle);

        // --- Lv2 累積タイマー (同ブロック内で Date.now() ベース算出) ---
        const now = Date.now();
        const elapsed = now - lastStuckTickRef.current;
        lastStuckTickRef.current = now;

        if (!isWallActiveRef.current && !isMonkModeRef.current) {
          if (state.stuck > LV2_STUCK_THRESHOLD) {
            stuckAccumMsRef.current += elapsed;
            if (stuckAccumMsRef.current >= LV2_TIMER_MS) {
              stuckAccumMsRef.current = 0;
              setIsWallActive(true);
            }
          } else if (state.stuck < LV2_SLACK_THRESHOLD) {
            // 閾値を大きく下回った場合: 2× 速度で減衰
            stuckAccumMsRef.current = Math.max(0, stuckAccumMsRef.current - elapsed * 2);
          }
          // LV2_SLACK_THRESHOLD ≤ stuck ≤ LV2_STUCK_THRESHOLD: 凍結（変化なし）
        } else {
          stuckAccumMsRef.current = 0;
        }
      } catch (e) {
        console.error("Failed to fetch state:", e);
        setCognitiveState({ flow: 1.0, incubation: 0.0, stuck: 0.0 });
        stuckAccumMsRef.current = 0;
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

  // 6. Overlay: セッション開始イベントを購読し isStarted を同期
  useEffect(() => {
    if (windowLabel !== "overlay") return;
    const unlisten = listen("session-started", () => setIsStarted(true));
    return () => { unlisten.then((f) => f()); };
  }, [windowLabel]);

  // 7. Overlay: セッション開始時にウィンドウを表示 (初期状態 visible:false)
  useEffect(() => {
    if (windowLabel === "overlay" && isStarted) {
      currentWindow.show().catch(() => {});
    }
  }, [windowLabel, isStarted, currentWindow]);

  // Render based on Window Label
  if (windowLabel === "overlay") {
    return (
      <Overlay
        stuckProb={cognitiveState.stuck}
        isWallActive={isWallActive}
      />
    );
  }

  const handleQuit = () => {
    invoke("quit_app").catch(console.error);
  };

  const handleStart = async () => {
    try {
      await invoke("start_session");
    } catch (e) {
      console.error("Failed to start session:", e);
      return;
    }
    setIsStarted(true);
    emit("session-started");
  };

  // セッション未開始時はスタート画面を表示
  if (!isStarted) {
    return (
      <div className="start-screen">
        <img src="/doe.svg" alt="GSE Logo" className="start-logo" />
        <div className="start-header">
          <h1>Generative Struggle Engine</h1>
          <p className="start-description">
            キーストロークを解析し、あなたの認知状態をリアルタイムで推定します。
          </p>
        </div>
        <button className="start-button" onClick={handleStart}>
          開始する
        </button>
        <p className="start-hint">
          自然にタイピングを始めると、検知が動作します。
        </p>
      </div>
    );
  }

  // Default to Main Dashboard
  return (
    <Dashboard cognitiveState={cognitiveState} onQuit={handleQuit} isMonkMode={isMonkMode} keyboardIdleMs={keyboardIdleMs} hookActive={hookActive} />
  );
}

export default App;
