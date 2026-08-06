# 次セッション開始プロンプト — Windows 実施の結果を受け取って処理する

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-06 に follow-up (F-1/F-2/F-3) を入れ、Windows 検証ビルドを CI で作り、
Google Drive に配布物を置いた。★ **研究者が P-1 の Windows 実施を進めた**。
⚠️ ★ **その結果はまだ受け取っていない。**

---

===

## §0 このセッションでやること

★ **入口は 1 つ**: 研究者から **Windows 実施の結果**を受け取り、それに応じて処理する。

⚠️ ★ **結果を見ていないうちに「動いた」と書かない。** 前セッションの時点で分かっているのは
「研究者が実施を進めた」ことだけである。

### 最初に聞くこと

1. ★ **`windows-verification.md` の W-1〜W-8 はどこまで実施したか**（各項目の記録欄）
2. ★★ **W-4 の `tasklist` 生出力**（★ これが最優先。下記 §2）
3. ⚠️ 実施したのは **検証（W-1〜W-8）** か、**P-1 本番のブロック実施**か
   （★ 本番を回したなら NDJSON が出ているので `validate_blocks.py --dataset` の対象になる）

---

## §1 いまの状態（★ 実測で確かめたものだけ）

### コード（`feature/g1-app-mode-and-log-rotation`・main の 8 コミット先）

| コミット | 何 |
|---|---|
| `f805322` | **F-1/F-2/F-3**。★ ログを開くのを `.setup()` へ移し、2 個目のプロセスが空 NDJSON を残さないようにした |
| `7a0704e` | CI に `workflow_dispatch`（★ **`main` に merge 済み** = PR #86 / `fa21812`） |
| `7e7a369` | Windows 検証手順書 ＋ 配布は**案 A（ad-hoc 署名）で確定** |
| `7b50240` | ⚠️ `cargo test --lib <filter>` の **0 件マッチが rc=0** で黙って緑になる穴を塞いだ |
| `6228584` `8428c24` `447fb70` `0fddb3c` | 文書（発火の実測 / 配布物の作り直しで見つかった 4 件 / フォルダ名依存の除去） |

- ⚠️ ★ **origin より 3 コミット先** (`ahead 3`)。push が要る（★ このセッションでは push が拒否された）
- 回帰: `cargo test --workspace` 294 / `--features package` 279 / golden replay 4 本 /
  `emit_schema` byte-equal / `tsc` / clippy 新規警告 0 / `run.sh` **GREEN (rc=0)**

### Drive（★ 2026-08-06 に MCP で実測）

| フォルダ | 中身 | 状態 |
|---|---|---|
| `G1_実施用_Windows` | 9 ファイル（平ら）。`g1.mode` **0 バイトが残存** | ✅ サイズ一致 |
| `G1_実施用_macOS` | `G1-macOS.dmg` **5,772,904 B** ＋ README | ✅ サイズ一致 |

⚠️ ★ **照合したのはサイズだけ**である（バイト同一性は未確認）。
⚠️ ★ 一度 `.app` を**フォルダとして**上げてしまい、実行ビットが失われる形になっていた。
研究者が dmg に差し替えて解消済み（`G1-app` / `gse-next.app` / `Contents` を Drive 全体で検索して 0 件）。

---

## §2 ★★ 最優先: `tasklist` パーサの実測検証

⚠️ ★ `g1::other_pids_from_tasklist` は **CSV の形だけ見て書いた**。実出力で確かめていない
（`g1.rs` のコメントに「実機未検証」と明記してある）。

研究者に貼ってもらう 2 つ:

```powershell
tasklist /FI "IMAGENAME eq gse-next.exe" /FO CSV /NH      # 1 個起動中
tasklist /FI "IMAGENAME eq notexist.exe" /FO CSV /NH      # 該当なし（★ 実文言を見る）
```

★ 受け取ったら:

1. その生出力を**そのままテストケースにする**（`g1.rs` の `tasklist_*` テストへ追加）
2. ⚠️ ★ **日本語 Windows では該当なしメッセージが日本語になりうる**。推測で「大丈夫」と書かない
3. ★ **直したら、その場でわざと壊して赤を実測する**（後回しにしない）

---

## §3 ⚠️ まだ確かめていないこと（★ 「たぶん」で埋めない）

| 何 | 状態 |
|---|---|
| ★★ **Windows 上の `cargo test`** | ⚠️ **1 度も走っていない**。私の手動発火が push 由来の `check` を `concurrency` で巻き添え cancel した（run `31029374567`）。→ ★ `gh run rerun 31029374567` |
| W-1〜W-8 | ⚠️ **研究者が実施したが結果未受領** |
| macOS の Gatekeeper ダイアログ | ⚠️ **未決着**。ad-hoc 署名は quarantine 下でも `codesign --verify --strict` rc=0（=「壊れている」型ではない）、`spctl` は rejected、★ **`open <パス>` からは止まらず起動した**（= ダブルクリックの代理にならない）。★ Finder でのダブルクリック 1 回が要る |
| 5 分の自動終了 | ⚠️ macOS でも実機で待っていない |
| 新品端末での TCC 初回 | 未測定 |
| Drive ダウンロード後に `g1.mode`（0 バイト）が残るか | ⚠️ 未確認（Drive 上には残っている） |

