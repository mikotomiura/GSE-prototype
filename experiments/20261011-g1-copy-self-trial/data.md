# 入力データ

## 記録（人のデータ・repo に入れない）

- 研究者本人が G1 で打った記録（P009・P010。G1 の番号で Phase1 とは別）。本人の記録なので、G1 の参加者への再同意なしに試しの計算に使う（ADR-039 D8 の 2026-10-11 の注）。
- 受領したのは `.age`（研究者の公開鍵で暗号化）。`gse-unpack --identity <研究者の秘密鍵>` で復号し、repo の外（セッションの scratchpad）に置いた。鍵の置き場所と中身は書かない。
- ファイル名とセッションの日時は書かない（`experiments/20260801-controlled-friction-task/protocol.md` §7）。記録には「P009_block01」のように書く。復号した NDJSON の SHA-256 は `config.json` の `records.sha256`。
- `run.sh` は `G1_RECORDS`（復号した NDJSON のディレクトリ。`P0xx_blockNN_` で始まるファイルを SHA-256 で照らして選ぶ）と `G1_WORK`（記録から作った区間の並び・揃えを書く repo の外のディレクトリ）を要る。作業が終わったら両方を消す。
- 記録・区間の並びは外部の LLM（Codex を含む）に送らない（`docs/external-skills.md`・`data-privacy` Skill）。

## 原文

`experiments/20260801-controlled-friction-task/materials/copy.md`（G1 の書き写しの原文。SHA-256 は `config.json`）。

## おとり（青空文庫）

前の実測の 1,500 作品（`experiments/20261009-length-sequence-uniqueness/data.md`）。zip は前の実測の `raw/zips/`（git に入らない）を `ZIPS` で指す。各 zip は前の実測の `results/corpus_manifest.json` の SHA-256 と照らし、違えば止まる。区間の並び（公開テキストから作った派生データ）は `raw/`（git に入らない）に JSON で置く。
