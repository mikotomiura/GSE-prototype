# tasklist

## 段 1: 最小の帯と確かめ 1〜3
- [x] 帯の窓（`handmark-edge-strip`）を作り NSPanel 化・層・振る舞い・クリック透過・確かめ用の読みを tracing へ
- [x] `on_window_event` の分岐・capabilities・`main.tsx` の分岐・`HandmarkEdgeStrip.tsx`（線 1 本）
- [x] トレイ「背景を見る」で前面に出られるかを読むだけ（隠さない）
- [x] cargo build / test / clippy・tsc
- [x] 確かめ 1: テキストエディットの全画面の上（研究者に先に聞く）
- [x] 確かめ 2: ブラウザ・エディタの全画面の上
- [x] 確かめ 3: トレイから前面に出られるか（全画面の外と中）→ やめる判定を決める（AskUserQuestion）
- [x] 結果を results.md に

## 段 2: 風と帯の中身・負荷
- [x] `handmark_wind.rs`（純粋な計算・TS と同じ値のテスト）
- [x] 250ms のスレッドと `handmark-wind` の配布・`HandmarkStage.tsx` を受け取る形に
- [x] 帯の線・霧・粒・描く回数（33ms / 100ms）
- [x] 覆われたら止める（WebKit が止めるかは測らず、Rust が 250ms ごとに occlusionState を読んで知らせる形にした。覆われた状態は実機でまだ一度も出ていない＝止まることは未確認）
- [x] 帯への近さの数（`handmark_stage_pointer.rs`）・検査の `WINDOW` に帯を足す・陽性対照
- [x] 確かめ 4: 負荷（30・10 回/秒）
- [x] 研究者の目視（見え方）

## 段 3: どける操作
- [ ] `handmark_reveal.rs` と順番の純粋な関数・テスト
- [ ] トレイの「背景を見る / 戻す」・やめたときの知らせ・状態に合わせた文字
- [ ] `shutdown()` で戻す
- [ ] 実機で隠す・戻す（研究者に先に聞く）

## 仕上げ
- [ ] cargo test --workspace・clippy・tsc・gse-replay --snapshot 1 回
- [ ] code-reviewer + security-checker
- [ ] /finish-task（/cross-review 必須）・コミット・push まで（PR なし）
