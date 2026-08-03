# 入力データの固定（未実施・実施時に埋める）

> ⚠️ **本実験は未実施**。被験者募集も行っていない。`results/` は空である。

## 規約（`docs/development-guidelines.md` §10 / `data-privacy` Skill）

- **セッション NDJSON は本リポジトリにコミットしない。**
- 生ログは [mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset)（private）の
  `raw/P*/` に置き、**本ディレクトリからは commit hash で参照する**。
- ★ **被験者が書いた本文は保存しない**（content-free 原則）。
  ブロック終了時に実験者が**文字数だけ**を数えて記録用紙に書く（`preregistration.md §3.5` の報告義務）。

## ★ 入力の単位 — 1 ブロック = 1 NDJSON ファイル

`protocol.md §1` で **(a) 1 ブロック = 1 セッション**を採った。したがって:

- 1 被験者 = **10 ファイル**（確証デザイン）／ **4 ファイル**（パイロット P-1）。
- 匿名化（`analysis/anonymize.rs`）が `t` を **session_start 相対 ms** に変換するため、
  ファイル内の時刻はそのまま**ブロック内相対時刻**になる。
- 匿名化により `key` の `vk` は **`category`** になる（`backspace` / `delete` の区別は保たれるので
  `bs_rate` は計算できる）。

## ★ ブロック↔ファイルの対応（`blocks/`）

アプリは HI / LO / copy を記録できない（`App.tsx` は `argumentative` ロック・凍結対象）。
したがって**ラベルの唯一の真実源は記録用紙**であり、それを機械可読にしたものが `blocks/P0xx.json`。

```bash
python3 assign.py --subject P015 --json > blocks/P015.json
# → 各 block に "file"（NDJSON 名）と "produced_chars"（記入パッドの文字数）を書き足す
# → 強制比較は **手で書かない**。フォームの CSV から機械変換する:
python3 forms_to_blocks.py --csv ~/Downloads/G1-M回答.csv --subject P015 --write
# → ★ 転記の整合を必ず検査する（構成・割付との一致・NDJSON 名・強制比較の対応・probe 行 0）
python3 validate_blocks.py --dataset ~/gse-dataset
```

★ **`validate_blocks.py` は転記ミスの検出だけを行う。** 除外も判定もしない（`§3.6` に触れない）。

## ★ B-4 — G1 のデータを Phase1 の較正プールから分離する

⚠️ G1 は**第 1 週（blind 較正）モード**で回すので、`session_meta` に
**`condition=blind_calibration` / `label_pool=calibration_blind`** が刻まれる。
これは **Phase1 の較正セッションとまったく同じラベル**である。

### ⚠️★ 前提が変わった（2026-08-03・研究者判断）— **P-ID は Phase1 と共有する**

**同じ人には同じ P-ID を使う**（1 人の人間に 2 つの識別子を作らない）。
採番元は **Phase1 の運用管理シート「参加者ロスター」ただ 1 つ**であり、G1 側では採番しない。

★ **これは分離の手当てを 1 つ失うことを意味する。**
以前は「G1 は P015 以降」という**被験者 ID の範囲**が、Phase1 の較正セッションとの唯一の切り分けだった。
ID を共有すると **同じ `P0xx/` ディレクトリに、同じ `label_pool=calibration_blind` のセッションが
Phase1 由来と G1 由来の両方入る**。

| リスク | 手当て |
|---|---|
| gse-dataset 側の集計が `label_pool` で拾うと、**G1 のデータが Phase1 の集計に混入しうる** | ⚠️ ★ **ID 範囲による分離はもう使えない**（P-ID を共有するため） |
| ★ `calibration_eval` が `label_pool` で絞っていない件は既知の問題 | ★ **残る分離手段は次の 2 つだけ。どちらも省略しない**（下記） |

★ **残る分離手段（2 つとも必須）**:

1. **`blocks/P0xx.json` の `file` 列** — どの NDJSON が G1 のどのブロックかを**列挙している**。
   G1 側の解析はこれを唯一の入口にするので、**逆流（Phase1 のセッションが G1 に混ざる）は起こらない**。
2. ★ **送付時に G1 であることを明示する** — こちらが**弱い側**である。
   Phase1 側の集計が `label_pool` だけで拾うと G1 を巻き込む。**送付フローで明示的に分ける**こと。

⚠️ ★ **G1 実施日を記録しておくこと**（管理シートの「G1 実施トラッキング」）。
万一 1 と 2 の両方が失われても、**実施日で切り分けられる**最後の手段になる
（⚠️ ただし日付は成果物には出さない・`protocol.md §7`）。

**送付フロー（★ P-1 で通しで確認する）**:

1. 匿名化して `.age` に固める（⚠️ **ファイル名に実名を使わない**。`P0xx` のみ）。
2. ★★ **G1 のセッションであることを送付時に明記する。**
   ⚠️ **被験者 ID では区別できない**（Phase1 と共有しているため）。ここを飛ばすと、
   その人の Phase1 較正セッションと G1 ブロックが gse-dataset 上で**見分けられなくなる**。
3. gse-dataset 側で **Phase1 の較正コホートの集計に入らない**ことを確認する。
4. ★ **`--verify-blocks` / `validate_blocks.py --dataset` を P-1 で初めて走らせる**——
   どちらも**データが 1 件も無かったため一度も実行されていない**。
   P-1 は「解析の前段が実際に動くか」を確かめる初回でもある。

★ **事前登録の変更は不要**（実施・データ管理の問題であって判定基準の問題ではない）。

⚠️ ★ **`blocks/*.json` はコミットしない**（`blocks/.gitignore`）。
NDJSON のファイル名には**セッション日時**が入り、再識別の手がかりになるため。
`analyze.py` の出力（`results/metrics.json`）には**ファイル名も日時も出さない**。

## 実施時に記入する

| 項目 | 値 |
|---|---|
| gse-dataset commit hash | TBD |
| 被験者 ID（P0xx） | TBD |
| セッション数 / ブロック数 | TBD（確証デザインは 1 人 10 ブロック = 10 セッション） |
| 実施 OS | TBD（★ `ime_dwell_med` の可用性に効く・`env.md`） |
| ★ `GSE_DISABLE_PROBES` | TBD（**必須 = 1**・`preregistration.md §5.4`。⚠️ `validate_blocks.py --dataset` が客観検証する） |
| NDJSON の hash | TBD |
| 課題文セット ID | TBD（`materials/topicNN_{lo,hi}.md`・パイロットは `topic01` のみ） |
| 配置（A / B） | TBD（`assign.py` が被験者番号から決定的に出す） |
| 凍結した n（`preregistration.md §2.4`） | TBD（**パイロット後・確証データ取得前**に凍結し、日時と commit を `notes.md` に記録する） |

## 課題文について

- パイロット用: **`topic01` の LO / HI ＋ `copy`** を作成済み（`materials/`）。
- 本番用: **8 題材 × 2 版**（`preregistration.md §2.7` の counterbalance）。
  ★ **第 3 版で作成済み**（`validate_materials.py --strict` が緑）。
  ⚠️ パイロットの結果（資料の量・ブロック長）を受けた修正は `§2.8` が許容している。
- ★ **課題文は被験者の産出物ではない**ためリポジトリ内に置いてよい。
- ★ **課題文セットをセッション間で使い回さない**（`preregistration.md §3.6`）。
  1 人が同じ題材を 2 回見ることは無い（`assign.py` が保証する）。