---

## §4 ★ 配布物を作り直す手順（⚠️ scratchpad は消える）

前セッションの成果物は **scratchpad にしか無い**。消えていたら作り直す。

**Windows**（★ CI の本番ビルド）:

```bash
gh run download 31029380118 -D <保存先>     # ⚠️ artifact の保持は 7 日（2026-08-12 失効）
# 失効していたら: gh workflow run ci.yml --ref <ブランチ>  → build-windows だけが走る
```

配布フォルダは**平ら**に組む: `g1.mode`（空）/ `gse-next.exe` / `gse-submit.exe` /
`pubkey.txt`（`src-tauri/resources/`）/ `block01〜04.html`（`pages/PILOT-win/`）。

**macOS**（⚠️ CI に mac ビルドは無い＝タグ push 限定なので手元ビルド）:

```bash
npx tauri build --target aarch64-apple-darwin --bundles app --features package
# ⚠️ ★ 素のままでは配れない。CI と同じ後処理を手で当てる:
#   1. gse-package と gse-unpack を .app から除去（★ 研究者専用の復号器）
#   2. ヘルパを個別 ad-hoc 署名 → 内側バイナリ → バンドル の順に
#      --entitlements src-tauri/Entitlements.plist で再署名
#   3. codesign --verify --strict が rc=0 になることを確認（素のままだと rc=1）
hdiutil create -volname "G1-macOS" -srcfolder <フォルダ> -ov -format UDZO <出力>.dmg
```

⚠️ ★ **macOS は必ず dmg / zip の 1 ファイルで配る。** `.app` をフォルダとして Drive に上げると
**実行ビットが失われて起動しない**（Drive に POSIX パーミッションの概念が無い）。

---

## §5 制約（厳守）

- ★★ `preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` を変更しない
- ★ **`§5.4-2` の客観検証（probe 行 0）は何があっても残す**
- ★ フォルダ名に依存した手順を書かない。★ **`g1.mode` との位置関係**で書く
  （Windows = exe の 1 階層上 / macOS = `.app` の 4 階層上。コードは名前を見ていない）
- **PII**: 実名・メール・**セッション日時 / NDJSON ファイル名**を成果物に出さない
- ⚠️ ★ 本リポジトリは一時 public にする運用がある
- 依存を足さない（Python は標準ライブラリのみ）
- ★ Rust を書くなら `rust-standards` / `hook-constraints` / `architecture-rules` を先に読む

## §6 ★ このセッションで踏んだ罠（**先に読む**）

| 罠 | 中身 |
|---|---|
| ★★ **`cargo test --lib <filter>` は 0 件マッチでも rc=0** | ゲートが黙って緑になる。★ **"N passed" の N を数える**（`run.sh` の `run_cargo_filter`）。⚠️ 既存の kill switch 検査にも同じ穴があった |
| ★ `workflow_dispatch` はデフォルトブランチに無いと発火しない | `ci.yml` だけの PR を `main` へ先に入れる必要があった |
| ★ 手動発火が push 由来の run を cancel する | `concurrency: <workflow>-<ref>` / `cancel-in-progress: true` |
| ★ `ditto --sequesterRsrc` は `__MACOSX` / `._*` を作る | Windows 向け zip には `zip -r -X` を使う |
| ⚠️ ★ **確認せずに別サービスへ上げた** | Drive の経路が全部塞がっていると分かった時点で Dropbox へ置いてしまった。★ **指定と違う場所へ出す前に必ず確認する**（削除済み） |
| ★ アサーションの側が誤る | 漏洩チェックの grep が `BLOCK` の中の `LO` に当たって誤検知した |

## §7 終わり方

- 実測結果を `windows-verification.md` の記録欄と `notes.md` に**そのまま**書く
  （★ **動かなかったものは「動かなかった」、試していないものは「試していない」**）
- `bash run.sh` が GREEN のまま。各 `--selftest` が緑のまま
- ★ Rust を触るなら `cargo test --workspace` と `gse-replay --snapshot` の回帰
- ★ **検査を足したら、その場でわざと壊して赤を実測する**
- 最後に `/cross-review`（★ 予算はその場で計算する。⚠️ **引き継ぎメモの数字を根拠にしない** —
  2026-08-06 は日付ロールオーバーで 0 から始まった）
