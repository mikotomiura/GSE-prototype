# 設計: 手跡の止まり（ADR-056）の試作

根拠: ADR-056 D1〜D7、設計案 §4.4、本タスクの判断 2〜5。調べたこと（2026-11-21・file-finder と impact-analyzer の報告に加え、要の箇所はメインが一次で読んだ）は末尾の「調べた事実」に書く。

## アプローチ

3 つの層に分けて作る。どれも Rust 側で値を決め、窓の側は描くだけにする（architecture-rules ルール 3）。

1. **見えの度合い v（`state.rs`）**: `Stage` に、止まりの移り変わりの始まり（`idle_since`・格子の時刻 1 つ）と、止まりを返してよいかのしるし（`armed`・`paused`）を足す。v は次の式で `state()` のたびに決める。列も履歴も持たない。
   - `armed` が偽、または `paused` が真なら v = 0。
   - `is_idle` が偽なら v = 0。
   - そうでなければ v = min(1, (grid_t − idle_since) / rise_ms)。
   - 戻りは Rust では v を即 0 にする。見た目の戻りは、窓の側が今も行っている 250 ms の線形の補間に任せる（ライブの遅れ 500 ms と合わせて、設計案の候補 0.3 秒に近い）。戻りの長さを別の値で振りたくなったら、そのとき状態を 1 つ足す（今は足さない）。
   - `idle_since` は「`is_idle` が初めて真になった格子の刻み」。各刻みの後と早送りの直前に `is_idle` を見て決め、偽に戻れば消す。早送りでも `advance_to` の呼び方でも同じ値になる。
   - `armed` は `Stage::new` で偽、`press` で真になる。一時停止が始まると偽に戻す。こうすると、起動の直後・戻した直後（`Stage` を作り直す）・一時停止の間・一時停止が明けた後（判断 2）が、どれも「最初の打鍵まで v = 0」になる。
2. **自律の動き（新しい `analysis/handmark/ambient.rs`）**: 純関数 `ambient(seed, t_ms, cfg) -> [f64; 3]`。
   - 絶対の時刻の 1 秒ごとの節 n（`t_ms / 1000`）に、`splitmix64(seed ^ splitmix64(n ^ チャネルの定数))` から [−1, 1] の値を作る。
   - 時刻 t の値は、t から窓 W（候補 10・20・30 秒）以内の節を、両端で 0 になる重み（二乗した余弦の窓）で足し合わせ、重みの和で割ったもの。節の順に整数で回すので、浮動小数の順序も決まる。
   - 窓より離れた 2 つの時刻は同じ節を使わない。このため、記憶は作りで W に切れる（ADR-056 D2 の (ii)）。`grid_start` も周期の関数も使わない（(iii)・D2）。
   - 3 チャネルは、3 つの形（帯の変位・粒の漂い・風の向き）の入力に使う。`seed` は `Stage::new` が今も受けている日の種（`Evaluation::draw_seed()`）をそのまま使う。
3. **研究者用の切り替え**: 環境変数 `GSE_HANDMARK_STOPPED` を、`GSE_DEBUG` が立っているときだけ読む。設定がなければ切っておく（参加者の配布物の既定）。形式の例: `form=band;rise_ms=2000;window_s=20;strength=0.5`。
   - 読むのは `lib.rs` で、純関数 `parse_stopped_cfg(Option<&str>, debug: bool) -> StoppedCfg` に渡す（`GSE_DISABLE_PROBES` と同じ形）。駆動役が `Stage` を作るときに渡す。
   - 切っているときは `StageState` の `v` と `ambient` が常に 0 で、形の番号も「なし」になる。窓の側の描画は今と同じになる。
   - 描画の側に環境変数の門を置かない（`handmark_edge_strip.rs:5` の方針）。形と強さは `StageState`（または `OpenWindow`）で Rust から渡す。

## 変更対象ファイル

