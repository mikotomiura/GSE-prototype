# 確認結果 (2026-08-10 macOS 実機)

## 【A】提出レシート UI — macOS (WKWebView) で 5 項目すべて確認

**使ったもの**: `dist/_common/G1_実施用_macOS.zip` (v0.1.25 の dmg から組んだ**配布物そのもの**) を
展開した `gse-next.app`。参加者 ID は **`P999`**、実施週 = 第1週 (blind 較正)。

| | 期待 | 結果 | 根拠 |
|---|---|---|---|
| 【1】 | ブロック終了後に確認カード | ✅ 出た | スクショ 13:26:26 `このブロックの記録を研究者に送信しますか？（未確認 2 件）` |
| 【2】 | ★ `記録を送信しています…` | ✅ **出た** | スクショ 13:27:20 |
| 【3】 | ★★ `✅ この回の記録を送信しました（HH:MM・N 件）` | ✅ **出た** | スクショ 13:28:04 `（13:27・2 件）` |
| 【4】 | ★★ 文字が読めるか | ✅ 読める | 4 枚すべてで、暗い地に明るい文字。★ **背景と同色の文字は無い** |
| 【5】 | `✅ 送信を待っている記録はありません。` | ✅ 出た | 起動直後のスクショ |

★ **2026-08-08 の「背景と同色の文字」は macOS でも再発していない。**

### 実体側の裏づけ (★ 画面だけを根拠にしない)

```
ローカル  P999_block01_gse_20260810_041051.age     482 B   .sent 13:27:32
          P999_block02_gse_20260810_041334.age 233,792 B   .sent 13:27:36
app.log   G1 auto-submit (after approval): {"sent":2,"errors":0,"unsent":0,"awaiting_approval":0}
Drive     P999_block01_… 482 B      2026-08-10T04:27:24Z  id 1NE4fmRIrVHYq5atHmluPLzk49ZtlOBC0
          P999_block02_… 233,792 B  2026-08-10T04:27:35Z  id 1Fry-3oRD9v6Ky_Exw47D6VzI_dA-_UlX
```

→ レシートの「**2 件**」は Drive に着いた本数と一致する。

⚠️ ★ **この回はレシートの時刻が「押した時刻」か「送れた時刻」かを判別できない。**
承認 (`.ok` 13:27:16) と送信完了 (`.sent` 13:27:32) が **同じ分**に入っているためである。
★ この性質は Windows 側で既に判別済み (`.steering/20260810-g1-submission-receipt-ui/verification.md`)。

### ⚠️ 参加者 ID の取り違え防止 — 効いた

`開始する` を押す前に AX API で入力欄の実体値を読み `value=[P999]` を確認してから押した。
★ 前回の `P009` 事故と同じ形の失敗は起きていない。

---

## ⚠️★★ 新しく見つかった欠陥 — ブロックを 1 度も始めていないセッションが「ブロック」として提出される

### 何が起きたか (実測)

`P999_block01_gse_20260810_041051.age` (482 B) の中身は、**ブロックを一度も開始していない**
セッションである。実体は以下の 4 行しかない:

```json
{"type":"meta","session_start":1786335051878,"hmm_version":"0.3.0","g1_mode":"marker"}
{"type":"ime_state","t":1786335051194,"on":false,"active":false}
{"type":"ime_state","t":1786335052653,"on":false,"active":false}
{"type":"meta","session_end":1786335132424}
```

これは **入力監視の権限を与えるためにアプリを起動して閉じただけ**の 80 秒間である。
それが `.age` に包まれ、**block01 を消費し**、研究者へ**送信された**。
→ ★ **本物の 1 本目のブロックが block02 になった。**

### なぜ通ってしまうのか

`reconcile::closed_sessions` の 4 条件は
「①`gse_*.ndjson` ②`session_end` がある ③`has_any_data_row` ④`meta` に `g1_mode` がある」。
⚠️ ★ ④ は **アプリ起動時**に書かれる (ブロック開始時ではない)。
⚠️ ★ ③ の `has_any_data_row` (`packaging.rs:177`) が除外するのは `hook_health` **だけ**で、
**IME モニタが起動直後に吐く `ime_state` はデータ行に数えられる**。
→ 打鍵ゼロ・ブロックゼロでも 2 条件とも成立する。

★ `packaging.rs:192` のコメントは
「診断行はデータ行に数えない。数えると**打鍵ゼロのセッションでも提出候補として残る**」
と書いている。⚠️ **`ime_state` がまさにその抜け道になっている。**

### なぜ macOS で重いのか

⚠️★ **macOS 参加者の初回起動は「起動 → 権限付与 → 再起動」が正規手順**である
(`README_先に読む.txt` / `初回セットアップ_mac.sh` がそう案内している)。
→ ★ **この経路を通る macOS 参加者は、ほぼ全員が余計な block01 を作る。**
Windows は初回に権限付与が要らないため、この確認では表に出なかった。

