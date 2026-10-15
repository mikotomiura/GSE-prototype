> 2026-10-16: **置き換え済み**。`next-session-eh3-pre-freeze-f1-and-separation.md`（EH3 の凍結の前の準備）に分け方の検査を写して 1 本にまとめた（研究者の指示）。こちらは使わない。

# 引き継ぎ: 肖像と招待の分け方を機械で守る検査

作成 2026-10-15（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-portrait-separation-check.md を読んで、EH3 の配布物の固定との順序を研究者に確かめてから、/start-task で検査を足すタスクを立てて。
```

## 1. 背景

- タスク `.steering/20261015-tangibility-design/` の判断 2・16（研究者・2026-10-15）。
- 肖像（`src-tauri/src/analysis/portrait/`・`wallpaper*.rs`）と招待（`analysis/invitation.rs`）を分けることは EH3 で設計と実装に入っている。生成器の入力（`generator.rs` の `Second`）は推定を受け取る欄を型として持たない。ただし、`analysis/portrait/` のモジュールが `engine`・`invitation`・`p_stuck` に依存しても赤になる検査は無い（2026-10-14 にコードで確かめた・引き継ぎ `next-session-tangibility-design.md` §1）。
- 将来の画面端の小面（判断 10・16）にも同じ門を当てる。

## 2. 決めること・やること

1. EH3 の配布物の固定（タグ）との順序。EH3 のファイルの近くに触れるので、固定の後か前かを研究者に確かめる。
2. 検査の形: Rust の単体テストで `analysis/portrait/` のソースに `engine`・`invitation`・`p_stuck`・`level` の参照が無いことを確かめる、`scripts/` の静的検査にする、など。`architecture-rules`・`rust-standards` を読む。
3. 参照の検査だけでは、呼び出し側が推定の結果で更新を起こす・止める経路を拾えない（`/cross-review` の Codex の指摘）。「材料にも契機にも使わない」を守るには、同じ打鍵・時計・操作の列に対して推定の値（`p_stuck` など）だけを変えても、形と更新の時刻が変わらないことを確かめる振る舞いの検査も要る。
4. 陽性対照: 参照を 1 行足す・推定で更新を止める分岐を 1 つ足すと、それぞれの検査が赤になることを確かめる（壊して赤を見る）。
5. Windows の CI で走ることを確かめる（macOS の手元の検査は Windows 固有のコードを通さない）。
