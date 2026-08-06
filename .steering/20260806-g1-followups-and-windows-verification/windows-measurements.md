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

## M-5. W-1b 対照 (マーカー無しフォルダ) — 実機実行

配布フォルダを丸ごと temp 配下へコピーし (`<作業フォルダ>`)、その中に `plain-app\` を作って
同じ exe をコピー (`g1.mode` は置かない)。`plain-app\gse-next.exe` を起動 → 「開始する」→
約 40 秒放置 → ウィンドウを閉じる、を実施。

最新 NDJSON の 1 行目 (依頼の PowerShell ワンライナーの生出力):

```
{"type":"meta","session_start":1786008116041,"hmm_version":"0.3.0"}
```

- `g1_mode` は **入っていない** → 合格。
- 画面の「G1 モードで動作しています」は **出なかった** (起動直後のスクリーンショットで確認)。
- ★ 対照が効いていることの裏取り: 同じ検証の中でマーカー側 (`<作業フォルダ>\gse-next.exe`) を
  起動したときは **「G1 モードで動作しています（marker）」が表示された** (M-6 のスクリーンショット)。
  → 「常に G1 モードと出る実装」ではない。

## M-6. W-3 二重起動 — 実機実行

マーカー側を起動したまま `plain-app\gse-next.exe` を起動。`tasklist` の**生出力**:

```
===== after marker only (+8s) =====
"gse-next.exe","19884","Console","4","43,508 K"
[rc=0]

===== immediately after 2nd launch =====
"gse-next.exe","19884","Console","4","43,520 K"
[rc=0]

===== +2s / +5s / +15s after 2nd launch =====
"gse-next.exe","19884","Console","4","43,564 K"
[rc=0]
```

★ **1 行のままで、2 行にはならなかった。** 高頻度サンプリング (12 秒 / 209 サンプル ≒ 57 ms 間隔)
でも 2 行は 1 度も観測されなかった (`max rows observed = 1`)。

理由は `Start-Process -PassThru` で実測した:

```
2nd instance created: PID=3984
2nd instance EXITED: pid=3984 exitcode=0 lifetime=14 ms
  StartTime=18:32:39.475 ExitTime=18:32:39.488
```

→ 2 個目は **14 ms で自分から終了** する (`tauri-plugin-single-instance`)。`tasklist` 1 回の所要
(≒57 ms) より短いので、**同名 exe の二重起動では原理的に 2 行を捕まえられない**。

画面で起きたこと (依頼の (a)/(b)/(c)): **(a) と (b) の両方**。
2 個目は勝手に終了し、かつ **1 個目の画面に「⚠ GSE が 2 つ動いている可能性があります。」が表示**された。
これは `lib.rs` の single-instance コールバック (`second-instance-blocked` emit) 由来であり、
起動 1.5 秒後の `other_instance_running()` 検査ではない (検査時点では 2 個目はまだ居ない)。

NDJSON は W-3 の間に **1 本**だけ増えた (マーカー側の 1 本)。★ ブロックされた 2 個目は
**0 本** — follow-up F-3 (「ファイルを開くのは setup の中」) が Windows でも効いている。

## M-7. W-6 偽 `tasklist.exe` — 実機実行

ダミーは依頼どおり Rust で作成 (`std::env::temp_dir().join("gse_w6_hijacked.txt")` に書く)。

1. **ダミー単体の動作確認 (先に実施)**: 実行後に `%TEMP%\gse_w6_hijacked.txt` が
   **8 バイトで生成された**ことを確認 → ダミーは動く。
2. 痕跡を消し、`<作業フォルダ>\tasklist.exe` として配置。
3. マーカー側を起動 → 10 秒待機 → さらに「開始する」も押下 (= 起動時 1.5 秒後の検査に加えて
   **ブロック開始時の検査も**走らせた) → 終了。
4. 判定 (`dir %TEMP%\gse_w6_hijacked.txt` の生出力):

```
 ドライブ C のボリューム ラベルは Windows です
 ボリューム シリアル番号は 009C-B81F です

 C:\Users\...\AppData\Local\Temp のディレクトリ

