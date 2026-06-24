# phase1-card-repro-backend-fix (#1 backend 層2 根本修正 ＋ カード再現性確保)

## 背景

プローブ/Nudge カードのボタン無反応バグ（#1）の **backend 根本修正**。前タスク
`20260625-phase1-pilot-fixes` で層1（フロント UX）は完了済（成功時のみ閉じ・失敗時はカード保持＋
インラインエラー＋リトライ）。未解決は backend 層2 のみ。

確定済の事実（前タスク blockers B1 / design 層2）:
- 3 コマンド（`record_realtime_answer` / `record_realtime_skip` / `record_intervention_dismiss`）の
  共通失敗点 = bounded log channel `tx.try_send`（`logger.rs:789` = `bounded(512)`）。parse 系は全否定済。
- 最有力仮説 = **(a) consumer 死亡 → Disconnected → 静かな全データ消失**。
  `logger.rs:799-804` の `File::create` 失敗（GSE_DATASET 誤指定 / macOS Documents/TCC 未許可）で
  consumer スレッドが `tracing::error` のみ残して early return → 以後 channel が Disconnected。
  キーストロークは `let _ = try_send` で握り潰し → NDJSON 全損・無通知。深刻度＝較正データ全損。
- コマンドは Full/Disconnected を両方 `"log channel full"` で潰しており**ラベルが誤誘導**。
- 前タスクで repro 試行 → 再現せず（間欠的・プローブが出にくい）。

## ゴール

1. **再現性確保**: debugView gate でプローブ/Nudge を即時に出すデバッグトリガを追加し、能動的に
   `record_*` 経路をテストできるようにする。
2. **backend 層2 根本修正**: 誤誘導ラベル是正＋ consumer 耐障害化＋ fail-loud（File::create 失敗で
   データを静かに全損させない・ユーザーに見える形で通知）。
3. `cargo test --workspace` パス。HMM 不変（schema_dto.rs を触らない）。

## スコープ

### 含むもの
- フロント: debugView gate のデバッグトリガ（プローブ強制 / Nudge 強制）。
- backend: `lib.rs` の log channel エラー文言の Full/Disconnected 分岐（誤誘導ラベル是正・無条件で安全）。
- backend: `logger.rs` consumer 耐障害化（temp フォールバック）＋ fail-loud（起動時の書込可否を
  IPC でフロントへ通知しバナー表示）。
- 回帰テスト（consumer フォールバック・文言分岐）。

### 含まないもの
- HMM 挙動の変更・`schema_dto.rs` / NDJSON schema の変更（HMM_VERSION bump 不要）。
- backlog（真の Full）専用の容量・drain 律速の是正は repro で Full が確定した場合のみ（現時点は
  Disconnected が最有力のため consumer 耐障害化を優先。realtime_label を落とさない方針は維持）。
- diff に未関係な未ステージ変更（budget.json/scripts/docs削除/MEMO）を混ぜない。

## 受け入れ条件

- [ ] debugView（`VITE_GSE_DEBUG==="1"`）でプローブカードと Nudge を即時に出せる。被験者バンドル
      （既定 OFF）には現れない。
- [ ] log channel 送信失敗時のエラー文言が Full と Disconnected を区別する。
- [ ] `File::create` が primary パスで失敗しても consumer スレッドが死なず、temp へフォールバックして
      データ全損を防ぐ。両方失敗時も channel は Disconnected にならない（カードが閉じる）。
- [ ] ログ書込が primary 以外に落ちた / 無効化された場合、フロントに fail-loud バナーが出る。
- [ ] 回帰テスト追加・`cargo test --workspace` パス。`gse-replay --snapshot` 現状維持。
- [ ] code-reviewer + security-checker（logger.rs 変更で必須）+ `/cross-review`。

## 関連ドキュメント

- 前タスク `.steering/20260625-phase1-pilot-fixes/`（design 層1/層2・decisions 判断2・blockers B1）。
- `docs/architecture.md`（スレッドモデル・logger consumer）、`data-privacy` / `intervention-design` Skill。

## 運用メモ
- /reimagine 適用: No
- 理由: 根本原因は静的調査でほぼ確定（consumer 死亡 → Disconnected）。修正方針も前タスクで
  設計済（design 層2）。複数案を比較する設計フェーズではなく、確定した方針の実装フェーズのため。
