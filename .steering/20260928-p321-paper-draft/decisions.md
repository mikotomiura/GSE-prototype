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
- ★ `claims()` が確かめる主張（1 巡目の後の全量）: 条件づけの効果（点推定が負・区間が 0 を含む・表示値で判定）／ 分母だけの効果の区間が 0 未満 ／ D1 の分子の効果の区間が 0 を含まない・D2 は 0.0 から ／ fresh の成分が 4 定義で同じで DF1 の最小値に一致（整数で比較・層が全 episode を分割）／ 未解決かつ参照なしの大半が DF3 ／ 全体・committed（逆向き・差は 1 episode）・fresh（全体と同じ向き）の参照の偏り ／ committed は未解決も参照も多い ／ [P433] の再現の内訳（strict が最多・他 3 定義は同数・時間の割合と短い episode は全定義で再現・「committed は全部」は issue tracker を含むときだけ・fresh と開発者は含まないときだけ・活動数と全体と長い episode はどれでも再現しない）／ D2 の表＋本文で分子の効果が半分（同じ n・b > 0）／ D2 の table+text で分母だけの効果が分子の効果の 2 倍超 ／ D2 の k が 1..b で一意に決まる。
- **検査の効き目（対照・論文用リポジトリの複製で実施）**: ① `main.tex` のキーを 1 か所だけ未定義のものに書き換え → LaTeX が `unknown key` で exit 1 ／ ② `metrics.json` の値を 1 つ変える → `build.sh` Step 2 が赤 ／ ③ 条件づけの効果を正にする → `claims()` が止める ／ ④ 無変更 → exit 0。★ 1 巡目の後、③ の型は `make_results.py --selftest`（10 通り）に移した。
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

## 判断 9: /cross-review の Codex 系統は原稿（論文用リポジトリ）に当て、GSE 側の文書は Claude 系統で見る

- **判断日時**: 2026-09-28
- **背景**: 主成果物は論文用リポジトリの原稿で、`scripts/run-codex-review.sh` は実行した場所の git の差分しか取れない。前タスクの Codex は GSE 側の文書だけを見ていた（1 巡目の出力逐語「解析コードは含まれていないため」）。
- **採用**: 論文用リポジトリのコミットを GSE の作業用 worktree に `git fetch`（ブランチも作業ツリーも変えない・オブジェクトだけ入る）し、ラッパーをそのまま `9c73181..e9c8e2b -- paper/main.tex paper/make_results.py paper/build.sh .gitignore README.md` で呼んだ。★ 機密フィルタ（rc=0）・予算ガード・`-C` の一時ディレクトリ・記帳はラッパーのものがそのまま効く。`paper/refs.bib`（書誌だけ）と `paper/results.tex`（生成物）は入力から外した。
- **予算**: ⚠️ 台帳がブランチごとに分かれていた（メインの checkout = IME ブランチは 96,246・origin/main は 198,283）。★ 一次で確かめると IME ブランチの 96,246 は o1-resilience の記帳 `07554770` で、origin/main の 198,283 に**含まれている**（重複ではない）→ 今日の実使用 = 198,283・残り約 101,700。1 巡の実績（33k〜77k）から、**Codex は原稿に 2 巡**、GSE 側の文書（references.md・作業記録）は code-reviewer と security-checker で見ると決めた。
- **1 巡目の実消費**: 41,889（198,283 → 240,172・invocations 5 → 6）。記帳は worktree の `.codex/budget.json`（本ブランチでコミットする）。
- ⚠️ `SHA-256` の全桁（L10 の指摘）: [V178] の PDF = `457858d6af60ccdef5f457a0e477e9773c55a25aa6af8f612bb532c994d0fc29`（IEEE の OA 版・841,101 B）。

## 判断 10: /cross-review 1 巡目の裁定（2026-09-28）

