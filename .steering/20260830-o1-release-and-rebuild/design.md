# 設計 — O1 リリースと配布物の作り直し

## アプローチ

順序依存が強いので**直列**に進める。前段が緑にならないと後段は測定として意味を持たない。

```
A. タグを切る ──> C. 配布物を作り直す ──> D. 実機通し確認 ──> E. 送信 timeout
       │                                                          │
       └─ B. secret ローテート（A と同時が最も安い）              └─ 設計変更を含むので /reimagine
                                                              F/G. 配布フォルダ・README
```

## A. バージョン bump の変更対象（★ 実測で確定した）

`git ls-files -z | xargs -0 grep -nF "0.1.29"` の結果を目で分類した:

| ファイル | 扱い |
|---|---|
| `package.json:4` | ✅ 上げる |
| `src-tauri/tauri.conf.json:4` | ✅ 上げる |
| `src-tauri/Cargo.toml:3` | ✅ 上げる |
| `src-tauri/Cargo.lock:1750` (`gse-next`) | ✅ `cargo check` が自動で追随 |
| `src-tauri/Cargo.lock:3969` (`schannel`) | ❌ **触らない**。★ 引き継ぎメモは「もう 1 つある」と書いたが、実体は **第三者クレート `schannel` の偶然の同名バージョン**である |
| `make-common-app-zip.sh:431,433,515` | ❌ 触らない（事故の記録としてのコメント） |
| `check-o1-release-readiness.sh:174,175,796` | ❌ 触らない（同上） |

⚠️ 引き継ぎメモの「`Cargo.lock` に 2 箇所」は**誤読を招く記述**だった。修正対象は 1 箇所。

## B. secret ローテート

`openssl rand -base64 32` で生成し、**2 か所を同時に**変える:

| どこ | 誰が | 備考 |
|---|---|---|
| Apps Script `GSE_O1_Submit` のスクリプトプロパティ `SHARED_SECRET` | **研究者（手作業）** | Claude からは触れない |
| ローカル `Form_O1/o1_submit.json` の `secret` | Claude | `.gitignore:100` 済み |

★ 変更後に `checkSubmitConfig()` を回して緑を確かめる。
⚠️ 片方だけ変えると送信が全部落ちる。

## C. 配布物

```bash
cd experiments/20260801-controlled-friction-task
./make-common-app-zip.sh --mode o1 --tag v0.1.30 --config ../../Form_O1/o1_submit.json
```

`--config` は省略不可（省略すると die する。既定は G1 の設定＝黙って G1 の受け口へ飛ぶ）。

## D. 実機確認の方針

★ **配布物そのものから**始める。`cargo run` は代用にならない（O1 の有無を検査できない）。
⚠️ 「動くはず」と書かず、実際に操作した範囲だけを報告する。特に D-7（この時間帯の記録を消す）は
全 OS を通じて未実施なので、実施したか未実施かを明示する。

## E. 送信 timeout — 設計変更を含む

⚠️ 測る前に**論理的な矛盾**がある: 受け口 `MAX_BYTES` = 48MB、base64 で 64MB。
180 秒固定はこの設計の上限で**必ず**落ちる。実測値がいくつでもこの矛盾は消えない。

→ `from_secs(180)` 固定を「ペイロード サイズ比例 ＋ 下限」にする案を **`/reimagine` で比較**する。
★ 一案に飛びつかない。ゲートは `from_secs(180)` が消えることを要求するので比例式でも通る。

★ E-0 の実測（前セッション）を自分でも確かめる: パイプラインに圧縮が無ければ、
合成ペイロードでの転送時間測定が実データと等価になる（24 時間待つ必要が無い）。

## テスト戦略

| 対象 | 検査 |
|---|---|
| バージョン整合 | `cargo check`（lock 追随）／dmg 名 |
| O1 実装の有無 | `make-common-app-zip.sh` の新ゲート（タグ＋実体・両 OS） |
| 配布物の全体 | `--selftest`（19 件）／`check-o1-release-readiness.sh`（19 件目標） |
| 実機 | 目視＋ログ実体（`gse_o1_*` / `Probe scheduler thread started` の不在） |
| レビュー | `code-reviewer` + `security-checker` 並列 → `/cross-review` |
