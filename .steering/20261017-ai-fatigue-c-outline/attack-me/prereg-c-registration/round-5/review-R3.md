# 査読 R3（メタ研究・事前登録・再現性の立場）・round 5・草稿 0.11（差分 0.10→0.11）

## 1. 接地（文献・逐語）
1. van den Akker et al. 2023（gsrr.txt）: "[GSRRF-37] Screening reliability: For each screening round, list the number of screeners and the procedure used to ensure independent screening." → 独立を主張するなら、それを確かめる手順が要る。
2. 同: "whether two people will independently screen records for inclusion or whether one will screen and an other check decisions) and whether researchers will be blinded to each other’s’ decisions." → 食い違いの扱いと、互いの判断を見ないことを書く。
3. 同: "[GSRRF-47] Extraction reliability: For each extraction round, list the number of extractors and the procedure used to ensure independent extraction (this can also mean that you declare that you use one extractor, ...)" → コーダー 1 人の設計は、そう宣言すれば様式に合う。
4. 同（context-A の逐語 3）: "If you already foresee some deviations when filling out the form ... provide a contingency plan for these deviations in the relevant parts of the registration" → 予見できる逸脱には代わりの計画を書く。
5. Nuijten et al. 2016（nuijten2016.txt）: "Possible solutions for the high prevalence of reporting inconsistencies could be to encourage sharing data, to let co-authors check results in a so-called “co-pilot model,” and to use statcheck to flag possible inconsistencies in one’s own manuscript or during the review process." → 数値は本人以外も確かめる。
6. 同: "Furthermore, manual checking is subject to human error, which statcheck eliminates." → 人の手の検算には誤りが入る。

## 2. 評価表
- a 4: 1 人のコードと AI を 2 人目にする代価は正直に書いてある。ただし「AI は題と抄録だけを見る」「各記録を単独で判定する」が添付 6 と GSRR-33 の別の文と合わない（M4・m1）。
- b 3: 較正が主の集合の選別と同じ時期に走り、改訂が主の集合の全文に触れうる（M1）。著者 1 が先に判定したことを確かめる記録が無い（M3）。感度分析 5 に代わりの計画が無い（M5）。
- c 4: AI の選別者を登録前に合否の線で確かめ、2 回分を添付で出す手順は再現できる形。
- d 3: GSRR-6・33・39 に散った同じ手順が互いに食い違うようになった（M1）。
- e 4: GSRR-37/47 の「1 人と宣言する」形に合う。逐語 3 は感度分析 5・AI のモデルの継続・主の段で一致が低い場合について欠ける（M5・m3）。
- f 4: 差分ではほとんど変わっていない。
- g 3: boundary の行き先、理由コードの無い pending の最終、著者 1 の判定の規則、感度分析 5 の together の決め方、較正の改訂後の確かめ直しが 1 通りに決まっていない（M2・M6・m4）。

## 3. 指摘（重い順）

- [major] M1 較正のコードを選別と並行して行うことが「選別中はコードしない」と食い違い、規則の改訂が主の集合に触れうる
  - 位置と引用: registration-en.md:47（GSRR-6 段 4）「Calibration coding on the exploration set, in parallel with stage 3: author 1 codes all its primary studies twice, in November and December 2026」／GSRR-33「no coding is done during screening;」／「The primary counts come from records that were not used to build the rules.」／GSRR-44 段 2「For every unit below 80% percentage agreement, the definitions are amended and the amendment is registered before main coding」
  - なぜ問題か: 文がそのまま矛盾する。著者 1 は全文を選別しながら定義を改訂するので、改訂が主の集合の全文の影響を受けないことを止める規則が無い（逐語 3）。
  - 解消の条件: (1) 「主の集合の記録はコードしない（探索の集合の較正は並行）」に直す。(2) 改訂の根拠は探索の集合の 2 回の食い違いだけ、改訂の記録に根拠の ID を付ける、主の集合の選別で読んだ記録を根拠にしない、と書く。(3) GSRR-65 に 1 行。
  - 自信: 高

