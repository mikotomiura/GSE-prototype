# 詰まりと解決 — O1 リリースと配布物の作り直し

## B-1. ⚠️★★★ 引き継ぎメモの D-4 の判定条件が**誤っている**

**メモの記述**（`next-session-prompt-o1-release-and-rebuild.md` §1-D-4）:

> ⚠️ `gse-app.log` に **`Probe scheduler thread started` が出ていない**こと

**実測**（v0.1.30 の配布物・O1 モードが確実に立っている状態）:

```
2026-08-30T05:36:59.067386Z  WARN gse_next_lib: O1 MODE ENABLED (source=marker): ...
2026-08-30T05:36:59.929353Z  INFO gse_next_lib: Probe scheduler thread started   ← ★ 出る
```

★ **O1 モードでも、このスレッドは必ず起動する。** → ⚠️ メモの条件は**永久に満たされない**。

### なぜそうなるのか（★ コードで確定）

`src-tauri/src/lib.rs:4418-4436`:

```rust
let disabled_by_g1 = g1_mode();
let probes_disabled = disabled_by_env || disabled_by_g1.is_some();   // ⚠️ O1 が入っていない
...
if !probes_disabled { thread::spawn(|| { tracing::info!("Probe scheduler thread started"); ... }) }
```

⚠️ ★ **プローブ抑止のゲートは `g1_mode()` しか見ていない。** O1 は明示的に止められていない。

### ではなぜ実害が出ないのか（★ 実測で確認）

スケジューラ本体は `SESSION_START_MS == 0` のあいだ `continue` するだけで、何も生まない。
そして `src/App.tsx:336` が逐語:

> ★ `start_session` も `record_session_meta` も **呼ばない** ——
> 記録は backend で既に走っており、宣言は被験者が任意のときに行う。

→ ★ O1 では `SESSION_START_MS` が 0 のままなので、**スケジュールが 1 件も作られない**。

**客観検証**（★ `lib.rs:4423` 自身が指定する方法 = NDJSON の `probe_assignment` 行数）:

| ファイル | `probe_assignment` | `probe_triggered` |
|---|---|---|
| `gse_o1_20260830_053659.ndjson` | **0** | **0** |
| `gse_o1_20260830_053726.ndjson` | **0** | **0** |

⚠️★ **私は最初これを 1 件と誤報告した。** `grep -c 'probe_assignment'` は
**行内の文字列**を数えるだけで、実体は `meta` 行（1 行目）の中の文字列だった。
→ ★ 型で数え直して 0 を確認した（memory `measurement-instrument-false-positives` と同型）。

### ⚠️★★ 残る潜在欠陥（★ 本セッションの発見・未修正）

★ O1 のプローブ抑止は **「たまたま `start_session` が呼ばれないから」成立している**。
⚠️ **設計としての門が無い。** G1 には明示ゲート (`disabled_by_g1`) があるのに O1 には無い。

→ ⚠️ 将来 O1 で `SESSION_START_MS` を立てる変更が入ると、
**被験者にランダムプローブが飛ぶ**（★ 同意文書に無い割り込み）。
★ しかも `lib.rs:4424` の「止まっているつもりを防ぐ番兵」warn も、O1 では**出ない**
（`probes_disabled` が false なので）。

**推奨**: `probes_disabled` に `crate::o1::is_o1()` を足し、O1 でも番兵 warn を出す。
⚠️ **本セッションでは直していない**（★ D の通し確認が主目的で、挙動を変えると
いま測っている配布物と実体がずれるため）。→ ★ 別 PR で。

### ★ 正しい判定条件（★ メモを直すならこれ）

- ❌ 「`Probe scheduler thread started` が出ていないこと」
- ✅ 「**NDJSON に `probe_assignment` 型の行が 0 であること**」（★ コードの指定と一致する）

---

## B-2. ⚠️ TCC 権限が新バイナリで再要求された（★ 未解決・研究者の操作が要る）

**メモの記述**: 「⚠️ TCC は前回**既に許可済み**だった（`input_monitoring=true accessibility=true`）」

