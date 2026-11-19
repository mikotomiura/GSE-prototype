# 重要な設計判断

## 判断 1: ラウンドの決め事（2026-11-20・研究者が AskUserQuestion で選択）

- 土台: 未マージの S-EA の枝（docs/expression-audit-literature・cc9150d4）から docs/handmark-coexistence-survey を切る。採番は P594 から。
  - 理由: S-EA が P555〜P593 を使っており、main から切ると欠番で check_citations が赤になる。S-EA の [P555]〜 を本文から引ける。
  - 却下案: main から切って P594 から（S-EA が入るまで赤）／S-EA を先に main へ（待ちが生じる）。
  - 失うもの: この枝の PR は S-EA の PR の後にしか merge できない。
- 予算: 計 10 本（Sonnet・並列・入れ子なし・各 25 分）。問い 1 に 4 本（名前の衝突の確認を厚くする）、問い 2・3 に 2 本ずつ、問い 4 に 2 本（どちらも反証の向き）。
  - 却下案: 計 8 本（推奨だった）・計 4 本。
- 下位の問い: 4 つ（requirement.md のとおり）。
- 用途: ランドスケープ把握（名前の衝突の確認）。gate 判定ではない。

## 判断 2: 取れない本文は Chrome で読む・重複を詰める（2026-11-20）

- 出版社のサイト（Cell・SAGE・MDPI・ACM）は WebFetch で 403、ブラウザを装った一括取得は自動モードに止められた。研究者の指示（「fetch・subagent で取れなかったものは Chrome でとろう」）で、Chrome の javascript_tool で本文から必要な文だけを抜いた（[P594] [P595] [P596] [P602]）。
- サブエージェントが新規と報告した Hale & Hamilton 2016 は既登録の [P531] だった（check_citations の key 重複で捕捉）。未コミットのうちに P617 の行を落とし、カード・索引の [P617] を [P531] に付け替えた。新規は P594〜P616 の 23 件。
- 登録しなかったもの: 書誌か抄録が確かめられないもの（Fukuda & Ueda 2010・Bailenson ら 2008・Ravid ら 2020・Fribourg ら・Liu ら 2025 など）。I/O Bits として報告された DOI は Laina で、使わない。
