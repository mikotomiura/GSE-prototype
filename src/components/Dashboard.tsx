import React, { useEffect, useState, useRef } from 'react';
import { invoke } from "@tauri-apps/api/core";
import { emit, listen } from "@tauri-apps/api/event";

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

/** Phase 1 Ground Truth ラベルの種別 (backend の UserLabelKind と同期)。 */
type LabelKind = "flow" | "incubation" | "stuck";

interface DashboardProps {
  cognitiveState: {
    flow: number;
    incubation: number;
    stuck: number;
  };
  onQuit: () => void;
  /** アプリを終了せずスタート画面へ戻る (設定変更・尺度理解テスト・再開のため)。 */
  onBack?: () => void;
  isMonkMode: boolean;
  keyboardIdleMs: number;
  hookActive: boolean | null;
  /**
   * v0.3 較正モード。true のときメイン画面からモデル出力 (推定状態 / Flow・Incubation・Stuck
   * 確率 / GT カウンタ / 状態説明) を隠し、主観回答の測定独立性を守る (アンカリング防止)。
   * 既定 false (通常 / デバッグ表示)。
   */
  calibrationMode?: boolean;
  /**
   * セッションが介入を有効化しているか (session_meta.intervention_enabled)。
   * false のとき backend は全介入を gate するため Monk Mode (Wall mute) は no-op。
   * → 効かない操作を見せないよう、false のとき Monk Mode トグルを非表示にする。既定 false。
   */
  interventionEnabled?: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({ cognitiveState, onQuit, onBack, isMonkMode, keyboardIdleMs, hookActive, calibrationMode = false, interventionEnabled = false }) => {
  // セッション経過時間 (ストップウォッチ)
  const sessionStartRef = useRef(Date.now());
  const [sessionSeconds, setSessionSeconds] = useState(0);
  // 「今詰まっている」自己ラベル記録直後の確認フラッシュ。
  const [stuckMarked, setStuckMarked] = useState(false);
  // hookActive=false が続いた秒数 (権限バナーの段階的メッセージ表示に使用)
  const [hookWaitingSec, setHookWaitingSec] = useState(0);
  // 診断情報 (トラブルシューティング用)
  const [diagnostics, setDiagnostics] = useState<DiagnosticInfo | null>(null);
  // TCC リセット実行結果メッセージ
  const [resetResult, setResetResult] = useState<string | null>(null);
  const [resetAxResult, setResetAxResult] = useState<string | null>(null);
  // 診断コピー済みフラグ
  const [copied, setCopied] = useState(false);
  // Phase 1 Ground Truth: ラベル累積カウンタ (Flow / Incubation / Stuck)
  // Backend の `user_label_recorded` イベントを購読してインクリメント。
  // セッション跨ぎでは Dashboard 再マウント時にリセットされる。
  const [labelCounts, setLabelCounts] = useState<Record<LabelKind, number>>({
    flow: 0,
    incubation: 0,
    stuck: 0,
  });

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

  // Phase 1 Ground Truth: backend が発火する `user_label_recorded` を購読。
  // payload.label は LabelKind union で型付け（Rust 側でバリデーション済み）。
  // 未知値が来た場合はフォールスルーで既存 state を返す。
  useEffect(() => {
    const unlistenPromise = listen<{ label: LabelKind; timestamp: number }>(
      "user_label_recorded",
      (event) => {
        setLabelCounts((prev) => {
          const key = event.payload.label;
          if (key in prev) {
            return { ...prev, [key]: prev[key] + 1 };
          }
          return prev;
        });
      }
    );
    return () => {
      unlistenPromise
        .then((fn) => fn())
        .catch((e) => console.error("user_label_recorded unlisten failed:", e));
    };
  }, []);

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

  // Phase 1 較正: モデル出力 (推定状態/確率/GT/状態説明) は被験者へ一切見せない (v0.4 §5.2 minimal dashboard)。
  // 第1週 (calibrationMode=true) は従来どおり常時ブラインド。第2週 (calibrationMode=false) も
  // プローブ回答のアンカリングを避けるためブラインドにし、開発ビルド (import.meta.env.DEV) でのみ
  // デバッグ用に表示する (force_wall と同方式)。pilot/release バンドルからは完全に除去される。
  const showModelOutput = !calibrationMode && import.meta.env.DEV;

  return (
    <div className={`dashboard-container ${showModelOutput ? `state-${dominant.toLowerCase()}` : 'state-calibration'}`}>
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
                    <strong>Accessibility 権限を手動で追加してください</strong>
                    <p style={{ marginTop: '0.3rem' }}>
                      ad-hoc 署名のため自動付与が動作しません。以下の手順で手動追加してください:
                    </p>
                    <ol style={{ margin: '0.5rem 0', paddingLeft: '1.5rem', fontSize: '0.85rem', lineHeight: '1.6' }}>
                      <li>
                        下のボタンで System Settings を開く
                        <br />
                        <button
                          style={{ fontSize: '0.8rem', padding: '4px 12px', cursor: 'pointer', marginTop: '4px' }}
                          onClick={() => {
                            invoke<string>("open_accessibility_settings")
                              .catch(e => setResetAxResult(`System Settings を開けませんでした: ${e}`));
                          }}
                        >
                          System Settings を開く
                        </button>
                      </li>
                      <li>左下の<strong>「+」ボタン</strong>をクリック</li>
                      <li><code style={{ fontSize: '0.8rem', background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '3px' }}>
                        {diagnostics?.bundle_path || '/Applications/gse-next.app'}
                      </code> を選択して「開く」</li>
                      <li><strong>gse-next のトグルがオン</strong>になっていることを確認</li>
                    </ol>
                    {hookWaitingSec >= 30 && (
                      <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.9 }}>
                        gse-next が既にリストにある場合は、<strong>一度オフにしてからオンに戻して</strong>ください。
                        アップデート後は署名が変わるため再設定が必要です。
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
                      入力監視をリセット
                    </button>
                    {diagnostics?.using_accessibility_fallback === 'true' && (
                      <button
                        style={{ fontSize: '0.8rem', padding: '4px 10px', cursor: 'pointer', marginRight: '0.5rem' }}
                        onClick={() => {
                          if (!window.confirm('全アプリのアクセシビリティ権限がリセットされます。続行しますか？')) return;
                          invoke<string>("reset_accessibility")
                            .then(msg => setResetAxResult(msg))
                            .catch(e => setResetAxResult(`Error: ${e}`));
                        }}
                      >
                        アクセシビリティをリセット
                      </button>
                    )}
                    {resetResult && (
                      <p style={{ marginTop: '0.3rem', fontSize: '0.75rem', opacity: 0.8 }}>
                        {resetResult}
                      </p>
                    )}
                    {resetAxResult && (
                      <p style={{ marginTop: '0.3rem', fontSize: '0.75rem', opacity: 0.8 }}>
                        {resetAxResult}
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
          {/* 較正中は状態パレット (flow=緑/incubation=黄) を避け中立色にする。
              打鍵状態の色が推定状態の色記号と誤連想されるのを防ぐ (測定独立性・security LOW)。 */}
          <span className={`session-value kbd-status ${!showModelOutput ? 'kbd-neutral' : keyIsActive ? 'kbd-active' : 'kbd-idle'}`}>
            {keyStatusLabel}
          </span>
        </div>
      </div>

      {/* Phase 1 較正: モデル出力 (推定状態/確率/GT/状態説明) は測定独立性のため非表示。
          第2週もアンカリング回避のためブラインド。表示は開発ビルド (showModelOutput) のみ。 */}
      {!showModelOutput ? (
        <div className="calibration-notice" role="status">
          <span className="calibration-notice-badge">較正モード</span>
          <p>
            主観回答の独立性を保つため、推定状態 (Flow / Incubation / Stuck) は表示していません。
            画面の問いに、今の感覚のまま回答してください。
          </p>
        </div>
      ) : (
        <>
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

          {/* Phase 1 Ground Truth: 読み取り専用ラベルカウンタ + ショートカット hint */}
          <div className="gt-counter" role="status" aria-label="Ground Truth labels">
            <span className="gt-counter-label">GT:</span>
            <span>Flow {labelCounts.flow}</span>
            <span>Inc {labelCounts.incubation}</span>
            <span>Stuck {labelCounts.stuck}</span>
            <span className="gt-counter-hint">
              {navigator.userAgent.includes("Mac") ? "⌘⇧⌥" : "Ctrl+Shift+Alt"} F/I/S
            </span>
          </div>
        </>
      )}

      {/* Monk Mode トグル: ON=Wall無効, OFF=通常。
          介入無効セッションでは backend が全介入を gate し no-op になるため非表示にする
          (効かない操作を見せない・interventionEnabled=true のときのみ表示)。 */}
      {interventionEnabled && (
        <button
          className={`monk-mode-toggle ${isMonkMode ? 'on' : 'off'}`}
          onClick={handleMonkModeToggle}
        >
          <span>{isMonkMode ? 'Monk Mode: ON' : 'Monk Mode: OFF'}</span>
          <span className="monk-mode-label">
            {isMonkMode ? 'Wall intervention disabled' : 'Wall intervention active'}
          </span>
        </button>
      )}

      {showModelOutput && (
        <div className="info-box">
          <p>Type naturally. The engine analyzes your keystroke dynamics.</p>
          <p><strong>Incubation</strong> suggests pausing. <strong>Stuck</strong> suggests moving.</p>
        </div>
      )}

      {/* 自己ラベル: 「今とても詰まっている」をワンタップで記録 (source=self_marker)。
          ホットキー Ctrl+Shift+Alt+D でも同じ。X 軸較正の正解ラベルになる (本文は記録しない)。 */}
      <button
        className={`self-stuck-button ${stuckMarked ? 'marked' : ''}`}
        disabled={stuckMarked}
        aria-label="今とても詰まっていると感じたら記録する自己ラベル"
        onClick={() => {
          invoke<boolean>("record_self_marker")
            .then((recorded) => {
              // デバウンスで弾かれた (false) ときは確認表示を出さない。
              if (!recorded) return;
              setStuckMarked(true);
              setTimeout(() => setStuckMarked(false), 1500);
            })
            .catch((e) => console.error("record_self_marker failed:", e));
        }}
        title="今とても詰まっていると感じたら押す (Ctrl+Shift+Alt+D)"
      >
        {stuckMarked ? '✓ 記録しました' : '🔴 今とても詰まっている'}
      </button>

      {/* デバッグ: Wall を HMM と切り離して強制発動する (dev ビルドのみ表示)。
          Wall→QR→スマホ解除→介入応答 (A2) 捕捉の end-to-end 検証用。
          `import.meta.env.DEV` gate により release/pilot バンドルからは完全に除去され、
          被験者セッションへの混入リスクをゼロにする (cross-review HIGH-B)。
          強制発動は NDJSON に reason="debug_force" で残り、解析時にも除外できる。 */}
      {import.meta.env.DEV && (
        <button
          className="debug-force-wall-button"
          onClick={() =>
            invoke("force_wall").catch((e) => console.error("force_wall failed:", e))
          }
          title="HMM を介さず Wall を強制発動 (動作確認用・reason=debug_force でログ)"
        >
          🧱 Wall 強制発動 (デバッグ)
        </button>
      )}

      {/* ナビ: アプリ終了 (quit_app) とは別に、スタート画面へ戻る導線を用意する
          (作業種別の変更・尺度理解テスト・再開のため。アプリは終了しない)。 */}
      <div className="dashboard-nav">
        {onBack && (
          <button className="back-button" onClick={onBack}>
            ← 戻る
          </button>
        )}
        <button className="quit-button" onClick={onQuit}>
          セッション終了
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
