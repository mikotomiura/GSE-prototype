# EH3 の配布物

EH3（肖像と招待の参加者内比較・`experiments/20261011-portrait-eh3/`）の配布物を作る・配るときの手順と記録。
O1 の配布タグ（`docs/o1-distribution-tag.md`）と G1 の配布タグ（`experiments/20260801-controlled-friction-task/distribution-tag.md`）とは分ける（R-D1）。

> **2026-11-07: EH3 は研究として実施しない（ADR-049）。** 配布物は作らず、配らない（§1 の条件がそろうことも待たない）。下の手順は、研究者が試しに EH3 のモードを立てるときと、その片付けの記録として残す。

## 1. まだ配っていない

2026-10-11 の時点で、EH3 に使ってよいリリースタグは無い。次がそろってから最初の節を足す。

- 事前登録の凍結（`experiments/20261011-portrait-eh3/preregistration-draft.md` の §10 を埋め、attack-me と `/cross-review` 2 巡を通す）。
- 形の文法（F-1）と招待の図像（F-3）を研究者が選び、配布物に反映する（図像は `src/components/Overlay.tsx` の `INVITATION_GLYPH`、文法は印の `grammar=` と `drift=`）。
- 同意文書と participant-guide の確定（記録項目の案は `experiments/20261011-portrait-eh3/consent-items-draft.md`）。
- Windows と macOS の実機の確認（`.steering/20261011-portrait-eh3-impl/tasklist.md` の PR3・PR4）。

## 2. 配布フォルダの印

EH3 は O1 の収集の器の上で動くので、配布フォルダには **`o1.mode` と `eh3.mode` の両方**を置く。`eh3.mode` だけでは EH3 は立たない（applog に警告が 1 行出る）。

`eh3.mode` の中身は、その参加者の割り当て 1 行である（`src-tauri/src/eh3.rs` の `parse_assignment`）。

```text
order=E,D,A;a_first=seed;grammar=raw;drift=none
```

| キー | 値 | 意味 |
|---|---|---|
| `order` | `E`・`D`・`A` の並び（3 つを 1 回ずつ） | ブロックの順序（`E` = 空・`D` = 日替わりの地模様・`A` = その回の形） |
| `a_first` | `none` / `seed` | A ブロックの初日の終わりの扱い（以後、日ごとに交互） |
| `grammar` | `raw` / `lattice` | 形の文法（F-1 で研究者が選ぶ） |
| `drift` | `none` / `diffuse` | 形の上書きの型（F-1 と一緒に選ぶ） |

- 割り当ての表（参加者ごとの `order` と `a_first`）は凍結の前に `SEED` から作り、ハッシュを記録する（稿 §2.1・F-10）。
- 中身が読めない・不正なら EH3 は立たない（既定の条件を勝手に選ばない）。applog には値を含まない 1 行が出る。
- 参加者 ID は O1 と別の名前空間で振る（例: `E` で始める）。提出物の名前は O1 と同じ規則で、研究者の側で `meta.eh3_mode` によって O1 の記録と分ける。

## 3. 期間の終わり・やめたときの片付け

- 壁紙: 期間の後になった時点（または EH3 の印を外した後の起動）で、アプリが元の壁紙に戻し、`~/.gse/eh3_wallpaper_original.json` と `~/.gse/eh3/` を消す。アプリを消す前に戻っていることを参加者に確かめてもらう（アプリを消した後では戻せない）。
- 自動では消えないもの: `~/.gse/eh3_state.json`（稼働日の日付と割り当て）と `~/.gse/eh3_invitation.json`（招待の設定）。案内に場所と消し方を書き、終わりの連絡のときに消してもらう。
- 配布フォルダの `eh3.mode`（割り当ての平文）も、フォルダごと消してもらう。

## 4. 試してから配るとき

同じ PC で `GSE_EH3_MODE` を使って試すと、`~/.gse/eh3_state.json`（数えた稼働日）と `~/.gse/eh3_invitation.json`（招待の設定）が残る。稼働日の台帳は割り当ての書式を持っていて、別の割り当てで読むと何も割り当てない（途中の日から始まらない）が、配る前に次を消しておく。

- `~/.gse/eh3_state.json`
- `~/.gse/eh3_invitation.json`
- `~/.gse/eh3_wallpaper_original.json` と `~/.gse/eh3/`（残っていれば、先に EH3 の印を外して 1 回起動すると元の壁紙へ戻してから消える）