- **レビュー**: Codex（原稿の差分・判断 9）／ code-reviewer ×2（原稿の主張・ツールと GSE 側文書）／ security-checker。★ 入れ子を避けるため `cross-reviewer` エージェントは使わず、メインから 4 本を並列に起動した。CRITICAL なし。
- ★ **採用（HIGH）**:
  1. ⚠️★★★ **凍結の開示が足りなかった**（code-reviewer）。★ 一次（`experiments/20260906-p321-resumption-baseline/notes.md` §2.2・§3）で確認: strict/DF1 の R0 = 70/89・R1 = 60/73・R0′ = 60/89 と分子の効果 +11.2pt は **2026-09-06 に既に計算していた**。→ 原稿の Method に 3 つ目の例外として「主推定値は凍結前から既知・凍結が守るのは追加の定義と区間の手続きと D2」と書き、統計的結論妥当性の節にも移した。論文用リポジトリの `NOTES.md`（Freeze）にも同じ事実を書いた。
  2. 結論節で C1 の限定（区間・D2 の打ち切り）が落ちていた・「打ち消し合う」は D2 の table+text に当たらない → 直した。
  3. 未解決かつ参照なしの 10 件の終端コードを数えていなかった（提言 3 と矛盾）→ ★ 解析の出力に `unresolved_no_consult_by_code` を追加（記述のみ・既存の値は 1 つも変わらない・`NOTES.md` Deviations 7）。★ **10 件のうち 8 件が DF3（後で戻る）**だった → 「未解決」は「観察された単位の中で解決しなかった」であって「諦めた」ではない、と原稿の複数箇所に入れた。
  4. `build.sh` がログの無いとき黙って成功する（Codex と code-reviewer が独立に指摘）→ 古いログを消し、ログを必須にした。偽の Tectonic で対照を取った。
- ★ **採用（MEDIUM / LOW）**: RQ4 の「省略で半分」は向きが逆（Codex・code-reviewer）／ 本文の直書きの数値をマクロに（Codex）／ `make_results.py` の値の許可リスト・n/a で停止・表示値での判定・整数比較・空のゲート・k の一意性・`--selftest`（Codex と code-reviewer）／ `curl -f` と照合してから mv・`.gitignore`・`.gitattributes`（security-checker・code-reviewer）／ LLM の使用の開示を D2 のコーディングと文献探索に広げた（security-checker・code-reviewer）／ README のライセンス（`paper/` のスクリプトは Apache-2.0・原稿は未定）／ RQ3 を「起点で違うか」に・fresh で向きが残ることを明記／ 再現の言い過ぎ（公表された定義 ≈ +OT2 で 3/8）と原著者の手落ちの推測を削除／ Shepperd の reproduction は RQ4 だけ／ ICH の対句をそのまま引き直した／ G1 の表に検討対象の概念の行／ P1TA の非対称／ p0 は確率と書く／ Hellas は q の補数に対応／ q の定義に N > S > 0／ [V178] の出典欄・カードに [V179]–[V183] の使用箇所。
- **採用しない**: GitHub の URL にアカウント名（security-checker LOW 6）→ EMSE は single-blind（判断 17・前タスク）なので不要。figshare の `/s/` リンク（LOW 7）→ DOI が存在しない（`DATA.md`・private link でしか配っていない）ので現状のまま。
- **研究者に確認すること（報告に載せる）**: コミットの著者メールが公開時に出る（security-checker MEDIUM 3）・原稿のライセンス・LLM の開示の文面。
- ★ 論文用リポジトリ `1db0cab`: `bash run.sh`（許可フラグなし）exit 0・`bash paper/build.sh` exit 0（`--selftest` を含む）・21 頁・要旨 239 語。

## 判断 11: /cross-review 2 巡目の裁定（2026-09-28）

