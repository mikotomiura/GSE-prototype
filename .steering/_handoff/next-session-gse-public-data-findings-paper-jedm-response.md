# 次のセッション —— 論文 1: JEDM から返事が来たときの対応

> 作成: 2026-11-07。JEDM の編集部・査読者から返事（デスクでの判断、確認や不備の指摘、査読の結果）が来たときに、このファイルから始める。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。CS1 の著者の返事は別の引き継ぎ `next-session-gse-public-data-findings-paper-cs1-reply.md`。

## 投稿の記録

- 誌: Journal of Educational Data Mining（JEDM）。OJS 3.5。節 Articles・単盲（匿名版にしない・判断 42）。査読者 3 名・3 か月を目指すと About にある。掲載料なし・CC BY-NC-ND 4.0。
- 投稿: 2026-11-07（サイトの時刻 03:21:40）・投稿番号 1484・状態 Queued（stage 1）。ダッシュボードはログインの後に https://jedm.educationaldatamining.org/index.php/JEDM から入る。
- 投稿した版: 草稿 v8（`papers/public-data-findings/manuscript/`）。本文の PDF 323,529 バイト・SHA-256 5eab8d6f…、カバーレターの PDF 40,571 バイト・SHA-256 6e0f4dce…。どちらも投稿の画面から取り直して手元と一致した。組み直すと時刻で SHA-256 が変わるので、照合はシステムから取り直したもので。
- システムの欄にだけ入れたもの: 要旨（`papers/public-data-findings/submission/abstract-plain.txt`）、キーワード 5 つ、参考文献 66 件（main.bbl から素の文）、編集者への欄（カバーレターの本文）、所属「Independent Researcher」。ORCID の欄は空（原稿とカバーレターに番号）。
- 記録: `.steering/20261105-public-data-findings-paper/paper-write/submission-prep.md` の「投稿」の節、判断は同じ dir の `decisions.md`（判断 42 まで）。
- 公開物: プレプリント Zenodo 10.5281/zenodo.24026330（誌名は書いていない・研究者の判断）。公開 repo https://github.com/mikotomiura/stall-runup-equivalence （手元 `~/stall-runup-equivalence`・v0.2.2 = 3ea2591・Zenodo 10.5281/zenodo.24026278）。

## 読む順

1. このファイル
2. 返事の全文。メールは研究用のアカウント（mmiura.network@gmail.com）に届く。Gmail のコネクタは別のアカウントにつながっているので、研究者が貼るか、研究者がログインした Chrome で私が読む（`browser-verification` Skill を先に読む）。ダッシュボードの文も Chrome で読める。
3. `.steering/20261105-public-data-findings-paper/decisions.md`（判断 36〜42）と `paper-write/submission-prep.md`
4. 原稿 `papers/public-data-findings/manuscript/sections/` と `appendix/`
5. 返事の内容によって: `.steering/20261105-public-data-findings-paper/attack-me/manuscript-paper1/`（round 1〜6 の指摘と未決の一覧。重なる指摘があれば材料になる）、`experiments/20261106-findings-paper1-exploration/notes.md`

## 手順（返事の種類ごと）

### A. 採否を決めずに確認や不備の指摘が来た場合（書式・ファイル・宣言・利益相反など）
1. 指摘を逐語で写し、何を直せば足りるかを一次資料（JEDM の Submissions・Author Guidelines・Competing Interest Guidelines の頁。curl で取り直す）で確かめる。
2. 書式だけなら直して組み直し（`manuscript/BUILD.md`・テンプレートは JEDM の頁の `2024_08_02_jedm-latex.zip`）、ダッシュボードで差し替える。上げるのは Chrome で私がしてよいが、送る前に研究者に確かめる。
3. 内容に触れる直しは C と同じ扱いにする（投稿中は査読への対応としてしか原稿を変えない）。

### B. デスクでの不採録（査読に回らなかった）
1. 理由を逐語で写す。
2. 次の投稿先は研究者が決める。目的から選ぶ（memory の feedback-venue-by-purpose・無料の道を先に）。比較の出発点は `paper-write/venue-fit.md`。
3. 新しい投稿先の規程を取り直し、テンプレート・語数・宣言を当て直す。プレプリントは誌名を書いていないので直さなくてよい。

### C. 査読の結果（major / minor revision）
1. 指摘を 1 件ずつ表にする（番号・査読者の言葉の逐語・種類・対応の案）。置き場は `.steering/20261105-public-data-findings-paper/revision-1/`（新しく作る）。
2. 各指摘の正否を、メインが一次資料（コード・結果のファイル・凍結した事前登録・引いた文献の本文）で確かめる。査読者の言葉を根拠にしない（`verify-before-claiming`）。
3. 対応の採否は研究者が決める。AskUserQuestion で 1 件 1 問、指摘の概要と論点（どの問いで答えが変わるか）と推奨を書いて聞く。推奨は「研究として強いか」で決める（計算が要らないかで決めない）。
4. 新しい計算が要る場合は、計算の前に条件を書いてコミットする（`experiments/` の規約・`reproducibility-discipline`）。凍結した事前登録・manifest・既存の結果は書き換えない。確認の検定に当たるものを足すなら、事前登録の外の分析として書き分ける。
5. 原稿を直す。直しは足すより移す（本文は簡潔に、細部は補足へ・paper-write の方針）。応答書（response to reviewers）を英語で書き、指摘ごとに直した箇所（節・頁）を示す。
6. 直しの後に attack-me を stage `revision` で回す（同じ panel＋E・Codex を加える。既知の未決の一覧を Codex に添えて判定に数えないよう頼む）。推移を見て minor が続けば閉じる。Codex に送ってよいのは原稿と応答書まで。査読の文そのものを送るかは研究者に確かめる。書き手ごとの値・CS1 のデータは送らない。
7. 組み直し、ダッシュボードの改訂の段から改訂稿・応答書を上げる（Chrome で私が上げてよいが、送る前に研究者に全頁を見てもらう）。
8. プレプリントを新しい版にするかを研究者に聞く（Zenodo の newversion を API で。公開は押す前に確かめる）。
9. 公開 repo の `paper/` を改訂稿に写し直すか、コードが変わるなら版を上げる（`assemble.sh` → 写す → `tools/verify.sh ~/gse-public-data` が 0 → push と release と Zenodo は研究者に確かめる）。原稿の code の DOI をその版に差し替えると、その版の写しは前の版の DOI のままになる（版の DOI は版の中に書けない）。

