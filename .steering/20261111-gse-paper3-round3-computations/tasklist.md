# タスクリスト

- [x] 条件 3 つと SEED をコードより前にコミット（51b7656c）
- [x] 計算 1 のコード・selftest（Mac で 6 門が通る）
- [x] 計算 2 のコード（run_add.py・sens_report.py の 2 群・足さないときの出力がバイト同じ）
- [x] 計算 3 のコード・selftest と変異（Mac で通る）
- [x] 計算 1 の複製 00 で P-REPRO を試す（値は見ない）
- [x] code-reviewer の指摘を直す → コードをコミット
- [x] 計算 1 の本計算（Mac・約 3.5 時間）
- [x] 計算 2 の本計算（Mac・約 8 時間）
- [x] 計算 3 の職場の PC への引き継ぎ（push は研究者に確かめる）
- [x] 計算 1・2・3 の notes（読みの形の当て）・計算 3 は HP Z2 で回した（e9f77348）
- [x] Take-home と推奨の書き換え（判断 6）
- [x] /cross-review（Codex 込み・判断 8）
- [x] 目的と休止の集計のコードの /cross-review（Codex 込み・判断 14）
- [ ] 計算の間に: 文献の調べ（T4）・結果に依らない外枠の直し（T8・T9・T10・言い回し）・意図の資料
- [x] 結果がそろったら外枠を直す（判断 6・7）
- [x] T4 の文献の一次の確かめ・カード・references・novelty の文（判断 9・Uto 2020 の評価の設計は未確認で Open items に残す）
- [x] context-B を今の外枠に合わせる（round 4 の下書き）
- [x] attack-me round 4〜7 を回した（判断 6〜13）。round 7 でメインの確かめで閉じた
- [ ] 本文を書く（paper-write）・その後に attack-me（stage manuscript）

## 本文の round 1 の計算 A・B・D（2026-11-12〜）
- [x] A・B・D の採否を研究者に問う（判断 17）
- [x] 条件 2 つと SEED をコードより前にコミット
- [x] A・B のコード・selftest と変異（Mac で通る）
- [x] D のコード・selftest と変異（Mac で通る）
- [x] /cross-review（Codex 込み・wrapper は本線から）と code-reviewer の指摘の採否（判断 18）
- [x] HP Z2 への引き継ぎを書く（push は研究者に確かめる）
- [x] HP Z2 で回す（A・B 38b4be20・D 57c902d6・B1 の対称版 de97bce5）
- [x] notes（読みの形の当て）: A・B 1e1ba8d7・D ff81c823・対称版 cffe96f3・判断 20
- [x] 本文の書き直し（判断 21・22・c9140726・9a4c1d34）・manuscript round 2（major・判断 23・0e5818b5）・round 2 の直し（7ac5bbb9）

## manuscript round 2 の後の計算 (f)（2026-11-13〜）
- [x] 設計を研究者に問う（6 問・判断 24）→ 条件と SEED をコードより前にコミット（1d82e941）
- [x] コード・selftest・変異（Mac・889ba260）
- [x] /cross-review（Codex 込み）と採否（判断 25）→ 直して selftest 11 門・変異 8 を Mac で通す
- [x] HP Z2 への引き継ぎ（next-session-gse-paper3-null-from-shared-run-on-hp-z2.md）・push は研究者に確かめる
- [x] HP Z2 で回す（c89be93f）・notes・本文の 4.4 ほかを直す（判断 26・R2）
- [x] manuscript round 3（major・判断 27・9ebccb21）

## manuscript round 3 の直し（2026-11-19〜・判断 27）
- [x] verdict §5 の 1〜9 の書き方の直し（要旨と結論で 2 つの値を分ける・比・限定・推奨を 2 つに・帰無の作り・本人側の割合・語の統一・細部を補足へ）
- [x] 最頻値との比べを 4.4 に 1 文・108 と 146 の食い違いを整える
- [x] 4.4 と 4.5 の入れ替え（方法の 3.5・3.6 も）・最初の帰無を 2 文・2 つ目の帰無の細部を S15 へ（outline.md の末尾に移した文を記録）
- [x] 方法の例の図（作った数）・組んで目で見た
- [x] 結論を 2 つに絞る・考察の第 1 段落に決定・Relation に Uto 型
- [x] Step 3b の言い換えの点検（paper-write/rewording-check-r3.md）
- [x] 語数を length-log に・警告 0
- [x] 数値の独立の照合（判断 22 の形・判断 28）
- [x] round 4 を回すかを研究者に問う（判断 29・回す）
- [x] manuscript round 4（対象 d6587f21・major・判断 30）

## manuscript round 4 の直し（2026-11-19〜・判断 30・31）
- [x] 書き方の直し 1〜11 を研究者に見せて承認（判断 31・全部）
- [x] A 決定を固定の平滑に限り推奨 (2) の版と並べる・失う精度の文・発見を考察の冒頭と結論へ
- [x] B 2 つ目の帰無の植えた差の下の振る舞いを 4.5 に
- [x] C 要旨の推奨に範囲の語・post hoc の括弧を 1 つに
- [x] Step 3b の点検（paper-write/rewording-check-r4.md）・語数を length-log に・警告 0
- [x] 数値の独立の照合（判断 31）
- [ ] manuscript round 5（本線の attack-me・round 4 の dir を土台に・Codex に既知の未決＋判断 30 の保留）

## manuscript round 7 の計算 A・B（2026-11-20〜・判断 37・38）
- [x] A・B の設計を研究者に問う（判断 38・全部推奨案）
- [ ] 条件を conditions.md に追記してコミット（コードより前）
- [ ] r7.py・selftest_r7.py・run_r7.sh を書き、Mac で selftest と変異を通す
- [ ] HP Z2 の引き継ぎを書く
- [ ] 結果 → notes → 本文の \PENDING → 数値の照合 → 削る → round 8
