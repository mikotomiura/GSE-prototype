## 監査の結果（意図の監査役・stage: manuscript・round 1）

一覧のファイルのうち、references.bib 以外はすべて読みました。原稿の本体は main.tex と sections/ の 12 本、ほかに outline.md と preregistration.en.md（References の節を除く 1〜306 行）です。

---

### 1. 意図にあって対象物に無いもの

**1-1. 持ち帰り 2 の「全体か区間か」を選ぶ材料に、過程の指標の軸がありません。**
- 意図（持ち帰り 2）は、照合の正答率と過程の指標の残り方の 2 軸で、全体か区間かを選ぶ材料にすることです。
- 原稿の過程の指標は、形ごと・全文だけで定義されています。区間（windows）の指標は定義が無く、要約の表と図も全文だけです。
  - protocol.tex §6.4 "The summary table covers full texts and the 500 writers"
  - 同 "The figure plots, for $N = 1{,}000$ on full texts"
- それでも discussion.tex §8.3 は、区間の選択にも 2 軸があるように予告しています。
  - "The results are material for three choices: ... and whether to release full logs or windows. Each statement takes the form ``against this attacker, at this $N$, this form had this multiple of $1/N$ and kept this much of the process measures''"
- 区間では「指標をこれだけ残した」の半分が出せません。

**1-2. 研究の「4 つの問い」が原稿のどこにも書かれていません。**
- 事前登録には Questions 1〜4 があり、原稿はそれを前提に書いています。
  - protocol.tex §6.6 "The fourth question of the study asks ..."
  - protocol.tex §6.7 "are not used to answer the four questions"
- しかし §1（方法の段落は角括弧）にも §3 にも、問いの列挙がありません。結果の後に書く方法の段落の計画（introduction.tex 24–30 行）にも、問いを示す予定がありません。

**1-3. 「検索の語は記録に無い」という限界が原稿にありません。**
- 意図の既知の限界は「検索の語は記録に無い」です。outline.md 85 行も "the search terms were not recorded and are not reconstructed" と書いています。
- related.tex 47–51 行は、日付・出典・件数を示し、"Google Scholar and Semantic Scholar were not searched" と書くだけです。語が記録されていないことは読者に開示されていません。

**1-4. outline の倫理の計画の 1 項目が本文にありません（軽微）。**
- outline.md の "The KLiCKe authors receive the paper when it is complete." が、ethics.tex にありません。

---

### 2. 対象物にあって意図に無いもの（漂流・範囲を超えた言い方）

**2-1. 序論が害 (a) を一般の規範として述べています。**
- introduction.tex 9–10 行 "A~log also carries the text it produced, so a release that is meant to protect the writers has to hide the text while keeping the process."
- 意図は、害 (a) を「公開した側が自ら掲げた目的に対して」の害に限っています。
- この文は「書き手を守る公開は本文を隠さねばならない」という一般の主張です。しかも同じ段落で、本文を公開する KLiCKe（同意あり）を挙げており、その例と緊張します。

**2-2. 照合された記録が「ラベル付きの標本」になる、という帰結が足されています。**
- threat-model.tex 56–57 行 "If a log were matched to a text whose writer is known, the log would from then on also be a labelled sample of that writer's keystrokes."
- 意図の害は (a) と (b) だけです。この文は、照合の後に打鍵の時間で別の公開物と結び付けることを示唆します。それは「複数の公開物の結び付けを使わない」という脅威モデルの外の連鎖です。
- outline は条件付きの推論として通していますが、意図の害の一覧にはありません。

**2-3. 害 (b) が表 1 で条件なしの言い方になっています。**
- threat-model.tex 表 1 の "Newly learned by matching" 列
  - Classroom: "The writing process, given for research, of a named student"
  - Published essay: "The writing process and score of a known writer"
- 意図は、(b) を「クラス単位の公開・公開作文から辿れた場合の帰結としてだけ」書くことです。本文 137–140 行はそのとおりですが、表の欄は条件を落として読めます。

