# 手跡の背景の層の試作に、カーソルとクリックを持ち込む（ADR-040 の見直しを含む）

## 背景

- 手跡の自然世界の見本は、打鍵に加えてカーソル・クリック・ホイールを表現の入力に使う形で固まった（枝 `docs/tangibility-design` の `.steering/20261020-handmark-multi-input/` 判断 2・10〜12・見本 Version 5 https://claude.ai/artifact/4FCokjbqZd13PXgVw2MkSg ）。
- 「表現には使うが記録しない」とその境界は ADR-040（Proposed・枝 `docs/tangibility-design`）で決めた。Migration は、実物へ持ち込むタスクの最初に D3 の検査を書き、持ち込んだ後に ADR を見直すとしている。
- 背景の層の試作（この枝 `spike/handmark-stage`・`.steering/20261016-handmark-stage-spike/`）は、等高線の波を描き、窓はマウスを受けない。計測のために窓が毎秒 `invoke` で描画の回数を返している（ADR-040 D2・D3 とぶつかる）。
- 引き継ぎ: 枝 `docs/tangibility-design` の `.steering/_handoff/next-session-handmark-stage-pointer.md`。

## ゴール

背景の層の窓に見本 Version 5 の自然世界を描き、カーソルの位置とクリックを Rust の側で描画のたびに一点読んで窓へ渡す。ADR-040 の D2〜D4 を検査とテスト（陽性対照つき）で固定し、研究者が実物の画面で見たうえで ADR-040 を見直す。

## スコープ

### 含むもの

- ADR-040 D3 の検査（行き先ごとの止め方と陽性対照）と D4 の「溜めない」のテスト
- macOS のカーソルの位置とクリックの取得（`NSEvent.mouseLocation`・`pressedMouseButtons`）と窓への配送
- 背景の窓の描画を、見本 Version 5 の自然世界（霧・草・粒・波紋・打鍵の風）に置き換える
- 窓の側から `invoke` を外す（計測の CSV をやめる）
- macOS でホイールを D7 の条件どおりに取れるかの確かめ（権限なし・権限ありの対照）。取れなければ入れない
- 負荷の計測（合成の入力か、ポインタを切った条件・外からの CPU）
- 研究者の試視
- ADR-040 の見直し（新しい節か新しい ADR かは研究者に聞く。ADR の本文は書き換えない）

### 含まないもの

- Windows の実装と実測（`GetCursorPos`・`GetAsyncKeyState`）。依頼文も書かない
- 多入力の伏せた見比べ
- O1 の `input/observe*.rs`・`analysis/pointer_bin.rs`・ADR-014 D4 のマスクの変更
- `analysis/portrait/`・`wallpaper*.rs`・`eh3.rs`・G-GEAR の `experiments/` への変更
- 本線へのマージ・PR（push まで）

## 受け入れ条件

- [ ] D3 の対応表の行き先ごとに、検査（またはテスト）があり、陽性対照で赤になることを確かめた。対照の文字列は実行時に組み立て、検査対象のファイルに書いていない
- [ ] D4: Rust の側は最後の一点だけを持つ。窓の側の枠は名前を決めた固定数で、寿命を過ぎたら位置と時刻を消し、入力を切ったら取得を止めて配送待ちを捨てる。これらをテストで固定した
- [ ] 窓の側のソースに `invoke`・ブラウザの保存先・`fetch` が無い
- [ ] 背景の窓に自然世界が描かれ、カーソルで近くの草がなびき粒が寄り、クリックで波紋が立つことを Mac で確かめた
- [ ] ホイールの確かめの結果を記録した（入れたか、入れなかったか）
- [ ] 負荷を合成の入力かポインタを切った条件で測り、人の手の描画の量を書いていない。計測の一時ファイルを消した
- [ ] 研究者の試視の結果を記録した
- [ ] ADR-040 の見直しを記録した
- [ ] `cargo test`・`cargo clippy`・`tsc` が緑。`/cross-review` を済ませ、push した

## 関連ドキュメント

- ADR-040（枝 `docs/tangibility-design` の `docs/adr/ADR-040-handmark-input-not-recorded.md`）
- `.steering/20261016-handmark-stage-spike/`（この枝）
- 枝 `docs/tangibility-design` の `.steering/20261020-handmark-multi-input/`・`.steering/20261021-handmark-input-adr/`

## 運用メモ

- /reimagine 適用: No
- 理由: 大きな形（型・境界・振る舞いの 3 層、`input/` に置く、描画のたびに一点）は ADR-040 で決まっている。残る分け方は design.md で案を並べて個別に聞く（研究者の回答・2026-10-21）
