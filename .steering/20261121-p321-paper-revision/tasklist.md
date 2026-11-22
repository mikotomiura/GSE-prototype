# tasklist — p321-paper-revision

## 0. 始める
- [x] grill（判断 1〜10）・`/start-task`（worktree `C:/GSE-wt/p321-desk-reject`・ブランチ `docs/p321-emse-desk-reject`・attack-me round 1 の記録 `bddf51f6` を取り込んだ）
- [x] 出し先の候補を一次で比べる → 研究者が選ぶ（判断 6）→ **JSS**（判断 11）
- [x] JSS の投稿ガイドの残り（LaTeX・Highlights・キーワード・要旨・生成 AI・データ・Open Science）と arXiv 2601.19217v2 の「依頼 20 件の上限」を一次で読んだ（design-v1.md §0）
- [x] design.md（v1）→ `/reimagine`（v2 は独立の Opus）→ ハイブリッドを採用（`design-comparison.md`）

## 1. 段（design.md §3 の S0〜S9）
- [x] S0a: journal 版の本文（NSF PAR の版）で確かめた → 件数は本文に無く、v1 が 10・79（判断 12）
- [x] S0b: 照会の文面（`inquiry-alaboudi-latoza-draft.md`）
- [x] S0c: 研究者が送った（2026-11-21・判断 13）。待つ目安は 2026-12-05
- [x] S1: 枠を elsarticle に移した（`061938a`・本文の差分 0・18 頁・判断 14）。推薦の査読者の欄は S9 で研究者が確かめる。Open Science Initiative に参加（判断 13）
- [x] S2: B（0 件・浅い）／ H（CR2-BM を採用）／ F（候補・査読者 8 人）→ `survey-s2.md`（判断 15・16）。⚠️ 使う行は S5 で一次を確かめる
- [x] S3: 補助解析を追加だけで足した（`c3e1133`・旧い値の不変は SHA-256 で検査・判断 16）／ K のライセンスは一次で CC BY 4.0（派生表の実装は S9 の前に）
- [x] S4: 名前は U・A・A|R ＋内容名・概念は unaided resolution（判断 17・研究者の選択）→ 一括で置き換えた
- [x] S5: 本文を内側から（A・B・E・F・G・H・I・J・K・L・M・minor・nit。各行に直した箇所か直さない理由）／ `NOTES.md` の "other project" を消す
  - [x] 前半: §4〜§8・結論（判断 18・`b80b2d8`〜`c84c86b`）
  - [x] 後半（判断 19・`8109d1f`〜`8129e92`）: 序論・§2（B の 0 件と検索の範囲・F の系統・L）／ §5.5 の LLM（E: モデルの版・日付・プロンプト・人が確かめた範囲・研究者に聞く）／ RQ4（G: 22 件の根拠・報告値どうしの算術・人の照合・照会）／ 要旨（−3.5 の符号・250 語）／ 声明を JSS の形に（CRediT・competing interest・生成 AI の節を文献表の直前）／ D1 と D2 の範囲を分ける（L256 の all/ce）／ 合わせ込みの的と検査の区別（L160）／ 再現一式の文言（config `_comment`・`analyze.py` の docstring・NOTES の "other project" と "drift" と L10）／ 引用を GSE の `docs/references.md` に登録（citation-ssot）
  - [x] K: 派生表（`5372cdb`） `results/d1_episodes.csv`（URL・名前・セッション ID なし）を実装する（§8 に約束を書いた）
- [x] S6: 題は案 A（判断 20）／ 要旨 249 語・Highlights 5 本・キーワード 6（build.sh が検査）
- [x] S7（判断 21〜23）: 研究者の通読と修正案の採用 → (1)(2)(3)・要旨・一般化は実施（`a55b9bb`）。残り: 文献検索 B のやり直し → §2.5 と付録 ／ 生成 AI の申告の「読んで直した」を研究者に聞く
- [ ] （旧 S7 の項目）研究者の通読と手入れ（記録する）／ journal 版の 8 つの報告値を研究者が PDF と照合するか（すれば §5.3 の文を直す）／ 通読の後に生成 AI の申告へ「読んで直した」の文を足す ／ Highlights とキーワードを見てもらう
- [ ] S8: attack-me round 2 → 研究者が採否 ／ `/cross-review` 2 巡
  - [x] attack-me round 2（`c077e5bf`・判断 25）。研究者が採否を決めた
  - [x] 文献検索 B を OpenAlex で回した（判断 26・INSTANCE 1 = Sychev 2022）→ 付録 `supplement/literature-search/`・§2.5・序論・要旨・§5.5 (3)（`d6e7962`・`b12e222`）
  - [ ] round 2 の直す一覧（verdict.md §4・判断 25）を実施する。研究者の D2 の手での数え直しを受け取る（手順と記入表は `d2-hand-recount.md`）
    - [x] D2 の 4 件の打ち切り（`9c4c3e7`・Deviations 12）・"positive in both" を観察した単位の中に限る
    - [x] Hellas の例の向き（`68ce171`・52.5% は make_results が計算）
    - [x] 2 つ目の実装の文（入力に在った値 / 無かった値・span と sum・指示文が残っていない・格を下げた）・duration の定義・"agreed to be observed"（`abd08f7`）
    - [x] 要旨の 3.5 の言い方（\Ro{} exceeded \Rz{}）・語数 245・序論 21 行
    - [x] 手での数え直しの結果を §5.5 (2)・§8・audit README に書いた（判断 27・`caeaece`・一致）
    - [x] 構成概念の分け・最後の DF3 の理屈（判断 28・`25f7191`）
    - [x] 再利用する人の表・debugging のログ研究の文献・CV3 と MacKinnon の言い換え（判断 28）
    - [x] 重複を消す（区間の但し書きを方法の節に 1 回・後の 7 つの変更は NOTES へ・凍結の前の値の開示は残した・`27a8ef2`）。DF3 の但し書き（189・324・365・390 行）は持ち帰りに関わるので残した
    - [ ] 残りの minor と nit（verdict.md §4）／ Data availability の DOI は S9
    - [ ] NOT-READ のうち機関リポジトリの 4 件（K53・K59・K61・K143）をブラウザで読むか（任意）
  - [ ] `/cross-review` 2 巡（直した後）
- [ ] S9: 照会の返事か未回答を反映（RQ4 の "at the time of submission we had not received a reply" を確かめる）／ README の引用の bibtex と Data availability の DOI を新しい版に ／ 新しいタグ ／ Zenodo の新しい版とプレプリントの下書き → 研究者が publish と JSS への投稿 → 原稿 ID を記録
