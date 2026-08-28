# 判断と根拠

## ✅ 研究者判断（2026-08-28・セッション内で聴取）

| # | 論点 | ✅ 決定 | 帰結 |
|---|---|---|---|
| **C-1** | O1 の提出先（受け口 / Drive / secret） | ★ **別に立てる（新プロジェクト C）** | 稼働中の G1 受け口に一切触らない。O1 名だけを通す `sanitizeName_` を最初から書ける |
| **C-2** | age 公開鍵 | ★ **G1 と共用**（現行 `resources/pubkey.txt`） | 追加ビルド・再署名・鍵管理が不要。⚠️ 復号できる範囲は G1 と同一 |
| **A/B** | 実機確認の実施 | ★ **今やる（A → B の順）** | 本セッションで A を実施した（下記） |

---

## 判断 A-1 — ★★★ `key` 行は実機で出た（前セッションの最大の積み残しが閉じた）

★ 実測条件: `GSE_O1_MODE=1` ＋ `GSE_DATASET=<スクラッチ>` で `src-tauri/target/debug/gse-next.exe` を起動し、
**研究者が実際にタイプした**（⚠️ アプリの「開始する」は押していない）。
出力: `<scratch>/raw/Pd5f83b5d8a13/gse_o1_20260827_171934.ndjson`

### 行種の内訳（実測）

```
2338  feat        184  key         19  focus_transition   12  ime_state
   5  ime_shadow    3  paste        2  starve_window       2  hook_health   1  meta
```

### チェックリストの結果

| 確認項目 | 結果 | 根拠（一次） |
|---|---|---|
| 「開始する」を押していないのに `key` 行が出る | ✅ **184 本** | NDJSON |
| ⚠️ `key` 行に**生 VK が 1 つも無い** | ✅ フィールド集合は `['category','press','t','type']` **1 種類のみ・184/184 本**。`vk` / `scan` / `char` / `modifiers` 等の検出 **0** | NDJSON |
| `category` に量子化されている | ✅ `alphabetic 118 / backspace 38 / space 14 / enter 10 / punctuation 2 / modifier 2` | NDJSON |
| `feat` の `keys` が 0 でなくなる | ✅ 最大 **70**、`keys > 0` の feat 行 **2124 / 2338** | NDJSON |
| トレイが「GSE — 計測中」 | ✅ `tray state (initial) -> Measuring (GSE — 計測中) o1_mode=Some(Env) paused=false` | `gse-app.log` |
| `meta` に `o1_mode` | ✅ `"o1_mode":"env"` | NDJSON 1 行目 |
| ⚠️ **`hook_health.starved_ms` が 0 のまま** | ⚠️ **成り立たなかった**（`starved_ms: 30000` が 2 行） | 下記 判断 A-2 |

★ **N-3 は解消した。** 前セッションで `key` 行が出なかったのは**注入入力**がフックに届かなかったためで、
**実キー入力は届く**。⚠️ 注入で検算する経路は今後も使えない。

---

## 判断 A-2 — ⚠️★★★ `starved_ms` は 0 にならない。**仕様どおりの誤検知**であり、O1 では常態になる

### 何が出たか（実測タイムライン・`session_start` からの相対秒）

```
t+ 214.9 〜 229.8s   key 132 行（打鍵の塊①）      ← ★ この間 hook_health は 1 行も出ていない
t+ 230  〜 2257s     打鍵なし（約 34 分）
t+2233  〜 2256s     focus_transition 11 行        ← ★ マウス / ウィンドウ操作だけがあった
t+2256.6s            hook_health {alive:true, starved_ms:30000, rehook:false, dropped:0}
t+2257.5s            paste                          ← ★ 1 秒後にフックは正常に発火している
t+2257.2 〜 2278.8s  key 52 行（打鍵の塊②③）
```

### ★ 原因は「フックが壊れた」ではない（一次資料で確定）

