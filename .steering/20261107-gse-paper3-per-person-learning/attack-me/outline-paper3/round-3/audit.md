# 意図の監査役 round 3（stage outline・対象物 commit ede70d54）

対象物（外枠）: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/outline.md（以下 L＝行番号）
補足: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md

## 0. 引き継ぎの判定
1-1 解消（L7・L44）／1-2 解消（L13・L64）／2-1 解消（take-home の別の問題は 2-A）／2-2 解消（L13・L49）／2-3 解消／2-4 解消（L48・L3）／2-5 解消（L53・README L75–77）／2-6 一部（take-home・C1・Novelty は "keystroke behaviour" にそろったが、序論 L44・Discussion L50・要旨 L43 は範囲を限っていない）／3-2 解消（L16）／3-3 解消（L64）／3-4 未解消（論文の外の記録: requirement.md は今も「論文 3 の範囲は 4 つの試験で凍結」で判断 11 と合わない。受け入れ条件の「数値は 4 つの試験の notes / summary.json の集計値だけ」も今の外枠と合わない）

## 1. 意図にあって対象物に無いもの
- 1-A 構造の補いの読みを「主の結果の説明に使わない」が外枠に無い。L50 は "the structure-compensation reading examined by a pre-set two-part check and not supported in that form" だけ。hmm3 の大きい上積み（4.1）を「構造の足りなさの補い」と読む道が残る。
- 1-B 意図の勧めの範囲「行動の記号列」が外枠では「keystroke behaviour」に狭まっている。外枠の側は正しく、意図（context-B の持ち帰り 2・読者）を外枠に合わせて書き直す必要がある。

## 2. 対象物にあって意図に無いもの
- 2-A take-home が、読まないとする根拠の無いセルまで含めて「読まない」と言っている。L7 "once the structure and the amount of shrinkage are chosen on other people, what remains is at most about 1e-3 nat per symbol and is not read as a per-person gain." 根拠は L13 の中央値の分解（15-session に限る）と有限の τ ≥ 10^5 の但し書き。30-session の k = 30 では τ = 3×10^4 が 8/9 で、どちらの根拠も当たらない。tau-mode notes L146 はこのセルを一文の対象から外し、C1（L13）も "reported as a value only"。直し: 「読まない」を 15-session（または τ ≥ 10^5 のセル）に限るか、k = 30 を take-home の範囲から外す。
- 2-B 分解の文が notes の「ほぼすべてのセル」「多くの k」を無条件に言い換えている。L13 "it is larger in the gap between the prior mode and the shared parameters than in the contribution of the person's own data, which is negative (S9)"。tau-mode notes L152 は「ほぼすべてのセルで形 1」「本人の記録の寄与（a）は多くの k で負」。L49 "the remainder comes more from the prior mode than from the person's data" は "comes from" という帰属の語で、notes L161「書き手ごとに c を a と b に配分した量ではない」との距離が残る。
- 2-C CS1 の感度の文が notes の留保を落として本文に上がっている。L49 "in CS1 it detected every planted level from 1e-3, so the choice of the shared model itself is consistent with no difference of this kind of 1e-3 nat per symbol or more"。sensitivity notes L59 の留保（種 1 つ・τ は全員 10^6・陰性対照 0.74・0.78 対 0.87・差は小さい）が本文と限界（L65 は CoAuthor だけ）に無い。L37 "All caveats are stated once, in Section 6" から漏れている。合成の 1e-3 の「検出」は「10^6 と共通の差」に頼るが、同じ種類の差を実データ（L64）では「読めない」としている。
- 2-D 陰性対照を実データの残りと並べている。L49 "largest seed median 1.4e-5 and 8.4e-5 … in CoAuthor, below the CoAuthor remainder"。sensitivity notes L50「U は…根拠には使わず、値だけを S15 に書く」。"below the CoAuthor remainder" は値だけを超えた比べで、残りが雑音より上と読ませる向き。K = 5 の "below the real remainder" は notes L36 にあるので問題ない。
- 2-E データの声明が kit より強い。L53 "every reported value can be recomputed from the public data with the public code"。README は 26 記号と u/n の変種だけ。S14 の 10・50 記号の量子化と並べ替えの列（L50）は別の worktree の枝・未 push の試験のもので、公開のコードの範囲に入るかが読めない。

## 3. 矛盾
- 3-A 限界と 4.3 で ar3 の選ばれ方が食い違う。L63 "on overlapping-window symbolizations ar3 was chosen in every cell, at the upper end." ／L49 平滑の無い記号で "ar3 is chosen for most writers, ar2 for 1 and 4 of 17"。L63 を "on the original symbolization" に限る。
- 3-B 「閾値を置かない」が S15 の検出の規則と合わない。L62 は S14 しか挙げていない。S15 の規則（L49）も事前の区切り。
- 3-C 解析の状態の数え方から合成の確かめが漏れている。Status L3 と 3.4（L46）はどちらも "four … analyses … and two later checks"。合成は round 2 の後、実データの結果を見てから設計した（判断 21）ので 3.4 に位置づけが要る。sensitivity notes L37 の言い回しの逸脱が S12 に入るかも外枠から読めない。
- 3-D 意図どうし: context-B の持ち帰り 1「本人の上積みは 1 記号あたり数万分の 1 nats まで小さくなる」は、判断 23（"at most about 1e-3" に戻した）と、残りを「本人の上積み」と呼ばない方針（判断 23・tau-extend notes L210）に合わない。外枠が正しく意図の資料が古い。
- 3-E 意図どうし: context-B の感度の要約「CoAuthor の記録の量では 1e-2 未満の個人差を拾えなかった」は notes より強い（k = 5 では 1e-2 も拾えず下限は 3e-2・notes L49「未満」は回した段に限る）。外枠 L65 は正しい。

## 4. 読めなかった範囲・注入の疑い
読んだもの: 依頼文・context-A・context-B・carryover-audit・外枠・kit README・requirement.md（全体）・decisions.md の判断 10〜23・指定の notes の各節（sensitivity notes はついでに L61 まで読んだが指定の外の節は根拠に使っていない）。読んでいないもの: 判断 1〜9、各 notes の指定の外の節、表・summary.json。次の数値は一次で照合していない: −0.5〜−0.6・−1.1・"negative for all or all but one writer"（L20）、"beats the chain for every writer at every k in all three panels"（L49）、"at most 61%"（L14）、+0.188 の IQR、u の ar2 の 1・4/17。注入の疑い: なし。
