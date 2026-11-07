# review-R1（outline round 2）
接地: Guo ら 2020 脚注 2「A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility. Because they laboriously enter text letter by letter, poor typists may have many long pauses between keystrokes that are not indicative of planning behavior.」・4.4「Figure 5 shows that Group 1 and Group 3 are quite comparable in typing speed.」・4.2「we conducted a 4-state vs. 3-state Semi-Markov model comparison …」・5「we used relatively simple heuristics to define our writing states …」・Li & An 2026「The non-hierarchical mixture model may enlarge the standard error when the number of events in that component is small」「establishing feature consistency is an initial first step …」「imagine that a student paused 10 s when he was spelling “pen.” …」
carryover: 解消 7・一部 3（θ の族は持ち帰りといちばん強い主張でまとめたまま・読者が引く比べは同じ記録の組だけで 25% に届かない・Guo ら 2020 の個人化の先例と 3.3 の表）。
評価表: a 3・b 3・c 4・d 4・e 4・f 3。
指摘:
- [major] 本人の分位の θ では停滞の率が打鍵の量（流暢さ）に比例する成分を持ち、得点との正の関連はそれで予測できる。固定 θ の負は遅い書き手の長い間隔で予測できる（Guo 2020 脚注 2）。そうなら逆の結論は恣意性でなく別の量を数えている証拠。解消: (i) 89 通りで書き手の率と 1 時間あたりの押下の数の順位相関を [記述] で出し、押下の率を固定した偏相関か参照の線を図 2 に、または (ii) C1 を「族によって停滞の率は打鍵の量にも遅さにも寄り、得点との関連の符号はそれに従う」に書き換える。群の比べではないので不採用の範囲に入らない。自信 中
- [major] 見出しの CS1 の 2 年版の比の逆転は 25% に届かず、固定 θ に偏り、年版の打鍵の速さの違いを点検していない。解消: 届かないこと・18/20 が固定 θ を書く・2 年版の打鍵の間隔の分布を集計値で 1 文・持ち帰りの主語を得点との関連へ。自信 高
- [minor] 基準 −0.06 はほぼ 0 で「逆の結論」は大きさを過大に伝える。解消: 大きさを主に・題を diverging などに。自信 中
- [minor] 定義ごとに書き手あたりの停滞の数が違い、率の信頼性が違うので相関の大きさの幅に混ざる。解消: S3 に書き手あたりの停滞の数の中央値か 0 件の割合の列・4.1 に 1 文。自信 中
- [minor] 課題文ごとの相関の扱いが外枠に無い。解消: 課題文の中でも正負の向きが同じかを 1 文。自信 中
- [minor] 3.3 の根拠の表が振った水準と合わない（作文の 2 秒は θ に無い・固定 10・30 秒の先例が見えない）。解消: 各水準に先例を 1 つずつ・無い水準を除いた数を S3。自信 中
- [minor] この誌の直接の先行（Guo ら 2020 の個人化閾値と速さの比べ）と指標の一貫性の流れが無い。解消: 柱 2 に Guo ら 2020・C4 を feature consistency の流れに 1 文。自信 中
- [nit] C3 の「頻度は条件つき（組の 2 割弱）」は「63 のうち 11」と数で。自信 低
総合: major（見出しの 2 つの数がそれぞれ片方の θ の族から来て、各族が打鍵の量か遅さを数えている可能性を点検していない）。
読めなかった範囲: results の JSON・カード 2 枚・接地の参考文献の後半。指摘 1 の比例は検出器の実装を読まずに出した推論。注入なし。