`input/liveness.rs` の doc に**既知の限界として明記されている**（逐語）:

> `GetLastInputInfo` は **マウスも含む**。したがって「2 分間ずっと読んで
> スクロールしていただけ」も **starvation として数えられる** (= 誤検知しうる)。

★ 裏づけ 2 点（grep で確認）:
1. `CALLBACK_COUNT` を増やすのは**キーボードフックだけ**（`hook_windows.rs:616` / `hook_macos.rs:333`）。
   ⚠️ O1 のポインタ観測は**別カウンタ** `POINTER_CALLBACK_COUNT`（`observe_macos.rs:147`）で、
   `liveness` は**それを読んでいない**。
2. `alive: true` ／ 30 秒後に `paste` と `key` が正常に流れている。

→ ★ **打鍵中は starvation が 30 秒に届いていない**（塊①の 15 秒間、`hook_health` は 0 行）。
   ⚠️ 立ったのは **34 分の無打鍵ののち、マウスだけで復帰した瞬間**である。

### ⚠️★★★ ここから導かれる、O1 固有の未解決問題（★ 新規発見・引き継ぎメモに無い）

`Thresholds::default()` は **30 秒 → `Suspect`（ログのみ）/ 120 秒 → `Down`** で、
⚠️ **O1 用の緩和が無い**（`lib.rs:3910` が `Thresholds::default()` をそのまま使う）。
`Down` になると `HOOK_STARVED = true` → `tray::measure_state` の第 2 引数が false になり、
トレイが逐語 **「⚠ GSE — 計測できていません（研究者に連絡してください）」** に変わり、
さらに `request_reinstall()` が走る（`lib.rs:4081-4088`）。

⚠️★★★ **これは O1 が観測対象として明示的に掲げている作業で常態になる。**
宣言 4 択の 1 つは逐語「**デザイン・映像・制作作業（図面・動画編集・3D など、文字をあまり打たない作業）**」であり、
★ **2 分以上キーを打たずにマウスだけ動かすのは、その作業では異常ではなく普通である。**

帰結（3 つ）:
1. ⚠️ 被験者が**繰り返し「計測できていません・研究者に連絡してください」を見る**（実際には正常に記録できている）
2. ⚠️ 同意文書 §4 の逐語「**印が出ていないときは記録していません**」の意味が濁る
3. ⚠️ 生きているフックに対して**再設置が走る**（★ エピソードごと 1 回に絞られてはいる）

### ✅★★★ 2026-08-28 追記 — **`Down` まで実測で到達した**（★ 予測ではない）

★ 研究者がアプリを閉じた際のログと NDJSON に、**120 秒到達から再設置までが丸ごと残っていた**。

`gse-app.log`（逐語）:

```
18:00:19.984 ERROR keyboard hook may be dead: the system saw input but the hook was not called
             (keystrokes may NOT be recorded) starved_ms=30000
18:01:55.009 ERROR keyboard hook is NOT delivering events; keystrokes are NOT being recorded
             for this block starved_ms=120000 rehook_requested=true
18:01:55.010 WARN  Keyboard hook reinstall requested by the liveness monitor
             (events stopped arriving). Re-installing in 2s...
18:01:55.089 ERROR tray: keyboard hook is down while a session is active;
             keystrokes are NOT being recorded          ← ★ トレイが HookDown に変わった
18:01:57.010 INFO  Keyboard hook installed                ← ⚠️ 生きているフックが再設置された
```

NDJSON（逐語）:

```
t+2444.7s  {"type":"hook_health","alive":true, "starved_ms":30000, "rehook":false,...}
t+2539.7s  {"type":"hook_health","alive":false,"starved_ms":120000,"rehook":true, ...}
```

⚠️★★★ **この区間、被験者は 1 文字も打っていないだけで、フックは正常だった。**
★ 直前 (t+2256s) には同じフックが `key` / `paste` を正常に記録している。
→ ★ **「マウスのみの作業 → 2 分で誤警告 ＋ 生存中のフックの再設置」が実機で成立することを確認した。**