- `src-tauri/src/analysis/handmark/state.rs` — `Stage` に `idle_since`・`armed`・`paused`・`cfg` を足す。`StageState` に `v: f64`・`ambient: [f64; 3]`・`form: u8`・`strength: f64` を足す。`bits()` を伸ばす。`set_paused(t, paused)` を足す（先に `advance_to(t)` を呼ぶ）。`replay`・`replay_live` に一時停止の列と `cfg` を渡す版を足す（今の署名は「一時停止なし・切っている」の版として残す）。
- `src-tauri/src/analysis/handmark/ambient.rs`（新規）と `mod.rs` — 自律の動きの純関数と、その単体テスト。
- `src-tauri/src/handmark_driver.rs` — `cfg` を持つ。`on_paused` で、一時停止の始まりと終わりの時刻を打鍵と同じ待ちの列に入れ、`tick` で `target` 以下になったものを時刻の順に `stage.set_paused` に流す。こうすると、ライブの 500 ms の遅れの規則と再生が一致する。
- `src-tauri/src/lib.rs` — 環境変数を読んで駆動役へ渡す（数行）。
- `src/components/HandmarkStage.tsx`・`handmarkStageDraw.ts` — 受ける型に 4 つの項目を足し、3 つの形を描く。どれも `v × strength × ambient` で描き、止まりの長さで大きさ・速さ・明るさ・数を変えない。
- `src/components/HandmarkEdgeStrip.tsx`・`handmarkStripFrame.ts` — 受ける型にだけ足して、描画は変えない（下の「決めてほしいこと」1）。
- `src-tauri/src/analysis/handmark/desk.rs`・`src-tauri/src/bin/replay.rs`（`write_frame`）・`experiments/20261115-handmark-leak-desk/scripts/pixels.mjs` — 再生に一時停止の列（`DeskFile.pauses`・既に記録から読んでいる）と `cfg` を渡す。B_state に v と ambient の列を足し、コマの書式に足して `DESK_VERSION` を上げる。
- 新しい `experiments/20261121-handmark-stopped-desk/` — 経過が読めない (i)〜(iii) の確かめ（下の「テスト戦略」2）。reproducibility-discipline に従う。
- `docs/functional-design.md`・`docs/glossary.md` — 止まりの表示と用語（見えの度合い・自律の動き）を足す。

## 既存パターンとの整合

- 乱数は `state.rs` の `splitmix64` を使う。新しい crate は足さない。
- 格子と早送りは今の `advance_to` に乗る。v は格子の時刻から決めるので、早送りで状態が変わらないという今の性質（`drift` と同じ扱い）を保つ。
- 待ちの列で時刻の順に流すのは、打鍵の `pending` と同じ形にする。
- 環境変数は、`lib.rs` で読んで純関数に渡す形にする（`GSE_DISABLE_PROBES`・`GSE_HANDMARK_TABLE`）。
- 机上の道具は、`stream_samples`（`desk.rs:724`）で Rust 側から描き直し、`pixels.mjs` で画面と同じ `handmarkStageDraw.ts` を使って描く。今の流れに項目を足すだけにする。

## テスト戦略

1. **単体テスト（`cargo test --manifest-path src-tauri/Cargo.toml --workspace`）**。requirement の受け入れ条件 1〜6 に対応する。
   - v: 移り変わりの後は一定で、止まりが 1 分でも 1 日でも同じ bits になる。境界の 4 つ（起動・戻し・一時停止の間・一時停止明け）で v = 0。
   - `idle_since`: 早送りと素朴な 1 刻みずつの進め方で一致する（今の `fast_forward_matches_the_naive_step_loop_including_long_gaps` を v まで含めて伸ばす）。`advance_to` を何回に分けても、立ち上がりの途中で bits が一致する。
   - ambient: `grid_start` をずらしても、同じ時刻なら同じ値になる。W より離れた 2 つの時刻は節を共有しない（関数の中の節の範囲で確かめる）。値の範囲は [−1, 1]。日の種を変えると値が変わる。
   - ライブと再生: 駆動役のテスト（`handmark_driver.rs:942` 付近の一致の検査）に、一時停止を挟む場合と、日付の切り替え・時計の飛びの場合を足す。
   - マウスだけを使う間（打鍵なし）は、ポインタの跡が今どおり出て、ambient が計算されている。ただし `armed` が偽なので v は 0 になる。ADR-056 D7（打鍵が 1 回来るまで返さない）に合わせた読みで、設計案 §4.4 の確かめ方 1 の「両方が出る」は「打鍵が 1 回あった後に、マウスだけを使う間」と読む（下の「決めてほしいこと」2）。
   - 切っているとき: `v`・`ambient` が 0 で、今の 4 つの項目の bits が変わらない（今のテストが通る）。
