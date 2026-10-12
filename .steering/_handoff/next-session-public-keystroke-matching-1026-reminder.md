# 次のセッション（2026-10-26 ごろ）: KLiCKe の著者への催促と、投稿までの日程の確認

作成 2026-10-12（判断 51 の後）。公開データでの照合の論文（PoPETs 2027 Issue 3・締切 2026-11-30 AoE）。
並行して、凍結から本計算までは別の引き継ぎ `next-session-public-keystroke-matching-research-forward.md` で進んでいる。このメモは催促と日程の確認だけを扱う。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-1026-reminder.md を読んで、KLiCKe の著者への催促と、投稿までの日程の確認をして。
```

## 今の状態（2026-10-12 時点）

- KLiCKe の著者（Yu Tian）への問い合わせは **2026-10-12 に研究者が送った**（判断 50）。文面は `.steering/20261012-public-keystroke-matching-judgement/author-inquiry-draft.md`（問いは 3 つ: 利用条件・同意と倫理審査・この解析への懸念）。
- 判断 51: 返事は待たずに凍結と取得に進む。返事が無ければ **10/26 に催促を 1 回**送る。返事が来たら内容を倫理の節に書き、利用に懸念が示されたら計算を止め、取得したデータを消し、経緯を報告する。
- 研究者の決定の記録: `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜51）。

## やること

1. **返事が来たかを研究者に尋ねる**（Claude はメールを読まない。返事の本文は repo に入れず、日付と要旨だけを `decisions.md` に追記する）。
   - 来ていれば: 要旨を研究者から聞いて記録する。3 つの問いへの答えを、事前登録の倫理の節（日英の両方。凍結後なら `notes.md` の「逸脱」ではなく論文の倫理の節の材料として）にどう書くかを案にする。懸念が示されていれば、計算を止める手順（取得したデータの削除・その記録・投稿の見送りかどうか）を研究者に問う。
   - 来ていなければ: 下の催促の下書きを研究者に渡し、研究者が自分のメールで送る（元のメールへの返信の形がよい）。送った日を `decisions.md` に記録する。
2. **PoPETs の録画の要否の問い合わせ**（研究者が PC chairs に送る・判断 2 と事前登録の未決）を送ったか、返事が来たかを尋ねる。録画やオンライン発表が必須なら、研究者の条件（登壇なし）と合わないので、投稿先を考え直す（候補は下）。
3. **日程の確認**: research-forward の引き継ぎの進み具合（凍結・取得・検査 1〜7・本計算）を `tasklist.md` と git の履歴で確かめ、11/9 までに本計算が終わる見込みかを研究者に伝える。遅れていれば、Issue 4（2027-02-28）に回すかを研究者に問う（推奨と理由を添える）。

## 催促の下書き（英語・研究者が名前を入れる）

**Subject**: Re: Question about the terms of use of the KLiCKe corpus for a secondary analysis

Dear Dr. Tian,

I am writing to follow up on my message of 12 October about a secondary analysis of the KLiCKe corpus. I understand that you are busy, and I would be grateful for any reply when you have time, even a short one.

To keep to my schedule, I have started the analysis under the terms stated on the Inputlog community page (that the files "can be downloaded and used freely" with the repository referenced as the source). I use only the keystroke logs and the essays, report only aggregate results, do not use the demographic file and do not redistribute the data. If you have any concern about this use, please let me know and I will stop the analysis and delete the data.

My remaining questions are whether the consent form mentioned public sharing and secondary use, and whether an ethics board reviewed the data collection, so that I can describe both accurately in the ethics section of the paper.

Thank you again for making the corpus available.

Kind regards,
[name]

（注: 2 段落目は、凍結と取得が済んでいる場合の文。まだ取得していなければ「I plan to start the analysis ...」に直す。送る前に研究者が文面を確かめる。）

## PoPETs が難しくなった場合の代わりの投稿先（未確認の候補）

事前登録は OSF に置き、投稿先から独立している。下の候補は、費用・発表・倫理の要件を一次でまだ確かめていない（確かめるのは投稿先を変えると決めてから）。研究者の条件は、登壇なし・費用ゼロ（`memory` の venue の条件。PoPETs の diamond OA は判断 2 で例外として受け入れた）。

- プライバシーとセキュリティの誌: ACM TOPS・Computers & Security・IEEE TIFS など（費用の形は要確認）。
- 教育データと作文研究の誌: Journal of Educational Data Mining（`@` のマスクの論文 [V243] の掲載誌）・Journal of Writing Research（KLiCKe [V264] の掲載誌）。公開する側への手引きとして書く形になる。

## 守ること

- 応答は日本語（AskUserQuestion の問い・選択肢も日本語）。★・⚠️ を多用しない。推奨と理由を添える。
- 返事の本文・メールアドレス以外の個人の情報を repo に入れない。Claude はメールを読まず、送らない（送るのは研究者）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- `.steering` だけの変更は push だけ（PR は要らない）。`git add -A` や `git add <dir>` を使わない。並行セッションがあるので worktree で作業する。
