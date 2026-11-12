# 手跡の PR 2 —— 下の縁の帯と見えていた時間（handmark-pr2-edge-strip）

## 背景

- ADR-051 D7 の PR 2。PR 1（1a #401・1b #402）と PR 3（#403・main 1d020fe3）で、段 1 の後期の背景の層（打鍵の風・カーソルとクリックの跡）・割付の表・`handmark_day`・入口の門・入力ごとの入れ切りが main に入った。
- 背景の層はデスクトップの高さにあり、普段の配置ではほとんど見えない。全画面の中では一切見えない。設計のタスク（枝 `docs/tangibility-design` の `.steering/20261029-handmark-edge-strip-design/` 判断 3〜7）は、画面の下の縁に、本体の窓 1 枚（非アクティブの NSPanel）の帯を常に出すと決めた。試作（枝 `spike/handmark-stage`・`handmark_edge_strip.rs`・`HandmarkEdgeStrip.tsx`・`.steering/20261030-handmark-edge-strip-impl/`）で、全画面の上に出ること・Dock の上端に沿わせること・全画面では下端に置くことを確かめた。
- ADR-051 D4 は日ごとの行に「出ていた時間・見えていた時間」を求める。`handmark_day.visible_ms` の欄は 1a で作り、計り方が決まるまで常に `null` にしてある。
- 引き継ぎ: `.steering/_handoff/next-session-gse-handmark-pr2.md`。

## ゴール

macOS の段 1 の後期で、手跡が出ている間、画面の下の縁に 14pt の帯が出て、背景と同じ Rust の状態（風）で動く。帯が覆われていなかった時間が `handmark_day.visible_ms` に日ごとに入る。描画は入力のあるとき 30 回／秒・無いとき 10 回／秒、完全に覆われたら止まり、描画の回数は状態に影響しない。

## スコープ

### 含むもの
- 帯の窓: 14pt・非アクティブの NSPanel・浮く層・全 Space・全画面の上・クリック透過・焦点を取らない。主画面の `visibleFrame` の下端（Dock の上端）に沿い、全画面の窓があるときは画面の下端に置く（試作の判断 5・6）。開け閉めは背景の窓と同じく駆動役の出来事だけで決める（入口の門・やめる・一時停止・日の割付に従う）。
- 帯の中身: 風で揺れる線 1 本・薄い霧 1 本・粒を少し（設計の判断 5）。状態は背景と同じ `StageState` を Rust から受ける（判断 1）。
- カーソルの近さ: Rust のポインタのスレッドが帯への近さを 0〜1 の数 1 つにして帯の窓へだけ送り、帯は近いほど薄くなる。トレイで「カーソル」を切った日・一時停止の間は送らない（判断 2）。
- 描画の回数: 入力のあるとき 30 回／秒・無いとき 10 回／秒。帯が全部覆われたら描かない。WKWebView の間引き（PR 3 の判断 12）とぶつからないようにする。
- 見えていた時間: 出ている間、帯の `occlusionState` が見えている時間を足し、`handmark_day.visible_ms` に書く（判断 3）。
- `lib.rs`・`tray.rs` の配線は main に合わせて書き直す（ADR-051 D7）。
- ADR-050 D2〜D4 の検査（イベント名・窓の列・payload の型）を帯の窓まで広げる（陽性対照つき）。

### 含まないもの
- 「背景を見る」（他のアプリをどける・PR 6）。試作の `handmark_reveal.rs` は写さない。
- ホイール（PR 5）・机上の道具（PR 4）・日の問いの項目（PR 7）・Windows 版（ADR-051 D1）
- 計測の仕掛け（`GSE_HANDMARK_EDGE_STRIP_OFF` などの環境変数の入口・確かめ用の `tracing` の行）（ADR-051 D2）
- 帯だけの入れ切り（帯は手跡が出ている間いつも出す・設計の判断 5 の論点 4）

## 受け入れ条件

- [ ] `cargo test --workspace`・clippy（`-D warnings`）・fmt・`tsc --noEmit`・`npm run test:handmark`（node）が緑
- [ ] 帯の描画の回数（30／10／止める）が状態に影響しないこと、帯が背景と同じ状態を受けることをテストで縛る
- [ ] `visible_ms` の足し方（出ている間だけ・覆われていない間だけ・日付の変わり目・区間の削除）をテストで縛り、守りを外す変異で赤になる
- [ ] ADR-050 D3 の検査が帯の窓とイベントに及び、各検査に陽性対照がある
- [ ] `emit_schema` の出力が `schema/current.json` と一致する。schema の文が変わったら gse-dataset の同期の枝を出す
- [ ] 画面の確かめ（PR 1 の判断 11・PR 3 と同じ段取り・研究者が gse-next を止めた時間に）: 帯が Dock の上端に沿って出る／全画面のアプリの上で画面の下端に出る／打鍵で線が揺れる／カーソルが近づくと薄くなる／覆うと描画が止まる／`visible_ms` が覆った時間だけ `shown_ms` より少ない
- [ ] CPU（1 コアの割合を累積の秒の差で測る・memory: macos-top-l2-undercounts-cpu）: 帯の有無で差をとり、覆った間に増え続けないこと
- [ ] code-reviewer・security-checker・/cross-review（Codex を加える）

## 関連ドキュメント

- `docs/adr/ADR-051-handmark-in-stage1-late-period.md` D2・D4・D5・D7
- `docs/adr/ADR-050-handmark-input-not-recorded.md` D1〜D6・補訂 1
- `.steering/20261108-handmark-stage1-late-pr1/decisions.md`・`.steering/20261109-handmark-pr3-pointer/decisions.md`
- 試作: `/Users/johnd/GSE-prototype-handmark-stage/src-tauri/src/handmark_edge_strip.rs`・`src/components/HandmarkEdgeStrip.tsx`・`.steering/20261030-handmark-edge-strip-impl/`
- 設計: 枝 `docs/tangibility-design` の `.steering/20261029-handmark-edge-strip-design/decisions.md` 判断 3〜7

## 運用メモ
- /reimagine 適用: No
- 理由: 帯の形は設計のタスク（判断 3・4）と試作（判断 5・6）で実機で確かめて決まっている。今回は main の形への写し替えが中心で、写し替えの選択肢は判断 1〜3 で閉じた（研究者・2026-11-12）。
