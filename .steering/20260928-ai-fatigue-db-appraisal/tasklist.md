# タスクリスト

## 準備
- [x] ワークブック全 16 シートを読む（scratchpad `dump.txt`）
- [x] GSE の既存 AI 疲労調査を確認（[P361]〜[P376]・生成的返権論 §6.3・ロードマップ §5.7・09-16 / 09-19 の steering・文献カード）
- [x] 評価プロトコルを抽出結果の前に固定（`design.md`）

## 抽出（サブエージェント・Sonnet・並列 7 本・入れ子禁止・締切 25 分）
- [x] G1 AF001–AF005, AF034
- [x] G2 AF006–AF010（標本重複の比較表つき）
- [x] G3 AF011–AF014
- [x] G4 AF015–AF020
- [x] G5 AF021–AF024
- [x] G6 AF025–AF033
- [x] 検索漏れ点検（OpenAlex / Crossref・11 クエリ・ヒット件数つき）

## 判定（メイン）
- [x] 争点の一次をメインが自分で開いて確認（AF001 PDF / AF004・AF034・AF019・AF002・AF003・AF015 ブラウザ / AF006・AF008 PDF / AF011 Europe PMC＋再計算 / AF012 Wayback / AF014 PDF＋Crossref＋DOI handle / AF031 Crossref / AF005 HTML）
- [x] Claude適格性評価（34 件・中心-A/B の 2 段）
- [x] Claude方法論評価（34 件・JBI／COSMIN 項目）
- [x] Claude領域別評価（中心候補 13 件）
- [x] Claude照合事項（R-I01〜R-I15 再照合＋C01〜C19 新規）
- [x] Claudeスクリーニング案
- [x] GSE照合（34 件＋GSE 由来の追加候補 8 件）
- [x] 検索漏れ候補（141 件＋AF017 の引用追跡 4 件・題名段）
- [x] Claude×GPT比較

## 出力と検算
- [x] 新 xlsx を書く（元ファイルは上書きしない）
- [x] 元シート不変の機械比較（変異を入れて赤になることも確認）・必須列・コード値の検査
- [x] LibreOffice でコピーを再計算し、数式 110 個の値を確認（空は元の AI判定比較 E5:E38 の `""` のみ）
- [x] 反証役による 10 主張の再照合（偽の主張 1 件は否定・AF005 の項目文を逐語に修正）
- [x] decisions.md（判断 1〜8・逸脱 1〜5）

## 完了処理
- [x] アーカイブ（`archive/`・SHA-256 つき README）
- [x] worktree でコミット（4e3119a9）
- [x] security-checker（CRITICAL・HIGH 0。MEDIUM 1・LOW 2 を反映＝判断 10）
- [x] code-reviewer（CRITICAL 0・HIGH 2・MEDIUM 9 を反映＝判断 11）
- [x] /cross-review の Codex 系統 1 回目は予算ガードで skip（判断 9）
- [x] Codex レビュー 1 巡目（日付が変わり当日分が 0 に戻ったため上限の引き上げは不要だった・81,940 tokens・P1 1・P2 5 を反映＝判断 12）
- [ ] Codex レビュー 2 巡目（今回足した規則の境界条件）
- [ ] 出荷フロー（push → PR → CI → merge）
- [ ] 研究者へ報告（限界を含む）
