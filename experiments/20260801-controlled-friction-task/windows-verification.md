# G1 モード — Windows 実機の検証手順（★ 2026-08-06 時点で **一切測っていない**）

> ## ⚠️ このファイルの位置づけ
>
> G1 モード（`preregistration.md` 第 10 版 `§5.4-5` / `§5.4-6`）は **macOS でしか実測していない**。
> `PILOT-win`（P-1 の残り半分）は Windows 回なので、★ **ここが緑にならないと Windows では回せない**。
>
> ★ **「macOS で動いたから Windows でも動く」とは書かないこと。**
> 実装は両 OS 分岐を持っているが、⚠️ **Windows 側は形だけ見て書いたコードを含む**
> （特に `tasklist` の出力解析。`g1.rs` のコメントに「実機未検証」と明記してある）。
>
> **記入したら `notes.md` と `.steering/` に結果をそのまま写す。**
> ★ 動かなかったものは「動かなかった」、試していないものは「試していない」と書き分ける。

---

## 0. 準備

### 0.1 検証するバイナリを手に入れる（★ 開発ビルドを使わない）

⚠️ 被験者が受け取るのは **CI が作った本番の portable exe** である（`protocol.md §4b.1`）。
★ **同じものを検証する。** 手元の `cargo build` の成果物では、`--no-bundle` の release 構成や
フロントの本番ビルドが違うため検証にならない。

```
GitHub → Actions → "CI / Release" → Run workflow
   └ Branch: <検証したいブランチ>  を選んで実行
```

CLI なら:

```bash
gh workflow run ci.yml --ref <検証したいブランチ>
```

- ★ **タグは切らない。** 手動発火 (`workflow_dispatch`) では `build-windows` だけが走り、
  **GitHub Release は作られない**（`ci.yml` の `release` ジョブはタグ限定のまま）。
- 成果物: Actions の artifact **`windows-portable`**（`gse-next.exe`）と
  **`windows-tools`**（`gse-submit.exe` / `gse-unpack.exe`）。★ 保持は **7 日**。

