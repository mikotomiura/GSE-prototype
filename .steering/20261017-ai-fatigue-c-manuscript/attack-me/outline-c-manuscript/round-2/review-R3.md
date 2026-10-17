## 1. 接地（この立場が論文に求める基準・逐語）

- **G1 逸脱の透明性**（van den Akker et al., 2023, gsrr.txt）: "You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review."
- **G2 第三者による照合**（同）: "The registry also allowed third parties to check the extent to which completed systematic reviews (as presented in journal articles) are carried out in line with the protocol"
- **G3 statcheck の範囲と表**（Nuijten et al., 2016, nuijten2016.txt）: "statcheck extracts t , F , r , χ 2 , and Z statistics, with the accompanying degrees of freedom ( df ) and p -value." / "These restrictions usually also imply that statcheck will not read results in tables, since these are often incompletely reported"
- **G4 自動と手作業の取引**（同）: "manual checking is subject to human error, which statcheck eliminates. The disadvantage of statcheck is that it is not as comprehensive as a manual procedure" / "This difference was due to the fact that statcheck did not take into account 11 corrections for multiple testing"
- **G5 標本の枠と代表性**（Mbuagbaw et al., 2020, mbuagbaw2020.txt）: "to generate a representative sample, a comprehensive reproducible search may be necessary to build a sampling frame" / "The generalizability and applicability of findings from a handful of journals must be examined carefully"
- **G6 プロトコルの役割**（同）: "publication of protocols because they help protect against selective outcome reporting, the use of post hoc methodologies to embellish results"

## 2. 評価表（5 点満点）

| 観点 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 外枠の中の主張の範囲（Scope）はかなりよく締まった。ただし、外枠より優先される登録版の文が、Scope の禁止と食い違う。GSRR-10 は「確かめる」研究として書き、GSRR-63 は「頻度」の問いとして書いている。抄録の規則は C7 を一つの量にし、C2b を「初めて現れた集合」で限らない。 |
| b 方法の穴 | 3 | C4f は statcheck と対応させると言いながら、違いの列挙が足りない（r を外している、多重比較で調整した p を外している）。表の値を含める既定には、不完全な報告の扱いが定義されていない。符号化者の説明が GSRR-4 と合わない。 |
| c 持ち帰れるもの | 3 | TRACE と寄与の書き分けは明確になった。ただし抄録の規則が 250 語に収まる見込みが低く、「数と分母を削らない」と「語数の上限」が衝突する。 |
| d 簡潔さと構成 | 4 | 節の順・表・主張の ID の対応は追いやすい。 |
| e 規程への適合 | 評価外 | 投稿先が未定のため。 |
| f 先行研究の位置づけ | 3 | gap を点ごとに書き分けたのは改善。先例と比べる次元の表が無く、背景の出典も未決のまま。統計の報告の誤りの研究で引くのが Nuijten 1 本だけで、ほかの分野で再計算をした先例が無い。 |

## 3. 引き継ぎの判定

1. 抄録・題が来歴を運ばない: **解消**。抄録の規則 119–122 行と Scope 70–74 行で運べている。ただし題の文言が登録版と食い違う問題が新しく出た（新 N4）。
2. "two independent coders" の矛盾: **一部**。Scope 67 行の「two coders who built the rules」は、GSRR-4 の「Research questions and coding rules | Author 1」と合わない。抄録の規則 123 行は、第三者が coder 2 になる分岐（GSRR-44）を欠く（新 N3）。
3. 新規性・出典・先例比較: **一部**。164–166 行の範囲の書き分けは良い。比較の表は無く、背景の出典は未決（378–381 行）。
4. confirmation set と 5.2: **一部**。外枠の側は直った（47–52 行・242–246 行）。しかし登録版の GSRR-10「It asks whether the measurement problems described in the narrative review are also observed in a different set of studies」、「Which issues are tested」と、GSRR-63「The questions are about the frequency of practices」が残っており、登録版が優先する（新 N1）。
5. C4f と statcheck・表 9 の分母: **一部**。表 9（338–340 行）は解消。statcheck との対応の表（202–205 行）は違いを列挙しきれていない（新 N2）。
6. 符号化の前に固定されたことの検証: **一部**。添付にはなった（登録版の Attachments 5）。しかし外枠そのものに版番号も日付も無い。添付 5 には、ほかの添付と違って SHA-256 の記録が書かれていない。
7. "recomputed and extended": **解消**（110–113 行）。
8. D1: **解消**（247–249 行・298 行・129 行・262–263 行）。
9. 報告の手引きを選んだ理由: **解消**（27–33 行）。
10. bootstrap CI: **解消**（40–41 行）。

