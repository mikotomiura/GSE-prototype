# 次セッション開始プロンプト — P-1 実施 / 分析 と G1 の残タスク

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-04 に 8 コミット追加。ブランチ `chore/g1-pilot-execution-prep`
（`main` から **39 コミット・未 push**）。作業ツリーはクリーン。

⚠️ ★ **旧引き継ぎ `next-session-prompt-g1-v9-and-pilot.md` は本セッションで一部更新したが、
本ファイルが最新である。** 第 9 版そのものの論証は旧版に残っているので、
**第 9 版の中身を知りたいときだけ**そちらを読む。

---

===

## §0 このセッションの位置づけ

**P-1 の配布物が Drive にそろい、研究者が P-1 を実施する段階に入った。**
本セッションでは実施していない。⚠️ ★ **T-3（Windows 実機）の記入枠はまだ空である。**

### ★ 本セッションで確定したこと（やり直さない）

| # | 決定 / 事実 | 要点 |
|---|---|---|
| 1 | ★ **受付メールは着信した** | `onG1ConsentSubmit` → `MailApp` → 実受信箱の経路が**端から端まで通った** |
| 2 | G1 実施トラッキングの **`P009` 行 = 残す** | ⚠️ ★ **由来はテスト提出**である（この記録が唯一の手がかり） |
| 3 | ★★ launcher 迂回への防御 = **案 B**（環境変数が無ければ警告 / 起動拒否） | ⚠️ **決定であって実装ではない**。P-1 後・別ブランチ |
| 4 | 新規 P-ID 採番の検証 = **実行しない** | ⚠️ ★ **本番当日、新規参加者の初回提出でこの枝が初めて走る**。リスクを明示的に受容した |
| 5 | ★ 打鍵取得の実績あり（研究者の指摘） | ad-hoc 署名の Input Monitoring リスクは**最優先から外した**（★ 実績 > 設計想定） |

根拠は `.steering/20260804-g1-pilot-execution/tasklist.md` の末尾と
`experiments/20260801-controlled-friction-task/notes.md` の 2026-08-04 の節。

---

## §1 ★ P-1 の実施手順（研究者が回す）

### 用語（⚠️ 逆向きなので混同しない）

| 何を | どうする | 根拠 |
|---|---|---|
| **アプリのセッション**（= NDJSON 1 ファイル） | ★ **分ける。** ブロックごとに起動し直す | `protocol.md §1` |
| **実施機会**（座って通す時間） | ★ **分けない。** 4 ブロックを一気通貫（約 23 分） | `preregistration.md §2.14-1` |

### macOS 回（`PILOT-mac` / topic02）— ★ この Mac は準備済み

```
g1        # ~/.zshrc に alias 済み。ブロックごとに 1 回（4 回）。2 回目以降は ↑ + Enter
```

- `/Applications/gse-next.app` 導入済み・**quarantine なし**・`codesign --verify --strict` OK
- 資材は `~/G1-mac/`（dmg / launcher / `pages/block01〜04.html`）
- ⚠️ ★ **初回起動時に Input Monitoring の許可 → アプリ再起動**が要る（対話）
- ⚠️ 初回は「ターミナルが gse-next を制御しようとしています」の許可も出る（`osascript` の quit）

### Windows 回（`PILOT-win` / topic01）— ★ **先に回す**

`ime_dwell_med` が取れて **14 特徴**（mac は構造的に欠測し実質 13）。
⚠️ ★ **同日なら 60 分以上空ける**か翌日（疲労が打鍵量の測定を歪める）。

### ★★ 各ブロックの「30 秒チェック」（本セッションで追加）

```bash
f=$(ls -t ~/Documents/GSE-sessions/gse_*.ndjson | head -1)
grep -c -E '"type":"(probe_assignment|probe_triggered|realtime_label)"' "$f"
```

