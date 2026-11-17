# 次のセッション（Mac）: 照合の論文 —— PoPETs から返事が来たとき

作成 2026-11-18（判断 98 の後）。worktree `/Users/johnd/GSE-wt-matching-manuscript`・枝 `docs/public-keystroke-matching-manuscript`。G-GEAR の作業は無い。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-review-response.md を読んで、PoPETs の返事に対応して。
```

返事のメール（または HotCRP の画面）の本文を会話に貼る。査読の文は外部 LLM に送ってよいかを最初に研究者に確かめる（打鍵の記録・本文ではないが、二重盲検の査読の文である）。

## 今の状態

- PoPETs 2027 Issue 3 の HotCRP に #55 として提出済み（2026-11-18）。https://submit.petsymposium.org/2027.3/paper/55
- 提出した PDF は `keystroke-log-release-matching-submission-20261117.pdf`（SHA-256 `26c50fc44caf…`・31 頁・本文 12 頁）。経緯は `.steering/20261012-public-keystroke-matching-prereg/decisions.md` の判断 98。
- 匿名の複製: https://anonymous.4open.science/r/keystroke-log-release-matching-3E48 （期限 2027-04-17。採否が 2 月なので、改訂が 4 月を越えるなら延ばすか作り直す）。
- 出席はしない（判断 81 付近: chairs の返事で、出席しなくても掲載され、遠隔の発表は録画も含めて無い）。
- プレプリントは採否まで出さない（判断 95）。
- Dr. Tian には提出済みの版を送り、採否まで草稿を伏せるよう頼んだ（下書き 8。送ったかは研究者に確かめる）。

## 日程（CFP https://petsymposium.org/cfp27.php を 2026-11-18 に取り直した。締切は AoE）

| 何 | いつ |
|---|---|
| 反論（rebuttal）の期間 | 2027-01-12〜01-18。査読ごとに 250 語まで |
| 採否の通知 | 2027-02-01 |
| 改訂（revise）の締切 | 2027-03-01（通知から 1 か月以内に認められれば Issue 3、4 か月以内なら次の号） |
| camera-ready | 2027-03-15 |
| 却下されたときの再投稿 | 1 号空ける。Issue 3（2027）の却下は 2028 の Issue 1 から |

最初の返事は 1 月 12 日ごろの査読の公開（反論の期間の始まり）。desk reject ならもっと早い。

## 返事の種類ごとにやること（順と範囲は最初に研究者に AskUserQuestion で確かめる）

### A. 査読が公開された（反論の期間・1/12〜1/18）

1. 査読を指摘ごとに表にする（誤読・追加の解析の要求・主張の範囲・倫理・再現性）。各指摘を原稿・事前登録・集計の JSON で一次で裏取りし、誤読と正当な指摘を分ける。
2. 反論は査読ごとに 250 語。誤読の訂正と、改訂で何をするかの約束に絞る。新しい解析の結果は書かない（期間内に回すなら研究者に聞く）。
3. 反論の文は Codex にも読ませてよいか研究者に確かめてから /cross-review の形で見せる。
4. HotCRP への貼り付けは私がしてよいが、送るボタンは研究者が押す（提出と同じ扱い）。

### B. 採録（accept）

1. camera-ready の版を作る（著者名入り・`build.sh` の第 3 引数で著者のファイル）。著作権の書式（`\setcopyright{popets}` など）は採録の案内に合わせる。
2. 出席できないことを chairs に伝える（下書きは Claude・送るのは研究者・判断 81 付近の約束）。
3. プレプリントの版の切り替え（判断 95）: OSF の登録を公開し、repo（Zenodo）を公開し、原稿のリンクを匿名の複製から実の repo に替え、個人的な連絡の日付を見直す。公開物の作法は memory「公開アーカイブは GitHub＋図と gif と日本語版の README を既定に」「公開物に投稿先や状態を書かない」。
4. Dr. Tian と The Learning Agency Lab（下書き 5）に知らせる。

### C. 改訂（major revision・revise）

1. 改訂の条件（revision criteria）を表にし、各条件に対する直しの案を研究者に AskUserQuestion で確かめる。
2. revision editor に改訂の予定を出す（CFP: 担当者と合意できる予定を提案する）。3/1 までに認められれば Issue 3。
3. 直しは足すより移す・削る（本文 12 頁）。直した後に attack-me（Codex を含む）と /cross-review。
4. 匿名の複製の期限（2027-04-17）に気をつける。

### D. 却下（reject）

1. 査読の要点を表にし、直すかどうかを研究者と決める。
2. 次の投稿先を目的から選ぶ（memory「投稿先は目的から選ぶ」「無料で済ませる」）。PoPETs に戻るなら 2028 Issue 1 以降。
3. プレプリントを出すかを研究者に確かめる（判断 95 の「採否まで待つ」が解ける）。

## 守ること

- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。それらを外部 LLM（Codex を含む）に送らない。原稿の diff は Codex に送ってよい（判断 83）。
- 本文 12 頁を超えない。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める（PR は研究者に確かめる）。
- HotCRP の送信・提出のボタンは研究者が押す。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
