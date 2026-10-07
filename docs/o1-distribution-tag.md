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

## v0.1.38（2026-09-28）

| 項目 | 値 |
|---|---|
| タグ | `v0.1.38` |
| コミット | `afe6b0d7`（PR #247 の merge。版を 0.1.37 → 0.1.38 に上げただけ） |
| タグ作成日 | 2026-09-28（研究者承認のうえ push） |
| 切り直した理由 | PR #246（`b955cf05`）の O1 耐障害性 3 点を配布バイナリに入れるため: **G-1 自動起動**（O1 の同意確認の後に 1 回だけログイン時起動に登録）／**G-2 定期再送**（6 時間ごと）／**G-5 32 MiB 超の送信見送り**（`oversize/` へ隔離・消さない）。記録: `.steering/20260928-o1-resilience-g1-g2-g5/` |
| 版を分けた理由 | G1 は `meta.app_version = 0.1.36` で G1 のファイルを見分ける契約。同じ番号の別バイナリを作らない |
| CI | run `36367017514`: `build-macos` / `build-windows` / `release` すべて success |
| 使う配布物 | `dist/_common/O1_実施用_macOS.zip` ／ `dist/_common/O1_実施用_Windows.zip`（★ Drive に置くのはこの 2 つだけ） |
| O1_実施用_macOS.zip の SHA-256 | `f5ad9a904368c726fbaf760eeffd5bb46319ffb2f2c3d38f87025d8af72d1028`（10,434,926 B） |
| O1_実施用_Windows.zip の SHA-256 | `e8c69975cb60df96dd4074d6c027d3a14af97daac31ef6a77b8907da8fc5c8b8`（5,983,577 B） |
| Release の dmg の SHA-256 | `3fae59180285718f793b8672848f5ac12b43d53408a8ef8e3ebdcb141be20f87`（`gse-next_0.1.38_aarch64.dmg`） |
| ログでの見分け方 | `meta` 行の `app_version = 0.1.38` ＋ `o1_mode` |
| 作ったコマンド | `bash make-common-app-zip.sh --mode o1 --tag v0.1.38 --config "$REPO/Form_O1/o1_submit.json"` |

### 実体で確かめたこと（2026-09-28・Mac）
- ★ 修正の目印を `LC_ALL=C grep -a -c -F` で数えた（`v0.1.37` を対照に）:

  | バイナリ | 目印 | v0.1.38 | v0.1.37（対照） |
  |---|---|---|---|
  | `gse-next`（mac）／`gse-next.exe` | `O1 autostart:` | 2 ／ 1 | 0 ／ 0 |
  | `gse-next`（mac） | `com.johnd.gse-next.o1`（LaunchAgent の Label） | 1 | 0 |
  | `gse-next.exe` | `GSE-O1`（Run の値名） | 1 | 0 |
  | `gse-next`（mac）／`gse-next.exe` | `periodic (O1)`（G-2） | 1 ／ 1 | 0 ／ 0 |
  | `gse-submit`（mac）／`gse-submit.exe` | `oversize_pending` / `the same name already exists in oversize/`（G-5） | 1 ／ 1 | 0 ／ 0 |
  | `gse-submit`（mac）／`gse-submit.exe` | `taking over a stale lock`（**陽性対照**・既存） | 1 ／ 1 | 1 ／ 1 |

- dmg 内 `gse-next.app`: `CFBundleShortVersionString = 0.1.38`・`codesign --verify --strict` OK。
- スクリプトの自己検査（初回セットアップ・署名・実行ビット・README 文言・余計なもの無し）はすべて ✅。
- 生成した zip を別の場所へ展開して、スクリプトとは別に再検算した:
  - macOS: 署名 OK・`0.1.38`・`Contents/MacOS/` の 7 ファイルすべて実行ビットあり・`gse-next` は Release の dmg 内のものと byte 一致。
  - Windows: `gse-next.exe` / `gse-submit.exe` が Release の資産と byte 一致（`cmp`）。
  - 両 OS: `o1.mode` あり・`g1.mode` なし・`o1.autostart` なし（★ 印は被験者の端末で同意確認の後にできる）。同梱の `g1-submit.json` は `Form_O1/o1_submit.json` と JSON として一致し、G1 の配布物のものとは不一致（endpoint も別）。
  - README（両 OS）: 新しい【3】（「参加の確認を済ませると…自動的に立ち上がる」）・【4】の「アプリを使うのをやめるとき」・持ち物の `o1.autostart` があり、旧版の手動登録手順（「おすすめ」）は無い。
- G1 の zip（`G1_実施用_*.zip`）は作成時刻 2026-09-27 01:23 のまま（本作業で上書きしていない）。