★ 副産物として確認できたこと:
- ✅ `session_end` が書かれた（`{"type":"meta","session_end":1787853771818}`）—— D-1 の「閉じる」経路が実機で動く
- ✅ `pointer_bin` 行が 2 本出ている（O1 のポインタ channel が生きている）

→ ★ **研究者判断が要る**（起票済み。本タスクで勝手に閾値を変えない）。

---

## ★ 引き継ぎメモの検算結果（⚠️ 3 件が古い / 誤り）

| メモの記述 | 一次資料 | 判定 |
|---|---|---|
| ブランチに 11 コミット未 push・`origin/main` より 3 後ろ | `git rev-list --left-right --count origin/main...main` = `0 0` | ⚠️ 解消済み |
| gse-dataset にコミット 1 本未 push | `git -C C:/gse-dataset rev-list --count origin/main..main` = `0` | ⚠️ push 済み |
| CI 復旧済み・main 緑 | `gh run list --branch main` 最新 `33096214706` = **success** | ✅ 支持 |
| C-5 の対象は `scripts/make-participant-zip.sh` | 同スクリプトは**汎用 zip 化のみ**。マーカーを置くのは `experiments/20260801-controlled-friction-task/make-distribution.sh:149-150,179-180` / `make-common-app-zip.sh:91-92,132-133` | ⚠️ **指す先が違う** |

## ⚠️★★★ 受け口の障害（C-1 の前提を崩した）

`Form_G1/GSE_G1_Submit.gs:229` の `sanitizeName_` は
`/^[A-Za-z0-9]{1,16}_block\d{2,3}_gse_\d{8}_\d{6}(_\d{1,10})?\.age$/` しか通さない。
O1 の提出物名は `submission.rs:267` の `o1_age_file_name` が作る `<pid>_o1day<NN>_<stem>.age`
（stem = `gse_o1_<date>_<time>`・`o1.rs:263`）。

★ 実測（`node` で当該正規表現をそのまま評価）:

```
ACCEPT  P012_block03_gse_20260807_101112.age
REJECT  P012_o1day01_gse_o1_20260828_143000.age
REJECT  P012_o1day01_gse_o1_20260828_143000_2.age
```

→ ⚠️ `bad name` が返り、収束器は「未送信」のまま失敗を繰り返す
（`.gs` 自身が「**永久に届かない**」と警告している型）。
→ ★ 研究者判断 C-1 =「別に立てる」により、新 `.gs` で O1 名だけを通す形にする。

---

## 判断 B-1 — ★ UI のクリック通し（★ 研究者が実機で操作・2026-08-28 10:21 JST）

⚠️ 時刻は `gse-app.log` が **UTC** で書く（`01:21Z` = JST 10:21）。★ 混ぜない（引き継ぎ §4-2）。

### ✅ 宣言 4 択 → ローテート

`gse-app.log`（逐語）:
```
01:21:03.423 INFO O1: rotating session log (declaration -> vibe_coding) -> ...gse_o1_20260828_012103.ndjson
01:21:03.423 INFO O1: task_kind declared: vibe_coding
01:21:03.423 INFO SessionLogger: rotated to ...gse_o1_20260828_012103.ndjson
```

NDJSON で検算:

| ファイル | `session_meta` | 判定 |
|---|---|---|
| `gse_o1_20260827_180839.ndjson`（旧・25981 行） | ⚠️ **0 本** | ✅ **未宣言のまま残った**（期待どおり） |
| `gse_o1_20260828_012103.ndjson`（新・61 行） | ✅ 1 本 | `{"track":"main","task_kind":"vibe_coding","intervention_enabled":false,"condition":null,"label_pool":null,"head_id":"coding_v0"}` |

★ 境界が正確: 旧の `session_end` = **1787880063423** = 新の `session_start`（**同一値**）。★ 隙間も重複も無い。
★ `intervention_enabled: false` = B-4（O1 で介入 OFF）も同時に確認できた。

