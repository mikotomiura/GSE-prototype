# 重要な設計判断

★ 2026-09-28 の grill（研究者との対話・4 問）で判断 1–4 を確定した。前提は前タスク `.steering/20260928-p321-reanalysis-paper/decisions.md` の判断 1–17。

## 判断 1: テンプレート = Springer Nature LaTeX テンプレート v3.1（2024 年 12 月）・`sn-basic`（著者名と年）

- **判断日時**: 2026-09-28
- **背景**: EMSE の規程ページ（前タスク判断 17）には (a) 規程ページの LaTeX マクロ zip と (b) Springer Nature の LaTeX テンプレートの 2 系統があり、Word も受け付ける。
- **研究者の選択**: 「両方取得して比べる」。基準は grill で合意した「著者名と年の引用ができ、新しい方」。
- **一次で確かめたこと**（2026-09-28 にダウンロード・scratch で展開）:

  | | (a) 規程ページの zip | (b) SN テンプレート |
  |---|---|---|
  | URL | `https://media.springer.com/full/springer-instructions-for-authors-assets/zip/468198_LaTeX_DL_468198_01072021.zip` | `https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12`（`https://www.springernature.com/gp/authors/campaigns/latex-author-support` の "Download the journal article template package (December 2024 version)"） |
  | サイズ / SHA-256 | 189,200 B / `2e5bbfde3deae204cf6f2926ba2d9088d02bec969a442f01db1fc5b373074453` | 901,814 B / `812e76dcaa9c28dc1bff1fb6065d51729b67d4ea140552a05088317414a3ecae` |
  | クラス | `svjour3.cls`（`history.txt` の最終更新 2021-06-18） | `sn-jnl.cls`（`sn-article.tex` の 1 行目 "Version 3.1 December 2024"） |
  | 著者名と年 | `spbasic.bst` | `sn-basic.bst`。逐語 "For author-year citation style: \documentclass[sn-basic]{sn-jnl}"・"Per default the reference list entries are alphabetized." |

- **採用**: (b)。`\documentclass[pdflatex,sn-basic]{sn-jnl}`。
- **理由**: 両方とも著者名と年の引用ができる → 新しい方。★ サンプル原稿を `sn-basic` に切り替えて Tectonic で組み、PDF で `(Jones et al., 1990)` の形の引用と、第一著者の姓のアルファベット順の文献リストを確認した（EMSE の規程「著者名と年」「第一著者の姓のアルファベット順」に合う）。
- **トレードオフ**: (a) は EMSE の規程ページに直接置かれている。(b) は Springer Nature 全体の汎用テンプレートなので、EMSE 固有の指定があれば投稿前に合わせる。
- **影響範囲**: 原稿の書式・`.bib` の書き方（natbib の `\citet` / `\citep`）。
- **見直しタイミング**: 投稿システムがクラスを拒んだとき、または EMSE の規程ページが (a) だけを指定するようになったとき。

## 判断 2: 手元のビルド = Tectonic 0.17.0 を scratch に置く

- **判断日時**: 2026-09-28
- **背景**: この PC には TeX（pdflatex / latexmk / lualatex / xelatex / bibtex / biber）が入っていない（`command -v` で確認）。
- **研究者の選択**: Tectonic を scratch に置く（システムには入れない）。
- **一次**: GitHub Releases `tectonic@0.17.0`（2026-07-27）`tectonic-0.17.0-x86_64-pc-windows-msvc.zip`（21,060,223 B・SHA-256 `f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f`）。初回のビルドで TeX のパッケージとフォントをネットから取った。
- ⚠️ **分かった制約**:
  1. **EPS の図は扱えない**（サンプルの `fig.eps` で xdvipdfmx が停止: "PostScript images are not supported by Tectonic"）→ 図は PDF / PNG で作る。
  2. ⚠️★ **Tectonic のエンジンは XeTeX で、投稿先・arXiv の pdfLaTeX とは別物**。手元で組めても pdfLaTeX で同じに組める保証は無い → **投稿前に pdfLaTeX（Overleaf か投稿システムのプレビュー）で一度組む**ことを残課題にする。
- **影響範囲**: `paper/build.sh`。
- **見直しタイミング**: pdfLaTeX で組んで差が出たとき。

## 判断 3: このタスクの範囲 = 全節の初稿まで ＋ /cross-review 2 巡

- **判断日時**: 2026-09-28
- **選択肢**: A: 全節の初稿（推奨）／ B: 引き継ぎ §2 の 1–4 まで ／ C: 骨組みだけ
- **採用**: A（研究者の選択）
- **書き順**: Results → Measures / Data / Method → Introduction / Related work → Discussion / Threats → Conclusion・Data availability → Abstract（主張を先に固定し、前置きを後から主張に合わせる）。
- ★ 著者情報・所属（または居住する都市と国）・Statements and Declarations（Funding / Competing interests / Ethics 等）は**仮置き**にし、最後に研究者へまとめて確認する（推測で埋めない）。

## 判断 4: /reimagine は適用しない

- **判断日時**: 2026-09-28
- **理由**: 原稿の執筆で、主張と根拠の対応・書いてはいけないことは `outline.md` と前タスクの判断 1–17 で確定している（研究者の選択）。

## 判断 5: テンプレートのクラス・bst は論文用リポジトリに入れず、公式 zip から SHA-256 を照合して取り込む

