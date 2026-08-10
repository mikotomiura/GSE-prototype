# 次セッション開始プロンプト — macOS の目視確認 ＋ 配布 zip の生成

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-10 に提出レシート UI を実装し、**Windows 実機で 5 項目すべて確認**して
`v0.1.25` をリリースした。⚠️ ★ **macOS の画面は誰も見ていない**のと、
**配布 zip の生成**が残っている。

---

===

## §0 このセッションでやること（★ この順で）

```
【A】★ macOS でレシート UI を目視する（この Mac でできる・5 分）
【B】配布 zip を生成する（Windows / macOS）
【C】⚠️ P009 のテスト送信の後片づけ（3 件・未処理）
```

⚠️ ★ **A を先にやる理由**: macOS の表示に問題があれば zip を作り直すことになる。

## §1 いまの状態（★ 確認済みの事実）

| | 状態 |
|---|---|
| `origin/main` | `9eb24d2`（PR #91 / #92 / #93 すべてマージ済み・作業ツリー clean） |
| タグ `v0.1.25` | ✅ `9eb24d2` を指す |
| GitHub Release `v0.1.25` | ✅ 作成済み（`build-windows` / `build-macos` / `release` すべて success） |
| 未マージの PR | **無し** |

### Release v0.1.25 の成果物（★ 実体で検算済み）

```
gse-next.exe                     10,786,304   Windows 本体
gse-submit.exe                    6,108,160   提出ツール
gse-unpack.exe                      736,768   ★ 研究者専用（配らない）
gse-next_0.1.25_aarch64.dmg      10,338,838   macOS 本体
gse-unpack                        1,110,576   ★ 研究者専用（配らない）
```

★ `gse-next.exe` に埋まった版文字列は **`0.1.25` が 2 件・`0.1.24` は 0 件**（実測）。
⚠️ サイズがドライラン版と 1 バイトも同じ（10,786,304）だが、SHA-256 は
`148fc1db…` → `9d20cac0…` で **別ビルド**である
（VERSIONINFO の `"0.1.24"` と `"0.1.25"` が同じ文字数なので size が変わらないだけ）。

## §2 【A】★ macOS でレシート UI を目視する

### 何を確かめるのか

Windows（WebView2）では **5 項目すべて確認済み**（`.steering/20260810-g1-submission-receipt-ui/verification.md`）。
⚠️★ **macOS は WKWebView で別エンジン**であり、片方の確認は他方の根拠にならない。
★ 2026-08-08 に「機械検査は全部緑なのに実機で読めない文字」を出した前例がある
（memory `ui-changes-need-eyes`）。

| | 見るもの |
|---|---|
| 【1】 | ブロック終了後の確認カード |
| 【2】 | ★ `記録を送信しています…` |
| 【3】 | ★★ `✅ この回の記録を送信しました（HH:MM・1 件）` |
| 【4】 | ★★ **文字が読めるか**（背景と同色でないか） |
| 【5】 | `✅ 送信を待っている記録はありません。` |

### 手順

1. Release から dmg を取る（`gh release download v0.1.25`）
2. dmg をマウントして `.app` を取り出す
3. `.app` と同じ階層に **`g1.mode`** を置く（★ これが無いと提出 UI が 1 枚も出ない）
   ⚠️ macOS の配布フォルダ構成は `experiments/20260801-controlled-friction-task/dist/_common/G1_実施用_macOS/` を見る
4. 参加者 ID は ⚠️★★ **必ず `P999`**（存在しない番号）
5. 1 ブロック（5 分）回して 5 項目を見る。★ 【3】はスクリーンショットを撮る

⚠️★★ **レシートは「実際に送信が成功した」ときにしか出ない**（設計 D-1）。
`g1-submit.json` が無いと `upload_disabled` になり【3】は永久に出ない。
→ 本番設定を入れる＝**本番送信先に 1 件届く**。だから ID は `P999` にする。

## §3 【B】配布 zip の生成

```bash
experiments/20260801-controlled-friction-task/make-common-app-zip.sh
```

- ⚠️ dmg をマウントして `.app` を取り出し、**署名を検証**する作り（`codesign --verify --strict`）
- 出力は `dist/_common/G1_実施用_macOS.zip` と Windows 版
- ⚠️ ★ `dist/` は **vite の出力先**でもある。★ **`npm run build` を走らせると中身が消える**
  （2026-08-10 に実際に消して artifact を取り直した）。★ CI の artifact はスクラッチパッドへ落とすこと

### 配布物に入れるもの / 入れないもの

