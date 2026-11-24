# 判断

## 判断 1: other-research の版と UMUAI の教訓を同じ枝で統合する（2026-11-25・研究者の選択・推奨案）
- GSE の paper-write / attack-me は 3 つの版に分かれていた: main（36f9952b 系）・この枝（範囲の門）・other-research（11-18・11-24 の段・範囲の門なし）。
- この枝は origin/main から 3 コミットだけ進んでいる（一度「main と関係ないコミットが 79 本混ざる」と研究者に伝えたが、手元の main が古かったための誤り。origin/main と比べて訂正した）。新しい枝は切らず、この枝に積む。
- paper-write は other-research の版を土台にし、`<PJ>/` を外し、目的の memory の参照と Chrome の手順を戻し、範囲の門の段・結論の 1 行・チェックリストを戻した。GSE の版にだけあった「方法の具体例は作った数で・実在の人の値を使わない」を具体例の項に足した。
- attack-me は枝の版を土台にし、other-research の実質の段（観点 7・8、context-A の優先、E の接地・見ること 1・7・8・9・出すもの 2b・3・4、Step 4 の写し、チェックリスト）を足した。other-research で一般化された語（`.claude/external-skills.md`・Codex を任意に）は GSE の版の語のまま。
- UMUAI の教訓: paper-write の目的の段・Step 1「中心の問いへの答え」・Step 4、attack-me の観点 9・E の見ること 10・Step 4・Step 5。
