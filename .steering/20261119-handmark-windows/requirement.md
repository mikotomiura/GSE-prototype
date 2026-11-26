# 手跡の Windows 版（handmark-windows）

## 背景

- 段 1 の後期の手跡は、まず macOS だけで main に入った（ADR-051 D1・判断 P・v0.1.42）。Windows の参加者の「あり」の日は、日ごとの行に「出せなかった理由」を書く形のままである。
- Windows 版は何も書かれていない。OS ごとに書き分けが要るのは次の 3 つで、どれも `#[cfg(target_os = "macos")]` に閉じている。
  - 背景の層の窓 `src-tauri/src/handmark_stage.rs`
  - 下の縁の帯 `src-tauri/src/handmark_edge_strip.rs`
  - ポインタの一点の読み `src-tauri/src/input/handmark_pointer_macos.rs`（Windows 版のファイルが無い）
  - 駆動役（`handmark_driver.rs`）・割付・日ごとの行・`analysis/handmark/` は OS に依存しない。`lib.rs` の `run_handmark_effects` は Windows では窓の出来事を捨てている。
- ADR-050 は Proposed のままで、Accepted の条件 (a)「Windows の位置とクリックの読みを確かめる」が済んでいない。
- 引き継ぎ: `origin/docs/gse-meta-before-run1:.steering/_handoff/next-session-gse-handmark-windows.md`（写しは同じディレクトリの `handoff-source.md`）。
- 始めたきっかけ: 研究者の判断で先に始める（2026-11-19・Windows の参加者はまだ決まっていない）。

## ゴール

1. Windows で手跡を出す方法を実機（G-GEAR・Windows 10.0.26300）で確かめ、背景の層の候補を研究者が選べる材料を出す。
2. 研究者が選んだ方法で、Windows 版の背景の層・帯・ポインタの読みを本番の形で実装し、main に merge する。

## スコープ

### 含むもの
- 確かめ（使い捨ての試作で測る。試作のコードは main に入れない・ADR-051 D7 の先例）
  1. 背景の層の 3 候補: WorkerW の下への差し込み／最前面でクリックを通す透過の窓／動かない壁紙の更新（`IDesktopWallpaper`）。それぞれ、成り立つか・画面共有に写るか・CPU。
  2. 帯をタスクバーの上に出せるか（全画面・タスクバーを自動で隠す設定・多画面）。
  3. ADR-050 の条件 (a): `GetCursorPos`・`GetAsyncKeyState(VK_LBUTTON)` を権限なしで読めるか。クリックの陽性対照は研究者の手で取る（合成の入力で代えない）。
- 研究者が候補を選ぶための停止点（結果と推奨を出して止まる）。
- 本番の実装: `input/handmark_pointer_windows.rs`・背景の層と帯の Windows の実装・`lib.rs` の配線・両 OS に対のテスト・ADR-050 D3 の境界の検査の Windows への拡張（キーボードの仮想キーを読まないことを含む）。
- ADR-050 の条件 (a) を閉じる補訂と、ADR-051 D1 の補訂。
- PR → CI 緑 → merge。

### 含まないもの
- ホイール（ADR-050 D7・Windows では使わない）。
- 版の更新と配布（v0.1.43 など）。別のタスク。
- ADR-050 を Accepted にすること（条件 (b) は macOS 側・研究者が決める）。
- 24H2・25H2 など別の版の Windows での確かめ（この機械の版を記録し、別の版は未確認として残す）。
- Windows の参加者の日を解析でどう扱うか（事前登録の改訂で決める・ADR-051 D1）。
- 机上の道具（ADR-051 D3）の Windows の記録への適用。

## 受け入れ条件

- [ ] 確かめの結果（候補ごとの成り立ち・画面共有・CPU、帯、条件 (a)）が OS の版とともに `results.md` にある。
- [ ] 研究者が背景の層の候補を選び、`decisions.md` に記録されている。
- [ ] Windows 版の背景の層とポインタの読みが本番の形で入り、Windows の実機で手跡が出ることを研究者が目で確かめた。
- [ ] 帯は従: 出せない画面の構成では背景だけを出し、理由を 1 行残す（Mac と同じ約束）。
- [ ] ADR-050 D3 の境界の検査が Windows のファイルにも効き、陽性対照で赤になることを確かめた。`GetAsyncKeyState` にマウスボタン以外の仮想キーを渡さないことを検査している。
- [ ] `cargo test`・clippy・tsc が手元と CI（Windows・macOS）で緑。
- [ ] ADR-050 の補訂（条件 (a)）と ADR-051 D1 の補訂がある。
- [ ] PR が merge され、main の CI が緑。

## 関連ドキュメント

- `docs/adr/ADR-050-handmark-input-not-recorded.md`（D3・D4・D6・D7・補訂 1）
- `docs/adr/ADR-051-handmark-in-stage1-late-period.md`（D1・D4・D7）
- `.steering/20261108-handmark-to-main-plan/`・`20261109-handmark-pr3-pointer/`・`20261112-handmark-pr2-edge-strip/`
- 枝 `docs/tangibility-design` の `.steering/_handoff/next-session-handmark-window-boundary.md`・`next-session-handmark-expression-design.md`・`next-session-handmark-input-adr.md`・`next-session-handmark-stage-pointer.md`
- 先例: `src-tauri/src/wallpaper_windows.rs`（`IDesktopWallpaper`）

## 運用メモ
- /reimagine 適用: Yes
- 理由: 背景の層の出し方（3 候補）はアーキテクチャの選択で、最良が自明でない。確かめの結果が出て研究者が候補を選んだ後、本番の実装の design.md を書いた段で `/reimagine` を回す。