★ **`0` なら続行。1 以上ならそのブロックは使えない。**
⚠️ ★ **`grep -c` は 0 件でも `0` を出す。「何も出ない」ではなく数字を読む**（実測）。
★ **ここで捕まえれば 1 ブロックのやり直しで済む**（終了後の `--dataset` まで待つと 4 本まとめて失う）。

### ★ `HMM_VERSION` の取り方

```bash
f=$(ls -t ~/Documents/GSE-sessions/gse_*.ndjson | head -1); echo "対象: $f"; head -1 "$f"
```

⚠️ ★ **ワイルドカードのまま `head -1` しない**（`==> ファイル名 <==` が返る・実測）。
⚠️ ★ **repo の `engine.rs`（`0.3.0`）で代用しない**（配布は `v0.1.22` 時点のもの）。

### ⚠️ 実行不能なので**やらない**こと

★ 「アプリのログに `probe scheduler DISABLED …` が出ることを確認」は**両 OS とも観測できない**
（Win: `windows_subsystem="windows"` / mac: `open -a` で stdout が出ない）。
本セッションで `protocol.md` / 両 launcher から**除去済み**。

---

## §2 ★ P-1 実施後にやること

1. G1-S に回答 → `analyze.py --verify-blocks --dataset ~/gse-dataset --subject PILOT-win`（mac 回は `PILOT-mac`）
   - ⚠️ ★ **P-1 が `--verify-blocks` の初回実行**である。出力が壊れていたら**その場で解析せず記録だけして持ち帰る**
2. NDJSON を gse-dataset へ（★ **G1 のセッションであることを明記**。P-ID が Phase1 と混ざる）
3. `validate_blocks.py --dataset ~/gse-dataset` が緑
4. `env.md` / `record-sheet-pilot.md` / `config.json` の `hmm_version` に転記
5. ★ **P-1 の目的は「5 分で十分な打鍵が出るか」**。⚠️ **判定はしない**（`§2.8`）

⚠️ ★ **`§3.1〜§3.6` を変更しない。** 改訂するなら**第 10 版として記録し、向きごとに論証**する。
版を上げたら `analyze.py` の `PREREG_REVISION` と `config.json` を**両方**上げる（現在どちらも **9**）。

---

## §3 ★ 残タスク（推奨順）

### ~~🔴 倫理審査 承認番号~~ → ★ **撤回した**（研究者判断 2026-08-04）

⚠️ ★ **倫理審査の記入枠は配布文書から撤去した**（`consent.md` / `debrief.md` / `protocol.md`）。
★ **確証実施のブロッカーではなくなった。** 経緯は `decisions.md` の **D-3**。

### 🟢 P-1 の後

| # | 何 | 備考 |
|---|---|---|
| 1 | ★★ **案 3 ＋ 案 B の統合実装**（アプリ内 G1 モード） | ⚠️ `§5.4` に触るので **第 10 版**の論証が要る → `/start-task` から別セッション |
| 2 | **STEP 8**（G1-M の回答をスプレッドシートへ） | ★ 必須。`forms_to_blocks.py` が CSV を読む |
| 3 | 確証用の配布物 ＋ Drive 共有設定 | ⚠️ **1 の後にやる**（構成が変わるため）。現在フォルダは **owner のみ**に共有されている |
| 4 | ★ **CI リリースゲートの修正**（下記 §4） | 独立して着手できる |
| 5 | 案 4（Developer ID ＋ 公証・$99/年）の判断 | ⚠️ **mac の被験者を取るなら実質必須** |

### ⚠️ 未検証のまま残すと決めたもの

- **新規 P-ID 採番**（`g1NextParticipantId_` → `roster.appendRow`）— 本番当日に初めて通る
- `sendTaskMaterialsEmail` は 1 度も実行していない
- ブロックページを**拡張機能なしのプロファイル**で開けるか
- `file://` そのものでの表示（`http://127.0.0.1` で代替検証した）

---

## §4 ⚠️★★ CI リリースゲート 3 本が発火していない（本セッションの発見）