### ✅ 「すぐ止める」 → 実体を伴う停止

```
{"type":"recording_pause","t":1787880073020,"paused":true}
{"type":"recording_pause","t":1787880080203,"paused":false}
```
`gse-app.log`: `01:21:13 tray state -> Stopped` → `01:21:20 tray state -> Measuring`

★ **停止区間 7.2 秒のあいだ、`feat` 行は 0 本**（前 9 本 / 後 45 本、`feat` 間隔の最大は 7991 ms ＝ 停止長）。
→ ⚠️ **「記録を止めています」は表示だけではなく、実際に記録が止まっている。**

### ✅ 開始前ゲート（「確認しました」）— ★ **両方向を実測した**

| 方向 | 実測 |
|---|---|
| **押す前** | ⚠️ `~/.gse/o1_consent_ack` 不在。★ 約 7 時間・**2 回の起動**を通して `O1 auto-submit` 行が **1 本も出ない** |
| **押した直後** | `01:21:58 INFO O1: enrollment acknowledged (participant id registered)` → `~/.gse/o1_participant_id` (`P009`) と `o1_consent_ack` (`{"acknowledged_at":1787880118104}`) が生成 |
| **押した後の起動** | ✅ `O1 auto-submit (at startup): {"packaged":0,"sent":0,"unsent":0,"upload_disabled":true,...}` が**出た** |

★ 根拠（一次）: `lib.rs:1918 auto_submit_enabled()` は O1 で `submission::o1_consent_acknowledged()` を返し、
`spawn_reconcile_with_guard`（`lib.rs:1939`）が false なら**即 return** する。

★ 副産物 2 件:
- `packaged: 0` ＝ 閉じた 3 セッションが**まだ 48 時間の猶予内**である（★ 猶予機構が効いていることの実測）
- `upload_disabled: true` ＝ 送信先未設定なので**端末から何も出ていない**

⚠️ **後始末が要る**: 登録された ID は **`P009`** で、これは **G1 が消費済みの P-ID**
（`.steering/20260808-g1-drive-and-gas-redeploy/` §5「消費した P-ID: P009」）。
★ 本番の O1 では別採番にすること。★ 本セッションの検証用なので `~/.gse/o1_*` は検証後に消す。

### ❌ 「この時間帯の記録を消す」 — **未実施**

⚠️ ログにも NDJSON にも削除の形跡が無く、3 ファイルとも残っている。★ **未確認と記録する。**

## 判断 B-2 — ⚠️ starved 誤検知は **別タスクに起票する**（研究者判断 2026-08-28）

★ 本タスクでは閾値も `liveness` の意味論も変えない。⚠️ **被験者を走らせる前に必ず解消すること**を起票に書く。

---

## 判断 C-1 実装 — ★ O1 専用の受け口 `Form_G1/GSE_O1_Submit.gs` を新規に作った

★ 研究者判断「別に立てる（新プロジェクト C）」に沿って、**G1 の `.gs` を 1 バイトも変えずに**新設した。

### ★ G1 の受け口から意図的に変えた 2 点（⚠️ それ以外は同一）

| # | 変更 | 根拠 |
|---|---|---|
| **V-1** | `sanitizeName_` が **O1 の名前しか通さない**（⚠️ **G1 の `_block<NN>_` 形は落とす**） | ★ 「2 研究を混ぜない」の**実装上の担保**。配布物を取り違えても受け口が構造的に受け取らない |
| **V-2** | `MAX_BYTES` を **8 MB → 48 MB** | ★ 下記の実測 |

### ⚠️★★★ `MAX_BYTES` は実測で決めた（★ G1 の 8 MB では毎日弾かれる）

