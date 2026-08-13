# タスクリスト — 瞬時 A/B 盲検の提示手順を直す

## 調査（完了）

- [x] 一次資料で `abxBlindNext` / `abxAnswer` / `buildAbxOrder` を読む
- [x] ★ 穴 2 を**実測**する（`abxSet("A")` が 400 → 106（150 ms）→ 100 の跳びを作る）
- [x] ★ 穴 3 を**実測**する（`buildAbxOrder(20260813, 8)` が 3 回とも同一・研究者の `truth` 列と一致）
- [x] ★ 研究者データの指紋を確認（誤り 3 件が「直前 diff」の 3 トライアルと完全一致）
- [x] ★ 穴 4（遷移時間軸との相互作用）を設計中に発見
- [x] 無効になった測定を `results/…__pre-boundary-fix.json` として保存

## 実装

- [ ] `step4.config.json`: `order_seed` 削除 ＋ `prep_seconds: 3.0` 追加（理由コメント付き）
- [ ] `player/step4.html`: `drawOrderSeed()` / `abxPrepSeconds()`
- [ ] `player/step4.html`: `abxBlindStart` が seed を引いて `abx.blind.orderSeed` に持つ
- [ ] `player/step4.html`: `abxBlindNext` を 3 相化（`abxPhase` ＋ 世代カウンタ）
- [ ] `player/step4.html`: `state().abx.blind` に `phase` / 残り時間 / `orderSeed` を出す
- [ ] `player/step4.html`: 結果 JSON に `order_seed` / `prep_seconds` を足す
- [ ] `player/step4.html`: 所要時間の表示を 3 相に合わせて直す
- [ ] `player/step4.html`: 中止経路が相の途中でも効く

## 検査（★ 書いたら必ず壊す）

- [ ] 新規検査: `prep_seconds` が config にあり 0 より大きい
- [ ] 新規検査: `order_seed` が config に**無い**（固定 seed を戻していない）
- [ ] 新規検査: `buildAbxOrder` の引数が**引き直した seed**である
- [ ] 新規検査: `abxSet("A")` が **1 区間目の開始より前**にある（★ 位置で見る・BF-5 の教訓）
- [ ] 新規検査: 準備区間が `遷移秒 + 2` を下回らない（★ 穴 4）
- [ ] 新規検査: 3 相の文言が画面に出る
- [ ] 新規検査: 結果 JSON に `order_seed` / `prep_seconds` が入る
- [ ] 新規検査: 盲検の提示に**音の印を足していない**（AB-D3）
- [ ] ★ **上の各件に meta 変異を 1 件ずつ**足し、**壊すと赤くなることを実測**

## 実地の実測（★ ブラウザ）

- [ ] AC-5: `bash run.sh check` が exit 0
- [ ] AC-2: 4 相の文言を実測
- [ ] AC-3: ② を 2 回開始し order が異なる／`order_seed` が JSON に入る
- [ ] AC-1 / AC-4: 背景サンプラで「跳びが prep の中」「1 区間目が rate_min で定常」を実測

## レビュー・完了

- [ ] `code-reviewer` ＋ `security-checker` を並列起動
- [ ] `notes.md` に **S5-11** として記録（★ 既存の実測値は 1 文字も書き換えない）
- [ ] `/cross-review`（⚠️ 実データを diff に含めない）
- [ ] `/finish-task`

## ★ 完了状況（2026-08-13 実測）

| 項目 | 状態 |
|---|---|
| 穴 1〜4 の修正 | ★ **完了**（実装 ＋ 検査 ＋ meta 変異） |
| ★ 穴 5（AB-D7・準備区間の跳びが真値を漏らす） | ⚠️ **部分的**（★ 周辺確率は消したが**同時確率が残る** → AB-D10） |
| ★ 穴 6（AB-D9・contrast_measurable） | ★ **完了**（★ 対照条件の見落としも cross-review で修正） |
| AB-D8 の 3 件（安全機構が到達不能） | ★ **完了**（中止ボタン新設 / `stop()` から中止 / `lockUI` 追加） |
| AC-1 / AC-2 / AC-3 / AC-4 / AC-5 / AC-6 | ★ **すべて実測で PASS** |
| 機械検査 | ★ **121 ok / meta 152 ok / 平滑器 51 / Step 3 30 / 混入 0 異常・exit 0** |
| `code-reviewer` ＋ `security-checker` | ★ **完了**（HIGH 6 / MEDIUM 6 → 反映済み。CRITICAL 0） |
| `/cross-review`（Claude ＋ Codex） | ★ **完了**（★ **Codex が AB-D10 を発見**） |
| notes への記録 | ★ **S5-11〜S5-31** |

## ⚠️★★★ 本タスクで**閉じなかった**もの（★ 次セッションの入口）

- **AB-D10**: ★ 準備区間の**跳びの偶奇**が入場状態（＝直前トライアルの真値）を一意に決める。
  ★ **候補 3 案と代償は `decisions.md` AB-D10 に記載。★ 研究者判断で選ぶ。**
  ★ **既存の 8/8 は漏れだけでは説明できない**（★ 期待点 4.80/8 と算出）が、⚠️ **点数は上振れしうる。**
- ⚠️ **AB-D9 の「断る枝」は実地で未実測**（条件を作れなかった。meta 変異で赤は確認済み）
- ⚠️ **`stop()` からの盲検中止は静的検査のみ**（実測すると音が止まり再開に実クリックが要るため）

## ★ 修正後にやること（本タスクの外・Step 5 本題へ戻る）

- [ ] ★ 0.5 で①を **3 回連続**測る（AB-D5 の食い違いの短時間の揺れを見る）
- [ ] ★ 0.5 を**測り直す** → 0.25 → 0.125 → 0
- [ ] ★★★ 閾値の倍率で **10 分の B1**
