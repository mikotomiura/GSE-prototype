# 設計 —— gse-overview-and-concept

## アプローチ

1. 俯瞰（`overview.md`）: 分析 13 本の notes と ADR-040〜046 を読み、分析ごとに問い・データ・結果・言えないこと・使われた ADR を 1 ブロックで書く。続けて、分析をまたいで繰り返す結論と、食い違う読みを並べる。数字は notes の値を写し、要の値は notes で裏取りする。
2. 文書のずれ（`doc-drift.md`）: 上流の文書を、ADR-040〜046（3 状態の名前・Nudge・招待・停滞を主の対象に・段 1/段 2）と照らし、ファイル・行・ずれの種類・直す時期（議論の前に直してよい事実の誤り／議論の結果を待つ主張）に分ける。
3. 論点と案（`concept-options.md`）: 俯瞰から、コンセプトの柱ごと（問い・対象・推定の役割・介入・検証の形・少ない人数）に、今の決定・分析が示すこと・案 2〜3 つ・それぞれで変わる文書と次の仕事を書く。
4. codex-consult: 俯瞰と案だけを渡す（集計値だけ）。既知の未決の一覧を添える。
5. 研究者の決定: 柱ごとに AskUserQuestion で 1 問ずつ。decisions.md に記す。
6. 直し: 決定に沿って上流の文書を直す。ADR に当たる決定は ADR を起票する。

## 変更対象

- `.steering/20261105-gse-overview-and-concept/` の文書
- 議論の後: `docs/research-positioning.md`・`docs/wbs-verification-halfyear.md`・`docs/functional-design.md`・`docs/glossary.md`・`docs/architecture/gse-design-map.md` ほか（doc-drift.md の一覧のとおり）

## テスト戦略

コードは変えない。文書の確かめは、俯瞰の値の notes との照合・ずれの一覧の grep での再現・code-reviewer と /cross-review。
