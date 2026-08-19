//! transfer-pipeline: raw NDJSON を被験者端末で匿名化する純粋変換 (age 暗号化前段)。
//!
//! data-privacy `anonymization.md` 準拠:
//! - **VK コード → `KeyCategory`** (どの文字かを失い、種類のみ残す → 本文再構成不能)。
//! - **絶対 epoch 時刻 → セッション開始からの相対 ms** (他ログとの突合による再識別を防ぐ)。
//! - ウィンドウタイトル/プロセス名/本文は元 NDJSON に存在しない (logger 設計) ため追加除去は不要。
//!
//! 本モジュールは `age` 非依存の純粋関数 (lib に常駐し常にテストされる)。暗号化は bin `gse-package`。

use serde_json::Value;

/// VK コードをプライバシーセーフなキー種別カテゴリに変換する (anonymization.md 準拠)。
/// 「どのキーか」を失い「どんな種類か」だけ残す。特徴量再計算に必要な
/// backspace/delete の区別は保持する (F3 修正率・F6 削除後停止率)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KeyCategory {
    Alphabetic,
    Numeric,
    Backspace,
    Delete,
    Space,
    Enter,
    Navigation,
    Modifier,
    Function,
    Escape,
    Other,
}

impl KeyCategory {
    pub fn from_vk(vk: u32) -> Self {
        match vk {
            0x41..=0x5A => Self::Alphabetic,
            0x30..=0x39 | 0x60..=0x69 => Self::Numeric,
            0x08 => Self::Backspace,
            0x2E => Self::Delete,
            0x20 => Self::Space,
            0x0D => Self::Enter,
            // 矢印 (0x25-0x28) + PgUp/PgDown/End/Home (0x21-0x24) = 0x21..=0x28。
            0x21..=0x28 => Self::Navigation,
            0x10 | 0x11 | 0x12 | 0x5B | 0x5C => Self::Modifier,
            0x1B => Self::Escape,
            0x70..=0x7B => Self::Function,
            _ => Self::Other,
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Alphabetic => "alphabetic",
            Self::Numeric => "numeric",
            Self::Backspace => "backspace",
            Self::Delete => "delete",
            Self::Space => "space",
            Self::Enter => "enter",
            Self::Navigation => "navigation",
            Self::Modifier => "modifier",
            Self::Function => "function",
            Self::Escape => "escape",
            Self::Other => "other",
        }
    }
}

/// 相対化する**絶対 epoch ミリ秒**フィールド名。`idle_ms` / `dwell_ms` / `latency_ms` /
/// `wall_accum_ms` / `elapsed_ms` / `session_elapsed_ms` 等は既に相対(継続時間)なので触らない。
/// `recovered_at` は通常 raw では null だが、metrics 後付け NDJSON を誤入力した時の防御で含める
/// (null はスキップされ無害・security レビュー defense-in-depth)。
const ABSOLUTE_TIME_FIELDS: &[&str] = &[
    "t",
    "ts",
    "session_start",
    "session_end",
    "scheduled_ts",
    "analysis_window_start_ms",
    "analysis_window_end_ms",
    "recovered_at",
];

/// NDJSON 1 行を匿名化する。`session_start_ms` は当該セッションの絶対開始時刻。
/// パース不能な行は `None` (呼び出し側で除外)。
pub fn anonymize_line(line: &str, session_start_ms: u64) -> Option<String> {
    let mut v: Value = serde_json::from_str(line).ok()?;
    let obj = v.as_object_mut()?;

    // `vk`(生値=本文再構成可) があれば**無条件で** category 化する。
    // type=="key" 限定にしない: 将来 type 名変更や vk を持つ別レコードが増えても漏らさない
    // (現スキーマでは Key のみだが匿名化保証として安全側に倒す・両レビュー指摘)。
    if let Some(vk) = obj.get("vk").and_then(Value::as_u64) {
        let cat = KeyCategory::from_vk(vk as u32);
        obj.remove("vk");
        obj.insert("category".to_string(), Value::from(cat.as_str()));
    }

    // 絶対 epoch 時刻 → session_start 相対 (saturating)。
    for &field in ABSOLUTE_TIME_FIELDS {
        if let Some(n) = obj.get(field).and_then(Value::as_u64) {
            let rel = n.saturating_sub(session_start_ms);
            obj.insert(field.to_string(), Value::from(rel));
        }
    }

    serde_json::to_string(&v).ok()
}

