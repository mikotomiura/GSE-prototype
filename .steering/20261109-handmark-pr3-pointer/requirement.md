# 手跡の PR 3 —— カーソルとクリック（handmark-pr3-pointer）

## 背景

- ADR-051 D7 の PR 3。PR 1（1a #401・1b #402・main a1ab71fa）で、段 1 の後期を始められる最小の切れ端（割付の表・`handmark_day`・入口の門・状態の純関数・背景の層（打鍵だけ）・やめる／描く）が入った。
- ADR-051 D2 は、カーソル・左クリックを手跡の入力に入れると決めた。ADR-051 D5 は、ライブの契約（状態は打鍵の列・ポインタの入力・種・時刻の純関数で、固定の刻みで進め、描画の回数に依らない）と、再生の契約（同じ関数のポインタの口に `pointer_bin` の 1 秒の量からの近似を入れる）を分けた。
- ADR-050 D2〜D4 と補訂 1 は、ポインタの入力を記録しない・溜めない・送らないことと、その検査（型・境界・振る舞いの 3 層・陽性対照）を決めた。
- 材料は試作の枝 `spike/handmark-stage`（worktree `/Users/johnd/GSE-prototype-handmark-stage`・読むだけ）。引き継ぎは `.steering/_handoff/next-session-gse-handmark-pr3.md`。

## ゴール

macOS の段 1 の後期で、手跡の背景の層がカーソルの位置と動き・左クリックに応じて動く。ライブと再生が同じ Rust の関数を通り、ポインタの値は記録・送信・推定のどこにも流れないことが検査で縛られている。

## スコープ

### 含むもの
- 16ms ごとに一点を読む（`NSEvent.mouseLocation`・`pressedMouseButtons` の最下位ビット・権限なし・フックなし）。`input/` に O1 の `observe*.rs` と別のファイルで置く（ADR-050 補訂 1 の項目 1・2）。
- 戻っていく値（草の押し・粒のずれ）を Rust の固定刻み（16ms）の状態で計算する。打鍵の 0.5 秒遅れの積分器とは別にし、ポインタには遅れを入れない（判断 1）。
- 波紋の 6 枠は窓（TSX）の側に置く（ADR-050 D4）。年齢は時刻で決める。
- 再生の口: `pointer_bin` の 1 秒の量から、描画の種で決めた合成の軌跡と等間隔の押下を作り、同じ関数に入れる（判断 2）。
- トレイに入力ごとの入れ切り（カーソル・クリック）を入れ、切った・戻した時刻を `handmark_day` に記録する（schema の変更・gse-dataset の同期の PR）（判断 3）。
- 記録の一時停止の間は、カーソル・クリックとも切ったのと同じに扱う（世代を進めて跡を消す・読まない）（補訂 1 の項目 8）。
- ADR-050 D2〜D4 の検査をポインタの経路まで広げる（陽性対照つき）。試作の `scripts/handmark-stage-trace.test.mjs` の 9 件を写す（ホイールに関わる分は除くか、PR 5 に回すと記録する）。

### 含まないもの
- ホイール（PR 5・ADR-050 の条件 (b) の実測の後）
- 帯（PR 2）・「背景を見る」（PR 6）・日の問いの項目（PR 7）
- 机上の描き直しと予測器の比べ（PR 4）。PR 3 は再生の口の写像と、その決定性のテストまで
- Windows 版（ADR-051 D1）

## 受け入れ条件

- [ ] `cargo test --workspace`・clippy（`-D warnings`）・fmt・`tsc --noEmit`・`node --test` が緑
- [ ] 同じ入力（打鍵・ポインタの列・種）からビット単位で同じ状態が出る性質のテスト。描画の回数（advance の呼び方）で状態が変わらないテスト
- [ ] 再生の口（`pointer_bin` → 合成の入力 → 状態）が決定的であるテスト
- [ ] ADR-050 D3 の検査がポインタの型・読みのスレッド・窓の受け取りに及び、各検査に陽性対照がある。守りを外す変異で赤になることを確かめる
- [ ] 一時停止・入力ごとの切り・全体のやめるで、跡が消え、遅れて届いた値で戻らないテスト
- [ ] 入力ごとの切った・戻した時刻が `handmark_day` に入り、区間の削除で消える。`emit_schema` の出力が `schema/current.json` と一致し、gse-dataset の同期の PR を出す
- [ ] 画面の確かめ（PR 1 の判断 11 と同じ段取り・研究者が gse-next を止めた時間に）: カーソルで近くの草がなびき粒が寄る、左クリックで波紋、入力ごとの切りが効く
- [ ] code-reviewer・security-checker・/cross-review（Codex を加える）

## 関連ドキュメント

- `docs/adr/ADR-051-handmark-in-stage1-late-period.md` D2・D3・D5・D7
- `docs/adr/ADR-050-handmark-input-not-recorded.md` D2〜D6・補訂 1
- `.steering/20261108-handmark-stage1-late-pr1/decisions.md` 判断 1〜11
- `.steering/_handoff/next-session-gse-handmark-pr3.md`

## 運用メモ
- /reimagine 適用: Yes
- 理由: ポインタの積分器と打鍵の積分器の分け方、再生の合成の軌跡の作り方に複数の案がありうる。ライブと再生の契約は PR 4 の判定の土台になるので、設計を 2 案で比べる（研究者が選んだ・2026-11-09）。
