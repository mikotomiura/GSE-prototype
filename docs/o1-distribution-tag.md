# O1 の配布に使ったリリースタグ（ADR-034 D3・ADR-031 M9）

> ⚠️★★★ **以後 `--mode o1` の配布物（`experiments/20260801-controlled-friction-task/make-common-app-zip.sh`）は、ここに記録した最新のタグ以外で作らない。**
> `--tag` と `--config` は**必ず明示**する（スクリプトの既定は古い `v0.1.24` と G1 の設定）。
> ⚠️ 追記のみ（append-only）。過去の節を書き換えない。新しいタグを切ったら下に節を足す。
> ★ G1 の配布タグは別の記録（`experiments/20260801-controlled-friction-task/distribution-tag.md`・`v0.1.36` で凍結）。**混ぜない。**

## v0.1.37（2026-09-27）

| 項目 | 値 |
|---|---|
| タグ | `v0.1.37` |
| コミット | `7b2846f`（PR #239 の merge。版を 0.1.36 → 0.1.37 に上げただけ） |
| タグ作成日 | 2026-09-27（研究者承認のうえ push） |
| 切り直した理由 | `v0.1.36` 以降の reconcile 修正（PR #233: `a819f0d` / `016b5f2` / `914e88f` / `a94e0ac` / `53e98b6`＝ロックの heartbeat と所有印）が配布バイナリに入っていなかった（`scripts/check-o1-release-readiness.sh` の「リリースタグが古い」） |
| 版を分けた理由 | G1 は `meta.app_version = 0.1.36` で G1 のファイルを見分ける契約。同じ番号の別バイナリを作らない |
| CI | run `36324136212`: `build-macos` / `build-windows` / `release` すべて success |
| 使う配布物 | `dist/_common/O1_実施用_macOS.zip` ／ `dist/_common/O1_実施用_Windows.zip`（★ Drive に置くのはこの 2 つだけ） |
| O1_実施用_macOS.zip の SHA-256 | `301f44fd3d9ab6fd899d8139b72a58742d209be57cb893430a92b0c97ee61398` |
| O1_実施用_Windows.zip の SHA-256 | `1da90c47fe181036340fc492b16abba8e6818c35209d16833f5d16d865578ff7` |
| Release の dmg の SHA-256 | `d1dfdafd8fd14a9f7000cecaded71d52f1d7a702abd2a53074ed5a79a99f35e0`（`gse-next_0.1.37_aarch64.dmg`） |
| ログでの見分け方 | `meta` 行の `app_version = 0.1.37` ＋ `o1_mode` |
| 作ったコマンド | `bash make-common-app-zip.sh --mode o1 --tag v0.1.37 --config "$REPO/Form_O1/o1_submit.json"` |

### 実体で確かめたこと（2026-09-27・Mac）
- ★ **修正の目印は `gse-submit` にある**（reconcile は `gse-submit` に入り、`gse-next` には入らない。⚠️ `gse-next` を grep すると修正の有無と無関係に 0 件になる）。
  `LC_ALL=C grep -a -c -F` で、新しい warn メッセージ `lock heartbeat` / `taken over or removed` を数えた:

  | バイナリ | `lock heartbeat` | `taken over or removed` | 旧来の `taking over a stale lock`（陽性対照） |
  |---|---|---|---|
  | v0.1.37 `gse-submit`（mac）／`gse-submit.exe` | 1 ／ 1 | 1 ／ 1 | 1 ／ 1 |
  | v0.1.36 `gse-submit`（mac）／`gse-submit.exe`（**対照**） | **0** ／ **0** | **0** ／ **0** | 1 ／ 1 |

- dmg 内 `gse-next.app`: `CFBundleShortVersionString = 0.1.37`・`codesign --verify --strict` OK。`gse-next` / `gse-next.exe` に `0.1.37` が 1 件（v0.1.36 では 0 件）・`o1.mode` が 2 件。
- 生成した zip を別の場所へ展開して、スクリプト自身の検算とは別に再検算した:
  - macOS: 署名 OK・`CFBundleShortVersionString = 0.1.37`・`Contents/MacOS/` の 7 ファイルすべて実行ビットあり。
  - 両 OS: `o1.mode` あり・`g1.mode` なし。同梱の `g1-submit.json` は `Form_O1/o1_submit.json` と JSON として一致し、G1 の `g1-submit.json` とは不一致（★ 行き先は O1 の受け口）。
  - Windows: 同梱の `gse-next.exe` / `gse-submit.exe` は Release `v0.1.37` の資産と byte 一致（`cmp`）。
- ⚠️ 限界: heartbeat の動作そのもの（O1 の滞留中にロックが奪われないこと）は実機で通し確認していない。担保は「修正コミットより後からビルドされた」ことと、上の文字列の有無と、CI の `cargo test`（reconcile 系）。

### 注意
- `dist/_common/` の `⚠️配るのはこの 2 つです_v0.1.34.txt`（2026-09-11 作成）は**古い**。本タグの内容ではない。
- `dist/_common/G1_実施用_*.zip` は `v0.1.36` のまま（本作業で上書きしていない。作成時刻 2026-09-27 01:23）。
- Drive への差し替え・被験者への送付は研究者が行う（未実施）。
