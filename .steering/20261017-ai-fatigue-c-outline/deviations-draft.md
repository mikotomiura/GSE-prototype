# 選別の段の逸脱の文案（原稿の表 2 に入れる前の下書き）

作成 2026-10-27（判断 120）。出どころは decisions.md の判断 85〜119 と、登録 `~/TRACE/registration-en.md` の GSRR-33・34・36・37・38・41。数はコミット済みの `screening/` の CSV と判断の記録から取った。記録ごとの判定の値は書かない。

表 2 の列は、原稿の `tables.tex` の殻に合わせて「日付・登録の項目・変えたことと理由・影響する符号と表」の 4 つにした。英文は表のセルにそのまま入る長さを目安にしている。

「状態」は、確定（このまま入れてよい）か、要確認（研究者か共著者の確かめが要る）かを示す。

---

## D1. 著者 1 が自分の除外をすべて見直した（判断 91〜97・102）

- 起きたこと: 段 1 で 2 人とも除外したのに理由が違う記録が 47 件出た。原因は、2 人が使った冊の『判定基準』に、付録 6 の決まりのうち次の 3 つが書かれていなかったことにある。
  - 除外理由の順
  - Q1 の一次研究の定義
  - E2・E3 の補足
- 対応: 著者 1 は自分の除外をすべて付録 6 に照らして見直した（段 1 は 390 件、段 2 は 44 件）。結果は次のとおり。
  - 段 1: 含めるに変えた 146 件、理由を変えた 81 件
  - 段 2: 含めるに変えた 6 件、保留に変えた 6 件、理由を変えた 4 件
- 記録の残し方と数え方:
  - 元の判定はコミット済みの CSV に残っている。
  - 段 1 の 2 割の一致率は、独立に判定した元の値で数えた。
  - 監査の分母も元の値で数えた。
  - 段 2・3 の一致率は見直し後の値で数えた。段 2 の見直しは、共著者の h1 を取り込む前に済んでいたからである。
- 道具と判定基準: 道具に `import-revision` を足した。判定基準のシートには欠けていた 6 行を足した。共著者の h1 は、足す前のシートで判定されている。
- 状態: 確定

**英文案（表 2）**

| Date | Registration item | Change and reason | Affected |
|---|---|---|---|
| 2026-10-24 | GSRR-36 (rules of attachment 6); GSRR-33 (batches and commits) | The criteria sheet of the screening workbooks did not carry three rules of attachment 6: the order of the exclusion codes, the definition of a primary study (Q1), and the notes on E2 and E3. The authors' codes differed on 47 records that both excluded at title and abstract. Author 1 therefore re-checked every one of their own exclusions against attachment 6: 390 at title and abstract and 44 at full text. At title and abstract, 146 exclusions became inclusions and 81 changed code. At full text, 6 became inclusions, 6 became pending and 4 changed code. The original judgements remain committed and are released beside the revised ones. Agreement on the random 20% and the denominator of the audit use the original, independent judgements; the revised values are shown as a supplement. Agreement at full text and centre uses the revised values, which were fixed before author 2's first full-text workbook was read. The missing rules were added to the criteria sheet; author 2's first full-text workbook had been judged with the earlier sheet. A command that records the revisions was added to the screening tool. | Flow diagram; screening agreement (note to Table 3); audit of stage-1 exclusions |

## D2. 共著者が判定の案に ChatGPT を使った（判断 91・104・114・119）

- 起きたこと: 共著者が戻した冊と表の根拠メモの末尾に、「ChatGPT判定」「ChatGPT確認案」「ChatGPT判定案」といった印があった。
  - 印があるもの: net1 で 166/166 件、h1 で 206/206 件。h2・理由の冊・2 人で決める表・h3 にもある。
  - 印が無いもの: 2 割の標本 113 件には 0 件。つまり、段 1 の一致率の元になる判定には印が無い。
- 登録との関係: 登録が選別に使う AI は、段 1 の網だけである（役割の表・GSRR-33）。
- 研究者の判断（判断 91）: 判定は共著者のもので、ChatGPT は補助として使った、と研究者は分かっている。そのまま進めた。
- 状態: 要確認。報告するかどうかではなく、書き方の確認である。共著者が何に使ったかを共著者の言葉で確かめ、Use of AI の宣言にも同じ内容を書く。

**英文案（表 2）**

