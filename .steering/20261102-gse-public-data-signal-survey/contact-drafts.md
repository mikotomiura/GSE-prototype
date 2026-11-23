# 打鍵の外の信号のデータの利用の問い合わせ（文案・送るのは研究者）

作成: 2026-11-02。研究者の決定（同日）: 要連絡の候補にメールで問い合わせる。カードは `docs/literature/20261102-public-data-beyond-keystrokes.md`。

共通の方針（CS1 の文案 `.steering/20261102-gse-public-data-landscape/cs1-contact-draft.md` と同じ形）:
- 頼む範囲は、時刻と出来事の種類（キーの種類・ポインタの動き・自己申告の値）だけ。本文・キーの名前・ウィンドウの題名は使わないか、受け取らない。
- 元の研究の倫理承認と同意の範囲の中で使う。再識別を試みない。ほかのデータと結び付けない。再配布しない。公開するのは集計値だけ。
- 自分の所属機関の倫理承認は無いと正直に書き、相手が条件を求めるならそれに従うと書く。
- 返事が来る前にデータを取らない（CS1 と同じ）。

宛先の出どころ（2026-11-02 に確かめた）:

| # | 候補 | 宛先 | 出どころ |
|---|---|---|---|
| 1 | Naegelin ら（職場・8 週） | aferrario@ethz.ch | medRxiv の本文の「For correspondence」（Chrome で確認）。本文の逐語 "Data are added to a repository in the Open Science Framework (OSF) under https://osf.io/qpekf/ and are available upon request."。OSF のノードは API で 401（非公開） |
| 2 | Clarkson II | citer@clarkson.edu | CITeR の Clarkson I のページの "To request this dataset, please contact citer@clarkson.edu and indicate the specific dataset."。Clarkson II のページ（citer.clarkson.edu/?p=4082）は請求の方法を書かず、"Contacts" に案内する。同じセンターなのでこの宛先にした |
| 3 | W-CoLeJa（国立国語研究所） | y.nakamura@ninjal.ac.jp | 2026-09-12 の NINJAL 日本語教師セミナーの案内の「プロジェクト窓口担当」（`[at]` を `@` に置き換えた） |
| 4 | Erasmus MC「Computer use 2002-2008」 | DANS のデータセットのページの「Contact」のボタン（メールの宛先は公開されていない） | DANS のページの "Use email button above to contact."・連絡先は HP Slijper (Erasmus MC) |
| 5 | Multi-ID | tjneal@usf.edu | 著者のデータセットのページの "You may contact Dr. Tempestt Neal for dataset access" とプロフィールのアドレス |
| 6 | SENSE-42 | Zenodo のレコードの「Request access」のフォーム | Zenodo の API で `access_right: restricted` を確認 |

送らない候補: Staley & Ford（データの公開の記述が無く 2015 年）、ISOT（指導者の署名つきの同意書が要るとの報告で、独立の研究者には満たせない）、EmoSurv（申請なしで落とせる・非商用）、Smeaton ら・RLKWiC（配布先を確かめていない）。

---

## 1. Naegelin ら（ETH Zurich）

宛先: aferrario@ethz.ch

Subject: Data request: OSF dataset of "One does not fit all" (mouse, keyboard, and cardiac data in the field)

Dear Dr. Ferrario,

I am Mikoto Miura, an independent researcher (ORCID 0009-0000-4196-0508). I study how the timing of keystrokes, pauses, and pointer movement during ordinary desk work can indicate when a person's work is stalling, without recording what they type.

