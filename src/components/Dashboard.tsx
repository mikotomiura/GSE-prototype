import React, { useEffect, useState, useRef } from 'react';
import { emit } from "@tauri-apps/api/event";

interface DashboardProps {
  cognitiveState: {
    flow: number;
    incubation: number;
    stuck: number;
  };
  onQuit: () => void;
  isMonkMode: boolean;
  keyboardIdleMs: number;
  hookActive: boolean | null;
}

const Dashboard: React.FC<DashboardProps> = ({ cognitiveState, onQuit, isMonkMode, keyboardIdleMs, hookActive }) => {
  // セッション経過時間 (ストップウォッチ)
  const sessionStartRef = useRef(Date.now());
  const [sessionSeconds, setSessionSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSessionSeconds(Math.floor((Date.now() - sessionStartRef.current) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const getMaxState = () => {
    const { flow, incubation, stuck } = cognitiveState;
    if (flow >= incubation && flow >= stuck) return 'Flow';
    if (incubation >= flow && incubation >= stuck) return 'Incubation';
    return 'Stuck';
  };

  const dominant = getMaxState();

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${m}:${String(s).padStart(2, '0')}`;
  };

  // 3秒以内に打鍵があれば "Active"、それ以上なら経過秒数を表示
  const keyIsActive = keyboardIdleMs > 0 && keyboardIdleMs < 3000;
  const keyStatusLabel =
    keyboardIdleMs === 0
      ? '---'
      : keyIsActive
      ? 'Active'
      : `Idle ${Math.floor(keyboardIdleMs / 1000)}s`;

  const handleMonkModeToggle = () => {
    // Monk Mode トグル: ON/OFF を broadcast → 両ウィンドウが isMonkMode を同期
    // ON 時は LV2 Wall タイマーが無効化される
    emit("monk-mode-changed", !isMonkMode).catch(() => {});
  };

  return (
    <div className={`dashboard-container state-${dominant.toLowerCase()}`}>
      <h2>Generative Struggle Engine</h2>

      {/* Input Monitoring 権限警告 (macOS向け。Windowsでは hookActive は常に true) */}
      {hookActive === false && (
        <div className="hook-warning-banner">
          ⚠ Input Monitoring 権限が必要です
        </div>
      )}

      {/* セッション情報バー: ストップウォッチ + キーボード状態 */}
      <div className="session-bar">
        <div className="session-item">
          <span className="session-label">Session</span>
          <span className="session-value">{formatTime(sessionSeconds)}</span>
        </div>
        <div className="session-item">
          <span className="session-label">Keyboard</span>
          <span className={`session-value kbd-status ${keyIsActive ? 'kbd-active' : 'kbd-idle'}`}>
            {keyStatusLabel}
          </span>
        </div>
      </div>

      <div className="state-card">
        <h3>Current State: <span className="dominant-state">{dominant}</span></h3>
      </div>

      <div className="metrics-container">
        <div className="metric-row">
          <label>Flow</label>
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill flow"
              style={{ width: `${cognitiveState.flow * 100}%` }}
            ></div>
          </div>
          <span>{(cognitiveState.flow * 100).toFixed(1)}%</span>
        </div>

        <div className="metric-row">
          <label>Incubation</label>
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill incubation"
              style={{ width: `${cognitiveState.incubation * 100}%` }}
            ></div>
          </div>
          <span>{(cognitiveState.incubation * 100).toFixed(1)}%</span>
        </div>

        <div className="metric-row">
          <label>Stuck</label>
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill stuck"
              style={{ width: `${cognitiveState.stuck * 100}%` }}
            ></div>
          </div>
          <span>{(cognitiveState.stuck * 100).toFixed(1)}%</span>
        </div>
      </div>

      {/* Monk Mode トグル: ON=Wall無効, OFF=通常 */}
      <button
        className={`monk-mode-toggle ${isMonkMode ? 'on' : 'off'}`}
        onClick={handleMonkModeToggle}
      >
        <span>{isMonkMode ? 'Monk Mode: ON' : 'Monk Mode: OFF'}</span>
        <span className="monk-mode-label">
          {isMonkMode ? 'Wall intervention disabled' : 'Wall intervention active'}
        </span>
      </button>

      <div className="info-box">
        <p>Type naturally. The engine analyzes your keystroke dynamics.</p>
        <p><strong>Incubation</strong> suggests pausing. <strong>Stuck</strong> suggests moving.</p>
      </div>

      <button className="quit-button" onClick={onQuit}>
        セッション終了
      </button>
    </div>
  );
};

export default Dashboard;