**2-4. 「実際に使われた加工」を一般化して使っています。**
- 原稿が示す、本文を隠した公開は Kaggle の 1 件だけです。threat-model.tex 34 行は @ マスクを "not an instance of the threat studied here" とし、区間とクラスは "We know of no such release" としています。
- それでも次の箇所は複数形に近い一般化で書いています。
  - related.tex 44 行 "the processing used in practice"
  - ethics.tex 55 行 "against the processing used in practice"
- 意図の持ち帰り 1 の「慣行は実在し」も 1 件に支えられているだけです。抄録・貢献で「慣行」と書くと根拠を超えます。

**2-5. 探索の 2 分析（R-DP と、語長の並びの一意性）が意図の芯の外にあります。**
- protocol.tex §6.7 "Two analyses were added after the preregistration was fixed and are not part of it."
- 意図の芯が並べる加工は、マスク・カテゴリ・区切りの統合・丸め・区間の値・間引きです。差分プライバシーの雑音は含まれていません。
- 原稿は「探索」と明示し、主表と図から外しています。それでも、頁の圧迫（outline の移す順 (4)）と主張の範囲の両方で、意図に無い項目が増えています。

**2-6. 倫理の節が結果の向きを先取りし、提供していない手段を約束しています。**
- ethics.tex 52–53 行 "parties who release keystroke logs learn how much each processing step reduced matching"。「減らした」は結果の向きを前提にした言い方です。
- ethics.tex 37 行 "the paper gives releasing parties the means to measure it"。しかし公開するコードは 2 つのコーパスを読むものだけです（open-science.tex）。他の公開物を測る手段は与えていません。

**2-7. 持ち帰り 2 の「同じ攻撃者」は、原稿の慎重な言い方より強い表現です（意図の側の注意）。**
- 意図: 「同じ攻撃者・同じ N で並べ」
- 原稿 protocol.tex §6.2: "These differences therefore contain both the column and the attacker."。形ごとに使える攻撃者が違い（A1 / A1′ / A2-b）、「最強の攻撃者」は形ごとの最大値です。
- 抄録・結論で意図の言い方をそのまま使うと、原稿の §6.2 と矛盾します。

---

### 3. 矛盾（意図どうし・節どうし・原稿と事前登録）

**3-1. 登録の日付とデータ取得の日付が、書かれたとおりだと逆順になります（最も重い）。**
- open-science.tex 3 行 "The study was preregistered on OSF on 13 October 2026, before any data were acquired."
- data.tex 17–18 行 "We acquired the corpus on 12 October 2026 (UTC), after the preregistration was fixed"
- data.tex 38 行 ENJA15 "The sessions were acquired on 12 October 2026 (UTC)"
- related.tex 47 行 "made on 12 October 2026, before registration"
- 「固定（commit）」と「OSF への登録」を区別しないと、「取得の前に登録した」という原稿の主張が日付の上で崩れて読めます。threat-model.tex 8 行・data.tex 6 行も "before any data were acquired" と書いています。

**3-2. 害 (a) と、公開した側の目的とのつながりが詰められていません（意図どうしの緊張でもあります）。**
- 公開した側の目的は "to prevent reproduction of the essay text" です。原稿の害 (a) は "learning which text a processed log hides"（threat-model.tex 133 行）です。
- 攻撃者はもともと本文を持っています。表 1 の 1 行目自身も "if the texts and logs are already public elsewhere, only which records of two releases correspond" と書いています。それでも 135 行は "If a log can be matched to its text, the processing does not meet its stated goal" と断定しています。
- 「再現の防止」が「既に持つ本文との対応の秘匿」を含むかという論証が欠けています。
- 事前登録の (a) は "Learning the content of a hidden text (defeating the purpose of the processing)" で、原稿の (a)（どの本文か）と語が違います。outline.md 104 行は、(a) を主にし (b) を条件付きにした並べ替えだけを記録しており、(a) の中身の言い換えは記録していません。