### 注意
- ⚠️ **同意フォームの文面を変えた**（自動起動の 1 文・PR #246）。被験者に届くのは、研究者が `Form_O1/GSE_O1_Form_Builder.gs` を O1 の Apps Script に貼り直し `migrateO1ConsentForm()` を実行してから（回答は保たれる）。
- ⚠️ 未確認（段階 B）: ログイン時の実起動・一覧での表示名（README は「gse-next」と書いた）・macOS の「バックグラウンドでの実行を許可」をオフにした状態が付け替え後も残るか。`.steering/20260928-o1-resilience-g1-g2-g5/g1-mac-autostart-experiment.md`。
- ⚠️ O1 ゲートの「同意文書の状態表の『未了』」（6 択 ESM 追補の採否）は研究者判断待ちのまま（本タグとは無関係）。
- Drive への差し替え・被験者への送付は研究者が行う（未実施）。

## v0.1.39（2026-10-02）

| 項目 | 値 |
|---|---|
| タグ | `v0.1.39`（軽量タグ・v0.1.38 と同じ形） |
| コミット | `d7694240`（PR #294 の merge。版を 0.1.38 → 0.1.39 に上げただけ） |
| タグ作成日 | 2026-10-02（研究者承認のうえ push） |
| 切り直した理由 | PR #292（`f04b4995`）の **ADR-037** を配布バイナリに入れるため: O1 の作業種別の宣言に 5 つ目の値 **`other`（「その他・細切れの作業」）**。Writing fallback で採点し推論は不変（`HMM_VERSION` 据え置き）。記録: `.steering/20261002-o1-task-kind-other/` |
| 版を分けた理由 | G1 は `meta.app_version = 0.1.36` で G1 のファイルを見分ける契約。同じ番号の別バイナリを作らない |
| CI | run `36987050681`（head = `d7694240`・event = push）: `build-macos` / `build-windows` / `release` すべて success |
| 使う配布物 | `O1_実施用_macOS.zip` ／ `O1_実施用_Windows.zip`（★ Drive に置くのはこの 2 つだけ）。⚠️ 作った場所は worktree `GSE-prototype-o1-other/experiments/20260801-controlled-friction-task/dist/_common/`（メインのチェックアウトの同名ファイルは v0.1.38 のまま・上書きしていない） |
| O1_実施用_macOS.zip の SHA-256 | `decb2c4316d5a4f50d570a4577a91bf4780631125d9d491c3e487054af295ae8`（10,436,688 B） |
| O1_実施用_Windows.zip の SHA-256 | `c17d296df9d74aa3790cce1939c45efcf3b3945b2750a6d61fafdcffa7d368d1`（5,982,909 B） |
| Release の dmg の SHA-256 | `06dd39026f149f864345300f2b7003c9b39663700245f0fdd274571343a3204c`（`gse-next_0.1.39_aarch64.dmg`） |
| ログでの見分け方 | `meta` 行の `app_version = 0.1.39` ＋ `o1_mode`。★ `session_meta` に `"task_kind":"other"` ＋ `"head_id":"writing_fallback"` が出うる |
| 作ったコマンド | `bash make-common-app-zip.sh --mode o1 --tag v0.1.39 --config "$REPO/Form_O1/o1_submit.json"` |

### 実体で確かめたこと（2026-10-02・Mac）
- スクリプトの自己検査（自動送信・O1 実装・`--o1`・reconcile・初回セットアップ・余計なもの無し・署名・実行ビット・README 文言・UTF-8 フラグ）はすべて ✅。
- 生成した zip を別の場所へ展開して、スクリプトとは別に再検算した:
  - macOS: `CFBundleShortVersionString = 0.1.39`・`codesign --verify --strict` OK・`Contents/MacOS/` の 7 ファイルすべて実行ビットあり・`gse-next` は Release の dmg 内のものと byte 一致。
  - Windows: `gse-next.exe` / `gse-submit.exe` が Release の資産と byte 一致（`cmp`）。
  - 両 OS: `o1.mode` あり・`g1.mode` なし・`o1.autostart` なし。
  - Release の資産の構成（名前）は v0.1.38 と同じ。
- ★ **`other` が入っていることは来歴の連鎖で確かめた**: PR #292 の merge `f04b4995` はタグ `v0.1.39` の祖先（`git merge-base --is-ancestor`）／ Release の run の head はタグのコミット `d7694240` ／ そのコミットの `RecordingControls.tsx` に「その他・細切れの作業」がある ／ zip の中身は Release の資産と byte 一致。
  - ⚠️ **バイナリの文字列検索では確かめられない**: 陽性対照「デザイン・映像・制作作業」が v0.1.38 / v0.1.39 の両方で **0 件**だった（Tauri が画面の資産を圧縮して埋め込むため）。→ この方法の 0 件を「入っていない」と読まないこと。