I read your medRxiv preprint "One does not fit all: Detecting work-related stress from mouse, keyboard, and cardiac data in the field" (doi:10.1101/2025.08.02.25332538). It says the data are in the OSF repository (https://osf.io/qpekf/) and are available upon request, so I am writing to ask whether I could use them. Your dataset is unusually valuable for my question because it combines field data from real office work over eight weeks with in-situ self-reports several times a day, and because the keyboard data were already made content-free (timestamps rounded to seconds and random key IDs).

How I plan to use the data:

- Only the raw mouse events (timestamp, position, event type), the partially aggregated keyboard events (the press and release events with random key IDs), and the EMA ratings with their timestamps. I would not need the cardiac data, the weekly questionnaires, or the sociodemographic variables.
- Descriptive, within-person analyses: how often long stops in typing occur, what the pointer is doing during those stops, and how this varies within and between participants. No attempt to identify or re-identify anyone, and no linking with other data.
- The data would stay on my own computer and would not be redistributed. Only aggregate numbers would appear in publications or public repositories, with your dataset and paper cited.

I am not affiliated with an institution, so I do not have my own ethics approval. I would use the data only within the scope of your ethics approval and your participants' consent. If you require a data use agreement, an institutional approval, or any other conditions, please let me know and I will follow them.

Thank you for considering this request.

Best regards,
Mikoto Miura
Independent Researcher
ORCID: https://orcid.org/0009-0000-4196-0508

---

## 2. Clarkson II（Clarkson University CITeR）

宛先: citer@clarkson.edu

Subject: Request for the Clarkson II keystroke dataset

Dear CITeR team,

I am Mikoto Miura, an independent researcher (ORCID 0009-0000-4196-0508). I study how the timing of keystrokes and pauses during ordinary computer use can indicate when a person's work is stalling, without recording what they type.

I would like to request the Clarkson II keystroke dataset (the free-text dataset recorded in users' natural settings, described at https://citer.clarkson.edu/?p=4082). It is the most suitable dataset I have found for my question, because it records each person's typing over a long period in their own environment, which lets me look at how long pauses vary within the same person.

How I plan to use the data:

- Only the key-down and key-up timestamps and, if present, a coarse key category (for example letter, space, backspace). I would not use any key identity beyond such a category.
- Descriptive, within-person analyses of pause lengths and of how often long stops in typing occur. No attempt to identify or re-identify anyone, no authentication or identification experiments, and no linking with other data.
- The data would stay on my own computer and would not be redistributed. Only aggregate numbers would appear in publications or public repositories, with the dataset and its papers cited.

I am not affiliated with an institution, so I do not have my own ethics approval. I would use the data only within the scope of the original consent and approval. If a release agreement or any other conditions apply, please send them to me and I will follow them. I would also be grateful to know which papers you would like me to cite for this dataset.

Best regards,
Mikoto Miura
Independent Researcher
ORCID: https://orcid.org/0009-0000-4196-0508

---

## 3. W-CoLeJa（国立国語研究所）

宛先: y.nakamura@ninjal.ac.jp

件名: W-CoLeJa の執筆ログ（EssayLogger）の研究利用についてのお問い合わせ

国立国語研究所「日本語学習者の作文の縦断コーパス研究（W-CoLeJa）」プロジェクト
中村 有里 様

突然のご連絡失礼いたします。独立研究者の〔お名前（漢字）〕（Mikoto Miura、ORCID 0009-0000-4196-0508）と申します。キーボードの打鍵の時刻と休止から、ふだんの作業が行き詰まりかけている時を推定する研究をしています。入力された文字そのものは記録・保存しない方法を取っています。

2026 年 9 月 9 日の Inalco の研究会のプログラムで、W-CoLeJa core_05 の執筆ログが「入力の系列、変換候補の選択、再変換、削除、置換、および時間情報」を記録していると拝見しました。日本語の変換の過程を時刻つきで記録した資料は、私の調べた範囲ではほかに見当たらず、大変貴重だと考えております。

そこで、次の点を教えていただけないでしょうか。

1. W-CoLeJa の執筆ログ（EssayLogger の記録）は、外部の研究者に提供・公開されていますか。または今後その予定はありますか。
2. 提供される場合、利用の条件と申し込みの方法を教えてください。

利用できる場合の使い方は次のとおりです。

- 使うのは、出来事の種類（文字の入力・変換・候補の選択・確定・削除など）とその時刻だけです。作文の本文や変換された語そのものは分析に使いません。
- 書き手ごとの休止の長さや、変換にかかる時間の分布を記述的に調べます。書き手を特定しようとしたり、ほかのデータと結び付けたりはしません。
- データは私の手元の計算機の中だけに置き、再配布しません。公開するのは集計した値だけで、コーパスと関連の論文を引用します。

なお、私は機関に所属していないため、私自身の倫理審査の承認はありません。元の研究の承認と協力者の方々の同意の範囲の中で使います。利用の条件（誓約書・所属機関の承認など）がございましたら、それに従います。

お忙しいところ恐縮ですが、ご検討いただけましたら幸いです。

〔お名前（漢字）〕（Mikoto Miura）
独立研究者
ORCID: https://orcid.org/0009-0000-4196-0508

（研究者へ: お名前の漢字は私が知らないので〔〕にしてあります。埋めてから送ってください。）

---

## 4. Erasmus MC「Computer use 2002-2008」（DANS の Contact のフォーム）

送り方: https://doi.org/10.17026/dans-zuf-ft56 のページの「Contact」のボタンから送る（宛先は HP Slijper と DANS）。

Subject: Access request: "Computer use 2002-2008" (doi:10.17026/dans-zuf-ft56)

Dear Dr. Slijper,

I am Mikoto Miura, an independent researcher (ORCID 0009-0000-4196-0508). I study how the timing of keystrokes, pauses, and mouse activity during ordinary office work can indicate when a person's work is stalling, without recording what they type.

The DANS record of "Computer use 2002-2008" says the main database is not available online but can be made available after contacting DANS and the depositor, so I am writing to ask whether that is possible. The dataset is very valuable for my question because it records the computer use of many employees during their normal work over long periods.

Before asking for the files, I would like to know:

1. Whether the consent and approval of the original study allow use by an outside researcher for a secondary analysis like the one below.
2. What the event records contain (for example, whether keystrokes are stored with key identities or only as timestamps, and the timing resolution), and what conditions apply.

How I would use the data:

- Only event timestamps and event types (keystroke, mouse movement, click, scroll). I would not use key identities or the questionnaire data beyond what is needed to describe the sample.
- Descriptive, within-person analyses of pause lengths and of how often long stops in activity occur. No attempt to identify anyone, and no linking with other data.
- The data would stay on my own computer and would not be redistributed. Only aggregate numbers would be published, with the dataset and your papers cited.

I am not affiliated with an institution, so I do not have my own ethics approval. If any conditions apply, please let me know and I will follow them.

Best regards,
Mikoto Miura
Independent Researcher
ORCID: https://orcid.org/0009-0000-4196-0508

---

## 5. Multi-ID（University of South Florida）

宛先: tjneal@usf.edu

Subject: Request for access to the Multi-ID dataset

Dear Dr. Neal,

I am Mikoto Miura, an independent researcher (ORCID 0009-0000-4196-0508). I study how the timing of keystrokes, pauses, and pointer movement can indicate when a person's work is stalling, without recording what they type.

I read your paper "Multi-ID: A Novel Dataset for Advancing Understanding of Cross-Task and Cross-Device Input Dynamics", and your datasets page says researchers may contact you for dataset access. I would like to ask whether I could use the desktop part of the dataset, because it records free-form keystrokes and free-form mouse movement from the same people in the same sessions.

How I plan to use the data:

- Only the desktop keystroke timestamps (press and release) with a coarse key category, and the mouse event timestamps and positions. I would not use the touch data or any key identity beyond a category.
- Descriptive analyses of what the pointer is doing during pauses in typing. No authentication or identification experiments, no attempt to re-identify anyone, and no linking with other data.
- The data would stay on my own computer and would not be redistributed. Only aggregate numbers would be published, with the dataset and paper cited.

I am not affiliated with an institution, so I do not have my own ethics approval. I would use the data only within the scope of the original consent and approval. If a data use agreement or other conditions apply, please let me know and I will follow them.

Best regards,
Mikoto Miura
Independent Researcher
ORCID: https://orcid.org/0009-0000-4196-0508

---

## 6. SENSE-42（Zenodo の Request access のフォーム）

送り方: https://zenodo.org/records/20328099 の「Request access」から送る。フォームの欄の名前は開いてから合わせる。

Justification（申請の理由の欄に貼る）:

I am an independent researcher (ORCID 0009-0000-4196-0508) studying how the timing of keyboard and mouse activity can indicate when a person's work is stalling, without recording typed content. I would use only the per-frame mouse and keyboard state with timestamps, for descriptive analyses of pauses in input and pointer activity during the tasks. I will not attempt to re-identify participants, will not link the data with other sources, and will not redistribute the data; only aggregate results would be published, with the dataset cited. I am not affiliated with an institution and do not have my own ethics approval, so I would use the data only within the scope of the original consent, and I will follow any data use conditions you set.
