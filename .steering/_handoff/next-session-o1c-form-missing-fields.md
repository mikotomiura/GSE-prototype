# 引き継ぎ: O1-C（説明・同意＝参加登録）のフォームに、お名前・メールアドレス・パソコンの種類が無い

> 済み（2026-10-08）。PR #327（`fix/o1c-form-missing-fields`）・記録は `.steering/20261008-o1c-form-missing-fields/`。
> - 3 設問を戻し、照合（`checkO1ConsentFormShape`）と修復（`repairO1ConsentRegistrationItems`）を足した。下の §2 の見立て（setupO1Forms の誤実行）は外れ（decisions.md D1）。
> - 同意の改訂（識別子の行・結果の公表と記録の公開の節と項目）も入れ、確認用の回答を消して作り直した（D8）。§4 の 1 つ目はこれで済み。
> - 「メールが届かない」は Google 側の配送の遅れ（15〜24 分）だった（D7）。
> - 残り: 参加者 ID とメールが食い違ったときに止めるか記録するか（研究者の判断待ち）／記号を減らすか（§4 の 2 つ目・判断待ち）。

作成 2026-10-08。新しいセッションは `/clear` の後、CLAUDE.md の行動規範（`/start-task` → docs を先に読む → Skill を参照）を踏んでから始める。
返答・文面では絵文字や記号（★・⚠️）を多用しない（研究者の指摘・memory `feedback-avoid-emoji-and-markers`）。

## 1. 分かっていること（2026-10-08 に実物で確認）

- 配備済みの O1-C フォーム（公開 URL は研究者が持っている）を Chrome で開き、設問を読み取った（回答は送っていない）。
- 実物は「同意の確認」のチェック 11 個 →「一部の方へのお願いについて」のお知らせ →「ご記名」の見出し →「参加者ID（お持ちの方のみ）」で終わる。
  - 文字の入力欄は 1 つ（参加者 ID）だけ、選択肢の欄は 0。
  - **お名前（必須）・メールアドレス（必須）・記録に使うパソコンの種類（必須）の 3 つが無い。**
- コード（`Form_O1/GSE_O1_Form_Builder.gs` の `buildO1ConsentForm`）は、参加者 ID の後に `Q_O1_NAME`・`Q_O1_EMAIL`（「@ を含む」の検査つき）・`Q_O1_OS`（Windows / Mac / 両方使う）を足し、最後に `o1RecordFormUrl_("O1_CONSENT", …)` を呼ぶ。
- 配備手順の記録では、2026-08-28〜29 に `setupO1Forms()` が「構築完了」で終わっている（`.steering/20260828-o1-gate-closeout-and-deployment/deployment-runbook.md:134`・`.steering/20260829-o1-builder-config-to-properties/decisions.md:141`）。
- 影響: 登録の処理（`onO1ConsentSubmit`）は、メールが空だと「no-email」で却下する（`GSE_O1_Form_Builder.gs` の `o1LogMgmt_("register", "", "blocked", "no-email", "")`）。参加者 ID の発番も受付メールも出ない。参加者には確認の文（「メールへお送りします」）だけが出る。
- **直すまで O1-C の URL を候補者に渡さない**と研究者に伝えた。

## 2. 見立て（未確認・断定しない）

- `setupO1Forms()` は回答 0 件のときだけ、フォームを空にして上から作り直す。途中で例外が出ると、今の形（参加者 ID で終わる）になる。
- 2026-10-07〜08 に研究者が `.gs` を Apps Script に貼り直した。Apps Script はページを読み込み直すと関数の選択が先頭（`setupO1Forms`）に戻るので、`refreshO1LinksTab` のつもりで `setupO1Forms` が走った可能性がある（`browser-verification` Skill §2.3b。G1 で 2026-08-07 に同じ形の事故）。
- 走ったとして、なぜ参加者 ID の直後で止まったかは分からない。候補は参加者 ID の欄の `setValidation`（`requireTextMatchesPattern("^[PpＰｐ]?[0-9０-９]*$")`）か、次の `addTextItem().setTitle(Q_O1_NAME)`。テストの偽環境はこれを捕まえない。

## 3. 次のセッションでやること

1. 研究者に、フォームビルダーの Apps Script の「実行数」で、今日の `setupO1Forms` の実行と最後のエラーの文を見てもらう（`browser-verification` §2.4。エディタのログには出ない場合がある）。
2. エラーの文から原因を確定し、`buildO1ConsentForm` を直す（`/fix-bug`・回帰のテストを先に書く・`o1_form_builder_test.cjs` と変異テストを緑に）。
3. 回答が 0 件であることを確かめてから、研究者が `setupO1Forms()` を実行して作り直す。実行の直前に関数の選択の表示を読み直す。
4. Chrome で実物を開き、3 つの設問が戻ったことを読み取りで確かめる（回答は送らない）。
5. 作り直すとフォームの URL は変わらないはずだが、確かめる。リンク集（`refreshO1LinksTab()`）も実行する。

## 4. 合わせて残っていること（このセッションから）

- 同意文書の今日の改訂（識別子の 1 行・結果の公表と記録の公開の一文）は、まだ `.gs` にも `consent-draft-o1.md` にも入っていない。案は `.steering/20261007-o1-install-id/consent-revision-proposal.md` と `.steering/20261007-research-use-and-release/o1-consent-today-proposal.md`。私の案で足した部分（集計値の公表の行・同意項目 1 つ）を入れるかは研究者の判断待ち。作り直す（上の 3）なら、改訂を先に `.gs` に入れてから作り直すと 1 回で済む（`migrateO1ConsentForm` だと新しい項目が末尾、メール欄の後ろに付く）。
- 記号を減らすかどうか（研究者の判断待ち）: 同意フォームの文面（中身は変えず ★・⚠️ を外す）、運営シートの「O1 リンク集」と「O1 終了判定」の文言。
- メインのチェックアウト（`/Users/johnd/GSE-prototype`・IME 論文のブランチ `docs/ime-m12-mac-conditions`）の `Form_O1/GSE_O1_Form_Builder.gs` と `Form_O1/GSE_O1_Ledger.gs` は、研究者が貼るために main の版で上書きしてある（「変更あり」と出る）。IME の作業のコミットに混ぜない。貼り終えたら `git checkout -- Form_O1/` で戻す。
- 作業用の worktree `/Users/johnd/GSE-prototype-research-use`（ブランチ `feature/o1-end-judgement`・マージ済み）は残っている。

## 5. このセッションでマージしたもの

- PR #322 ADR-039（研究利用と公開・Proposed）と同意・問い合わせの草案
- PR #323 運営ワークフローを repo の外の docx に（`~/Downloads/GSE_G1_O1_運営ワークフロー.docx`・生成スクリプトは `.steering/20261007-research-use-and-release/make_ops_docx.js`）
- PR #324 運営シートの「O1 リンク集」タブ（`refreshO1LinksTab()`）
- PR #325 受領台帳の「O1 終了判定」タブ（最初に記録した日から暦日 21 日）
- gse-dataset PR #2 schema の同期（`o1_install_id`）