★ 実測手順（2026-08-28・本機）:
1. `GSE_O1_MODE=1` で実走 → `gse_o1_20260827_180839.ndjson` = **6,388,517 B / 7.21 時間**
2. `gse-package --input <上記> --recipient src-tauri/resources/pubkey.txt --participant P900`
   → `.age` = **5,730,783 B**

| 何 | 値 |
|---|---|
| `.age` 実測 | 5,730,783 B / 7.21 時間 |
| **24 時間換算** | **約 18 MB** |
| G1 の上限 | 8 MB → ⚠️ **毎日 `too large` で永久に届かない** |
| 採用した上限 | **48 MB** |

⚠️★★ **この実測区間は打鍵 0 本のほぼ無操作である。★ すなわちこれは下限である。**
⚠️★★★ **未実測**: GAS が受け取れる本文の実際の上限。★ `GSE_G1_Submit.gs` は逐語
「実測では 50 MB でも通った（上限未到達）」と書くが、**base64 本文かデコード後かはその記録から決まらない**。
→ ★ **配備時に 1 日ぶんの実サイズで通し確認する**（`.gs` の配備手順 8 に書いた）。

### ★ 検査 — `Form_G1/o1_submit_guard_test.cjs`（41 ケース・`run.sh §4` に接続済み）

⚠️ **緑であることは根拠にしていない。** ★ 各ガードを 1 つずつ壊して**赤になることを実測した**
（`verify-before-claiming` ルール 5b）:

| 変異 | 結果 |
|---|---|
| 名前ガードを無効化（常に通す） | ✅ 赤（16 件） |
| 名前ガードを G1 形に差し替え | ✅ 赤（15 件） |
| `MAX_BYTES` を G1 の 8 MB に戻す | ✅ 赤（1 件） |
| シークレット照合を常に `true` | ✅ 赤 |
| 0 バイト検査を外す | ✅ 赤 |
| 重複を握り潰す | ✅ 赤 |
| 設定不足の検査を外す | ✅ 赤 |
| `bad json` を `server error` に丸める | ✅ 赤 |
| `bad base64` を `server error` に丸める | ✅ 赤 |
| GET で情報を返す | ✅ 赤 |
| `.gs` にシークレット直書き | ✅ 赤 |

→ ★ **11 / 11。空回りしているガードは無い。**

★ さらに「検査自体の空回り」も潰した:
- ケース数の**下限 30** を置き、5 件に削ると `exit 1` になることを実測
- 末尾行の書式を `submit_guard_test.cjs` と同一にし、`run.sh` の `guard_count()` が
  **41 と読める**ことを実測（⚠️ 書式がずれると「件数不明」に落ちるが**赤にはならない**）

⚠️ **`.gs` はまだ配備していない**（★ Apps Script への貼り付け・スクリプトプロパティ・
デプロイは**研究者が手で行う**。関数セレクタは自動操作を受け付けないことが実測済み）。

---

## 判断 C-7 (R-14) — ★ 削除台帳を作った（`docs/o1-deletion-ledger.md`）

⚠️★★★ **これが欠けると ADR-014 判断 O1-2（48 時間の猶予後に自動提出する）が成立しない。**
★ 同意文書ドラフト §4-3 は既に被験者へ逐語で約束している——
「⚠️ **送られたあと** → 研究者側で削除し、**削除したことを記録に残します**」。

### ★ 台帳が網羅すべきコピーの所在を**一次資料で数え上げた**（16 か所）

⚠️ 「送信済みを消す」は Drive の `.age` を消せば済む話**ではない**。実際には
研究者側 8 か所（Drive / ゴミ箱 / 受領 `.age` / 復号平文 / gse-dataset metrics / 派生 CSV /
`analysis.db` / `experiments/` の hash）と被験者端末 6 か所（平文 / temp 退避 /
⚠️ **クラウド同期の複製** / `.age` / `.sent` と `manifest.jsonl` / 診断ログ）に散る。
→ ★ **チェックリストにして §3 に置いた。** ⚠️ 記憶で場所を思い出さない。

