# 2b の差分は意図通りか — ADR-006 Migration step 4 の記録

> ADR-006 Migration step 4 逐語:
> 「**この段で初めて `HMM_VERSION` を bump** → ゴールデン再生成 → 差分が意図通りか `.steering/` に記録」

実施日: 2026-08-18 / `HMM_VERSION`: `0.3.0` → **`0.4.0`**（MINOR・D-4）

---

## 1. 既存ゴールデン 4 本 — **差分ゼロ**（意図通り）

| ゴールデン | `session_meta` | 結果 |
|---|---|---|
| `minimal.json` | 無し | **byte-equal** |
| `phase1_ime_heavy.json` | 無し | **byte-equal** |
| `category_coverage.json` | 無し | **byte-equal** |
| `deep_silence.json` | 無し | **byte-equal** |

`git status src-tauri/tests/snapshots/` で**新規 1 ファイル以外に変更が出ないこと**を実測で確認した。

★ **なぜ差分が出ないか**: 4 本とも `session_meta` 行を 1 件も持たない（実測）。
`task_kind` が取れないので `TaskDomain::Writing` へフォールバックし、
Writing head = Phase1 と同一経路を通る。**これが「既存ログの確率列は 1 ビットも動かない」の実体**であり、
`HMM_VERSION` を MAJOR ではなく MINOR にした根拠でもある（D-4）。

⚠️ Phase1 の実データ 63 セッションは `session_meta` を**持つ**が、全件 `task_kind=argumentative` である
（`experiments/20260731-phase1-calibration-analysis/notes.md` §1）。`argumentative` → `Writing` なので
**Phase1 データの再現性も保たれる**。

## 2. 新規ゴールデン `vibe_coding_ime_mixed` — 意図した差分の中身

fixture: 30.4 秒 / 251 行 / snapshot 30 本。生成器は
`scratchpad/gen_vibe_fixture.py`（決定論・乱数なし）。

同一 fixture から `session_meta` 行だけを除いたもの（= Writing head へフォールバック）と比較した実測:

| 区間（fixture 上の時刻） | 内容 | Coding head vs Writing head |
|---|---|---|
| **0〜8.0s** | IME off・ラテン入力 (f1=150ms) | **完全一致**（snapshot 1.0〜8.0s） |
| **8.0〜24.0s** | IME **on**・日本語 (f1=200ms) | ⚠️ **相違**（snapshot 9.0s 以降・30 本中 22 本） |
| 16.3〜20.2s | IME **on** のまま backspace 16 連打 | 両方とも `obs=25` は**出ない**（gate が効く） |
| 27.8〜30.2s | IME **off** で backspace 16 連打 | 両方とも `obs=25` が**発火**（snapshot 30.0s） |

⚠️ **2026-08-18 訂正**: 当初この表を「9〜24s / 18〜24s / 30s」と書いていたが、
fixture 生成器の算術と実測に照らすと上記が正しい（code-reviewer 指摘）。
**表の主張（どこが一致し、どこで割れるか）は再現確認済みで変わらない。**

### 差分が意図通りである根拠

1. **0〜8.0s が一致するのは正しい。** IME off の Writing head は `β_writing_latin` を使い、
   その値は Coding head の初期シードと**同値**である（ADR-006 下位決定 #2/#3）。
   ここに差が出たら改名が値を変えてしまっている証拠になる。
2. **8.0〜24.0s で割れるのが 2b の目的そのもの。** 配線前は `ime_open` だけで β を選んでいたため、
   **日本語コメントを書いている coder が IME を開いた瞬間に `β_writing` で採点されていた**。
   これが `research-positioning.md §8` の言う「タスク混在は単一 β での採点ミスマッチ（交絡）」であり、
   2b はこれを消した。数値で言うと f1=200ms のとき φ1 が **0.5（β_writing）→ 0.167（β_coding）** に変わる。
3. **backspace ペナルティが IME on で出ず IME off で出るのは D-3 どおり。**
   Coding head も `!ime_open` で gate する決定をゴールデンが固定している。

## 2.1 ⚠️ ゴールデンの穴を 1 本追加して塞いだ（code-reviewer 指摘・2026-08-18）

★ **既存 4 本は `session_meta` を 1 行も持たないため、ルーティング表が
`Argumentative → Coding` に壊れても 5 本すべて緑のまま通る**ことが実測で示された。
守っていたのは `logger.rs` の unit test だけで、パイプライン全体の回帰保護は無かった。

→ **`argumentative_ime_mixed`**（`vibe_coding_ime_mixed` と `task_kind` **だけ**が違う双子）を追加。

| 比較 | 結果 |
|---|---|
| `argumentative_ime_mixed` vs `session_meta` 無し版 | **byte-equal** = 宣言があっても Writing 挙動は不変 |
| `argumentative_ime_mixed` vs `vibe_coding_ime_mixed` | **相違** = ルーティングが効いている |

★ **変異テストで検証済み**: `From<TaskKind>` を `Argumentative → Coding` にわざと壊すと
`argumentative_ime_mixed.json drift` で落ちることを実測した（壊す前は 29 tests 緑、
壊した後は 1 failed）。⚠️ **この 2 本は対で維持すること** —— 片方だけ再生成すると
ルーティングの壊れが差分として現れなくなる。

ゴールデンは **6 本**（`minimal` / `phase1_ime_heavy` / `category_coverage` / `deep_silence` /
`vibe_coding_ime_mixed` / `argumentative_ime_mixed`）。

## 3. 意図しない差分は無いか