**実測**: ⚠️ **新しいバイナリでは許可されていない。**

```
WARN ... Input Monitoring permission not granted. Opening System Settings ...
WARN ... Input Monitoring (ListenOnly) failed 3 times. Switching to Accessibility permission fallback ...
WARN ... CGEventTap creation still failing via Accessibility after 5 attempts.
ERROR ... keyboard hook may be dead: the system saw input but the hook was not called
          (keystrokes may NOT be recorded) starved_ms=30095
```

★ トレイは `HookDown (⚠ GSE — 計測できていません（研究者に連絡してください）)` を表示している
＝ **番兵は正しく働いている**（★ 黙って壊れていない）。

→ ⚠️ **`key` 行が出るかの確認 (D-4) は、許可を与えるまで実施できない。**

---

## B-2b. ✅ セッション NDJSON 2 本の消失は**研究者による手動削除**（★ 不具合ではない）

★ 通し確認の途中で `gse_o1_20260830_053659.ndjson` / `gse_o1_20260830_053726.ndjson` が
両方消えた。⚠️ ゴミ箱にも他の場所にも無く、削除に類するログ行も
`redaction_ledger.jsonl` も無かったため、**アプリ側の不具合の可能性**を疑って調査した。

→ ★ **研究者が Finder で手動削除したもの**と確認（2026-08-30・本人の回答）。
（★ アプリは終了時に `Opening session folder` でセッションフォルダを Finder に開く。）

⚠️★ **推測で「削除された」と書かずに本人に確認したのは正しかった** ——
もし不具合だったなら、これは「被験者のデータが黙って消える」最悪の欠陥であり、
★ リリース作業を止めてでも先に潰すべき事象だった。

★ 教訓として残す: **痕跡が無いこと自体は原因を決めない。**
「ゴミ箱に無い / ログに無い」は「アプリが消した」の証拠にも「人が消した」の証拠にもならない。

## B-4. ⚠️★★★ **O1 の画面に、O1 では出てはいけない UI が 3 つ出ている**（★ 実機の目視で発見）

★ 2026-08-30、配布物 v0.1.30 を macOS 実機で動かした画面（研究者提供のスクリーンショット）から発見。
⚠️ **機械検査は 1 つも捕まえていない**（配布ゲート 19/19・`--selftest` 19/0 とも緑）。
★ memory `ui-changes-need-eyes`（「UI を変えたら画面を見るまで完了ではない」）の再現である。

⚠️ ★ `Dashboard.tsx:574` の `{!o1Mode && (` は **「セッションの提出」節だけ**を隠している。
★ つまり O1 ゲート自体は存在するのに、**掛け忘れが 3 か所ある**。

### B-4a. ⚠️ 「較正モード」バッジと、**存在しない問いへの回答指示**

画面の文言（逐語）:

> **較正モード**
> 主観回答の独立性を保つため、推定状態 (Flow / Incubation / Stuck) は表示していません。
> **画面の問いに、今の感覚のまま回答してください。**

`Dashboard.tsx:226` / `:452`:

```tsx
const showModelOutput = !calibrationMode && debugView;
...
{!showModelOutput ? ( <div className="calibration-notice"> ... ) : ( ... )}
```

⚠️ 被験者ビルドは `debugView === false` なので、★ `calibrationMode` の値に関係なく
**この節は必ず出る**。→ ⚠️ O1 でも「較正モード」と表示される。

★ **より悪いのは後半**である: 「画面の問いに回答してください」と指示しているが、
⚠️ **O1 に問いは出ない**（★ 本セッションで `probe_assignment` = **0 行**を 3 ファイルで実測）。
→ ⚠️ **被験者は永遠に来ない問いを待つことになる。**

⚠️ ブラインドにすること自体は正しい（`App.tsx:1036` 逐語「O1 では**常にブラインド**にする。
自然作業を数日〜数週間観測するあいだ推定状態が画面に出ていると、被験者はそれを見て行動を変える」）。
★ 問題は**バッジ名と後半の指示文**であって、非表示そのものではない。

