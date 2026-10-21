# 設計（Claude の作業）

研究者の判断は decisions.md にある。ADR-040 は `/Users/johnd/GSE-prototype-tangibility/docs/adr/ADR-040-handmark-input-not-recorded.md` から読む（判断 2）。

## 1. 形

```
NSEvent.mouseLocation / pressedMouseButtons      （input/handmark_pointer_macos.rs・OS の API はここだけ）
        │ 16ms ごとに一点（判断 7）
        ▼
PointerReader（input/handmark_pointer.rs・OS に依らない）
  最後の一点と左の押下の前の値だけ。変わったときだけ PointerUpdate を返す
        │
        ▼
handmark_stage_pointer.rs（読みのスレッド・入れ切り・世代・窓への配送）
  PointerUpdate → 数だけの payload → emit_to("handmark-stage", "handmark-stage-pointer")
        │
        ▼
HandmarkStage.tsx（描画）＋ handmarkStageTrace.ts（跡の枠と受け取りの判定・DOM を持たない）
```

- 型（D3）: `PointerSample` と `PointerUpdate` は `Debug`・`Display`・`Serialize` を持たない。窓へは `handmark_stage_pointer.rs` の専用の関数で数だけの payload にする。payload の型はこのファイルの外へ出さない。
- 境界（D3）: OS の API を呼ぶのは `input/handmark_pointer_macos.rs` だけ（`input/` の中・O1 の `observe*.rs` とは別のファイル）。`analysis/` に置かない。`handmark_stage_spike.rs`（窓の用意・トレイ・`tracing` を使う）はポインタの値の型を知らない。`handmark_stage_pointer.rs` は `tracing` を使わない。
- objc2-app-kit 0.3.2 の `NSEvent::mouseLocation()`・`pressedMouseButtons()` は `unsafe` でもメインスレッドの印を取る宣言でもない（`src/generated/NSEvent.rs:1142・1150`）。読みのスレッドから直接呼ぶ。`modifierFlags` などキーボードの状態は読まない。
- 座標: `mouseLocation` は主画面の左下が原点の Cocoa の座標。そのまま送り、窓の側で `innerHeight - y` に直す（窓は主画面の全体を覆う）。主画面の外の点は窓の側で使わない。
- 時刻と世代（D4）: payload は読みのスレッドが始まってからのミリ秒と、入れ切りの世代を持つ。入れ切りのたびに世代を 1 つ進め、新しい世代の「切った」payload を送る。窓の側は古い世代の payload を捨て、時刻のずれが最小のずれより 250ms 以上遅れた payload も捨てる（描画が止まっていた間に溜まったもの）。
- 入れ切り（判断 5）: トレイの「カーソル」「クリック」。両方を切ると読みのスレッドは OS を読まない（取得を止める）。窓は切ったと知ったら、その入力の跡（草の押し・粒のずれ・波紋の枠）をすぐ消す。
- 合成の入力（判断 4・ADR-040 判断 7）: `GSE_HANDMARK_STAGE_SPIKE_SYNTH_POINTER=1` のとき、OS を読まず、決まった円を描くカーソルと 2 秒ごとのクリックを作る。負荷の計測はこれか、ポインタを切った条件で行う。

## 2. 描画（判断 3）

- 見本 Version 5 の `handmark-nature-multi.html` の霧・草・粒・波紋・打鍵の風を `HandmarkStage.tsx` に移す。壁紙の絵・作業の窓の絵・欄は移さない（実物の壁紙と窓がある）。
- 大きさ: 見本は仮想の画面（高さ 900 を基準に `S = H / 900`）。実物では `H = innerHeight`（CSS px）。canvas は `devicePixelRatio`（上限 2）。
- 跡の枠と受け取りの判定（波紋の 6 枠・世代と時刻の判定・切ったときの消去・寿命を過ぎた枠の消去）は `src/components/handmarkStageTrace.ts` に DOM なしで置き、`node --test` でテストする（package.json にテストの道具が無いので、Node 22 の型の除去で `.ts` を直接読む。`scripts/` に置き tsc の対象にしない）。
- 霧は入力に依らず漂うので、描画のループは止まらない（判断 3 のトレードオフ）。「動きを減らす」設定は見本どおり基層と粒の流れだけを 0.3 倍。
- 窓の側から `invoke` を外し、計測の CSV と `handmark_stage_tick`・`handmark_stage_measure_enabled` を消す（判断 4）。打鍵の payload から `measure` を外す。

## 3. 検査（ADR-040 D3 の対応表の行き先ごと）

すべて `cargo test` で走る（`handmark_stage_pointer.rs` のテスト）。窓の側の TS は `include_str!` で読む。

