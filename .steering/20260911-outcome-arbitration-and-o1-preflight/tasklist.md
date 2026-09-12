# タスクリスト

> ★ 本タスクは issue 単位 (`issues/007.md` / `008.md` / `009.md`)。
> ⚠️ 各 issue の受け入れ条件は **その issue ファイルが SSOT**。ここは進捗の見取り図。

## issue 008 — macOS の IME 確定 / 放棄判別（★ 実装完了・実機のみ未実施）

### 準備
- [x] `_handoff/next-session-idea-to-ssot-intake.md` と `requirement.md` / `decisions.md` / `blockers.md` を読む
- [x] `survey-input-channels.md §7` を読む（★ macOS に composition の公開 API が無いことを一次資料で確認）
- [x] `hook-constraints` / `rust-standards` Skill を参照
- [x] Windows 側 `ime_shadow` 実装（`hook_windows.rs` / `ime_windows.rs` / `lib.rs`）を読む
- [x] ⚠️ **前提の再検証**: 「配布後は原理的に復元できない」→ **成立しない**（`decisions.md` 判断 7）
- [x] ⚠️ **既存の研究者判断 D-9 との衝突を研究者に諮る**（`decisions.md` 判断 9）

### 実装
- [x] `input/ime_compose.rs`（新規・OS 非依存）— 状態機械 `step` + Atomic ドライバ `drive`
- [x] `input/mod.rs` — `pub mod ime_compose;`（`#[cfg]` を付けない）
- [x] `input/hook.rs` — shadow atomics 5 つ + `IME_COMPOSING` の `#[cfg]` を外す
- [x] `input/hook_macos.rs` — `update_compose_state` を撤去し `ime_compose::drive` を呼ぶ
- [x] `lib.rs` — `emit_ime_shadow` の `#[cfg]` を外し、READY ポーリング経路だけ両 OS 有効化
- [x] `capabilities.rs` — 両 OS で `ime_shadow` を宣言。OS 対テストを反転
- [x] `schema_dto.rs` — `ImeShadow` doc の「Windows のみ」を訂正
- [x] `schema/current.json` — 意図的再生成（⚠️ description 1 行のみ・構造は不変）

### テスト
- [x] 状態機械の単体テスト 28 本（★ 両 OS で走る。⚠️ 修飾キー 6 本・マウス確定の合算 1 本を含む）
- [x] Atomic ドライバのテスト 9 本（★ 両 OS で走る。⚠️ 要約の偽装回帰 1 本・OS 別 drain 方針 1 本を含む）
- [x] `cargo test --workspace` — **645 passed / 0 failed**（ベースライン 577）
- [x] ゴールデン `gse-replay --snapshot` — `OK: 15 snapshots match`
- [x] `emit_schema` parity（CI と同じ `diff -u`）— PASS
- [x] `cargo fmt --check` — 差分なし
- [x] `cargo clippy --workspace --all-targets -- -D warnings` — ★ **main と同じ 29 件で新規ゼロ**（worktree で実測）
- [ ] ⚠️★★★ **AC 6: macOS 実機での確定 / 放棄の区別** → `blockers.md` 起票 4
- [x] ⚠️ **CI (self-hosted macOS) で macOS ビルドを通す** → ✅ PR #182 で **pass (4m54s)**

### レビュー
- [x] `code-reviewer` の指摘対応（HIGH 2 / MEDIUM 4 / LOW 5 — **全件対応**）
- [x] `security-checker` の指摘対応（⚠️ CRITICAL / HIGH は **0 件**。MEDIUM 2 件を対応）
- [x] ⚠️ `/cross-review`（Codex の独立レビュー）— ★ パス限定で実行・exit 0。新規 4 件（1 件は誤検知）を対応（`design-008` §10）

### ドキュメント
- [x] `docs/architecture.md` — macOS の IME 状態機械の置き場所と由来の非対称
- [x] `docs/repository-structure.md` — `ime_compose.rs` を 2 か所の一覧へ追加
- [x] `check_doc_lexicon.py` / `check_citations.py` — 違反なし
- [x] glossary への用語追加 — ★ **不要**（新しいドメイン用語を作っていない）

