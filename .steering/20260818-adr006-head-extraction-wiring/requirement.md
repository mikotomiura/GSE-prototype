# ADR-006 Phase 2a/2b — Writing head 抽出 と task_kind → head 配線

## 背景

`task_kind`（`Argumentative` / `Correspondence` / `Creative` / `VibeCoding`）は
`logger.rs:66-71` / `schema_dto.rs:270-275` / `src/probeTypes.ts:7-11` に定義されているが、
**`src-tauri/src/analysis/` 配下では 1 件もヒットしない = 推論パイプラインでは完全な dead_code**（実測）。

β baseline の選択は `engine.rs:311` で **実行時の `ime_open` だけ**を見て 2 択している:

```rust
let (beta_f1, beta_f3, beta_f4, beta_f5, beta_f6) = if ime_open {
    (BETA_WRITING_F1 /* 100 */, 0.10, 2.5, 1.0, 0.12)
} else {
    (BETA_CODING_F1  /* 150 */, 0.06, 5.0, 2.0, 0.08)
};
```

つまり「どのドメインの baseline で採点するか」を、**宣言された `task_kind` ではなく
その瞬間の IME 状態が代理している**。`docs/research-positioning.md §8` はこれを
「task_kind→β 未配線 → タスク混在は単一 β での採点ミスマッチ（交絡）」と明記している。

**Phase1 が 2026-08-18 に収集打ち切りで終了した**（verdict = `inconclusive` / GATE3 = `DataInsufficient`）
ため、`docs/adr/README.md` の凍結（`engine.rs` HMM_VERSION 等）が解除された。
ADR-006 Migration step 1「Phase1 完了 + verdict 確定を待つ」の条件が満たされた。

## ゴール

ADR-006 の Alternative C「分離」を実装する。**2 コミットに分ける**（ADR-006 逐語
「両者を混ぜて 1 コミットにしない」）。

- **2a 抽出（挙動不変）**: β を Writing head の所有物へ移送し、`β_coding` を `β_writing_latin` に改名する。
  β 選択ロジックは変えない。`HMM_VERSION` 不変。
- **2b 配線（挙動変更）**: `task_kind` を head 選択へ効かせ、**Coding head v0**（β_coding シードのみ）を追加する。
  `HMM_VERSION` を `0.4.0` へ bump。

## スコープ

### 含むもの

**2a**
- `analysis/writing/` モジュール新設。β 定数と選択ロジックを Writing head の所有物へ移送
- `BETA_CODING_*` → `BETA_WRITING_LATIN_*` に改名（**値は変えない**・ADR-006 下位決定 #2）
- `ime_open` を Writing head 内部の within-writing 信号として維持
  （β 切替 + backspace ペナルティ gate `pending && !ime_open` は現行どおり）
- `DomainInferenceHead` trait を導入（`infer()` のみ）

**2b**
- `task_kind` を `lib.rs` / `bin/replay.rs` 境界で analysis 層のルーティング型へ変換して渡す
- head 選択: `Argumentative` / `Correspondence` / `Creative` → Writing head、`VibeCoding` → Coding head v0
- **Coding head v0**: 現 `β_coding` の値を初期シードとして所有し、**`ime_open` に関わらず**適用する
  （ADR-006 下位決定 #3）。backspace ペナルティ gate は Writing と同じく維持（D-2b-1）
- Creative は Writing head へ流すが、出力に `head_id` を刻んで後から分離可能にする（D-2b-2）
- `HMM_VERSION` `0.3.0` → `0.4.0`。`engine.rs` の SemVer コメントに定義の穴を埋める行を追記
- ゴールデン `vibe_coding_ime_mixed` を新規追加（4 本 → 5 本）

### 含まないもの（Out）

- **Wall 関連**（コード・docs とも一切触らない）。`.idea` §3.4 の警告どおり PM-Q1〜Q7（表現層）と
  セットで決めるべき論点で、repo の研究者決定 A-Q6 は「保留」のままである
- **T2 観測空間拡張**（ポインタ動態 / 編集イベント / アプリ切替回数）→ 2b 完了後の別タスク。
  input 層（OS フック）の新規実装で、analysis 層の本タスクとは触るファイルが完全に別
- **Epic 4 の coding イベント**（accept / reject / test / revert / diff-review）
- **Creative 専用 head**（Epic 6・編集/タイムラインイベント基盤）
- **ADR-010 の `scope_fit` / `evidence_quality`**
- **`DomainAdapter` trait**（`ingest` / `privacy_audit` / `feature_snapshot`）→ Epic 4/5
- **`src/App.tsx` の argumentative lock 解除** → Phase2 の募集・教示・条件割付の運用設計とセットの別タスク
- `probe_scheduler` の個人適応

## 受け入れ条件

### 2a（挙動不変）

- [ ] `cd src-tauri && cargo test --workspace` 緑
- [ ] `replay_snapshot_goldens_byte_equal`（`bin/replay.rs:2916`）緑 = ゴールデン 4 本 byte-equal
- [ ] `HMM_VERSION == "0.3.0"` 不変
- [ ] 旧 HEAD ビルドと新ビルドで **全 10 fixture** の replay 出力が一致
      （snapshot 未整備の 6 本は旧バイナリで生成して比較）
- [ ] `cargo run --bin emit_schema` の出力が `schema/current.json` と byte-equal（schema drift なし）
- [ ] clippy 警告が変更前と同数（新規ゼロ）

### 2b（挙動変更）

- [ ] 既存ゴールデン 4 本が **byte-equal のまま**（= 無関係な副作用が無いことの証明）
- [ ] 新規ゴールデン `vibe_coding_ime_mixed` が緑
- [ ] `vibe_coding_uses_coding_beta_regardless_of_ime` 緑
- [ ] `creative_and_correspondence_route_to_writing_head` 緑
- [ ] `HMM_VERSION == "0.4.0"`
- [ ] `cargo test --workspace` 緑 / schema drift なし / clippy 新規ゼロ
- [ ] 差分が意図通りかを `.steering/` に記録（ADR-006 Migration step 4）

### 文書

- [ ] ADR-002 を **Accepted** に昇格（trait 範囲は `DomainInferenceHead` のみと明記）
- [ ] ADR-006 に実施記録を追記（Creative の扱い・BS gate・bump 幅・ゴールデン方針）
- [ ] `docs/adr/README.md` の凍結注記を「Phase1 は 2026-08-18 に収集打ち切りで終了」へ更新
- [ ] `docs/glossary.md` に確定用語を追記
- [ ] 引き継ぎ §3 の誤前提（「研究者は Wall を廃止した」）の訂正を `decisions.md` に事実として記録

## 関連ドキュメント

- `docs/adr/ADR-006-task-kind-beta-wiring.md`（Decision / 下位決定 #2 #3 / Migration）
- `docs/adr/ADR-002-domain-local-inference.md`（Proposed → Accepted へ）
- `docs/architecture/domain-adapter-boundary.md` §Layer 3-4
- `docs/research-positioning.md` §8 段別表 T0–T3 / §9 A-Q3 解除条件
- `experiments/20260731-phase1-calibration-analysis/notes.md` §5
- `docs/development-guidelines.md` §3（HMM_VERSION bump 手順）

## 運用メモ

- /reimagine 適用: **No**
- 理由: ADR-006 が Decision・下位決定 #2/#3・Migration の 2 サブフェーズ分割まで具体化済みで、
  設計の再生成余地は本セッションの grill で閉じた 7 分岐に尽きている（D-1〜D-7）。
