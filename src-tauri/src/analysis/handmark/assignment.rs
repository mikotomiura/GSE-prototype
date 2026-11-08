//! 割付の表（`handmark_assignment.json`）の解釈・日の割付・SHA-256 の照合・描画の種（ADR-051 D4）。
//!
//! IO は持たない（バイト列を受ける）。`*_day` は `eh3::local_day` の数え方（4:00 区切り）。

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use super::state::SplitMix64;

/// 表の版（これだけを受ける）。
pub const TABLE_VERSION: u32 = 1;
/// 日の番号の常識の範囲（`eh3::local_day` の数え方で 1970 年から約 2700 年）。
pub const DAY_RANGE: std::ops::RangeInclusive<i64> = 0..=1_000_000;
/// `days` の長さの上限。
pub const MAX_DAYS: usize = 400;

/// 割付の表。キーの順はこの宣言の順で固定する（正規のバイト列）。
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Table {
    pub version: u32,
    pub s1_start_day: i64,
    pub early_days: u32,
    pub late_start_day: i64,
    /// 後期の (i+2) 日目の「あり・なし」。後期の初日は割付の外で必ず表示する。
    pub days: Vec<bool>,
}

/// ある日の割付。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Assigned {
    Before,
    LateFirst,
    On,
    Off,
    After,
}

impl Assigned {
    pub const ALL: [Assigned; 5] = [
        Assigned::Before,
        Assigned::LateFirst,
        Assigned::On,
        Assigned::Off,
        Assigned::After,
    ];

    pub fn as_str(self) -> &'static str {
        match self {
            Assigned::Before => "before",
            Assigned::LateFirst => "late_first",
            Assigned::On => "on",
            Assigned::Off => "off",
            Assigned::After => "after",
        }
    }
}

impl Table {
    /// 表の中身を検める（読み込みのとき）。
    pub fn validate(&self) -> Result<(), String> {
        if self.version != TABLE_VERSION {
            return Err(format!("unsupported version {}", self.version));
        }
        if !DAY_RANGE.contains(&self.s1_start_day) || !DAY_RANGE.contains(&self.late_start_day) {
            return Err("day out of range".into());
        }
        let expected = i128::from(self.s1_start_day) + i128::from(self.early_days);
        if i128::from(self.late_start_day) != expected {
            return Err("late_start_day != s1_start_day + early_days".into());
        }
        if self.days.is_empty() || self.days.len() > MAX_DAYS {
            return Err(format!(
                "days length {} out of 1..={MAX_DAYS}",
                self.days.len()
            ));
        }
        for (k, block) in self.days.chunks(2).enumerate() {
            match block {
                [a, b] if a == b => return Err(format!("block {k} is not one on and one off")),
                [_, _] | [_] => {}
                _ => return Err("bad block".into()),
            }
        }
        Ok(())
    }

    /// `day` の割付。
    pub fn assigned(&self, day: i64) -> Assigned {
        if day < self.late_start_day {
            return Assigned::Before;
        }
        if day == self.late_start_day {
            return Assigned::LateFirst;
        }
        let idx = i128::from(day) - i128::from(self.late_start_day) - 1;
        match usize::try_from(idx).ok().and_then(|i| self.days.get(i)) {
            Some(true) => Assigned::On,
            Some(false) => Assigned::Off,
            None => Assigned::After,
        }
    }

    /// 正規のバイト列（コンパクトな JSON・改行で終わる）。
    pub fn canonical_bytes(&self) -> Vec<u8> {
        let mut v = serde_json::to_vec(self).unwrap_or_default();
        v.push(b'\n');
        v
    }
}

/// 表の読み込みの結果。
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TableLoad {
    Missing,
    Broken,
    ShaMissing,
    ShaMismatch,
    Ok { table: Table, sha256: String },
}

/// 16 進（小文字）にする。
pub fn hex(bytes: &[u8]) -> String {
    use std::fmt::Write;
    bytes
        .iter()
        .fold(String::with_capacity(bytes.len() * 2), |mut s, b| {
            let _ = write!(s, "{b:02x}");
            s
        })
}