| Date | Registration item | Change and reason | Affected |
|---|---|---|---|
| 2026-10-24 to 2026-10-27 | Roles (AI assistant; screeners); GSRR-33 (AI only as the safety net at title and abstract) | Author 2 used ChatGPT (OpenAI) to draft the reasons for their judgements in the net workbook, the full-text workbooks, the workbook on exclusion codes and the reconciliation tables; each judgement was made and entered by author 2. The registration names no AI tool for the screeners other than the safety net. Author 2's judgements on the random 20% at title and abstract carry no such mark, so the title-and-abstract agreement does not involve the tool. [to be confirmed with author 2: what the tool was given and what it returned] | Use of AI statement; screening at full text and centre |

## D3. 戻った冊を取り込む前に、値の形を直した（判断 88・101）

- 段 1 の 2 割の冊: Google スプレッドシートを通って戻ったため、ID の列がリンクの内部表記に置き換わっていた。リンク先の ID で書き戻してから取り込んだ（113 行。ほかのセルの違いは 0）。
- h1: 共著者が保留にした 24 件に「境界（保留）」の中心が入っていた。中心は含めた記録にだけ付けるものなので、取り込む前に「未判定」に戻した（違いは 24 セルだけ）。
- どちらも、戻った冊と取り込んだ写しの SHA-256 を記録してある。
- 状態: 確定

**英文案（表 2）**