### D. 不採録（査読の後）
1. 理由と査読の文を逐語で写し、C の 1〜2 と同じく正否を確かめる。
2. 直すかと次の投稿先は研究者が決める（B の 2〜3）。

### E. 採録
1. 校正と著作権の手続きは研究者がする（CC BY-NC-ND 4.0）。
2. プレプリントの記録に誌の DOI を足す（Copyright Notice が求める）。Zenodo の公開済みの記録は metadata の編集で関連の識別子を足せるか API で確かめ、無理なら新しい版。
3. 公開 repo の README（英・日）と CITATION.cff の引用を誌の書誌（巻・号・頁・DOI）に直す。push と release は研究者に確かめる。

## 査読への材料: 停滞の定義を変えた検査（2026-11-16〜17・投稿の後）

投稿の後に、論文 1 の 2 つの読みが停滞の定義しだいで変わらないかを確かめた（ADR-054 D4）。2 つの読みとは、(a) 推定器の 30 秒の上がりが帯の内で同等であること、(b) 同じ対で学習器が上がりを上回ること。原稿はまだ変えていない。査読で「定義しだいではないか」「学習器との差は頑健か」と問われたときの材料に使う。

- 置き場: 枝 `exp/gse-r1-definition-check`（worktree `/Users/johnd/GSE-prototype-r1-defcheck`・論文 2 の枝から切った）の `experiments/20261116-r1-definition-check/`。条件は `conditions.md`・`conditions-2.md`（値の前にコミット）、結果は `notes.md` と `results/`、判断は `.steering/20261116-gse-r1-definition-check/decisions.md`（判断 1〜10）。位置づけの記録は main の `docs/research-positioning.md` §1.4（PR #422）。
- 結果（崩れた定義は無い）:
  - CS1 の holdout では、主の定義の他に重なりを除いて 93 定義を試した。内訳は、θ の累積・分位 0.995・窓 15 秒と 60 秒・分位 0.95・θ 固定 10 秒・条件 A を文字だけで数える・押下の空白 5 分で区切る、の 8、停滞の長さ 60 秒と 90 秒、論文 2 の全格子 89。全ての定義で (a)(b) が成り立った。上がりの区間は 0.462〜0.524、学習器 − 上がりの差の下限は最小 0.015（分位 0.995 の定義）。
  - KLiCKe（4,992 人）では 7 定義を試し、全てで (a)(b) が成り立った。学習器を KLiCKe で回したのは初めて（AUC 0.60〜0.68）。
- 使うときの注意:
  - 地位は探索。CS1 は holdout を開けた後の [E-H]、KLiCKe は [E] である。事前登録の確認の検定ではないので、改訂稿に入れるなら事前登録の外の分析として書き分ける。
  - 付録にすでに推定器の側の 4 版（θ の累積・q0.995・W15・W60）がある（`supplement.tex` の感度の表）。新しいのは、学習器の側と、それ以外の定義である。
  - 出すのは集計値だけ（CS1 の約束）。
  - 言えないこと: 全格子は論文 2 の格子の中に限る。CoAuthor と対照の休止の幅は試していない。学習器の差の内訳は見ていない。
  - 実験の枝は main にも論文 1 の枝にも入っていない。改訂で使うなら、論文 1 の枝に写すかを先に決める。

## 査読が進むまでにしてよいこと

- 待つあいだに原稿の内容を変えない。他誌に出さない。
- 状態を見るなら、研究者がログインした Chrome でダッシュボードを読むか、`/index.php/JEDM/api/v1/submissions/1484` を読む（書き換える呼び出しはしない）。

## 気をつけること

- 公開 repo に `.steering/`・GSE の `docs/`・未踏の情報を入れない。公開 repo のコミットに `Claude-Session:` を書かない。書き手ごとの値・推定の行・取り置きの id の一覧は、CS1 の著者の許しが無いかぎり出さない（別の引き継ぎ）。
- Zenodo は API だけ。token は `~/zenodo/zenodo_token.txt` をプロセスの中で読むだけ。OSF は触らない。
- パスワードは入れない（ログインは研究者）。最後の送信の前に止めて研究者に確かめる。
- `.codex/budget.json` は未ステージのまま。
- 返答とファイルは日本語、記号を控える。公開物・応答書・原稿は英語の学術的な文で、作業の言葉を入れない。未決は AskUserQuestion で日本語で聞く。
