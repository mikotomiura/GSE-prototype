import React, { useEffect, useState, useMemo, useRef } from 'react';
import { getCurrentWindow, currentMonitor } from "@tauri-apps/api/window";
import { PhysicalSize, PhysicalPosition } from "@tauri-apps/api/dpi";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import ProbeCard from "./ProbeCard";

// プローブ単独表示時にオーバーレイ窓を縮小する右上ボックス (logical px)。
// カード (~360px) を収め、これ以外の画面領域は OS レベルでクリック透過になる。
const PROBE_BOX_W = 390;
const PROBE_BOX_H = 430;
const PROBE_BOX_MARGIN = 12;

interface OverlayProps {
    interventionDecision: InterventionDecision;
    isWallActive: boolean;
}

type InterventionAction = "none" | "nudge" | "wall" | "defer";

// 介入応答 (dismiss) の固定カテゴリ。Need 誤りと Opportunity 誤りを分離する (WBS 0.8 / v0.4 §9)。
// Rust 側 `DismissReason` (logger.rs) と文字列を一致させること。
type DismissReason = "not_stuck" | "want_to_struggle" | "just_close" | "silent";

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

interface WallServerInfo {
    url: string;
    qr_svg: string;
}

const Overlay: React.FC<OverlayProps> = ({ interventionDecision, isWallActive }) => {
    const [nudgeOpacity, setNudgeOpacity] = useState(0);
    const [wallServerInfo, setWallServerInfo] = useState<WallServerInfo | null>(null);
    const [showTypingWarning, setShowTypingWarning] = useState(false);
    const [phoneConnected, setPhoneConnected] = useState(false);
    // Task C: プローブカード表示中フラグ。表示中は cursor events を受け付け、overlay を可視化する。
    const [probeActive, setProbeActive] = useState(false);
    // Nudge を dismiss 済みか。同一 nudge の再表示を防ぐ。action が nudge 以外に変わると解除。
    const [nudgeDismissed, setNudgeDismissed] = useState(false);
    const currentWindow = useMemo(() => getCurrentWindow(), []);

    // Nudge に対するユーザー応答 (dismiss 理由) を NDJSON へ記録する (WBS 0.8)。
    // 固定カテゴリのみを送る。中身・本文は一切送らない。
    const handleNudgeDismiss = (reason: DismissReason) => {
        setNudgeDismissed(true);
        setNudgeOpacity(0);
        invoke("record_intervention_dismiss", { action: "nudge", reason }).catch((e) =>
            console.error("record_intervention_dismiss failed:", e)
        );
    };

    // Wall発動中のキーボード打鍵検知に使うref群
    const wallStartTimeRef = useRef<number>(0);
    const lastWarnedKeyAtRef = useRef<number>(0);
    const warningTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // スマートフォン接続イベントの購読
    useEffect(() => {
        const unlisten = listen("wall-phone-connected", () => {
            setPhoneConnected(true);
        });
        return () => {
            unlisten.then((f) => f());
        };
    }, []);

    // マウント直後に即座にクリック透過を有効化 (初期状態保証)
    // React の useEffect は最初のレンダー後に実行されるため、起動時に
    // オーバーレイが一瞬クリックをブロックしてウィンドウをドラッグ不能にする問題を防ぐ。
    // 表示モード (透過/ブロック・サイズ) の真の権威は下の統合 effect で、これより後に走り
    // 最終状態を確定する (本 effect は初回ドラッグ可能性の保証のみ)。
    useEffect(() => {
        currentWindow.setIgnoreCursorEvents(true).catch(() => {});
    // currentWindow は useMemo で安定しているが lint 警告を避けるため含める
    }, [currentWindow]); // eslint-disable-line react-hooks/exhaustive-deps

    // オーバーレイ窓の表示モードを (wall / probe / nudge) から決める統合 effect。
    //   - Wall:            全画面 + クリックブロック (QR スキャンまで操作不可・現状維持)
    //   - プローブ単独:     右上の小ボックスに縮小 + カード以外は OS レベルでクリック透過
    //                       (被験者は作業を続けながら任意のタイミングで回答できる)
    //   - Nudge / 同時表示: 全画面 + クリックブロック (nudge は top:42% 配置のため box 化しない)
    //   - いずれも無し:     hide()
    // box 化が失敗した環境では安全側 (全画面 + ブロック=現状挙動) にフォールバックする。
    useEffect(() => {
        const win = currentWindow;
        const visible = isWallActive || probeActive || nudgeOpacity > 0;
        const probeOnly = probeActive && nudgeOpacity <= 0 && !isWallActive;
        let cancelled = false;

        // 全画面を「明示的にモニタ全域へ復元してから maximize」する。box 化で縮小済みの窓を
        // maximize() だけに頼ると WM 次第で小窓のまま復帰しないため (Wall が小窓 QR で解除不能=
        // 被験者ロックの回避)。physical 座標で扱い DPI 二重変換を避ける。
        const applyFullscreenBlock = async () => {
            const mon = await currentMonitor();
            if (cancelled) return;
            if (mon) {
                await win.setPosition(new PhysicalPosition(mon.position.x, mon.position.y));
                if (cancelled) return;
                await win.setSize(new PhysicalSize(mon.size.width, mon.size.height));
                if (cancelled) return;
            }
            await win.maximize();
            if (cancelled) return;
            await win.setIgnoreCursorEvents(false);
        };

        (async () => {
            // 非表示は独立処理。hide 失敗時に全画面ブロックへ転落させない (= 何も出ていないのに
            // 画面が操作不能になる事故の回避)。最悪でも透過に留める。
            if (!visible) {
                try {
                    await win.hide();
                } catch (e) {
                    console.warn("overlay hide failed:", e);
                    try { await win.setIgnoreCursorEvents(true); } catch { /* noop */ }
                }
                return;
            }
            try {
                await win.show();
                if (cancelled) return;
                if (probeOnly) {
                    // 右上小ボックス化 → カード外は他アプリへクリックが通る (非ブロック)。
                    const mon = await currentMonitor();
                    if (cancelled) return;
                    // 非 maximize 窓では no-op。失敗時も box 化を続行 (失敗すれば下の catch で全画面へ)。
                    await win.unmaximize().catch((e) => console.warn("unmaximize failed:", e));
                    if (cancelled) return;
                    const scale = mon?.scaleFactor ?? 1;
                    await win.setSize(
                        new PhysicalSize(Math.round(PROBE_BOX_W * scale), Math.round(PROBE_BOX_H * scale))
                    );
                    if (cancelled) return;
                    if (mon) {
                        // 右上 (画面外に出ないよう clamp)。
                        const x = Math.max(
                            mon.position.x,
                            mon.position.x + mon.size.width - Math.round((PROBE_BOX_W + PROBE_BOX_MARGIN) * scale)
                        );
                        const y = mon.position.y + Math.round(PROBE_BOX_MARGIN * scale);
                        await win.setPosition(new PhysicalPosition(x, y));
                        if (cancelled) return;
                    }
                    await win.setIgnoreCursorEvents(false);
                } else {
                    // Wall / Nudge / 同時表示: 全画面 + クリックブロック (現状維持)。
                    await applyFullscreenBlock();
                }
            } catch (e) {
                // 既にこの effect がキャンセル済み (新 state へ遷移済み) なら何もしない。
                // stale な effect が全画面ブロックで新モードを上書きする race を防ぐ。
                if (cancelled) return;
                // box 化に失敗しても被験者が操作不能にならないよう全画面=現状挙動へ倒す。
                console.warn("overlay window mode failed, falling back to fullscreen:", e);
                try {
                    await applyFullscreenBlock();
                } catch (e2) {
                    console.error("overlay fullscreen fallback also failed:", e2);
                }
            }
        })();

        return () => { cancelled = true; };
    }, [isWallActive, probeActive, nudgeOpacity, currentWindow]);

    // Wall 発動時はプローブカードを畳む (介入中は自然作業のサンプリングでなく UI も衝突するため)。
    // ProbeCard はアンマウントされ onActiveChange(false) を呼ばないので probeActive を明示リセット。
    useEffect(() => {
        if (isWallActive) setProbeActive(false);
    }, [isWallActive]);

    // Wall発動/解除に連動してWall Serverを起動/停止する
    useEffect(() => {
        if (isWallActive) {
            invoke<WallServerInfo>("start_wall_server")
                .then(info => setWallServerInfo(info))
                .catch(e => console.error("Failed to start wall server:", e));
        } else {
            invoke("stop_wall_server").catch(console.error);
            setWallServerInfo(null);
        }
    }, [isWallActive]);

    // Wall発動時刻を記録し、Wall解除時にリセット
    useEffect(() => {
        if (isWallActive) {
            wallStartTimeRef.current = Date.now();
            lastWarnedKeyAtRef.current = 0;
            setShowTypingWarning(false);
        }
    }, [isWallActive]);

    // Wall発動中のキーボード打鍵検知: 打鍵を検知したら警告バナーを2.5秒表示
    // lastKeyAt = Date.now() - idle が wallStartTime より後なら Wall後の打鍵
    // 同一バーストへの重複警告を防ぐため1秒のデバウンスを設ける
    useEffect(() => {
        if (!isWallActive) {
            setShowTypingWarning(false);
            return;
        }
        const interval = setInterval(async () => {
            try {
                // get_last_keypress_timestamp() は Rust の LAST_KEY_MS をエポックmsで直接返す。
                // Date.now() - idle_ms の逆算より精度が高い (advice.md §D)
                const lastKeyAt = await invoke<number>("get_last_keypress_timestamp");
                if (
                    lastKeyAt > wallStartTimeRef.current &&
                    lastKeyAt > lastWarnedKeyAtRef.current + 1000
                ) {
                    lastWarnedKeyAtRef.current = lastKeyAt;
                    setShowTypingWarning(true);
                    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
                    warningTimerRef.current = setTimeout(() => setShowTypingWarning(false), 2500);
                }
            } catch (_) {}
        }, 300);
        return () => {
            clearInterval(interval);
            if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
        };
    }, [isWallActive]);

    useEffect(() => {
        if (interventionDecision.action === "nudge" && !isWallActive) {
            // 既に dismiss 済みなら再表示しない (同一 nudge の押下後にちらつかせない)。
            if (nudgeDismissed) {
                setNudgeOpacity(0);
                return;
            }
            const opacity = Math.min(
                1,
                Math.max(0.2, (interventionDecision.need_score - 0.6) / 0.3)
            );
            setNudgeOpacity(opacity);
        } else {
            // nudge 以外に遷移したら dismiss 状態を解除し、次の nudge を表示可能にする。
            setNudgeOpacity(0);
            if (nudgeDismissed) setNudgeDismissed(false);
        }
    }, [interventionDecision, isWallActive, nudgeDismissed]);

    return (
        <div className="overlay-root">
            {/* Task C: v0.3 較正のプローブ回答カード (probe_triggered を listen)。
                Wall 発動中は表示しない (上の effect で probeActive もリセット)。 */}
            {!isWallActive && <ProbeCard onActiveChange={setProbeActive} />}

            <aside
                className="nudge-card"
                style={{
                    opacity: nudgeOpacity,
                    transform: nudgeOpacity > 0 ? "translateX(0)" : "translateX(120%)",
                }}
            >
                <div className="nudge-card-accent"></div>
                <div className="nudge-card-copy">
                    <span className="nudge-card-kicker">Pause point</span>
                    <strong>One breath. Next move.</strong>
                </div>
                {/* dismiss 4択 (WBS 0.8): Need 誤り / Opportunity 誤り / 単に閉じる を分離記録。
                    「無言(silent)」はボタンを押さずフェードした場合に相当し UI には出さない。 */}
                <div className="nudge-card-dismiss">
                    <button
                        type="button"
                        className="nudge-dismiss-btn"
                        onClick={() => handleNudgeDismiss("not_stuck")}
                    >
                        詰まってない
                    </button>
                    <button
                        type="button"
                        className="nudge-dismiss-btn"
                        onClick={() => handleNudgeDismiss("want_to_struggle")}
                    >
                        今はもがきたい
                    </button>
                    <button
                        type="button"
                        className="nudge-dismiss-btn"
                        onClick={() => handleNudgeDismiss("just_close")}
                    >
                        閉じる
                    </button>
                </div>
            </aside>

            {/* The Wall (Blocking Layer) */}
            {isWallActive && (
                <div className="wall-layer">
                    <h1>Time to Move!</h1>
                    <p>Scan the QR code with your phone to unlock</p>

                    {wallServerInfo ? (
                        <div className="qr-container">
                            <img src={wallServerInfo.qr_svg} alt="QR Code" className="qr-code" />
                            <p className="qr-hint">
                                Open camera app and point at QR code
                            </p>
                            {wallServerInfo.url && (
                                <p className="qr-url">{wallServerInfo.url}</p>
                            )}
                        </div>
                    ) : (
                        <p className="qr-loading">Starting unlock server...</p>
                    )}

                    <p className="wall-network-hint">
                        PCとスマホが同じWi-Fiに接続されていることを確認してください
                    </p>
                    {/* スマートフォン接続バッジ */}
                    {phoneConnected && (
                        <div className="phone-connected-badge">
                            Phone connected — Zen Timer running
                        </div>
                    )}
                    {/* Wall発動中の打鍵警告バナー */}
                    {showTypingWarning && (
                        <div className="wall-typing-warning">
                            ⚠ キーボードは使えません！
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Overlay;
