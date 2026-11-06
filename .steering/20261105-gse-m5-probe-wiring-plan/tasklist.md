# タスクリスト

## A この計画のタスク（2026-11-05）

- [x] 引き継ぎ `next-session-gse-m5-plan-and-dashboard-names.md` §3 を読む
- [x] 一次の決定を読む（design-map §3・§4・ADR-031・ADR-043 D5〜D10・ADR-048 D3・事前登録 S1-A1〜A7・S1-F5〜F10）
- [x] R1 の状態を研究者に聞く（判断 0: 実機の確かめは未実施）
- [x] 日の終わりの問い・問わない区間を試しに入れるか（判断 1・2）
- [x] file-finder と impact-analyzer を並列で（既存の実装の場所・R1 との衝突点）。戻り値の要点を一次で確かめた（main の 188 コミットがソースに触れていない）
- [x] design.md v1 → /reimagine で v2（v1 を読ませない Opus）→ 比べ（`design-comparison.md`）→ ハイブリッドを採用（判断 3）
- [x] 設計の未決のうちコードの形を変える 7 項目を研究者に聞く（判断 4〜10）
- [x] 実装のタスクの粒度の tasklist（下の B）
- [x] 枝 `docs/gse-m5-probe-plan` にコミット（push は研究者の手元で）
- [ ] 引き継ぎに §7 の追記（この計画の置き場所と次の一手）

## B 実装のタスク（R1 が main に入ってから・新しいセッションで `/start-task` → `/add-feature`）

着手の条件: R1（`feature/nudge-default-off`）が main に入り、R1 の残り（実機の確かめ・schema parity）が済んでいる。新しい worktree を main から切る。行番号は R1 の後の main で引き直す。

場面ごとに使うもの（完了の前にこの表と照合する）:

| 場面 | 使うもの |
|---|---|
| `*.rs` を書く | `rust-standards`・`architecture-rules`（`s1.rs`・`analysis/probe_arbiter.rs` の新規・mod.rs） |
| `logger.rs`・`redaction.rs`・`recording.rs`・自己申告の選択肢 | `data-privacy` |
| `*.tsx` を書く | `typescript-standards` |
| 区切りの点検 | `code-reviewer` ＋ `security-checker` を並列 |
| 完了 | `/finish-task`（`/cross-review` を含む。Codex に記録の本文を送らない） |
| 画面の確かめ | macOS は自分で AX と画面の取得、Windows は研究者の手か CI |

### B1 段 1 の層（`s1.rs`）と門

- [ ] `s1.rs`: 印 `s1.mode`・env `GSE_S1_MODE=1`（"1" のみ）・`resolve(detected, o1_active, eh3_active)`（O1 のときだけ・EH3 と同時なら両方落とす＝判断 7）・`OnceLock`・`is_s1()`
- [ ] `lib.rs` の起動時に `s1::set_mode`。EH3 との衝突は `tracing::error!`
- [ ] `meta` に `s1_mode`（`o1_install_id` の直後・`eh3_*` の前）。素の O1 の `meta` は byte-equal
- [ ] `o1::activity_label_allowed(stage1_mode, consent_ack)` に読み替え、検査 `activity_label_needs_both_o1_and_consent` を書き換える（PR に明記）
- [ ] `submission::s1_probe_consent_acknowledged`・`write_s1_probe_consent`（`~/.gse/s1_probe_consent`・時刻と `consent_version` だけ）と登録の画面の同意の項目（判断 5）
- [ ] 検査: `s1_requires_o1`・`s1_and_eh3_both_dropped`・`s1_marker_beats_env`・`env_value_exactly_1`・`activity_label_none_for_o1_even_with_consent`・`activity_label_some_only_for_s1_with_ack`・`o1_meta_unchanged_without_s1_marker`・`s1_meta_fragment_order`・`s1_never_shows_invitation_or_nudge`

### B2 調停器（`analysis/probe_arbiter.rs`）

- [ ] `RandomFrame`（seed と起点で決まる候補の列・`sample_interval_ms` を `pub(crate)` で共有）
- [ ] `StrataDetector`（`low_operation_end`・`resumption`・自分の窓の遷移を除いた入力）
- [ ] `NoAskPlan`（既定は無効・R1 の splitmix64）
- [ ] `DayQuestion`（契機・拾い直し・補助の契機・1 日の上限）。状態ファイルの IO は持たない
- [ ] `Arbiter::tick` の順（無作為 → 層化 → 日の問い）
- [ ] 仮の定数の表（design.md §6）をそのまま定数に。`S1_MAX_PROBES_PER_HOUR`
- [ ] 検査: design.md「テスト戦略」の `probe_arbiter.rs` の全項目（時差は JST と UTC の両方）