- [x] `cargo test --workspace` **420 passed / 0 failed**（2a 時点 408 + 2b の新規 12）
- [x] `replay_snapshot_goldens_byte_equal` が **6 本**（既存 4 + 新規 2）で緑
- [x] `emit_schema` の差分は **additive のみ**（+20 行 / 削除 0・`required` 追加なし・型変更なし）
- [x] `check_schema_parity.py --dataset /c/gse-dataset` **exit 0**（gse-dataset 側も `d0e964e` で同期済み）
- [x] clippy **49 件**（2a コミット時点と同数 = **新規ゼロ**）
      ⚠️ **数え方**: `cd src-tauri && cargo clippy --workspace --all-targets 2>&1 | grep -c "^warning:"`。
      この数え方は各クレートの summary 行（`generated N warnings`）も 1 件として数えるため、
      **実診断件数より多く出る**（実診断は 45 件）。次セッションで「増えた」と誤認しないよう、
      比較するときは同じコマンドで測ること。
- [x] 既存 Phase1 ログ互換: `session_meta` に `head_id` を additive 追加。
      `ReplayEvent::SessionMeta` には**足していない**ので旧ログの deserialize は不変

## 3.1 レビューで塞いだ「本番とリプレイがずれる」経路（security-checker 指摘・2026-08-18）

⚠️ どちらも **Replay-as-Truth（ゴールデンが守っている保証）を無効化する型**の欠陥だった。

1. **`set_domain()` が検証・ログ送信より前にあった**（`lib.rs`）。
   `condition` / `label_pool` が不正、またはログチャネル満杯で早期 `Err` すると、
   **engine は Coding head に切り替わったのに `session_meta` 行が 1 行も残らない**。
   `start_session` は既に走っているので分析スレッドは動き続け、
   「Coding head で採点された `feat` 行が head 宣言の無いファイルに書かれる」状態になる。
   そのファイルを `gse-replay` に食わせると `task_kind` 不在 → Writing head へフォールバックし、
   **本番とリプレイの採点が食い違う**。
   → **差し替えを全検証と送信成功の後へ移した。** `head_id` は engine を触らずに
   `TaskDomain::head_id()` で先に求める。反映結果は `debug_assert_eq!` で突き合わせる。

2. **replay が「ファイル内の最初の `session_meta` だけ」を全区間に適用していた**（`bin/replay.rs`）。
   非 G1 モードはログをローテートしないので、「開始 → 戻る → 別 `task_kind` で開始」や
   再押下リトライで 1 ファイルに複数の `session_meta` が並ぶ。本番は 2 個目で head を差し替えるが
   replay は区間を持たないので再現できない。
   → **黙って先頭勝ちにせず `Err` で落とす**ようにした（相異なる `task_kind` が複数ある場合／
   `session_meta` があって `session_start` が複数ある場合）。
   ★ **再現できないものを再現したふりをするのが一番危ない**ため、フォールバックではなく失敗にした。
   検査は `multiple_distinct_task_kinds_in_one_file_is_rejected` /
   `multiple_session_starts_with_declared_task_kind_is_rejected`。

その他（LOW）:
- `update()` が 1 tick 内で `head()` を **2 回**ロック取得しており、その隙間に `set_domain` が入ると
  BS ペナルティ gate と潜在二軸が**別 head 由来**になりえた → **1 回だけ取る**形に修正。
- `set_domain()` が**反映後の `HeadId` を返す**ようにした（呼び出し側が `set_domain` → `head_id()` と
  2 回ロックを取ると、記録した `head_id` と実際に走る head がずれうるため）。
- `head_id` が手書き NDJSON ライタで**唯一 enum 由来でない文字列引数**だった
  （他は全て `as_str()` か `json_opt_str` でエスケープ済み）。`format!` はエスケープしないので、
  将来ここに動的文字列が流れると偽の NDJSON 行を注入できる。→ **`HeadId` enum を新設して型で閉じた。**
- 未知 `task_kind` の warn が全長出力だった（1 行は最大 500 MB まで許容される）→ **先頭 32 文字に切り詰め**。

## 4. ⚠️ 残る既知の穴（本タスクでは塞がない）

1. **`start_session` → `record_session_meta` の間の窓**: engine は起動時 1 個を使い回すため、
   `start_session` の `reset()` で Writing に戻り、`record_session_meta` で head が確定する。
   その間に挟まる 1Hz tick は Writing head で採点される。`App.tsx` は
   `start_session` 成功直後に `record_session_meta` を invoke するので実測上 1 秒未満だが、ゼロではない。
   → 塞ぐには `start_session` 自体に `task_kind` を持たせる必要があり、フロントの IPC 契約変更を伴う。
   ⚠️★ **さらにこの窓は非対称である**: リプレイは `task_kind` を先に読んで head を t=0 から固定するので、
   **窓が実際に効いたログはリプレイで再現できない**。
   ★ ただし code-reviewer の実測によれば、`AnalysisState::reset` が `extractor` も同時にリセットして
   `f1=0` になるため `update()` は早期 return し、窓の間に `feat` 行は出ない（実質閉じている）。
   採点が起きるには「`start_session` の数 ms 後までに 2 打鍵以上」が必要で、分析スレッドは
   非アクティブ時 50ms sleep のため現実的には成立しない。
2. **`App.tsx` の argumentative lock が残っている**ため、実運用では `vibe_coding` セッションが
   まだ発生しない（D-9・別タスク）。2b は「lock を外した瞬間に効く」状態で置いてある。
3. **Coding head v0 は打鍵 β だけ**。主信号である coding イベント（accept/reject/test/revert/
   diff-review）は Epic 4（ADR-006 #3）。
