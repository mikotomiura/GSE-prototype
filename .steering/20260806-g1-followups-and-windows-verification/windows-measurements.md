# Windows 機での実測記録 (2026-08-06)

> このファイルは **Windows 機側で採取した一次データ**だけを置く。W-1〜W-8 の合否記録は
> macOS 側が `experiments/20260801-controlled-friction-task/windows-verification.md` /
> `notes.md` に書くため、ここでは**重複させない**。
>
> ★ 依頼元は Windows 機ローカルの `.idea/macOS_request.md`（gitignore 対象・リポジトリには入らない）。
> 依頼の指示は「**情報収集だけ・コードは 1 行も直さない**（修正は文脈を持つ macOS 側が行う）」。
> ★ **その指示どおり、本セッションでコード・テストは一切変更していない。**

## 環境

| 項目 | 値 |
|---|---|
| OS | `Microsoft Windows [Version 10.0.26200.8973]` |
| ロケール | `(Get-Culture)` = `ja-JP` / `(Get-UICulture)` = `ja-JP` |
| コンソール CP | `chcp` → `Active code page: 65001` |
| 採取シェル | `cmd.exe`（バッチに引数をそのまま書いて実行。PowerShell の引数解釈を挟まない） |

## M-1. `tasklist` 該当プロセス「なし」の実出力（★ 最優先の未検証項目だったもの）

3 パターンとも **rc=0**、出力は 1 行。

```
===== tasklist /FI "IMAGENAME eq notexist.exe" =====
INFO: No tasks are running which match the specified criteria.
[rc=0]

===== tasklist /FI "IMAGENAME eq notexist.exe" /FO CSV =====
INFO: No tasks are running which match the specified criteria.
[rc=0]

===== tasklist /FI "IMAGENAME eq notexist.exe" /FO CSV /NH =====
INFO: No tasks are running which match the specified criteria.
[rc=0]
```

分かったこと（★ 測ったことだけ）:

- **ja-JP 環境だが文言は英語**だった。文字化けではない（CP=65001 で採取し、Shift-JIS デコードでも同一）。
  ⚠️ ただしこれは**この 1 台の実測**であり、「日本語 Windows なら常に英語」を意味しない。
- **`/FO CSV` を付けても CSV 化されない**。この INFO 行がそのまま出る。
- ★ この INFO 行は **stdout に出る**（PowerShell から `2>$null` で stderr を捨てても残る）。
  → `g1::other_instance_running()` は `o.stdout` しか読まないので、**この行は確実にパーサへ渡る**。
- 引き継ぎが警戒していた「エラー: 無効な引数またはオプションです」は **cmd.exe では再現しなかった**。

## M-2. `tasklist` 該当プロセス「あり」の実出力

`gse-next.exe` はこの機で**既に起動中**だった（こちらで新規起動していない）。代用ではなく本物。

```
===== tasklist /FI "IMAGENAME eq gse-next.exe" /FO CSV /NH =====
"gse-next.exe","17456","Console","3","47,644 K"
[rc=0]

===== tasklist /FI "IMAGENAME eq explorer.exe" /FO CSV /NH =====
"explorer.exe","2084","Console","3","386,368 K"
[rc=0]
```

## M-3. 実出力を `other_pids_from_tasklist` に突き合わせた結果（★ 解析のみ・コード未変更）

`src-tauri/src/g1.rs` の実装は `l.split("\",\"")` で分割し、`cols.len() < 2` を捨て、
`cols[1]` を `u32` にパースできた行だけを拾う。上の実出力に当てると:

| 入力 | 分割結果 | 判定 |
|---|---|---|
| `INFO: No tasks are running which match the specified criteria.` | `","` を含まない → `cols.len() == 1` | 捨てられる → 空 Vec → `other_instance_running() = false`。**誤検知しない** |
| `"gse-next.exe","17456","Console","3","47,644 K"` | `cols[1] = "17456"` | `17456` を取得。`self_pid` と異なれば検出。**期待どおり** |

- メモリ列 `"47,644 K"` のカンマは、区切りが `","`（引用符込み）なので**影響しない**。
- `cols[1]` が数値にならない行は捨てる実装のため、**該当なし文言が何語でも安全側（= 検出なし）に倒れる**。

### ⚠️ ここで確かめて「いない」こと

- **2 個同時起動時の実出力は未採取**（= 「検出できる」ことの実測ではない。パーサの入力形式の検証まで）。
- 他の ja-JP 端末で該当なし文言が日本語になる可能性は**否定できていない**。
- ★ 上記はあくまで**実出力に当てた解析**であり、この記録の時点で**回帰テストは追加していない**
  （依頼どおり修正は macOS 側が行うため）。

## M-4. Windows 上の `cargo test`（★ 「1 度も走っていない」残課題を消化）

```
cargo test --manifest-path src-tauri/Cargo.toml --workspace
```

```
test result: ok. 271 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out   (lib)
test result: ok.  23 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out   (gse-replay)
   emit_schema / cohort / main / Doc-tests … いずれも 0 tests, ok
```

**合計 294 passed / 0 failed**、終了コード 0。`replay_snapshot_goldens_byte_equal` を含む
ゴールデン回帰も Windows で緑。

### ⚠️ 手順書の穴（★ 実測で踏んだ）

リポジトリ直下で手順書どおり `cargo test --workspace` を叩くと**即座に空振りする**:

```
error: could not find `Cargo.toml` in `C:\GSE-prototype` or any parent directory
```

`Cargo.toml` は `src-tauri/` にあるため、Windows 側の手順には
`--manifest-path src-tauri/Cargo.toml` か `src-tauri/` への移動が要る。

### 付随して分かったこと

- 起動中の `gse-next.exe`（PID 17456）は**リンクを妨げなかった**
  （テストバイナリはハッシュ付き別名でビルドされるため）。アプリは起動したまま完走した。

## この記録に PII は含まれない

イメージ名 / PID / セッション名 / メモリ量 / OS ビルド番号のみ。
NDJSON (`gse_*.ndjson`) の中身・ファイル名、メールアドレス、鍵は含んでいない
（採取物を `data-privacy` の観点で走査して確認済み）。
