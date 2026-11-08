//! メニューバー / タスクトレイの常駐アイコン。
//!
//! # なぜ要るか（★ 2 つの問題が同じ穴だった）
//!
//! 1. ⚠️ **窓を閉じても終了できない。** `lib.rs` は実行時に `overlay` 窓を作るので、
//!    Tauri の「全部の窓が閉じたら終了する」に到達しない。`CloseRequested` を捌く箇所も
//!    無かった（grep 済み）。★ 2026-08-08 に **3 時間動き続けていた `gse-next`
//!    （CPU 157 分・`g1_mode:"marker"` のまま打鍵を記録中）** を実際に見つけた。
//! 2. ⚠️ **計測中かどうかが分からない。** `SessionActive` も `HOOK_ACTIVE` も Rust 側にあるが、
//!    Dashboard を開いていないと見えない。★ いちばん知りたい「窓を閉じた状態」で見えない。
//!
//! → ★ **窓と独立に生き続けるトレイ**に置けば両方解ける。
//!
//! # ⚠️ 盲検（`preregistration.md §2.12`）
//!
//! ★ **認知状態 (Flow / Incubation / Stuck) はここに出さない。** 出すのは
//! 「打鍵を記録しているか」だけである。⚠️ 状態を出すと被験者に仮説が漏れる。
//! `measure_label` が返す 3 つの文字列以外をトレイに載せないこと
//! (`tray_labels_never_leak_cognitive_state` テストで固定してある)。

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;

use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::tray::TrayIconBuilder;
use tauri::AppHandle;

/// トレイに出す「計測の状態」。★ 認知状態ではない。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MeasureState {
    /// セッションが動いていない = 打鍵を記録していない。
    Stopped,
    /// セッション中で、フックも生きている = 正常に記録できている。
    Measuring,
    /// ⚠️ ★ セッション中なのに**フックが死んでいる**。
    ///
    /// macOS の CGEventTap は失効しうる (memory: `macos-tap-idle-away-probe-bug`)。
    /// ★ 今まではこの状態を **画面を見ないと気づけなかった**（しかも気づけた例が無い）。
    /// ⚠️ 気づかないまま続けると、そのブロックは**打鍵ゼロのまま記録される**。
    HookDown,
}

/// 2 つの Atomic から状態を決める純関数。★ Tauri に触らないので単体で検算できる。
pub fn measure_state(session_active: bool, hook_active: bool) -> MeasureState {
    match (session_active, hook_active) {
        (false, _) => MeasureState::Stopped,
        (true, true) => MeasureState::Measuring,
        (true, false) => MeasureState::HookDown,
    }
}

/// トレイに出す文字列。⚠️ ★ **ここに認知状態を書かない**（盲検）。
pub fn measure_label(state: MeasureState) -> &'static str {
    match state {
        MeasureState::Stopped => "GSE — 停止中（記録していません）",
        MeasureState::Measuring => "GSE — 計測中",
        MeasureState::HookDown => "⚠ GSE — 計測できていません（研究者に連絡してください）",
    }
}

/// macOS のメニューバーに出す短い見出し。★ 常時見えるので最小限にする。
///
/// ⚠️ Windows のトレイに題名は出ない（tooltip 側で見せる）。
pub fn measure_title(state: MeasureState) -> &'static str {
    match state {
        MeasureState::Stopped => "○",
        MeasureState::Measuring => "● 計測中",
        MeasureState::HookDown => "⚠ 計測できていません",
    }
}

/// 招待の「印の説明と設定」をトレイに出すか（純関数）。
///
/// EH3 は常に出す（起動時に作る項目・今のまま）。通常のモードは、招待が許されているセッションの間
/// （`NORMAL_INVITATION_ALLOWED` が真の間）だけ出す。第 1 週・セッションが無い・O1・G1 では出さない。
pub fn invitation_item_visible(eh3: bool, normal_allowed: bool) -> bool {
    eh3 || normal_allowed
}