### ⚠️★★★ 実測で見つかった穴 — O1 を gse-dataset に出すと削除が git 履歴の書き換えになる

| 実測（2026-08-28） | 結果 |
|---|---|
| `scripts/sync-session.sh` / `.ps1` に O1 を弾く記述はあるか | ⚠️ **`o1` の出現 0 件**＝弾いていない |
| gse-dataset の `.gitignore` は `metrics/` を除外するか | ⚠️ **していない**（除外は `raw/**/*.ndjson` 等の NDJSON だけ） |
| `metrics/` は実際に追跡・push されているか | ⚠️ **されている**（`git ls-files metrics/` = **34 件**） |

→ ⚠️ O1 を `sync-session.sh` に通すと private repo に commit＋push され、
★ 削除が **force push を伴う履歴書き換え**になり、他の clone には残り続ける。
→ ★ 台帳 §4 に運用規則として書き、**ガードの追加を起票**した（本タスクでは未実施）。

### ⚠️ 未確定として明示したもの — **保管上限**

ADR-014 D8 制約 3 は「削除要求経路と**保管上限**を台帳に載せる」と要求するが、
★ ADR-012 D12-b が数値を決めているのは**録画について**であり、
⚠️ **O1 の打鍵データの保管上限は repo のどこにも無い**（2026-08-28 に確認）。
→ ★ 台帳 §5 に `⚠️ 未確定` と書き、**下記ゲートが赤になるようにした**（記憶に頼らせない）。

## 判断 C-6 — ★ 同意文書の連絡先を埋めた

⚠️★ **引き継ぎメモの枠組みが実態と違った。** ★ G1 は `consent.md` を**埋めていない**
（L133-134 は今も「（実施前に記入）」）。同意の**正本は Google フォーム**であり、
連絡先は `GSE_G1_Form_Builder.gs:107 CONTACT_EMAIL` / `:1748 G1_CONTACT` に入っている。
→ ★ すなわち `.md` は**配布されない雛形**である。

★ 研究者から聴取（2026-08-28）: **三浦尊統 / ZEN大学 / mmiura.network@gmail.com**。
→ `consent-draft-o1.md` §7 を埋め、dev メモの未了 1 / 10 を解消に更新した。
⚠️ **フォーム側（C-4）にも同じ値を `O1_CONTACT` として置くこと**（★ そちらが正本）。

## 判断 C-8 — ★ 配布前ゲート `scripts/check-o1-release-readiness.sh` を作った

⚠️★★★ **このゲートは今は赤いのが正しい。** ★ 役目は「何が残っているか」を
**人の記憶ではなく機械に持たせる**ことである。
★ 動機: 2026-08-27 に dev が README の古い記述だけを見て「未作成」と誤報した
（どちらも済んでいた）。→ ⚠️ **文書は実体ではない。実体を毎回見に行くものを置く。**

★ 現在の結果（実測）: **通過 7 / 未達 5**

```
✅ 同意文書に未記入の欄が無い / 連絡先 / 所属
✅ 削除台帳がある
✅ 受け口がある / .gs に秘密が直書きされていない / ガード検査が緑 (41 ケース)
❌ 削除台帳の保管上限が未確定
❌ O1 のフォーム類が無い
❌ 配布スクリプトが o1.mode を置かない
❌ sync-session.sh に O1 を弾くガードが無い
❌ O1 で liveness の閾値が G1 と同じ（マウスのみ 2 分で誤警告）
```

### ★ ゲート自身も 3 状態で試した（ルール 5b）

⚠️ 「7 件が緑」を根拠にしていない。★ fixture を作り、**✅ を 1 つずつ壊して赤になるか**を測った:

| 変異 | 結果 |
|---|---|
| 同意文書に空欄を戻す / 連絡先を消す / 所属を消す | ✅ 赤 |
| 削除台帳を消す / 受け口を消す / ガード検査ファイルを消す | ✅ 赤 |
| `.gs` に秘密を直書き / 受け口の名前ガードを壊す | ✅ 赤 |