配布された `v0.1.22` の `.app` に **`gse-package` / `gse-unpack` が残存**していた。
`ci.yml:248` は残存で `::error::` ＋ `exit 1` する設計であり、strip コミット `f8286aa`(2026-06-29) は
`v0.1.22`(2026-08-03) に **含まれている**（`git merge-base --is-ancestor` で確認）。

**機構**（★ `silent-failure-in-guard-scripts` の型）:

```bash
APP=$(find src-tauri/target/release/bundle -name "*.app" -type d | head -1)
if [ -n "$APP" ]; then     # ⚠️ ★ else が無い
  ... strip / 再署名 / ::error:: ゲート 3 本 ...
fi                         # → $APP が空なら全部飛んで step は exit 0
```

**傍証**: 実物の署名フラグが `adhoc,**runtime**`。CI は
「`--options runtime` は ad-hoc 署名では使用しない」と明記して再署名する
→ ★ **載っているのは tauri 自身の署名 = CI の再署名は走っていない**。

⚠️ ★ **`find` が空を返した理由は未特定**（Actions のログが要る）。

**影響**: P-1 は実害なし。確証配布では `gse-unpack` が被験者に渡る（鍵が無ければ無力）。
⚠️ ★ **より重いのはゲート 3 本がまとめて無効だったこと** —
`gse-submit` / `pubkey.txt` の欠落も検出できない状態だった（今回は実物に両方あることを確認済み）。

**直し方**: `if [ -n "$APP" ]` に `else` を足して「`.app` が見つからない = 失敗」として `exit 1`。

---

## §5 現在の状態

- ブランチ **`chore/g1-pilot-execution-prep`**・**39 コミット・未 push**・ツリーはクリーン
- `bash run.sh` = **GREEN** / `analyze.py` `validate_blocks.py` `assign.py` `build_task_pages.py`
  の `--selftest` すべて緑 / `make-handouts.sh` 緑
- 事前登録 **第 9 版**（`config.json` = `analyze.py` = 9）
- **データは 1 件も無い**

### Drive 配布物（★ そろっている）

| `Gate/G1/G1_実施用_macOS`（7） | `Gate/G1/G1_実施用_Windows`（8） |
|---|---|
| `gse-next_0.1.22_aarch64.dmg` 5,995,136 | `gse-next.exe` 10,316,800 |
| `launch-g1-macos.command` 7,991 | `gse-submit.exe` 960,512 |
| `block01〜04.html` 7268/6858/6642/7268 | `launch-g1-windows.bat` **4,574** |
| `README_先に読む.txt` 3,109 | `pubkey.txt` 507 |
| | `block01〜04.html` 7268/6869/6613/7268 |

⚠️ ★ **バイト一致を主張できるのは `base64Content` で送ったものだけ**
（`.command` / `.bat` / mac の `block01〜04`）。
**`.dmg` / `.exe` / `pubkey.txt` / Windows の `block0N.html` はサイズしか照合していない**
→ ★ 実機で `certutil -hashfile … SHA256`（Win・期待値は記入枠に記録済み）/
`shasum -a 256` = `41069c47a1ab64f19bd9183bc26184207266ccdd29f76e0f4fd96290e2b9da85`（mac）。

- Apps Script `GSE_Gate1` = リポジトリと SHA-256 一致 ／ トリガー 1 件・`G1_AUTO_SEND=true`
- 3 フォームの公開 URL の**指紋**を `Form_G1/README.md` STEP 9 に記録（実 URL は `.idea/短縮版リンク集.md`・gitignore 済）
- 管理シート `1jQPxF4f…`（G1 実施トラッキングは 19 列）／ Phase1 ロスター `1ND5HSXZ…`

---

## §6 ⚠️★ 本セッションで踏んだ罠（先に読む）