/// いまの状態を Atomic から読む。
///
/// ⚠️★★ 「フックが生きている」は **2 つの AND** である:
/// - `HOOK_ACTIVE` … 設置に成功した (`SetWindowsHookExW` / `CGEventTap`)
/// - `!HOOK_STARVED` … ★ **イベントが実際に届いている** (`input::liveness` が判定)
///
/// 2026-08-09 の Windows 実機では前者だけが `true` のまま、5 分間 0 打のブロックが
/// 「● 計測中」の表示で自動提出された (`windows-verification.md` §5-7)。
/// ★ 純関数 `measure_state()` の意味 (第 2 引数 = 「フックが生きているか」) は変えていない。
/// ⚠️★★★ **O1 (R3-a) では第 1 引数が `session_active` ではない。**
///
/// ★ O1 は「開始する」を押さないので `session_active` は **永久に false** である。
/// そのまま渡すと `measure_state(false, _) == Stopped` → 逐語
/// 「**GSE — 停止中（記録していません）**」を出しながら**実際には記録し続ける**。
/// → ⚠️ **同意文書 §4 の逐語「印が出ていないときは記録していません」と正面から矛盾する。**
/// ★ 判定は `o1::recording_active` (純関数) に置いてある。⚠️ **非 O1 は従来どおり
/// `session_active` そのもの**なので、Phase1 / G1 の表示は 1 バイトも変わらない。
fn current_state(session_active: &AtomicBool) -> MeasureState {
    let installed = crate::input::hook::HOOK_ACTIVE.load(Ordering::Relaxed);
    let starved = crate::input::hook::HOOK_STARVED.load(Ordering::Relaxed);
    measure_state(
        crate::o1::recording_active(
            crate::o1::is_o1(),
            session_active.load(Ordering::Acquire),
            crate::recording::is_paused(),
        ),
        installed && !starved,
    )
}

/// 手跡の「やめる」／「描く」の項目の ID(段 1 の後期・ADR-051)。
const MENU_HANDMARK: &str = "gse-tray-handmark";

/// 手跡のトレイの項目の状態(駆動役が書き、更新スレッドが読む)。0 = 出さない・1 = やめる・2 = 描く。
static HANDMARK_TRAY: std::sync::atomic::AtomicU8 = std::sync::atomic::AtomicU8::new(0);

/// メニューに実際に出している手跡の項目の状態(更新スレッドが書き、押下の処理が読む)。
static HANDMARK_TRAY_SHOWN: std::sync::atomic::AtomicU8 = std::sync::atomic::AtomicU8::new(0);

fn handmark_item_code(t: crate::handmark_driver::TrayItem) -> u8 {
    use crate::handmark_driver::TrayItem;
    match t {
        TrayItem::Hidden => 0,
        TrayItem::Stop => 1,
        TrayItem::Restore => 2,
    }
}

fn handmark_item_from_code(c: u8) -> crate::handmark_driver::TrayItem {
    use crate::handmark_driver::TrayItem;
    match c {
        1 => TrayItem::Stop,
        2 => TrayItem::Restore,
        _ => TrayItem::Hidden,
    }
}

/// 駆動役が手跡の項目の状態を知らせる(項目の出し入れは更新スレッドが 1 秒ごとに行う)。
pub fn set_handmark_item(t: crate::handmark_driver::TrayItem) {
    HANDMARK_TRAY.store(handmark_item_code(t), Ordering::Release);
}

/// メニュー項目の ID。
const MENU_QUIT: &str = "gse-tray-quit";
const MENU_STATUS: &str = "gse-tray-status";
/// EH3: 招待の説明と設定の窓を開く（招待を止めた後でも、ここから戻せる・ADR-035 D1 / D2）。
const MENU_INVITATION: &str = "gse-tray-invitation";
/// EH3: 肖像を止めて元の壁紙に戻す（いつでも・記録しない・R-P8 / R-P9）。
const MENU_PORTRAIT_STOP: &str = "gse-tray-portrait-stop";