> ### ✅ ★ ここは **2026-08-06 に実測した**（run `31029380118`）
>
> | 確かめたこと | 結果 |
> |---|---|
> | ★ **デフォルトブランチに `workflow_dispatch` が無いと発火できない** | ⚠️ ★ **そのとおりだった。** `main` へ先に `ci.yml` だけを PR (#86) して merge するまで、feature ブランチを ref にしても発火できない。★ **これは GitHub の仕様であって回避策ではない** |
> | 発火後に走るジョブ | ★ **`build-windows` だけ**。`check` / `frontend-check` / `build-macos` はすべて **skipped**（`if` 条件どおり） |
> | pull_request のとき | ★ `build-windows` は **skipped**（PR #86 の checks で確認）。★ 通常の PR を重くしない |
>
> ⚠️ ★ **`main` に `workflow_dispatch` が入っていない状態は二度と来ない**（merge 済み）ので、
> 次回以降は `gh workflow run ci.yml --ref <ブランチ>` だけでよい。
>
> ### ⚠️★★ **push した直後に発火すると、push 由来の `check` が巻き添えで cancel される**
>
> `ci.yml` の `concurrency` は `group: <workflow>-<ref>` ／ `cancel-in-progress: true` である。
> ★ **手動発火は push 由来の run と同じグループに入る**ので、
> 2026-08-06 は push した `check`（Windows / mac の `cargo test`・`frontend-check`）が
> **3 ジョブとも cancelled** になった。
>
> ⚠️ ★ **「Windows でテストが通った」ことにはならない。** 通ったのは
> `build-windows`（`npx tauri build --no-bundle` = **コンパイル**）だけである。
> → ★ 発火は **push の run が終わってから**行うか、終わったあとで
> `gh run rerun <push の run id>` で `check` を回し直すこと。

### 0.1b 落とした exe が本物か確かめる（★ 数字で見る）

```bash
gh run download <run id> -D <保存先>
file <保存先>/windows-portable/gse-next.exe
```

★ 2026-08-06 の実測（run `31029380118`）:

| ファイル | サイズ | `file` の判定 |
|---|---|---|
| `windows-portable/gse-next.exe` | 10,474,496 | `PE32+ executable (GUI) x86-64` ← ★ GUI = `windows_subsystem="windows"` と整合 |
| `windows-tools/gse-submit.exe` | 968,192 | `PE32+ executable (console) x86-64` |
| `windows-tools/gse-unpack.exe` | 736,768 | `PE32+ executable (console) x86-64`（★ **研究者専用**。被験者に配らない） |

⚠️ artifact の保持は **7 日**（この回は `2026-08-12` 失効）。

### 0.2 フォルダを 2 つ作る

```
G1-app\                      ← ★ こちらが検証対象
├── g1.mode                  ← 空ファイルでよい
├── gse-next.exe             ← 0.1 で落としたもの
└── gse-submit.exe

plain-app\                   ← ★ マーカー無し（対照）
└── gse-next.exe             ← ★ 同じ exe をコピー
```

⚠️ ★ **`g1.mode` は `gse-next.exe` と同じ階層に置く**（Windows は exe の **1 階層上** =
exe が入っているフォルダ。`g1.rs::exe_to_folder_levels()`）。macOS は `.app` の 4 階層上なので**違う**。

---

## 1. 検査項目（★ 1 項目ずつ「操作 → 何を見る → 記録」）

### W-1. マーカーの探索階層

| | |
|---|---|
| **操作** | `G1-app\gse-next.exe` を **ダブルクリック**する |
| **何を見る** | 画面に **「G1 モードで動作しています」** が出るか |
| **合格** | 出る |
| **⚠️ 落ちたら** | マーカーの階層が違う（`exe_to_folder_levels()` の Windows 分岐 = 1）。★ 実装のバグ |

**記録**: 出た / 出ない → 

---

### W-1b. 対照（マーカーが無ければ G1 モードにならない）

| | |
|---|---|
| **操作** | W-1 のアプリを終了し、`plain-app\gse-next.exe` を開く |
| **何を見る** | 「G1 モードで動作しています」が **出ない**こと |
| **合格** | 出ない |

★ **これを飛ばさない。** 「常に出る」実装でも W-1 は緑になる
（＝ W-1 だけでは**検査が発火していない**のと区別がつかない）。

**記録**: 

---

### W-2. `meta` 行に `g1_mode` が刻まれる

| | |
|---|---|
| **操作** | W-1 の状態で「開始する」を押し、1 分ほど何か打ってからアプリを終了する |
| **何を見る** | `%USERPROFILE%\Documents\GSE-sessions\` の最新 NDJSON の **1 行目** |
| **合格** | `{"type":"meta", … ,"g1_mode":"marker"}` になっている |

```powershell
# 1 行目だけ見る（★ 打鍵内容は見ない）
Get-Content -TotalCount 1 "$env:USERPROFILE\Documents\GSE-sessions\<最新のファイル>"
```

⚠️ ★ **記録するときはファイル名と日時を `<file1>` に置き換える**
（`§5` の PII 制約: セッション日時 / NDJSON ファイル名を成果物に出さない）。

**記録**: 

---

### W-3. 二重起動の検出（★ 実測で macOS では再現した問題）

| | |
|---|---|
| **操作 a** | `G1-app\gse-next.exe` を開く → そのまま `plain-app\gse-next.exe` も開く |
| **何を見る** | (1) プロセスが 1 個のままか、(2) 画面に二重起動の警告が出るか |
| **合格** | ★ **どちらかが起きる**（プラグインが止める、または警告が出る） |

```powershell
tasklist /FI "IMAGENAME eq gse-next.exe" /FO CSV /NH
```

- ⚠️ ★ **止まらず・警告も出ない**なら、打鍵が 2 本の NDJSON に割れる（`protocol.md §2-3`）。
  ★ **これは実施を止める理由になる。**
- ★ macOS の実測では `tauri-plugin-single-instance` は **同一ビルド同士なら止めた**が、
  **プラグインを持たない旧ビルドとは共存した**（`decisions.md` R-8 結果 3）。
  → ⚠️ 被験者の実環境（Phase1 の旧 exe が残っている）を再現するなら、
  **Phase1 の古い `gse-next.exe` を先に起動してから** G1 を開く形も試す。

**記録**: (a) プロセス数 = ／ 警告 = 

---

### W-4. ★★ `tasklist` の実出力（**ここが一番の未検証**）

⚠️ ★ `g1::other_pids_from_tasklist` は **CSV の形だけ見て書いた**。実出力で確かめていない。

| | |
|---|---|
| **操作** | `gse-next.exe` を **1 個だけ**起動した状態で下のコマンドを実行し、**出力をそのまま貼る** |
| **何を見る** | 列の並び・引用符・区切り・ロケール（日本語 Windows で列見出しや文言が変わらないか） |

```powershell
tasklist /FI "IMAGENAME eq gse-next.exe" /FO CSV /NH
# ★ 1 個も起動していない状態でも 1 回実行する（"INFO: No tasks…" の実文言を見るため）
tasklist /FI "IMAGENAME eq notexist.exe" /FO CSV /NH
```

★ **この 2 つの生出力を貼ってもらえれば、パーサの実測検証を Claude 側で代行できる**
（PII は含まない: イメージ名 / PID / セッション名 / メモリ量のみ）。

⚠️ ★ **日本語 Windows では該当なしメッセージが日本語になる可能性がある**。
`other_pids_from_tasklist` は「数字に見える 2 列目」しか拾わないので大半は無害だが、
★ **推測で「大丈夫」と書かない。実出力で判定する。**

**記録（貼り付け）**:
```
（1 個起動時）

（該当なし時）

```

---

### W-5. `CREATE_NO_WINDOW`（コンソール窓が光らないか）

| | |
|---|---|
| **操作** | `G1-app\gse-next.exe` を起動し、**起動直後 1.5 秒**と**「開始する」を押した瞬間**を見る |
| **何を見る** | 黒いコンソール窓が **一瞬でも**光らないか |
| **合格** | 光らない |

★ 検査は **2 か所**から走る（`lib.rs`）: 起動 1.5 秒後（1 回）と、**ブロック開始のたび**（follow-up F-1）。
⚠️ ★ **後者は 2026-08-06 に足したばかりで、Windows では一度も動かしていない。**

**記録**: 

---

### W-6. `SystemRoot` 経由の絶対パス起動

| | |
|---|---|
| **操作** | W-3 / W-5 が動いていれば、`tasklist.exe` は絶対パスで起動できている（間接的な確認） |
| **★ 直接確認** | `G1-app\` に**ダミーの `tasklist.exe`**（何もせず終了する .exe / .bat ではなく .exe）を置き、W-3 をやり直す |
| **何を見る** | ダミーではなく `%SystemRoot%\System32\tasklist.exe` が使われる（＝検出結果が変わらない） |

⚠️ ★ これは security-checker 指摘 1 の実測確認である（配布フォルダは被験者が解凍する
**書き込み可能な場所**なので、同階層に置かれた `tasklist.exe` に乗っ取られないこと）。
★ ダミー exe を用意できないなら **「試していない」と書く**（無理に代用しない）。

**記録**: 

---

### W-7. ローテートと 5 分自動終了（★ 端から端まで）

| | |
|---|---|
| **操作** | `G1-app` のアプリで「開始する」→ **5 分待つ** → 戻ったら再度「開始する」→ もう一度 5 分待つ |
| **何を見る** | (1) 5:00 で自動的にスタート画面へ戻るか、(2) NDJSON が **2 本**できるか、(3) 1 本目の**最終行が `session_end`** で、その後ろに 1 行も無いか、(4) 2 本目が自分の `meta` 行から始まるか |

```powershell
# ★ 行の「型」だけ数える（打鍵内容は見ない）
Select-String -Path "$env:USERPROFILE\Documents\GSE-sessions\<file1>" -Pattern '"type":"(\w+)"' -AllMatches |
  ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Group-Object | Select Name,Count
# 最終行
Get-Content "$env:USERPROFILE\Documents\GSE-sessions\<file1>" -Tail 1
```

★ macOS では 2 ブロック通しを実測済み（`tasklist.md §10`）だが、
⚠️ ★ **5 分の自動終了そのものは macOS でも実機で待っていない。** Windows で初めて通しになる。

**記録**: (1) ／ (2) ／ (3) ／ (4) 

---

### W-8. プローブが出ない（★ `§5.4-2` の客観検証・**何があっても残す**）

| | |
|---|---|
| **操作** | W-7 のログをそのまま使う |
| **何を見る** | `probe_assignment` 行が **0 件** |

```powershell
(Select-String -Path "$env:USERPROFILE\Documents\GSE-sessions\<file1>" -Pattern 'probe_assignment').Count
```

★ **0 を「無い」と読む前に、数えるコマンド自体が動いているか**を別のパターン（例 `"type":"meta"`）で
確かめる。⚠️ ★ 本タスクで `log show` が **0 件・rc=0** を返して偽の緑を踏んだのと同型の罠である。

**記録**: probe = ／ 対照で数えた meta = 

---

## 2. 終わったら

- [ ] 結果を `notes.md`（G1 の実施記録）と `.steering/20260806-g1-followups-and-windows-verification/` に写す
- [ ] ⚠️ ★ **落ちた項目があれば「Windows では未達」と書き、`PILOT-win` を回さない**
- [ ] W-4 の生出力を Claude に渡し、`other_pids_from_tasklist` の実測検証を行う
      （★ 必要ならパーサを直し、**わざと壊して赤を実測**してから入れる）
- [ ] ⚠️ ★ PII: ファイル名・日時・実名を成果物に残さない（`<file1>` 等に置換する）
