# tasklist — F-3 / F-4

## F-3
- [x] `stop-check.sh` の clippy を `--features package` に置き換える
- [x] 失敗時に指摘の先頭 (15 行) ＋ 件数を出す
- [x] 再現コマンドの文言を実際に打てるものへ訂正
- [x] ⚠️ 陽性対照: わざと lint 違反を作り、**WARN に中身が出る**ことを確認
- [x] ⚠️ 陰性対照: 綺麗な状態で**何も出ない**ことを確認

## F-4 (やらない ＋ 代替ゲート)
- [x] `scripts/check_default_feature_subset.py`
- [x] `scripts/tests/test_check_default_feature_subset.py` (⚠️ 4 対照)
- [x] ⚠️ **空ディレクトリ / 不在で緑にならない**ことを対照で実証
- [x] `ci.yml` に step を 1 つ追加
- [x] ⚠️ CI に default clippy job を**足していない**ことを確認

## 検証
- [x] `cargo clippy --all-targets [--features package] -- -D warnings` exit 0
- [x] `cargo test --features package --workspace` 緑
- [x] ゴールデン / schema byte-equal
- [x] ⚠️ `analysis/` 無変更 (`HMM_VERSION` 据え置き)
- [x] CI 両 OS 緑

## 記録
- [x] decisions.md / コミット / PR
