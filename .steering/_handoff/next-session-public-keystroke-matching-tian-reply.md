# 次のセッション（Mac）: 照合の論文 —— Dr. Tian の返事を受けて原稿と知らせを直す

作成 2026-11-12（判断 90 の後）。下書き 4 の簡易版を研究者が 2026-11-12 に送った（前のスレッドへの返信・宛先は Dr. Tian だけ・添付はプレプリントの版の PDF、SHA-256 `94d42f05…dc9a`）。分析 6・7 の段は別の引き継ぎ（`next-session-public-keystroke-matching-manuscript-exploratory-6-7.md`）。

## 新しいセッションで最初に打ち込む文

返事が来たとき（返事の本文を貼る）:
```
.steering/_handoff/next-session-public-keystroke-matching-tian-reply.md を読んで、Dr. Tian の返事を原稿に反映して。返事は次のとおり: （ここに貼る）
```

返事が無いまま 11/19 ごろになったとき:
```
.steering/_handoff/next-session-public-keystroke-matching-tian-reply.md を読んで、返事が無いので The Learning Agency Lab への知らせ（下書き 5）を仕上げて。
```

## 送ったもので尋ねたこと（`.steering/20261012-public-keystroke-matching-prereg/reply-drafts-20261013.md` の「4 の簡易版」）

1. コンペのデータが KLiCKe から取られたこと（§3.3・序論・倫理の節）と、IRB の承認と同意の範囲（倫理の節）を、Dr. Tian からの personal communication として載せてよいか。言い方は正確か。コンペの作文が公開のコーパスに全部入っているか一部か。
2. The Learning Agency Lab に、草稿を渡さずに投稿の前に知らせるのがよいか。
3. 時間があれば、作文研究の立場から草稿の中身への意見と議論を歓迎する（判断 84 の入口・共著には触れていない）。

約束したこと: 補足の解析（分析 6・7）が入ったら新しい版を送る。投稿は 11 月末（PoPETs）。草稿は手元にとどめてほしいと頼んだ。

## 返事が来たら（答えごとに）

返事の本文は研究者が貼る。`.steering/20261012-public-keystroke-matching-prereg/decisions.md` に判断（次の番号）として要旨を書く。返事の本文を Codex など外部の LLM に送らない（原稿の diff は送ってよい・判断 83）。

- **載せてよい（問い 1）**: `sections/ethics.tex` 20 行目の角括弧（「[After they have read the draft: whether they agreed ...]」）を、読んで了承したことの 1 文に替える。言い方の直しがあれば `threat-model.tex` 99 行目付近（§3.3）・序論・`ethics.tex` 10 行目付近・`data.tex` 21 行目に入れる。全部か一部かが分かれば「not specified」の文を直す（`grep -n "specified" sections/*.tex` で探す）。
- **載せないでほしい・別の書き方で**: 序論・§3.3・倫理の節の主張に響く（コンペの本文が今は公になっているという条件つきの帰結の根拠が無くなる）。書く前に、直す範囲を推奨と理由を添えて AskUserQuestion で研究者に聞く。
- **知らせについての助言（問い 2）**: 勧められたら下書き 5 を仕上げる（下記）。Crossley 経由を勧められたらそれに合わせ、下書き 5 は送らない（判断 73）。知らせない方がよいと言われたら、知らせるかを研究者に聞く（倫理の節の 33 行目の角括弧と判断 68 に響く）。
- **中身に踏み込んだ意見（問い 3）**: 判断 84 のとおり、共著の提案の下書きを書く（送るのは研究者）。役割の候補: 過程の指標の式を作文研究の定義（Inputlog など）と照らす・§8 の作文研究への意味づけ・KLiCKe の記述の確認。全文を承認してもらう期限は 11/30 の数日前。共著になったら直すものの一覧は判断 84（利害の表明・出どころの文を personal communication から著者の知識へ・AI の利用の節への同意・貢献の記述・OSF の登録の著者）。間に合わなければ Issue 4（2027-02-28）。発表を誘いの理由にしない（判断 84）。
- **短いお礼だけ**: 原稿は変えない。問い 1 の答えが無ければ、角括弧を残したまま、投稿の前に一言だけ確かめる短い返信を研究者に勧める。

## 返事が無いとき（11/19 ごろ・判断 73）

- 下書き 5（The Learning Agency Lab への知らせ）を研究者が送る。`[ ]` を埋める: 主な結果の 1〜2 文（集計だけ・抄録の値）、投稿の時期（11 月末）、応答の期限。
- 判断 68 の 4 の猶予（約 2 週）は、11/19 に送ると 11/30 まで 11 日になる。期限の書き方（例: 11/27）を研究者に AskUserQuestion で聞く。
- 宛先の連絡先は**まだ確かめていない**（下書き 5 の注）。公式サイトの連絡先を研究者が一次で確かめる。
- 送った日付と応答を `ethics.tex` 33 行目の角括弧に入れる。

## 直したら

- 投稿版 `bash build.sh <テンプレート> <出力先>` とプレプリントの版 `bash build-preprint.sh <出力先> /Users/johnd/paper-authors/keystroke-log-release-matching-preprint.tex` の両方をビルドする（BUILD.md・テンプレートは submission-template-2027.zip、SHA-256 `b1abbcc0…`）。エラー 0・未定義 0。本文の頁（Ethical Considerations が p12 右段）を測る。
- 文体の門: repo の根から `python3 .steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py --root . papers/keystroke-log-release-matching`。
- `/cross-review`（原稿の diff だけ）。commit・push だけ（PR は出さない）。

## 守ること

- worktree `/Users/johnd/GSE-wt-matching-manuscript`（枝 `docs/public-keystroke-matching-manuscript`）。始める前に `git fetch` と `git merge --ff-only origin/docs/public-keystroke-matching-manuscript`。コミット前に `git branch --show-current`。`git add -A` を使わない。
- 公開する原稿に内部の番号・GSE・著者名を書かない（著者名は repo の外のファイルだけ）。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
