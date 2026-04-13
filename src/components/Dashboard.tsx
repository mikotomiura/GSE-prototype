import React, { useEffect, useState, useRef } from 'react';
import { invoke } from "@tauri-apps/api/core";
import { emit } from "@tauri-apps/api/event";

interface DiagnosticInfo {
  hook_active: string;
  last_key_ms: string;
  os: string;
  arch: string;
  version: string;
  input_monitoring_granted?: string;
  ax_is_trusted?: string;
  callback_count?: string;
  consecutive_tap_failures?: string;
  using_accessibility_fallback?: string;
  bundle_path?: string;
  quarantine_present?: string;
  codesign_valid?: string;
}

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
  // hookActive=false が続いた秒数 (権限バナーの段階的メッセージ表示に使用)
  const [hookWaitingSec, setHookWaitingSec] = useState(0);
  // 診断情報 (トラブルシューティング用)
  const [diagnostics, setDiagnostics] = useState<DiagnosticInfo | null>(null);
  // TCC リセット実行結果メッセージ
  const [resetResult, setResetResult] = useState<string | null>(null);
  // 診断コピー済みフラグ
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setSessionSeconds(Math.floor((Date.now() - sessionStartRef.current) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // hookActive=false の間、経過秒数をカウントする。
  // 30秒経過後に段階的ガイダンスを追加表示する。
  useEffect(() => {
    if (hookActive !== false) {
      setHookWaitingSec(0);
      return;
    }
    const interval = setInterval(() => {
      setHookWaitingSec(s => s + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [hookActive]);

  // macOS: 30秒経過で自動的に診断情報を取得（60s の条件分岐メッセージに必要）
  // === 30 ではなく >= 30 を使用（タイマー tick 飛び対策）
  useEffect(() => {
    if (hookWaitingSec >= 30 && !diagnostics) {
      invoke<DiagnosticInfo>("get_diagnostics")
        .then(d => setDiagnostics(d))
        .catch(() => {});
    }
  }, [hookWaitingSec, diagnostics]);

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

      {/* キーボードフック状態警告 (両プラットフォーム共通) */}
      {hookActive === false && (
        <div className="permission-banner">
          <span className="permission-icon">⚠️</span>
          <div className="permission-text">
            {navigator.platform.startsWith('Mac') ? (
              <>
                {diagnostics?.using_accessibility_fallback === 'true' ? (
                  <>
                    <strong>Accessibility 権限が必要です</strong>
                    <p>
                      入力監視の権限取得に失敗したため、アクセシビリティ権限に切り替えました。<br />
                      <em>System Settings › プライバシーとセキュリティ › アクセシビリティ</em> で
                      <strong> gse-next </strong>にチェックを入れてください。
                    </p>
                    {hookWaitingSec >= 30 && (
                      <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.9 }}>
                        gse-next が既にチェック済みの場合は、<strong>一度オフにしてからオンに戻して</strong>ください。
                      </p>
                    )}
                  </>
                ) : (
                  <>
                    <strong>Input Monitoring 権限が必要です</strong>
                    <p>
                      System Settings が自動で開かれました。<br />
                      <em>プライバシーとセキュリティ › 入力監視</em> で
                      <strong> gse-next </strong>にチェックを入れてください。
                      権限が付与されると自動的に検知が開始されます。
                    </p>
                    {hookWaitingSec >= 30 && (
                      <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.9 }}>
                        gse-next が既にチェック済みの場合は、<strong>一度オフにしてからオンに戻して</strong>ください。
                        アップデート後はセキュリティ署名が変わるため、再設定が必要です。
                      </p>
                    )}
                    {hookWaitingSec >= 60 && (() => {
                      if (diagnostics?.codesign_valid === 'false') return (
                        <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.9 }}>
                          コード署名が無効です。ターミナルで以下を実行してください:<br />
                          <code style={{ fontSize: '0.8rem', background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '3px' }}>
                            codesign --force --sign - /Applications/gse-next.app
                          </code><br />
                          その後アプリを再起動してください。
                        </p>
                      );
                      if (diagnostics?.quarantine_present === 'true') return (
                        <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.9 }}>
                          quarantine 属性が残っています。ターミナルで以下を実行してください:<br />
                          <code style={{ fontSize: '0.8rem', background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '3px' }}>
                            xattr -dr com.apple.quarantine /Applications/gse-next.app
                          </code><br />
                          その後アプリを再起動してください。
                        </p>
                      );
                      return (
                        <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.9 }}>
                          約20秒後にアクセシビリティ権限へ自動切替されます。それまでお待ちください。
                        </p>
                      );
                    })()}
                  </>
                )}
                {hookWaitingSec >= 90 && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <button
                      style={{ fontSize: '0.8rem', padding: '4px 10px', cursor: 'pointer', marginRight: '0.5rem' }}
                      onClick={() => {
                        if (!window.confirm('全アプリの入力監視権限がリセットされます。続行しますか？')) return;
                        invoke<string>("reset_input_monitoring")
                          .then(msg => setResetResult(msg))
                          .catch(e => setResetResult(`Error: ${e}`));
                      }}
                    >
                      権限をリセット
                    </button>
                    {resetResult && (
                      <p style={{ marginTop: '0.3rem', fontSize: '0.75rem', opacity: 0.8 }}>
                        {resetResult}
                      </p>
                    )}
                  </div>
                )}
              </>
            ) : (
              <>
                <strong>キーボード検知の初期化に失敗しました</strong>
                <p>
                  キーボードフックのインストールに失敗しました。自動的に再試行しています。
                </p>
                {hookWaitingSec >= 10 && (
                  <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.9 }}>
                    解決しない場合は、<strong>アプリを再起動</strong>してください。
                    セキュリティソフトがキーボードフックをブロックしている可能性があります。
                  </p>
                )}
                {hookWaitingSec >= 30 && (
                  <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.9 }}>
                    Smart App Control が有効な場合:<br />
                    <em>設定 › プライバシーとセキュリティ › Windows セキュリティ ›
                    アプリとブラウザーコントロール</em> で確認してください。
                  </p>
                )}
              </>
            )}
            {hookWaitingSec >= 20 && !diagnostics && (
              <button
                style={{ marginTop: '0.5rem', fontSize: '0.8rem', padding: '4px 10px', cursor: 'pointer' }}
                onClick={() => {
                  invoke<DiagnosticInfo>("get_diagnostics")
                    .then(d => setDiagnostics(d))
                    .catch(() => {});
                }}
              >
                診断情報を表示
              </button>
            )}
            {diagnostics && (
              <div style={{ marginTop: '0.5rem' }}>
                <pre style={{ fontSize: '0.75rem', opacity: 0.8, textAlign: 'left', margin: 0 }}>
                  {Object.entries(diagnostics).map(([k, v]) => `${k}: ${v}`).join('\n')}
                </pre>
                <button
                  style={{ marginTop: '0.3rem', fontSize: '0.75rem', padding: '2px 8px', cursor: 'pointer' }}
                  onClick={() => {
                    const text = Object.entries(diagnostics).map(([k, v]) => `${k}: ${v}`).join('\n');
                    navigator.clipboard.writeText(text).then(() => {
                      setCopied(true);
                      setTimeout(() => setCopied(false), 2000);
                    }).catch(() => {});
                  }}
                >
                  {copied ? 'Copied!' : '診断情報をコピー'}
                </button>
              </div>
            )}
          </div>
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
