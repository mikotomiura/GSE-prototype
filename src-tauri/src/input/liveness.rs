//! キーボードフックが「生きているか」を、**フックとは独立した情報源**で確かめる。
//!
//! ## ⚠️★★ なぜ要るか (2026-08-09 の Windows 実機)
//!
//! G1 の 1 ブロック (5 分) が **打鍵 1 件のまま「正常なブロック」として自動提出された**。
//! アプリ側に異常を示すログは 1 行も無く、トレイは終始「● 計測中」だった。
//! 一次記録: `experiments/20260801-controlled-friction-task/windows-verification.md` §5-7。
//!
//! 構造的な理由は 2 つある:
//!
//! 1. `HOOK_ACTIVE` は **`SetWindowsHookExW` が成功した**ことしか意味しない
//!    (`hook_windows.rs`)。OS が低レベルフックを黙って外しても `true` のままである。
//! 2. フックスレッドのメッセージループは **`WM_QUIT` でしか抜けない**ので、
//!    再設置経路 (`Keyboard hook message loop exited`) も発火しない。
//!    ★ 実測: 当該ログでその行は **0 件**、対照の `Keyboard hook installed` は 3 件。
//!
//! → ★ **「設置済み」と「イベントが届いている」を別の概念として分ける**のが本モジュールである。
//!
//! ## 設計
//!
//! - **測る**: `last_system_input_tick()` = OS が持つ「最後の入力時刻」の**生 tick**。
//!   ★ 値の**変化**しか見ないので、絶対時刻へ変換せず、⚠️ 32bit tick のラップアラウンドも
//!   踏まない (等値比較なので巻き戻っても壊れない)。
//!   ⚠️ ★ **キーの内容も種別も読まない** (`data-privacy`)。得られるのは「何か入力があったか」だけ。
//! - **判断する**: `step()` / `health()` は **OS 非依存の純関数**。閾値は引数
//!   (`Thresholds`) なので、境界を単体テストで固定できる。
//! - **配線する**: `lib.rs` の 1 Hz 監視スレッド。⚠️ ★ **トレイのスレッドには載せない**
//!   (トレイは生成に失敗しうるので、そこに載せると検知ごと消える)。
//!
//! ## ⚠️ 既知の限界 (★ 隠さずテストで固定してある)
//!
//! `GetLastInputInfo` は **マウスも含む**。したがって「2 分間ずっと読んで
//! スクロールしていただけ」も **starvation として数えられる** (= 誤検知しうる)。
//! ★ だから NDJSON には**判断ではなく測った量** (`starved_ms`) を残し、
//! 後から閾値を変えて再解釈できるようにする。

/// フックの健康状態。★ 認知状態ではない (盲検)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HookHealth {
    /// 正常、または判断材料が無い。
    Ok,
    /// ⚠️ 疑わしい。★ ログにだけ残す段階 (トレイは変えない)。
    Suspect,
    /// ⚠️★ 届いていないとみなす段階。トレイを「計測できていません」にし、再設置を要求する。
    Down,
}

/// 判定のしきい値 (ms)。★ **定数ではなく値**にしてあるのは、境界をテストで固定するため。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Thresholds {
    /// この時間 starve したら `Suspect` (ログに 1 回だけ `ERROR`)。
    pub log_after_ms: u64,
    /// この時間 starve したら `Down` (トレイ表示 + 再設置)。
    pub down_after_ms: u64,
}

impl Default for Thresholds {
    /// 既定は 30 秒 / 120 秒 (二段)。
    ///
    /// ⚠️ ★ トレイ側を長く取るのは、**被験者の目に入る警告**だからである
    /// (マウス中心の作業で誤検知しうる)。ログ側は研究者が後から読むので短くてよい。
    fn default() -> Self {
        Self {
            log_after_ms: 30_000,
            down_after_ms: 120_000,
        }
    }
}

/// 「システムには入力があるのに、自前のフックには何も来ていない」時間の累積。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Starvation {
    pub starved_ms: u64,
}

/// 1 tick 分の状態遷移。★ **純関数**。時計もグローバルも触らない。
///
/// - `session_active`: 計測中か。⚠️ 非計測中は打鍵が無くて当たり前なので数えない。
/// - `system_input_seen`: この tick の間に **OS 側の最終入力時刻が変化した**か
///   (= 誰かがキーかマウスを触った)。
/// - `hook_event_seen`: この tick の間に **自前のフックが呼ばれた**か。
/// - `tick_ms`: この tick の長さ。
///
/// ★ 「システム入力が無い」ときは **進めも戻しもしない** (`prev` をそのまま返す)。
/// ⚠️ 本人が席を外しているだけの沈黙を starvation として数えないためである。
pub fn step(
    prev: Starvation,
    session_active: bool,
    system_input_seen: bool,
    hook_event_seen: bool,
    tick_ms: u64,
) -> Starvation {
    if !session_active || hook_event_seen {
        // ★ 届いた瞬間に 0 へ戻す (復帰の判定はここに集約する)。
        return Starvation { starved_ms: 0 };
    }
    if !system_input_seen {
        // 判断材料が無い = 凍結する。
        return prev;
    }
    Starvation {
        starved_ms: prev.starved_ms.saturating_add(tick_ms),
    }
}

/// 累積 starvation を健康状態へ写す。★ 純関数。
pub fn health(s: Starvation, th: Thresholds) -> HookHealth {
    if s.starved_ms >= th.down_after_ms {
        HookHealth::Down
    } else if s.starved_ms >= th.log_after_ms {
        HookHealth::Suspect
    } else {
        HookHealth::Ok
    }
}

