# 設計（design）

## アプローチ
v0.4・既存 steering（D1–D7 / retro-labeling / intervention-response-capture）・実装コードを真実源とし、
`Form_Phase1/` の md 草案と GAS ビルダーを整合させる。設問は主観のみを扱い、行動指標はアプリ内 NDJSON、
派生指標はログ解析へ振り分ける（FD5）。尺度は GSE-10 無改変 + 自作主指標の二本立て（FD4）。

## このセッションで適用済みの変更
### `GSE_GoogleForm設問草案.md`
- F3 の波形 cue/手がかり再生 記述を削除 → blind リアルタイムプローブのフォールバックに訂正（D-2/D-9/D-12）。
- 「GSES」→「GSE-10」表記統一＋システム GSE との略称衝突注記。
- F2-C を「作業再開感・自己調整感」に改称＋自作尺度ガード注記。matched pre/post 化（項目4 事前専用を撤回）。
- F5 を SE/利用体験 分離＋NASA-TLX short 追記。L174「介入もない」→「単群・対照なし」訂正。2相プロトコル注記追加。

### `GSE_Phase1_Form_Builder.gs`
- F1 不適格3分岐に `setGoToPage(SUBMIT)`（フォールスルー阻止）。
- F2–F5 に `setCollectEmail(false)`（PII 分離）。
- F3 に `probe_id` 必須フィールド（`participant_id + probe_id` 突合）。
- F4 セッションキーを F3 と同形式へ統一＋annoyance 任意1項目（helpfulness はアプリ内へ委譲）。
- F5 を「作業再開感・自己調整感(matched 4)」＋「利用体験2」＋「NASA-TLX short 3」に再構成。
- F2-B/F5 GSE-10 に「公式日本語版へ差し替え必須」⚠コメント（捏造しない）。

## 実装済み（2026-06-24・次セッション分）
### `src/App.tsx`（tasklist #A 完了）
- 介入/較正2チェックボックス → 単一週セレクタ（`PhaseWeek`/`PHASE_WEEKS: WeekConfig[]`）。
  `interventionEnabled`/`calibrationMode`/`condition`/`labelPool` を週ごとのタプルで一括設定し、
  union リテラル型で不整合組合せを型レベル排除（decisions FD7）。`condition`/`labelPool` は backend enum と byte 一致。
- `record_session_meta` 失敗時を fail-loud 化（タグ欠落 + INTERVENTION_ENABLED 残留による blind 較正汚染を防止）。
- `Dashboard.tsx` は props（`calibrationMode`/`interventionEnabled`）据え置き。派生値を渡すのみ。

### `GSE_Phase1_Form_Builder.gs`（tasklist #B/#C 完了 2026-06-24）
- #B: buildF2/buildF5 の `gsesItems` を GSE-10 公式日本語版（Ito, Schwarzer & Jerusalem, 2005）逐語10項目へ置換。
  アンカーも公式版（全く当てはまらない〜全くその通り）へ。pre/post byte 一致を検証。`設問草案.md` も同期更新。
- #C: `buildF5` を `FormApp.create` → `openById(F5_FORM_ID="1I-X1B8F-…")` 化＋既存設問全削除を追加（FD8）。
- 構文チェック: `node --check` 緑。⚠ GSE-10 逐語は公式ページで人手最終照合・利用条件確認が残課題。

### `GSE_Phase1_Form_Builder.gs`（tasklist #D 完了 2026-06-24・FD9）
- 自作尺度4項目を「効力感(正)/逆転/行動信念/選好」の混在へ改訂（旧版の「AIに頼らず」方向偏重を是正）。
  方針 A をユーザー承認。項目2は逆転（採点 6−x）。
- pre(F2-C)/post(F5) を単一定数 `TSE_ITEMS` 参照に一元化し byte 一致を構造保証（code-reviewer LOW 対応）。
- プレレジ（採点法/α=報告のみ.70参照/主仮説=記述的pre→post）を `preregistration-tse-scale.md`＋FD9 に文書化。
- `node --check` 緑。code-reviewer HIGH/MEDIUM なし。GSE-10 公式ページ再 WebFetch で逐語一致を再確認（人手最終照合は残）。

## 変更対象（下流の実装タスク・未着手）
- `src-tauri/src/lib.rs` ほか — would-fire shadow ログ（tasklist #E、延期）。

## テスト戦略
- GAS: Apps Script エディタで `buildForm` / `buildAllSupportForms` 実行し、実機で分岐挙動（特に不適格分岐の送信終了）・回答メール非収集を確認。
- TS（週セレクタ）: `typescript-standards` 準拠、`any` 禁止。手動でセッション開始時の condition/label_pool/intervention_enabled が session_meta に正しく載るか確認。
- 尺度差し替え: pre(F2-B)/post(F5) の GSE-10 が**完全同一の項目文・尺度**であること（pre/post 比較の前提）。
