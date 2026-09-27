# 設計 — p321-reanalysis-paper

## アプローチ

- 解析一式は論文用の別リポジトリ `mikotomiura/self-resolution-measure`（private・`C:/self-resolution-measure`）に置く（判断 6）。
  GSE 側には作業記録・`docs/references.md`・`docs/glossary.md` だけを残す。
- 解析手続きは 2026-09-06 に検算済みの `experiments/20260906-p321-resumption-baseline/analyze_p321.py` を移植し、次を足す:
  - 参照の定義 4 通り（strict / ＋U / ＋OT2 / ＋OT2＋U）× 解決の定義 2 通り（DF1 / DF1＋DF2）
  - 開発者単位のクラスタ・ブートストラップ（B = 10,000・seed = `SEED`・percentile 95%）と Wilson（素の区間・比較用）
  - 起点（committed / fresh）での層別
  - 正式版 [P433] の報告値の再現表（ゲートではない・判断 7）
  - [P434] の二重転記の照合と、論文内の別の数値による転記検査
- 定義は `config.json` に凍結してから結果を出す（判断 5）。凍結コミット = 新リポジトリ `416a0fc`。

## 変更対象

| リポジトリ | ファイル | 内容 |
|---|---|---|
| self-resolution-measure | `config.json` / `SEED` / `DATA.md` / `NOTES.md` / `ENV.md` / `README.md` | 定義・来歴・凍結の記録 |
| self-resolution-measure | `analysis/{analyze,d1,d2,stats}.py` / `run.sh` | 解析本体（標準ライブラリのみ） |
| self-resolution-measure | `data/p434/transcription_{a,b}.csv` / `text_external.csv` | [P434] の転記（A = メイン、B = 独立 subagent） |
| GSE-prototype | `docs/glossary.md` | 「成果を要求しない自己解決指標」「分子の効果 / 分母の効果」 |
| GSE-prototype | `docs/references.md` | [P433] の gloss に「パッケージは v1 と同一」を追記（予定） |

## テスト戦略

- `run.sh` Step 0: 入力の SHA-256（zip 2 種のどちらか ＋ `rowData.json`）
- Step 1 `--selftest`: D1 ゲートの 正常 / 不在（参照を全削除）/ 壊れている（DF7 の畳み込み無効 → 109 episode）、
  D2 転記の 正常（A = B）/ 1 セル改変の検出、D2 ゲートの 正常 / 改変、
  陽性対照（合成データで既知の 2×2 を完全回収・畳み込み込み）、陰性対照（未解決 0 → 分子の効果 0）、
  ブートストラップ（1 クラスタなら区間が点に潰れる・同じ seed で同一）
- Step 3: 2 回実行して `metrics.json` / `report.md` がバイト一致

## 残り

- （完了）位置づけのサーヴェイ 1 ラウンド → `docs/literature/20260928-self-resolution-measure-positioning.md`
- （完了）外枠 → `outline.md`（EMSE 研究論文の構成に改めた）

## 実装中に変わったこと（2026-09-28・最終化）

- ★ **正式版 [P433] のパッケージは v1 とバイト同一だった**（判断 7）→ 「版を主 / 感度に分ける」設計は「公開コーディングは 1 つ・[P433] の報告値は再現表で扱う」に変わった。参照の定義を 4 通りに増やした（issue tracker を含める版は [P433] の定義に合わせたもの）。
- ★ **[P434] は本文に表に載らない参照が 2 task ある**（P1TA・S5TA）→ 感度 `table5_plus_text` を追加。二重転記は独立 subagent で行い、バイト同一。
- ★ **投稿先を EASE 2027 Short から EMSE 研究論文に変えた**（判断 8・9：研究者の条件「登壇なし・費用ゼロ」）→ 6 頁の制約が消え、外枠は EMSE の研究論文の構成に改めた。プレプリントは投稿と同時（判断 10）、ライセンスは Apache-2.0 ＋ CC BY 4.0（判断 11）。
- ★ **サーヴェイの判定は go（主張範囲を縮めて）**（`docs/literature/20260928-self-resolution-measure-positioning.md`）→ 「参照なし ≠ 自力解決」[P436] と「成果で条件づける」[P435] は新規性として主張しない。
- 論文用リポジトリのコミット: `416a0fc`（定義の凍結）→ `834f16a`（解析と結果）→ `4aab7f0`（ライセンス）。`bash run.sh` exit 0・自己検査 12 項目緑・2 回実行でバイト同一。