/// バイト列の SHA-256（小文字の 16 進 64 桁）。
pub fn sha256_hex(bytes: &[u8]) -> String {
    hex(&Sha256::digest(bytes))
}

/// `.sha256` の本文の最初の語（空白区切り）が 64 桁の 16 進なら、小文字にして返す。
pub fn parse_sha_file(text: &str) -> Option<String> {
    let word = text
        .trim_start_matches('\u{feff}')
        .split_whitespace()
        .next()?;
    if word.len() == 64 && word.bytes().all(|b| b.is_ascii_hexdigit()) {
        Some(word.to_ascii_lowercase())
    } else {
        None
    }
}

/// 表のバイト列と `.sha256` の本文（どちらも無ければ `None`）から、読み込みの結果を出す。
/// 順序: 表が無い → 表が壊れている → `.sha256` が無い → 一致しない。
pub fn load_from_bytes(table_bytes: Option<&[u8]>, sha_text: Option<&str>) -> TableLoad {
    let Some(bytes) = table_bytes else {
        return TableLoad::Missing;
    };
    let table: Table = match serde_json::from_slice(bytes) {
        Ok(t) => t,
        Err(_) => return TableLoad::Broken,
    };
    if table.validate().is_err() {
        return TableLoad::Broken;
    }
    let Some(sha_text) = sha_text else {
        return TableLoad::ShaMissing;
    };
    let actual = sha256_hex(bytes);
    match parse_sha_file(sha_text) {
        Some(expected) if expected == actual => TableLoad::Ok {
            table,
            sha256: actual,
        },
        _ => TableLoad::ShaMismatch,
    }
}

/// 描画の種: `SHA-256(sha256_hex + ":" + day の 10 進)` の先頭 8 バイト（big endian）。
/// 前期の日にも同じ式で決まる。
pub fn draw_seed(table_sha256_hex: &str, day: i64) -> u64 {
    let digest = Sha256::digest(format!("{table_sha256_hex}:{day}").as_bytes());
    let mut b = [0u8; 8];
    b.copy_from_slice(&digest[..8]);
    u64::from_be_bytes(b)
}

