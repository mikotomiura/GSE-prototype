# 次のセッション（Mac）: 照合の論文 —— 投稿（PoPETs 2027 Issue 3・締切 2026-12-01 06:59:59 EST ＝ JST 12-01 20:59）

作成 2026-11-18（判断 97 の後）。worktree `/Users/johnd/GSE-wt-matching-manuscript`・枝 `docs/public-keystroke-matching-manuscript`（最新 `064afe5a` の後の引き継ぎのコミット・push 済み）。G-GEAR の作業は無い。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-submit.md を読んで、照合の論文の投稿を進めて。
```

## 今の状態

- 原稿は完成（角括弧 0）。投稿版 エラー 0・overfull 2・31 頁・倫理は p12。プレプリントの版 エラー 0・35 頁。
- 匿名の複製: https://anonymous.4open.science/r/keystroke-log-release-matching-3E48 （論文用 repo `5ea8f12`・伏せる語は判断 97）。期限 2027-04-17（無料の上限）。repo を更新したらダッシュボードで「Force update」。
- 論文用 repo（private）は `5ea8f12`。公開物の中身と照合は判断 97。
- `build.sh` はビルドの後に PDF の手元のパスを調べ、あれば止まる（判断 97 の追記 2）。
- 研究者に渡したもの（`~/Downloads`）:
  - `keystroke-log-release-matching-submission-20261117.pdf`（投稿版・SHA-256 `26c50fc44caf…`）
  - `keystroke-log-release-matching-abstract-20261117.txt`（metadata の抄録・LaTeX なし・337 語）
  - `keystroke-log-release-matching-draft-20261117.pdf`（Dr. Tian に添えるプレプリントの版・`12e42f7e4763…`）
- Dr. Tian への下書き 8（`.steering/20261012-public-keystroke-matching-prereg/reply-drafts-20261013.md`）は最新の版に合わせた。送るのは研究者。

## やること（順と範囲は最初に研究者に AskUserQuestion で確かめる）

1. 研究者が投稿版の PDF を読んだ結果を聞く（memory「投稿の Submit の前に校正刷りを見てもらう」）。直しがあれば直してビルドし直す（`build.sh` の検査が緑・12 頁・文体の門）。
2. Dr. Tian へ下書き 8 とプレプリントの版を送ったかを聞く（送るのは研究者）。返事で直しが出たら反映する。
3. 投稿: 研究者が submit.petsymposium.org/2027.3/ でサインインして登録し、PDF を上げる。サイトは HotCRP。metadata の題・抄録・キーワード（`main.tex` の `\keywords`）・トピック・利益相反の欄を研究者と埋める。押すのは研究者。投稿と同時の公開はしない（判断 95）。HotCRP が PDF を処理した後の表示（頁数・フォント）を研究者に見てもらう。
4. 投稿の後: 投稿番号と日時を decisions.md に書き、memory に投稿済みの記録を足す。プレプリントの版の切り替え（OSF と repo のリンク・個人的な連絡の日付）は採否の後（判断 95）。

## 守ること

- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。それらを外部 LLM（Codex を含む）に送らない。原稿の diff は Codex に送ってよい（判断 83）。
- 本文 12 頁を超えない。足すより移す・削る。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める（PR は研究者に確かめる）。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
