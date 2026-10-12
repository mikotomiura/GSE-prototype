# context A（査読者役と監査役の両方に渡す）

stage: `prereg`（事前登録の下書き・凍結の前）。round 1。対象物のコミット: `c1e96efe`（ブランチ `docs/public-keystroke-matching-prereg`）。

## 対象物の概要（1 段落）

公開の打鍵の記録に施された加工（Kaggle の `q` のマスク・キーの種類への縮約・時刻の丸め・区間の長さを粗くする・置換・並べ替え・抑制）が、記録から本文を照合する攻撃にどこまで効くかを、本文の分かる公開データ（英語の自由作文の KLiCKe・日本語 IME の翻訳の ENJA15）で測る実験の事前登録の下書き。論文の投稿先の第一候補は PoPETs。データはまだ取得していない。文書は日本語で書かれている。文中の `[V264]` などは著者の書誌の ID で、書誌の本体は一覧に入れていない（題は対象物の中で読み取れる範囲で扱うこと）。

## 読んでよいファイルの一覧（これだけ）

- C:\GSE-wt-matching-prereg\experiments\20261012-public-keystroke-matching\preregistration.md
- C:\GSE-wt-matching-prereg\experiments\20261012-public-keystroke-matching\config.json
- C:\GSE-wt-matching-prereg\experiments\20261012-public-keystroke-matching\data.md
- C:\GSE-wt-matching-prereg\experiments\20261012-public-keystroke-matching\README.md
- C:\GSE-wt-matching-prereg\experiments\20261012-public-keystroke-matching\SEED
- C:\GSE-wt-matching-prereg\experiments\20261011-g1-copy-self-trial\scripts\align.py（事前登録が「型」として名指す区間の揃えのコード。このファイルだけ。同じディレクトリの他のファイルは読まない）

## 測った値（メインが機械で測った・2026-10-12）

| ファイル | 行 | 文字 |
|---|---|---|
| preregistration.md | 196 | 8,992（節 17・表の行 63） |
| config.json | 60 | 3,494 |
| data.md | 24 | 1,368 |
| README.md | 22 | 1,072 |

原稿はまだ無い（stage `prereg` では欠陥にしない）。

## 投稿規程の一次の抜粋（PoPETs 2027）

取得: 2026-10-12、`curl -sL` で HTML を取り、タグを除いたテキストで逐語を確かめた（照合済み）。

| 要件 | 出典 | 逐語 | 状態 |
|---|---|---|---|
| 範囲 | https://petsymposium.org/cfp27.php | "Papers that treat privacy as a superficial application domain (e.g., if the only relationship to privacy is a privacy-related dataset) do not demonstrate relevance to real-world privacy problems and are therefore out of scope." | 照合済み |
| 倫理の節 | https://petsymposium.org/authors-2027.php | "Authors are required to include a section on ethical considerations per the new 2027 LaTeX template . This section should include a justification of the ethics of the work and information about whether the work was submitted to an external ethics panel such as an IRB or the Tor Research Safety Board . Research that is deemed to not have met adequate ethical standards may be rejected on those grounds." | 照合済み |
| 倫理の指針 | 同 | "See the Menlo Report for detailed guidelines on ethical research." | 照合済み |
| 分量 | 同 | "Submissions and resubmissions to PoPETs must consist of at most 12 typeset pages for the main body of the paper. The main body excludes the three mandatory sections per the 2027 template (ethical considerations, open science, and AI use)" | 照合済み |
| コードとデータ | 同 | "PETS asks the authors to indicate at the time of submission whether the authors plan to release code and data upon acceptance of the paper (see the mandatory open science section in the new 2027 LaTeX template ). If 'no', authors will be asked to provide a brief explanation." | 照合済み |
| 発表 | https://petsymposium.org/cfp27.php | "However, in-person attendance is not strictly required for publication in the proceedings." | 照合済み |
| 締切（参考） | 同 | "Issue 3 Paper submission deadline: November 30, 2026 (firm)" ／ "Issue 4 Paper submission deadline: February 28, 2027 (firm)" | 照合済み |
| 事前登録 | — | 取得した範囲の原文に、事前登録を求める・評価する文は無い | 規定なし |
