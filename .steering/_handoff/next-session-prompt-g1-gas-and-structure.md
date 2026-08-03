# 次セッション開始プロンプト — GAS の実動作検証と G1 構造の整理

> ## ✅ 2026-08-03 に実施済み（このプロンプトは**再実行しない**）
>
> 結果は `.steering/20260804-g1-pilot-execution/`（`decisions.md` の D-1/D-2・J-1〜J-5、`tasklist.md`）と
> `experiments/20260801-controlled-friction-task/notes.md` の「作りっぱなしを実際に動かして確かめた回」。
>
> | 項目 | 結果 |
> |---|---|
> | **T-1** GAS 実動作 | ✅ 通した。★ **欠陥 2 件を発見・修正**（受付メールの「署名」文言 / 実シートとの列ズレ） |
> | **T-2** ブラウザ表示 | ✅ 全項目クリア（文字数一致・コピー不可・番号固定・題材非露出） |
> | **T-3** Windows launcher | ❌ ★ **未実施**（Windows 実機が要る）。**残タスクはこれが本体** |
> | **D-1** 同意の様式 | ✅ **(a) 電子同意（G1-C）が正本・紙署名は廃止**。★ 6 か所を同時に是正した |
> | **D-2** 実施日 | ✅ **08-04** |
>
> ⚠️ ★ **本文中の「GAS は一度も動かしていない」は誤りだった**（旧版で 16:35 に配備済みだった）。
> ⚠️ ★ **「同意の食い違いは 2 文書」も誤り**で、実際は **6 か所**あった。
>
> **残っていること**: T-3 ／ 新規 P-ID 採番経路の検証 ／ 受付メールの着信確認 ／
> フォーム回答のスプレッドシート連携（★ G1-M は必須）／ `consent.md §8` の承認番号。
>
> ➡️ ★ **後続は `next-session-prompt-g1-v8-and-remaining.md` に移した**（2026-08-04）。
> ⚠️ その後 **第 8 版**（課題文の本文を来所前に開示）が入り、本ファイルの
> 「課題文は当日その場で初めて読む」という前提は**もう成り立たない**。**こちらを使わない。**

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-03 に大きく作り替えた（ブランチ `chore/g1-pilot-execution-prep`・**13 コミット・未 push**）。
⚠️ **データは依然 1 件も無い。** ⚠️ **GAS は Apps Script 上で一度も動かしていない。**

---

===

## §0 このセッションの位置づけ

**2026-08-03 に作ったものを「実際に動かして」確かめ、G1 の構造の残り 2 件を決める回。**

⚠️ ★ **前セッションは作りっぱなしである。** 機械検査（`run.sh` / `--selftest` / node スタブ）は
全部緑だが、★ **Apps Script 上の実動作・ブラウザでの表示・Windows 実機は 1 つも試していない**。

### ★ 前セッションで確定したこと（やり直さない）

| # | 決定 | 要点 |
|---|---|---|
| **G-1/G-4** | P-1 を **Windows(topic01) / macOS(topic02) で 1 回ずつ** | `blocks/PILOT-win.json` / `PILOT-mac.json` 生成済み |
| **G-2** | ★ **P-1 では強制比較（G1-M）を取らない**（`§2.8`） | `protocol.md §6` 冒頭に但し書き済み |
| **G-5** | 課題文は 1 枚ずつ（→ 画面方式に発展）。手引きは冊子化 | |
| **G-6→撤回** | 分野の事前開示は **第 7 版で撤回** | `§2.6` は元の強さに戻った |
| **第 7 版** | ★ **課題文は画面提示**（`pages/<ID>/blockNN.html`・ブロックごとに 1 ファイル） | `build_task_pages.py` |
| **登録** | ★ **G1-C がそのまま参加登録**（G1-R は作って廃止した） | `onG1ConsentSubmit` |
| **メール** | ★ **自動は受付の 1 通だけ**。リマインド無し・日時/場所は書かない | `sendThankYouEmail` は手動 |