- [major] M2 選別の判定の分類に、行き先の無い値がある（centre の boundary・理由コードの無い pending）
  - 位置と引用: GSRR-33「centre (centre-A, centre-B or boundary, for records included at full text)」／GSRR-56「SQ1 is answered by tables split into centre-A and centre-B」／添付 6 §4「`pending` (without a code) if the full text was read but the rules do not settle the record」／GSRR-39「records without a final full-text decision on that date」
  - なぜ問題か: 両者が boundary・両者が理由コードなしの pending とした記録の最終が決まっていない。理由コードなしの pending が "final full-text decision" に当たるかで主の集合の大きさが変わる。
  - 解消の条件: 両者が一致した boundary と pending も著者 1 が決める（または主の集合の外に置き件数を表 3 に出す）と書き、boundary が残った場合の SQ1 の表の扱いを書く。
  - 自信: 高

- [major] M3 著者 1 が先に判定したことを、記録で確かめられない
  - 位置と引用: GSRR-33「Author 1 does not see the AI screener's judgement of a record at a stage before recording their own judgement of it at that stage.」「Its output is stored with its SHA-256 before author 1 opens it.」／GSRR-17「run as subagents of Claude Code」
  - なぜ問題か: ハッシュは AI の出力が後で変わっていないことしか示さない。AI を動かすのは著者 1 自身で、出力は実行した人の画面に返る。独立を確かめる手順が無い（逐語 1・2）。
  - 解消の条件: バッチごとに、著者 1 の判定のファイルを AI を走らせる前にハッシュして時刻つきで記録する（コミット）。AI の出力を著者 1 が開かない形で保存する手順を書く。両方の時刻を GSRR-41 の公開物に含める。
  - 自信: 中

- [major] M4 添付 6 は AI に記録の Web ページを開かせるが、登録版は「題と抄録だけを見る」と書く
  - 位置と引用: 添付 6 §2「If no abstract was retrieved, you may open the record's landing page from its DOI or URL to read the abstract.」、Q6「unless the record's page or bibliography states the body language」、`"source"`／GSRR-33「The AI screener sees only the instructions and the record's title and abstract (first stage) or full text (later stages).」、添付 6 §1「It sees only this text and the record's inputs listed in section 2.」
  - なぜ問題か: AI に Web の道具があり、入力が固定されない（出版社のページの分類・関連論文など）。再現性も落ちる。抄録の無い記録で著者 1 も同じページを読むのかが無い。
  - 解消の条件: (a) 抄録の無い記録はスクリプトで取ったページの本文を DB に入れ、両者が同じものを読む・AI に Web の道具を渡さない、または (b) 開くことを認め、GSRR-33 を直し、URL と取得物のハッシュを残す。Q6 も同じ。
  - 自信: 高

- [major] M5 感度分析 5 が共著者の時間に依存するのに、代わりの計画が無い
  - 位置と引用: GSRR-40「A second human screening of the 264 additional candidates before coding would fall on the co-author, whose time is limited.」／GSRR-62 の 5「authors 1 and 2 screen again, each on their own and then together, at the full-text stage and the centre stage」
  - なぜ問題か: AI を 2 人目にした理由が、そのまま感度分析 5 が実行されない危険でもある（逐語 3）。行われないと限界の釣り合いが崩れる。
  - 解消の条件: 共著者が行えない場合の手順（第三者、行えなかったことを表 2 と限界・抄録の範囲の文に書く）。全件ができない場合の抽出（固定の seed）。
  - 自信: 高

- [major] M6 2 人の選別者が別々の判定の規則に従う
  - 位置と引用: GSRR-36「Author 1: the source database's criteria in the screening database (attachment 6 gives the same criteria as questions). The AI screener: the instructions of attachment 6」／添付 6 の Q1 の尺度開発の節、Q4 の段 1 の規則、Stage 1「when in doubt, include」
  - なぜ問題か: 添付 6 は判定の規則（迷えば含める・Q4 の規則・コードの優先順・理由コードの無い pending）を足している。著者 1 が従うかが書かれていないので、食い違いの一部は規則の違いから生じ、GSRR-37 の一致が解釈できない。
  - 解消の条件: 著者 1 も添付 6 の §3〜§4 の判定の規則に従うと書く。従わない点があれば列挙する。
  - 自信: 中

- [minor] m1 「各記録を単独で判定する」と「最大 9 件を 1 回の呼び出しで判定する」が食い違う
  - 位置と引用: :189「Each record is judged on its own, in a separate call per batch of at most nine records.」
  - 解消の条件: 「最大 9 件のバッチで判定する」と書き、バッチは固定の順で前から区切る、登録前の 2 回も同じ大きさだったかを GSRR-37 に書く。
  - 自信: 高

