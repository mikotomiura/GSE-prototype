# G-GEAR のセッション: Windows でポインタの行がほとんど記録されない理由を確かめて直す（3 名の前）

作成: 2026-11-26（Mac・`.steering/20261126-mhd-input-candidates/` 判断 1）。Windows の実機での確かめと直しは G-GEAR で行う。

## 見えていること（Mac で集計と文書で確かめた）

- O1 の Windows の 3 人（配列 `00000411`）は、打鍵の行に対してポインタの行（`pointer_bin`）がほとんど無い（打鍵 4.8 万に対して 424 など）。macOS の本人は 20 万行。フォーカス・貼り付け・IME の行は 3 人とも残っている。`meta.capabilities` には `pointer_bin` が宣言されている（設置は失敗していないと見られる）。
- `src-tauri/src/input/observe_windows.rs` の観測スレッドのループは、毎回 `PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE)` で `WM_INPUT` を含む全部のメッセージを取り除いて `DispatchMessageW`（`wnd_proc` は `DefWindowProcW`）してから、`GetRawInputBuffer` で読んでいる。
- Microsoft の文書:
  - `GetRawInputBuffer` は「the raw input messages data found in the calling thread's message queue」を読み、「corresponding WM_INPUT messages are removed from the calling thread's message queue」。
  - *Using Raw Input* のバッファ読みの手本は「WM_INPUT messages are intentionally never dispatched through DispatchMessage」とし、`PeekMessageW(&msg, NULL, 0, WM_INPUT - 1, PM_REMOVE)` と `PeekMessageW(&msg, NULL, WM_INPUT + 1, 0xFFFF, PM_REMOVE)` で `WM_INPUT` を飛ばし、`GetRawInputBuffer` に残す。
- 仮説（未確認）: 先に `WM_INPUT` を取り除くので、`GetRawInputBuffer` には、取り除いた後の数ミリ秒に届いた分しか残らない。行がゼロではなく少しだけあることとも合う。

## やること（/fix-bug の順で）

1. 今の版で、マウスを 1 分動かしたときの `pointer_bin` の行の数を数える（回帰の材料）。
2. 回帰テストを先に置く（Windows だけのテストは `#[cfg(target_os = "windows")]`・CI の windows で走ることを確かめる）。メッセージのループを関数に切り出して、`WM_INPUT` を取り除かないことを縛る形を考える。
3. ループを文書の手本の形（`WM_INPUT` の前後の 2 つの範囲で `PeekMessageW`）に直す。WinEvent のコールバックは `WM_INPUT` 以外のメッセージで駆動されるので、フォーカスの行が減らないことも確かめる。
4. 直した版でマウスを 1 分動かし、行の数が macOS と同じ桁（動かした秒の数に近い）になることを確かめる。打鍵・フォーカス・IME の行が変わらないこと。
5. 3 名の版の配布物に入れる（配る前の条件に「Windows でポインタの行が記録される」を足すかは研究者に聞く）。

## 守ること

- 座標を持たない・量だけ（ADR-014 D4・`data-privacy`）。`hDevice` と `ulExtraInformation` は今どおり捨てる。
- 本人の段 1 の記録の中身を出さない。push と PR は研究者に確かめてから。
- 11 月は Actions の含まれる分を使い切っている（12-01 に戻る）。CI の windows が走らないときは G-GEAR の手元の `cargo test` と実機で確かめ、そう記録する。
