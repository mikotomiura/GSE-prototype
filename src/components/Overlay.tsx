import React, { useEffect, useState, useMemo, useRef } from 'react';
import { getCurrentWindow, currentMonitor, primaryMonitor } from "@tauri-apps/api/window";
import { PhysicalSize, PhysicalPosition } from "@tauri-apps/api/dpi";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import ProbeCard from "./ProbeCard";

// プローブ/Nudge 単独表示時にオーバーレイ窓を縮小する右上ボックス (logical px)。
// カード (~360px) を収め、これ以外の画面領域は OS レベルでクリック透過になる
// (被験者は作業を続けられる)。nudge も同じ box を再利用し非ブロック化する。
const PROBE_BOX_W = 390;
const PROBE_BOX_H = 430;
const PROBE_BOX_MARGIN = 12;

// idle 時にオーバーレイ窓を退避させる画面外座標 (physical px)。全モニタ構成の左上外側へ十分
// 負方向に振る (revert された card 窓方式と同値・design.md)。幾何的に画面と重ならないため、
// ignoresMouseEvents の tri-state バグや OS 退行 (Tahoe 26.x) に依らず背後クリックを奪わない。
const OFFSCREEN_POS = -20000;

// overlay のクリック受理切替。macOS では NSPanel 化窓で JS の setIgnoreCursorEvents が実効しない
// ため、Rust 権威の set_overlay_interactive コマンド経由で ignoresMouseEvents を設定する (D9)。
// interactive=true: カード/Wall がクリックを捕捉 / false: 背後アプリへ透過。
const setOverlayInteractive = (interactive: boolean): Promise<unknown> =>
    invoke("set_overlay_interactive", { interactive });

// show 時のモニタ解決。idle 退避 (画面外 -20000,-20000) で窓がどのモニタとも交差しないと
// macOS の currentMonitor() は null を返す (NSWindow.screen()==nil) ため、primaryMonitor() へ
// フォールバックする。これがないと退避後の初回 probe/Wall で setPosition がスキップされ、
// カードが画面外に留まる / Wall が全画面化しない退行が起きる (窓位置に依存しない解決にする)。
const resolveShowMonitor = async () => (await currentMonitor()) ?? (await primaryMonitor());

// Nudge は応答 (dismiss ボタン) があるまで消えない。無応答が続いたらこの時間で
// 自動フェード = silent 記録 (HCI: 自動消滅でユーザーが応答できない問題の回避 + CD7 silent 送出)。
const NUDGE_TIMEOUT_MS = 60_000;

// idle 残存バグ (透明 overlay が画面に残り背後クリックを奪う) を一次情報で監査するための計装ゲート。
// 研究者が `VITE_GSE_DEBUG=1` でビルドしたときだけ有効。被験者ビルドでは下記 auditWindowState は no-op。
const OVERLAY_DEBUG = import.meta.env.VITE_GSE_DEBUG === "1";

// `debug_overlay_window_state` の戻り値 (Rust `OverlayWindowState` DTO のフロント契約)。
// 結果はフロントで捨て tracing(overlay_audit) のみが本質だが、型を固定して回帰検知に効かせる。
interface OverlayWindowState {
    x: number;
    y: number;
    width: number;
    height: number;
    visible: boolean | null;
    offscreen: boolean;
    ex_transparent: boolean | null;
    ex_layered: boolean | null;
}

