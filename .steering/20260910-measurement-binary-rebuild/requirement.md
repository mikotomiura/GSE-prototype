# requirement — 計測用バイナリを配布物と同じ版に揃え、8h 再測をやり直す

## 背景（★ 一次資料で確認したもの）

★ 2026-09-10 12:56 時点で `bash scripts/check-measurement-binary.sh` は **rc=3**:

```
repo (src-tauri/Cargo.toml): 0.1.33
app  (CFBundleShortVersionString): 0.1.31   ← ⚠️ 版ずれ
★ ビルド時刻: 2026-09-03 21:03
陽性対照 4/4 → strings は機能している
⚠️ 診断 tap_enabled : 0 件
稼働中 gse_o1_20260909_174803.ndjson の meta.app_version: 0.1.31（★ app と一致）
```

→ ⚠️★★★ **計測用 app は v0.1.31 のまま**であり、
① 機序追跡に要る診断 `tap_enabled`（`cb1aa25` / 09-05）が入っていない、
② **配布物 (v0.1.33) の稼働コストを測っていない**。

⚠️ さらに、前セッションが 12:04 に開始していた 8h 再測
(`results/with-gse-20260910-macos-8h`) も **v0.1.31 を測っていた**。
★ 45 分経過時点で停止し `_aborted-...-v0131` へ退避した（★ 破棄はしていない）。

## ゴール

1. ★ 計測用 app を **v0.1.33 相当**で作り直し、**ゲート (`check-measurement-binary.sh`) を通してから**差し替える。
2. ★ GSE を再起動し、**もう一度**ゲートを通して「走っているのが新版」であることを一次資料で確かめる。
3. ★ 8h 再測を**新版で**開始し直す。
4. ★ 余力で §5 ブランチ棚卸し（記録の救出）。

## 受け入れ条件

- [ ] `check-measurement-binary.sh`（引数なし＝稼働中との照合込み）が **rc=0**
- [ ] ★ 版一致 0.1.33 / `tap_enabled` ≥ 1 件 / 陽性対照 4/4
- [ ] ★ 稼働中 NDJSON の `meta.app_version` が **0.1.33**
- [ ] ★ 8h run が `GSE_COST_LABEL` 付きで走っており `meta.json` の `cpu_source` が `ps -o cputime delta`

## 触らないもの（★ 引き継ぎ §7）

- 事前登録の凍結節 / `Form_G1/` / `Form_O1/` / `docs/adr/` 既存本文 / G1 zip・Drive の O1 zip