### 完了処理
- [x] `design-008-macos-ime-shadow.md`（設計 SSOT）
- [x] `decisions.md` 判断 7〜11
- [x] `blockers.md` 起票 4〜6
- [x] `issues/008.md` の Status / Execution Result
- [x] git commit（`bd5e6b8`）
- [x] PR → https://github.com/mikotomiura/GSE-prototype/pull/182 (⚠️ **CI 全緑 / MERGEABLE**。マージは研究者判断)

## issue 007 — 転帰定義の一本化（★ **ADR-029 を書いて完了**・2026-09-13）

### 準備
- [x] `requirement.md` / `issues/007.md` / `decisions.md` 判断 3・7〜12 / `blockers.md` 起票 1〜9 を読む
- [x] `verify-before-claiming` / `citation-ssot` Skill を参照
- [x] ADR-009（374 行）/ ADR-024（370 行）を**メインが全文**読む
- [x] ★ サブエージェント 3 本を**並列**起動（`.idea` 語彙調査 / `metrics.rs` 実装現況 / 設計文書と README 書式）
- [x] ⚠️★★★ **ADR-014（O1 の定義）/ ADR-016（O1 の非打鍵区間）/ ADR-025 を追加で読む** ——
      ★ **ここで issue 007 の前提 2 件が崩れた**（`decisions.md` 判断 13）

### 設計（★ `/reimagine` 1 回目）
- [x] 初回案 `design.md` を書く → `design-v1.md` へ退避
- [x] `requirement.md` のゴールのみから v2 を再生成
- [x] `design-comparison.md` で 2 案を比較
- [x] ★ **研究者が v2 を採用**（2026-09-13）／★ ESM 監査 criterion は **起票のみ**と決定

### 実装（★ コード変更ゼロ / 新観測ゼロ）
- [x] `docs/adr/ADR-029-outcome-role-arbitration.md`（新規・D1〜D6 / Alternatives A1〜A7 / 禁止 #15〜#21）
- [x] `docs/adr/README.md` ① ADR-029 の行 ② ADR-009 行の重ね書き注記
      ③ ADR-024 行の重ね書き注記 ④ **転帰定義の連鎖注記ブロック**（★ 表現チャネル連鎖と同型）

### テスト（⚠️ 機械 AC は**衛生条件**）
- [x] AC 4 `check_doc_lexicon.py` — **exit 0**（⚠️★★★ **ただし ADR は検査対象外**・実行記録に明記）
- [x] AC 5 `check_citations.py` — **exit 0**（★ 2 巡とも。`docs/**` 再帰走査なので ADR-029 は対象内）
- [x] AC 6 README の行 ＋ ファイル実在 — grep 済み
- [x] AC 7 `昇格元:` — grep 済み
- [x] AC 8 `/cross-review`（★ パス限定）→ `_codex-review-007.md`
- [x] `code-reviewer` ＋ `security-checker` を**並列**起動
- [ ] ⚠️ **AC 1〜3（裁定の妥当性）は研究者承認待ち**

### 完了処理
- [x] `decisions.md` 判断 13
- [x] `blockers.md` 起票 10（ESM 監査 criterion）/ 11（セッション終了の independent 仮定）/ 12（設計文書 2 本の未反映）
- [x] `issues/007.md` の Status / Execution Result
- [x] git commit

## issue 009 — 修飾キー同時押下フラグ（⚠️★★★ **不要として閉じた**・2026-09-13）

- [x] ★ **issue 007 の裁定（ADR-029）を確認** —— ⚠️ `revision topology` を主要アウトカムに据えていない
- [x] ⚠️★★★ **不要と判定し `issues/009.md` の Execution Result に根拠を明記**
      （★ 予測トラックも報告トラックも **undo / redo を使わない** ／
      `.idea/20260910-criterion:94` は T2 を「**privacy/feasibility 未確定**」の候補と自認 ／
      `:202` 逐語「**追加観測は別 ADR / 別計測器で裁く**」）
- [x] ★ 将来 T2 を採る場合に必要なこと（`KeyCategory` 量子化 / ADR-005 / `data-privacy` 再評価）を記録
- ★ 副産物: ⚠️ issue 008 との `hook_macos.rs` / `hook_windows.rs` / `schema_dto.rs` 交差も解消した
