# arXiv の endorsement の依頼文の下書き（判断 3）

⚠️ 下書き。研究者が相手に合わせて直して送る。
- 送る前に: arXiv で新しい投稿を始め、カテゴリ **cs.SE** を選ぶと、endorsement の依頼メール（6 文字の endorsement code と、相手に渡すリンク入り）が届く（arXiv の help "Start a new submission and select the category you wish to submit to. Check your email for an endorsement request email."）。下の `[code]` と `[link]` をそれで埋める。
- 相手の条件: arXiv の cs の分野で、3 か月〜5 年前に出した論文が一定数あり、著者として登録されている人（help "we only count papers that have been submitted between three months and five years ago"）。相手が endorse できるかは、相手の論文の abstract ページの "Which authors of this paper are endorsers?" で確かめられる。
- ⚠️ arXiv の help: 個人的に知っていて分野に詳しい人に頼む・**大勢に一斉に送らない・同じ人に繰り返し送らない**。
- ★ endorsement は査読ではない（help "The endorsement process is not peer review."）。相手に求めるのは「cs.SE にふさわしい論文か」の確認だけ。
- ⚠️ **送る時点で再現一式が未公開なら**（Zenodo の公開と GitHub の public 化は投稿日・判断 4）、DOI はまだ解決しない（"The DOI will only be registered once the record is published."）。→ 再現一式の行を「投稿日に公開予定」と書き換え、原稿は PDF を添付する。⚠️ 添付する PDF の中の DOI と GitHub の URL も、その時点ではまだ開けない（GitHub は private）→ 本文で一言断る。投稿日の後に送るならそのままでよい。★ 送る前に `[...]` が残っていないことを確かめる。

---

## 日本語版

件名: arXiv（cs.SE）への投稿の endorsement のお願い

[お名前] 先生

[挨拶・自分との関係を一言]

突然のお願いで恐縮です。単著の論文を arXiv の cs.SE に投稿したいのですが、arXiv に論文を出すのが初めてで、既存の著者の方からの endorsement が必要になりました（2026 年 1 月から、所属機関のメールだけでは自動の endorsement にならなくなりました）。

論文は、公開されている 2 つの debugging の観察データの再解析で、「参照しなかった」を「自力で解決した」と読むと、未解決のまま終わった単位まで数えてしまうことを、その差の大きさとともに示したものです。*Empirical Software Engineering* に投稿済み（または投稿予定）です。

- 題: When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets
- 原稿: [PDF を添付 / 共有リンク]
- 再現一式: https://doi.org/10.5281/zenodo.23029603 [投稿日より前に送るなら: 「投稿日に公開予定」]

arXiv の案内によれば、endorsement は査読ではなく、分野にふさわしい論文かを見ていただくものとのことです。もし差し支えなければ、次のリンクから endorsement をお願いできますでしょうか。

[link]（endorsement code: [code]）

ご多忙のところ恐れ入ります。難しい場合はご放念ください。

[氏名]（Mikoto Miura）
mmiura.network@gmail.com

---

## English version

Subject: Request for arXiv endorsement (cs.SE)

Dear [name],

[One sentence on how you know each other.]

I would like to post a single-author paper to arXiv in cs.SE. As this is my first submission to arXiv, I need an endorsement from an established author; since January 2026 an institutional email address is no longer sufficient on its own.

The paper reanalyses two public observational datasets of professional debugging and shows how far the share of units without consultation overstates the share resolved without consultation when units can also end unresolved. It has been [will be] submitted to *Empirical Software Engineering*.

- Title: When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets
- Manuscript: [attached / link]
- Replication package: https://doi.org/10.5281/zenodo.23029603 [before the submission day: "to be released on the day of submission"]

arXiv notes that endorsement is not peer review but a check that the paper is appropriate for the subject area. If you are willing, you can endorse me at [link] (endorsement code: [code]).

Thank you for considering this request, and please feel free to decline.

Best regards,
Mikoto Miura
mmiura.network@gmail.com
