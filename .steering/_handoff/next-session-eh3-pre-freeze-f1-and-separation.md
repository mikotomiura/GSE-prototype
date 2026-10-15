# 引き継ぎ: EH3 の凍結の前の準備 —— F-1 の見比べ → 分け方の検査（Mac）

作成 2026-10-16（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。AskUserQuestion には推奨と理由を添える。

このメモは `next-session-eh3-f1-wallpaper-viewing.md` と `next-session-portrait-separation-check.md`（どちらも 2026-10-15）を 1 本にまとめたもの（研究者の指示・2026-10-16）。2 本の中身はこのメモの §2・§3 に写した。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-eh3-pre-freeze-f1-and-separation.md を読んで、/start-task で EH3 の凍結の前の準備のタスクを立て、§2 の 1（画の作り方）を研究者と決めるところから始めて。
```

## 1. 背景と順序

- タスク `.steering/20261015-tangibility-design/`（ブランチ `docs/tangibility-design`・push 済み・PR なし）の判断 2・3・16・21。
- どちらも EH3 の配布物の固定（タグ）の前に要る。順序は **F-1 → 分け方の検査**。F-1 で文法を選ぶと `eh3.mode` の `grammar=`・`drift=` の既定の近くを触る可能性があり、分け方の検査も `src-tauri/src/analysis/portrait/` に足すので、並行するとぶつかる。固定の前に検査を入れれば、固定する版がその門を通る。この順でよいかは着手のときに研究者に確かめる。
- F-1 の見比べは研究者が数日かける。その間に別のセッション（別の worktree）で `next-session-tangibility-narrow-novelty-survey.md` を回してよい。触るファイルは重ならない。
- G-GEAR の作業（`next-session-tangibility-relative-timing-desk-check.md`）は G-GEAR で行い、このタスクに混ぜない。

## 2. 段 1: F-1 を自分の壁紙で数日見比べて選ぶ（判断 3）

- F-1 は形の文法（`raw` / `lattice`）と drift（`none` / `diffuse`）。見本のページ（`next-session-portrait-eh3-after-impl.md` の 19 行目にある研究者の非公開の artifact）はあるが、壁紙として日をまたいで見たときの慣れや読まれ方は分からない。`raw` の歩みは縁（左上の角）に寄って留まる（`.steering/20261011-portrait-eh3-after-impl/decisions.md` 判断 1・3）。
- 基準: 「予想しない形が返るか」と「良し悪しに見えないか」。EH2 と同じ扱いで参加者なし。
- 判断 14 の「全体の速さを割り引いた相対のタイミング」は将来の材料の仮説で、この見比べでは材料（F 系列）を変えない。

決めること:
1. 画の作り方: 判断 3 は「合成の列だけ」なので、既定は EH1 の `render_e18.py` 系で合成の列から静止画を作って手で壁紙に置く形（時計の更新は再現しない）。`eh3.mode` の `grammar=`・`drift=` で実物を回す形は研究者の打鍵が入るので、選ぶなら研究者が判断 3 の「合成の列だけ」を明示的に改める（EH2 と同じく本人の PC の中だけで、記録を外部の LLM に送らない）。
2. 日数と順序（候補 4 つを何日ずつ・どの順で）。
3. 記録の仕方（研究者のメモだけ。系に記録しない）。

## 3. 段 2: 肖像と招待の分け方を機械で守る検査（判断 2・16）

- 肖像（`src-tauri/src/analysis/portrait/`・`wallpaper*.rs`）と招待（`analysis/invitation.rs`）を分けることは EH3 で設計と実装に入っている。生成器の入力（`generator.rs` の `Second`）は推定を受け取る欄を型として持たない。ただし、`analysis/portrait/` が `engine`・`invitation`・`p_stuck` に依存しても赤になる検査は無い（2026-10-14 にコードで確かめた）。将来の画面端の小面にも同じ門を当てる。

やること:
1. 検査の形: Rust の単体テストで `analysis/portrait/` のソースに `engine`・`invitation`・`p_stuck`・`level` の参照が無いことを確かめる、`scripts/` の静的検査にする、など。`architecture-rules`・`rust-standards` を読む。
2. 参照の検査だけでは、呼び出し側が推定の結果で更新を起こす・止める経路を拾えない。同じ打鍵・時計・操作の列に対して推定の値（`p_stuck` など）だけを変えても、形と更新の時刻が変わらないことを確かめる振る舞いの検査も足す。
3. 陽性対照: 参照を 1 行足す・推定で更新を止める分岐を 1 つ足すと、それぞれの検査が赤になることを確かめる（壊して赤を見る）。
4. Windows の CI で走ることを確かめる（macOS の手元の検査は Windows 固有のコードを通さない）。

## 4. 守ること

- 合成の列だけを使う（§2 の 1 で研究者が改めない限り）。キーストロークの内容・NDJSON を外部の LLM（Codex を含む）に送らない。
- `git add -A` を使わない。並行するセッションとは worktree を分ける。