### 注意
- ⚠️★★★ **同意フォームの文面を変えた**（宣言の列挙を 5 択へ・PR #292）。被験者に届くのは、研究者が `Form_O1/GSE_O1_Form_Builder.gs` を O1 の Apps Script に貼り直し `migrateO1ConsentForm()` を実行してから（回答は保たれる）。⚠️ **再配備はこのタグの zip を Drive に置くのと同時かその後**に行う（逆順だと、同意は 5 択・画面は 4 択の旧 zip、という食い違いが起きる）。
- ⚠️★ **v0.1.38 以前を O1 に使わない**（宣言が 4 択しか出ず、5 択の同意フォームと食い違う）。
- Drive への差し替え・被験者への送付は研究者が行う（未実施）。

## v0.1.40（2026-10-07）

| 項目 | 値 |
|---|---|
| タグ | `v0.1.40`（注釈付きタグ） |
| コミット | `d3d1a914`（PR #320 の merge。`o1_install_id` ＋ 版 0.1.39 → 0.1.40） |
| タグ作成日 | 2026-10-07（研究者承認のうえ push） |
| 切り直した理由 | **ADR-038**: O1 の `meta`（session_start）行に、導入ごとの乱数 16 桁 hex **`o1_install_id`** を刻む。複数端末で走らせても解析で端末を分けるため。記録: `.steering/20261007-o1-install-id/` |
| 版を分けた理由 | G1 は `meta.app_version = 0.1.36` で G1 のファイルを見分ける契約。同じ番号の別バイナリを作らない |
| CI | run `37608888169`（event = push）: `build-macos` / `build-windows` / `release` すべて success |
| 使う配布物 | `O1_実施用_macOS.zip` ／ `O1_実施用_Windows.zip`（★ Drive に置くのはこの 2 つだけ）。作った場所は worktree `GSE-prototype-o1-device-id/experiments/20260801-controlled-friction-task/dist/_common/` |
| O1_実施用_macOS.zip の SHA-256 | `7451ae20a3a8346701650d44538001af557255805fe115ebdf8e0b2b4cb2f251`（10,439,503 B） |
| O1_実施用_Windows.zip の SHA-256 | `44554576e42fe9a927258c31208741b7fde902c5f51da8347e89015722cddeba`（5,987,315 B） |
| Release の dmg の SHA-256 | `79cbdf2fcbaf93f056392a7b0c262bb18dec7059caf89002d65514f5b9b4d782`（`gse-next_0.1.40_aarch64.dmg`） |
| ログでの見分け方 | `meta` 行の `app_version = 0.1.40` ＋ `o1_mode` ＋ **`o1_install_id`（`^[0-9a-f]{16}$`）** |
| 作ったコマンド | `bash make-common-app-zip.sh --mode o1 --tag v0.1.40 --config "$REPO/Form_O1/o1_submit.json"` |

### 実体で確かめたこと（2026-10-07・Mac）
- スクリプトの自己検査（自動送信・O1 実装・`--o1`・reconcile・初回セットアップ・余計なもの無し・署名・実行ビット・README 文言・UTF-8 フラグ）はすべて ✅。
- 生成した zip を別の場所へ展開して、スクリプトとは別に再検算した:
  - macOS: `CFBundleShortVersionString = 0.1.40`・`codesign --verify --strict` OK・`gse-next` は Release の dmg 内のものと byte 一致。
  - Windows: `gse-next.exe` / `gse-submit.exe` が Release の資産と byte 一致（`cmp`）。
  - 両 OS: `o1.mode` あり。
- ⚠️ **未実施**: 実機で O1 を起動して NDJSON の 1 行目に `o1_install_id` が出ること／再起動で同値／`~/.gse/o1_install_id` を消すと別値／非 O1 で出ないこと（陰性対照）。**配布前に実機で確かめる**こと。
- ⚠️ 単体テストでは、非 O1 の断片が空文字列であること・妥当でない値を刻まないこと・anonymize が保つことを固定済み（PR #320）。

### 注意
- ⚠️★★★ **同意文書の改訂が先行条件**: 「記録するもの」に乱数の識別子を足す（案: `.steering/20261007-o1-install-id/consent-revision-proposal.md`）。研究者が `Form_O1/GSE_O1_Form_Builder.gs` を O1 の Apps Script に貼り、`migrateO1ConsentForm()` を実行する。⚠️ **zip の差し替えと同時かその後**に行う。
- ⚠️★ **v0.1.39 以前を O1 の開始に使わない**（識別子が無く、複数端末を分けられない）。
- ⚠️ gse-dataset の `schema/current.json` 同期（additive）が未了。
- Drive への差し替え・被験者への送付は研究者が行う（未実施）。
