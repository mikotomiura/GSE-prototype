# 問い合わせ文の草案（BRM の編集者・ZEN大学・所属機関の外の審査委員会）

> ⚠️ 草案。**送るのは研究者**（外部への送信は取り消せない）。宛先・氏名は送る前に一次で確かめる。
> ★ 打鍵の記録・NDJSON・参加者の情報を**添付しない**（`data-privacy` Skill）。
> 根拠: ADR-039 D2（条件 a・b）・D3。順序の推奨: **B（大学）→ C（外部の委員会）→ A（編集者）**。
> 理由: A に「どの委員会が見るか」を書けたほうが答えが具体になる。ただし A の答えは D2 の条件 a なので、B・C が長引くなら並行して送る。

---

## A. BRM の編集者あて（英語）

⚠️ 宛先: 投稿規定の「未解決の質問は編集者へ」の箇所にある連絡先（下位エージェントの報告では編集者 2 名の名とアドレスがあった。**私は確かめていない** → 送る前に <https://link.springer.com/journal/13428/submission-guidelines> で確認する）。

```
Subject: Pre-submission inquiry: ethics approval for a keystroke-timing dataset collected before committee review

Dear Editor,

I am an independent researcher affiliated with ZEN University (Japan) and plan to submit to
Behavior Research Methods. Before designing the study, I would like to ask how the journal would
treat the following situation.

1. The study records keystroke timing in participants' everyday computer work (key category such
   as "letter / backspace / space / enter" and timestamps only; no characters, no screen content,
   no application names). Participants are a small group (3–5) recruited directly by me, with
   written (electronic) informed consent, an on-screen recording indicator, one-click pause, and
   the right to delete any time range.
2. My university does not appear to operate a research ethics committee for non-medical human
   research [I am confirming this with the university]. Data collection started on 8 October 2026
   without committee approval or exemption, based on my own assessment.
3. I understand from the submission guidelines that retrospective approval usually cannot be
   obtained and that proceeding to peer review is at the Editor's discretion.

My questions:
(a) If an independent ethics committee reviews and approves (or exempts) the secondary analysis and
    publication of the already-collected data, could a manuscript using these data be considered
    for peer review? If so, what should the ethics statement contain?
(b) If not, would the journal consider a manuscript whose data are newly collected after committee
    approval, while the earlier data are described only as a pilot (not analysed in the paper)?
(c) Because keystroke timing may allow re-identification, I plan to share the processed data
    under a controlled-access agreement rather than openly. Would this satisfy the journal's
    research data policy if the conditions of access are stated in the Open Practices Statement?

Thank you for your time.

[Name]
[Affiliation]
[Email]
```

⚠️ (b) の「pilot として記述するだけで解析しない」は ADR-039 D1 の書き方に合わせた。O1 を論文でどう扱うかは研究者が決める。

---

## B. ZEN大学あて（研究推進・研究倫理の窓口）

⚠️ 宛先: 公開資料に、人を対象とする研究の審査の窓口は見つからなかった（研究不正の告発窓口だけ）。【学生／教員の別に応じて、指導教員・事務局・研究倫理教育責任者のどれに送るかを研究者が決める】

```
件名: 人を対象とする研究の倫理審査の取り扱いについてのお問い合わせ

【所属・氏名】です。
個人として行っている研究について、学外の学術雑誌（Behavior Research Methods）へ投稿する際に、
倫理審査の承認または免除の記載を求められるため、次の点をお尋ねします。

研究の概要:
・パソコン作業中のキー操作の「種類と時刻」だけを記録し、作業の状態の推定に使えるかを調べる研究です
 （打った文字・画面の内容・アプリ名は記録しません）。
・対象は研究者が直接説明する 3〜5 名程度で、電子的な説明と同意を取っています。
・医学系の研究ではありません。

お尋ねしたいこと:
1. 本学に、人を対象とする研究（医学系以外）の倫理審査を行う委員会や手続きはありますか。
   あれば、申請の方法と、【学生／教員】が申請できるかを教えてください。
2. 無い場合、「本学では人を対象とする研究の倫理審査を取り扱っていない」旨を、
   書面（メール可）でいただくことはできますか（投稿先への説明に使います）。
3. 委員会が無い場合に、所属機関の長などによる承認で代える仕組みはありますか。
4. 学外の倫理審査委員会で審査を受けることについて、本学として定めや制約はありますか。

お手数をおかけしますが、よろしくお願いいたします。
【氏名・連絡先】
```

★ 3 は日本心理学会の方針（委員会が無ければ所属機関の長の承認で代えることを認める場合がある）[V241] に合わせた問い。⚠️ BRM が所属機関の長の承認を「委員会の承認」として受けるかは確かめていない → A で併せて聞くかは研究者が決める。

---

## C. 所属機関の外の審査委員会あて（例: 心理学調査・実験に関する研究倫理審査委員会 [V242]）

⚠️ 宛先: 委員会のページの問い合わせ窓口（ページに記載のフォームまたはメール）。費用 20 万円（税別）・最長 5 週間（ページの逐語）。

```
件名: 申請資格と、既に始めている収集の扱いについての事前のお問い合わせ

【氏名】と申します。【ZEN大学の学生／教員】で、個人として研究を行っています。
申請の前に、次の点をお尋ねします。

研究の概要:
・パソコン作業中のキー操作の「種類と時刻」だけを記録し、作業の状態の推定に使えるかを調べる研究です
 （打った文字・画面の内容・アプリ名は記録しません）。対象は 3〜5 名程度、電子的な説明と同意を取ります。
・成果は学術雑誌（Behavior Research Methods）への投稿と、加工した記録の公開（申請制を検討）を予定しています。

お尋ねしたいこと:
1. 所属機関に倫理審査委員会が無い（または取り扱っていない）研究者の申請を受け付けていますか。
   【学生の場合: 学生個人の申請は可能ですか】
2. これから始める新しい収集の審査（研究計画・同意文書・データ公開の方法を含む）をお願いできますか。
3. 既に別の目的で 2026 年 10 月 8 日から始めている収集（委員会の承認を受けていないもの）について、
   その記録の解析と公表を新しい研究として審査していただくことはできますか。
4. 審査の対象に、加工した打鍵の記録を公開することの適否（再識別のおそれへの対策）を含められますか。

よろしくお願いいたします。
【氏名・連絡先】
```

---

## 答えが来たら

| 答え | 次にすること |
|---|---|
| A の (a) が可 | ADR-039 D2 の条件 a を満たした、と記録する（書面を保管・repo には要旨のみ） |
| A の (a) が否 | O1 のデータは 2 本目に使わない（D2 は不成立）。D1 の新しい収集だけで進める |
| B で委員会あり | 大学の委員会に申請（C は不要） |
| B で委員会なし・書面あり | 書面を保管し、C へ申請 |
| C で申請不可 | 他の委員会を探す（未踏査: NPO・一般社団法人の委員会） |