⚠️ ★ **これらを再検討しない。** 根拠は `experiments/20260801-controlled-friction-task/notes.md`
の第 6 版・第 7 版の節と `.steering/20260804-g1-pilot-execution/decisions.md`。

---

## §1 ★★ まず実際に動かす（機械検査では捕まらないもの）

### T-1 GAS を Apps Script 上で動かす

**手順は `Form_G1/README.md` の「配備手順（コピペから実施まで・通し）」STEP 1〜10。**

```javascript
// 定数を 2 つ埋める（★ フォーム ID 3 本は記入済み。新規に作るフォームは無い）
var PHASE1_MGMT_SHEET_ID = "★Phase1 管理シートの ID★";
var G1_CONTACT = "研究責任者 ○○（xxx@example.com）";

setupG1Forms()             // ★ 既存 3 本の設問が作り直される（URL は変わらない）
previewRegisterAckEmail()  // 受付メールの文面をログで確認（送信しない）
// G1_AUTO_SEND = true にする
installG1ConsentTrigger()  // ★ 一度だけ
```

★ **確かめること**（node のスタブでは分からない）:

- [ ] 権限承認が通るか（Forms / Spreadsheet / Gmail）
- [ ] `setupG1Forms()` が 3 フォーム＋管理シートを作れるか
- [ ] ★ **G1-C にテスト提出して `onG1ConsentSubmit` が動くか**
      - Phase1 ロスターに P-ID が採番されるか
      - G1 実施トラッキングに行ができるか
      - 受付メールが届くか（`G1_AUTO_SEND=true` のとき）
- [ ] ★ **同じメールで 2 回提出しても再発番されないか**（冪等の実地確認）
- [ ] ⚠️ テストで作った行・P-ID を**後片付け**する（本番の採番に混ざらないように）

⚠️ ★ **失敗したらログをそのまま持ち帰る**。推測で直さない。

### T-2 ブロックページをブラウザで開く

```bash
cd experiments/20260801-controlled-friction-task
python3 build_task_pages.py --subject PILOT-win
open pages/PILOT-win/block02.html      # ★ 拡張機能なしのプロファイルで
```

- [ ] 課題文が読める・記入欄に打てる
- [ ] ★ **文字数カウントが動く**（`validate_materials.py` の `count_chars` と同じ規則）
- [ ] ★ **課題文を選択・コピーできない**（`user-select: none`）
- [ ] ブロック番号が埋まっていて編集できない
- [ ] タブのタイトルが「G1 ブロック 2」（★ 題材名が出ていない）

### T-3 Windows で launcher を試す

- [ ] `launch-g1-windows.bat` をダブルクリック → 文字化けしない（BOM+CRLF 済み）
- [ ] `gse-next.exe` が起動する
- [ ] ★ **起動中にもう一度実行 → 終了してから起動し直す**（`taskkill` 検証ロジック）

---

## §2 ★ 構造の残り 2 件（研究者判断が要る）

### D-1 ⚠️ 同意の取り方が 2 文書で食い違っている

| 文書 | 何と書いてあるか |
|---|---|
| `protocol.md §4.1 / §6` | 「`consent.md` を読み上げ、**署名を得る**」（紙署名が主） |
| `Form_G1/README.md` | 「紙は**フォームが使えないときの控え**」（フォームが主） |

★ **決めるのは倫理審査**である。`consent.md` 冒頭が「本文書は**雛形**」とし、
`§8` の**承認番号も未記入**なので、前セッションでは決めなかった。

→ 様式が確定したら **(a) 電子同意で足りる → 紙を廃止し `protocol.md §4.1` を直す /
(b) 紙署名が要る → README の「控え」表現を直す** のどちらかへ**両文書を同時に**そろえる。
⚠️ **片方だけ直すとまたズレる**（このプロジェクトで繰り返している失敗）。

