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
- [x] 研究者に凍結を問う → 英語の版と OSF の文面まで用意し、凍結は KLiCKe の返事の後（判断 49）
- [x] 英語の版 `preregistration.en.md`・OSF の各欄の文面 `osf-registration-fields.md`
- [x] 書誌番号の無かった引用を登録（[V280] Wagner & Eckhoff・[V281] Menlo Report（provisional）・[V282] Kerckhoffs（provisional））・PoPETs の注に [V271]
- [ ] 凍結（判断 51 で KLiCKe の返事を待たないことにした・論文用のリポジトリ・OSF・状態の行）→ `next-session-public-keystroke-matching-research-forward.md`
- [x] 送った日（10/12）と目標（11 月末）を記録（判断 50）・日程と進め方（判断 51）・引き継ぎ 2 つ（10/26 の催促・research-forward）
- [x] 倫理の節の「同意は目的と手順を示したとだけ」を KLiCKe の一次と照らす（[V264] §2.1 にだけ当てはまり [V274] には同意の記載が無い → 2 つに分けて書いた）
- [ ] PoPETs のオンライン発表・録画の要否（CFP: 対面は不要・費用なし。録画の要否は CFP に無い → 研究者が PC chairs に問い合わせる）

## 完了処理
- [ ] 引き継ぎ（次のセッション: 凍結・取得の開始条件の確認・合成の記録の検査のコード）
- [x] `/cross-review` 1 巡目（合成の記録の検査・Codex 4 件・code-reviewer 12 件）→ 判断 44〜47 → 下書き 7
- [x] `/cross-review` 2 巡目（自分が足した規則の境界条件・Codex 4 件・code-reviewer 12 件）→ 判断 48・判断 42 の確認 → 下書き 8
- [ ] commit → push → PR → CI → merge → main の CI
