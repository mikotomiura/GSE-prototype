//! 参照入力欄の核（OS 非依存）: IME のメッセージ・呼び出しを `gt/1` の 1 行にする。
//!
//! ⚠️★★★ content-free: `Ev` のどのバリアントも文字列型（`String` / `&str` / `char`）を持たない。
//! 記録するのは**種別・フラグ・長さ・時刻**だけで、確定文字列・未確定文字列は型の上で運べない。
//! ★ 形の契約は `kit/formats/FORMATS.md` の `gt/1`。検査は `kit/formats/validate_logs.py --kind gt`。
//! ⚠️ JSON は手書き（整数と列挙の名前だけなのでエスケープが要らない。serde は使わない）。
//! ⚠️ 区切りに空白を入れない・エスケープを使わない・BOM を付けない（FORMATS.md「共通」）。

/// `gt/1` のヘッダの `format`。
pub const GT_FORMAT: &str = "gt/1";

/// 参照入力欄の経路（`gt/1` の `src`）。Windows の 2 経路だけ（macOS は別の部品が出す）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Src {
    /// IMM 互換（自窓の `WM_IME_*` / `IMN_*`）。issue 008。
    WinImm,
    /// TSF 直受け。issue 009。
    WinTsf,
}

impl Src {
    fn name(self) -> &'static str {
        match self {
            Src::WinImm => "win_imm",
            Src::WinTsf => "win_tsf",
        }
    }
}

/// 候補窓・読み窓などの UI 要素の種類（`ui_kind`）。列挙だけ。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum UiKind {
    Candidate,
    Reading,
    Other,
}

impl UiKind {
    fn name(self) -> &'static str {
        match self {
            UiKind::Candidate => "candidate",
            UiKind::Reading => "reading",
            UiKind::Other => "other",
        }
    }
}

/// 記録する事象。⚠️★★★ どのバリアントも文字列を持たない（整数・列挙・真偽値だけ）。
/// 長さはすべて **UTF-16 のコード単位数**。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ev {
    /// `WM_IME_STARTCOMPOSITION`
    StartComp,
    /// `WM_IME_COMPOSITION`: `lParam` の GCS_* のビットと、`GCS_COMPSTR` / `GCS_RESULTSTR` の長さ。
    Comp {
        flags: u32,
        comp_len: u32,
        result_len: u32,
    },
    /// `WM_IME_ENDCOMPOSITION`
    EndComp,
    /// `WM_IME_NOTIFY` の `wParam`（IMN_* の値）
    Notify { imn: u32 },
    /// `WM_KEYDOWN` の仮想キーコード。IME が処理中なら `VK_PROCESSKEY`（0xE5）になるが、そのまま記録する。
    KeyDown { vk: u32 },
    /// `WM_SETFOCUS`
    FocusIn,
    /// `WM_KILLFOCUS`
    FocusOut,
    /// issue 009: `OnStartComposition`
    TsfStart,
    /// issue 009: `OnUpdateComposition`（長さは範囲の `cch` だけ）
    TsfUpdate { len: u32 },
    /// issue 009: `OnEndComposition`
    TsfEnd { result_len: Option<u32> },
    /// issue 009: `ITfUIElementSink::BeginUIElement`
    UiBegin { kind: UiKind },
    /// issue 009: `ITfUIElementSink::UpdateUIElement`
    UiUpdate { kind: UiKind },
    /// issue 009: `ITfUIElementSink::EndUIElement`
    UiEnd { kind: UiKind },
}

