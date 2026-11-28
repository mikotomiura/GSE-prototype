# 設計: windows-pointer-raw-input

## 根本原因（診断で確かめる・結果は下の「診断」）

`observe_windows.rs` の観測スレッドのループは、`PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE)` で `WM_INPUT` を含む全部のメッセージを取り除き（`DispatchMessageW` → `DefWindowProcW`）、その後に `GetRawInputBuffer` を呼ぶ。

- `GetRawInputBuffer` は「the raw input messages data found in the calling thread's message queue」を読み、読んだ分の `WM_INPUT` をキューから取り除く。
- 先に `PeekMessageW(..., 0, 0, PM_REMOVE)` で `WM_INPUT` を取り除くと、その raw input は `GetRawInputBuffer` から見えなくなる（`DefWindowProcW` が後始末するだけ）。残るのは、Peek の後から `GetRawInputBuffer` までの短い間に届いた分だけになる。ループは 5 ms 眠るので、眠っている間に届いた分は次の Peek で捨てられる。
- これは「ゼロではなく少しだけある」こととも合う。

## 修正方針（最小限）

*Using Raw Input* のバッファ読みの手本と同じく、`WM_INPUT`（0x00FF）を dispatch せず、前後の 2 つの範囲だけで `PeekMessageW(..., PM_REMOVE)` する。

- `pump_messages_except_raw_input()` として関数に切り出す（テストで縛るため）。範囲は `0..=WM_INPUT-1` と `WM_INPUT+1..=0xFFFF`（`wMsgFilterMax = 0` は「全部」の意味になるので、後ろの範囲の上限は 0 にしない）。
- WinEvent（`WINEVENT_OUTOFCONTEXT`）のコールバックは `WM_INPUT` 以外の経路で駆動されるので、フォーカスの行は変わらない見込み（直した版の確かめで測る）。
- 読み出し・量子化・捨てるもの（`hDevice`・`ulExtraInformation`・座標・向き）は変えない。

## 変更対象ファイル

- `src-tauri/src/input/observe_windows.rs` だけ

## テスト戦略

1. 回帰テスト（CI の windows でも走る・入力のデスクトップに依らない）: 自スレッドのメッセージ専用窓に `WM_INPUT` と `WM_USER` を `PostMessageW` し、`pump_messages_except_raw_input()` の後に `WM_INPUT` がキューに残り、`WM_USER` は取り除かれていることを `PeekMessageW(PM_NOREMOVE)` で確かめる。直す前の形（`0, 0`）では `WM_INPUT` が残らず赤になる。
2. 実機の確かめ（`#[ignore]`・手元だけ）: `SendInput` で相対の移動（±1 px を 4 ms ごと）を 3 秒入れ、直す前と直した後の形で `GetRawInputBuffer` の件数を比べる。注入した入力は打鍵（`keybd_event`）と違い raw input には届く見込み。届かなければ研究者にマウスを動かしてもらう。
3. 実アプリの確かめ: 一時フォルダの `USERPROFILE`/`GSE_DATASET` で O1 を起動し、マウスを 1 分動かして `pointer_bin` の行の数を数える（中身は出さない・行の数だけ）。フォーカス遷移の行も出ること。
4. `cargo test --workspace`・clippy。

## 診断（2026-11-27・G-GEAR・Windows 11 Home 26300）

1. 使い捨ての `#[ignore]` テスト（消した）で、同じプロセスにメッセージ専用窓と `RIDEV_INPUTSINK` を登録し、`SendInput` で ±1 px の相対の移動を 4 ms ごとに 3 秒入れ、ループの形だけを替えて `GetRawInputBuffer` の件数を数えた。
   - 今の形（`PeekMessageW(.., 0, 0, PM_REMOVE)`）: 入れた 675 件に対して 0 件
   - 手本の形（`WM_INPUT` の前後の 2 範囲）: 入れた 677 件に対して 677 件
   → 仮説どおり。原因はメッセージのループで確定した。注入した移動は raw input に届く（打鍵の `keybd_event` と違う）。
