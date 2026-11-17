# 設計

## アプローチ

選択肢を 1 つ足す additive な変更（ADR-005）。行種 `activity_label` は増やさず、`category` の値に `working` を足す。`HMM_VERSION` は上げない（推論・特徴量・介入に触れない）。

## 変更対象

| # | 対象 | 変更 |
|---|---|---|
| 1 | `docs/adr/ADR-055-q3-working-option.md`（新規） | ADR-031 D3 条件 i を 7 択に改める。文言・境の規則・並び・6 択と 7 択の読み方・同意の版。Proposed |
| 2 | `docs/adr/README.md` | 一覧に ADR-055 を足す |
| 3 | `src-tauri/src/logger.rs` | `ActivityCategory::Working`（`as_str`/`parse`/`ALL`/`exhaustive_marker`）・doc・テストの数 6→7 |
| 4 | `src-tauri/src/schema_dto.rs` | `ActivityCategoryDto::Working`（位置は `Away` と `CannotAnswer` の間） |
| 5 | `src-tauri/schema/current.json` | `emit_schema` で作り直す |
| 6 | `src-tauri/src/submission.rs` | `S1_PROBE_CONSENT_VERSION` を `s1-n3-1` に上げる・旧い版 `s1-self-trial-1` が無効になるテスト |
| 7 | `src/probeTypes.ts` | 型と `ACTIVITY_CHOICES` に `working` |
| 8 | `src/components/S1ProbeCard.tsx` | Q3 の問いの文に「いくつか当てはまるときは、いちばん長かったもの」 |
| 9 | `.steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md` | その場で直し、承認の印を外す（判断 7）。`Form_O1/GSE_O1_Form_Builder.gs` とそのテストも直す |
| 10 | `docs/preregistration-stage1.md` | Q3 を使う箇所（S1-A2・S1-A3 ほか）に 7 択と畳み方 |
| 11 | `.claude/skills/data-privacy/SKILL.md` ルール 7 条件 i・`docs/glossary.md` C4・`docs/architecture/gse-design-map.md` の問いの行 | 選択肢の中身を 7 択に |

## 確かめたこと（着手時）

- `ActivityCategory` の値を読むのは logger・schema_dto・schema・probeTypes・S1ProbeCard だけ。解析のスクリプトは値を読まない。
- `ALL` の網羅は `exhaustive_marker` の `match` でビルドが守る。
- 同意の印は版が一致するときだけ有効（`submission.rs` `s1_probe_consent_acknowledged_at`）。版を上げると旧い印では問いが出ない。
- 事前登録の草案は凍結していない。未マージの改訂の枝 `docs/gse-stage1-prereg-revision` があるので、こちらは Q3 の箇所だけを小さく直す。

## テスト戦略

- `cargo test`（logger の往復・網羅・書き出し、submission の版）
- `cargo run --bin emit_schema` と `current.json` の byte-equal
- gse-dataset との parity check（`/finish-task` Step 3・origin/main と比べる）
- `npx tsc --noEmit`
- 画面: S1ProbeCard を shim で実マウントして 7 つと問いの文を目で確かめる（カードの高さが overlay に収まるか）

## 影響範囲

- gse-replay と golden は `activity_label` を特徴量に使わない（ADR-031 D4・記録のみ）ので byte-equal は変わらない見込み。走らせて確かめる。