| | 入れる |
|---|---|
| `gse-next.exe` / `gse-next.app` | ✅ |
| `gse-submit.exe` | ✅（提出の実体） |
| `g1.mode` | ✅ **必須**（無いと G1 モードにならない） |
| `pubkey.txt` / `g1-submit.json` | ✅ |
| `gse-unpack` / `gse-unpack.exe` | ❌ **研究者専用。配らない** |

★ 日本語ファイル名を含む zip は `scripts/make-participant-zip.sh` を使う
（UTF-8 フラグ bit11 を立てないと Windows の「すべて展開」で化ける）。

## §4 【C】⚠️ P009 のテスト送信の後片づけ（★ 未処理）

ドライランで **手順書は `P999` 指定だったが `P009`（割り当て済みの実番号）で送信された**。
経緯と判断は `.steering/20260810-g1-submission-receipt-ui/verification.md` に記録済み。

1. **Drive でリネーム**（`(windows_test)` を前置。8/09 のテストと同じ型）
   `P009_block01_gse_20260810_024022.age`
   id `1YJB8pjcr7zsEsVWLV5OoM3o_zRpCQCIu`
   ⚠️ Drive MCP はリネーム/削除ができない → **人が UI から**
2. **Windows 機のローカル**: `~/Documents/GSE-submissions/` の同名 `.age` と `.sent`、
   `manifest.jsonl` の該当行
3. ⚠️ **8/08 の `P009_block01_gse_20260808_060459.age`（66,236 B）の素性が不明**。
   テストなら同じくリネームする

★ 番号消費は伝播しない（`next_block_number` はローカルの提出物フォルダだけを見る）。
⚠️ ただし **サーバ側では実 P009 の提出物と両方が block01 を名乗る**ので、前置は必要。

## §5 ⚠️ 積み残し（急ぎでない）

- ⚠️★★ **macOS ではフック生存検知が動かない**（`liveness.rs:141` が `None` を返す）。
  macOS 参加者は Windows と同じ保護を持たない。★ 配線は別タスク
  （`CGEventSourceSecondsSinceLastEventType`）
- ⚠️★ **`f1` の凍結**（`.steering/20260809-g1-hook-liveness-detection/measurements.md §7-2`）。
  ウィンドウが壁時計でなく最後のイベント基準なので、長時間沈黙用の `SilencePath` が
  実質到達不能。実測で **打鍵ゼロ 15 分でも `p_stuck` 1.1% 止まり**。
  → `HMM_VERSION` bump ＋ ゴールデン再生成が要り、⚠️ **Phase 1 の較正データはこの挙動の下で
  採られている**ので、**凍結に触れてよいかの判断が先**
- `analyze.py` 側の `hook_health` 消費者（`validate_blocks.py` には入れた）
- ⚠️ `gse-dataset` の既存 NDJSON が schema 検証を通らない（本トラックと無関係）
- ⚠️ レシート UI に `code-reviewer` / `security-checker` / `/cross-review` は**未実施**
  （前セッションは subagent 起動が既定で禁止されていた）

## §6 ⚠️★ 前セッションで踏んだ罠（★ 繰り返さない）

1. ⚠️★★ **タグを打つ前に版番号を検算しなかった。**
   版上げ PR が未マージのまま `v0.1.25` を打ってしまい、
   **「タグは v0.1.25・中身は 0.1.24」のリリースが走った**（ビルドを cancel して復旧）。
   → ★ **打つ前に必ず `git show HEAD:package.json | grep version` で確認する。**
2. ⚠️★ **CI の artifact を `dist/` に落とした** → `npm run build`（vite outDir）が**消した**。
   → ★ artifact はスクラッチパッドへ。
3. ⚠️★ **`concurrency: cancel-in-progress` で走行中の build を push が巻き添えにした。**
   → ★ push の前に `gh run list` で in-progress を確認する。
4. ⚠️★★ **自分の測定器が偽陽性を出した（2 回）。**
   - 輝度測定で `.start-button`（`linear-gradient`）を `cr=1.00`＝背景と同色と誤判定
     → `background-image` を見ていなかった。★ 2026-08-08 の**実際の欠陥と見分けがつかない**
   - `grep -c "[applog]"` の `[...]` が**文字クラス**として解釈され、a/p/l/o/g を含む
     全 110 行を数えて「applog 警告 110 件」と誤報告（正しくは `grep -F` で **0 件**）
   → ★ **欠陥を直しに行く前に、測定器のほうを対照で検算する。**
5. ★ `--selftest` が緑でも根拠にせず、**2 方向に変異させて赤を見る**
   （案 A の実装で実施。空振りでないことを確認できた）