/// トレイを作り、1Hz で状態を追う更新スレッドを起こす。
///
/// ★ 更新を polling にしているのは、セッションの on/off が
/// `start_session` / ブロック自動終了 / 停止 と**複数の箇所**で切り替わるためである。
/// ⚠️ 呼び出し側に通知を足して回ると、足し忘れた経路だけ古い表示が残る
/// （★ 静かに間違う）。1Hz の読み取りは `FeatSnapshot` のゲートと同じ粒度で、費用も無い。
/// ⚠️ ★ ランタイムは `Wry` に固定する（generic にしない）。
/// `TrayIconBuilder::build` が `Manager<Wry>` を要求するうえ、終了経路
/// (`crate::shutdown_and_exit`) も `AppHandle<Wry>` を取る。★ generic にすると
/// 呼び出し側で必ず型が合わなくなる（実際に合わずに落ちた）。
pub fn setup(app: &AppHandle, session_active: Arc<AtomicBool>) -> tauri::Result<()> {
    // ★ 初期値を決め打ちにしない。⚠️ `false, false` と書くと、setup の順序が変わったときに
    //   **最大 1 秒間だけ嘘を表示する**（2026-08-08 の cross-review）。実際の値から始める。
    let initial = current_state(&session_active);
    // ⚠️★★ **初期状態もログに残す** (2026-08-27)。★ 更新スレッドは**変化したときだけ**
    //   書くので、初期値のまま動き続けたセッションは `gse-app.log` から
    //   「トレイに何が出ていたか」を**事後に確認できなかった**。
    //   ★ O1 は「記録しているのに『記録していません』と出ていないか」を後から検証する
    //   必要がある (同意文書 §4 の逐語) ので、1 行だけ残す。
    tracing::info!(
        o1_mode = ?crate::o1::mode(),
        paused = crate::recording::is_paused(),
        "tray state (initial) -> {:?} ({})",
        initial,
        measure_label(initial)
    );

    // ★ 状態表示は**押せない項目**にする（押しても何も起きないのに押させない）。
    let status = MenuItem::with_id(
        app,
        MENU_STATUS,
        measure_label(initial),
        false,
        None::<&str>,
    )?;
    let quit = MenuItem::with_id(app, MENU_QUIT, "GSE を終了", true, None::<&str>)?;
    let separator = PredefinedMenuItem::separator(app)?;
    // 通常のモード用: 招待が許されている間だけ後から差し込む項目（EH3 は下の静的な項目を使う）。
    let dynamic_invitation = if crate::eh3::is_eh3() {
        None
    } else {
        Some(MenuItem::with_id(
            app,
            MENU_INVITATION,
            "印の説明と設定",
            true,
            None::<&str>,
        )?)
    };
    let menu = if crate::eh3::is_eh3() {
        let invitation =
            MenuItem::with_id(app, MENU_INVITATION, "印の説明と設定", true, None::<&str>)?;
        let portrait_stop = MenuItem::with_id(
            app,
            MENU_PORTRAIT_STOP,
            "壁紙を元に戻す",
            true,
            None::<&str>,
        )?;
        Menu::with_items(
            app,
            &[&status, &separator, &invitation, &portrait_stop, &quit],
        )?
    } else {
        Menu::with_items(app, &[&status, &separator, &quit])?
    };

    let mut builder = TrayIconBuilder::with_id("gse-tray")
        .menu(&menu)
        .tooltip(measure_label(initial))
        .title(measure_title(initial))
        // ★ アイコンだけを左クリックしてもメニューを出す（macOS の既定に合わせる）。
        .show_menu_on_left_click(true)
        .on_menu_event(|app, event| {
            if event.id.as_ref() == MENU_QUIT {
                tracing::info!("tray: quit requested");
                // 段 1 では日の終わりの問いを挟みうる（段 1 でなければ今のまま `shutdown_and_exit`）。
                crate::request_quit(app);
            } else if event.id.as_ref() == MENU_PORTRAIT_STOP {
                // ⚠️ 選んだことは記録しない（applog にも出さない・R-P9）。
                crate::stop_portrait_by_person();
            } else if event.id.as_ref() == MENU_HANDMARK {
                // ⚠️ 選んだことは applog にも出さない(日の行に切った／戻した時刻が残るだけ)。
                // 押された項目の文言(メニューに出ていた状態)を渡し、駆動役の今の状態と照らす
                crate::handmark_toggle_from_tray(
                    app,
                    handmark_item_from_code(HANDMARK_TRAY_SHOWN.load(Ordering::Acquire)),
                );
            } else if event.id.as_ref() == MENU_INVITATION {
                // ⚠️ 開いたことは記録しない（applog にも出さない・R-I1）。
                let _ = crate::show_invitation_settings_window(app);
            }
        });
    if let Some(icon) = app.default_window_icon() {
        builder = builder.icon(icon.clone());
    }
    let tray = builder.build(app)?;
    // 手跡の項目(今日の割付が出す日のときだけ駆動役が `Hidden` 以外にする)
    let handmark_menu_item = MenuItem::with_id(app, MENU_HANDMARK, "やめる", true, None::<&str>)?;

    std::thread::Builder::new()
        .name("gse-tray".to_string())
        .spawn(move || {
            let mut last = initial;
            // 通常のモード: 項目をいま差し込んでいるか
            let mut invitation_shown = false;
            // 差し込みの失敗は最初の 1 回だけ警告する(毎秒の連投を避ける・内容は書かない)
            let mut insert_failure_warned = false;
            // 手跡の項目をいま差し込んでいる文言
            let mut handmark_shown = crate::handmark_driver::TrayItem::Hidden;
            loop {
                std::thread::sleep(Duration::from_millis(1000));
                // ★ 終了処理が始まったら抜ける。⚠️ 落ちるまでの数百 ms のあいだ
                //   トレイを触り続けると、破棄済みのハンドルに書きに行くことになる。
                if crate::is_shutting_down() {
                    tracing::info!("tray updater stopping (shutdown in progress)");
                    return;
                }
                // ⚠️ 項目の出し入れは記録しない（applog にも出さない・R-I1）。
                if let Some(item) = dynamic_invitation.as_ref() {
                    let want =
                        invitation_item_visible(false, crate::normal_invitation_allowed_now());
                    if want && !invitation_shown {
                        // 状態表示・区切りの次（静的な並びの「印の説明と設定」と同じ位置）
                        invitation_shown = menu.insert(item, 2).is_ok();
                        if !invitation_shown && !insert_failure_warned {
                            insert_failure_warned = true;
                            tracing::warn!("tray invitation item could not be inserted");
                        }
                    } else if !want && invitation_shown && menu.remove(item).is_ok() {
                        invitation_shown = false;
                    }
                }
                // 手跡の項目: 状態が変わったときだけ触る(出し入れは記録しない)
                let want = handmark_item_from_code(HANDMARK_TRAY.load(Ordering::Acquire));
                if want != handmark_shown {
                    match want.label() {
                        None => {
                            if menu.remove(&handmark_menu_item).is_ok() {
                                handmark_shown = want;
                                HANDMARK_TRAY_SHOWN
                                    .store(handmark_item_code(want), Ordering::Release);
                            }
                        }
                        Some(label) => {
                            let _ = handmark_menu_item.set_text(label);
                            let inserted = handmark_shown
                                != crate::handmark_driver::TrayItem::Hidden
                                || menu.insert(&handmark_menu_item, 2).is_ok();
                            if inserted {
                                handmark_shown = want;
                            }
                        }
                    }
                }
                let next = current_state(&session_active);
                if next == last {
                    continue; // ★ 変わっていないなら触らない（無用な UI 更新を出さない）
                }
                last = next;
                // ⚠️ ★ 「計測できていません」は**ログにも残す**。トレイは後から読み返せない
                //   （`gse-app.log` があれば研究者が後から追える）。
                if next == MeasureState::HookDown {
                    tracing::error!(
                        "keyboard hook is down while a session is active; \
                         keystrokes are NOT being recorded"
                    );
                } else {
                    tracing::info!("tray state -> {:?}", next);
                }
                let _ = status.set_text(measure_label(next));
                let _ = tray.set_tooltip(Some(measure_label(next)));
                let _ = tray.set_title(Some(measure_title(next)));
            }
        })?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stopped_when_no_session_regardless_of_hook() {
        assert_eq!(measure_state(false, false), MeasureState::Stopped);
        assert_eq!(measure_state(false, true), MeasureState::Stopped);
    }

    #[test]
    fn measuring_only_when_session_and_hook_are_both_up() {
        assert_eq!(measure_state(true, true), MeasureState::Measuring);
    }

    /// ⚠️★★ ここがこの機能のいちばんの値打ち。
    ///
    /// セッション中にフックが死ぬ (macOS の CGEventTap 失効) と、
    /// ★ **打鍵ゼロのブロックが静かに記録される**。今までは気づく手段が無かった。
    #[test]
    fn hook_down_is_distinguished_from_stopped() {
        let s = measure_state(true, false);
        assert_eq!(s, MeasureState::HookDown);
        assert_ne!(
            s,
            MeasureState::Stopped,
            "★ 「止めた」と「壊れている」を同じ表示にしてはならない"
        );
        assert!(
            measure_label(s).contains("計測できていません"),
            "★ 異常だと分かる言葉になっていない: {}",
            measure_label(s)
        );
    }

    /// ⚠️ ★ 盲検: トレイに認知状態を出さない (`preregistration.md §2.12`)。
    ///
    /// ★ ここを緩めると、被験者はトレイを見るだけで「いま Stuck 判定だ」と分かってしまう。
    #[test]
    fn tray_labels_never_leak_cognitive_state() {
        let banned = [
            "Flow",
            "flow",
            "Incubation",
            "incubation",
            "Stuck",
            "stuck",
            "フロー",
            "インキュベーション",
            "スタック",
            "停滞",
            "沈思",
            "確率",
            "p_",
        ];
        for state in [
            MeasureState::Stopped,
            MeasureState::Measuring,
            MeasureState::HookDown,
        ] {
            // 手跡の「やめる」／「描く」も同じ禁止語の対象(状態に依らない文言)
            let handmark = [
                crate::handmark_driver::TrayItem::Stop.label().unwrap_or(""),
                crate::handmark_driver::TrayItem::Restore
                    .label()
                    .unwrap_or(""),
            ];
            for text in [
                measure_label(state),
                measure_title(state),
                handmark[0],
                handmark[1],
            ] {
                for word in banned {
                    assert!(
                        !text.contains(word),
                        "★ トレイの文言に非開示語 {word:?} が入っている: {text:?}"
                    );
                }
            }
        }
    }

    /// 手跡のトレイの文言(「やめる」／「描く」)も非開示語を含まず、手跡の語を出さない。
    #[test]
    fn handmark_tray_labels_are_plain() {
        use crate::handmark_driver::TrayItem;
        let banned = [
            "Flow",
            "flow",
            "Incubation",
            "incubation",
            "Stuck",
            "stuck",
            "フロー",
            "スタック",
            "停滞",
            "確率",
            "p_",
            "手跡",
            "Handmark",
            "handmark",
            "背景",
            "状態",
        ];
        for t in [TrayItem::Stop, TrayItem::Restore] {
            let label = t.label().expect("label");
            for w in banned {
                assert!(!label.contains(w), "{label:?} has {w:?}");
            }
        }
        assert_eq!(TrayItem::Hidden.label(), None);
        for t in [TrayItem::Hidden, TrayItem::Stop, TrayItem::Restore] {
            assert_eq!(handmark_item_from_code(handmark_item_code(t)), t);
        }
    }

    /// 招待の項目の出し入れ: EH3 は常に、通常のモードは許されている間だけ。
    #[test]
    fn invitation_item_visibility() {
        assert!(invitation_item_visible(true, false));
        assert!(invitation_item_visible(true, true));
        assert!(invitation_item_visible(false, true));
        assert!(!invitation_item_visible(false, false));
    }

    /// 3 状態が**互いに違う文言**であること（同じだと区別できない）。
    #[test]
    fn all_three_states_are_visually_distinct() {
        let labels = [
            measure_label(MeasureState::Stopped),
            measure_label(MeasureState::Measuring),
            measure_label(MeasureState::HookDown),
        ];
        let titles = [
            measure_title(MeasureState::Stopped),
            measure_title(MeasureState::Measuring),
            measure_title(MeasureState::HookDown),
        ];
        for set in [labels, titles] {
            assert_eq!(
                std::collections::HashSet::from(set).len(),
                3,
                "★ 3 状態のうち 2 つが同じ文言になっている: {set:?}"
            );
        }
    }
}
