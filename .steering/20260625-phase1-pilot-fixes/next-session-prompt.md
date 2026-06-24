# 次セッション用 開始プロンプト（Phase 1 パイロット実機フィードバック修正）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> 前タスク `20260624-phase1-form-survey-design`（#A–#D + プレレジ）は完了・コミット済
> （branch `feature/phase1-form-survey-design`、2 commits）。本タスクはその実機起動で判明した 3 件の修正。

---

## 依頼
実機起動で判明した 3 件に対応する。実装系なので **`/start-task`**（task-name=`20260625-phase1-pilot-fixes`、
本ディレクトリを利用）で steering を起こし、**main から新規ブランチ**を切る（前ブランチの PR は別途）。
バグ修正は **`/fix-bug`**、尺度・UI 変更は **`/add-feature`** or `/refactor`。設計判断は憶測せずソースに当たる。
プレレジに関わる判断（尺度点数・採点法）は**勝手に確定せず、ドラフト提案 → ユーザー確定**。

## 優先度と内容

### 【最優先・バグ】#1 プローブ/Nudge カードのボタンが効かず出っぱなしになる
**症状（ユーザー報告・第2週で発生）**: PAUSE 時に出るウィンドウ（= Nudge カード。kicker が "Pause point"。
ボタン=「詰まってない/今はもがきたい/閉じる」）で、ボタンを押しても反応せずウィンドウが消えない。
プローブカード（Q1摩擦/Q2前進）も同型の作りで同症状の可能性。

**前セッションの根本原因調査（要点・file:line 付き）**:
- 両カードは **backend `invoke` が成功したときだけ閉じる**設計。失敗時はカードを残す
  （較正データを静かに失わない/永久ブロック回避の意図）。
  - ProbeCard: `src/components/ProbeCard.tsx:63-91`（`record_realtime_answer`/`record_realtime_skip` 成功時のみ `setProbe(null)`）。
  - Nudge: `src/components/Overlay.tsx:63-76`（`record_intervention_dismiss`）。失敗時 catch で `setNudgeDismissed(false)` →
    nudge effect（`Overlay.tsx:259-284`）が action=nudge のまま再表示 → **押す→消える→即再表示の無限ループ**＝「反応せず出っぱなし」に一致。
- つまり**症状の正体は「backend コマンドが毎回 Err を返している」**＋フロントの“失敗時保持”設計。
- backend 失敗ポイント（`src-tauri/src/lib.rs`）:
  - `record_realtime_answer:674` / `record_realtime_skip:706`: `build_probe_ref(source, probe_id)` が Err /
    `window_end_ms < window_start_ms` / **`log channel full`（`tx.try_send`）**。
  - `record_intervention_dismiss:234`: parse 系は全 OK（`parse_dismiss_reason:621` / `DismissReason::parse` は
    not_stuck/want_to_struggle/just_close/silent を全受理）。残る失敗は **`log channel full`**。
  - 3 コマンド共通の唯一の失敗点 = **bounded log channel の `try_send`**（consumer が drain していない/セッション未初期化/ファイル書込ブロック等）。

**やること（厳密に repro してから修正）**:
1. devtools コンソールを開いて repro。フロントは失敗時に `console.error(...)` で**実エラー文字列**を出す
   （`ProbeCard.tsx:74,87` / `Overlay.tsx:71,273`）。**その文字列が根本原因の確定情報**。NDJSON 生ログは外部に出さない。
2. 実エラーに応じて backend を修正（例: log channel 容量/consumer 起動順、`build_probe_ref` の source/probe_id 条件、
   window_ms の前後関係）。`rust-standards`/`hook-constraints`（overlay/cursor）/`data-privacy` 参照。
3. **UX 改善**: 失敗が続くときに「無反応の死んだボタン」に見えないよう、カードにインライン
   エラー/リトライ表示を出す（“データを静かに失わない”意図は維持しつつ、無限再表示ループは断つ）。
4. 併せて overlay のクリック透過 (`setIgnoreCursorEvents`) が box 化時に確実に false になるかも実機確認
   （`Overlay.tsx:110-191`。クリックが届かない別経路の可能性を排除）。

