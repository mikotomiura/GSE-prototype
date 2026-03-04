import { useEffect, useState, useMemo, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { listen } from "@tauri-apps/api/event";
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
  // advice.md §C: 累積タイマー (連続ではなく累積 30 秒で Wall 発動)
  const stuckAccumMsRef = useRef<number>(0);
  const lastStuckTickRef = useRef<number>(Date.now());

  // D-1: getCurrentWindow() を useMemo でメモ化し不要な再生成を防止
  const currentWindow = useMemo(() => getCurrentWindow(), []);
  const windowLabel = currentWindow.label;

  // 2. Poll Cognitive State (Every 500ms)
  //    オーバーレイウィンドウは常時ポーリング。メインウィンドウはセッション開始後のみ。
  useEffect(() => {
    if (windowLabel !== "overlay" && !isStarted) return;

    const interval = setInterval(async () => {
      try {
        const state = await invoke<CognitiveStateRaw>("get_cognitive_state");
        setCognitiveState(state);
      } catch (e) {
        console.error("Failed to fetch state:", e);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [isStarted, windowLabel]);

  // 3. Intervention Layer ロジック (advice.md §C 累積タイマー)
  //    D-2: Lv1 (Nudge) は Overlay.tsx 側で stuck>0.6 時に即時表示済み
  //    D-3: Lv2 (Wall) は stuck>LV2_STUCK_THRESHOLD の累積時間が LV2_TIMER_MS に達したら発動
  //    「連続 30 秒」ではなく「累積 30 秒」: 一瞬閾値を下回っても即リセットされない。
  //    stuck < LV2_SLACK_THRESHOLD に落ちた場合のみ累積を 2× 速度で減衰させる。
  //    0.5 ≤ stuck ≤ 0.7 の範囲は「遊び」として累積を凍結（増加も減衰もしない）。
  useEffect(() => {
    const now = Date.now();
    const elapsed = now - lastStuckTickRef.current;
    lastStuckTickRef.current = now;

    // Wall 発動中 or Monk Mode ON: 累積リセット
    if (isWallActive || isMonkMode) {
      stuckAccumMsRef.current = 0;
      return;
    }

    if (cognitiveState.stuck > LV2_STUCK_THRESHOLD) {
      stuckAccumMsRef.current = Math.min(stuckAccumMsRef.current + elapsed, LV2_TIMER_MS);
      if (stuckAccumMsRef.current >= LV2_TIMER_MS) {
        stuckAccumMsRef.current = 0;
        setIsWallActive(true);
      }
    } else if (cognitiveState.stuck < LV2_SLACK_THRESHOLD) {
      // 閾値を大きく下回った場合: 2× 速度で減衰
      stuckAccumMsRef.current = Math.max(0, stuckAccumMsRef.current - elapsed * 2);
    }
    // LV2_SLACK_THRESHOLD ≤ stuck ≤ LV2_STUCK_THRESHOLD: 凍結（変化なし）
  }, [cognitiveState.stuck, isWallActive, isMonkMode]);

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
    }
    setIsStarted(true);
  };

  // セッション未開始時はスタート画面を表示
  if (!isStarted) {
    return (
      <div className="start-screen">
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
    <Dashboard cognitiveState={cognitiveState} onQuit={handleQuit} isMonkMode={isMonkMode} />
  );
}

export default App;
