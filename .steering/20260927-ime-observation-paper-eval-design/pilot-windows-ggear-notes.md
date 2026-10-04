# Windows 較正パイロットの最初の試し（2026-10-03 未明・G-GEAR・内部記録）

> ★ **2026-10-04 追記（判断 144）**: これは **M5 の記録ではない**。M5 は Surface Pro 8（計測する機械）で行った（判断 136・`pilot-windows-1-notes.md`）。G-GEAR のこの試しは、Surface の M5 より前に別の版の MS-IME（`IMJPTIP.DLL` 10.0.26100.9278・26H2 / 26300）で回したもの。S4（変換の後の Esc 2 回で取り消されない）と S8（数字の後に Enter が要る）は Surface でも同じに出た（判断 137）。元は枝 `docs/ime-m5-pilot-ggear`（`433d13ff`・main に入れていない）の `pilot-windows-1-notes.md`。下の「判断 133〜135」「この後」は当時の記述のまま（判断 135 の番号は main の判断 135 と別物）。

> 公開物の `experiment/pilot-windows.md` は、正解の経路と定義が決まってから英語で書く（M5 の Done・M6 の根拠）。これは内部の生の記録。
> ⚠️ 観測側の ImeShadow は**読まない**（`seal_obs.py` で封印してから、キーの行だけで集計する）。⚠️ `run.json` の `outputs.obs.lines` も見ない（キーの行の数を引くと ImeShadow の行の数が出る）。
> 場所: 判断 134（数時間以上の run だけ別の Windows 実機・それ以外は G-GEAR）。実行は研究者の離席中に自動（研究者の選択・2026-10-03）。

## 条件

- 機械: G-GEAR（デスクトップ・AC 電源・バッテリーなし）・Windows 11 `26H2`・build `26300`・JIS キーボード（`kbd106.dll`・`PCAT_106KEY`）。
- IME: Microsoft IME（日本語）だけ（`{03B5835F-F03C-411B-9CE2-AA23E1171E36}`）・`IMJPTIP.DLL` 10.0.26100.9278。Google 日本語入力は無し。設定は既定のまま（`romastyle` MS-IME・予測入力は既定・`UseCloudSuggestion` 0）。
- IME の学習は**リセットしない**（判断 133 の研究者の答え）。
- 電源: AC のスリープ・画面オフ・休止はもともと 0（なし）。スクリーンセーバーは未設定（`ScreenSaveTimeOut`・`SCRNSAVE.EXE` が空）→ **変更なし**（戻す作業も無い）。
- 道具: Python 3.11.9・cargo / rustc 1.98.1・git 2.53.0・gh 2.90.0。
- 書き出し: タグ `ime-observation-prereg-macos`（`ff122e32`）のクリーンな worktree `C:/wt/ime-m5-tag` から `export.internal.py --allow-missing-license` → `C:/ime-pilot-win/export`。★ **一覧は `freeze-export-list-macos.txt` とバイト一致・98 ファイル・SHA-256 `29b183ba…6c49`**（3 台目の機械でも一致・判断 68）。
- ビルド（書き出した側）: `kit/logger` release 13.7 秒・`kit/refinput-windows` release（`--bins`）11.5 秒。`bash kit/check.sh` 27 本緑・`refinput_imm` / `refinput_tsf` の `--selftest` と `validate_logs.py --kind gt` 緑・ロガーの `--selftest` と `--kind obs` 緑。
- 計画: `plan_config.macos.json` を写して n = 3・`block_size` 21 にした仮の設定（`C:/ime-pilot-win/plan_config.pilot.json`・`config_sha256` `9dae1700…`）・`recipes.json`（`os.windows`）・コーパス `c8f890cb…`・`--os windows`・seed 1 → **117 試行・6 ブロック**（S9 は既定で無効・S11 は Windows の手順に無い）・見積もり 1,597 秒（27 分）・`plan-pilot-s1.jsonl` の SHA-256 `850cc7e1…`。短い試しは同じ計画のブロック 0 の先頭 6 試行（S2・S3・S15・S5・S13・S14）。
- セルのファイル（作業ディレクトリ・コミットしない）: `cell-pilot-imm.json` / `cell-pilot-tsf.json`。`focus_cmd` は `focus_ime_on.py`（題名で窓を 1 つ探す → `SetForegroundWindow` → 前面を最大 5 回読み戻す → `VK_IME_ON` を押して離す）。S15 の移り先は `away_window.ps1`（入力欄の無い WinForms の窓・題名 `ime-pilot-away`）。

## 準備中の所見