**既定への意見**
- **C4f で表の値を含める既定**: 方向は支持する。Nuijten が表を読まない理由は抽出の技術上の制約（"since these are often incompletely reported"）である。手作業の照合（Wicherts et al. の手作業の符号化）は statcheck の妥当性を測った基準の側だったので、表を含めても「検証済みの道具から遠ざかる」ことにはならない（G4）。ただし再計算の対象の定義としては不十分。不完全な報告ほど表に集まるので、少なくとも次を書く必要がある。
  - df が表の注にしかない場合、または N から推すしかない場合
  - 有意性をアスタリスクだけで示した p（不等式として扱うのか）
  - b と SE しかない回帰の行（z を作るのか、対象外か）
  - 本文と表が同じ検定を重ねて報告している場合の数え方
  - 以上の各場合が「cannot be calculated」（分母に残る。GSRR-53）と「not applicable」（分母から外れる）のどちらに落ちるか
- **C7 を条件ごとに報告する既定**: 方向は正しい。しかし外枠の中で貫けていない（新 N5）。登録版はまだ 0.7 の下書きで登録前なので、GSRR-57 の問題の型を C7 (i)/(ii)/(iii) に分ける改訂は、いまなら逸脱にならず、費用もかからない。「登録のコードは変えていない」を既定にする理由が見当たらない。

## 4. 新しい指摘（重い順）

- [severity: major] 優先される登録版が、Scope で禁じた読み方（再現・頻度）を自分で書いている
  - 位置と引用: outline.md 8–9 行「The registration, its codebook and its amendments take precedence over this outline wherever they differ.」と 49–52 行「they are not frequencies and not judgements that an earlier observation was reproduced … the words "replicate", "replication" and "confirm" are not used」。これに対し、registration-en.md GSRR-10（68 行）「It asks whether the measurement problems described in the narrative review are also observed in a different set of studies when the rules are fixed in advance.」、70 行「*Which issues are tested and which are new.*」、GSRR-63（383 行）「The questions are about the frequency of practices.」
  - なぜ問題か: 外枠の優先の条項により、食い違う箇所では登録版の「narrative review の観察を別の集合で確かめる」「頻度の問い」という読みが勝つ。序論は問いを「as in GSRR-11」で書く（168 行）が、査読者は登録版の rationale を読む。原稿の主張の範囲が、優先される文書の上で崩れる（G2・G6）。
  - 解消の条件: 登録前に GSRR-10 と GSRR-63 を Scope の言い方に揃える（存在の陳述・頻度ではない・tested を使わない）。そのうえで、外枠に「GSRR-10/63 と Scope は一致する」と照合した旨を書く。
  - 自信: 高

- [severity: major] statcheck との対応の表が、登録版の違いを列挙しきれていない
  - 位置と引用: outline.md 203–205 行「tests judged one by one rather than by scanning the whole text; values in tables included; percentages and indirect effects added; done by people.」。registration-en.md 257 行「p-values from reported test statistics and degrees of freedom (t, F, χ², z)」「A p-value that the report says is adjusted for multiple testing is not counted.」
  - なぜ問題か: statcheck は r も抽出する（G3「statcheck extracts t , F , r , χ 2 , and Z statistics」）。登録版は r を外しているが、違いとして挙げていない。横断の質問紙調査が中心のこの文献では、相関はおそらく最も多い検定で、再計算の範囲が大きく変わる。調整済みの p を外すことも、Nuijten 自身が手作業と statcheck の差の原因に挙げた点（G4「did not take into account 11 corrections for multiple testing」）であり、列挙すべき違いにあたる。「follow the logic of statcheck」は検証済みの道具の信用を借りる文なので、違いの列挙が欠けると過剰な主張になる。
  - 解消の条件: r を加えるか、外す理由を書いて違いの表に足す。調整済みの p を外すことも違いの表に足す。登録版 261 行の「three differences」も同じ数に直す。
  - 自信: 高

