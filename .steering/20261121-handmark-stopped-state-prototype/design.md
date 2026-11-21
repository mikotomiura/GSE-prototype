# 設計: 手跡の止まり（ADR-056）の試作 —— 今の手跡の状態に触れない「別の層」として足す

採用は /reimagine 1 回目のハイブリッド（判断 10）。構造は v2、自律の動きの作りは v1。比較は `design-comparison.md`、初回案は `design-v1.md`（調べた事実はそこの末尾）。

## アプローチ

段 1 の後期は今の手跡のまま配る（判断 3）。回 2（12-09 以降）も、今の机上の道具で回る。そこで、今の `StageState`・`bits()`・コマの書式（`write_frame`・`pixels.mjs`）・`B_STATE_NAMES` を変えず、止まりを別の層として足す。切っているとき、窓へ送るものも机上の出力も今と同じになる。

1. **`Stage` に足すのは `idle_since` の読み口だけ**
   - `Stage` は `idle_since: Option<u64>` を持つ。値は「`is_idle` が初めて真になった格子の刻み」。
   - 各刻みの後と早送りの直前に `is_idle` を見て決め、偽に戻れば消す。こうすると、早送りでも `advance_to` の呼び方でも同じ値になる。
   - 風・不規則さ・位相・漂いの計算は変えない。`StageState` も `bits()` も変えない。
2. **止まりの層（新しい `analysis/handmark/stopped.rs`）**: 次の純関数で 1 コマを作る。
   `stopped_view(idle_since, grid_t, gate, seed, cfg) -> StoppedFrame`
   - `gate`（返してよいか）は、打鍵と一時停止の時刻だけから決める。`Stage` の起点 t0・最後の再開の時刻のどちらよりも後に打鍵があり、かつ一時停止の外なら真。これで起動の直後・戻した直後・一時停止の間・一時停止明け（判断 2）が、どれも最初の打鍵まで 0 になる。打鍵の後にマウスだけを使う間は v が出る（判断 8）。
   - v = min(1, (grid_t − idle_since) / rise_ms)。`gate` が偽のとき、または `idle_since` が無いときは 0。移り変わりが終われば 1 のままで、止まりの長さを持たない。
   - 戻りは v を即 0 にする。見た目の戻りは、窓の側の 250 ms の線形の補間に任せる（ライブの遅れ 500 ms と合わせて、設計案の候補 0.3 秒に近い）。
   - 自律の動き `ambient(seed, t_ms, window_s) -> [f64; 3]` は、v1 の重みの和で作る。
     - 絶対の時刻の 1 秒ごとの節 n に、`splitmix64` で日の種・節の番号・チャネルから [−1, 1] の値を置く。
     - 時刻 t の値は、t から W 以内の節を、両端で 0 になる余弦の二乗の重みで足し、重みの和で割ったもの。節の番号の順に回すので、和の順序が決まり、bits が再現する。
     - 窓より離れた 2 つの時刻は節を共有しないので、記憶は W で切れる。分散は時刻に依らず一定になる。`grid_start` も周期の関数も使わない。
     - 種は、`Stage::new` が今も受けている日の種（`Evaluation::draw_seed()`）を使う。
   - `StoppedFrame { v, ambient: [f64; 3], form: u8, strength: f64 }` は別の serde の型で、`bits()` も別に持つ。
3. **再生**: `replay_stopped(presses, pauses, seed, t0, t, cfg) -> StoppedFrame` と、そのライブ版（`now − LIVE_LAG_MS`）を足す。中で今の `replay` と同じ順で `Stage` を回し、`idle_since` と、打鍵と一時停止の時刻から `stopped_view` を呼ぶ。
4. **ライブ（駆動役）**
   - 一時停止の始まりと終わりの時刻を、打鍵と同じ待ちの列に入れる。`tick` で `target` 以下になったものを時刻の順に適用する。こうすると、500 ms の遅れの規則で再生と一致する。
   - 切っているときは何もしない（今と同じ）。入っていれば、`Effect::Stopped(StoppedFrame)` を出す。
5. **窓**
   - 別のイベント `handmark-stopped` で送る。切っているときは送らない。
   - `HandmarkStage.tsx` は、`drawFrame` の後に、新しい `handmarkStoppedDraw.ts` の `drawStopped` を呼んで重ねる（3 つの形）。どれも `v × strength × ambient` で描き、止まりの長さで大きさ・速さ・明るさ・数を変えない。衰えや疲れの形・評価の色を使わない。
   - 端の帯は変えない（判断 7）。
6. **研究者用の切り替え**
   - `lib.rs` で、`GSE_DEBUG` が立っているときだけ `GSE_HANDMARK_STOPPED` を読む。純関数 `parse_stopped_cfg(Option<&str>, debug: bool) -> Option<StoppedCfg>` に渡す（`GSE_DISABLE_PROBES` と同じ形）。
   - 形式は `form=band;rise_ms=2000;window_s=20;strength=0.5` のようにする。読めない値は切ったままにし、`tracing::warn!` を出す。
   - 描画の側に環境変数の門を置かない。