// 窓状態の読み返しログ (debug 専用)。各状態遷移直後に Rust 権威の `debug_overlay_window_state` を
// 呼び、overlay 窓の実位置/サイズ/(Windows) クリック透過を tracing(overlay_audit) へ出す。
// 読み取り専用で窓を変更しないため D7-D13 非回帰。失敗は握りつぶす (計装が本流を壊さない・
// GSE_DEBUG 未設定時は backend が Err を返すだけ)。`delayMs>0` は idle 後に窓が後から box へ
// 戻る上書き (hypotheses H2/H3) を捕まえるための遅延読み返し。
// 注: 遅延タイマーは effect cleanup と連動させない (意図的)。state/ref を一切触らず invoke→log のみで
// 副作用がなく、後続遷移/アンマウント後に発火しても無害。むしろ「後から戻る上書き」を捕えたいので止めない。
const auditWindowState = (tag: string, delayMs = 0): void => {
    if (!OVERLAY_DEBUG) return;
    const read = () => {
        void invoke<OverlayWindowState>("debug_overlay_window_state", { tag }).catch((e) => {
            console.warn("debug_overlay_window_state failed:", tag, e);
        });
    };
    if (delayMs > 0) {
        setTimeout(read, delayMs);
    } else {
        read();
    }
};

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
    // Nudge は「表示中か」を真偽で持つ (live action から切り離す)。一度出たら応答/タイムアウト
    // まで保持し、p_stuck 振動で action が変わっても消さない (= 勝手に消えるバグの修正)。
    const [nudgeVisible, setNudgeVisible] = useState(false);
    const [wallServerInfo, setWallServerInfo] = useState<WallServerInfo | null>(null);
    const [showTypingWarning, setShowTypingWarning] = useState(false);
    const [phoneConnected, setPhoneConnected] = useState(false);
    // Task C: プローブカード表示中フラグ。表示中は cursor events を受け付け、overlay を可視化する。
    const [probeActive, setProbeActive] = useState(false);
    // Nudge を dismiss 済みか。同一 nudge の再表示を防ぐ。action が nudge 以外に変わると解除。
    const [nudgeDismissed, setNudgeDismissed] = useState(false);
    // dismiss 記録 (record_intervention_dismiss) が失敗したときのインラインエラー文言。
    // null = エラーなし。失敗時はカードを保持してこれを表示し、ボタン再押下でリトライさせる
    // (= 旧実装の「失敗→dismissed 解除→即再表示」無限ループを廃止)。
    const [nudgeError, setNudgeError] = useState<string | null>(null);
    // dismiss 送信中フラグ (ボタン disable 用)。
    const [nudgeSubmitting, setNudgeSubmitting] = useState(false);
    // dismiss 送信の相互排他ガード (手動ボタン経路と silent タイマー経路の二重送信を防ぐ)。
    // state はタイマー closure 内で stale になるため ref で同期的に判定する。
    const dismissInFlightRef = useRef(false);
    // 無応答フェードアウト (silent) 用タイマー。
    const nudgeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const currentWindow = useMemo(() => getCurrentWindow(), []);

    // Nudge を閉じてユーザー応答 (dismiss 理由) を NDJSON へ記録する (WBS 0.8)。
    // 固定カテゴリのみを送る。中身・本文は一切送らない。
    // 記録成功時のみカードを閉じる。失敗時はカードを保持してインラインエラーを出し、
    // ボタン再押下でリトライさせる (較正データを静かに失わない + 無限再表示ループを断つ)。
    const handleNudgeDismiss = async (reason: DismissReason) => {
        if (dismissInFlightRef.current) return; // 二重送信防止 (silent タイマーとも相互排他)
        if (nudgeTimerRef.current) {
            clearTimeout(nudgeTimerRef.current);
            nudgeTimerRef.current = null;
        }
        dismissInFlightRef.current = true;
        setNudgeSubmitting(true);
        setNudgeError(null);
        try {
            await invoke("record_intervention_dismiss", { action: "nudge", reason });
            setNudgeDismissed(true);
            setNudgeVisible(false);
        } catch (e) {
            console.error("record_intervention_dismiss failed:", e);
            // 失敗時はカードを保持し、インラインエラー + リトライ (ボタン再押下) に倒す。
            // 旧実装の setNudgeDismissed(false) による「失敗→即再表示」無限ループは廃止。
            setNudgeError("記録に失敗しました。もう一度お試しください。");
        } finally {
            dismissInFlightRef.current = false;
            setNudgeSubmitting(false);
        }
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
        // 初回マウント時に透過を保証 (Rust 権威の set_overlay_interactive 経由)。
        setOverlayInteractive(false).catch(() => {});
    }, []);

    // オーバーレイ窓の表示モードを (wall / probe / nudge) から決める統合 effect。
    //   - Wall:            全画面 + クリックブロック (QR スキャンまで操作不可・現状維持)
    //   - プローブ/Nudge:   右上の小ボックスに縮小 + カード以外は OS レベルでクリック透過
    //                       (被験者は作業を続けながら任意のタイミングで応答できる=非ブロック)
    //   - Wall+他 同時:     全画面 (Wall 優先)
    //   - いずれも無し:     hide()
    // box 化が失敗した環境では安全側 (全画面 + ブロック=現状挙動) にフォールバックする。
    useEffect(() => {
        const win = currentWindow;
        const visible = isWallActive || probeActive || nudgeVisible;
        // Wall 以外 (probe / nudge) は右上の小 box にして非ブロック化する。
        const widgetOnly = (probeActive || nudgeVisible) && !isWallActive;
        let cancelled = false;

        // 全画面化は「モニタ全域へ明示 setPosition + setSize」で行う。physical 座標で扱い DPI 二重
        // 変換を避ける。**maximize() は使わない**: macOS で overlay は NSPanel 化済み (decisions D7) で、
        // maximize() が内部で setStyleMask: を呼ぶと WKWebView の contentLayoutRect オブザーバ解除に
        // 失敗して NSRangeException でクラッシュする (実機確認・D8)。明示サイズはタスクバーごと全被覆=
        // Wall の全ブロック意図にも合致する。
        const applyFullscreenBlock = async () => {
            // 退避後は窓が画面外のため currentMonitor() が null になりうる。primaryMonitor()
            // フォールバックで mon を必ず得て setPosition/setSize を確実に走らせる
            // (mon が null だと Wall が 1x1 offscreen のまま=全画面ブロック不成立になる退行を防ぐ)。
            const mon = await resolveShowMonitor();
            if (cancelled) return;
            if (mon) {
                await win.setPosition(new PhysicalPosition(mon.position.x, mon.position.y));
                if (cancelled) return;
                await win.setSize(new PhysicalSize(mon.size.width, mon.size.height));
                if (cancelled) return;
            }
            await setOverlayInteractive(true);
        };

        (async () => {
            // idle (何も表示しない) でも **hide() しない** (decisions D10)。macOS で NSPanel/overlay を
            // orderOut (hide) すると webview の JS が休眠し、probe_triggered を取りこぼして
            // カードが出ない (実機の診断ログで setOverlayInteractive(true) 不到達=リスナー休眠を確認)。
            // 代わりに「画面に出したまま透明 + クリック透過 (ignoresMouseEvents=true)」にして JS を生かす。
            // overlay の中身は idle 時すべて非表示 (ProbeCard=null / Nudge=opacity0 / Wall 非描画) なので
            // 透明窓として不可視・無害。被験者のクリックは背後アプリへ透過する。
            if (!visible) {
                // 一次ガード (幾何退避): 窓を画面外 + 1x1 へ退避し、背後アプリと重なる領域を
                // 物理的に消す。これにより ignoresMouseEvents の tri-state バグや OS 退行に
                // 依らず背後クリックを奪わない (design.md 多層防御)。hide()/orderOut は使わない
                // (D10: webview JS 休眠で probe_triggered 取りこぼし) — 窓は出したまま退避する。
                // 二次ガードの setOverlayInteractive(false) とは try/catch を分け、panel 変換失敗で
                // ignoresMouseEvents が設定できない場合でも退避だけは効かせて全画面ブロックを断つ
                // (= 旧実装の「panel 失敗→idle throw→全画面透明窓が全クリック奪取」増幅条件の遮断)。
                // cancelled ガード: idle→show 遷移で本 effect が stale 化した場合、退避が後続の
                // show (box/全画面) を上書きしないよう各 await 後に中断する。
                try {
                    await win.setPosition(new PhysicalPosition(OFFSCREEN_POS, OFFSCREEN_POS));
                    if (cancelled) return;
                    await win.setSize(new PhysicalSize(1, 1));
                    if (cancelled) return;
                } catch (e) {
                    console.warn("overlay idle offscreen retreat failed:", e);
                    if (cancelled) return;
                }
                // 二次ガード (ignoresMouseEvents=YES)。退避の成否と独立に必ず試す。
                try {
                    await setOverlayInteractive(false);
                } catch (e) {
                    console.warn("overlay idle (transparent click-through) failed:", e);
                }
                // 計装: idle 確定直後の実窓位置を読み返す (退避が効いたか)。さらに ~1.5s 後にも読み、
                // 別 effect が後から box へ戻す上書き (H2/H3) を捕まえる。debug ビルドのみ。
                auditWindowState("idle-immediate");
                auditWindowState("idle-after-1500ms", 1500);
                return;
            }
            try {
                await win.show();
                if (cancelled) return;
                if (widgetOnly) {
                    // 右上小ボックス化 → カード外は他アプリへクリックが通る (非ブロック)。
                    // unmaximize() は使わない (maximize と同じく NSPanel + WKWebView でクラッシュ。D8)。
                    // 全画面状態からの復帰も下の明示 setSize で box サイズへ直接縮小すれば足りる。
                    // 退避後は窓が画面外で currentMonitor() が null になりうるため primaryMonitor()
                    // フォールバック (resolveShowMonitor)。これで下の setPosition (if (mon) 内) が
                    // 確実に走り、カードがオンスクリーン右上へ復帰する (画面外残留=不可視を防ぐ)。
                    const mon = await resolveShowMonitor();
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
                    await setOverlayInteractive(true);
                    // 計装: box(widget) show 後の実窓位置/サイズ (オンスクリーン右上 box か)。debug のみ。
                    auditWindowState(`widget-show probe=${probeActive} nudge=${nudgeVisible}`);
                } else {
                    // Wall (単独 or 他と同時): 全画面 + クリックブロック。
                    await applyFullscreenBlock();
                    // 計装: Wall 全画面化後の実窓位置/サイズ (モニタ全域か)。debug のみ。
                    auditWindowState("fullscreen-wall");
                }
            } catch (e) {
                // 既にこの effect がキャンセル済み (新 state へ遷移済み) なら何もしない。
                // stale な effect が全画面ブロックで新モードを上書きする race を防ぐ。
                if (cancelled) return;
                // box 化失敗時は probe/nudge でも全画面ブロック (interactive=true) へ倒す。
                // 一見 widgetOnly は非ブロック (setOverlayInteractive(false)) へ倒す方が穏当に見えるが
                // (cross-review/Codex 指摘)、それは窓全体 ignoresMouseEvents=true でカード自体も
                // クリック不能=死んだボタン・較正ラベル静的損失 (本タスクで直した元バグそのもの) に
                // 戻る。較正データ正確性を最優先する研究ツールでは、背後を一時ブロックしてでもカードを
                // 回答可能に保つ方を採る (カードは ✕ で dismiss でき必ず復帰する)。box 化失敗は capability
                // 付与 (D11) 後はほぼ起きない縮退路。意味を変えずに「非ブロックへ倒す」改変をしないこと。
                console.warn("overlay window mode failed, falling back to fullscreen:", e);
                try {
                    await applyFullscreenBlock();
                } catch (e2) {
                    console.error("overlay fullscreen fallback also failed:", e2);
                }
            }
        })();

        return () => { cancelled = true; };
    }, [isWallActive, probeActive, nudgeVisible, currentWindow]);

    // Wall 発動時はプローブカード・Nudge を畳む (Wall が支配)。
    // ProbeCard はアンマウントされ onActiveChange(false) を呼ばないので probeActive を明示リセット。
    useEffect(() => {
        if (isWallActive) {
            setProbeActive(false);
            if (nudgeTimerRef.current) {
                clearTimeout(nudgeTimerRef.current);
                nudgeTimerRef.current = null;
            }
            setNudgeVisible(false);
            // Wall 割込みで畳む際、保持していたエラー/送信中フラグも掃除する (次サイクルへ持ち越さない)。
            setNudgeError(null);
            setNudgeSubmitting(false);
            dismissInFlightRef.current = false;
        }
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

    // Nudge は「一度出たら応答 (dismiss) かタイムアウトまで保持」する。
    // live action が none/defer/wall に変わっても消さない (= ボタンを押す前に勝手に消える問題の修正)。
    useEffect(() => {
        // probe 表示中は nudge を出さない (同じ box に重ねない・MEDIUM 対応)。probe 応答後に出る。
        const isNudge =
            interventionDecision.action === "nudge" && !isWallActive && !probeActive;
        if (isNudge && !nudgeVisible && !nudgeDismissed) {
            // 新規 nudge を表示。無応答が続いたら NUDGE_TIMEOUT_MS で silent としてフェードアウト。
            setNudgeVisible(true);
            setNudgeError(null); // 新規表示でエラー表示をクリア。
            if (nudgeTimerRef.current) clearTimeout(nudgeTimerRef.current);
            nudgeTimerRef.current = setTimeout(() => {
                nudgeTimerRef.current = null;
                // 記録成功時のみ閉じる。失敗時はカードを保持しエラー表示 + リトライ
                // (旧実装の setNudgeDismissed(false) による無限再表示ループを廃止)。
                // 手動ボタン経路と同じ相互排他ガードを通し、二重送信 (silent + 手動) を防ぐ。
                void (async () => {
                    if (dismissInFlightRef.current) return;
                    dismissInFlightRef.current = true;
                    setNudgeSubmitting(true);
                    try {
                        await invoke("record_intervention_dismiss", {
                            action: "nudge",
                            reason: "silent",
                        });
                        setNudgeDismissed(true);
                        setNudgeVisible(false);
                    } catch (e) {
                        console.error("record_intervention_dismiss (silent) failed:", e);
                        // 失敗時はカード保持。ユーザーは手動 dismiss ボタンでリトライ可能 (回復経路)。
                        setNudgeError("記録に失敗しました。もう一度お試しください。");
                    } finally {
                        dismissInFlightRef.current = false;
                        setNudgeSubmitting(false);
                    }
                })();
            }, NUDGE_TIMEOUT_MS);
        } else if (!isNudge && !nudgeVisible && nudgeDismissed) {
            // dismiss / silent はいずれも record_intervention_dismiss を送り、backend の record_dismiss が
            // current_action をリセット + recent_dismiss を立てるため action は nudge を離れる (defer)。
            // それを検知して dismissed を解除し、次の nudge (cooldown 後) を再表示可能にする。
            setNudgeDismissed(false);
        }
    }, [interventionDecision, isWallActive, probeActive, nudgeVisible, nudgeDismissed]);

    // アンマウント時にタイマーを掃除する。
    useEffect(() => {
        return () => {
            if (nudgeTimerRef.current) clearTimeout(nudgeTimerRef.current);
        };
    }, []);

    return (
        <div className="overlay-root">
            {/* Task C: v0.3 較正のプローブ回答カード (probe_triggered を listen)。
                Wall 発動中は表示しない (上の effect で probeActive もリセット)。
                overlay 窓は tauri-nspanel で非アクティブ Panel 化しクリックを webview へ配送する
                (透明窓でもクリックが届く・フォーカスは奪わない。decisions D7)。 */}
            {!isWallActive && <ProbeCard onActiveChange={setProbeActive} />}

            <aside
                className={`nudge-card ${nudgeVisible ? "nudge-card-visible" : ""}`}
                style={{
                    opacity: nudgeVisible ? 1 : 0,
                    transform: nudgeVisible ? "translateY(0)" : "translateY(12px)",
                    pointerEvents: nudgeVisible ? "auto" : "none",
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
                        disabled={nudgeSubmitting}
                        onClick={() => handleNudgeDismiss("not_stuck")}
                    >
                        詰まってない
                    </button>
                    <button
                        type="button"
                        className="nudge-dismiss-btn"
                        disabled={nudgeSubmitting}
                        onClick={() => handleNudgeDismiss("want_to_struggle")}
                    >
                        今はもがきたい
                    </button>
                    <button
                        type="button"
                        className="nudge-dismiss-btn"
                        disabled={nudgeSubmitting}
                        onClick={() => handleNudgeDismiss("just_close")}
                    >
                        閉じる
                    </button>
                </div>
                {/* 記録失敗時のインラインエラー。死んだボタンに見せず、再押下でリトライ可能と伝える。 */}
                {nudgeError && (
                    <div className="nudge-card-error" role="alert">
                        {nudgeError}
                    </div>
                )}
            </aside>

            {/* The Wall (Blocking Layer) — 即時不透明でなく数秒かけてゆっくり減光 (穏やかな onset)。 */}
            {isWallActive && (
                <div className="wall-layer wall-dim-in">
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
                            いまは手を止めて、ひと休みしましょう
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Overlay;
