import { useEffect, useState, useMemo } from "react";
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

function App() {
  const [windowLabel, setWindowLabel] = useState<string>("");
  const [cognitiveState, setCognitiveState] = useState<CognitiveStateRaw>({
    flow: 0.1,
    incubation: 0.1,
    stuck: 0.0, // Default to neutral/low stuck
  });
  const [isWallActive, setIsWallActive] = useState(false);

  // D-1: Memoize getCurrentWindow (Performance Optimization)
  const appWindow = useMemo(() => getCurrentWindow(), []);

  // 1. Identify Window Label
  useEffect(() => {
    const label = appWindow.label;
    setWindowLabel(label);
    console.log("Window Label:", label);
  }, [appWindow]);

  // 2. Poll Cognitive State (Every 500ms)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const state = await invoke<CognitiveStateRaw>("get_cognitive_state");
        setCognitiveState(state);
      } catch (e) {
        console.error("Failed to fetch state:", e);
      }
    }, 500);

    return () => clearInterval(interval);
  }, []);

  // 3. Intervention Logic (D-2/D-3)
  // Lv2 (Mist): Stuck > 0.7 for 30s.
  // Note: 'isWallActive' currently toggles the Overlay component which handles the Mist effect.
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    
    // Check if Stuck state is dominant/high
    if (cognitiveState.stuck > 0.7) {
      if (!isWallActive) {
        // If Stuck stays high for 30 seconds, activate Mist (Lv2)
        timer = setTimeout(() => {
          setIsWallActive(true);
        }, 30000); // 30 seconds
      }
    } else {
        // Reset if stuck drops below threshold
        // Optional: Add hysteresis (e.g. drop below 0.5 to clear)
        if (isWallActive) {
            setIsWallActive(false);
        }
    }
    return () => clearTimeout(timer);
  }, [cognitiveState.stuck, isWallActive]);

  // 4. Sensor Integration (Unlock Logic)
  useEffect(() => {
    const unlisten = listen("sensor-accelerometer", (event) => {
      console.log("Sensor Event:", event.payload);
      if (event.payload === "move") {
        setIsWallActive(false);
      }
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

  // Default to Main Dashboard
  return (
    <Dashboard cognitiveState={cognitiveState} />
  );
}

export default App;
