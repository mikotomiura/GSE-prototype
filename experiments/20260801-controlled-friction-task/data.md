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
# → 各 block に "file"（NDJSON 名）と "produced_chars"（産出文字数）を書き足す
# → 末尾に "manipulation_check_answers" を書き足す
```

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
| NDJSON の hash | TBD |
| 課題文セット ID | TBD（`materials/topicNN_{lo,hi}.md`・パイロットは `topic01` のみ） |
| 配置（A / B） | TBD（`assign.py` が被験者番号から決定的に出す） |
| 凍結した n（`preregistration.md §2.4`） | TBD（**パイロット後・確証データ取得前**に凍結し、日時と commit を `notes.md` に記録する） |

## 課題文について

- パイロット用: **`topic01` の LO / HI ＋ `copy`** を作成済み（`materials/`）。
- 本番用: **8 題材 × 2 版**が要る（`preregistration.md §2.7` の counterbalance）。**未作成**。
  パイロットの結果（資料の量・ブロック長）を見てから作る。
- ★ **課題文は被験者の産出物ではない**ためリポジトリ内に置いてよい。
- ★ **課題文セットをセッション間で使い回さない**（`preregistration.md §3.6`）。
  1 人が同じ題材を 2 回見ることは無い（`assign.py` が保証する）。