2. **机上の確かめ（研究者の手元の記録で・外部の LLM に送らない）**。
   - 本人の段 1 の記録を、研究者用の設定（形ごと・W ごと）で描き直す。立ち上がりと W より長い止まりについて、移り変わりが終わった後のコマを取り出す。
   - (i) 1 枚の見た目、(ii) 数十秒ぶんの時系列、(iii) 同じ時系列から `grid_start` からの経過、を推す予測器を作る。止まりの単位でまとめた交差検証で当て、ラベルを止まりの単位で入れ替えた帰無の分布と比べる。
   - 合否の基準の案: 観測の当てやすさ（順位相関）が、帰無の分布の 95 パーセント点を超えないこと（片側 5%）。値は研究者が決める（「決めてほしいこと」3）。
   - 見た目は、今ある基層（`drift` の霧と粒）・ポインタの跡・自律の動きを合わせた最終の画（`pixels.mjs` のコマ）から取る。基層が (iii) で落ちたら、研究者に確かめる（tasklist）。
   - 漏れの検査（ADR-051 D3）: 今の手順を、v と ambient を入れた B_state・B_pixel で回す。
3. **手動の確かめ**: 研究者のデバッグ起動で、3 つの形が出ることと、切っているとき何も変わらないことを見る。研究者自身の数日ずつの試しは次のタスク（判断 5）。

## 決めてほしいこと（承認のときに）

1. **帯（`HandmarkEdgeStrip`）にも出すか**。推奨は「今回は窓（`HandmarkStage`）だけ」。机上の道具の B_pixel は `handmarkStageDraw.ts` で描いていて、帯の描画は確かめ方の外にあるため。
2. **マウスだけを使う間の読み**。推奨は「打鍵が 1 回あった後なら両方出る」。ADR-056 D7 が「少なくとも 1 回の打鍵が来た後に限る」としているので、起動してからマウスだけの間は v = 0 になる。
3. **(i)〜(iii) の合否の基準**。推奨は、止まりの単位の入れ替えの帰無に対して片側 5%（観測が 95 パーセント点を超えたら「偶然を上回った」）。ADR-056 には基準の数字が無い。
4. **作業の分け方**。推奨は PR を 2 本にすること。PR-a は Rust の状態・自律の動き・駆動役・窓の描画・切り替えで、既定では切っているので参加者には何も変わらない。PR-b は机上の道具の拡張と確かめの結果。

## 調べた事実（2026-11-21）

- 一時停止の間の打鍵は、手跡に届かない（`lib.rs:5778` の `!crate::recording::is_paused()`）。ADR-056 D7 の前提が成り立つ。
- 一時停止を `Stage` は知らない。駆動役の `self.paused` だけが持ち、一時停止の間も `stage.advance_to` と `Effect::State` は続く（`handmark_driver.rs:470-488`）。再開で `Stage` を作り直すのは、一時停止の間に起点を取り直した場合（`stage_restarted`）だけ（`handmark_driver.rs:361-380`）。
- 駆動役に渡る一時停止の時刻と、記録の `recording_pause` の行の時刻は、同じ `now` である（`lib.rs:3386`・`:3400`・`:3404`）。刻みの側の `on_paused(fs, is_paused(), wall)`（`lib.rs:2686`）は、コマンドの経路で既に合わせてあれば何もしない。ほかの経路で一時停止が変わったときに時刻がずれうるので、実装で確かめる。
- 再生（`desk.rs`）は一時停止の区間を `DeskFile.pauses` として既に読んでいる。ただし、使っているのは窓を除くことだけで、`Stage` の再現には使っていない。
- `StageState` は schema（`schema_dto.rs`・`current.json`）に入っていない。項目を足しても schema の差分は出ない。
- 構造体を完全に書き下している箇所は `state.rs:224` と `bin/replay.rs:5421`・`:5443`。コマのバイナリの書式は `bin/replay.rs:2195-2215` と `pixels.mjs:36-59` に、オフセットを直書きしている。
- TS の受ける型は `HandmarkStage.tsx:55` と `HandmarkEdgeStrip.tsx:41` の 2 か所にある。窓の側は、受けた値を 250 ms で線形に補間している（`HandmarkStage.tsx:181-184`）。