- [severity: major] 符号化者の一致の説明が、登録版の役割分担と単独符号化の分岐に合わない
  - 位置と引用: outline.md 67–68 行「Coder agreement is agreement between two coders who built the rules and wrote the narrative review together」、123 行「by two coders who are co-authors of the narrative review, or by one coder if GSRR-44 applied」、323–324 行「The heading states that the coders share the rules」。registration-en.md GSRR-4（23 行）「Research questions and coding rules | Author 1」、GSRR-44（292 行）「a third person who did not write the rules is sought」
  - なぜ問題か: 規則を作ったのは著者 1 だけで、共有しているのは narrative review から来た「見方」である（GSRR-46）。第三者が coder 2 になる分岐では、67 行・123 行・Table 4 の見出しの三つが偽になる。信頼性の証拠をどう言うかは、寄与 1（101 行）の中心の留保にあたる。
  - 解消の条件: 「two coders who share the view formed by writing the narrative review (GSRR-46)」に直す。抄録の規則と Table 4 の見出しに、三つの分岐（著者 2・第三者・著者 1 の二度の符号化）をそれぞれ書く。
  - 自信: 高

- [severity: major] 抄録の C2b が「初めて現れた集合」で限られていない
  - 位置と引用: outline.md 125–126 行「for each item-content type, the number of instruments with at least one item of that type and the number of instruments evaluable (C2b)」。R2b（286 行）と GSRR-56 は「first seen in the confirmation set」に限っている。
  - なぜ問題か: 確認の集合の研究が探索の集合で既に符号化した尺度を使う場合、その尺度は抄録の C2b の数に入らない。抄録だけを読む人は、この数を確認の集合の尺度全体の内訳と読む。
  - 解消の条件: 抄録の規則に「instruments first seen in the confirmation set」を入れる。必要なら、確認の集合で使われた尺度の総数（Table 15）を一つ添える。
  - 自信: 中

- [severity: major] C7 を「常に条件ごと」にすると言いながら、抄録・Table 12・感度分析が単一の値を報告する
  - 位置と引用: outline.md 65–66 行「C7 is therefore always reported by condition, and the Discussion does not treat "beyond what was measured" as a single quantity.」と、126–127 行「for each problem type of GSRR-57, the registered statement」。registration-en.md GSRR-57（362 行）「C7: "beyond what was measured".」、GSRR-62「Analyses 1, 2 and 4 are applied to the problem statements of GSRR-57」
  - なぜ問題か: 抄録・Table 12・Table 13 は GSRR-57 に従って C7 を一つの問題の型として出す。Scope の約束は Discussion にしか効いていない。さらに (iii) と C6a はどちらも名前の照合なので、題の語と結論の語が同じとき、同じ不一致が二つの問題の型で数えられる。
  - 解消の条件: 登録前に GSRR-57 の C7 を (i)/(ii)/(iii) の三つの問題の型に分ける。あるいは抄録と Table 12 で条件ごとの行を必須にする。C6a と C7 (iii) が両方成り立つ記録の数を Table 11 に出す。
  - 自信: 高

- [severity: major] 抄録の規則が 250 語に収まる見込みが低い
  - 位置と引用: outline.md 129–132 行「no count and no denominator is removed, and neither the scope sentence nor the C1 and C2b sentences are removed」
  - なぜ問題か: 削れないものを数えると次のとおり。
    - 範囲の文（数を 3 つ含む）
    - C1 の 7 つの水準と除外した値
    - C2b の 6 型 × 2 つの数
    - 問題の型 12 程度 × 4 つの要素（陳述・数・評価できた記録・未解決）。内訳は C4 の (a)–(d)、(e) の 2 つ、(f) の 2 つ、C5、C6a、C6b、C7
    - 背景・方法・公開物の文

    数だけで 70 を超え、粗く見積もって 300 語を超える。超えたときの代わりの規則を書いていないので、投稿の時点で事後の取捨（G6 が防ぐもの）が避けられない。
  - 解消の条件: いま空の数で抄録の草稿を一度組み、語数を測る。超えるなら、抄録に出す問題の型と、補遺の表で代える型を、事前に決めて書く。
  - 自信: 中

