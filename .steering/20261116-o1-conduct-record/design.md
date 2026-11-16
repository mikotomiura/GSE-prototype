# 設計 — o1-conduct-record

## 実装アプローチ

n4（`experiments/20261103-o1-n4-pause-stall/`）のパイプラインを、コードを変えずに import して全期間へ当て、足りない 3 つ（実施の記録・手前の窓・探索の AUC）を新しく書く。条件の文は `experiments/20261116-o1-conduct-record/conditions.md`（R1〜R8）。

| 部分 | 使い回すもの | 新しく書くもの |
|---|---|---|
| 復号・中間・記号 | `build_n4.py`（`select`・`salt`・`symbols`・`meta`・復号と印）・`build_o1.py` | `build_cr.py`: 取り置きを外す（`build_n4.HOLD_FROM` を全期間に替えて `main` を呼ぶ）。n4 の塩を写して同じ記号にする。追加の中間（`gse-replay` の既定の出力の `[t, p_stuck, ewma_x]`・`ime_state`・`ime_shadow` の行）と日番号の表 |
| 休止の分布・停滞の率（R3） | `pausestall.run`（n4 の N2〜N5 そのまま） | なし（出力先だけ替える） |
| 実施の記録（R2） | `files.json`・中間の `types` | `conduct.py` |
| 手前の窓の型（R4） | `types_core.Rec`・`analyze_o1.Day`・`posthoc.place` | `prewin.py`（人ごと・単位を再標本化した差の区間） |
| 探索の AUC（R5） | 論文 1 の 18 量の定義・KLiCKe K6 の停滞と対照の作り方 | `auc.py`（ロジスティック回帰を numpy で・単位で分けた 5 分割・対にした AUC・単位を再標本化した区間） |
| 公開の版と漏れ（R7） | `pausestall.public`・`leaks`・`round_count` | AUC と実施の記録の件数のキーを足した許可リスト |

学習器は論文 1 のロジスティック回帰（中央値の補完と欠けの印・標準化・L2 で C = 1）だけを numpy で書く。勾配ブースティングは scikit-learn がこの環境に無いので省く（decisions 判断 6）。

## 変更対象

### 新規作成するファイル
- `experiments/20261116-o1-conduct-record/conditions.md`・`SEED`・`data.md`・`env.md`・`run.sh`
- `build_cr.py`・`conduct.py`・`prewin.py`・`auc.py`・`mutants.py`・`notes.md`（計算の後）・`results/`

### 修正するファイル
- なし（n4・停滞の分解・c1c2c6 のコードは変えない。`run.sh` が未コミットの変更を検査する）

## 影響範囲

- repo の外: `~/gse-o1-derived/20261116-o1-conduct-record/`（平文・中間・丸めない結果・記号の対応）。削除台帳 A-4 の置き場。
- 受け取りフォルダは読むだけ（取り込みは済み・判断 5）。

## 既存パターンとの整合性

- 条件を記録を開く前にコミット・陽性対照と変異・`run.sh` の門（gse-replay と gse-unpack の SHA-256・削除台帳 §6・未コミットの変更・空き容量）・来歴 `results/provenance.json`。
- repo には記号を付けた丸めた集計だけ。日付・時刻・ファイル名・P-ID・版の文字列は出さない（n4 判断 7・8）。

## テスト戦略

- 陽性対照（R8）: 合成の中間で、実施の記録の数・欠番・行の型の数が手計算と一致／手前の窓で、停滞の手前にだけ遷移を入れた合成で差の区間が 0 を超え、入れない合成で 0 を含む／AUC で、対の AUC の手計算・既知の差を 1 つの打鍵以外の量に入れた合成で ΔAUC の下限が 0 を超え、入れない合成で 0 を含む・停滞の手前の打鍵の量に差を入れた合成で K の AUC が 0.5 を超える。
- 変異: 主な規則を壊した写しで対照が赤になる（mutants.py）。
- n4 の selftest・c1c2c6 の selftest・posthoc の selftest も run.sh の頭で回す。

## ロールバック計画

- repo の変更は新しいディレクトリだけなので、ブランチを捨てれば戻る。repo の外の平文は削除台帳 A-4 の置き場として扱い、要らなくなったら `~/gse-o1-derived/20261116-o1-conduct-record/` ごと消す。
