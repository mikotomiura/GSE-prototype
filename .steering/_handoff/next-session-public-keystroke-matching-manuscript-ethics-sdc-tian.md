# 次のセッション（Mac）: 照合の論文 —— 倫理審査の手段・統計的開示制御の文献・Dr. Tian への草稿

作成 2026-10-29（判断 86 の後）。この機械は Mac。G-GEAR の作業（探索的な分析 6・7、全員の付録）はこのセッションでしない。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-ethics-sdc-tian.md を読んで、照合の論文の残り 3 つ（倫理審査の手段・統計的開示制御の文献・Dr. Tian への草稿）を検討して。
```

## 始める前に

- worktree は `/Users/johnd/GSE-wt-matching-manuscript`（枝 `docs/public-keystroke-matching-manuscript`）。`git fetch` と `git merge --ff-only origin/docs/public-keystroke-matching-manuscript`。G-GEAR が分析 6・7 の結果を merge していれば、それも入る（このセッションでは原稿に入れない。入れる段は別）。
- 読む物: 判断 71・72〜75・83〜86（`.steering/20261012-public-keystroke-matching-prereg/decisions.md`）、attack-me round 3 の `verdict.md`（`.steering/20261020-public-keystroke-matching-manuscript/attack-me/manuscript-matching/round-3/`）、`reply-drafts-20261013.md`（下書き 4・5）。

## 1. 倫理審査を頼む他の手段（attack-me round 3・R3 の minor）

- 指摘: ethics.tex の「No institutional ethics committee was available to the authors, and no external committee or board reviewed the study.」について、所属先の無い研究でも独立の審査サービスに頼むことや、コーパス側の IRB に問い合わせることができる。それらを検討したかが書かれていない（Kohno ら: 倫理を「やるかどうか」の判断に置くこと）。
- ぶつかる判断: 判断 71 で研究者は、外部の審査を受けなかった理由を「書かない」と選んだ（推奨は「費用のみ」だった）。
- このセッションで研究者に問う（AskUserQuestion・推奨と理由つき）。選択肢の案: (a) 判断 71 のまま書かない（査読で問われる点として残る）、(b) 検討した事実だけを書く（実際に検討したことだけ。検討していないなら書けない）、(c) 理由を 1 文（費用など・判断 71 の「費用のみ」の案）。⚠️ 事実を研究者に確かめてから書く（検討したか・何を検討したかを推測で書かない）。
- PoPETs の規程（round 1 で照合）: 「This section should include a justification of the ethics of the work and information about whether the work was submitted to an external ethics panel such as an IRB or the Tor Research Safety Board.」。審査を受けていないことは既に書いてある。

## 2. 統計的開示制御（SDC）の文献（attack-me round 1 から未解消・round 3 の R2 の minor）

- 指摘: 管理する側は、丸め（global recoding）・抑制（suppression）・集計だけを出す（aggregation）・申請者にだけ渡す（tiered access）という語彙で選ぶ。R3-t・R4・R7・§8.2 をこの語彙に対応させれば、§8 の持ち帰りが実務の道具箱につながる。標準の文献を 1 本引き、表 2 か §8.3 で各形を技法に 1 文で対応させる。読める総説か公的なガイドで足りる。
- やること: 無料で全文が読める標準の文献を選ぶ。**文献の調査はサブエージェントか `/literature-review` で行う**（メインが検索を叩かない・memory の指示）。依頼文には「著者のページ・リポジトリ・OA を探す順」と「curl で取れない URL は Chrome」を最初から書く。
- 候補（未確認・確かめてから使う）: Eurostat などの SDC のハンドブック（公的な無料の PDF があるか）、sdcMicro の論文（Journal of Statistical Software・OA か）。題・著者・年・DOI・OA を OpenAlex で確かめる。
- 引用は `citation-ssot`（docs/references.md に append-only で登録・references.bib）。足す文は本文の余白（p12 で約 0.3〜0.4 頁）の中で、足す前に頁を測る。用語の対応が正しいか（R3-t は丸め＝global recoding、R7 は local suppression に当たるか・R4 は何か）を文献の定義で確かめてから書く。

## 3. Dr. Tian への草稿（判断 73・84）

- 決めること（研究者に AskUserQuestion）:
  - 送る版: (a) 今の版（attack-me round 3 と /cross-review の直しの後・`f0da031d` 以降）で送る、(b) 探索的な分析 6・7 の結果を入れてから送る。考える点: 11/30 の締切、判断 84（議論の後に役割を添えて共著を提案する）で承認の期間が要ること、6・7 は粗い形の記述を変えうること、Dr. Tian に見てほしいのは主に出どころの文と方法・指標であること。
  - 下書き 4（`reply-drafts-20261013.md`）の直し: 草稿の版と、確かめてほしい箇所（コンペのデータの出どころを書いた文の位置: 序論・§3.3・倫理の節。倫理の節の「公表への同意」の角括弧）、Crossley に見せてよいか・The Learning Agency Lab へ知らせるべきか（判断 73）。共著の提案はこのメールに入れない（判断 84）。送るのは研究者。
  - 草稿の形式: PDF（ビルドした版）。二重盲検の投稿版とは別に、著者名入りで送るか。
- 下書きは英語、地の文の説明は日本語。

## 4. 終わったら

- 判断（87 から）を `../20261012-public-keystroke-matching-prereg/decisions.md` に書く。原稿を直したらビルド・頁・文体の門・数値の照合・/cross-review（研究者は原稿の diff を Codex に送ってよいと認めている・判断 83）。commit・push だけ（PR は出さない）。
- 別に残っている段: 探索的な分析 6・7 を原稿に入れる段（G-GEAR の結果の後）、全員の付録（`next-session-public-keystroke-matching-manuscript-stage-3.md`・11 月中旬）、匿名リンク、公開元への知らせの日付（研究者が送った後）。

## 守ること

- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。それらを外部 LLM に送らない。
- 引用は citation-ssot。公開する原稿に内部の番号・GSE を書かない。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion（日本語）で聞く。絵文字・★・⚠️ を多用しない。
