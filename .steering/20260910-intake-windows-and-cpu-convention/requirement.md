# requirement — Windows 実測の取り込みと CPU% 規約の決着

## 背景

`.steering/_handoff/next-session-prompt-intake-windows-and-continue.md` の指示で開始。
G-GEAR (Windows) 側が `feat/resumption-outcome-arbitration` に Windows 8h 実測を記録したが、
その中で **「Windows の CPU 平均 2.06 % は macOS 基準に換算すると 33.0 % で FAIL 相当」**
という主張が立てられている。根拠は `sample-windows.sh` の **コメント逐語**
（「Get-Counter は全コアに対する % を返す」）であり、⚠️ **一次資料でも実測でもない**。

## ゴール

1. ⚠️★★★ **CPU% の OS 間規約を決着させる**（Windows の `\Process(x)\% Processor Time` は
   1 コア = 100 % 基準か、全コア = 100 % 基準か）。
2. ★ 決着した規約を **コメントではなく meta/列** に残す（`sample-windows.sh` / `summarize.py`）。
3. ★ Windows 実測ぶんを main に取り込む（引き継ぎ §2 案 **B**: cherry-pick 先行、残りは後続 PR）。
4. ★ mac 側の残り: 起動時の山の 1 秒間隔計測 (B) / スリープ跨ぎ検証 (A) / ブランチ棚卸し (C・D)。

## 受け入れ条件

- [ ] CPU% 規約について **一次資料の逐語** と **Windows 実機の実測値** の両方が notes.md にある
      （⚠️ 実測が取れなければ「未実測」と明記する）
- [ ] `sample-windows.sh` / `sample-macos.sh` の出力に規約が機械可読な形で残る
- [ ] Windows 実測の steering / results が main に載る
- [ ] mac 側 A / B の結果が「見た / 見ていない」「期待どおり / 違った」で書かれている
- [ ] ⚠️ 「問題なし」と書かない。「N 件中 M 件を実測、未検証 K 件」で書く