ファイルが見つかりません
```

→ **無い = 乗っ取られていない (合格)**。`<作業フォルダ>\tasklist.exe` は検証後に削除済み。

## M-8. E-1 (Windows 側で追加した陽性対照) — 「検査が本当に走ったか」

⚠️ M-7 の「無い」だけでは *検査自体が走っていなくても*「無い」になる (空振り合格)。
そこで **`gse-next.exe` という名前で 120 秒眠るだけの別プロセス**(アプリではない・
single-instance プラグインを持たない) を先に起こしてからマーカー側を起動した。
★ このとき **偽 `tasklist.exe` は配布フォルダに置いたまま**にしてある。

2 プロセス同時のときの `tasklist` 生出力 (★ W-3 で採れなかったもの。ただし片方は代用プロセス):

```
"gse-next.exe","13864","Console","4","4,212 K"
"gse-next.exe","13696","Console","4","37,164 K"
```

結果: マーカー側の画面に **「⚠ GSE が 2 つ動いている可能性があります。」が表示された**。
偽 `tasklist.exe` は何も出力しないので、乗っ取られていれば **検出できず警告も出ない**。
→ この 1 回で同時に 3 つ言える:

1. `other_instance_running()` は Windows で **実際に走った**。
2. 使われたのは **System32 の本物** (絶対パス指定が効いている)。痕跡ファイルも作られなかった。
3. `other_pids_from_tasklist()` が **実機の CSV 出力を実際にパースして PID を拾えた**
   (g1.rs の doc コメント「⚠️ Windows では未実測」が指していた穴が、これで塞がる)。

代用プロセスは検証後に削除済み。

## M-9. 付随して観測されたこと (依頼外・未追試)

- ★ **ウィンドウの × で閉じてもプロセスが残る**。W-1b / W-3 とも、メインウィンドウが消えた後
  10〜90 秒待っても `gse-next.exe` は生きていた (`Get-Process` で確認)。検証では
  `Stop-Process -Force` で落とした。⚠️ 被験者が × で閉じて次のブロックを開くと
  「2 つ動いている」状態になりうる。★ アプリ内の「終了」ボタン経路 (`quit_app`) は**試していない**。
- ★ **合成打鍵はフックに乗らなかった**。`SendKeys` (136 打) と `keybd_event` (77 打) の両方を
  送ったが、画面の KEYBOARD は `---` のまま (= `LAST_KEY_MS == 0`)、NDJSON の
  `feat` 339 行はすべて `"f1":2000.00` (無打鍵の飽和値) だった。権限バナーは出ていないので
  `HOOK_ACTIVE` 自体は true。⚠️ **原因は切り分けていない**。★ **物理キーボードでの確認は
  していない** (この検証はすべて合成入力で行ったため、実キー入力が拾えるかは何も言えない)。
- `tasklist` の該当なし文言は、**PowerShell 経由 (`& cmd.exe /c ...`) だと日本語**で返った
  (`情報: 指定された条件に一致するタスクは実行されていません。`)。M-1 の cmd.exe 直叩きでは
  英語だった。⚠️ 条件の違いは特定していない。どちらも `","` を含まないので
  `other_pids_from_tasklist` の判定は変わらない。

## この記録に PII は含まれない

イメージ名 / PID / セッション名 / メモリ量 / OS ビルド番号のみ。
NDJSON (`gse_*.ndjson`) の中身・ファイル名、メールアドレス、鍵は含んでいない
（採取物を `data-privacy` の観点で走査して確認済み）。

M-5〜M-9 の追記分も同じ基準で確認した:

- 貼った NDJSON は **1 行目の `meta` のみ** (M-5)。`session_start` の epoch ms と
  `hmm_version` だけで、打鍵内容・ファイル名は含まない。★ M-9 の `f1` 集計は
  **検証者自身が合成入力で作ったセッション**のもので、被験者データではない。
- 作業フォルダの絶対パスとユーザー名は `<作業フォルダ>` / `C:\Users\...` に伏せた。
- 画面のスクリーンショットは temp 配下に置いただけで、**リポジトリには入れていない**。