### B3 行種と記録

- [ ] `LogEntry::{ProbeFrame, ProbeSuppressed, DayQuestion}`・整形の純粋関数・`line_type`・`SkipReason::Superseded`（判断 9）・`probe_suppressed.reason` に `card_open`・`no_ask`
- [ ] `day_question` に `target_day`・`shown_local_minute`（時差は書かない・判断 4）
- [ ] `capabilities.rs`: `activity_label` を `emitterless` から外し、4 行種を `config_gated`。段 1 だけで宣言するか（`config_gated` がモードで出し分けるか）を確かめる
- [ ] `redaction.rs`: 新しい行種は `"t"` で消える。`probe_frame` は消さない（判断 8）。削除の台帳（`docs/o1-deletion-ledger.md`）と `data-privacy` の文言と合うかを確かめ、合わなければ止めて研究者に相談する
- [ ] `schema_dto.rs` → `emit_schema` → `schema/current.json`（手で解かない）
- [ ] 検査: 整形の byte-equal・`realtime_label_skip_superseded`・`new_s1_rows_are_deleted_by_t`・`probe_frame_survives_redaction`・一時停止で新しい行種が落ちる（`KNOWN_LINE_TYPES` から導く既存の検査）

### B4 駆動役（`lib.rs`）

- [ ] 今のプローブのスレッドは段 1 では起こさない（`probes_disabled || s1::is_s1()`）
- [ ] 段 1 の駆動スレッド: 起点 `O1_LOG_OPENED_MS`・世代 `S1_FRAME_GEN`（ローテートで進める）・`probe_frame` の出し直し・`GSE_DISABLE_PROBES` は見ない（警告 1 行・判断 6）・同意の印が無ければ調停器を作らない
- [ ] 特徴量のキーの押下の時刻（`LAST_KEY_MS` は全てのキーで更新されるので使えるか確かめる）とフォーカスの遷移（`eh3::focus_row_allowed` の絞り込みを段 1 にも）
- [ ] 電源の通知を段 1 でも起こす（`power::start` を 2 回呼ばない）
- [ ] `s1_day_state.rs`（`~/.gse/s1_day_state.json`・原子的な書き込み・壊れていたら日の問いを出さない）
- [ ] コマンド `record_probe_response`・`record_probe_skip`・`record_day_question`・`get_s1_mode`・`acknowledge_s1_probe_consent`
- [ ] overlay を段 1 で `show()`（NSPanel 化の後）
- [ ] トレイの終了の補助（「答えて終了／答えずに終了」・60 秒・判断 10）。一時停止は再開の直後に予約

### B5 画面

- [ ] `ProbeCard.tsx`: 6 択（固定・自由記述なし・理由を問わない）・3 問を 1 枚・「直前の30秒」・`superseded` の扱いは backend の指示に従う
- [ ] `DayQuestionCard.tsx`（仮の文は S-DQ の候補の表から・`items_version`）
- [ ] `Overlay.tsx` でカードの排他・`App.tsx` に `get_s1_mode`・登録の画面の同意の項目
- [ ] 画面の確かめ（macOS・Windows）: 同意の前は出ない・見える・押せる・背後のクリックを奪わない・一時停止の間は出ない・「答えずに終了」が 60 秒以内に終わる

### B6 再生と配布の門

- [ ] `gse-replay --probes`（記録から調停器を回し、一致・欠け・余りを JSON で）・`--day-questions`（回答の後の押下の数）。R1 の `--invitation` と相互に排他
- [ ] 既存のゴールデンの `--snapshot` の byte-equal
- [ ] 段 1 の配布物の門（`check-s1-release-readiness.sh`）: `s1.mode`・`GSE_DISABLE_PROBES` を付けない・本人用の印（判断 5）・他の参加者向けは同意文書の承認の印・EH3 の印と同居しない（判断 7）。O1 の門は `s1.mode` を含まないことを検査
- [ ] 段 1 の launcher（`.bat` を作る場所を確かめる）

### B7 文書と同期

- [ ] `docs/architecture.md`・`docs/architecture/gse-design-map.md`（§1 のラベルの行・§4）
- [ ] R3: gse-dataset の schema の同期
- [ ] `/finish-task`（`/cross-review` を含む）。push と PR は研究者に確かめてから。`src/` を変えるので `[skip ci]` を付けない（G-GEAR の self-hosted ランナーの空きを確かめる）

## 完了処理（この計画のタスク）

- [x] design.md の最終化（v2 ハイブリッド・判断 4〜10 の注）
- [x] decisions.md（判断 0〜10）
- [x] git commit
