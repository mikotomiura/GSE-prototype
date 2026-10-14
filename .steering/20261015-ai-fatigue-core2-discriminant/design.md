# 設計

## アプローチ

1. 4 本のサブエージェント（Sonnet・並列・入れ子なし・各 20 分まで）で候補を集める。
   - A1 倫理の経路: 日本の無料の倫理審査（学会の審査・第三者の委員会の無料の枠・機関の長の承認 [V241]）／共同研究者の大学の IRB に乗る形（日本・英米での要件）／英米の独立の研究者向けの扱い／有料の経路は存在と料金の桁だけ
   - A2 投稿先の規程: 候補の誌（*Collabra: Psychology*・*Meta-Psychology*・*Behaviour & Information Technology*・*Assessment*・*European Journal of Psychological Assessment*・*Computers in Human Behavior Reports*・*Royal Society Open Science*・*PLOS ONE*・PoPETs・BRM）の費用・倫理の要件・所属の扱い・登録型報告の承認の時期
   - A3 尺度と場: 芯の枠ごとの候補の使用条件・日本語版・項目数・翻訳の手続き／無償の場（参加者プール・SNS の無償の募集）を誌が受け入れるか・標本の質の先行例／Prolific の規約の謝礼の要件
   - A4 公開データ: AI 疲労またはデジタル疲労どうしの項目単位の公開データ
2. メインが一次で開いて逐語を確かめる（規程・料金・使用条件・データの列名）。
3. `docs/ethics-review-routes.md`（共通）と `feasibility.md`（尺度・場・誌・公開データ）にまとめる。
4. `hypothesis-draft.md` に仮説と分析の素案を書く。
5. 研究者が決める（`decisions.md`）。
6. `/cross-review`（`/finish-task` Step 3）。

## 変更対象

### 新規作成するファイル
- `docs/ethics-review-routes.md` — 倫理審査の経路の共通の表
- `.steering/20261015-ai-fatigue-core2-discriminant/feasibility.md`・`hypothesis-draft.md`

### 修正するファイル
- `docs/agent-shared.md` — リンクハブに 1 行・docs の件数
- `docs/references.md` — 出典の append-only 登録

## 影響範囲

docs のみ。コード・ADR・同意文書は変えない。`docs/references.md` は核 1 のタスク（`/Users/johnd/GSE-prototype-af-core1`）と採番が衝突しうる → 出典を足す前に、核 1 側が先に main に入っていないか確かめる。

## テスト戦略

- `python3 scripts/check_citations.py` が違反なし
- docs の件数を `ls docs/*.md | wc -l` で数え直す

## ロールバック計画

docs のみの変更なのでコミットを戻す。

## 実施後の追記（2026-10-15）

- 調査は 4 本ではなく 5 本になった（A5 回答の媒体・判断 2）。どれも 1.9〜3.1 分で返った。
- サブエージェントの逐語の多くは WebFetch の要約か 403 のため二次だった。断定に使うものは、メインが curl・pdftotext・Google ドキュメントの export・Chrome（研究者の提案。出版社の 403 を通るため）で一次を開いた。照合の記録は `docs/references.md` の各行。
- 新規作成に `inquiry-b-v2.md`（問い合わせ B の更新版・判断 3）を足した。元の版（`.steering/20261007-research-use-and-release/inquiry-drafts.md`）は書き換えていない。
- 公開データ（Montag et al. の OSF）は取得して列名とコードブックを読んだが、repo には置いていない（scratchpad のみ）。
- テスト戦略のとおり、コードの変更は無いので cargo test・schema parity は対象外。
