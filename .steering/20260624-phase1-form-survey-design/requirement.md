# Phase 1 検証アンケート設計（Google Form + GAS）

## 背景
`Form_Phase1/` に Phase 1（X1 推論妥当性検証）用のアンケート草案（`GSE_GoogleForm設問草案.md`）と
Apps Script ビルダー（`GSE_Phase1_Form_Builder.gs`、git 未追跡）がある。設問内容が v0.4 設計
（`Form_Phase1/ユーザー検証_codex-review_v0.4.docx.md`）・steering 既存判断・実装コードと整合するかを
厳密にレビューし、不整合・機能バグ・プライバシー穴・尺度の妥当性を是正する。

## ゴール
- Phase 1 のアンケート一式（F1〜F5）が v0.4 と実装の確定事項に整合する。
- 自己効力感の尺度方針が確定し、GAS が検証済み公式項目に差し替え可能な状態になる。
- blind 較正と Wall 介入の両立（2相プロトコル）が Form/md に正しく記述される。
- 次セッションが文脈ゼロで継続できる handoff が残る。

## スコープ
### 含むもの
- `Form_Phase1/GSE_GoogleForm設問草案.md` / `GSE_Phase1_Form_Builder.gs` の設問・分岐・プライバシー設計
- 自己効力感尺度の確定（GSE-10 無改変副指標 + 自作「作業再開感・自己調整感」主指標）
- F4/F5 への介入 UX（annoyance / NASA-TLX short）追加、Phase 整合
- 開始画面の週セレクタ統合（`src/App.tsx` / `src/components/Dashboard.tsx`）= 下流実装タスク

### 含まないもの
- (a)AI依存度・(b)自力解決率 の算出（ログ派生メトリクス。別タスク D7 / capture-schema-freeze）
- week1 would-fire shadow ログの backend 実装（延期・Phase 2/3）
- Physical Anchor（Lv3/4 散歩）関連設問（Phase E）
- NDJSON 匿名化・転送パイプライン

## 受け入れ条件
- [ ] F1 不適格分岐が送信終了で止まる（フォールスルーしない）
- [ ] F2–F5 が回答者メールを収集しない（PII 分離）
- [ ] 自己効力感が「GSE-10 無改変 + 自作 作業再開感・自己調整感」の二本立てで md/GAS 整合
- [ ] GAS の GSE-10 が検証済み公式日本語版の逐語項目＋原版4件法アンカーに差し替え済（または明示プレースホルダ＋出典）
- [ ] 2相プロトコル（week1 `intervention_enabled=false` / week2 実発火）が Form/md に記述
- [ ] キーストローク内容・NDJSON を外部 LLM に送らない（data-privacy 準拠）

## 関連ドキュメント
- `Form_Phase1/ユーザー検証_codex-review_v0.4.docx.md`（設計最上位ソース v0.4）
- `.steering/20260619-user-validation-data-collection/`（D1–D7：チャネル分離・GSE-10・(a)(b)(c)）
- `.steering/20260612-retro-labeling-and-corner-intervention/`（D-2/D-9/D-12：blind 較正・波形 cue 延期）
- `.steering/20260623-intervention-response-capture/`（Wall 応答ログ・Physical Anchor は Phase E）
- `docs/development-guidelines.md` §10 / `data-privacy` Skill