2. 直した版の実アプリ（`npx tauri dev`・`GSE_O1_MODE=1`・`USERPROFILE` と `GSE_DATASET` は scratchpad・本物の記録に触れない）で、研究者が実際のマウスを約 60 秒動かし、途中で前面を切り替えた。数えたのは種類ごとの行の数だけ（中身は出していない）。
   - `pointer_bin` 32 行（14:56:39Z〜14:57:27Z の約 48 秒・途中に登録の画面での打鍵がある）
   - `focus_transition` 2 行（フォーカスの行は直した形でも出る）
   - 起動から研究者が戻るまでの約 8 時間は `pointer_bin` 0 行・`focus_transition` 0 行。研究者はその間 G-GEAR のマウスを使っていない（離席・Mac を使っていた。2026-11-28 に AskUserQuestion で確かめた）ので、0 行と矛盾しない
   - 動かした秒の数そのものは測っていない（研究者の申告は約 60 秒・途中に登録の画面での打鍵がある）。32 行は「動かした秒の数に近い」と読むが、厳密な比は出していない
   - 直す前の版の実アプリは測っていない。直す前の量は O1 の 3 人の集計（打鍵 4.8 万に対して 424 など）と、上の 1 の 0 件で代える。

## レビューの採否（Step G）

- code-reviewer MEDIUM 1（WinEvent が保たれる根拠）: 実アプリでフォーカスの行が出ることを確かめ、コメントの根拠を実測に替えた。
- code-reviewer MEDIUM 2・security-checker LOW 1（`GetRawInputBuffer` の失敗で `WM_INPUT` が溜まる）: 失敗したら 1 回だけ警告し、溜まった `WM_INPUT` を既定処理へ渡して捨てる（`discard_queued_raw_input`）。
- code-reviewer LOW（後ろの範囲の上限）: `0xFFFF` → `u32::MAX`。
- code-reviewer LOW（`dispatch` が safe）: `unsafe fn` にして `# Safety` を書いた。
- code-reviewer LOW（テストの役割分担）・security-checker LOW 2（注入が本物の O1 に混ざる）・UIPI: テストの doc とメッセージに書いた。
- 採らなかったもの: drop guard・`RIDEV_REMOVE`（テストのプロセスの中だけで害がない）。

## /cross-review の採否（2026-11-28・Codex の実消費 60,994）

Claude の系統は、cross-reviewer がサブエージェントを起動できなかったため、cross-reviewer 自身が読んだ（code-reviewer の定義どおりの独立のレビューではない）。Step G の code-reviewer と合わせて 2 回の Claude の目が入っている。

- 両者一致（中）実機テストが送った件数を縛っていない: `sent >= 450` と、緩い上限（届いた移動量が送った件数の 2 倍以下）を足した。
- 両者一致（低）失敗時の後始末のテストが無い: `discard_removes_queued_wm_input` を足した（API を失敗させる手段が無いので後始末の関数だけを縛る）。
- Codex（中）`PeekMessageW` の上限に `u32::MAX` は契約の外: Step G で 0xFFFF から `u32::MAX` にしたのを 0xFFFF に戻した（メッセージの値は 16 ビットの範囲）。戻した形で `#[ignore]` の実機テスト（本番と同じ回し方と読み方）を回し直して緑。
- Codex（中→低）`GetLastError` を取らない: 警告に `Error::from_win32()` を添えた。バッファを広げて再試行する案は採らない（マウスだけ・16 KiB で不足は起きにくい）。
- Codex（低）動かした秒の数が不明: 上の診断 2 に書いた。
- Claude（低）警告が 1 回だけ: 保留（1 行は残る・続く失敗は行の数で見える）。

## 配布のときに書くこと

Windows の既存の被験者では、これまでほぼ記録されていなかった `pointer_bin` が記録され始める（中身は量だけで変わらない・`meta.capabilities` はもともと宣言済み）。配る版の変更の記録（`docs/o1-distribution-tag.md` など）に書く（security-checker の勧め）。