- **範囲**: 1 巡目の修正（論文用リポジトリ `e9c8e2b..1db0cab`・GSE `ab72170e..e30b6f33`）の境界条件。Codex（判断 9 と同じ方法・実消費 43,585 = 240,172 → 283,757・invocations 6 → 7）と Claude の code-reviewer。CRITICAL なし。
- ★ **採用（HIGH）**: ⚠️★★★ **凍結の開示が一次資料より狭かった**（code-reviewer）。★ 一次（`experiments/20260906-p321-resumption-baseline/notes.md` L80–105・§9.2、GSE コミット `068e3bfb` 01:24 と論文用リポジトリの凍結 `416a0fc` 02:16）で確認: 2026-09-06 に **strict と broad（= +U）× DF1 / DF1+DF2 の点推定**と**主系列の Wilson 区間**、凍結前に **strict の起点別の層**も計算済みだった。→ ★ 原稿の Method を「報告する点推定のほとんどは凍結前から既知。凍結が固定したのは報告する定義の集合・クラスタ・ブートストラップの手続き・本文記述の追加規則だけ」と書き直した。`NOTES.md`（総論と Freeze）も揃えた。⚠️ 1 巡目の判断 10 採用 1 の「凍結が守るのは追加の定義と区間の手続きと D2」は**狭すぎた**（本判断で置き換える）。
- ★ **採用（MEDIUM / LOW・Codex P2 / P3 を含む）**: 「区間が 0 を含む」は表示の端点を含む（`<=`・陽性対照を追加）／ D2 の p0 > 2.5% と下端が生の値で 0 を検査に追加、Method は「exactly 0」→「expected to be 0（D2 では 0）」／ `--selftest` は止まった理由まで照合する（★ これで「解決 0 件」の改変が別の理由＝矛盾した counts で止まっていたことが分かり、改変を整合する形に直し、counts の矛盾そのものを検査に足した）／ 1 巡目で足した主張 4 本の改変・想定外の終端コード・None・ハイフンのマイナスを追加（改変は計 21 本）／「+OT2 に最も近い」→「+OT2 か +OT2+U（どちらも 3/8）」・「our operationalisations」／ DF3 は意図の記録で後続の作業とは紐づかない／ LLM の開示 (3) を事実に合わせた（本文を読めなかった文献がある・引用の照合はアシスタント、D2 の 3 文は著者）・[V174] は返答論文が伝える範囲だけで書く／ `build.sh` は `main.blg` も必須・`--version` の失敗を案内。
- **誤検知**: Codex P1（生成物の更新が差分に無い）→ 範囲から外したのはメイン（`results/`・`results.tex` は `1db0cab` に入っている）。Codex 自身も条件付きと書いていた。
- **3 巡目は回さない**: Codex の今日の残りは約 16,000 で 1 回分（30,000）に足りない。2 巡目の HIGH は一次資料で確かめて直し、検査の側は `--selftest`（21 本・理由まで照合）で効きを確かめた。
- ★ 論文用リポジトリ `be754be`: `bash run.sh`（許可フラグなし）exit 0・`bash paper/build.sh` exit 0・21 頁・要旨 239 語（pypdf で R′ を 2 語と数えた値）。

## 判断 12: 著者情報と、研究者が選んだ残りの決定（2026-09-28・研究者の回答）

- **著者**: Mikoto Miura・mmiura.network@gmail.com・Hiroshima, Japan（研究者が指定）。★ 所属は無く、EMSE の規程（前タスク判断 17: 所属の無い著者は都市と国だけ）どおり `\affil` は都市と国だけにした。
- **Statements and Declarations**: すべて該当なし（研究者の選択）→ Funding「組織からの支援なし」／ Competing interests「開示すべき利害なし」／ Ethics「該当なし（公開・オープンライセンスのデータと論文の二次分析で、人からの新しいデータ収集はない）」／ Author contributions「単著・着想・解析・執筆に責任を負う。LLM の使用は Sect. 5.5」。
- **LLM の使用の開示**: 今の文面（4 項目＋「The author is responsible for the content」）のまま（研究者の選択）。
- **題**: 仮題のまま確定 —— *When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets*。
- **原稿のライセンス**: 投稿時に決める（README の「未定」のまま。arXiv に出すときに出版社の規程を一次で確かめる）。
- **論文用リポジトリのコミット著者**: 過去のコミットは書き換えない（凍結の順序を示すハッシュを保つ）。以後のコミットはリポジトリ固有の設定で Mikoto Miura <mmiura.network@gmail.com>（`git config --local`・最初のコミットは `4a81a43`）。⚠️ 公開すると、それ以前のコミットの著者（John Do <johndo.mik.080@gmail.com>）も公開される。
- **main の CI**: PR #254 の merge 後、macOS の self-hosted runner が「Complete job」で通信を失って failure（検査ステップはすべて緑）→ 研究者の選択で失敗したジョブを 1 回だけ再実行した。
- ★ 論文用リポジトリ `4a81a43`: `bash paper/build.sh` exit 0・21 頁・仮置きは Data availability の DOI だけになった。
