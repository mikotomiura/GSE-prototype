# タスクリスト

## 準備
- [x] 引き継ぎを読む・worktree を origin/main から切る（`../GSE-wt-matching-prereg`・ブランチ `docs/public-keystroke-matching-prereg`）
- [x] 冒頭の 3 問（判断 6）・所属なし（判断 7）
- [x] 必須 Skill（reproducibility-discipline・citation-ssot・verify-before-claiming・subagent-delegation）を読む

## 再検索（やること 1）
- [x] 被引用の追跡（サブエージェント A）・作文研究の著者別（同 B）・Kaggle の 1 位の解法（Chrome・メイン）
- [x] 一次で確かめる（OpenAlex の数・[V276] の全文・[V275] [V277] [V278] の抄録）
- [x] カード `docs/literature/20261012-public-keystroke-matching-prereg-search.md`・[V275]–[V279]・`_index.md`・check_citations 違反なし・単独でコミット

## 設計（やること 2）
- [x] `design.md`（Claude の案）
- [x] 研究者への問い 2 回（判断 8〜15）
- [x] KeyTAR の成果物の条件と GPU（判断 10 の細部）
- [x] `experiments/20261012-public-keystroke-matching/` の下書き（preregistration・config・SEED・README・data.md）

## 凍結の前の攻撃（やること 3）
- [x] `attack-me`（stage `prereg`）round 1（major）→ 判断 16〜23 → 下書き 2
- [x] round 2（minor・設計の判断 5 件）→ 判断 26〜31 → 下書き 3
- [x] round 3（major・局所・設計の判断 4 件）→ 判断 32〜36 → 下書き 4
- [x] round 4（minor・再査読は要らない）→ 判断 37〜40 → 下書き 5
- [x] 合成の記録の検査（凍結の前・`scripts/synthetic_logs.py`・R7 の道が切れる割合・align.py の包み）→ 判断 41〜43 → 下書き 6（`notes.md`）
- [ ] 研究者に凍結を問う（判断 42 の 5 つの分け方の確認を含む）
- [ ] 倫理の節の「同意は目的と手順を示したとだけ」を KLiCKe の一次と照らす
- [ ] PoPETs のオンライン発表・録画の要否（研究者が問い合わせる）

## 完了処理
- [ ] 引き継ぎ（次のセッション: 凍結・取得の開始条件の確認・合成の記録の検査のコード）
- [ ] `/cross-review` 2 巡
- [ ] commit → push → PR → CI → merge → main の CI