### B-4b. ⚠️★★★ 自己ラベルのボタンが O1 で押せる（★ ホットキーは同じ理由で**わざわざ止めてある**）

画面に **「🔴 今とても詰まっている」** ボタンがある（`Dashboard.tsx:523-540`）。
⚠️ **`o1Mode` ゲートが掛かっていない。** backend `record_self_marker`
(`lib.rs:2522`) にも **O1 の門が無い**（★ デバウンスのみ）。

⚠️★★★ 一方で **同じ機能のホットキーは O1 で意図的に登録していない**。起動ログ逐語:

> `O1: global shortcuts are NOT registered (they would take 6 key combinations away for weeks and
> could write user_label / review_marker rows that **the consent form does not list**)`

→ ★ **「同意文書に無い行を書くから」という理由でホットキーを塞いだのに、
ボタンは残っている。** ⚠️ 塞いだ理由がボタンにはそのまま当てはまる。

⚠️ ★ **正確に書く**: ボタンが書くのは `realtime_label`
(`record_self_marker_inner` → `LogEntry::realtime_label_answered`) であり、
ログ文が挙げる `user_label` / `review_marker` と**同じ行型ではない**。
★ したがって「同意文書違反である」と断定はしない —— ⚠️ **同意文書 §を読んで
`realtime_label` が挙がっているかを研究者が確認すること**。
★ ただし「ラベル付けの導線を O1 の被験者に与えている」点は同じであり、
⚠️ **片方だけ塞いだ状態には根拠が無い**。

### B-4c. ⚠️ 「セッション終了」ボタンが O1 で押せる（★ 押すと**その日の収集が終わる**）

`Dashboard.tsx:637` の 「セッション終了」→ `handleQuit` → `invoke("quit_app")`
(`App.tsx:423`) ＝ **アプリを終了する**。

⚠️ O1 は「セッション」を被験者が区切る設計ではない（★ 記録は常時・ローテートは 24 時間）。
→ ⚠️ 押した被験者は「今回の分を終えた」つもりで、実際には**その日の収集を止める**。
★ README / 受付メール逐語「**アプリが起動していない日は、記録がまるごと空になります**」と正面から衝突する。

⚠️★ **開発者は同種の配慮を既にしている**: `App.tsx:1032` 逐語
「⚠️ O1 では「戻る」を出さない (押しても何も起きないボタンを見せない)」。
→ ★ **「何も起きないボタン」は隠したのに、「その日の収集を止めるボタン」は残っている。**

### ★ 推奨（⚠️ 本セッションでは直していない）

⚠️ いま直すと**測定中の配布物と実体がずれる**ので、**別 PR**にする。
★ ただし B-4b / B-4c は **被験者に配る前に**塞ぐべきである（★ 研究者判断）。

| | 直し方の案 |
|---|---|
| B-4a | 較正の文言を `calibrationMode` で分岐させ、O1 では「バッジ名」と「問いに回答」の一文を出さない |
| B-4b | ボタンを `{!o1Mode && ...}` で隠す **＋ backend `record_self_marker` にも O1 の門**（★ 片側だけにしない） |
| B-4c | O1 では「セッション終了」を隠す。⚠️ 終了手段が無くなる問題は**トレイの「GSE を終了」が既にある**（`tray.rs:142`）ので解決済み |

★ ⚠️ **回帰の掛け金**: 直したら「O1 で画面に出ない文言」の検査を
`make-common-app-zip.sh --selftest` 側に足す（★ 現状の検査は README 文言しか見ていない）。

## B-5. ⚠️★★★ 引き継ぎメモの **D-7 の操作順が O1 では逆**（★ 私はそれをそのまま渡して踏ませた）

**メモの記述**（§1-D-7）:

> ⚠️ **一時停止 → 削除**の順で操作する

⚠️ ★ **これは Phase1 / G1 の規則であって、O1 には当てはまらない。**

★ 一次資料（`RecordingControls.tsx:505-508` 逐語）:

