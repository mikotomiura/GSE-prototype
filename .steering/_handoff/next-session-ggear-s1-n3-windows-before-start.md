# G-GEAR のセッション: 3 名を始める前の Windows の確かめと直し（ポインタの直し・カードの表示と答え方）

作成: 2026-11-27（Mac）。Windows の実機での確かめと直しは G-GEAR で行う。Mac 側は同意の承認の取り直し・解析の script・凍結を並行して進める。結果は記録の枝に書いて push し（研究者に確かめてから）、Mac 側はそれを fetch して読む。

## 枝

- カードの確かめ: `feature/s1-probe-window-wording`（K1 の文・作業の説明・作業のときの問いの順・ADR-055 補訂 1・ADR-057 補訂 1・2）。まだ main に入っていない。
- ポインタの直し: main から `fix/windows-pointer-raw-input` を切る（カードの枝とは別にする・どちらも main に入れてから配る版を作る）。

## 1 ポインタの行がほとんど記録されない（配る前の条件 15）

詳しい見立ては `docs/gse-mhd-input-candidates` の枝の `.steering/_handoff/next-session-ggear-windows-pointer-raw-input.md`（`git show origin/docs/gse-mhd-input-candidates:.steering/_handoff/next-session-ggear-windows-pointer-raw-input.md`）。要点:

- O1 の Windows の 3 人は、打鍵の行に対して `pointer_bin` の行がほとんど無い（macOS の本人は桁が違う）。フォーカス・貼り付け・IME の行は残っている。
- `src-tauri/src/input/observe_windows.rs` の観測のループは、`PeekMessageW(..., 0, 0, PM_REMOVE)` で `WM_INPUT` を先に取り除いてから `GetRawInputBuffer` を読んでいる。Microsoft の *Using Raw Input* のバッファ読みの手本は、`WM_INPUT` の前後の 2 つの範囲で `PeekMessageW` して `WM_INPUT` を残す。仮説は未確認。
- 手順は `/fix-bug`: 今の版でマウスを 1 分動かした行の数 → 回帰テスト（`#[cfg(target_os = "windows")]`）→ ループを手本の形に → 直した版で行の数が動かした秒の数に近く、打鍵・フォーカス・IME の行が変わらないこと。
- 座標を持たない・量だけ（ADR-014 D4・`data-privacy`）。`hDevice`・`ulExtraInformation` は捨てたまま。

## 2 カードの表示と答え方（配る前の条件 13・14）

カードの枝で作った版を段 1 の 3 名の形で動かし、デバッグの起動（`VITE_GSE_DEBUG=1` と `GSE_DEBUG=1` の両方・memory の debug-vs-participant-launch）で `debug_force_s1_probe`（`src-tauri/src/lib.rs`）からカードを出して確かめる。画面は自分で見る（memory の ui-changes-need-eyes）。

1. 見出し「カードが出る前の30秒について」と Q3「カードが出る前の30秒、何をしていましたか?」が、それぞれ 1 行に収まる（Mac の確かめ用の頁ではカードの幅 372 px で 1 行）。
2. 作業の説明「手を動かしていた（進んだかは問わない）。入力・編集・単純作業を含む」が読める（Mac では 2 行に折り返した）。
3. Q3 で作業を選ぶと、次に Q2「どれだけ前に進んでいる感覚ですか?」が見出し「（あと 2 問）」で出て、その次に Q1 が「（あと 1 問）」で出る。詰まり・熟考は Q1 → Q2 のまま。
4. 作業で Q2 だけ答えて閉じると、`realtime_label` の行が `q1_friction: null`・`q2_progress` ありで残る（記録の中身は出力しない・行の形だけ確かめる）。
5. 条件 14: Ctrl＋Alt＋数字で答えられる、2 分でキーが外れる、作業中のアプリに文字が入らない・フォーカスが動かない、キーを受け取れないときはボタンだけで答えられる。作業で Q2 が先に出る段でも、数字の割り当てが段どおり（1〜5）になる。

## 3 同じ回に Windows で確かめられる残り（同意文書の配る前の条件）

- 条件 4: どけた回数の記録（`reveal_count`）が Windows でも日ごとの行に入る。
- 条件 10: トレイの「やめる」「描く」が通知領域にあり、同意文書の書き方と合う。
- 条件 12: 一時停止中の後半の表示（出続けるか・操作に合わせて動くか）が §4 の 2 番の文と合う。

## 書き戻す先

- カードの確かめ: `feature/s1-probe-window-wording` の `.steering/20261127-s1-probe-window-wording/tasklist.md` と、同意文書の配る前の条件の表（`.steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md`）の出所の欄。
- ポインタの直し: `fix/windows-pointer-raw-input` に `.steering/<日付>-windows-pointer-raw-input/`。

## 守ること

- 本人の段 1 の記録の中身・個々の申告を出さない。NDJSON の生ログを外部の LLM に送らない（`/cross-review` の Codex には diff だけ）。
- push と PR は研究者に確かめてから。
- Actions の含まれる分は 12-01 に戻る。それまで CI の windows が走らないときは、G-GEAR の手元の `cargo test` と実機で確かめ、そう記録する。