| 罠 | 対処 |
|---|---|
| ★★ **Drive MCP の `textContent` は中身によってバイトが化ける** | ⚠️ `\uXXXX` を含む HTML で **44 B 欠損**した（7268 → 7224）。★ **`base64Content` を使う**（`base64 < file \| tr -d '\n'`）。実測で 6858/6642/7268 が完全一致 |
| ★ **上げたら必ず `fileSize` を照合する** | ★ これが私の破損を捕まえた。⚠️ **`create_file` は更新も削除もできない**ので、壊すと同名重複が残り人に頼むことになる |
| ★★ **`.bat` は行末 `^` が行継続**／`echo` 内の `<` `>` がリダイレクト解釈 | ⚠️ 両方とも私が持ち込んだ。★ **Windows で実行できないなら危ない構文を使わない**。`echo` 行に `& \| < > ^` と単独 `%` が 0 件であることを機械検査した |
| ★★ **是正を片方の OS にだけ入れて忘れた** | `writing-pad.html` の記述を mac 側だけ直し `.bat` に残した。★ **同じ内容を持つファイルが 2 つあるときは両方 grep で数え直す** |
| ★ **メタデータの数値を実体の検査と読み替えた** | zip の「破損」は Drive の `fileSize` だけが根拠で、実物の EOCD は 13,815 B を宣言していた。★ **中身を言うなら中身を読む** |
| ⚠️ **誤った根拠から立てた正しい規則を、根拠を崩したついでに捨てない** | zip の診断は誤っていたが「1 ファイルずつ上げてサイズ照合」という規則自体は正しかった |
| ★ **`gh release download` は quarantine を付けない**（実測） | ⚠️ ブラウザ / Drive 経由だと付く。★ **「剥がす」より「付けない」** |
| ★ `bash <file>` は実行ビットも quarantine も回避する（3 状態で実測） | ⚠️ ★ **Finder のダブルクリック経路は未検証**（bash から再現できない） |

---

## §7 制約（厳守）

- ★★ **`preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` を変更しない**
- ⚠️ 版を上げたら `analyze.py` の `PREREG_REVISION` と `config.json` を**両方**上げる（現在 **9**）
- **PII**: 実名・メールを G1 実施トラッキングに書かない。**raw NDJSON をコミットしない**。
  **`blocks/*.json` / `pages/` をコミットしない**。★ **セッション日時を成果物に出さない**
- ⚠️ ★ **本リポジトリは一時 public にする運用がある。** フォーム回答 URL を repo に置かない
- 依存を足さない（Python は標準ライブラリのみ）
- ★ 文献に依拠する記述は `citation-ssot`。`docs/references.md` の次番号は **`[P45]` / `[V75]`**
- ★★ **ブラウザを触る前に `.claude/skills/browser-verification/SKILL.md` を読む**
- ★ `/cross-review` は `-C "$TMPDIR_WORK"` の措置が入っている（実測 458,940 → 39,936 トークン）。
  ⚠️ **予算ガードは「呼ぶ前」しか見られない**ので、消費量をログで確認する

---

## §8 まず読むもの（この順）

1. `.steering/20260804-g1-pilot-execution/tasklist.md` の **2026-08-04 の節すべて**（★ 実測結果）
2. `experiments/20260801-controlled-friction-task/record-sheet-pilot.md`（★ P-1 の記録用紙・30 秒チェック入り）
3. `experiments/20260801-controlled-friction-task/protocol.md` の **`§1` / `§5.1` / `§6` / `§6.1`**
4. `experiments/20260801-controlled-friction-task/preregistration.md` の **`§2.8`（パイロット）/ `§2.14`**
5. `Form_G1/README.md`（配備手順 STEP 1〜10・公開 URL の指紋）

## §9 終わり方

- 実測結果を `.steering/` と `notes.md` に**そのまま**記録する
  （★ **動かなかったものは「動かなかった」、試していないものは「試していない」**と書き分ける）
- `bash run.sh` が GREEN のまま。各 `--selftest` が緑のまま
- 決定を変えたら**関係する文書を全部同時に**直す（⚠️ ★ **grep で数え直す**）
- ★ **決定を変えたら検査のほうも増やす**
- 最後に `/cross-review`（★ 消費量をログで確認する）
