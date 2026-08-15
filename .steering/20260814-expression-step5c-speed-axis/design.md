# 設計 — A′（準備区間で状態を動かさない）と速度軸 4 点

## アプローチ

### 1. 提示手順の再設計（S5C-D1）

```text
【旧（3phase-prep-v1）】★ 準備区間に跳びが 2 回入る（← AB-D10 の漏れ）
  [prep1 1.5s: carry(乱数)] [prep2 1.5s: A] [i1 4s: A] [i2 4s: A or B] → 回答
   ↑ 入場状態から carry へ跳ぶ   ↑ carry から A へ跳ぶ
   ⚠️ 跳びの回数の偶奇 = 入場状態 = 直前トライアルの真値

【新（3phase-noreset-v2）】★ 準備区間に状態変化が 1 つも無い
  [prep 3.0s]        [i1]              [i2]                  → 回答
   直前の到達点のまま  同じ状態          same: 同じ / diff: 反転
   ★ 跳び 0 回        ★ 跳び 0 回        ★ ここだけが刺激
```

**実装（`player/step4.html`）**

| 対象 | 変更 |
|---|---|
| `abxBlindStart` | ★ `abxSetInstant("A")` を **1 回だけ**呼んで開始状態を定義（★ `abx.active` もここで立てる）。`bl.state = "A"` を持つ。⚠️ `carrySeed` は**削除**（★ 使わない乱数を残さない） |
| `abxBlindNext` | ★ 準備区間を **1 相**（`prep`）にし、**状態を変える呼び出しを 1 つも置かない**。`i1` も同様。`i2` の直前だけ `abxSet(target)`。`target = kind === "diff" ? flip(bl.state) : bl.state`。★ i2 の後に `bl.state = target` |
| `abxPrepSeconds` | ★ 式は据え置き（`max(prep_seconds, 2.0)`）。⚠️ **理由が変わった**ので comment を書き換える（跳びを収める場所 → 境目を画面で示す場所） |
| `abxBlindFinish` | ★ `protocol` を **`"3phase-noreset-v2"`** に変える（⚠️ 旧記録と取り違えない）。`timing[i]` に `from` / `to` を残す |
| `describeRework` | ★ 所要の見積もりは `prep + side*2` のまま（★ 相の数は 3 のまま） |

**⚠️ `same` でも `abxSet(target)` を呼ぶ**: `from === to` になるので音は動かないが、
★ **same と diff でコードの経路と所要をまったく同じにする**（★ 経路差が手がかりになるのを防ぐ）。

### 2. 検査（`scripts/step4_selftest.py`）

| 既存検査 | 扱い |
|---|---|
| AB-D2「リセットが 1 区間目より前」 | ★ **置換** → 「★ 準備区間と 1 区間目に状態を変える呼び出しが**無い**」 |
| AB-D7「carry が真値に依らない」 | ★ **置換** → 「★ `abxBlindNext` に `abxSetInstant` が 1 つも無い」 |
| AB-D7「採点区間で abxSetInstant を使わない」 | ★ **強化**（関数全体で禁止）＋ `abxSet` の引数が `bl.state` 由来であること |
| `abxPrepSeconds` の式検査 | ★ 据え置き |

**新規検査（受け入れ条件に対応）**

1. ★ `abxBlindNext` に `abxSetInstant` / `abxSet("A")` / `abxSet("B")` の**リテラル指定が無い**
   （★ 2 区間目の状態は **1 区間目の状態から**決まらなければならない）
2. ★ **`bl.state` が i2 の後に更新される**（★ 更新しないと次のトライアルの基準が固定に戻る）
3. ★★★ **算術検査**: `buildAbxOrder` の出力（4 diff / 4 same）に対して状態列をシミュレートし、
   ★ **上向き diff = 2・下向き diff = 2・終状態 = 開始状態**を全 70 通りで確かめる
   （⚠️ 実装の再実装ではなく、**A′ の定義から出る不変量**を検査する）
4. ★ `protocol` が `3phase-noreset-v2` であり、**旧手順の文字列が残っていない**

⚠️★★ **検査を書いたら必ず壊して赤くなることを実測する**（meta 変異）。
★ この系列で silent pass は **26 件以上**出ている。★ 2 つの型に注意:
「同じ関数の別の場所に同じ語がある」／「アンカー文字列が実在せず置換が no-op」。

### 3. 測定（S5C-D2）

| 順 | 遷移 | 1 トライアル | 8 回 | 目的 |
|---|---|---|---|---|
| 1 | 0 秒 | 11 s | 1.5 分 | ★ 新手順の基準点（★ 旧手順 8/8 の測り直し） |
| 2 | 5 秒 | 17 s | 2.3 分 | ★ 同上 |
| 3 | 20 秒 | 47 s | 6.3 分 | ★ 状態帯の上端の外 |
| 4 | 60 秒 | 127 s | 17 分 | ★★★ **製品の速度。ここが本命** |

★ 条件は **`t_low_wide` × `レベルにも出す(c_level)` × 幅 100–400 × 層 0 = 1.0** に固定。
⚠️ **①は各条件で測り直す**（★ 遷移時間を変えても①は端点で測るので値は変わらないはずだが、
★ **予測せず毎回実測する**）。

### 4. B1（10 分）

★ 層 0 = 1.0 のまま 10 分、研究者が作業しながら聴く。★ 問いは **「気になるか」**。
★ 申告は**原文のまま** notes に残す（★ 「かも」を「である」に直さない）。

## テスト戦略

```bash
bash experiments/20260812-expression-step4-grain/run.sh check    # ★ 静的 + meta + 平滑器 + 混入
```

★ ブラウザ実地は `run.sh serve` → `http://127.0.0.1:8732/player/step4.html`。
⚠️★★★ **測る前に BL-1 の関門を必ず実測する**
（`visibilityState` / `hasFocus` / `outerWidth`）。★ `resize_window` では直らない。

★ 実地の受け入れ確認（AC-1〜AC-3）は **自動回答 ＋ 背景サンプラ**で相と粒子率を記録する
（★ 耳は使わない。★ 相の構造だけを測る）。

## 変更対象ファイル

- `experiments/20260812-expression-step4-grain/player/step4.html`
- `experiments/20260812-expression-step4-grain/step4.config.json`（`_why` の更新のみ）
- `experiments/20260812-expression-step4-grain/scripts/step4_selftest.py`
- `experiments/20260812-expression-step4-grain/notes.md`（★ 記録）
- `.steering/20260814-expression-step5c-speed-axis/*`

⚠️ **触らないもの**: GSE 本体（`src-tauri/` / `src/`）・凍結対象・`docs/preregistration-v0.3.md`
