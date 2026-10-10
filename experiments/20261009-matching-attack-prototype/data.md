# 入力データ

人のデータ（O1・G1・Phase1 の NDJSON）は使わない。入力は IME 論文の評価一式の Windows のセルの記録で、executor が計画どおりに送った合成入力（人の打鍵ではない）。それでも NDJSON の生ログとして扱い、Codex など外部の LLM に送らない（コードと集計だけを送る）。

## 記録と計画（Windows のセル・試行 2）

| ファイル | パス（repo 直下から） | SHA-256 |
|---|---|---|
| 記録（`obs/1`） | `papers/ime-observation/experiment/runs/windows-msime-tsf-2/obs.jsonl` | `58f0bda61fa4310c58a643bb605a68c360f34378b651a3b85d58290fabcd2562` |
| 計画（`plan/1`） | 同 `plan.jsonl` | `b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0` |
| 実行の記録 | 同 `run.json` | `5c74a1fad735b5983152847d29a540e71673f7d13257950af9726ddd79a33d82` |

- 測定機（G-GEAR・Windows 11 Home）で 2026-10-04 01:57〜13:03 JST に記録された（`papers/ime-observation/experiment/data.windows.md` の「Run checks」）。2,925 試行（13 シナリオ × 3 速さ × 75）・117 ブロック（25 試行ずつ）。
- `run.json` の `outputs.obs.sha256`・`outputs.plan.sha256` は上の 2 つと一致する。`run.json` の SHA-256 は `data.windows.md` の `manifest_sha256`。
- git に入っていない（`papers/ime-observation/.gitignore` の `runs/`）。手元に無ければ、Zenodo の寄託（DOI 10.5281/zenodo.23183438・`data.windows.md` の Deposits の表の `windows-msime-tsf (attempt 2)`・アーカイブの SHA-256 `f2287a7494b108a7b827f96da48f523e84e1a9478121d03fa82dca2c8749cd06`）から取り、`runs/windows-msime-tsf-2/` に展開する。
- ライセンス: IME 論文の `LICENSE-DATA`（同じ研究者のデータ）。

## 語句コーパスと手順

| ファイル | パス | SHA-256 |
|---|---|---|
| 語句（`corpus/1`） | `papers/ime-observation/kit/corpus/data/phrases.jsonl`（git に入っている） | `c8f890cb4d0848bf04e6d7d95efe4e4d3dfd02a23eb1c7f103344f14d13e4620` |
| 手順 | `papers/ime-observation/kit/gen/recipes.json` | `430ec52c67f0592bc1c9d038a972876a2608ed7c39eb2aabcf68efc4ff908411` |
| 計画の設定 | `papers/ime-observation/experiment/plan_config.windows.json` | `400fe5314d0f660f2e776a7f86deb471ae1235a3bea4c1be457b26ebe0a9181f` |

- 語句は青空文庫の 12 作品（著作権なし・新字新仮名）から 150 句ずつ、計 1,800 句（読み 6〜30 字・中央値 16）。読みの重複を除くと 1,791。作り方は `papers/ime-observation/experiment/data.md` の「Phrase corpus」。
- 計画のヘッダーの `recipes_sha256`・`config_sha256` は上の手順と設定の SHA-256 と一致する（`closed_set.py` が照らす）。

## 比べる値

- IME 論文の公開値: `papers/ime-observation/experiment/results/windows/e2_closed_set_windows-msime-tsf.json`（k = 1 の再現の確認）。
- 前のタスクの値: `experiments/20261009-length-sequence-uniqueness/results/matching.json`（SHA-256 `0d97c6a0ec1bd576f01c44862bc94c3b63dfde760ad49eb5292704a1c30aae6a`）。

## 派生データ

`raw/`（git に入らない）に、試行ごとのカテゴリ列と打鍵数（`raw/trials.json`）と、シミュレーション攻撃の試行ごとの距離（`raw/dist/`）を置く。記録の中身（カテゴリの列）を含むので、他人と受け渡さない・外部の LLM に送らない。`results/` には集計だけを置く。