### 影響

- ブロック番号がずれる (研究者は block01..04 を期待する)
- 中身の無い `.age` が送信先に溜まる
- ⚠️ データの**損失ではない** (本物のブロックは block02 以降として全部届く)

### 直し方の候補 (★ 本タスクでは直していない)

1. `has_any_data_row` の除外に `ime_state` を足す (最小・`hook_health` と同じ扱い)
2. ★ より本質的には「**ブロックが始まった証拠**」を条件にする
   (`session_start` 行 / `session_meta` 行の有無)。④ の `g1_mode` は起動の証拠でしかない
3. ⚠️ どちらもゴールデン再生成は不要 (HMM に触れない) だが、
   `packaging.rs` のテストに「`ime_state` だけのセッションを包まない」を足すこと

---

## 【B】配布 zip (v0.1.25)

```
dist/_common/G1_実施用_macOS.zip     10,336,723 B
dist/_common/G1_実施用_Windows.zip    6,013,965 B
```

スクリプト側の検査 (署名 / 実行ビット / `g1.mode` / セットアップ自己検査 / README 文言 /
UTF-8 フラグ / 課題ページ非混入) はすべて通った。★ それとは**独立に**以下を検算した:

| 検算 | 結果 |
|---|---|
| Windows zip の中身 (7 エントリ) | `gse-next.exe` `gse-submit.exe` `g1.mode` `g1-submit.json` `pubkey.txt` `launch-g1-windows.bat` |
| macOS zip の中身 | `gse-next.app` `g1.mode` `g1-submit.json` `README_先に読む.txt` `初回セットアップ_mac.sh` |
| `gse-next.exe` の版 (バイト列) | `0.1.25` × 2 (UTF-16LE) / `0.1.24` × **0** |
| `gse-next.app` の版 | `CFBundleShortVersionString = 0.1.25` |
| 秘密鍵の混入 | 同梱 7 バイナリすべて **0 件** (`gse-unpack` の 1 件はエラーメッセージ文字列。実鍵の形 `AGE-SECRET-KEY-1<base32>` は 0 件と確認) |

### ⚠️ `gse-unpack` は `.app` の中に入っている

引き継ぎは「`gse-unpack` は研究者専用・配らない」としているが、
⚠️ ★ **`gse-next.app/Contents/MacOS/` には `gse-unpack` が同梱されている**
(`emit_schema` `gse-cohort` `gse-package` `gse-replay` も同様。Tauri が workspace の
bin を全部束ねるため)。**v0.1.23 / v0.1.24 でも同じ**であり、今回の変更ではない。

★ 実害は小さい: `gse-unpack` は復号鍵を `--identity <keyfile>` で **外から**受け取る作りで、
鍵は埋まっていない (上表で実測)。⚠️ ただし「配らない」と書いた文書と実体が食い違っているので、
どちらかに寄せること。

---

## 【C】P009 のテスト送信 — ⚠️ 前セッションの「素性不明」が解けた

`P009_block01_gse_20260808_060459.age` (66,236 B) は **研究者のこの Mac で作られたテスト**である。

**根拠** (推測ではなく実体):

```
~/Documents/GSE-sessions/gse_20260808_060459.ndjson   ← 元セッションが**この Mac に在る**
~/Documents/GSE-submissions/P009_block01_gse_20260808_060459.age  (8/08 15:10 作成)
                            …age.ok (approved) / …age.sent (sent)
manifest.jsonl: {"age":"P009_block01_gse_20260808_060459.age","block":1,"participant":"P009",…}
```

→ ★ 8/10 の Windows 分と**同じ扱い** (テスト送信) にしてよい。
⚠️ ただし **作られた OS が違う**ので、前置は `(windows_test)` ではなく
`(macos_test)` とするのが正確である (運用の型は同じ)。

### 今回さらに増えた後片づけ対象 (★ 本セッションのテスト送信)

```
Drive  P999_block01_gse_20260810_041051.age  482 B      id 1NE4fmRIrVHYq5atHmluPLzk49ZtlOBC0
       P999_block02_gse_20260810_041334.age  233,792 B  id 1Fry-3oRD9v6Ky_Exw47D6VzI_dA-_UlX
ローカル (この Mac) ~/Documents/GSE-submissions/ の P999_* 6 ファイル + manifest.jsonl の 2 行
```

★ `P999` は**存在しない番号**なので実データを汚さない。⚠️ ただし Drive に残ると
「これは何か」が後から分からなくなるため、削除するか `(macos_test)` を前置すること。
⚠️ Drive MCP はリネーム/削除ができないので、**人が Drive の UI から**行う。
