import React, { useEffect, useState, useMemo, useRef, useCallback } from 'react';
import { getCurrentWindow, currentMonitor, primaryMonitor } from "@tauri-apps/api/window";
import { PhysicalSize, PhysicalPosition } from "@tauri-apps/api/dpi";
import { invoke } from "@tauri-apps/api/core";
import ProbeCard from "./ProbeCard";
import InvitationGlyph, { GLYPH_SIZE_PX, INVITATION_GLYPH } from "./InvitationGlyph";

// プローブ/Nudge 単独表示時、overlay 窓は「カードの実寸ちょうど」に縮める (logical px)。
// これにより窓=カードとなり透明余白が生じない → Windows でカード周囲のクリックを奪わない
// (#11461: 透明 WebView2 窓は透明ピクセルでもクリックを捕捉するため、退避でなく実寸縮小で対処)。
// 実寸は ResizeObserver で測る。下記は「測定が出るまでの一瞬」のフォールバック。
// ★必ず実カードより大きい側に倒す: 過大なら 1 フレーム余分に透明余白が出て測定で即縮むだけ (自己回復) だが、
//   過小だと submit/skip ボタンが窓外にクリップされ到達不能=較正ラベル喪失 (最悪)。非対称なので大きめ既定。
const PROBE_FALLBACK_W = 380;
const PROBE_FALLBACK_H = 470;
const NUDGE_FALLBACK_W = 360;
const NUDGE_FALLBACK_H = 250;
// 招待の図像の窓の大きさ (logical px)。図像は固定の大きさで、提示ごとに変えない (R-I1)。
const INVITATION_BOX = GLYPH_SIZE_PX + 8;
// 招待の状態を読む間隔。Rust 側の状態機械が 1 秒に 1 回進むのに合わせる。
const INVITATION_POLL_MS = 1000;
// カードと画面端の余白 + カード切れ防止の僅かなパディング (透明余白を最小化するため 1px)。
const CARD_SCREEN_MARGIN = 12;
const CARD_FIT_PAD = 1;

// idle 時にオーバーレイ窓を退避させる画面外座標 (physical px)。全モニタ構成の左上外側へ十分
// 負方向に振る (revert された card 窓方式と同値・design.md)。幾何的に画面と重ならないため、
// ignoresMouseEvents の tri-state バグや OS 退行 (Tahoe 26.x) に依らず背後クリックを奪わない。
const OFFSCREEN_POS = -20000;

// overlay のクリック受理切替。macOS では NSPanel 化窓で JS の setIgnoreCursorEvents が実効しない
// ため、Rust 権威の set_overlay_interactive コマンド経由で ignoresMouseEvents を設定する (D9)。
// interactive=true: カードがクリックを捕捉 / false: 背後アプリへ透過。
const setOverlayInteractive = (interactive: boolean): Promise<unknown> =>
    invoke("set_overlay_interactive", { interactive });

// show 時のモニタ解決。idle 退避 (画面外 -20000,-20000) で窓がどのモニタとも交差しないと
// macOS の currentMonitor() は null を返す (NSWindow.screen()==nil) ため、primaryMonitor() へ
// フォールバックする。これがないと退避後の初回 probe で setPosition がスキップされ、
// カードが画面外に留まる退行が起きる (窓位置に依存しない解決にする)。
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
}

type InterventionAction = "none" | "nudge" | "defer";

// 介入応答 (dismiss) の固定カテゴリ。Need 誤りと Opportunity 誤りを分離する (WBS 0.8 / v0.4 §9)。
// Rust 側 `DismissReason` (logger.rs) と文字列を一致させること。
type DismissReason = "not_stuck" | "want_to_struggle" | "just_close" | "silent";

interface InterventionDecision {
    action: InterventionAction;
    need_score: number;
    opportunity_score: number;
    p_stuck: number;
    idle_ms: number;
    reason: string;
    suppressed_by: string[];
}


