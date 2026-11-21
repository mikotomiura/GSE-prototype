# 原著者（Alaboudi & LaToza）への照会の下書き（S0・判断 5）

- 送るのは研究者（外に出る行為）。宛先のアドレスは研究者が公開の一次（論文の著者情報・所属のページ）で確かめる。私は調べていない。
- 送った日付をここと decisions.md に記録する。2 週間を待つ目安にする（判断 5）。
- 前提は一次で確かめた（2026-11-21・decisions.md 判断 12）:
  - journal 版の本文は NSF Public Access Repository の版で読んだ（`https://par.nsf.gov/servlets/purl/10490781`・34 頁・SHA-256 `38fe7001…`）。
  - arXiv v1 の本文は "Ten debugging episodes started because five developers … worked towards debugging reported defects" と "In the remaining 79 debugging episodes" と書いている。
  - journal 版の本文は件数を書き直していない。ただし "Half of the debugging episodes focused on committed defects and did not end with a successful fix" は 10 件中 5 件と合う。
- 数字は再現一式の `results/metrics.json`（タグ `submission-2026-09-29`）と同じ。⚠️ 送る前に、研究者が自分の言葉に直してよい（JSS の生成 AI の規程とは別だが、本人の手紙なので）。

---

**Subject:** Question about the consultation figures in "What constitutes debugging?" (EMSE 28:117)

Dear Dr. Alaboudi and Dr. LaToza,

I am an independent researcher reanalysing the debugging-episode data that you shared with your study "What constitutes debugging? An exploratory study of debugging episodes" (Empirical Software Engineering 28:117, 2023) and its preprint (arXiv:2105.02162). Thank you for making the coding available; it made the reanalysis possible.

While comparing the published figures with the shared coding, I could not reproduce some of the consultation figures of the journal version, and I would be grateful if you could help me understand how they were computed. My reanalysis and its code are public (https://doi.org/10.5281/zenodo.23029603).

1. **Definition of consultation.** The journal version reports that consulting resources occurred in 33% of debugging episodes, in all committed and 15% of fresh episodes, in 74% of the longest quarter of episodes, and that 91% of developers consulted resources at least once. Using `rowData.json`, I tried four definitions (the "Seeking information" activity alone; adding the unclassified codes; adding issue-tracker activities; adding both). No single definition reproduces these figures together: "all committed episodes" requires counting issue-tracker activities, while "15% of fresh episodes" and "91% of developers" are reproduced only without them. Which codes did you count as consulting resources for these figures?

2. **Episode counts.** The preprint states that 10 episodes concerned reported (committed) defects and 79 inserted (fresh) defects, and the journal version's statement that half of the committed episodes did not end with a fix agrees with 10 committed episodes. With 10 committed and 79 fresh episodes, consultation in all committed and 15% of fresh episodes gives about 22 of 89 episodes (about 25%), not 33%. Were the episode counts, or the assignment of episodes to committed and fresh, different in the journal version?

3. **Revised coding.** The journal version reports 2,135 activities, and the preprint 2,137 (the shared coding gives 2,136 by my extraction). The two replication packages on figshare contain the same `rowData.json` (byte-identical). Was the coding revised for the journal version, and if so, is the revised coding available?

4. **Episodes the developer continued later.** For episodes that end because the developer decides to continue another time (code DF3), do you know whether the defect was later resolved, for example in a later session in the dataset?

I would like to describe your answer accurately in a manuscript that I plan to submit, and I will of course check any description with you if you wish. If it is easier, a short answer to any one of these questions would already help.

Thank you very much for your time.

Kind regards,
Mikoto Miura