/// OS が持つ「最後の入力時刻」の生 tick。⚠️ ★ **値の変化だけを見る**こと。
///
/// `None` は「この OS では判断材料が無い」を意味し、呼び出し側は
/// `system_input_seen = false` として扱う (= starvation を進めない = 安全側)。
#[cfg(target_os = "windows")]
pub fn last_system_input_tick() -> Option<u32> {
    use windows::Win32::UI::Input::KeyboardAndMouse::{GetLastInputInfo, LASTINPUTINFO};

    let mut lii = LASTINPUTINFO {
        cbSize: std::mem::size_of::<LASTINPUTINFO>() as u32,
        dwTime: 0,
    };
    // SAFETY: `lii` は正しい `cbSize` を持つローカル変数で、API は当該構造体へ
    // 書き込むだけである (ポインタを保持しない)。失敗時は戻り値 FALSE で判別する。
    let ok = unsafe { GetLastInputInfo(&mut lii) };
    if ok.as_bool() {
        Some(lii.dwTime)
    } else {
        None
    }
}

/// macOS 等: 判断材料が無い。★ D-4 により配線は次タスク
/// (`CGEventSourceSecondsSinceLastEventType` は別の実測が要る)。
#[cfg(not(target_os = "windows"))]
pub fn last_system_input_tick() -> Option<u32> {
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    const TICK: u64 = 1_000;

    fn th() -> Thresholds {
        Thresholds {
            log_after_ms: 30_000,
            down_after_ms: 120_000,
        }
    }

    /// 正常: フックが呼ばれ続けている → 何度回しても `Ok` で 0 のまま。
    #[test]
    fn healthy_hook_never_starves() {
        let mut s = Starvation::default();
        for _ in 0..300 {
            s = step(s, true, true, true, TICK);
        }
        assert_eq!(s.starved_ms, 0);
        assert_eq!(health(s, th()), HookHealth::Ok);
    }

    /// ★★ 本命: システムには入力があるのにフックが呼ばれない → 30 秒で Suspect、120 秒で Down。
    #[test]
    fn silent_hook_is_detected_at_both_thresholds() {
        let mut s = Starvation::default();
        for _ in 0..29 {
            s = step(s, true, true, false, TICK);
        }
        assert_eq!(health(s, th()), HookHealth::Ok, "29 秒ではまだ Ok");

        s = step(s, true, true, false, TICK);
        assert_eq!(s.starved_ms, 30_000);
        assert_eq!(
            health(s, th()),
            HookHealth::Suspect,
            "30 秒ちょうどで Suspect"
        );

        for _ in 0..89 {
            s = step(s, true, true, false, TICK);
        }
        assert_eq!(
            health(s, th()),
            HookHealth::Suspect,
            "119 秒ではまだ Suspect"
        );

        s = step(s, true, true, false, TICK);
        assert_eq!(s.starved_ms, 120_000);
        assert_eq!(health(s, th()), HookHealth::Down, "120 秒ちょうどで Down");
    }

    /// ⚠️★ **既知の誤検知を仕様として固定する**: マウスだけ動かしている人も Down になる。
    ///
    /// ★ `GetLastInputInfo` はマウスを含むので、キーボードだけを見分けることはできない。
    /// この挙動を「バグ」ではなく「限界」として明示的に残す。
    /// → だから NDJSON には `starved_ms` を載せ、**後から再解釈できる**ようにしてある。
    #[test]
    fn mouse_only_work_is_a_known_false_positive() {
        let mut s = Starvation::default();
        for _ in 0..120 {
            // system_input_seen = true (マウス) / hook_event_seen = false (打鍵なし)
            s = step(s, true, true, false, TICK);
        }
        assert_eq!(
            health(s, th()),
            HookHealth::Down,
            "マウスのみの作業は Down に化ける (既知の限界)"
        );
    }

    /// 計測していないときは数えない。
    #[test]
    fn inactive_session_never_starves() {
        let mut s = Starvation::default();
        for _ in 0..300 {
            s = step(s, false, true, false, TICK);
        }
        assert_eq!(s.starved_ms, 0);
        assert_eq!(health(s, th()), HookHealth::Ok);
    }

    /// 誰も何も触っていない沈黙は starvation ではない (凍結する)。
    #[test]
    fn no_system_input_freezes_instead_of_accumulating() {
        let mut s = Starvation::default();
        for _ in 0..40 {
            s = step(s, true, true, false, TICK); // まず 40 秒 starve させる
        }
        let frozen = s.starved_ms;
        assert_eq!(frozen, 40_000);
        for _ in 0..600 {
            s = step(s, true, false, false, TICK); // 10 分間、誰も触らない
        }
        assert_eq!(s.starved_ms, frozen, "沈黙中は進まない");
        assert_eq!(
            health(s, th()),
            HookHealth::Suspect,
            "Down へ勝手に落ちない"
        );
    }

    /// 復帰: フックが 1 回でも呼ばれたら 0 に戻る。
    #[test]
    fn recovery_resets_to_zero() {
        let mut s = Starvation::default();
        for _ in 0..200 {
            s = step(s, true, true, false, TICK);
        }
        assert_eq!(health(s, th()), HookHealth::Down);
        s = step(s, true, true, true, TICK);
        assert_eq!(s.starved_ms, 0);
        assert_eq!(health(s, th()), HookHealth::Ok);
    }

    /// ★ 判断材料が無い OS (macOS 等) では安全側 = 何も起きない。
    #[test]
    fn platform_without_a_source_never_reports_down() {
        // `last_system_input_tick()` が None のとき、呼び出し側は
        // `system_input_seen = false` を渡す契約である。
        let mut s = Starvation::default();
        for _ in 0..600 {
            s = step(s, true, false, false, TICK);
        }
        assert_eq!(s.starved_ms, 0);
        assert_eq!(health(s, th()), HookHealth::Ok);
    }
}