| 行き先 | 検査 | 陽性対照 |
|---|---|---|
| 型 | `PointerSample`・`PointerUpdate` が `Debug`・`Display`・`Serialize` を実装しないこと（固有の定数と trait の定数の解決の差で、実装の有無を値にして調べる） | 実装している型（`f64`）で真になる |
| NDJSON・applog・`tracing` | ポインタの 3 ファイルの本体（テストとコメントを除く）が `LogEntry`・`tracing`・`log_tx`・`POINTER_TX`・`println`・`eprintln`・`dbg!` を含まない。振る舞い: 合成のサンプルで配送の関数を回し、`tracing` の行が 0 | 文字列は実行時に組み立てた本文で赤。振る舞いはわざと出す版で 0 でない |
| 提出物 | `logger.rs`・`schema_dto.rs`・`submission.rs`・`packaging.rs` が型の名前・payload の名前・イベント名を含まない | 同上 |
| 計測のファイル | 3 ファイルが `std::fs`・`File`・`OpenOptions` を含まない。振る舞い: 配送を回しても `gse-handmark-spike/` に何も増えない | 同上 |
| ネットワーク | Rust の 3 ファイルが `TcpStream`・`UdpSocket`・`reqwest`・`ureq`・`hyper` を含まない。窓の 2 ファイルが `fetch`・`XMLHttpRequest`・`WebSocket`・`EventSource`・`sendBeacon` を含まない | 同上 |
| 窓の保存と返送 | 窓の 2 ファイルが `invoke`・`@tauri-apps/api/core`・`localStorage`・`sessionStorage`・`indexedDB`・`caches`・`cookie`・`postMessage`・`emit` を含まない | 同上 |
| 他の窓への配送 | ポインタのイベント名は `handmark_stage_pointer.rs` と窓の 2 ファイルの外に現れない（`src/` の全 TS と `src-tauri/src/` の全 Rust を見る）。`handmark_stage_pointer.rs` は `.emit(` を使わず `emit_to` だけ | 同上 |
| 推定 | 3 ファイルと窓の 2 ファイルが `analysis`・`engine`・`invitation`・`p_stuck` を含まない | 同上 |
| 列（D4） | Rust の 3 ファイルが `Vec`・`VecDeque`・`HashMap`・`BTreeMap`・`HashSet`・`LinkedList`・`BinaryHeap` を含まない。窓の 2 ファイルの配列・表の作り（`[]`・`Array.from`・`new Array`・`new Map`・`new Set`・`.push(`）は、名前の一覧（`presses`・`blades`・`motes`・`ripples`）の外に無い | 一覧に無い名前で作る本文で赤 |
| 境界 | macOS のファイルが読むのは `mouseLocation`・`pressedMouseButtons` だけ（`modifierFlags`・`keyCode`・`CGEventTap`・`addGlobalMonitor` を含まない）。`handmark_stage_spike.rs` は `PointerSample`・`PointerUpdate` を含まない | 同上 |

- 対照の文字列は `concat!` ではなく `format!` などで実行時に組み立て、検査対象のファイルにもテストのファイルにも禁じる語をそのまま書かない（gate-green-but-artifact-broken の 4 型目）。
- 「止められないもの」は ADR-040 の表のまま（数に取り出した後に別名の関数へ渡すこと等）。レビューで見る。

## 4. D4 のテスト

- Rust: `PointerReader` は最後の一点と左の押下の前の値だけを持つ（構造の検査は上の列の行）。同じ点では `None`・動けば `moved`・左の 0→1 だけで `clicked`（1→1・右は数えない）。切ったら `reset` で前の点と押下を捨てる（入れ直した最初の一点で `moved` も `clicked` も出さない）。両方を切った間は読みの関数を 1 回も呼ばない（呼んだ数を数える偽の読みで確かめる）。入れ切りで世代が進む。
- 窓の側（`node --test`）: 枠は 6 で増えない。寿命（1.6 秒）を過ぎた枠は、入力が来なくても掃除の呼び出しで位置と時刻が消える。切ったら全部の枠が消える。古い世代と遅れた payload を捨てる。

## 5. ホイールの確かめ（D7）

- 権限なしの ad-hoc 署名の .app と、権限のある対照で、聞くだけの CGEventTap（`scrollWheel`）に届くかを数える（20261020 design.md §2 と同じ形・tap の生存も見る）。スクロールは合成で入れる。
- 取れなければホイールは入れない。取れても、権限が要るなら実物へ入れるかは研究者に聞く（D7 の条件「O1 の記録の経路と同じ場所を通らない」を満たすかを添えて）。

## 6. 負荷の計測

- `load-run.sh` を元に、3 条件: (a) ポインタを切り合成の打鍵、(b) 合成のポインタと合成の打鍵、(c) 何もしない 60 秒。CPU は外から（`cpu-sum.py`）。人の手の入力は使わない。
- 計測の一時ファイル（本体の記録の `ds-*`）は測った後に消す。描画の回数はもう取れない（判断 4）。

## 7. 試視

- `manual-check.md` の形で手順を書く。Claude が起動して「開始する」を押せる（`env -u GSE_HANDMARK_SPIKE_MEASURE`）。見るところ: 見本と同じ（どの動きがどの手から来たか・騒がしさ・止めたら静まるか）に、実物の壁紙と窓の重なり・トレイの入れ切り。