1. **セルのファイルの相対パスは `./` が要る（Windows）**: `kit/logger/...` の形（Mac の `cell.example.json` と同じ形）は `subprocess.Popen` が `FileNotFoundError`（`[WinError 2]`）で起動できない。`./kit/...` か `\` 区切りなら起動する（実測）。→ セルのファイル側で直した（凍結のコードには触れない）。M6 で Windows のセルの例を足すなら `./` の形で書く。
2. Claude Code の裏のシェルから、作ったばかりの参照入力欄の窓を `SetForegroundWindow` で前面に出せた（`focus_ime_on.py --no-key`・キーは送っていない）。
3. dryrun（キーを送らない・`--i-understand-this-sends-keys` なし）: 子 2 つが起動して止まる（`forced`・Windows の `taskkill /T /F`）・`gt` は `validate_logs.py --kind gt`・oracle は `emit.py --validate` を通る。
4. `emit.py --selftest --full`（CI の job が無い時に・Claude Code の裏のシェルから）: 送出の遅れの 95 パーセンタイル **0.03 ms**（基準 20 ms 未満）・両方の時計が 1 ms 以下。

## 短い試し（ブロック 0 の先頭 6 試行: S2・S3・S15・S5・S13・S14・mid の速さ）

| run | 経路 | 結果 |
|---|---|---|
| `short-imm-1` | IMM | ⚠️ **2 試行目（S3）の途中で中断**（`the foreground window changed; o is not sent`・02:57:12）。研究者が画面を見ていて、送出中にスクリーンショット（Win+Shift+S）を取った。送った小文字 `…reikanim` に対し IME の表示に大文字が出ていた（Shift が重なった形）・Win+A で前面が変わったと見る（確証なし）。送出側は設計どおりそこで止まり、他の窓にキーは入っていない。1 試行目（S2）は完走（IMM のメッセージが届く・到達 33 / 33・時計の差 1〜2 ms）。**記録として残す**（消さない） |
| `short-imm-2` | IMM | 完走（6 / 6）。到達 161 / 163（欠けは S14 の `ime_off` / `ime_on` の 2 押下だけ＝**観測しない設計のキー**・Mac と同じ）。gt − oracle 4 ms・obs − oracle 2 ms |
| `short-tsf-1` | TSF | 完走（6 / 6）。到達は同じ（161 / 163・欠けは S14 の IME キー）。gt − oracle 2 ms・obs − oracle 1 ms |

- ⚠️ **`refinput_imm` の窓には文字が出ない**（研究者の指摘・設計どおり）: テキスト欄を持たない窓で、メッセージを `DefWindowProcW` に渡すだけ → 変換中の文字は Windows の既定の IME 表示（画面の左上に浮く小窓）に出る。`refinput_tsf` はリッチエディットなので窓の中に出る。→ `pilot-windows.md` に書く（読者が実機で試すときに迷う）。
- ★ **確定と取消は 2 経路で一致**（長さだけで比べた・ImeShadow は見ていない）: 6 試行とも組み立ての開始と終了が 1 回ずつ（持ち越しなし）。確定の長さ IMM（`comp` の `result_len`）／TSF（`tsf_end` の `result_len`）= S2 15 / 15・S3 20 / 20・S15 8 / 8・S13 15 / 15・S14 11 / 11、S5（Esc 1 回）は IMM で結果なし・TSF で `result_len` 0（取消）。
- ★ **MS-IME の挙動（Mac と違う）**: S14（変換中に IME をオフ → オン）は**オフの時点で確定する**（長さ 11）。手順書の `intent.commit` は `none`。S15（変換中に前面の窓を離れる）は**離れた時点で確定する**（TSF では `tsf_end` → `focus_out` → `focus_in` の順・戻った後の Enter は空の欄に入る）。→ 正解の定義（M6）でこの 2 つを確定として扱うか。
- IMM の呼び出し列: `start_comp` → `notify[15]+` → `comp` → `notify[269]` → `notify[5]`（IMN_OPENCANDIDATE）→ 打鍵ごとに `notify[15]+ → comp → notify[3]`（IMN_CHANGECANDIDATE）… → `notify[4]`（IMN_CLOSECANDIDATE）→ `comp`（結果）→ `end_comp` → `notify[270]`。⚠️ **予測入力の候補窓が IMM では候補窓（OPEN / CHANGE / CLOSECANDIDATE）として届く**（打鍵の最初から開く）。15・269・270 は文書に無い値（IMN_PRIVATE は 14）。→ Windows の定義の「候補窓」を何で取るか（M6）。
- TSF の呼び出し列: `tsf_start → tsf_update → ui_begin[candidate] → ui_end[candidate] → tsf_update+ →（S2 は変換の候補窓でもう一度 ui_begin / ui_end）→ tsf_end`。

## 本体（117 試行・seed 1）

| run | 経路 | 結果 |
|---|---|---|
| `pilot-imm-1` | IMM | ⚠️ **開始の前面化で中断**（`SetForegroundWindow returned 0`・03:04:13）。キーは 1 つも送っていない（oracle は頭の行だけ・`focus` は空）。`run_cell.py` は `with Emitter(...)` で backend を開く時に最初の前面化をする（1 つ目の `focus_cmd` より前）。前面ロックの待ち時間は 2,147,483,647 ms（実質無期限）なので「待ち時間切れ」では説明できない。研究者の入力の直後（VS Code が前面＝起動の連鎖に権限がある）に始めた短い試し 3 本は通った → **研究者の返事の直後に始める**。M7（研究者が端末で起動する）では起きにくいが、手順に書く |
| `pilot-tsf-1` | TSF | 完走（117 / 117・26.3 分・03:04:33〜03:30:56）。6 ブロックすべてで前面の確認が取れた。到達 3,718 / 3,736（欠けは S14 の 9 試行の IME キー 2 押下ずつだけ・設計どおり）。gt − oracle 中央値 2.5 ms（壁）/ 2.8 ms（単調）・obs − oracle 0 ms・ドリフト 2 ms / 時以下。割り当てられない呼び出し 3（`focus_in`・`ui_begin`・`ui_end`） |

### `pilot-tsf-1` の所見（長さだけ・ImeShadow は見ていない）

| シナリオ | 結果（開始 s・終了 e・確定 C / 取消 x・候補窓の開始の数）|
|---|---|
| S1 | 8 試行は s1 e1 C・1 試行は前からの持ち越し（s0） |
| S2 | 9 / 9 が s1 e1 C（候補窓 2〜3 回） |
| S3 | 7 は s1 e1 C・2 は持ち越しの終わり（x）の後に C |
| ⚠️ **S4** | **8 / 9 で終了なし**（Space → think → Esc → Esc で取り消されない）。次の試行の打鍵が続けて足され、次の Enter でまとめて確定（例 t00011 → t00012 S7 の Enter で 31）。think 0.2〜19 秒によらない（0.2 秒・3 秒・11 秒・17.7 秒とも失敗、19.2 秒の 1 件だけ取消）→ IME の遅れではなく、**この MS-IME では変換の後の Esc 2 回では取消まで届かない**と見る（何回要るかは未確認） |
| S5 | 取消（Esc 1 回）。持ち越しを受けた 3 試行は、持ち越しごと取消 |
| S6 | 取消（Backspace を読みの長さだけ） |
| S7 | C（持ち越しの影響 3 件） |
| ⚠️ **S8** | **7 / 9 で終了なし**（Space 2 回 → think → 数字で候補を選んでも確定しない）。次の試行の最初の打鍵で確定し、TSF では「確定の直後に新しい組み立て」として `tsf_end`（`result_len` なし）→ `tsf_start` が同じ時刻に出る（README のとおり・下流は取消と数える）→ **Windows も数字の後に Enter が要る** |
| S10・S12〜S15 | C（S14 は IME オフで確定・S15 は前面を離れた時点で確定） |

### 直せる範囲（事前登録 §8）

- **S8**: `_PROFILES["windows"]["after_digit"]` を `["enter"]` に・`recipes.json` の `os.windows` の S8 に Enter を足す → **§8 の範囲内**（追補で変えてよい）。
- ⚠️★ **S4**: 生成器の検査が **OS によらず** `downs == full + ["space", "esc", "esc"]`（`generate_plan.py` の `_scenario_checks`・`_PROFILES` の外）→ Windows だけ Esc の回数を変えるのは **§8 の範囲の外**（コードの変更）。→ 研究者の判断: (a) 検査を profile から読む形に直す逸脱（`deviations.md`・macOS の計画のバイトは変わらない）／ (b) Windows では S4 を手順書の `os.windows` で無効にする（§8 の範囲内・シナリオが 1 つ減る）／ (c) その他。⚠️ 先に、何回の Esc で取り消されるかを短い試しで確かめる。

## この後（判断 135）

- 研究者の選択で、M5 の残りの run（S4 / S8 の確認・本体の走らせ直し）は**別の Windows 実機**（M7 を行う機械）で行う。確認の run の計画（`plan-probe-s4s8.jsonl`: S4 は Esc を 0.8 秒おきに計 4 回・S8 は数字の 0.8 秒後に Enter）は G-GEAR で作って dryrun で `run_cell.py` が受け付けることを確かめたが、**キーは送っていない**。
- 道具は `pilot-windows-tools/` に写した（`make_plans.py` は G-GEAR の短い試しと確認の計画をバイト一致で作り直す）。
- G-GEAR の生ログ（`C:/ime-pilot-win/runs/`: `dry-imm-1`・`dry-imm-2`・`short-imm-1`・`short-imm-2`・`short-tsf-1`・`pilot-imm-1`・`pilot-tsf-1`・`dry-probe-1`〔obs は読まずに消した〕）は G-GEAR に置いたまま。封印の `seal.json` も各 run の `sealed/` にある。
