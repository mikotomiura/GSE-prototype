# windows-pointer-raw-input

## 背景

O1 の Windows の 3 人（配列 `00000411`）は、打鍵の行に対して `pointer_bin` の行がほとんど無い（打鍵 4.8 万に対して 424 など）。macOS の本人は 20 万行。フォーカス・貼り付け・IME の行は残っており、`meta.capabilities` には `pointer_bin` が宣言されている（Mac での集計・`.steering/20261126-mhd-input-candidates/` 判断 1）。

`src-tauri/src/input/observe_windows.rs` の観測スレッドは、毎回 `PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE)` で `WM_INPUT` を含む全部のメッセージを取り除いてから `GetRawInputBuffer` を読む。`GetRawInputBuffer` が読むのは呼び出し元スレッドのキューに残っている raw input だけなので、先に取り除くと、取り除いた後の数ミリ秒に届いた分しか残らない、という仮説がある（未確認）。Microsoft の *Using Raw Input* のバッファ読みの手本は `WM_INPUT` を dispatch せず、`WM_INPUT` の前後の 2 つの範囲だけで `PeekMessageW` する。

出所: `origin/docs/gse-mhd-input-candidates:.steering/_handoff/next-session-ggear-windows-pointer-raw-input.md`、`origin/main:.steering/_handoff/next-session-ggear-s1-n3-windows-before-start.md` §1（段 1 の 3 名の配る前の条件 15）。

## ゴール

Windows でマウスを動かした秒に `pointer_bin` の行が記録される（動かした秒の数に近い）。打鍵・フォーカス・IME の行は変わらない。

## スコープ

### 含むもの
- 今の版で、マウスを動かしたときの行の数を測る（回帰の材料）
- 回帰テスト（`#[cfg(target_os = "windows")]`）を先に置く
- メッセージのループを手本の形（`WM_INPUT` を残す 2 つの範囲）に直す
- 直した版で同じ測り方をして、行の数と他のチャネルを確かめる

### 含まないもの
- 座標・デバイス識別子を持つこと（ADR-014 D4・`data-privacy`。`hDevice`・`ulExtraInformation` は捨てたまま）
- macOS 側の変更
- カードの表示の確かめ（handoff §2・§3 は別の作業）
- 配る版を作ること（main に入れた後）

## 受け入れ条件

- [ ] 直す前の版で、マウスを動かした秒に対する行の数を記録した
- [ ] 回帰テストが直す前の実装で赤、直した後で緑（Windows・手元の `cargo test`）
- [ ] 直した版で、マウスを動かした秒に対する行の数が、動かした秒の数に近い
- [ ] フォーカス遷移の行が直した版でも出る
- [ ] `cargo test --workspace`・clippy が緑

## 関連ドキュメント

- docs/adr の ADR-014（D4 L-b ポインタ・D5 ゼロ抑制）
- `.claude/skills/hook-constraints`・`data-privacy`・`rust-standards`

## 運用メモ
- /reimagine 適用: No
- 理由: 原因の仮説と直し方（Microsoft の手本）が一次資料で決まっており、複数案の比較が要らない。仮説は診断の測定で確かめる（研究として強い方を自分で選ぶ・memory 11-23）。