### D-2 P-1 をいつ回すか

`protocol.md §5-1` は「課題文を作った日と 1 日空ける」を要求し、課題文は **08-03 生成**。
→ **最短 08-04**。⚠️ ★ **画面方式に変えたので、T-2 を済ませてから回すこと。**

---

## §3 GAS の改善候補（実動作を見てから決める）

⚠️ ★ **T-1 を通す前に着手しない。** 動かして初めて分かる問題が優先である。

- `refreshRosterStatus` 相当（G1 版の進捗集計）が要るか。★ n が小さいなら不要
- `buildManagementSheet` の「リンク集」に G1-C の**募集用 URL** を目立たせる
- ★ 受付メールの HTML 版（Phase1 の `f1EmailHtml_` 相当）。現状はプレーンテキストのみ
- テスト用の後片付け関数（`removeTestParticipant("P0xx")`）— T-1 の実地テストで要ると分かったら

---

## §4 制約（厳守）

- ★★ **`preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` を変更しない。**
  改訂するなら**第 8 版として記録し、判定を緩めていないかを論証**する。
  ⚠️ 第 6 版は**唯一「緩めていない」と言えなかった版**で、第 7 版で撤回した。同じ轍を踏まない。
- ⚠️ **版を上げたら `analyze.py` の `PREREG_REVISION` も上げる**
  （`--selftest` が `config.json` との一致を機械検査する。現在はどちらも **7**）。
- **PII**: 実名・メールを G1 実施トラッキングに書かない。**raw NDJSON をコミットしない**。
  **`blocks/*.json` / `pages/` をコミットしない**。★ **セッション日時を成果物に出さない**。
- ★ 文献に依拠する記述は `citation-ssot`。`docs/references.md` の次番号は **`[P45]` / `[V75]`**。
- 依存を足さない（Python は標準ライブラリのみ）。

---

## §5 現在の状態

- ブランチ **`chore/g1-pilot-execution-prep`**（`173c601`）・**13 コミット・未 push**。作業ツリーはクリーン。
- `bash run.sh` = **GREEN**（`build_task_pages.py --selftest` を含む）。
- `python3 scripts/check_g1_emails.py` = 緑（★ リポジトリルートで実行すること）。
- 事前登録 **第 7 版**（`config.json` = `analyze.py` = 7）。
- **データは 1 件も無い**。Phase1 は GATE2 pass / GATE3 DataInsufficient（凍結は解除されていない）。
- ⚠️ **未検証**: Apps Script 実動作 / ブラウザ表示 / Windows launcher。

---

## §6 まず読むもの（この順）

1. `experiments/20260801-controlled-friction-task/notes.md` の **第 6 版・第 7 版の節**（★ 何をなぜ変えたか）
2. `Form_G1/README.md`（配備手順 STEP 1〜10 ＋ G1-C が参加登録である理由）
3. `experiments/20260801-controlled-friction-task/protocol.md §1.2`（画面方式）
4. `.steering/20260804-g1-pilot-execution/decisions.md`（G-1〜G-6 / I-1〜I-3）
5. `preregistration.md` の **改訂履歴 第 7 版**＋`§2.12`／`§2.13`

---

## §7 終わり方

- T-1 / T-2 / T-3 の結果を `.steering/` と `notes.md` に**そのまま**記録する
  （★ 動かなかったものは「動かなかった」と書く）。
- `bash run.sh` が GREEN のまま。各 `--selftest` が緑のまま。
- D-1 / D-2 を決めたら**両文書を同時に**そろえる。
- 最後に `/cross-review`。⚠️ ★ **前回 Codex が予算を 458,940 トークン食った**
  （`per_invocation_max=30,000` を大幅超過。read-only でもリポジトリを自分で読み返すため）。
  **回す前に対策する**（file-read 無効化 / turn 数上限 / reasoning_effort 引き下げ）。