/// `gt/1` のヘッダ 1 行（末尾の改行なし）。`os` は常に `windows`。
///
/// ⚠️ `app_version` は `^[0-9A-Za-z.+-]{1,32}$` に収まる値だけを渡すこと（検査器がそれ以外を拒否する。
/// ここでは JSON のエスケープを避けるために、範囲外の文字を `_` に置き換える）。
pub fn header(src: Src, app_version: &str) -> String {
    let mut ver: String = app_version
        .chars()
        .take(32)
        .map(|c| {
            if c.is_ascii_alphanumeric() || matches!(c, '.' | '+' | '-') {
                c
            } else {
                '_'
            }
        })
        .collect();
    if ver.is_empty() {
        ver.push('0');
    }
    format!(
        "{{\"kind\":\"header\",\"format\":\"{}\",\"src\":\"{}\",\"app_version\":\"{}\",\"os\":\"windows\"}}",
        GT_FORMAT,
        src.name(),
        ver
    )
}

/// 事象 1 件の `gt/1` の行（末尾の改行なし）。
pub fn line(ev: Ev, t_wall_ms: u64, t_mono_ns: u64) -> String {
    let (name, tail) = match ev {
        Ev::StartComp => ("start_comp", String::new()),
        Ev::Comp {
            flags,
            comp_len,
            result_len,
        } => (
            "comp",
            format!(",\"flags\":{flags},\"comp_len\":{comp_len},\"result_len\":{result_len}"),
        ),
        Ev::EndComp => ("end_comp", String::new()),
        Ev::Notify { imn } => ("notify", format!(",\"imn\":{imn}")),
        Ev::KeyDown { vk } => ("key_down", format!(",\"vk\":{vk}")),
        Ev::FocusIn => ("focus_in", String::new()),
        Ev::FocusOut => ("focus_out", String::new()),
        Ev::TsfStart => ("tsf_start", String::new()),
        Ev::TsfUpdate { len } => ("tsf_update", format!(",\"len\":{len}")),
        Ev::TsfEnd { result_len: None } => ("tsf_end", String::new()),
        Ev::TsfEnd {
            result_len: Some(n),
        } => ("tsf_end", format!(",\"result_len\":{n}")),
        Ev::UiBegin { kind } => ("ui_begin", format!(",\"ui_kind\":\"{}\"", kind.name())),
        Ev::UiUpdate { kind } => ("ui_update", format!(",\"ui_kind\":\"{}\"", kind.name())),
        Ev::UiEnd { kind } => ("ui_end", format!(",\"ui_kind\":\"{}\"", kind.name())),
    };
    format!("{{\"kind\":\"ev\",\"t_wall_ms\":{t_wall_ms},\"t_mono_ns\":{t_mono_ns},\"ev\":\"{name}\"{tail}}}")
}

/// `gt/1` の行に現れてよいキー（FORMATS.md の `gt/1` の表にある名前だけ）。
const KEYS: &[&str] = &[
    "kind",
    "format",
    "src",
    "app_version",
    "os",
    "t_wall_ms",
    "t_mono_ns",
    "ev",
    "flags",
    "comp_len",
    "result_len",
    "imn",
    "vk",
    "len",
    "ui_kind",
];

/// 文字列の値として現れてよい列挙（`app_version` だけは別に版の形で検査する）。
const ENUM_VALUES: &[&str] = &[
    "header",
    "ev",
    "gt/1",
    "win_imm",
    "win_tsf",
    "windows",
    "start_comp",
    "comp",
    "end_comp",
    "notify",
    "key_down",
    "focus_in",
    "focus_out",
    "tsf_start",
    "tsf_update",
    "tsf_end",
    "ui_begin",
    "ui_update",
    "ui_end",
    "candidate",
    "reading",
    "other",
];

