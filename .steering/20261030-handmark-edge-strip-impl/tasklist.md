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
- [x] `handmark_reveal.rs` と順番の純粋な関数・テスト
- [x] トレイの「背景を見る / 戻す」・やめたときの知らせ・状態に合わせた文字
- [x] `shutdown()` で戻す
- [x] 実機で隠す・戻す（研究者に先に聞く）（run8: 位置・隠して戻す・Dock から 1 つ戻す。全画面の中ではトレイに届かず、やめる道筋は未確認＝判断 7）
- [x] 全画面の中で帯を画面の下端に置く（判断 6・run9 で研究者の目視）

## 仕上げ
- [x] cargo test --workspace・clippy・tsc・gse-replay --snapshot 1 回（968 件・警告なし・tsc 0・15 snapshots 一致）
- [x] code-reviewer + security-checker（review.md・HIGH 2 件を直し、Cmd+Q と近さを実機で確かめた）
- [x] /finish-task（/cross-review 必須）・コミット・push まで（PR なし）

## 次のタスクへ回すもの

- GSE を軽い処理で動かす設計の検討（run11 で重い処理の間は前に出られなかった・研究者の提案）
- logger.rs の recv_timeout が待ち時間 0 で回る件（main にも同じ行）
- 覆われたら描くのを止めることの実機の確かめ