→ ★ **8 / 8 で赤。** 逆向きの陽性対照も 4/4 で緑に変わることを確認
（保管上限を埋める / `sync-session.sh` に `gse_o1_` / フォームビルダーを置く / `o1.mode` を置く）。

⚠️★ **弱いチェックを 1 つ見つけて締めた**: 当初 `grep -qE 'gse_o1_|o1' sync-session.sh` は
**コメントに `o1` と書くだけで緑**になった。→ `gse_o1_` に絞り、
★ **「弾くことまでは測っていない」という限界をスクリプト内に明記**した。

---

## 判断 R-1 — ★ 並列レビュー (code-reviewer ＋ security-checker) の指摘を反映した

⚠️ **両者が HIGH で一致した 1 件目は、私が入れた「約束と実装のずれ」だった。**

### ★ 直したもの

| # | 指摘 | 出所 | 直し方 |
|---|---|---|---|
| **F-1** | ⚠️★★★ **`--selftest` が使い方に書いてあるのに実装が無い**（引数を 1 つもパースせず、打ち間違いも黙って通常実行になる） | 両者 HIGH | ★ **実装した**（fixture を作り 18 ケースを実行）。知らない引数は `exit 2` |
| **F-2** | ⚠️ ゲートのアンカー喪失が**緑**になる（`Thresholds::default()` が改名・移動しただけで「別扱いになっている」に落ちる） | code-reviewer HIGH | ★ アンカーが無い場合を **`ng`** にした（3 分岐） |
| **F-3** | ⚠️ ゲートが `sync-session.ps1` を見ていない（★ Windows が主ターゲット。`.sh` だけ直すと緑になる） | code-reviewer HIGH | ★ **両方**を要求。selftest 3 で「片方だけでは緑にしない」を固定 |
| **F-4** | ⚠️ 保管上限の判定が散文の grep（表記を変えるだけで未設定のまま緑） | security-checker MEDIUM | ★ **機械可読マーカ** `<!-- o1-retention: unset -->` にし、⚠️ **マーカ喪失も赤**にした |
| **F-5** | ⚠️★★ **`MAX_BYTES=48MB` に送信側が届かない** —— `reconcile.rs` の timeout は **180 秒固定**、実測 207 KB/s。48MB(base64 64MB) ≒ **310 秒**。⚠️ 実測の 1 日ぶん 18MB でも ≒ **116 秒**＝ timeout の 2/3 で、**しかも Drive 保存時間を含まない** | code-reviewer HIGH | ★ `.gs` に**表で明記**し、⚠️ **ゲートの検査項目に足した**（180 秒固定のあいだ赤） |
| **F-6** | ⚠️ 同意文書の状態表が本文より古い（★ 本ゲートを作った動機＝古い記述による誤報が、**同じ文書の中で再発**していた） | 両者 MEDIUM | ★ 実体に合わせ、⚠️ **ゲートに「`⚠️ **未了` が残っていたら赤」を追加**した |
| **F-7** | ⚠️ 削除台帳に保存先の抜け（GAS 実行ログ / 削除要求メール ＋ P-ID↔個人の対応表 / 研究者端末のバックアップ・版履歴 / **最後の回収経路**） | 両者 MEDIUM | ★ **A-9〜A-12 と B-7 を追加**（★ 回収経路は `submission.rs:47` 逐語「常に生きている」） |
| **F-8** | ⚠️ 台帳 §6 の「実施者」が実名（★ 研究チーム構成員の PII を git 履歴に永久化する） | security-checker LOW | ★ **イニシャル/役割**に変更。§7 に「公開前に §6 を確認」を追加 |
| **F-9** | ⚠️★★ **O1 の名前規約に Rust 側の対テストが無い**（G1 には `generated_names_fit_the_endpoint_name_rule` がある。cjs 側は手書きリテラルなので、`o1_age_file_name` を変えても両方緑のまま通る） | code-reviewer MEDIUM | ★ `generated_o1_names_fit_the_o1_endpoint_name_rule` を追加。⚠️ G1 の照合器を**テストモジュール直下に切り出して共有**し、**両方向の分離**を固定した |
| **F-10** | ⚠️ 「上限を超える大きさ」が `ok===false` しか見ていない（名前ガードが壊れても同じ結果で緑） | code-reviewer MEDIUM | ★ `error==='too large'` と**保存されていないこと**まで固定。`decodedLength_` の padding 0/1/2 の境界も追加 |
| **F-11** | ⚠️ **O1 の未達で実施中の G1 のゲートが赤くなる**（`run.sh` は「G1 の技術的準備だけを見る」と宣言している） | code-reviewer MEDIUM | ★ `run.sh` では **`note` に落とし、G1 の合否に影響させない**。判定は O1 のゲートが持つ |