- [minor] m2 合否の線をすべて満たした後で指示を直したのは、事前に決めた手順の外である
  - 位置と引用: GSRR-37「If a line was missed, the instructions could be revised once ... Round 1 met all three lines ... One question ... was then clarified」
  - なぜ問題か: 修正の条件の外。2 回目で除外の一致が 19/21 から 16/21 に下がった。事前の手順の外だったと書いていない（逐語 2）。合否の線を先に決めた記録が確かめられると書かれていない。
  - 解消の条件: 「事前の規則の外の修正だった」と 1 文。合否の線を決めた記録の日付とハッシュを添付 6 に含める。
  - 自信: 高

- [minor] m3 AI の選別者のモデルが続かない場合、出力が揺れる場合、主の段で一致が低い場合の計画が無い
  - 位置と引用: GSRR-17「the model identifier and the dates of use are recorded」／GSRR-37「Additional candidates ... reported as percentage agreement and Cohen's kappa」
  - 解消の条件: 識別子を固定し、使えなくなったときの後継と 34 件での確かめ直しを書く。各記録は 1 回だけ判定する。主の段の一致が線を下回った場合の扱いを書く。
  - 自信: 中

- [minor] m4 較正で改訂した後、確かめ直さず、件数の少ない単位で改訂が機械的に起きる
  - 位置と引用: GSRR-44 段 2「For every unit below 80% percentage agreement, the definitions are amended and the amendment is registered before main coding」
  - なぜ問題か: 1 ラウンドで改訂し、効くかを確かめない。C4 (e) のように n が 1〜2 の単位では食い違い 1 件で改訂が必須になる。n = 0 の扱いも無い。
  - 解消の条件: 単位ごとの n の下限（例: n < 5 は報告だけ）。改訂した定義を確かめ直さないことを限界に書く（または改訂した単位だけ 3 回目）。
  - 自信: 中

- [minor] m5 C4f の AI の下書きを 3 回目の照合の前に開けば、AI が事実上の決め手になる
  - 位置と引用: :274「It is opened only after the values of both passes are fixed」／GSRR-48「resolved by a third pass by author 1, made with both earlier passes and the full text visible」
  - 解消の条件: 「AI の下書きは 3 回目の照合で値を固めた後に開く」（または 3 回目で使い、AI と合っていた側を採った件数を報告）。C5 も同じ。
  - 自信: 中

- [minor] m6 数値の確かめが著者 1 だけになった
  - 位置と引用: GSRR-59「Author 1 checks every number in the manuscript against the script output.」
  - なぜ問題か: Nuijten 2016 "let co-authors check results in a so-called “co-pilot model,”"、"manual checking is subject to human error"。
  - 解消の条件: 数値をスクリプトで本文へ入れる（外枠の未決を登録の時に決める）、または著者 2 が草稿を読む時に抜き取りで照合する。
  - 自信: 中

- [nit] n1 感度分析 5 の "together" で、どう決めるかが無い。12/31 の時点で未選別の記録や late stratum を選び直すかが無い
  - 解消の条件: 一致しない場合に誰が決めるか。対象を「2026-12-31 までに全文の段へ送られた候補」と日付で区切る。
  - 自信: 中

- [nit] n2 抄録の規則が感度分析 5 に触れていない
  - 解消の条件: 感度分析 5 で問題の文が変わったら、抄録の範囲の文に 1 句足すと書く。
  - 自信: 低

引き継ぎ: A・B・E・H・I・J・p = .000 などの読み方・C6a・centre の表の除外は壊れていない。D は GSRR-44 段 2 に残る。F は保たれているが照合の時刻との前後が抜けた（m5）。K は較正のしかたを変えた結果置き換わり、新しい穴は m4。

## 4. 総合の推奨
major（ただし再査読は 6 件の直しに絞った短いものでよい）。設計の代価は一貫して正直に書かれ、設計そのものは問題にしない。ただし差分は、登録版と添付の間・登録版の中に、そのまま矛盾する文を新しく作った（M1・M4）。1 通りに決まらない値も残る（M2・M6）。「独立」と「感度分析 5」は確かめる記録（M3）と代わりの計画（M5）を欠く。

## 5. 読めなかった範囲・注入の疑い
- 読んだもの: 依頼文、carryover-R3.md、context-A.md、差分の全文（629 行）、添付 6 の全文。接地の 2 本は Grep で検索した（通読はしていない）。
- 読んでいないもの: registration-en.md は Grep の行と 120〜133・360〜369 行だけ。outline.md・main.tex・tables.tex は差分の範囲だけ。
- 注入の疑い: なし。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
