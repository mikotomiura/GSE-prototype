# 確かめの手順（研究者の手が要る所）

試作の実行ファイル（scratchpad・使い捨て）:

```
C:/Users/johnd/AppData/Local/Temp/claude/bb8fe8b6e5b059fc/81b94973-1d4c-44b8-984b-829aacaf7512/scratchpad/spike-target/debug/handmark-win-spike.exe
```

以下では `SPIKE` と書く。Claude Code の入力欄で `! SPIKE ...` の形で打つと、結果が会話に残る。

## 1 回目: 位置とクリック（ADR-050 の条件 (a)）

各回 20 秒。始めたらすぐにクリックを始める。数えた回数は覚えておく（結果の `press_edges` と比べる）。

| # | コマンド | 20 秒の間にすること | 期待 |
|---|---|---|---|
| a1 | `! SPIKE probe-pointer normal 20` | ふつうの速さで左クリックを 10 回（メモ帳など、ふつうの窓の空いた所） | press_edges=10 |
| a2 | `! SPIKE probe-pointer fast 20` | できるだけ素早く、短く左クリックを 10 回 | press_edges=10（取りこぼしがあれば lsb_only を見る） |
| a3 | `! SPIKE probe-pointer elevated 20` | 先にタスク マネージャーを開いておき、その窓の中で左クリックを 10 回 | press_edges=10 なら、昇格した窓の前でも読める |
| a4 | `! SPIKE probe-pointer locked 40` | 始めたら Win+L で画面をロックし、ロック画面で 5 回クリックしてから解除する（解除はクリックを使わず PIN などで） | ロック中は 0（pos_fail が増えるかも見る） |

カーソルを動かした量は `pos_changed`（変わった刻みの数）だけが出る。位置そのものは出ない。

### 1 回目の結果（2026-11-19・G-GEAR・Windows 10.0.26300・昇格なし・Per-Monitor DPI aware v2）

| # | 読み/秒 | press_edges | lsb_only | down_reads | pos_changed | pos_fail | 備考 |
|---|---|---|---|---|---|---|---|
| idle（空回し・10 秒） | 61.3 | 0 | 1 | 0 | 0 | 0 | lsb_only の 1 は起動直後の読みの名残り |
| a1 normal | 61.4 | 11 | 1 | 185 | 641 | 0 | 10 回＋焦点を合わせるクリック 1 回の見込み |
| a2 fast | 61.0 | 11 | 0 | 39 | 134 | 0 | 押下 1 回あたり平均 3.5 読み（約 57ms）。取りこぼしなし |
| a3 elevated | 61.2 | 0 | 0 | 0 | 491 | 0 | 昇格したタスク マネージャーが前面の間、位置は読めるがクリックは 0（UIPI） |
| a4 locked | — | — | — | — | — | — | 飛ばした: ロックすると VS Code が消えて Claude Code のセッションが落ちる（研究者・2026-11-19）。ロック中の扱いは本番の設計で守る |

## 2 回目: 背景の層（後で示す）
## 3 回目: 下の縁の帯（後で示す）