7. **机上**
   - `desk.rs` に、止まりのコマの列を出す口を足す（`--stopped <cfg>` のときだけ）。今の出力・`write_frame`・`DESK_VERSION` は、切っているときは変わらない。
   - 新しい `experiments/20261121-handmark-stopped-desk/` で、今のコマの画に止まりの層を重ねて描く。画面と同じ `drawFrame` → `drawStopped` の順で呼ぶ。そのうえで (i)〜(iii) と漏れの検査を回す。

## 変更対象ファイル

PR-a（判断 9 の分け方）:
- `src-tauri/src/analysis/handmark/state.rs` — `idle_since` と読み口。
- `src-tauri/src/analysis/handmark/stopped.rs`（新規）・`mod.rs` — `StoppedCfg`・`parse_stopped_cfg`・`ambient`・`stopped_view`・`StoppedFrame`・`replay_stopped`・テスト。
- `src-tauri/src/handmark_driver.rs` — 一時停止の待ちの列・`Effect::Stopped`・cfg。
- `src-tauri/src/handmark_stage.rs` — `handmark-stopped` を送る。
- `src-tauri/src/lib.rs` — 環境変数を読む・`Effect::Stopped` を送る。
- `src/components/HandmarkStage.tsx`・`src/components/handmarkStoppedDraw.ts`（新規）・`scripts/handmark-stopped-draw.test.mjs`（新規）。
- 必要なら `handmark_guard.rs`（TS と Rust のイベント名の一致の検査に、新しいイベントを足す）。
- `docs/functional-design.md`・`docs/glossary.md`。

PR-b:
- `src-tauri/src/analysis/handmark/desk.rs`・`src-tauri/src/bin/replay.rs`（止まりの出力の口）。
- `experiments/20261121-handmark-stopped-desk/`（重ね描き・(i)〜(iii)・漏れの検査・結果）。

## 既存パターンとの整合

- 窓への別の系統のイベントは、ポインタの跡（`emit_trace`）や波紋（`emit_ripple`）と同じ前例に乗る。
- 乱数は `state.rs` の `splitmix64` を使う。新しい crate は足さない。
- 待ちの列で時刻の順に流すのは、打鍵の `pending` と同じ形にする。
- 環境変数は、`lib.rs` で読んで純関数に渡す。

## テスト戦略

1. **今のテストは、どれも変えずに通る**（`StageState` を変えないため）。これを先に確かめ、最後にも確かめる。
2. **新しい単体テスト（`cargo test --manifest-path src-tauri/Cargo.toml --workspace`）**
   - `idle_since`: 早送りと素朴な 1 刻みずつの進め方で一致する。打鍵で消える。
   - v: 移り変わりの後は一定で、止まりが 1 分・1 時間・1 日で bits が同じ。境界の 4 つで 0。打鍵の後にマウスだけを使う間（打鍵なし）は v が上がる。`advance_to` を何回に分けても、立ち上がりの途中で bits が一致する。
   - ambient: `grid_start` をずらしても、同じ時刻なら同じ値になる。W より離れた 2 つの時刻は節を共有しない（節の範囲を返す内部関数で確かめる）。値は [−1, 1]。日の種を変えると値が変わる。
   - cfg: 既定（環境変数なし・`GSE_DEBUG` なし・読めない値）は切ったまま。
   - ライブと再生: 駆動役のテストに、一時停止を挟む・日付の切り替え・時計の飛びを足し、`Effect::Stopped` の bits と `replay_stopped` のライブ版が一致することを確かめる。切っているときは `Effect::Stopped` が出ない。
3. **窓の側**: `node --test` の流儀で、`drawStopped` が v = 0 で何も描かないこと、`HandmarkStage` が `drawFrame` → `drawStopped` の順で呼ぶことを確かめる。tsc が緑。
4. **机上（PR-b・研究者の手元の記録で・外部の LLM に送らない）**: (i)〜(iii) は、止まりの単位でまとめた交差検証と、入れ替えの帰無に対する片側 5%（判断 9）。止まりの数と帰無の分布の幅を添える。漏れの検査は、ADR-051 D3 の手順で、今の B に止まりの列を足した B′ と A を比べる。今ある基層（`drift`）が (iii) で落ちたら研究者に確かめる。
5. **手動**: 研究者のデバッグ起動で 3 つの形が出ること、切っているときに何も変わらないことを見る。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: ハイブリッド（構造は v2・自律の動きは v1・返してよいかは v2 の純関数）
- 根拠: 研究者が推奨どおり選んだ（判断 10）。切っているときに段 1 の後期の配布物と回 2 の机上の道具を 1 ビットも揺らさないことが要件の芯に合う。値のノイズは分散の揺れが見え、記憶が 2W になるので、重みの和を採る。
