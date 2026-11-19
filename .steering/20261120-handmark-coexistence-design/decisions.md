# 重要な設計判断

## 判断 1: 土台と形（2026-11-20）

- 土台: S-CX の枝（ed43c6b9）から docs/handmark-coexistence-design を切る。設計案がカードの [P594]〜 を引くため。
- スライド: 既存の 4 本と同じ形（tpl・Klee One・deckkit・手描き風の図）。テンプレートは研究者の指定の c:\deck-temp\deck_temp.pptx（既存の tpl.pptx と同じ系統か確かめる）。PDF は、この Windows 機に PowerPoint が無いので LibreOffice で書き出す（Mac の先例は Keynote）。
- 名前: GSE_handmark_design.pptx / .pdf（既存の GSE_project_*.pptx に合わせる）。

## 判断 2: 見て直したこと（2026-11-20）

- Windows で組んだ。Klee One はユーザーのフォント（GSE_DECK_FONT で sketch.py に渡す）。PDF は LibreOffice で書き出し、pypdfium2 で画像にして 4 枚ずつ見た。Klee One は正しく出た。
- 直したもの: 名前の衝突の図の下の 2 行が箱に重なった／場の図の説明が草に重なった／「≥」が Klee One に無く □ になった（「以上」に）／「4 つの問い」の題が折り返して本文に重なった（題を短く）／カードの下が空いた（既存のアイコンを入れた）／「進める順」の図が小さかった（要点と注を足した）／反証のスライドで表の枠が全幅でグラフに重なる組み方だった（右だけに置いた）。
- 内容の直し: 日の問いの項目案が 4 つで、ADR-048 D3 の「2〜3 項目・10 秒ほど」を超えていた。中心を由来の判断と感じの 2 つにし、反証の側は候補とした（設計案 §5 と図）。
- Drive: G:\マイドライブ\Doe_Systems\Reserch_production\GSE\slides に GSE_handmark_design.pptx と .pdf を置いた（既存の 4 本と同じ形）。
