"""P1 の「軸ごとの上下界」の結合器 (事前宣言 v1.1 冒頭 (3) の規則をコードで固定する)。

## ★ 何をする関数か

**任意のスカラー量**を極ごとに受け取り、軸ごとに min / max / 幅と状態を返す。
G2 は recovery 推定器と介入判断が未実装で今は計算できないが、規則は量に依らないので、
量から切り離して先にテストで固定する (`.steering/20260926-p1-main-prep/decisions.md` 判断 3)。
→ G2 ができたら、`values` に G2 を差し込む。

## ⚠️★★★ 規則 (docs/preregistration-p1-episode.md v1.1 冒頭 (3))

- 軸は **2 本**: ポインタ軸 = `baseline` と `pointer_b`／修飾キー軸 = `baseline` と `modifier_m_plus`。
  ⚠️ **軸をまたいで 3 極の min / max を取らない**。
- ★ 上下界は**極の順序を前提にせず**、独立に求めた 2 極の値の min / max で取る。
- ⚠️ ポインタ軸で `pointer_b` が非適用: 極 B を入れず、**算出不可** (`not_computable`)。**幅 0 と報告しない**。
- ⚠️ 修飾キー軸で `modifier_m_plus` が非適用: `not_applicable`。**極 M+ を計算したと書かない**
  (幅への寄与はゼロ: 極 M+ は構造上 baseline と恒等)。

## 出力の形 (判断 20)

| 状態 | `min` / `max` | `width` | `poles_used` |
|---|---|---|---|
| `ok` | 2 極の値の min / max | `max − min` | 2 極 |
| `not_computable` (ポインタ軸のみ) | `None` | `None` | 空 |
| `not_applicable` (修飾キー軸のみ) | baseline の値 | `0` | `["baseline"]` (⚠️ 極 M+ の名前も値も出ない) |

使い方: `python -m unittest scripts.tests.test_p1_bounds -v` (repo 直下から)。
"""

import math

# ★ 軸 → (極 A 側, 極 B 側)。⚠️ 極の名前であって、値の大小の順序ではない。
AXES = {
    "pointer": ("baseline", "pointer_b"),
    "modifier": ("baseline", "modifier_m_plus"),
}
POLES = tuple(dict.fromkeys(pole for poles in AXES.values() for pole in poles))

OK = "ok"
NOT_COMPUTABLE = "not_computable"
NOT_APPLICABLE = "not_applicable"
STATUSES = (OK, NOT_COMPUTABLE, NOT_APPLICABLE)

# ⚠️ 非適用のときの状態は軸ごとに違う: 極 B の 0 行は判定不能 (算出不可) だが、
#   修飾キー 0 行の極 M+ は恒等が構造で保証される (not_applicable)。
_INAPPLICABLE_STATUS = {"pointer": NOT_COMPUTABLE, "modifier": NOT_APPLICABLE}


def _check_number(pole, value):
    # ⚠️ bool は int の subclass なので、素通りさせない
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"極 {pole!r} の値が有限の数ではない: {value!r}")


def _check_inputs(values, applicable):
    for name in (*values, *applicable):
        if name not in POLES:
            raise ValueError(f"知らない極名: {name!r} (知っている極: {POLES})")
    for pole in POLES:
        if not isinstance(applicable.get(pole), bool):
            raise ValueError(f"applicable[{pole!r}] が bool ではない: {applicable.get(pole)!r}")
    # ⚠️ baseline は両軸の共通の基準。無いなら、どちらの軸も何も言えない
    if not applicable["baseline"]:
        raise ValueError("baseline が非適用 (基準が無いので、どの軸も報告できない)")
    # ★ 使う極の値だけを検査する。非適用の極の値は使わないので、何が入っていても読まない
    for pole in POLES:
        if applicable[pole]:
            _check_number(pole, values.get(pole))


def _one_axis(axis, values, applicable):
    pole_a, pole_b = AXES[axis]
    if applicable[pole_b]:
        used = [pole_a, pole_b]
        lo = min(values[pole] for pole in used)
        hi = max(values[pole] for pole in used)
        return {"status": OK, "min": lo, "max": hi, "width": hi - lo, "poles_used": used}
    if _INAPPLICABLE_STATUS[axis] == NOT_COMPUTABLE:
        # ⚠️ 幅 0 を返さない: 測っていない幅が 0 として報告されるのを防ぐ
        return {"status": NOT_COMPUTABLE, "min": None, "max": None, "width": None, "poles_used": []}
    # ★ 極 B は計算していない。baseline の値を置くだけで、極 B の名前も値も結果に出さない
    base = values[pole_a]
    return {"status": NOT_APPLICABLE, "min": base, "max": base, "width": 0, "poles_used": [pole_a]}


def axis_bounds(values, applicable):
    """軸ごとの上下界を返す。

    `values`: 極名 → 数値 (非適用の極は `None` 可・値は読まない)。
    `applicable`: 極名 → bool (`baseline` / `pointer_b` / `modifier_m_plus` の 3 つとも要る)。
    戻り値: `{"pointer": {...}, "modifier": {...}}`。各軸は `status` / `min` / `max` / `width` / `poles_used`。
    入力が不正 (baseline が非適用・適用可の極の値が数でない・知らない極名) なら `ValueError`。
    """
    _check_inputs(values, applicable)
    return {axis: _one_axis(axis, values, applicable) for axis in AXES}


def summarize(units):
    """単位 (セッション / 参加者) ごとの `axis_bounds` の結果から、軸ごとに状態の件数を数える。

    戻り値: `{axis: {"ok": n, "not_computable": n, "not_applicable": n}}` (⚠️ 0 件の状態もキーを残す)。
    """
    counts = {axis: {status: 0 for status in STATUSES} for axis in AXES}
    for unit in units:
        for axis in AXES:
            if axis not in unit:
                raise ValueError(f"単位に軸 {axis!r} が無い: {unit!r}")
            status = unit[axis].get("status")
            if status not in STATUSES:
                raise ValueError(f"知らない状態: {status!r} (軸 {axis!r})")
            counts[axis][status] += 1
    return counts
