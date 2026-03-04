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
// Lv2トリガー閾値: Wallは stuck>0.7 が 30秒継続した際に表示
const LV2_STUCK_THRESHOLD = 0.7;
const LV2_TIMER_MS = 30_000;

function App() {
  const [cognitiveState, setCognitiveState] = useState<CognitiveStateRaw>({
    flow: 0.1,
    incubation: 0.1,
    stuck: 0.8,
  });
  const [isWallActive, setIsWallActive] = useState(false);
  const [isMonkMode, setIsMonkMode] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

  // 3. Intervention Layer ロジック
  //    D-2: Lv1 (Nudge) は Overlay.tsx 側で stuck>0.6 時に即時表示済み
  //    D-3: Lv2 (Ambient Fade/Wall) は stuck>LV2_STUCK_THRESHOLD が LV2_TIMER_MS 継続で発動
  //    useRef でタイマー参照を保持し、ポーリング更新のたびにリセットされる問題を修正
  useEffect(() => {
    if (cognitiveState.stuck > LV2_STUCK_THRESHOLD && !isWallActive && !isMonkMode) {
      // 閾値超過中かつタイマー未設定のときのみ新規タイマーを立てる
      if (!timerRef.current) {
        timerRef.current = setTimeout(() => {
          timerRef.current = null;
          setIsWallActive(true);
        }, LV2_TIMER_MS);
      }
    } else {
      // 閾値を下回った or Wall 解除 or Monk Mode ON → タイマーキャンセル
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    }
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
