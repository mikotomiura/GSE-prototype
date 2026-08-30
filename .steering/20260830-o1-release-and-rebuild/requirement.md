# 要件 — O1 のリリースを切って配布物を作り直す

## 背景

前セッション (2026-08-30) で、**`v0.1.29` で作った O1 配布物が「O1 を知らないビルド」**
だったことが判明した。署名・実行ビット・`o1.mode` はすべて正常で、配布物としては
完全に正常に見えたが、バイナリに O1 実装が 1 バイトも入っていなかった。

本セッション開始時に**自分で確かめ直した一次資料**:

| 検査 | 実測（2026-08-30 本セッション） |
|---|---|
| `git ls-tree v0.1.29 src-tauri/src/o1.rs` | **空**（exit 0 だが出力なし） |
| `git tag --contains 7a062cc` | **空** ＝ O1 を含むリリースタグが 1 本も無い |
| `gh pr view 130` | `MERGED` (2026-08-30T04:29:43Z) |
| `gh run list` 直近 | 全部 `success`（`main` の merge run 含む） |
| self-hosted runner | `g-gear-win-x64` online / `macbook-air-m-arm64` online |
| `scripts/check-o1-release-readiness.sh` | **通過 17 / 未達 2** |

未達 2 件は順序依存であり、この順でしか消せない:

1. O1 実装を含むリリースタグが無い
2. 送信 timeout が未実測（1 が解けないと `gse-submit --o1` が使えず実施不能）

## ゴール

1. **O1 実装を含むリリースタグ `v0.1.30` を切り**、release 資産に dmg / exe が揃う
2. `SHARED_SECRET` をローテートする（★ 研究者判断で「する」に決定・2026-08-30）
3. `--mode o1 --tag v0.1.30` で配布物を作り直し、新ゲートが全部通る
4. macOS 実機で **配布物そのものから** 通し確認する（`cargo run` で代用しない）
5. 送信 timeout の設計矛盾（`MAX_BYTES` 48MB vs `from_secs(180)`）に対処する
6. 配布フォルダに zip を置き、被験者がアプリを入手できる状態にする

## 受け入れ条件

- [ ] `git tag --contains 7a062cc` が `v0.1.30` を返す
- [ ] `gh release view v0.1.30 --json assets` に dmg と exe が揃う
- [ ] `make-common-app-zip.sh --mode o1 --tag v0.1.30 --config ../../Form_O1/o1_submit.json` が完走
- [ ] 実機で `gse_o1_*` のファイル名が出る／`Probe scheduler thread started` が出ない
- [ ] `scripts/check-o1-release-readiness.sh` が **通過 19 / 未達 0**
      （★ 期待値 17/0 は古い。O1 タグ検査を足したので 19 が正しい）
- [ ] 実施しなかったことは「未実施」と明記する

## 研究者判断（2026-08-30 本セッションで確定）

| 論点 | 決定 |
|---|---|
| `SHARED_SECRET` ローテート | **する**（O1 を含むリリースが無く、有効な secret を持つ配布物が被験者の手元にゼロ＝いま実質無料） |
| Intel Mac の被験者 | **保留**（対象者が確定してから判断。v0.1.30 は aarch64 dmg のまま） |

## 適用範囲外

- Intel Mac 向け universal ビルド（上記のとおり保留）
- `sync-session.ps1` の Windows PowerShell 5.1 (Desktop) 検証（Windows 作業時）
- `sync-all.sh` の O1 生 NDJSON コピー順序（`.ps1` と対で直す）
