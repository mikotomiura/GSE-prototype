# ⚠️ この run は中止した —— ★ **マシンが寝てしまった**

- ★ 開始 15:28 / ⚠️ 実質停止 **15:50:55**（★ 22 分・14 サンプル）
- ⚠️★★★ **原因**: 2026-09-10 15:07 に `sudo pmset -a disablesleep 0` で
  **スリープを有効に戻した**ため（★ スリープ跨ぎ検証のため）。
  ★ バッテリー駆動 ＋ `sleep 1` 分設定なので、⚠️ **放置すると 1 分で寝る**。
  ★ 一次資料 (`pmset -g log`):
    - 16:04:28 `Entering Sleep state due to 'Maintenance Sleep'`
    - 16:06:20 `Entering Sleep state due to 'Clamshell Sleep'`
    - 16:09:27 `Wake from Deep Idle`
- ⚠️★★★ **重要な帰結**: ★ これまでの macOS 稼働コスト実測は**すべて
  `SleepDisabled = 1` の下**で採られていた（★ この Mac は 46 日間寝ていなかった）。
  → ★ 8h 無人計測を回すには、**寝ない状態を作り直す**必要がある。
- ★ 副産物: ⚠️ **GSE v0.1.34 はこの複数回のスリープを跨いで生き延びた**
  （★ pid 27279 が 1 時間 44 分連続・`crash-watch.tsv` は 0 件）。
- ★ 経緯: `.steering/20260910-measurement-binary-rebuild/decisions.md`
