# 次セッション用 開始プロンプト

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。

---

## 依頼
`.steering/20260624-phase1-form-survey-design/` のタスクを継続する。
`requirement.md` / `design.md` / `decisions.md` / `tasklist.md` を読み、**今回の主タスクは #D（自作尺度の項目最終化）**。
あわせて #A/#B/#C の**最終化（人手照合・実機確認・cross-review・コミット）**まで進める。
実装系なので `/start-task` ではなく既存 steering を引き継ぐ。設計判断は憶測せずソース（v0.4 / decisions FD1–FD8）に当たる。
プレレジに関わる判断（採点法・仮説・α 目標）は**勝手に確定せず、ドラフト提案 → ユーザー確定**の順で進める。

## 真実源（先に読む）
- 本 steering 4ファイル（要件・設計・判断 FD1–FD8・タスク）
- `Form_Phase1/ユーザー検証_codex-review_v0.4.docx.md` §4.3（自作尺度の設計意図）/ §4.4（NASA-TLX）
- `Form_Phase1/GSE_Phase1_Form_Builder.gs`（`tseItems`＝buildF2 / `tsePost`＝buildF5。GAS は git 未追跡）
- `Form_Phase1/GSE_GoogleForm設問草案.md`（F2-C / F5 節）

## 前セッション（2026-06-24）の到達点
- **#A 週セレクタ統合**（`src/App.tsx`, git 追跡）完了。`PhaseWeek`/`PHASE_WEEKS`/`WeekConfig` で
  `intervention_enabled`+`condition`+`label_pool`+`calibrationMode` を一括設定（不整合を型で排除, FD7）。
  `record_session_meta` 失敗時は fail-loud。`tsc`/`build` 緑、code-reviewer HIGH なし。
- **#B GSE-10 差し替え**（GAS, 未追跡）完了。Ito, Schwarzer & Jerusalem (2005) 公式日本語版を逐語投入、
  pre/post byte 一致。アンカー=全く当てはまらない／当てはまらない／まあ当てはまる／全くその通り（FD6）。
- **#C 新フォーム ID 配線**（GAS, 未追跡）完了。`buildF5` を `openById(F5_FORM_ID)` 化＋既存設問全削除（FD8）。
- **未コミット**（10 files）。tracked= `src/App.tsx` + `Form_Phase1/*.md` + `.steering/...`。GAS は未追跡。

## 今回やること

### 1. #D 自作尺度「作業再開感・自己調整感」の項目最終化（主タスク）
現状 `tseItems`（buildF2）/ `tsePost`（buildF5）の4項目は全て「AIに頼らず／自力で」方向に偏っている。
decisions **FD4** に従い是正する:
- **逆転項目・行動信念項目・選好項目を混在**させ、黙従/方向バイアスを下げる。
- 「自己効力感」と称さない（過剰主張回避）。pre(F2-C)/post(F5) は**項目1–4を matched**・**byte 一致**を維持。
- 介入体験項目（取り戻す感覚/継続意欲＝F5 の experienceItems）は SE と**別構成概念**として分離済を維持。
- 手順: (a) 改訂項目案（逆転/行動信念/選好のラベル付き）を**ドラフト提示** → ユーザー承認、
  (b) 承認後に GAS の `tseItems`/`tsePost` を byte 一致で置換＋`設問草案.md` 同期、
  (c) **プレレジ文書化**（Cronbach α 目標・採点法＝逆転項目の再コード・主仮説）を `.steering/` に残す。
  ※ プレレジ内容は研究者判断。憶測で確定せずユーザーに確認する。

### 2. #A/#B/#C の最終化（コミット前の残作業）
- **#B 人手照合（重要）**: GSE-10 逐語は WebFetch 経由取得。本番投入前に公式ページ
  `http://userpage.fu-berlin.de/~health/japan.htm` で**逐語一致を目視確認**＋**研究利用条件**（無償・要引用か）を確認。
- **GAS 実機確認**: Apps Script で `buildForm`/`buildAllSupportForms` 実行 → 実機で
  不適格分岐の送信終了・回答メール非収集・F5 が固定フォーム（openById）に投入されることを確認。
- **#A 手動確認**: セッション開始時、週セレクタ選択が `session_meta` の
  `intervention_enabled`/`condition`/`label_pool` に正しく載るか NDJSON で確認。
- **レビュー**: code-reviewer + **`/cross-review`**（Codex 独立レビュー, CLAUDE.md で必須）。
  diff に NDJSON 生ログ・キーストローク内容は含めない（data-privacy）。GAS は未追跡のため diff 対象外＝
  GAS 変更は md と steering で担保。
- **コミット**: `/finish-task` で steering 最終化 → `git-workflow` 準拠でコミット
  （tracked= `src/App.tsx`・`Form_Phase1/*.md`・`.steering/`。type/scope 形式・Refs 付与）。

## 制約
- NDJSON 生ログ・キーストローク内容を外部 LLM/クラウドに送らない（data-privacy）。
- `src/` を触るなら `typescript-standards`（any 禁止）、`*.rs` なら `architecture-rules`/`rust-standards`。
- GSE-10・自作尺度とも**捏造・自前翻訳しない**。pre/post は byte 一致。
- GAS は未追跡。反映確認は Apps Script 実行＋実機挙動で行う。

## 延期（今回やらない）
- **#E week1 would-fire shadow ログ**（backend 改修・schema drift 注意。Phase 2/3）。