| Date | Registration item | Change and reason | Affected |
|---|---|---|---|
| 2026-10-24; 2026-10-25 | GSRR-41 (author 2's workbooks released) | Two returned workbooks were corrected in form before import. In the title-and-abstract workbook, which had passed through Google Sheets, the record IDs had been replaced by internal link codes; they were written back from the link targets (113 rows; no other cell changed). In the first full-text workbook, 24 records that author 2 left pending carried the centre value boundary; centres are given only to included records (attachment 6), so these cells were cleared (no other cell changed). The SHA-256 of both the returned and the imported versions is recorded. | None (no judgement changed) |

## D4. 冊と表が、共有フォルダでなく直接の連絡で戻った（判断 106・114）

- 起きたこと: 共著者の h2 と、2 人で決める表 2 冊は、共有フォルダを通らず、研究者への直接の連絡（zip など）で戻った。
- 確かめたこと: 受け取ったときに SHA-256 を記録し、配った版と、判定の欄以外の違いが 0 であることを確かめた。
- 登録との関係: 登録と添付を "shared"・"folder" で探したが、戻し方の決まりは無かった（GSRR-33 は冊で渡すとだけ書く）。逸脱ではない。
- 状態: 確定（方法の節に 1 文書く）

**英文案（方法の節）**

> Author 2 returned one full-text workbook and the two reconciliation tables directly to author 1 rather than through the shared folder; their SHA-256 was recorded on receipt, and they differed from the versions sent only in author 2's columns.

## D5. 2 人で決めるのを、案と同意の 2 段で行った（判断 112〜116・119）

- やり方: 全文と中心の段で 2 人が違った 116 件（b01〜b39）は、次の順で決めた。
  1. 著者 1 が表に案と理由を書いた。
  2. 著者 2 は 100 件に同意し、16 件に同意しなかった。
  3. 16 件は 2 人で全文を読み直して決め、著者 2 がすべての結論に合意した。
  - 段 1 で理由が違った記録も、同じ形で決めた（見直しの後に残った 16 件）。
  - b40 の 3 件は、2 人で決めたうえで著者 2 が合意した。
- 登録との関係: GSRR-38 の「一緒に決める」の形として書く。逸脱ではない。
- 状態: 確定（方法の節に書く）

**英文案（方法の節）**

> Differences were reconciled in two steps. Author 1 wrote a proposal with its reason for each record in a table; author 2 agreed or disagreed and commented. Records author 2 disagreed on were read again in full text and decided together, and author 2 agreed with each outcome. At full text and centre, author 2 agreed with 100 of 116 proposals; the other 16 were decided together.

## D6. S13-18 の全文が抄録の 1 頁だけだった（判断 115）

- 起きたこと: 段 2 で 2 人が読んだ S13-18 の全文（Authorea のプレプリント v1 の PDF）は、抄録の 1 頁だけだった。本文は、記録の頁の補足資料の docx にあった。
- 著者 1 の読み方: 著者 1 の根拠は、題名と年がこの記録と違う、2022 年の別の誌の版の本文だった。
- 対応: 2 人で決める段で、研究者が docx を保存した。打ち直さずに PDF に変え、その本文で 2 人が決めた。
- 登録との関係: 登録は「2 人は同じ全文を使う」とし、「後で無料の全文が見つかった保留の記録は、束にして 2 人が判定し直す」とする。S13-18 は保留ではなかった。そのため束での判定し直しをせず、照合の段で決めた。
- 状態: 確定

**英文案（表 2）**

| Date | Registration item | Change and reason | Affected |
|---|---|---|---|
| 2026-10-27 | GSRR-33 (full texts; both authors use the same full text; records whose free full text is found later are judged again) | For one record (S13-18), the file judged at full text held only the one-page abstract of the preprint; the full text was in a supplementary file on the record's page. Author 1's judgement had also drawn on a 2022 version with a different title and year. The full text was obtained during reconciliation (converted to PDF without retyping), and the record was decided together on it rather than judged again in a separate batch, because it was not a pending record. | One record's stage-2 decision |

## D7. 理由なしの保留を、合意で保留のまま残した（24 件・判断 115・116・119）

- 起きたこと: 段 2 の最終が「保留・理由なし」の記録が 24 件ある。どれも決まり方は「consensus」で、内訳は次のとおり。
  - 2 人とも理由なしの保留: 15 件
  - 片方が保留で、もう片方が含める: 5 件
  - 片方が保留で、もう片方が除外: 4 件
- 登録との関係: GSRR-33 は次のように決めている。
  - 2 人とも理由なしで保留にした記録は、読み直して一緒に決める。合意できなければ unresolved にする。
  - 含めるかで合意できない記録は unresolved にし、ID と数を報告する。

  登録が書く最終の値は、含める・除外（理由つき）・E6 の保留・unresolved だけで、「合意して理由なしの保留」は無い。道具の `unresolved_row` も、2 人とも理由なしの保留にした記録を unresolved の対象としている。
- 影響: どちらにしても本体の外である。違いは表 3 と流れ図での数え方（pending か unresolved か）と、ID を報告するかどうか。
- 訂正: 私は b40 の CS00828 に「保留・理由なし」を勧めた。そのとき「合意できない」の説明に「2 人の判断は割れていないので実際の状態と合わない」と書いたが、これは登録の文を読み落としていた。
- 状態: 要確認（研究者の選択）。決め方は 2 つある。
  - (a) 24 件の最終を「合意できない」に書き直す（新しい書き出しのコミットが要る）。
  - (b) そのまま残し、逸脱として報告する。

**英文案（表 2・(b) を選んだ場合）**

| Date | Registration item | Change and reason | Affected |
|---|---|---|---|
| 2026-10-27 | GSRR-33 (a record left pending without a code is decided together and is unresolved if they cannot agree) | For 24 records at full text, the authors agreed, after reading them again, that the rules do not settle them (15 both left pending without a code; in 9 one author left the record pending). They were recorded as pending without a code by consensus rather than as unresolved. Like unresolved records, they are outside the main set; their IDs are released and they are counted with the records pending at the closing date. | Table 3; flow diagram |

## D8. 方法の節に書くが、逸脱ではないもの

- 全文の探し直しと判定し直し（判断 117〜119）: E6 の保留 102 件の全文を探し直し、7 件の本文を取った。7 件は束 b40 で 2 人が判定し直した（GSRR-33 どおり）。最後の回を数える。
- データセットの記録の全文（判断 83・98・117）: 公開されている説明の頁を全文とした。対象は CS00828・CS07885・CS09148、学会の抄録の頁の 1 件。
- 形式の変換（判断 88・98・115・117）: docx・xlsx だけが公開されていた 4 件は、打ち直さずに PDF に変えた。元のファイルも横に残した。
- 著者 1 の判定の入力（判断 80・81・89）: 著者 1 が決めた判定とメモを、Codex（Google Drive のプラグイン）が DB に書き込んだ。
  - 状態: 要確認。判断 85 では、段 2 の 1 回目の 174 件の表が作業を始めて約 6 分でできていた。入力だけだったのかを研究者に確かめ、Use of AI に書くかを決める。

**英文案（方法の節）**

> Pending records whose free full text was found in a later search were judged again by both authors in one batch (7 of 102 records left pending with E6). For records that are datasets, the public description page was taken as the full text. Full texts published only as word-processor or spreadsheet files were converted to PDF without retyping, and the original files were kept.