/// 読み戻した 1 行が「content-free な `gt/1` の形」かを確かめる（selftest 用の厳格な小さい検査器）。
///
/// 受け入れるのは、ASCII だけ・空白もエスケープも無い・キーは `KEYS` の名前だけで重複なし・
/// 値は 64 bit 符号なし整数か、`ENUM_VALUES` の列挙（`app_version` は `^[0-9A-Za-z.+-]{1,32}$`）だけの
/// 1 行の JSON オブジェクト。⚠️ 形の正本は `kit/formats/validate_logs.py`（受け入れではそちらも回す）。
/// 返す理由に、行の中の値は含めない。
pub fn check_line(s: &str) -> Result<(), &'static str> {
    if !s.is_ascii() {
        return Err("non-ASCII byte");
    }
    if s.len() < 2 || !s.starts_with('{') || !s.ends_with('}') {
        return Err("not a one-line object");
    }
    let mut rest = &s[1..s.len() - 1];
    let mut seen: Vec<&str> = Vec::new();
    loop {
        let (key, after_key) = take_string(rest)?;
        if !KEYS.contains(&key) {
            return Err("unknown key");
        }
        if seen.contains(&key) {
            return Err("duplicate key");
        }
        seen.push(key);
        let after_colon = after_key.strip_prefix(':').ok_or("missing colon")?;
        if after_colon.starts_with('"') {
            let (val, after_val) = take_string(after_colon)?;
            let ok = if key == "app_version" {
                (1..=32).contains(&val.len())
                    && val
                        .bytes()
                        .all(|c| c.is_ascii_alphanumeric() || matches!(c, b'.' | b'+' | b'-'))
            } else {
                ENUM_VALUES.contains(&val)
            };
            if !ok {
                return Err("string value outside the enumeration");
            }
            rest = after_val;
        } else {
            let n = after_colon.bytes().take_while(u8::is_ascii_digit).count();
            if n == 0 || after_colon[..n].parse::<u64>().is_err() {
                return Err("not an unsigned integer");
            }
            rest = &after_colon[n..];
        }
        match rest.strip_prefix(',') {
            Some(next) => rest = next,
            None if rest.is_empty() => return Ok(()),
            None => return Err("unexpected text after a value"),
        }
    }
}

/// 先頭の `"…"`（中に `"` も `\` も制御文字も無い）を取り出し、残りを返す。
fn take_string(s: &str) -> Result<(&str, &str), &'static str> {
    let body = s.strip_prefix('"').ok_or("expected a string")?;
    let end = body.find('"').ok_or("unterminated string")?;
    let val = &body[..end];
    if val.bytes().any(|c| c == b'\\' || c < 0x20 || c == 0x7f) {
        return Err("escape or control character");
    }
    Ok((val, &body[end + 1..]))
}

/// `ImmGetCompositionStringW` が返すバイト数を UTF-16 のコード単位数にする（`bytes / 2`）。
///
/// ⚠️ 負の値は IMM のエラー（`IMM_ERROR_NODATA` = −1 / `IMM_ERROR_GENERAL` = −2）で、文字列が
/// 取れなかったことを表す。長さは非負のコード単位数なので、エラーは 0 として記録する
/// （★ 区別しない。解釈はしない）。
pub fn units_from_bytes(bytes: i32) -> u32 {
    if bytes <= 0 {
        0
    } else {
        (bytes as u32) / 2
    }
}