/// 表を作る（`gse-handmark-table`）。前期の長さは `[early_min, early_max]` から種で一様に引く。
/// `days` は後期の 2 日目から `late_days - 1` 日分を、2 日ずつのブロックの中で並べ替える。
pub fn generate(
    seed: u64,
    s1_start_day: i64,
    early_min: u32,
    early_max: u32,
    late_days: u32,
) -> Result<Table, String> {
    if early_min > early_max {
        return Err("early-min > early-max".into());
    }
    if late_days < 2 || late_days as usize > MAX_DAYS + 1 {
        return Err(format!("late-days must be in 2..={}", MAX_DAYS + 1));
    }
    let mut rng = SplitMix64::new(seed);
    let span = u64::from(early_max - early_min) + 1;
    let early_days = early_min + rng.below(span) as u32;
    let n = (late_days - 1) as usize;
    let mut days = Vec::with_capacity(n);
    let mut i = 0;
    while i < n {
        let first_on = rng.next_u64() >> 63 == 1;
        days.push(first_on);
        if i + 1 < n {
            days.push(!first_on);
        }
        i += 2;
    }
    let table = Table {
        version: TABLE_VERSION,
        s1_start_day,
        early_days,
        late_start_day: i64::try_from(i128::from(s1_start_day) + i128::from(early_days))
            .map_err(|_| "day overflow")?,
        days,
    };
    table.validate()?;
    Ok(table)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample() -> Table {
        Table {
            version: 1,
            s1_start_day: 20_400,
            early_days: 10,
            late_start_day: 20_410,
            days: vec![true, false, false, true, true],
        }
    }

    fn sha_of(t: &Table) -> String {
        format!(
            "{}  handmark_assignment.json\n",
            sha256_hex(&t.canonical_bytes())
        )
    }

    #[test]
    fn canonical_bytes_have_the_fixed_key_order_and_a_newline() {
        let b = sample().canonical_bytes();
        assert_eq!(
            std::str::from_utf8(&b).unwrap(),
            "{\"version\":1,\"s1_start_day\":20400,\"early_days\":10,\"late_start_day\":20410,\"days\":[true,false,false,true,true]}\n"
        );
    }

    #[test]
    fn assigned_covers_before_first_on_off_and_after() {
        let t = sample();
        assert_eq!(t.assigned(20_409), Assigned::Before);
        assert_eq!(t.assigned(0), Assigned::Before);
        assert_eq!(t.assigned(20_410), Assigned::LateFirst);
        assert_eq!(t.assigned(20_411), Assigned::On);
        assert_eq!(t.assigned(20_412), Assigned::Off);
        assert_eq!(t.assigned(20_413), Assigned::Off);
        assert_eq!(t.assigned(20_414), Assigned::On);
        assert_eq!(t.assigned(20_415), Assigned::On);
        assert_eq!(t.assigned(20_416), Assigned::After);
        assert_eq!(t.assigned(i64::MAX), Assigned::After);
    }

    #[test]
    fn load_ok_missing_broken_sha_cases() {
        let t = sample();
        let bytes = t.canonical_bytes();
        let sha = sha_of(&t);
        assert!(matches!(
            load_from_bytes(Some(&bytes), Some(&sha)),
            TableLoad::Ok { .. }
        ));
        assert_eq!(load_from_bytes(None, Some(&sha)), TableLoad::Missing);
        assert_eq!(
            load_from_bytes(Some(b"{nope"), Some(&sha)),
            TableLoad::Broken
        );
        assert_eq!(load_from_bytes(Some(&bytes), None), TableLoad::ShaMissing);
        let other = sha.replacen(&sha[..1], if &sha[..1] == "0" { "1" } else { "0" }, 1);
        assert_eq!(
            load_from_bytes(Some(&bytes), Some(&other)),
            TableLoad::ShaMismatch
        );
        assert_eq!(
            load_from_bytes(Some(&bytes), Some("not hex\n")),
            TableLoad::ShaMismatch
        );
        // 大文字でも通る
        let upper = sha.to_ascii_uppercase();
        assert!(matches!(
            load_from_bytes(Some(&bytes), Some(&upper)),
            TableLoad::Ok { .. }
        ));
        // 表を 1 バイト変えると、元の .sha256 では通らない
        let mut changed = bytes.clone();
        changed.insert(changed.len() - 1, b' ');
        assert_eq!(
            load_from_bytes(Some(&changed), Some(&sha)),
            TableLoad::ShaMismatch
        );
    }

    #[test]
    fn validate_rejects_bad_tables() {
        let mut t = sample();
        t.version = 2;
        assert!(t.validate().is_err());
        let mut t = sample();
        t.late_start_day = 20_411;
        assert!(t.validate().is_err());
        let mut t = sample();
        t.days = vec![];
        assert!(t.validate().is_err());
        let mut t = sample();
        t.days = vec![true; 401];
        assert!(t.validate().is_err());
        // ブロック [true, true] は不可
        let mut t = sample();
        t.days = vec![true, true];
        assert!(t.validate().is_err());
        // 最後のブロックが 1 つなら true でも false でもよい
        for last in [true, false] {
            let mut t = sample();
            t.days = vec![true, false, last];
            assert!(t.validate().is_ok());
        }
        // 壊れた表（未知のキー）は Broken
        let bytes = br#"{"version":1,"s1_start_day":1,"early_days":1,"late_start_day":2,"days":[true],"x":1}"#;
        assert_eq!(load_from_bytes(Some(bytes), Some("0")), TableLoad::Broken);
    }

    #[test]
    fn day_arithmetic_does_not_overflow_at_the_boundaries() {
        let t = sample();
        assert_eq!(t.assigned(i64::MIN), Assigned::Before);
        assert_eq!(t.assigned(i64::MAX), Assigned::After);
        // 範囲の端
        let ok = Table {
            version: 1,
            s1_start_day: 0,
            early_days: 1,
            late_start_day: 1,
            days: vec![true],
        };
        assert!(ok.validate().is_ok());
        let top = Table {
            version: 1,
            s1_start_day: 1_000_000,
            early_days: 0,
            late_start_day: 1_000_000,
            days: vec![true],
        };
        assert!(top.validate().is_ok());
        assert_eq!(top.assigned(i64::MAX), Assigned::After);
        // 範囲の外・オーバーフローする値は壊れた表
        for (s, e, l) in [
            (-1i64, 1u32, 0i64),
            (1_000_001, 0, 1_000_001),
            (i64::MAX, 1, i64::MAX),
            (i64::MAX, u32::MAX, i64::MAX),
            (1_000_000, 1, 1_000_001),
        ] {
            let t = Table {
                version: 1,
                s1_start_day: s,
                early_days: e,
                late_start_day: l,
                days: vec![true],
            };
            assert!(t.validate().is_err(), "{s} {e} {l}");
        }
        assert!(generate(1, i64::MAX, 1, 1, 3).is_err());
        assert!(generate(1, 1_000_000, 1, 1, 3).is_err());
        assert!(generate(1, 999_999, 1, 1, 3).is_ok());
    }

    #[test]
    fn parse_sha_file_takes_the_first_word() {
        let h = "a".repeat(64);
        assert_eq!(parse_sha_file(&format!("{h}  file\n")), Some(h.clone()));
        assert_eq!(parse_sha_file(&format!("  \n{h}")), Some(h.clone()));
        assert_eq!(parse_sha_file(&"g".repeat(64)), None);
        assert_eq!(parse_sha_file(&"a".repeat(63)), None);
        assert_eq!(parse_sha_file(""), None);
    }

    #[test]
    fn sha256_known_vector() {
        assert_eq!(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
    }

    #[test]
    fn draw_seed_is_deterministic_and_depends_on_both_inputs() {
        let h = "b".repeat(64);
        assert_eq!(draw_seed(&h, 20_411), draw_seed(&h, 20_411));
        assert_ne!(draw_seed(&h, 20_411), draw_seed(&h, 20_412));
        assert_ne!(draw_seed(&h, 20_411), draw_seed(&"c".repeat(64), 20_411));
        // 式の固定（先頭 8 バイトの big endian）
        let d = Sha256::digest(format!("{h}:20411").as_bytes());
        assert_eq!(
            draw_seed(&h, 20_411),
            u64::from_be_bytes(d[..8].try_into().unwrap())
        );
    }

    #[test]
    fn generate_is_deterministic_valid_and_seed_sensitive() {
        let a = generate(42, 20_400, 7, 12, 15).unwrap();
        let b = generate(42, 20_400, 7, 12, 15).unwrap();
        assert_eq!(a.canonical_bytes(), b.canonical_bytes());
        assert!(a.validate().is_ok());
        assert!((7..=12).contains(&a.early_days));
        assert_eq!(a.days.len(), 14);
        let mut differs = false;
        for s in 0..20u64 {
            let c = generate(s, 20_400, 7, 12, 15).unwrap();
            assert!(c.validate().is_ok());
            if c.canonical_bytes() != a.canonical_bytes() {
                differs = true;
            }
        }
        assert!(differs);
        // 通る: 出力を読み込みの検めに通す
        let bytes = a.canonical_bytes();
        assert!(matches!(
            load_from_bytes(Some(&bytes), Some(&sha_of(&a))),
            TableLoad::Ok { .. }
        ));
        // 奇数の長さ（late_days = 4 → days 3）
        assert_eq!(generate(1, 0, 5, 5, 4).unwrap().days.len(), 3);
        assert!(generate(1, 0, 5, 4, 10).is_err());
        assert!(generate(1, 0, 5, 6, 1).is_err());
    }
}
