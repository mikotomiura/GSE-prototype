# round 2 — R2（推奨 minor）

接地: Conijn 2019（803–805 "caution should be taken when generalizing the effect of these features across tasks …"／26–27 "keystroke features are sensitive to small differences in the writing tasks at hand."／84–85 "The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions."）・Monaco 2018（17–18 "a temporal side channel leverages key press and release timings"／1124–1126 "mitigates the possibility of an attack under a specific set of assumptions, and not in general."／356–357 "64 Hz, or a 15.625 ms tick, is characteristic of the Windows family"）。

引き継ぎ: R2-1 部分的に解消（経路は時点ごと・弁は行を書く）・R2-2〜R2-7 解消・R2-8 部分的に解消（「does not depend on the kind of field」に根拠が無い・手順が実行できない）・R2-9・R2-10 解消。検算: 574/852/882・401/123/93・617・8 層・27 ブロック 429 試行・2,700 すべて合う。

評価: a3 b3 c2 d3 e4 f3 g3。

新しい指摘:
- [major] 他のアプリへ持ち出す手引きが根拠の無い主張と実行できない手順: §10.11「does not depend on the kind of field」— TSF では窓を出すかを入力欄が `BeginUIElement` の `pbShow` で決める（kit の参照も tsf.rs 470–474 で TRUE にしている）。UILess のアプリでは窓が出ない可能性。パイロットは観測の行を読んでいない。`kit/pilot/README.md` の手順は参照入力欄でしか実行できない。予測候補を切った環境ではセッションの始まりが変わる。→ 主張を削り、(a) 窓を表示させる入力欄でだけ見えること（未検証）、(b) 既定の設定に条件づけられること、(c) 読者にできることを率直に。自信 高
- [major] 問 4 の Windows の判定は、Windows のログにしか無い修飾キーの行（と離鍵の行）を評価しない（計画は Shift を送らない・§7 "modifier keys, which no plan of this study sends"・keyboard.rs l.4 は離鍵も書く・closed_set.py は押下だけ）→ §10.7 Question 4 に、推奨は修飾キーの行と離鍵の行を除いた key 行についてだけ言えると 1 文。自信 中〜高
- [major] 観測器の経路は時点ごとに切り替わり、行に経路が残らず、判定と報告の規則が事前に決まっていない（ime_winevent.rs 32–34・cloak.rs 105–106・20–23・main.rs 86・271–283）→ §10.3 に時点ごと・行に残らないこと・弁が ≈25 s の行を書くこと。§10.7 に run を単位にした判定の規則、§10.11 に混在の限界。自信 中
- [minor] 節番号の参照の古さ（data.windows.md・pipeline.py 988–989・262・scope_windows.py）。自信 高
- [minor] D4 の盲点が 2 つ足りない（観測の行が欠けた送出と人の押下の相殺・ポインタ・タッチ・ペン）。自信 中
- [minor] §10.9 の `cpu_all_zero` と `kit/e3/README.md` の矛盾。自信 中
- [minor] macOS の証拠が途中の commit。自信 低〜中
- [minor] Windows 11 Home での自動更新の一時停止と時刻同期の止め方が手順書に無い・cloak の経路が見る窓のクラス `IME` が本文に無い。自信 中
- [nit] key 行は離鍵も書く（「for each key press and release」）。
- [nit] 「10 of 10」と IMM を寄託しない理由の重複。

総合: minor。N3 の直しで観測器のコードに手を入れるなら major。

読めなかった範囲: 応答に列挙。一覧の外は開いていない。注入の疑い: なし。