/// raw NDJSON 全体から `meta` の `session_start` (相対化基点) を探す。
/// **フォールバックは持たない**: 正規セッションは必ず先頭に `meta.session_start` を持つため、
/// 無い入力は破損/切り詰めとみなし `None` を返す (silent fallback=0 による誤相対化を避ける)。
pub fn find_session_start(raw: &str) -> Option<u64> {
    for line in raw.lines() {
        if let Ok(v) = serde_json::from_str::<Value>(line) {
            if let Some(ss) = v.get("session_start").and_then(Value::as_u64) {
                return Some(ss);
            }
        }
    }
    None
}

/// raw NDJSON 全体を匿名化する (1 行ずつ変換)。`session_start_ms` は相対化基点。
/// 戻り値: (匿名化 NDJSON, パース不能で除外した行数)。除外件数は呼び出し側が監査報告に使う。
pub fn anonymize_ndjson(raw: &str, session_start_ms: u64) -> (String, usize) {
    let mut out = String::with_capacity(raw.len());
    let mut skipped = 0usize;
    for line in raw.lines() {
        if line.trim().is_empty() {
            continue;
        }
        match anonymize_line(line, session_start_ms) {
            Some(a) => {
                out.push_str(&a);
                out.push('\n');
            }
            None => skipped += 1,
        }
    }
    (out, skipped)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn vk_to_category_covers_doc_mapping() {
        assert_eq!(KeyCategory::from_vk(0x41), KeyCategory::Alphabetic); // A
        assert_eq!(KeyCategory::from_vk(0x5A), KeyCategory::Alphabetic); // Z
        assert_eq!(KeyCategory::from_vk(0x30), KeyCategory::Numeric); // 0
        assert_eq!(KeyCategory::from_vk(0x08), KeyCategory::Backspace);
        assert_eq!(KeyCategory::from_vk(0x2E), KeyCategory::Delete);
        assert_eq!(KeyCategory::from_vk(0x20), KeyCategory::Space);
        assert_eq!(KeyCategory::from_vk(0x0D), KeyCategory::Enter);
        assert_eq!(KeyCategory::from_vk(0x25), KeyCategory::Navigation);
        assert_eq!(KeyCategory::from_vk(0x10), KeyCategory::Modifier);
        assert_eq!(KeyCategory::from_vk(0x1B), KeyCategory::Escape);
        assert_eq!(KeyCategory::from_vk(0x70), KeyCategory::Function);
        assert_eq!(KeyCategory::from_vk(0xBC), KeyCategory::Other); // 記号
    }

    #[test]
    fn key_line_loses_vk_and_relativizes_time() {
        let line = r#"{"type":"key","t":1000500,"vk":74,"press":true}"#;
        let out = anonymize_line(line, 1_000_000).unwrap();
        // vk 生値が残らない・category になる・本文再構成不能。
        assert!(!out.contains("\"vk\""), "vk leaked: {out}");
        assert!(!out.contains("74"), "raw vk value leaked: {out}");
        assert!(out.contains("\"category\":\"alphabetic\""), "{out}");
        // 絶対 epoch → 相対 (1000500 - 1000000 = 500)。
        assert!(out.contains("\"t\":500"), "time not relativized: {out}");
        assert!(out.contains("\"press\":true"));
    }

    #[test]
    fn non_key_events_relativized_and_kept() {
        // feat: 絶対 t を相対化、他フィールドは保持。
        let feat = r#"{"type":"feat","t":1030000,"f1":104.00,"p_stuck":0.5,"obs":3}"#;
        let out = anonymize_line(feat, 1_000_000).unwrap();
        assert!(out.contains("\"t\":30000"), "{out}");
        assert!(out.contains("\"p_stuck\":0.5"));
        assert!(out.contains("\"obs\":3"));
        // session_meta: ts 相対化、track 等カテゴリは保持。
        let meta = r#"{"type":"session_meta","track":"main","ts":1000050,"condition":"blind_calibration"}"#;
        let o2 = anonymize_line(meta, 1_000_000).unwrap();
        assert!(o2.contains("\"ts\":50"), "{o2}");
        assert!(o2.contains("\"track\":\"main\""));
    }

    /// ⚠️★★★ **プライバシーのゲート（security-checker MEDIUM・2026-08-16 追加）**
    ///
    /// `anonymize_line()` は **allow-list ではなく passthrough** である
    /// (`vk` の category 化と絶対時刻の相対化以外は素通し)。したがって
    /// **`feat` 行に新フィールドを足すと、匿名化のレビューを一切経ずに
    /// 被験者端末の `.age` バンドルへ載る**。CD1 の防御が producer 側の注意力だけに
    /// 依存している状態を、ここで機械的なゲートに変える。
    ///
    /// ★ 入力は `schema_dto::LogEntryDto::Feat`（= NDJSON の宣言上のミラー）から作る。
    /// ★ `LogEntry::Feat` にフィールドを足して `schema_dto` に同期すると**本テストが落ちる**。
    ///   落ちたら「その値を被験者端末の外へ出してよいか」を判断し、意図的なら期待集合を更新すること。
    /// ⚠️ `schema_dto` への同期漏れ自体は schema drift check が別途捕まえる。
    #[test]
    fn anonymized_feat_line_field_set_is_pinned() {
        use crate::schema_dto::LogEntryDto;

        let src = LogEntryDto::Feat {
            t: 1_030_000,
            f1: 104.0,
            f3: 0.125,
            f4: 4.0,
            f5: 1.0,
            f6: 0.5,
            p_flow: 0.6,
            p_inc: 0.25,
            p_stuck: 0.15,
            raw_x: 0.1,
            raw_y: 0.8,
            ewma_x: 0.05,
            ewma_y: 0.7,
            obs: 3,
            alpha: 0.3,
            keys: Some(48),
            bs_keys: Some(6),
        };
        let line = serde_json::to_string(&src).expect("serialize LogEntryDto::Feat");
        let out = anonymize_line(&line, 1_000_000).expect("anonymize feat line");
        let v: Value = serde_json::from_str(&out).expect("anonymized line is JSON");
        let obj = v.as_object().expect("object");

        let mut got: Vec<&str> = obj.keys().map(String::as_str).collect();
        got.sort_unstable();
        let expected = [
            "alpha", "bs_keys", "ewma_x", "ewma_y", "f1", "f3", "f4", "f5", "f6", "keys", "obs",
            "p_flow", "p_inc", "p_stuck", "raw_x", "raw_y", "t", "type",
        ];
        assert_eq!(
            got, expected,
            "feat 行のフィールド集合が変わった。匿名化バンドルに出してよい値か判断してから更新すること"
        );

        // ★ `type` 以外はすべて数値であること = 本文性のある文字列が 1 つも無いこと。
        for (k, val) in obj {
            if k == "type" {
                continue;
            }
            assert!(
                val.is_number(),
                "feat の {k} が数値でない ({val}). 文字列は本文を運びうるので匿名化の再検討が要る"
            );
        }
        // 絶対時刻は相対化されている。
        assert_eq!(obj["t"], Value::from(30_000u64));
        // ★ Tier 0 の打鍵数は「数」としてそのまま残る (F3/F6 と同じ扱い・再計算に必要)。
        assert_eq!(obj["keys"], Value::from(48u64));
        assert_eq!(obj["bs_keys"], Value::from(6u64));
    }

    #[test]
    fn meta_session_start_becomes_zero() {
        let meta = r#"{"type":"meta","session_start":1700000000000,"hmm_version":"0.3.0"}"#;
        let out = anonymize_line(meta, 1_700_000_000_000).unwrap();
        assert!(out.contains("\"session_start\":0"), "{out}");
        assert!(out.contains("\"hmm_version\":\"0.3.0\""));
    }

    #[test]
    fn anonymize_ndjson_finds_session_start_and_strips_all_vk() {
        let raw = concat!(
            r#"{"type":"meta","session_start":1000000,"hmm_version":"0.3.0"}"#,
            "\n",
            r#"{"type":"key","t":1000200,"vk":65,"press":true}"#,
            "\n",
            r#"{"type":"key","t":1000300,"vk":8,"press":true}"#,
            "\n",
            "broken json line not parseable\n",
        );
        let ss = find_session_start(raw).expect("meta session_start present");
        assert_eq!(ss, 1_000_000);
        let (out, skipped) = anonymize_ndjson(raw, ss);
        assert_eq!(skipped, 1, "broken line should be counted as skipped");
        assert!(!out.contains("\"vk\""), "vk leaked in batch: {out}");
        assert!(out.contains("\"category\":\"alphabetic\""));
        assert!(out.contains("\"category\":\"backspace\""));
        assert!(out.contains("\"t\":200"));
        assert!(out.contains("\"session_start\":0"));
    }

    #[test]
    fn find_session_start_none_when_no_meta() {
        // meta.session_start を持たない断片は None (CLI 側で reject される)。
        let raw = r#"{"type":"key","t":1000200,"vk":65,"press":true}"#;
        assert_eq!(find_session_start(raw), None);
    }

    #[test]
    fn vk_stripped_unconditionally_and_recovered_at_relativized() {
        // type が "key" でなくても vk があれば category 化する (防御)。
        let weird = r#"{"type":"key_down","t":1000100,"vk":65}"#;
        let o = anonymize_line(weird, 1_000_000).unwrap();
        assert!(!o.contains("\"vk\""), "vk leaked on non-key type: {o}");
        assert!(o.contains("\"category\":\"alphabetic\""));
        // recovered_at (絶対 epoch) も相対化される。
        let ul = r#"{"type":"user_label","t":1005000,"label":"stuck","recovered_at":1010000}"#;
        let o2 = anonymize_line(ul, 1_000_000).unwrap();
        assert!(o2.contains("\"recovered_at\":10000"), "{o2}");
        assert!(o2.contains("\"t\":5000"));
        assert!(o2.contains("\"label\":\"stuck\""));
    }

    /// ⚠️★★★ ADR-013 で足した行種・フィールドが匿名化を**素通りしない**こと。
    ///
    /// ★ `anonymize_line` は未知フィールドを serde の往復でそのまま通すので、
    /// **新しい行種を足したときに絶対 epoch がそのまま残る**経路が生まれうる。
    /// → ⚠️ `starve_window` の `t` が相対化されることを固定する
    /// (★ 相対化が外れると**セッションの実時刻**が匿名化済みデータに載る)。
    #[test]
    fn adr013_lines_are_anonymised_too() {
        // ① starve_window: `t` は相対化、`win_ms` / 件数は**そのまま** (相対化してはならない)。
        let sw =
            r#"{"type":"starve_window","t":1060000,"win_ms":60000,"n_lt30":7,"sum_lt30_ms":4200}"#;
        let o = anonymize_line(sw, 1_000_000).unwrap();
        assert!(o.contains("\"t\":60000"), "t が相対化されていない: {o}");
        assert!(o.contains("\"win_ms\":60000"), "{o}");
        assert!(o.contains("\"n_lt30\":7"), "{o}");
        assert!(o.contains("\"sum_lt30_ms\":4200"), "{o}");

        // ② hook_health の dropped_delta は件数なので不変。
        let hh = r#"{"type":"hook_health","t":1002000,"alive":true,"starved_ms":0,"rehook":false,"dropped":10,"dropped_delta":7}"#;
        let o2 = anonymize_line(hh, 1_000_000).unwrap();
        assert!(o2.contains("\"t\":2000"), "{o2}");
        assert!(o2.contains("\"dropped_delta\":7"), "{o2}");

        // ③ meta の capabilities / app_version は**保たれる** (解析側の機械判定に要る)。
        //    ⚠️ 落とすと「計器が無い」と誤判定される。
        let meta = r#"{"type":"meta","session_start":1000000,"hmm_version":"0.4.0","app_version":"0.1.26","capabilities":{"unconditional":["key"],"threshold_gated":["hook_health"]}}"#;
        let o3 = anonymize_line(meta, 1_000_000).unwrap();
        assert!(o3.contains("\"session_start\":0"), "{o3}");
        assert!(o3.contains("\"app_version\":\"0.1.26\""), "{o3}");
        assert!(
            o3.contains("\"threshold_gated\""),
            "capabilities が落ちた: {o3}"
        );
    }
}
