# 設計 — 瞬時 A/B 盲検の提示手順を直す

## アプローチ

★ **1 トライアルを 3 相にする。** 前トライアルの持ち越しを**採点区間の外**へ追い出し、境目を画面に出す。

```text
【いま】  [A 4.0 s] [A または B 4.0 s] → 回答
          ↑ ここに前トライアルの跳び（400→100）が乗る   ↑ 境目の印が無い

【これから】
          [準備中 3.0 s] [1 区間目 4.0 s] [2 区間目 4.0 s] → 回答
           ↑ abxSet("A") はここ           ↑ abxSet(kind) はここ
           ★ 跳びは採点区間の外           ★ 各相の名前と残り秒を画面に出す
```

## ⚠️★★★ 設計中に見つけた 4 件目の穴 — **遷移時間軸との相互作用**

★ `abxSet()` は **選択中の遷移時間を尊重する**（`dur: abxTrOpt().seconds`）。
→ ⚠️★★★ **`tr_60` では、準備区間の `abxSet("A")` が 60 秒かけてランプする。**
★ **準備 3.0 s では終わらないので、持ち越しが 1 区間目へそのまま漏れる。**

- ★ **今日の探索は `tr_0` だけ**なので今日は表面化しない。⚠️ **しかし遷移時間軸は「量と速度を切り分ける」
  ために作られた軸**（S4-D14 の次の一手）であり、★ **その最初の使用時に静かに壊れる。**
- ★ **解**: 準備区間を **`max(prep_seconds, 遷移秒 + 2)`** にする。
  ★ **これは既存の `abxSideSeconds()` とまったく同じ規則**（「遷移が終わる前に聴かせない」）であり、
  ★ **この repo に既にある型を再利用する**（S4-D15 が「既にある正しい型を新しい検査で使わなかった」と
  BF-4 を名指ししたのと逆をやる）。
- ★ **`tr_0` では `max(3.0, 2.0) = 3.0`** —— ★ **研究者が選んだ 3 秒がそのまま出る。**

## 変更対象

| ファイル | 変更 |
|---|---|
| `step4.config.json` | `layer2_rework.abx.blind`: `order_seed` を**削除**（＋戻さない理由）／`prep_seconds: 3.0` を追加 |
| `player/step4.html` | `drawOrderSeed()` 新設／`abxPrepSeconds()` 新設／`abxBlindStart` で seed を引く／`abxBlindNext` を 3 相化／`state()` に相を出す／結果 JSON に `order_seed` と `prep_seconds` |
| `scripts/step4_selftest.py` | 新規検査 ＋ **同数の meta 変異**（★ 壊して赤くなることを実測） |

⚠️ **触らないもの**: `buildGraph` / `LAYER0-CORE`（S4-D8）／`grain-processor.js`（BF-6 は S5-D10 で聴取の後）／
`blind_test.order_seed`（★ **B7 の別系統**。今回の対象ではない）。

## 実装の要点

### 1. seed を毎回引く（AB-D1）

```js
function drawOrderSeed() {
  return crypto.getRandomValues(new Uint32Array(1))[0];   // ★ 引いた値は必ず記録する
}
```

- `abxBlindStart`: `const orderSeed = drawOrderSeed(); const order = buildAbxOrder(orderSeed, B.trials);`
- `abx.blind.orderSeed = orderSeed` → 結果 JSON の `order_seed` へ
- ⚠️ **config から `order_seed` を消す** —— ★ **残すと「使われていない定数」ではなく
  「いつでも戻せる罠」になる**（★ 実際に今回それで踏んだ）。

### 2. 3 相にする（AB-D2 / AB-D3）

```js
async function abxBlindNext() {
  ...
  const kind = bl.order[bl.i];
  abxSet("A");                                   // ★ 準備区間の先頭で持ち越しを捨てる
  await abxPhase(bl, "prep", abxPrepSeconds() * 1000, "準備中（まだ判定しません）");
  await abxPhase(bl, "i1",   abxSideSeconds() * 1000, "1 区間目");
  abxSet(kind === "diff" ? "B" : "A");
  await abxPhase(bl, "i2",   abxSideSeconds() * 1000, "2 区間目");
  bl.phase = "answer";
  $("abx-choices").hidden = false;
}
```

- `abxPhase()` は **100 ms 周期で残り秒を `abx-blind-state` に書く**（★ 境目を画面で示す・AB-D3）
- ★ `bl.phase` / `bl.phaseEndsAt` を **`__step4.state().abx.blind` に出す** ——
  ⚠️★★★ **出さないと AC-1 / AC-2 / AC-4 を実測できない。**
  ★ **「検査できる形で作る」を後付けにしない**（S5-D11）。
- ⚠️ **音に印を足さない**（AB-D3）——★ 新しい oscillator も無音区間も作らない。

### 3. 中止経路

★ `abxBlindStop`（既存の「中止」）が相の途中で走ったとき、**進行中の `abxPhase` が
そのまま次へ進まない**ようにする（★ 世代カウンタ `bl.gen` で判定する）。
⚠️ **これを忘れると、中止したのに次のトライアルが始まる。**

## テスト戦略

★ **AC ごとに「どう測るか」を先に決める**（★ 後から発明しない・`browser-verification` §0）。

| AC | 測り方 |
|---|---|
| AC-1 | ★ 背景サンプラ（`setInterval`）で **粒子率と `bl.phase` を対にして記録**し、`diff` の次のトライアルで **跳びの時刻が `phase==="prep"` の中**にあることを実測。⚠️ **CDP は 45 秒で切れる**ので、サンプラを仕込んで**後から読む**（引き継ぎ §5-4-11） |
| AC-2 | ★ 各相で `abx-blind-state` の文言を実測（4 相ぶん） |
| AC-3 | ★ ② を 2 回開始し、**order が異なる**ことと **`order_seed` が JSON に入る**ことを実測 |
| AC-4 | ★ AC-1 と同じサンプラで、**1 区間目の粒子率が rate_min で定常**であることを実測 |
| AC-5 | `bash run.sh check`（exit 0 / 103 以上・meta 109 以上） |
| AC-6 | ★ **新規検査ごとに meta 変異を 1 件足し、壊すと赤くなることを実測** |

⚠️★★ **silent pass はこの系列で 12 回以上出ている。** ★ **検査を書いたら必ず壊す。**

## レビュー

★ `code-reviewer` ＋ `security-checker` を**並列**で起動する（S4-D1・★ 本 Step で 3 回とも効いた）。
★ **`/cross-review` は `/finish-task` Step 3 で必須。** ⚠️ **diff に実データを含めない。**