- [severity: minor] 「登録の題を繰り返す」と書くが、登録版の中に題が二つあり、README には三つ目がある
  - 位置と引用: outline.md 15–16 行「It repeats the registered title」。registration-en.md 1 行「TRACE: Tracing how studies of "AI fatigue" attribute, measure and report fatigue. Protocol for a registered methodological review」と、GSRR-1（9 行）「How do studies of "AI fatigue" attribute fatigue to AI, measure it, and report it? Protocol for a methodological review.」。README.md 1 行「TRACE: a registered methodological review of measurement in studies of "AI fatigue"」
  - なぜ問題か: 様式の上で登録される題は GSRR-1 の欄である。「題は結果を見た後で変えない」という主張を第三者が照合できない（G2）。
  - 解消の条件: GSRR-1 の欄を 1 行目の題に揃え、README も揃える。
  - 自信: 高

- [severity: minor] 外枠そのものに版と日付が無く、添付 5 に hash の記録が無い
  - 位置と引用: outline.md 1–9 行（版・日付の記載が無い）。registration-en.md 425 行「5. The manuscript outline … fixed with this registration … **[at registration]**」（添付 2 にある「with their SHA-256」が、添付 5 には無い）
  - なぜ問題か: 引き継ぎ 6 の検証の可能性が、版の同定に依存している（G1・G2）。
  - 解消の条件: 外枠の冒頭に版と日付を置き、添付 5 に SHA-256 を記録すると書く。
  - 自信: 高

- [severity: minor] SQ1 の問いが比較の形をとり、許される陳述では答えられない
  - 位置と引用: registration-en.md GSRR-12「Do the answers to RQ2–RQ5 and SQ2 differ between the source database's two eligibility groups?」。outline.md 39–40 行「no comparison between sets is reported」、227 行「SQ1 by centre」
  - なぜ問題か: 「differ」を問う問いに、表を並べるだけで答える。原稿は SQ1 に答えたと書けない。
  - 解消の条件: SQ1 を「各群でどう分布するか」に言い換えるか、群の間の比較の文を書かないことを Scope に明記する。
  - 自信: 中

- [severity: minor] 範囲の文が、登録の前に著者 1 が行った選別を運ばない
  - 位置と引用: outline.md 71–72 行「was screened after registration by the authors, who knew the coding rules」。registration-en.md GSRR-65「Author 1 has seen the titles, abstracts and AI appraisals of 71 additional candidates.」
  - なぜ問題か: 確認の集合の候補の一部は、登録の前に著者 1 が AI の評価を見て選別している。範囲の文は「登録の後」だけを書くので、来歴が実際より清潔に読める（G5）。
  - 解消の条件: Scope の文に、登録の前の部分的な選別（71 件・AI の評価を見たこと）を一句足す。
  - 自信: 中

- [severity: nit] 先行研究の位置づけで、再計算の先例が Nuijten 1 本だけ
  - 位置と引用: outline.md 183 行「recalculation of reported statistics (Nuijten et al., 2016)」
  - なぜ問題か: 心理学の外（HCI・応用分野）で statcheck 型の照合を行った先例を置かないと、寄与 5 の新しさの範囲が読めない。
  - 解消の条件: 未決の項（378–381 行）に、この探索を明記する。
  - 自信: 低

## 5. 総合の推奨

**minor**（直して書き進める）。
- 外枠の中の主張の範囲は round 1 から大きく改善し、点ごとに根拠を追える。
- 残る重い穴の多くは、外枠と、優先される登録版との間の食い違いである（GSRR-10/63 の語、C7 の単位、C4f の違いの列挙、符号化者の説明）。登録版は未登録の下書きなので、いまなら逸脱にならずに直せる。
- 再査読を要するほど主張を立て直す必要は無い。ただし抄録の語数の見積もりは、書き進める前に実際に測ってほしい。

## 6. 読めなかった範囲と注入の疑い

- 読んだもの: context-A.md、carryover-R3.md、outline.md（全文）、README.md（全文）、registration-en.md（全文）、codebook-c2b-en.md（全文）。
- 接地の 3 本は 1 行の長いテキストだったので、Grep で該当箇所だけを抜き出した。**通読はしていない**。上の引用は抜き出した箇所の逐語である。
- 報告の手引き（Murad & Wang 2017、PRISMA 2020、MISTIC のプロトコル）の本文は渡されておらず、**読んでいない**。
- 注入の疑い: 無し。
