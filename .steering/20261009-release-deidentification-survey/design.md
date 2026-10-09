# 設計: サーヴェイ 1 ラウンドの回し方

- 手順の SSOT: `.claude/commands/literature-review.md`（Step 0〜9）。
- 名前空間: **V**（検証方法論・データの公開の方法論）。[V243] から採番。
- 探索: 下位問いごとに 1 本、計 4 本の subagent（`general-purpose`・`model: sonnet`・入れ子禁止・締切 20 分）を
  1 メッセージで並列に投げる。反証 angle を各本に含める（例: 公開しても問題が起きなかった先例・加工が効いた例・攻撃が失敗した例）。
  生の出力は scratchpad（`$CLAUDE_JOB_DIR/tmp/survey/s1–s4.md`）。
- 一次の確認: 断定の根拠にする逐語は**メインが自分で開く**（WebFetch・PDF は pypdf）。有料の本文は使わない。
- 3 票の検証: 内的妥当性 / 外的妥当性（GSE の KeyCategory・n 3〜5・日本語 IME への外挿）/ 頑健性（反証・出版バイアス）。
- `references.md` への追記はメインが直列で行う。
- 検査: `python3 scripts/check_citations.py` を「違反なし」まで繰り返す。
