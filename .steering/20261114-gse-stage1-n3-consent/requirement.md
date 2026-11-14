# 段 1 の 3 名の同意文書とフォーム

## 背景

ADR-052（Accepted・2026-11-14）は、段 1 の確認を採択前の本人以外の 3 名で行うと決めた。3 名の同意に入れるものは D6（参加・問い・手跡の後期・匿名の個人ごとの集計値と図の公表。記録の公開は求めない）、同意の型は O1 のもの（ADR-014 D7）を使い回す。ADR-031・ADR-032 は、3 名の同意文書を研究者が承認したときに Accepted にする（ADR-052 D7・ADR-043 D8）。ADR-032 の計器を入れるかと、どけた回数を記録するかは、同意の文と同時に決める（ADR-043 D9・ADR-051 D2）。

段 1 の配布の門（`scripts/check-s1-release-readiness.sh --audience participants --consent <md>`）は、同意文書の md に行頭の承認の印 `<!-- s1-esm-consent: approved -->` が 1 回だけあることを求める。今その文書は無い。

入口: `.steering/_handoff/next-session-gse-stage1-after-adr-052.md` の 2。

## ゴール

3 名に渡せる段 1 の同意文書（md の雛形と、正本の Google フォームの段 1 版）を書き、研究者の承認を受ける。承認で ADR-031・ADR-032 を Accepted にする。

## スコープ

### 含むもの
- 段 1 の同意文書の md（O1 の雛形 `consent-draft-o1.md` の型・承認の印の置き場所）
- `Form_O1/GSE_O1_Form_Builder.gs` に段 1 の同意フォームを足す（同意項目を md と 1 対 1 に照合するテストつき）
- `docs/participant-setup-guide.md` の段 1 の節（被験者向けの契約）
- ADR-031・ADR-032 の状態の更新（承認の後）と、ADR の README・設計の地図の関係する行
- 決めたことの decisions.md への記録

### 含まないもの
- 3 名向けの組み立て（`make-common-app-zip.sh --audience participants`）・配布フォルダの README・リリースタグ（手跡の PR 6 と Windows 版の後の別タスク）
- ADR-032 の計器の実装（判断 2 で入れないと決めた）
- どけた回数の実装（手跡の PR 6）
- 事前登録の値（引き継ぎの 1）
- フォームの配備（研究者が Apps Script で行う。Chrome での確かめは研究者に確かめてから）

## 受け入れ条件

- [ ] 同意文書の md が、ADR-052 D6 の 4 つ（参加・問い・手跡の後期・公表）と、ADR-031 D5 保証 3（会話を選ぶと残る・送った後は端末で消えない・答えなくてよい）、ADR-051 D2（手跡を切れる・切った／戻した時刻とどけた回数を記録する）を書いている
- [ ] 文面の頻度・選択肢・問いの数がアプリの実装（`ProbeConfig`・`ACTIVITY_CHOICES`・`S1ProbeCard`・`DayQuestionCard`）と一致する（ADR-031 D8 の 2026-09-14 追記）
- [ ] フォームの段 1 の同意項目が md と 1 対 1 で、`node Form_O1/o1_form_builder_test.cjs` と変異のテストが緑
- [ ] `check-s1-release-readiness.sh --selftest` が緑のまま、承認後の md を `--consent` に渡すと [3] が緑
- [ ] /cross-review（Codex を含む）の指摘を処理した
- [ ] 研究者が文面を承認した（承認の印は研究者の承認の後に入れる）

## 関連ドキュメント

- ADR-052 D6・D7、ADR-043 D7〜D9、ADR-051 D2、ADR-031 D3・D5・D8、ADR-014 D7・D8
- `.steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md`（O1 の雛形・注 D の問いの案）
- `Form_O1/GSE_O1_Form_Builder.gs`（O1 の同意の正本）
- `scripts/check-s1-release-readiness.sh` [3]
- `.steering/_handoff/next-session-esm-consent-next-study.md`（別の worktree にある。§2 の 1〜6）

## 運用メモ
- /reimagine 適用: No
- 理由: 被験者向け文書とフォームの追加で、形は O1 の型（ADR-014 D7）と ADR-052 D6 が決めている。判断が要るのは文面の中身で、研究者に 1 問ずつ聞く。