const Overlay: React.FC<OverlayProps> = ({ interventionDecision }) => {
    // Nudge は「表示中か」を真偽で持つ (live action から切り離す)。一度出たら応答/タイムアウト
    // まで保持し、p_stuck 振動で action が変わっても消さない (= 勝手に消えるバグの修正)。
    const [nudgeVisible, setNudgeVisible] = useState(false);
    // Task C: プローブカード表示中フラグ。表示中は cursor events を受け付け、overlay を可視化する。
    const [probeActive, setProbeActive] = useState(false);
    // プローブ/Nudge カードの実描画サイズ (logical px)。overlay 窓をこの実寸へ縮め透明余白を消す。
    // null = 未測定 (フォールバックサイズを使う)。サイズ未変化なら state を更新しない (窓再配置の churn 抑制)。
    const [probeCardSize, setProbeCardSize] = useState<{ w: number; h: number } | null>(null);
    const [nudgeCardSize, setNudgeCardSize] = useState<{ w: number; h: number } | null>(null);
    // Nudge カード本体 (実寸測定用)。
    const nudgeRef = useRef<HTMLElement | null>(null);
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
    // EH3: 招待を出しているか（Rust の状態機械の出力をそのまま映す。ここでは何も判定しない）。
    // EH3 でなければ backend は常に false を返す。
    const [invitationPresent, setInvitationPresent] = useState(false);

    useEffect(() => {
        let alive = true;
        const read = () => {
            invoke<boolean>("get_invitation_state")
                .then((v) => {
                    if (alive) setInvitationPresent(v);
                })
                .catch(() => {
                    if (alive) setInvitationPresent(false);
                });
        };
        read();
        const t = setInterval(read, INVITATION_POLL_MS);
        return () => {
            alive = false;
            clearInterval(t);
        };
    }, []);

    // 招待の図像を押すと説明と設定の窓を開く。⚠️ この操作は記録しない・応答として扱わない (R-I1)。
    const openInvitationSettings = () => {
        invoke("open_invitation_settings").catch((e) => {
            console.warn("open_invitation_settings failed:", e);
        });
    };

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


    // ProbeCard から実寸通知を受ける安定コールバック (ProbeCard 側 effect deps の identity 維持)。
    // サイズ未変化なら同一参照を返し、不要な窓再配置 effect を起こさない。
    const handleProbeResize = useCallback((size: { w: number; h: number } | null) => {
        setProbeCardSize((prev) => {
            if (size === null) return null;
            if (prev && prev.w === size.w && prev.h === size.h) return prev;
            return size;
        });
    }, []);

    // Nudge カードの実寸を測る (ProbeCard と異なり Nudge は常時マウントされ opacity で出し入れするため
    // ここで観測)。窓はこの実寸へ縮める。
    useEffect(() => {
        const el = nudgeRef.current;
        if (!el) return;
        const report = () => {
            // offsetWidth/Height は layout 寸法で transform (nudge の translateY/transition) 非依存。
            const w = el.offsetWidth;
            const h = el.offsetHeight;
            if (w > 0 && h > 0) {
                setNudgeCardSize((prev) => (prev && prev.w === w && prev.h === h ? prev : { w, h }));
            }
        };
        report();
        const ro = new ResizeObserver(report);
        ro.observe(el);
        return () => ro.disconnect();
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

    // オーバーレイ窓の表示モードを (probe / nudge) から決める統合 effect。
    //   - プローブ/Nudge:   右上の小ボックスに縮小 + カード以外は OS レベルでクリック透過
    //                       (被験者は作業を続けながら任意のタイミングで応答できる=非ブロック)
    //   - いずれも無し:     退避 (hide() は使わない)
    // ⚠️★★★ **Wall 削除 (2026-08-23) で「全画面 + クリックブロック」は通常経路から消えた。**
    // ★ `applyFullscreenBlock` は **box 化が失敗した環境の縮退路としてのみ**残す。
    useEffect(() => {
        const win = currentWindow;
        // 招待の図像は probe / nudge と同じ箱の仕組みで出す（EH3 では probe も nudge も出ない）。
        const invitationOnly = invitationPresent && !probeActive && !nudgeVisible;
        const visible = probeActive || nudgeVisible || invitationPresent;
        let cancelled = false;

        // ⚠️ 縮退路専用。全画面化は「モニタ全域へ明示 setPosition + setSize」で行う。physical 座標で扱い DPI 二重
        // 変換を避ける。**maximize() は使わない**: macOS で overlay は NSPanel 化済み (decisions D7) で、
        // maximize() が内部で setStyleMask: を呼ぶと WKWebView の contentLayoutRect オブザーバ解除に
        // 失敗して NSRangeException でクラッシュする (実機確認・D8)。
        const applyFullscreenBlock = async () => {
            // 退避後は窓が画面外のため currentMonitor() が null になりうる。primaryMonitor()
            // フォールバックで mon を必ず得て setPosition/setSize を確実に走らせる
            // (mon が null だと 1x1 offscreen のまま縮退が成立しない退行を防ぐ)。
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
            // overlay の中身は idle 時すべて非表示 (ProbeCard=null / Nudge=opacity0) なので
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
                {
                    // 窓を「表示中カードの実寸ちょうど」に縮め、右上へ置く → 窓=カードで透明余白ゼロ。
                    // カード外 (窓外) は他アプリへクリックが通り、カード footprint だけが操作対象になる
                    // (Windows: 透明余白でもクリックを奪う #11461 を、退避でなく実寸縮小で根治)。
                    // unmaximize() は使わない (NSPanel + WKWebView でクラッシュ。D8)。退避後は窓が画面外で
                    // currentMonitor() が null になりうるため resolveShowMonitor (primaryMonitor フォールバック)。
                    const mon = await resolveShowMonitor();
                    if (cancelled) return;
                    const scale = mon?.scaleFactor ?? 1;
                    // 実寸 (未測定なら一瞬のフォールバック)。測定が出たら本 effect が再実行され縮む。
                    const cardSize = invitationOnly
                        ? { w: INVITATION_BOX, h: INVITATION_BOX }
                        : probeActive
                          ? (probeCardSize ?? { w: PROBE_FALLBACK_W, h: PROBE_FALLBACK_H })
                          : (nudgeCardSize ?? { w: NUDGE_FALLBACK_W, h: NUDGE_FALLBACK_H });
                    // 窓がモニタを超えないよう clamp (高 DPI/小画面でカード下端=ボタンが画面外に
                    // 出るのを防ぐ。maxHeight を viewport 非依存にした代償をここで回復する)。
                    const marginPx = Math.round(CARD_SCREEN_MARGIN * scale);
                    let winW = Math.round((cardSize.w + CARD_FIT_PAD) * scale);
                    let winH = Math.round((cardSize.h + CARD_FIT_PAD) * scale);
                    if (mon) {
                        winW = Math.min(winW, mon.size.width - 2 * marginPx);
                        winH = Math.min(winH, mon.size.height - 2 * marginPx);
                    }
                    await win.setSize(new PhysicalSize(winW, winH));
                    if (cancelled) return;
                    if (mon) {
                        // 右上 (画面外に出ないよう clamp)。winW は physical 値なのでそのまま引く。
                        const x = Math.max(
                            mon.position.x,
                            mon.position.x + mon.size.width - winW - marginPx
                        );
                        const y = mon.position.y + marginPx;
                        await win.setPosition(new PhysicalPosition(x, y));
                        if (cancelled) return;
                    }
                    await setOverlayInteractive(true);
                    // 計装: カード実寸 show 後の実窓位置/サイズ (窓=カード実寸に縮んだか)。debug のみ。
                    auditWindowState(`widget-show probe=${probeActive} nudge=${nudgeVisible}`);
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
        // probeCardSize/nudgeCardSize: 実寸測定が出たら窓をカード実寸へ縮め直す (透明余白を消す)。
    }, [probeActive, nudgeVisible, invitationPresent, currentWindow, probeCardSize, nudgeCardSize]);

    // live action が none/defer に変わっても消さない (= ボタンを押す前に勝手に消える問題の修正)。
    useEffect(() => {
        // probe 表示中は nudge を出さない (同じ box に重ねない・MEDIUM 対応)。probe 応答後に出る。
        const isNudge =
            interventionDecision.action === "nudge" && !probeActive;
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
    }, [interventionDecision, probeActive, nudgeVisible, nudgeDismissed]);

    // アンマウント時にタイマーを掃除する。
    useEffect(() => {
        return () => {
            if (nudgeTimerRef.current) clearTimeout(nudgeTimerRef.current);
        };
    }, []);

    return (
        <div className="overlay-root">
            {/* Task C: v0.3 較正のプローブ回答カード (probe_triggered を listen)。
                overlay 窓は tauri-nspanel で非アクティブ Panel 化しクリックを webview へ配送する
                (透明窓でもクリックが届く・フォーカスは奪わない。decisions D7)。 */}
            <ProbeCard onActiveChange={setProbeActive} onResize={handleProbeResize} />

            {/* EH3 の招待の図像（文字なし・固定の大きさ・量を描かない。ADR-026 / R-I1）。 */}
            {invitationPresent && !probeActive && !nudgeVisible && (
                <button
                    type="button"
                    className="invitation-glyph"
                    aria-label="説明と設定を開く"
                    onClick={openInvitationSettings}
                >
                    <InvitationGlyph variant={INVITATION_GLYPH} />
                </button>
            )}

            <aside
                ref={nudgeRef}
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

        </div>
    );
};

export default Overlay;