### ★ 検証（⚠️ すべて実行した。予測していない）

| 何 | 結果 |
|---|---|
| `node Form_G1/o1_submit_guard_test.cjs` | ✅ **全 44 ケース**（41 → 44） |
| `node Form_G1/submit_guard_test.cjs`（G1 非回帰） | ✅ 全 33 ケース |
| `bash scripts/check-o1-release-readiness.sh --selftest` | ✅ **18 / 18**（壊すと赤 11・満たすと緑 6・片方だけでは緑にしない 1） |
| 打ち間違い `--selftst` | ✅ `exit 2`（★ 黙って通常実行しない） |
| `cargo test --features package --lib` | ✅ **557 passed / 0 failed**（★ +1 = 新テスト） |
| ★ **新テストの変異**（`o1day`→`o1d` / `{day:02}`→`{day}`） | ✅ **どちらも FAILED**（空回りしていない） |
| ゴールデン byte-equal | ✅ `OK: 15 snapshots match` |
| schema drift | ✅ byte-equal |
| clippy（`submission.rs`）/ fmt | ✅ 指摘 0 / 差分なし |
| ゲート本体 | 通過 8 / 未達 6（★ **赤いのが正しい**） |

### ⚠️ 直さずに残したもの（★ 記録する）

| # | 指摘 | なぜ今直さないか |
|---|---|---|
| **S-1** | ⚠️★★ 受け口が**認証前に本文全体を `JSON.parse`** する／レート制限・投稿数上限が無い（★ 秘密不要の DoS ／ 秘密ありなら `_dup-` 無限増殖で Drive 枯渇） | ⚠️ **研究者判断が要る**（受け入れ本数の上限は被験者数×日数で自明だが、値は研究者が決める）。★ 起票する |
| **S-2** | ⚠️ 中身が age 暗号文か検証していない（★ 先頭 21 バイト `age-encryption.org/v1` で確定できる） | ★ 安価で有効。⚠️ ただし**受け口の意味論を変える**ので、S-1 とまとめて 1 回で入れる |
| **S-3** | ⚠️ 共有シークレットが全被験者共通・平文配布・非ローテーション（★ `HMAC(master, pid)` 派生にすれば失効と帰属が立つ） | ⚠️ **G1 と共通の設計**であり、O1 だけ変えると運用が二重になる。★ 研究者判断 |
| **S-4** | ⚠️ 端末が送る名前の集合のほうが受け口より広い（★ `is_o1_session_file_name` は `gse_o1_` 前方一致＋`.ndjson` だけで、クラウド同期の競合コピー `…-PCNAME.ndjson` が `.age` 名に載りうる） | ⚠️ **`src-tauri/` の変更**であり、本タスクは計器を触らない約束。★ 起票する（**実害は「その日は永久に届かない」**なので優先度は高い） |
| **S-5** | ⚠️ ゲートが配布経路（`make-distribution.sh` 等）から呼ばれていない | ★ C-5 で配布側を触るときに同時に入れる |