- **判断日時**: 2026-09-28
- **背景**: 論文用リポジトリは投稿時に公開する（前タスク判断 10・11）。`sn-jnl.cls` の冒頭は LPPL 1.3c を掲げつつ、逐語 "This file may only be distributed together with a copy of the LaTeX base system." とも書く（LaTeX base から生成されたファイルの定型文が残っている）。`sn-basic.bst` は逐語 "This file can be redistributed and/or modified under the terms of the LaTeX Project Public License"。
- **採用**: 2 ファイルは `.gitignore` に入れ、`paper/build.sh` が公式 zip（判断 1 の URL・SHA-256）から取り出し、ファイルごとの SHA-256 を照合して `paper/` に置く。
- **理由**: 配布条件の読みが割れうるファイルを、公開予定のリポジトリに自分で再配布しない。再現に必要な情報（URL・ハッシュ）は残す。★ データの扱い（`raw/` を入れず、取得手順と SHA-256 を `DATA.md` に書く）と同じ型。
- **トレードオフ**: 公式 URL が変わるとビルドの前に手作業が要る（`build.sh` は zip を手で `paper/` に置けば動くようにする）。投稿用の zip には 2 ファイルを同梱する（投稿システムが要求するため）。

## 判断 6: 原稿の数値と定性的な主張は `results/metrics.json` から生成し、機械で検査する

- **判断日時**: 2026-09-28
- **背景**: 前タスクの判断 12・13 で、丸めた値の足し算の食い違い・「3 倍」などの言い過ぎが 2 巡のレビューで見つかった。原稿に手で数値を写すと同じ型の誤りが入る。
- **採用**:
  1. 本文の解析由来の数値はすべて `\R{<key>}`（`paper/make_results.py` が `results/metrics.json` から `paper/results.tex` を生成）。未定義のキーはビルドを止める。`build.sh` は `results.tex` を生成し直して `cmp` する。
  2. ★ 本文の**定性的な主張**（「条件づけの効果の点推定は 10 セルすべてで負・区間はすべて 0 を含む」「分母だけの効果の区間はすべて 0 未満」「D1 の分子の効果の区間はすべて 0 を含まない・D2 は 0 から始まる」「DF1 の最小値 = fresh の成分で 4 定義とも同じ」「committed は未解決も参照も多い」「表＋本文で分子の効果が半分」「strict 以外の 3 定義は再現数が同じ」「D2 の k」）は `make_results.py` の `claims()` が数値から確かめ、偽になれば生成を止める。
- **検査の効き目（対照・論文用リポジトリの複製で実施）**: ① 未定義キー → LaTeX が `unknown key` で exit 1 ／ ② `metrics.json` の値を 1 つ変える → `build.sh` Step 2 が赤 ／ ③ 条件づけの効果を正にする → `claims()` が止める ／ ④ 無変更 → exit 0。
- ★ 実際に拾ったもの: 初稿で手計算の「1.1 points」を書いていた → マクロ経由の文に直した。「R0 が数える参照なしの episode の約 9 分の 1」は誤り（10/89 は全 episode に対する割合。参照なしの 70 件に対しては 10/70）→ 直した。

## 判断 7: 分解の読み替え（R0 − R0′ = u·q、R0 − R1 = u·(q − R1)）を Measures に置く

- **判断日時**: 2026-09-28
- **背景**: outline C3 は「条件づけの効果が小さいのは、分子の効果と分母だけの効果が打ち消し合うから」と書くが、なぜ負になるかの説明が無かった。
- **採用**: u = 未解決の割合、q = 未解決のうち参照なしの割合とすると R0 = (1 − u)·R1 + u·q。よって R0 − R0′ = u·q、R0 − R1 = u·(q − R1)。★ **定義を足したのではなく、凍結済みの 3 指標の恒等式**（新しい解析ではない）として本文に明記した。値（q = 62.5%・未解決のうち参照あり 37.5%・解決のうち参照あり 17.8%）は `make_results.py` が counts から計算する。
- ⚠️ outline C3 の禁止（「分母だけの効果のほうが大きい」を独立の発見として書かない・「3 倍」と書かない）は守った。初稿にあった「分子の効果は条件づけの効果の 3 倍以上」という文は、判断 12 の「3 倍」と紛れるので削った。

## 判断 8: 区間の手法の出典 [V179]–[V183] を足す（少数クラスタの文献は「類比」として引く）

- **判断日時**: 2026-09-28
- **背景**: 前タスクの `NOTES.md` は「クラスタが少ないと percentile のクラスタ・ブートストラップ区間は名目より狭い」を出典なしで書いていた。原稿には出典が要る。
- **探索**: subagent（Sonnet・20 分・入れ子禁止・scratch 以外に書かない）。★ メインが戻り値を一次で照合した: Cameron et al. 2008（NBER の WP 版）・Cameron & Miller 2015（著者ページの原稿版）・Hesterberg 2015（arXiv 版）は pypdf で逐語一致。Brown et al. 2001 は要旨を OpenAlex から取って一致（本文はスキャンで未読）。Wilson 1927 は書誌のみ（本文はスキャンで未読）。書誌は 5 本とも Crossref。
- ⚠️ **限界**: 少数クラスタの証拠（[V181] [V182]）は**回帰係数の検定**についてで、割合の区間についての研究は見つからなかった → 原稿は "this evidence is indirect" と書き、区間を「不確かさの下限」と読むにとどめた。
- **影響範囲**: `docs/references.md` に [V179]–[V183] を append（`check_citations.py` 違反なし）。[V178] の行に本文を読んだことを追記。
