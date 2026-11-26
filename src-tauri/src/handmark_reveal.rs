//! 手跡の「ほかの窓をどける」（段 1 の 3 名の版・ADR-051・handmark-reveal-count）の OS に依らない判定。
//!
//! どけるときは、押した時に見えていた他のアプリ（macOS）・窓（Windows）だけを覚え、戻すときはそれだけを戻す
//! （window-boundary 判断 5・handmark-reveal-count 判断 3）。覚えた一覧は OS の層のメモリにだけ置き、
//! 記録・tracing に出さない。窓の題名やアプリの名前は読まない（判定に使うのは種類と状態の真偽だけ）。
//!
//! OS の呼び出しは `handmark_reveal_macos.rs` と `handmark_reveal_windows.rs`。ここは cfg なしで、両 OS の
//! CI のテストで縛る。

/// デスクトップとタスクバーの窓のクラス名（Windows）。どけない（デスクトップごと消すと背景の層が見えなくなる）。
pub const SHELL_CLASSES: [&str; 4] = [
    "Progman",
    "WorkerW",
    "Shell_TrayWnd",
    "Shell_SecondaryTrayWnd",
];

/// Windows のトップレベルの窓 1 枚の、どけるかどうかを決める属性（真偽だけ）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct WinWindow {
    pub visible: bool,
    pub minimized: bool,
    /// DWM で隠されている（別の仮想デスクトップ・ストアのアプリの休止など）。
    pub cloaked: bool,
    /// 持ち主の窓がある（ダイアログ・浮いた道具の窓。持ち主と一緒に動く）。
    pub has_owner: bool,
    pub tool_window: bool,
    /// `WS_EX_APPWINDOW`（持ち主があってもタスクバーに出る窓）。
    pub app_window: bool,
    /// GSE 自身の窓（背景の層・帯・overlay）。
    pub own_process: bool,
    pub shell_class: bool,
}

/// クラス名がデスクトップかタスクバーの窓か。
pub fn is_shell_class(name: &str) -> bool {
    SHELL_CLASSES.contains(&name)
}

/// Windows: この窓をどけるか。見えていて、最小化されておらず、DWM で隠されておらず、GSE 自身でもシェルでもなく、
/// タスクバーに出る種類の窓（持ち主が無く道具の窓でない、または `WS_EX_APPWINDOW`）だけ。
pub fn is_windows_candidate(w: &WinWindow) -> bool {
    w.visible
        && !w.minimized
        && !w.cloaked
        && !w.own_process
        && !w.shell_class
        && (w.app_window || (!w.has_owner && !w.tool_window))
}

/// macOS: このアプリを覚えて隠すか。窓を持てるアプリ（起動の方針が `Prohibited` でない＝Dock に出る通常の
/// アプリと、Dock に出ないが窓を出せるメニューバーのアプリ）で、隠れておらず、GSE 自身でないものだけ。
/// `hideOtherApplications` はこの両方を隠すので、両方を覚えないと戻らないものが出る（レビュー MEDIUM）。
/// もともと隠していたアプリは覚えないので、戻すときにも出さない。
pub fn is_mac_candidate(can_have_windows: bool, hidden: bool, own: bool) -> bool {
    can_have_windows && !hidden && !own
}

/// 戻す順。覚えた一覧は上から下（`EnumWindows` の重なり順）なので、下から戻して元の重なりに近づける。
pub fn restore_order<T: Copy>(remembered: &[T]) -> Vec<T> {
    remembered.iter().rev().copied().collect()
}

/// Windows: 覚えた窓を戻すか。まだ在り、覚えたときと同じプロセスの窓で、最小化されたままのときだけ
/// （その間に本人が戻した窓・閉じた窓・閉じた後にハンドルが別のプロセスの窓へ使い回されたものには触らない。
/// 同じプロセスの中での使い回しまでは見分けない）。
pub fn should_restore_window(exists: bool, same_process: bool, minimized: bool) -> bool {
    exists && same_process && minimized
}

#[cfg(test)]
mod tests {
    use super::*;

    fn normal() -> WinWindow {
        WinWindow {
            visible: true,
            ..WinWindow::default()
        }
    }

    #[test]
    fn a_plain_visible_app_window_is_a_candidate() {
        assert!(is_windows_candidate(&normal()));
    }

    #[test]
    fn hidden_minimized_cloaked_own_and_shell_windows_are_not_candidates() {
        for w in [
            WinWindow {
                visible: false,
                ..normal()
            },
            WinWindow {
                minimized: true,
                ..normal()
            },
            WinWindow {
                cloaked: true,
                ..normal()
            },
            WinWindow {
                own_process: true,
                ..normal()
            },
            WinWindow {
                shell_class: true,
                ..normal()
            },
        ] {
            assert!(!is_windows_candidate(&w), "{w:?}");
        }
    }

    #[test]
    fn owned_and_tool_windows_are_skipped_unless_they_are_app_windows() {
        let owned = WinWindow {
            has_owner: true,
            ..normal()
        };
        let tool = WinWindow {
            tool_window: true,
            ..normal()
        };
        assert!(!is_windows_candidate(&owned));
        assert!(!is_windows_candidate(&tool));
        assert!(is_windows_candidate(&WinWindow {
            app_window: true,
            ..owned
        }));
        assert!(is_windows_candidate(&WinWindow {
            app_window: true,
            ..tool
        }));
        // app_window でも、見えていなければ・GSE 自身なら候補でない
        assert!(!is_windows_candidate(&WinWindow {
            app_window: true,
            own_process: true,
            ..owned
        }));
    }

    #[test]
    fn shell_classes_are_recognised_exactly() {
        for c in SHELL_CLASSES {
            assert!(is_shell_class(c));
        }
        assert!(!is_shell_class("progman"));
        assert!(!is_shell_class("Notepad"));
        assert!(!is_shell_class(""));
    }

    #[test]
    fn mac_candidates_are_visible_regular_other_apps() {
        assert!(is_mac_candidate(true, false, false));
        assert!(!is_mac_candidate(false, false, false), "窓を持てないアプリ");
        assert!(!is_mac_candidate(true, true, false), "もともと隠していた");
        assert!(!is_mac_candidate(true, false, true), "GSE 自身");
    }

    #[test]
    fn restore_goes_from_the_bottom_up_and_only_touches_still_minimized_windows() {
        assert_eq!(restore_order(&[1, 2, 3]), vec![3, 2, 1]);
        assert!(restore_order::<u8>(&[]).is_empty());
        assert!(should_restore_window(true, true, true));
        assert!(!should_restore_window(true, true, false), "本人が戻した窓");
        assert!(!should_restore_window(false, true, true), "閉じた窓");
        assert!(
            !should_restore_window(true, false, true),
            "ハンドルが別のプロセスの窓に使い回された"
        );
    }
}