**3-3. 頁の計画と投稿規程が衝突しそうです。**
- 意図: 「頁は結果の後に、重複と手続きの段落から付録へ移して 12 頁」
- outline.md は次のものを付録へ移す順に挙げています。
  - "(5) the methods for the Japanese translation logs (Sections 4.1, 4.3, 5.5 and 6.6)"
  - "(6) the details of A3 and of the alignment"
- 一方 §7 には問い 4 に答える ENJA15 の小節が残ります。規程は "The paper should be complete and self-contained without appendices. PC members are not required to read the appendices" です。
- さらに protocol.tex は、主張の材料を付録に置くと書いています。
  - "Attackers A0 to A3 on all writers after exclusion are reported in the appendix"
  - "All cells are given in the appendix"

**3-4. KLiCKe のライセンスの記述が節ごとに違います。**
- ethics.tex 12 行（私信）"the corpus is released under the MIT License"
- data.tex 16–17 行 "The terms of use allow the files to be downloaded and used freely, with the corpus cited as the source."
- discussion.tex 56 行 "KLiCKe may be downloaded and used freely, with the repository cited as the source"
- MIT への言及は倫理の節にしか無く、どれが根拠かが揃っていません。

**3-5. ENJA15 の R3j-t(w) は、定義上 R3j と同じ値になります。**
- attackers.tex 177–178 行 "Neither reads a string, so they give the same values on R0j, R3j and R3j-t"。ENJA では A0 と A2 しか走らず、どちらも時刻を使いません。
- protocol.tex 169 行は "R3j-t($w$) and R4($w$) are reported with the same rule" と、独立の結果として報告する書き方です。
- 事前登録どおりではあります。ただ、時刻を丸める比較が ENJA では情報を持たないことが明示されていません。

**3-6. 予測の範囲が事前登録より狭く書かれています（軽微）。**
- protocol.tex 230 行 "we registered predictions of the strongest attacker's accuracy for $N = 1{,}000$ on full texts"
- 事前登録の予測表には A4（最強の攻撃者に含まれない）と R5・R6 の予測も入っています。

**3-7. 付録と必須の 3 節の置き場所が outline の中で食い違っています（軽微）。**
- outline.md 20 行は、必須の 3 節を "(after `\appendix`, as in the template's example)" に置くとしています。
- outline.md 40 行は、付録を "(after the references)" に置くとしています。
- main.tex の順は \appendix → acks → 3 節 → 参考文献で、付録の中身の置き場所がまだ定まっていません。

**3-8. 二重盲検の扱いが未決のまま本文に残っています。**
- ethics.tex 3 行 "The author is not affiliated with a research institution"、および全体で単数の "the author" を使っています。
- 単著の独立研究者であることは、原稿から読み取れます。outline.md の倫理の計画も "check that the wording about affiliation ... do not identify the author" を未決としています。
- 意図の判断（登録のリンクは伏せ、匿名の複製で示す）は守られています。ただ、この点の判断は意図に書かれていません。

---

### 4. 整合していた点（短く）

- 新しさの範囲は意図どおりです。related.tex "we do not claim a stronger attack"・"The processing steps evaluated here are not new"、事前登録の "What is not concluded" とも一致します。
- 推奨の規則を出さない点も意図どおりです（threat-model.tex 171–172 行、protocol.tex §6.4、discussion.tex §8.3）。
- 次の既知の限界は、本文に明記されています: 閉じた世界・棄権しない・偽の一致の率を出さない／安全の証明・上限を主張しない／KeyTAR は脅威モデルの外の参考／Kaggle のデータを使わず、重なりも調べない／書き手の属性による差を主張しない／ENJA15 の差を言語・IME に帰さない／Inputlog と照合できなかった。
- 方法は事前登録から変えておらず、逸脱 2 件は記録として開示されています。
- 予測は §6 の末尾で触れ、§7 で示す予定です。攻撃コードは 2 つのコーパスを読むものだけを公開します。

---

### 5. 読めなかった範囲と注入の疑い

- 読んでいないもの: references.bib（書誌の中身は確かめていません）／preregistration.en.md の 308 行以降（References の節）
- 注入の疑い: ありません。読んだ文に、LLM や査読者に向けた指示は見つかりませんでした。
