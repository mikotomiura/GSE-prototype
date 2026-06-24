# タスクリスト

## 完了済み（2026-06-24）
- [x] v0.4・steering・実装コードを読み、Form 草案/GAS の不整合・バグ・プライバシー穴を洗い出し
- [x] F1 不適格分岐に `setGoToPage(SUBMIT)`、F2–F5 に `setCollectEmail(false)`
- [x] F3 に `probe_id` 必須、F4 セッションキー統一＋annoyance 1項目
- [x] 自己効力感を「GSE-10 無改変 + 自作 作業再開感・自己調整感」に確定・改称（md/GAS）
- [x] F5 を SE/利用体験/NASA-TLX short に再構成、L174 訂正、2相プロトコル注記
- [x] codex-consult で第二意見取得（anticipation contamination / shadow 二相 / 構成概念改称）
- [x] GSE-10 出典の所在を確認（公式 selfscal.htm / NFER-NELSON。repo には逐語なし）

## 実装（次セッション）
- [x] **#A 開始画面の週セレクタ統合**（完了 2026-06-24）
  - `src/App.tsx`: 介入/較正2チェックボックス → 単一週セレクタ (`PhaseWeek`/`PHASE_WEEKS`/`WeekConfig`)
  - 選択で `intervention_enabled`＋`condition`＋`label_pool`＋`calibrationMode` を一括設定。
    union リテラル型で不整合な組合せを型レベルで表現不能化（FD7）
  - 開始後はスタート画面を離れるためセッション中変更不可（実質ロック）
  - `record_session_meta` 失敗時は fail-loud（setStartError+return）に変更（code-reviewer MEDIUM）
  - `tsc --noEmit` 緑 / `npm run build` 緑 / code-reviewer レビュー済（HIGH なし）
  - 残: 実機で session_meta に condition/label_pool/intervention_enabled が正しく載るか手動確認
- [x] **#B GSE-10 を公式日本語版へ差し替え**（完了 2026-06-24）
  - 出典: Ito, K., Schwarzer, R., & Jerusalem, M. (2005) Japanese Adaptation of the GSE
    （`http://userpage.fu-berlin.de/~health/japan.htm`、Schwarzer 公式配布ページ）を WebFetch で逐語取得
  - GAS `buildF2`/`buildF5` の `gsesItems`（プレースホルダ10項目）を公式逐語10項目へ置換。byte 一致を検証済
  - アンカーを公式版へ: 1 全く当てはまらない／2 当てはまらない／3 まあ当てはまる／4 全くその通り。
    ScaleItem は両端のみラベル可のため中間2/3はセクション教示文に明記
  - md 草案（F2-B/F5 節）も教示文・アンカー・出典を更新
  - 再照合 (2026-06-24): 公式ページを再 WebFetch し GAS の F2-B/F5 と byte 比較 → **公式==F2-B==F5 一致**。
  - ⚠ **残課題（ユーザー作業）**: (1) WebFetch は要約モデル経由のため公式ページを**人手で最終目視照合**
    （再 WebFetch 一致は強い裏付けだが代替にはならない）、(2) 研究利用条件（無償・要引用か）を公式ページで確認
    （ページ上に明示の制限記載なし。慣例上は非商用研究で要引用・無償だが要確認）
- [x] **#C 新フォーム ID の配線決着**（完了 2026-06-24・割当先=F5）
  - ユーザー指定により `1I-X1B8F-tQk7aEAdqderOLhjobeHct48KU23NWwfhlY` を **F5 事後アンケート**へ割当
  - `buildF5` を `FormApp.create` → `FormApp.openById(F5_FORM_ID)` 化（F1 と同方式）。
    再実行時の設問重複防止に既存設問の全削除（CLEAR_EXISTING）を追加。F2/F3/F4 は引き続き create 方式
- [x] **#D 自作尺度「作業再開感・自己調整感」の項目最終化**（完了 2026-06-24・FD9）
  - 方針 A（4項目・混在指標）をユーザー承認。効力感(正)/逆転/行動信念/選好を1項目ずつ混在に改訂
  - GAS `tseItems`/`tsePost` を byte 一致で置換（`node --check` 緑）、`設問草案.md` F2-C 同期
  - プレレジ（採点法=項2逆転6−x後4項平均 / α=報告のみ.70参照 / 主仮説=記述的pre→post）を
    `preregistration-tse-scale.md` + decisions FD9 に文書化

## 延期
- [ ] **#E week1 would-fire shadow ログ**（非推奨・Phase 2/3 へ延期）
  - `intervention_enabled=false` 時に policy を dry-run し would-fire を shadow フラグで記録（backend 改修・schema drift 注意）

## レビュー / 完了処理
- [x] code-reviewer（#D 中心・App.tsx 含む）→ HIGH/MEDIUM なし。LOW（pre/post 単一定数化）対応済
- [x] `/cross-review`（cross-reviewer 起動・ステージ済み diff 対象）。
      ★ **Codex パスは縮退（skip）**: `run-codex-review.sh` が `git diff`（`--cached` 無し）を使うため
        無関係な未ステージ `scripts/secrets-filter.sh` が混入し、ファイル名の "secret" が secrets-filter の
        skip 条件にマッチして exit 2 → ラッパーが「機密検出」と誤判定し Codex 未起動。**本タスク diff の問題ではなく
        ラッパー側の既知制限**。CLAUDE.md の安全ゲート縮退に該当 → Claude 単独レビューで代替（理由明記）。
      → 別タスク提案: `run-codex-review.sh` を `git diff --cached` 化 + secrets-filter.sh 自身の自己ブロック回避。
      ★ Claude 側指摘: MEDIUM 1件（App.tsx `?? PHASE_WEEKS[0]` 黙フォールバック）→ **対応済**
        （不変条件を `!` で表明し fail-loud 化, tsc 緑）。NASA-TLX 件法注記を `設問草案.md` に追記。
        残 LOW（研究者確認）: F4 annoyance 項目の対応注記 / プレレジ §6 効果量指標の確定（open のまま）。
- [ ] **GAS 実機確認（ユーザー作業）**: Apps Script で `buildForm`/`buildAllSupportForms` 実行 →
      不適格分岐の送信終了・回答メール非収集・F5 が openById 固定フォーム投入を確認
- [ ] **#A 手動確認（ユーザー作業）**: セッション開始時 週セレクタ選択が session_meta の
      `intervention_enabled`/`condition`/`label_pool` に正しく載るか NDJSON で確認
- [ ] **コミット（ユーザー判断・スコープ注意）**: tracked= `src/App.tsx`（前セッション）。
      `Form_Phase1/`・`.steering/` は**新規未追跡**（要 git add）。`.codex/budget.json`・`docs/*.md` 削除・
      `scripts/*.sh` は本タスク無関係 → コミットに含めない
- [x] `tsc`/`build` 緑（前セッション #A 時点）。`node --check`（GAS）緑