### 【測定整合】#2 第2週ダッシュボードの 3 状態（Flow/Incubation/Stuck）表示
**ユーザー指摘**: V2 は Need 層として「STUCK か否か」の判断だけ。INC/STUCK/FLOW の 3 状態表示は不要では？
**調査**: ダッシュボードは `calibrationMode===false` のときだけ 3 状態バー＋状態カード＋GT カウンタ＋
「Incubation/Stuck の助言」info-box を表示（`src/components/Dashboard.tsx:357-439`）。FD7 では
**第2週=calibration OFF** なので第2週で表示される。一方プローブは第2週（post_intervention プール）でも発火し、
ProbeCard は原則5「モデル出力は一切表示しない」（`ProbeCard.tsx:17`）。**背後ダッシュボードの常時 3 状態表示が
第2週プローブ回答をアンカリングする恐れ**＋ v0.4 §5.2「Phase 1 は blind/minimal dashboard・状態表示を見せない」。
**やること（ユーザー確定の上で）**: 次のいずれかを提案→確定→実装。
  (A) Phase 1 中は両週ともモデル出力を隠す（debug は `import.meta.env.DEV` gate。`force_wall` と同方式 `Dashboard.tsx:467`）。
  (B) 第2週は 3 状態でなく Need ベースの単一 STUCK 指標に置換。
  (C) 3 状態表示を DEV gate。
  推奨は (A)（アンカリング排除＋V2 Need 整合＋v0.4 minimal dashboard）。`typescript-standards`/`hmm-analysis`/`intervention-design` 参照。

### 【プレレジ変更】#3 自作尺度を 5 件法→4 件法（偶数）に
**ユーザー指摘**: 奇数件法は中央選択（中心化傾向）バイアスを招くため偶数（1–4）の強制選択にしたい。
**調査/判断**:
- 自作 TSE 尺度は現在 5 件法（FD9 で確定）。GSE-10 副指標は**公式 4 件法（無改変・変更不可）**。
  → TSE を 4 件法にすると中心化傾向を抑制でき、**GSE-10 と件法が揃う**利点。欠点=中立表明不可・変化検出の粒度減。
- **スコープ注意**: 「事前・事後アンケート」= F2/F5。**F3 プローブ（Q1摩擦/Q2前進, 1–5）は X1 較正の正解ラベルで
  C-index 妥当性分析に直結**するため、勝手に偶数化しない（ユーザーに別途確認）。NASA-TLX/F4 を含めるかも要確認。
**やること（ドラフト→ユーザー確定→実装）**:
  - 確定後、GAS `TSE_ITEMS` の `setBounds(1,5)`→`(1,4)`＋アンカー 4 ラベル化（ScaleItem は両端のみ→中間は教示文）。
  - **採点法の再プレレジ**: 逆転再コードが 6−x → **5−x** に変わる（`preregistration-tse-scale.md` §3 / decisions FD9 / `設問草案.md` F2-C を同期）。新規 decisions FD10 として記録。
  - pre/post は `TSE_ITEMS` 単一定数参照で byte 一致維持（GAS は未追跡。md/steering で担保）。

## 真実源（先に読む）
- 本 steering（`/start-task` 後に作成）＋ 前タスク `.steering/20260624-phase1-form-survey-design/`（decisions FD1–FD9・`preregistration-tse-scale.md`）。
- `src/components/Overlay.tsx` / `ProbeCard.tsx` / `Dashboard.tsx`、`src-tauri/src/lib.rs`（上記 file:line）、`logger.rs`（DismissReason/SkipReason）。
- `Form_Phase1/ユーザー検証_codex-review_v0.4.docx.md` §4.3/§4.4/§5.2、`Form_Phase1/GSE_Phase1_Form_Builder.gs`（`TSE_ITEMS`）。

## 制約
- NDJSON 生ログ・キーストローク内容を外部 LLM/クラウドに送らない（data-privacy）。devtools エラー文字列のみ扱う。
- `*.rs` は `architecture-rules`/`rust-standards`/`hook-constraints`、`src/` は `typescript-standards`（any 禁止）。
- 既存テストを無断削除しない。HMM 挙動を変えるなら `HMM_VERSION` bump＋ゴールデン再生成。
- プレレジ（#3 採点法・件法）は憶測確定せずユーザー承認を取る。F3 プローブ件法は勝手に変えない。
- 完了時は code-reviewer＋`/cross-review`（diff に未関係な未ステージ変更を混ぜない。cross-review の Codex 自己ブロック既知issue: `run-codex-review.sh` を `--cached` 化検討）。

## 着手順
#1（データ収集をブロックするバグ）→ #2（測定整合）→ #3（プレレジ件法）。