/// `QueryPerformanceCounter` の値（ticks）を ns にする。`freq` は 1 秒あたりの ticks（0 なら 0）。
/// ⚠️ 途中で溢れないよう 128 bit で計算する（10 MHz でも ticks × 10⁹ は 64 bit を超えうる）。
pub fn ticks_to_ns(ticks: i64, freq: i64) -> u64 {
    if ticks <= 0 || freq <= 0 {
        return 0;
    }
    let ns = (ticks as u128) * 1_000_000_000u128 / (freq as u128);
    u64::try_from(ns).unwrap_or(u64::MAX)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn l(ev: Ev) -> String {
        line(ev, 1_700_000_000_123, 456_789)
    }

    const T: &str = "\"t_wall_ms\":1700000000123,\"t_mono_ns\":456789";

    #[test]
    fn header_has_the_contract_shape() {
        assert_eq!(
            header(Src::WinImm, "0.1.0"),
            r#"{"kind":"header","format":"gt/1","src":"win_imm","app_version":"0.1.0","os":"windows"}"#
        );
        assert_eq!(
            header(Src::WinTsf, "0.1.0+x-1"),
            r#"{"kind":"header","format":"gt/1","src":"win_tsf","app_version":"0.1.0+x-1","os":"windows"}"#
        );
    }

    #[test]
    fn header_sanitizes_the_version_instead_of_escaping() {
        // 検査器が拒否する文字は `_` にする（エスケープを出さない）
        let h = header(Src::WinImm, "a b\"c\\d");
        assert!(h.contains("\"app_version\":\"a_b_c_d\""), "{h}");
        assert!(!h.contains('\\'), "{h}");
        // 空・長すぎる版
        assert!(header(Src::WinImm, "").contains("\"app_version\":\"0\""));
        let long = "v".repeat(40);
        assert!(
            header(Src::WinImm, &long).contains(&format!("\"app_version\":\"{}\"", "v".repeat(32)))
        );
        // 日本語などの多バイト文字も `_`（1 文字 1 つ）
        assert!(header(Src::WinImm, "あい").contains("\"app_version\":\"__\""));
    }

    #[test]
    fn every_variant_matches_the_expected_json() {
        let cases: Vec<(Ev, String)> = vec![
            (
                Ev::StartComp,
                format!(r#"{{"kind":"ev",{T},"ev":"start_comp"}}"#),
            ),
            (
                Ev::Comp {
                    flags: 2056,
                    comp_len: 6,
                    result_len: 0,
                },
                format!(
                    r#"{{"kind":"ev",{T},"ev":"comp","flags":2056,"comp_len":6,"result_len":0}}"#
                ),
            ),
            (
                Ev::EndComp,
                format!(r#"{{"kind":"ev",{T},"ev":"end_comp"}}"#),
            ),
            (
                Ev::Notify { imn: 5 },
                format!(r#"{{"kind":"ev",{T},"ev":"notify","imn":5}}"#),
            ),
            (
                Ev::KeyDown { vk: 0xE5 },
                format!(r#"{{"kind":"ev",{T},"ev":"key_down","vk":229}}"#),
            ),
            (
                Ev::FocusIn,
                format!(r#"{{"kind":"ev",{T},"ev":"focus_in"}}"#),
            ),
            (
                Ev::FocusOut,
                format!(r#"{{"kind":"ev",{T},"ev":"focus_out"}}"#),
            ),
            (
                Ev::TsfStart,
                format!(r#"{{"kind":"ev",{T},"ev":"tsf_start"}}"#),
            ),
            (
                Ev::TsfUpdate { len: 3 },
                format!(r#"{{"kind":"ev",{T},"ev":"tsf_update","len":3}}"#),
            ),
            (
                Ev::TsfEnd { result_len: None },
                format!(r#"{{"kind":"ev",{T},"ev":"tsf_end"}}"#),
            ),
            (
                Ev::TsfEnd {
                    result_len: Some(2),
                },
                format!(r#"{{"kind":"ev",{T},"ev":"tsf_end","result_len":2}}"#),
            ),
            (
                Ev::UiBegin {
                    kind: UiKind::Candidate,
                },
                format!(r#"{{"kind":"ev",{T},"ev":"ui_begin","ui_kind":"candidate"}}"#),
            ),
            (
                Ev::UiUpdate {
                    kind: UiKind::Reading,
                },
                format!(r#"{{"kind":"ev",{T},"ev":"ui_update","ui_kind":"reading"}}"#),
            ),
            (
                Ev::UiEnd {
                    kind: UiKind::Other,
                },
                format!(r#"{{"kind":"ev",{T},"ev":"ui_end","ui_kind":"other"}}"#),
            ),
        ];
        for (ev, want) in cases {
            assert_eq!(l(ev), want, "{ev:?}");
        }
    }

    #[test]
    fn lines_have_no_spaces_no_escapes_and_no_newline() {
        let evs = [
            Ev::StartComp,
            Ev::Comp {
                flags: u32::MAX,
                comp_len: u32::MAX,
                result_len: u32::MAX,
            },
            Ev::Notify { imn: 0x10 },
            Ev::TsfEnd {
                result_len: Some(1),
            },
            Ev::UiEnd {
                kind: UiKind::Candidate,
            },
        ];
        for ev in evs {
            let s = line(ev, u64::MAX, u64::MAX);
            assert!(
                !s.contains(' ') && !s.contains('\\') && !s.contains('\n') && !s.contains('\r'),
                "{s}"
            );
        }
        let h = header(Src::WinImm, "0.1.0");
        assert!(
            !h.contains(' ') && !h.contains('\\') && !h.contains('\n'),
            "{h}"
        );
    }

    #[test]
    fn utf16_bytes_convert_to_code_units() {
        assert_eq!(units_from_bytes(0), 0);
        assert_eq!(units_from_bytes(2), 1);
        assert_eq!(units_from_bytes(12), 6);
        // 端数は切り捨て（UTF-16 では起きないが、壊れた値で溢れない）
        assert_eq!(units_from_bytes(7), 3);
        // IMM のエラー（負値）は 0
        assert_eq!(units_from_bytes(-1), 0);
        assert_eq!(units_from_bytes(-2), 0);
        assert_eq!(units_from_bytes(i32::MIN), 0);
        assert_eq!(units_from_bytes(i32::MAX), (i32::MAX as u32) / 2);
    }

    #[test]
    fn ticks_convert_to_ns_without_overflow() {
        // 10 MHz: 1 tick = 100 ns
        assert_eq!(ticks_to_ns(1, 10_000_000), 100);
        assert_eq!(ticks_to_ns(10_000_000, 10_000_000), 1_000_000_000);
        // ticks × 10⁹ が u64 を超える値でも正しい（起動から約 30 日 = 2.6e13 ticks @ 10 MHz）
        let ticks: i64 = 26_000_000_000_000;
        assert_eq!(ticks_to_ns(ticks, 10_000_000), 2_600_000_000_000_000);
        // 周波数 0・負の値は 0
        assert_eq!(ticks_to_ns(5, 0), 0);
        assert_eq!(ticks_to_ns(-5, 10_000_000), 0);
        assert_eq!(ticks_to_ns(5, -1), 0);
    }

    #[test]
    fn check_line_accepts_every_line_this_module_writes() {
        assert_eq!(check_line(&header(Src::WinImm, "0.1.0")), Ok(()));
        assert_eq!(check_line(&header(Src::WinTsf, "a.b+c-1")), Ok(()));
        let evs = [
            Ev::StartComp,
            Ev::Comp {
                flags: 2056,
                comp_len: 6,
                result_len: 0,
            },
            Ev::EndComp,
            Ev::Notify { imn: 5 },
            Ev::KeyDown { vk: 0xE5 },
            Ev::FocusIn,
            Ev::FocusOut,
            Ev::TsfStart,
            Ev::TsfUpdate { len: 3 },
            Ev::TsfEnd { result_len: None },
            Ev::TsfEnd {
                result_len: Some(2),
            },
            Ev::UiBegin {
                kind: UiKind::Candidate,
            },
            Ev::UiUpdate {
                kind: UiKind::Reading,
            },
            Ev::UiEnd {
                kind: UiKind::Other,
            },
        ];
        for ev in evs {
            let s = line(ev, u64::MAX, 0);
            assert_eq!(check_line(&s), Ok(()), "{s}");
        }
    }

    #[test]
    fn check_line_rejects_anything_that_could_carry_text() {
        let good = r#"{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"key_down","vk":13}"#;
        assert_eq!(check_line(good), Ok(()));
        let bad = [
            // 未知のキー（本文を運べる位置）
            r#"{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"key_down","text":"a"}"#,
            r#"{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"key_down","vk":"a"}"#,
            // 列挙の外の文字列
            r#"{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"typed"}"#,
            r#"{"kind":"ev","t_wall_ms":1,"t_mono_ns":2,"ev":"comp","ui_kind":"あ"}"#,
            // 空白・エスケープ・非 ASCII
            r#"{"kind":"ev", "t_wall_ms":1,"t_mono_ns":2,"ev":"key_down","vk":13}"#,
            "{\"kind\":\"ev\",\"t_wall_ms\":1,\"t_mono_ns\":2,\"ev\":\"key_down\",\"vk\":13,\"ui_kind\":\"\u{3042}\"}",
            // 整数でないもの
            r#"{"kind":"ev","t_wall_ms":-1,"t_mono_ns":2,"ev":"key_down","vk":13}"#,
            r#"{"kind":"ev","t_wall_ms":1.5,"t_mono_ns":2,"ev":"key_down","vk":13}"#,
            r#"{"kind":"ev","t_wall_ms":true,"t_mono_ns":2,"ev":"key_down","vk":13}"#,
            r#"{"kind":"ev","t_wall_ms":18446744073709551616,"t_mono_ns":2,"ev":"key_down","vk":13}"#,
            // 重複キー・入れ子・形の崩れ
            r#"{"kind":"ev","kind":"ev"}"#,
            r#"{"kind":"ev","t_wall_ms":{"a":1}}"#,
            r#"{"kind":"ev","t_wall_ms":1,}"#,
            r#"{"kind":"ev","t_wall_ms":1"#,
            r#"["kind"]"#,
            "",
            "{}",
        ];
        for s in bad {
            assert!(check_line(s).is_err(), "{s}");
        }
        // エスケープ（バックスラッシュ）は、列挙に合う綴りでも拒否する。
        // ⚠️ ソースに綴りを書くとツール経由で化けることがあるので、文字コードから組み立てる。
        let bs = char::from(0x5c_u8);
        let escaped = format!(
            "{{\"kind\":\"ev\",\"t_wall_ms\":1,\"t_mono_ns\":2,\"ev\":\"key{bs}_down\",\"vk\":13}}"
        );
        assert!(check_line(&escaped).is_err(), "{escaped}");
        // app_version は版の形だけ
        let hdr = |v: &str| {
            format!(
                r#"{{"kind":"header","format":"gt/1","src":"win_imm","app_version":"{v}","os":"windows"}}"#
            )
        };
        assert_eq!(check_line(&hdr("0.1.0")), Ok(()));
        assert!(check_line(&hdr("")).is_err());
        assert!(check_line(&hdr("a b")).is_err());
        assert!(check_line(&hdr(&"v".repeat(33))).is_err());
        // 理由に行の中の値を含めない
        let secret = r#"{"kind":"ev","zzsecret":1}"#;
        assert!(!check_line(secret).unwrap_err().contains("zzsecret"));
    }

    #[test]
    fn selftest_sequence_shape_is_plausible_gt_1() {
        // 代表的な変換 1 回（開始 → 更新 → 確定 → 終了）が gt/1 の形（JSON オブジェクト 1 行）になる
        let seq = [
            Ev::FocusIn,
            Ev::KeyDown { vk: 0xE5 },
            Ev::StartComp,
            Ev::Comp {
                flags: 0x0008,
                comp_len: 1,
                result_len: 0,
            },
            Ev::Comp {
                flags: 0x0800,
                comp_len: 0,
                result_len: 1,
            },
            Ev::EndComp,
            Ev::FocusOut,
        ];
        for (i, ev) in seq.iter().enumerate() {
            let s = line(*ev, 1000 + i as u64, 2000 + i as u64);
            assert!(
                s.starts_with("{\"kind\":\"ev\",") && s.ends_with('}'),
                "{s}"
            );
        }
    }
}
