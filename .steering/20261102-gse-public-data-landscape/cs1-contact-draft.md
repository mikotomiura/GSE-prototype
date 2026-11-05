# CS1 打鍵データの利用の連絡（文案・送るのは研究者）

- 宛先: john.edwards@usu.edu（Dataverse の termsOfAccess の指定・2026-11-02 に API で確認）
- 頼む範囲（研究者の決定・2026-11-02・判断 3）: 2019 年版（doi:10.7910/DVN/6BPCXN）と 2021 年版（doi:10.7910/DVN/BVOF7S）の `keystrokes.csv` だけ。課題文・調査票（`keystrokes-survey.csv`）・`students.csv`・2019 年版の `keystrokes-raw.csv`・2021 年版の実行の記録（`runs1.csv`・`runs2.csv`）は頼まない。
- 文案は英語（受け取る側の言語に合わせた）。

---

Subject: Request for access to the CS1 keystroke datasets (doi:10.7910/DVN/6BPCXN and doi:10.7910/DVN/BVOF7S)

Dear Dr. Edwards,

I am Mikoto Miura, an independent researcher (ORCID 0009-0000-4196-0508). I study how the timing of keystrokes and pauses during ordinary desk work can indicate when a person's work is stalling, without storing what they type.

I would like to use the two CS1 keystroke datasets described in your JEDM 2023 paper: the 2019 dataset (doi:10.7910/DVN/6BPCXN) and the 2021 dataset (doi:10.7910/DVN/BVOF7S). The termsOfAccess asks researchers to contact you before using the files, so I am writing first. The 2021 dataset is especially useful to me because each student worked on several assignments, which lets me look at how pauses vary within the same person across tasks.

How I plan to use them:

- Only the keystrokes.csv file of each dataset. I would not download or use the assignment descriptions, the starter code and videos, the survey file, students.csv, keystrokes-raw.csv, or the run logs (runs1.csv and runs2.csv).
- From keystrokes.csv, only the event timestamps and the type of each event (insert, delete, cursor movement). I would map each event to a coarse key category and discard the inserted and deleted text without storing it.
- Descriptive summaries only: the distribution of pauses, how often long stops in text production occur, and how these vary within and between students. No attempt to identify or re-identify anyone, and no linking with other data.
- The raw files would stay on my own computer and would not be redistributed. Only aggregate numbers would appear in publications or public repositories, with your datasets and paper cited.

If this use is acceptable, I would be grateful for your permission. If there are conditions you would like me to follow, please let me know.

Best regards,
Mikoto Miura
