# タスクリスト

## 準備
- [x] ADR-052・043・051・031・032・014 と O1 の同意の雛形・フォームを読む
- [x] 範囲と中身の判断を研究者に聞く（判断 1〜13）

## 文面
- [x] 草稿 `consent-draft-s1.md`（b7d68371）
- [ ] 研究者が草稿を読み、直しを入れる ← 今ここ
- [ ] `docs/participant-setup-guide.md` に段 1 の節

## フォーム
- [ ] `Form_O1/GSE_O1_Form_Builder.gs` に段 1 の同意フォーム（`FORM_ID_S1_CONSENT`・同意項目・受付メール）
- [ ] `o1_form_builder_test.cjs` に md との 1 対 1 の照合、変異のテスト
- [ ] `node Form_O1/o1_form_builder_test.cjs` と変異のテストが緑
- [ ] `bash scripts/check-s1-release-readiness.sh --selftest` が緑

## レビュー（場面ごとの道具）
- [ ] 文面: attack-me か /cross-review（Codex を含む・記録の本文と集計は送らない）
- [ ] フォームのコード: code-reviewer ＋ security-checker ＋ /cross-review

## 承認の後
- [ ] 承認の印を md の行頭に 1 回
- [ ] ADR-031・ADR-032 を Accepted（ADR-032 は段 1 の系統に計器を入れないと状態の行に・判断 11）、README を更新
- [ ] `docs/o1-deletion-ledger.md` に段 1 の同意の正本と取り消し（判断 8）の行

## 引き継ぎ（他のタスクへ渡す）
- [ ] 手跡の PR: 消した時間帯の累計を後の行から引く（判断 13）・どけた回数（判断 3）・一時停止中の表示（配る前の条件 12）
- [ ] 3 名向けの配布のタスク: `S1ConsentPanel.tsx` の取り消しの文（判断 8）・トレイの場所の書き方（条件 10）・終了後の説明（判断 6）
- [ ] 事前登録のタスク: 最長の期間は 8 週間以内（判断 9）・取り消しはやめた扱い（判断 8）・頻度を変えたら同意を直す（条件 9）

## 完了処理
- [ ] design.md の最終化
- [ ] /finish-task