> ★ O1 では削除の直前に**現行ファイルを閉じてから**消すので、いまの記録も消せる。
> ⚠️ 逆に**止めているあいだは閉じられない**ので、そのときだけ再開を促す。
> ★ 通常運用 / G1 は従来どおり「先に止める」を出す (挙動を変えていない)。

`lib.rs:1400`:

```rust
if crate::o1::is_o1() && !crate::recording::is_paused() {   // ★ 停止中はローテートしない
```

⚠️ 停止中にローテートしないのは**意図的**である（逐語「停止中は `session_meta` が停止ゲートに
落ちるので、回すと**宣言が黙って失われる**」）。

### ★ 実際に起きたこと（2026-08-30・実測）

| 時刻 (UTC) | 出来事 |
|---|---|
| 06:51:06 | `tray state -> Stopped`（★ 研究者が「すぐ止める」を押した＝**私の誤った指示**） |
| 06:51:51 | `delete_time_range completed files_touched=0 lines_removed=0 files_skipped=1` |
| 06:51:58 | 同上（★ 案内に従って再実行したが、停止中なので**何度やっても同じ**） |
| 06:52:03 | `tray state -> Measuring`（再開） |

→ ⚠️ **被験者が消したい区間 (15:30–15:51) は 1 行も消えなかった。**
★ 台帳には `files_touched:0, lines_removed:0` の行が 2 本残った（★ 台帳自体は正しく動いている）。

### ✅ E-1（削除後の案内が O1 で逆を指す）は**再発していない**

★ 画面に出たのは `o1Mode && !paused` の分岐の文言であり、
⚠️ 旧文の「『すぐ止める』を押してからもう一度実行してください」**ではなかった**。
→ ★ 2026-08-28 の修正は効いている。⚠️ **メモの「E-1 が踏めるのはここ」は外れ**である。

⚠️★ ただし**私の指示が原因で、正しい案内が出る前に停止させてしまった**。
★ 教訓: **引き継ぎメモの操作手順も一次資料で裏を取ってから渡す。**
（memory `feedback-verify-before-claiming`: 三次資料を根拠にしない。★ 私はメモをそのまま渡した。）

## B-6. ⚠️ キーボードフックの飢餓が頻発している（★ 観察・本セッションの主題外）

★ 実測（2026-08-30 の 1 セッション・約 35 分）:

| | 回数 |
|---|---|
| `keyboard hook may be dead` / `is NOT delivering events` | **13** |
| `keyboard hook is delivering events again` | 7 |
| NDJSON の `starve_window` 行（現行ファイル） | 7 |
| NDJSON の `key` 行（現行ファイル） | 1794 |

★ **打鍵は記録できている**（1794 行）ので致命ではない。
⚠️ ただし `starved_ms=120340` の回もあり、逐語「the system saw input but the hook was not called」
＝ **入力があったのにフックが呼ばれていない**区間が 2 分続いた。

⚠️ ★ 原因は未調査。★ 候補: macOS の `secure_input`（★ `secure_input` 行が実在する）／
CGEventTap の失効（memory `macos-tap-idle-away-probe-bug` と同型か）。
→ ★ **別タスクで追う。** ⚠️ 被験者環境で頻発すると欠測になるので、優先度は低くない。

## B-3. ✅ Apps Script の `SHARED_SECRET` を更新した（★ 2026-08-30 に解消）

| 側 | 状態 |
|---|---|
| 送信側 `Form_O1/o1_submit.json` | ✅ Claude がローテート（sha256[:12] = `6994e16cdb42`） |
| 受信側 `GSE_O1_Submit` のスクリプト プロパティ | ✅ **研究者が登録**（2026-08-30） |
| `checkSubmitConfig()` | ✅ 緑（研究者が実行して確認） |

★ プロジェクトは `GSE_O1_Submit`（`1pXbO3Mp…`）。⚠️ `GSE_Gate1_submit`（G1・実施中）とは別物である。
★ 再デプロイは不要だった —— `config_()` が `PropertiesService.getScriptProperties()` を
`doPost` の実行時に読むため（新バージョンが要るのは `.gs` のコードを直したときだけ）。

→ ★ **§1-E（送信 timeout の実測）のブロックは外れた。**
