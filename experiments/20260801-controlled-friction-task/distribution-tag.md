# G1 の配布に使ったリリースタグ（ADR-034 D3 / Migration 3）

> ⚠️★★★ **以後 `--mode g1` の配布物（`make-common-app-zip.sh` / `make-distribution.sh`）は、ここに記録したタグ以外で作らない。**
> G1 の収集が完了するまで凍結（ADR-034 D3）。`--tag` は**必ず明示**する（スクリプトの既定は古い `v0.1.24`）。
> ⚠️ 追記のみ（append-only）。過去の行を書き換えない。

| 項目 | 値 |
|---|---|
| タグ | `v0.1.36` |
| コミット | `24c5e3e`（PR #232 の merge） |
| タグ作成日 | 2026-09-27 |
| 使う配布物 | `gse-next_0.1.36_aarch64.dmg`（macOS）／ `gse-next.exe` ＋ `gse-submit.exe` ＋ `gse-unpack.exe`（Windows） |
| dmg の SHA-256 | `b37247d5f9133f08cf899bde2dd0db8f9723168248e949fc8840009e231d72bb` |
| ログでの見分け方 | `meta` 行の `app_version = 0.1.36` ＋ `g1_mode`（ADR-034 D3。⚠️ G1 の解析はこれを持つファイルだけを使う） |
| 作ったコマンド | `bash make-common-app-zip.sh --mode g1 --tag v0.1.36` |

## 実体で確かめたこと（2026-09-27・Mac）
- Release `v0.1.36` の資産 5 点（dmg・`gse-next.exe`・`gse-submit.exe`・`gse-unpack`・`gse-unpack.exe`）を取得。
- dmg 内 `gse-next.app`: `CFBundleShortVersionString = 0.1.36`・`codesign --verify --strict` OK。バイナリに `0.1.35` が 0 件・`activity_label`（v0.1.35 より後に入った行種）が 3 件（**対照**: v0.1.35 の dmg では `0.1.35` が 1 件・`activity_label` が 0 件）。
- `gse-next.exe`: `0.1.36` あり・`0.1.35` 0 件・`activity_label` 1 件。
- 生成した G1 用 macOS zip を展開して署名・`CFBundleShortVersionString`・`Contents/MacOS/` の実行ビット・`g1.mode` を再検算（スクリプト自身の検算とは別に実施）。
- ⚠️ 限界: 区間指定削除の修正そのもの（`1c60b2c` など）を示す文字列は、バイナリの grep では特定できていない。修正の有無は「v0.1.35 より後のコミットからビルドされた」ことと CI の `cargo test`（redact 系）で担保している。実機での削除の通し確認は未実施。

## 注意
- `dist/_common/` に 2026-09-11 作成の **O1 用 zip・旧 `⚠️配るのはこの 2 つです_v0.1.34.txt` が残っている**（本タグのものではない）。⚠️ 配らない。O1 の配布物は O1 用の別タグで作り直す（ADR-034 D3・ADR-031 M9）。
