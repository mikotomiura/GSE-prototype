# M5 Windows 較正パイロット 1 回目の記録（2026-10-03・Surface Pro 8・内部記録）

> 公開物の `experiment/pilot-windows.md` は、正解の定義（M6）が決まってから英語で書く。これは内部の生の記録。
> ⚠️ 観測側の ImeShadow は**読んでいない**（`seal_obs.py` で封印してから、キーの行だけで集計した）。参照のログ（gt）のキーコードは転記していない（IME が処理したかどうか〔229 か否か〕だけを数えた）。
> ⚠️ 1 件の逸脱: 短い試し（IMM）の実行中に、進み具合を見るため `obs.jsonl` の**行数**を 1 回表示した（`wc -l`・実行の途中の値）。中身は読んでいない。封印の規則（元の行数を出さない）の趣旨に反するので、以後は obs の行数を数えていない。

## 条件

- 機械: **Surface Pro 8**（`TABLET-J870RJQA`・i5-1135G7・8 GB）・Windows 11 Home 25H2 build 26200.8875・JIS（PCAT_106KEY）・MS-IME（`IMJPTIP.DLL` 10.0.26100.8875）・ローマ字入力・予測入力は既定のまま・IME の学習はリセットしていない（判断 133）。AC 電源。→ この機械が M7 の計測の機械（判断 134〜136）。
- 道具: Python 3.11.9・rustc 1.98.1・MSVC 14.44（判断 136）。
- 書き出し: タグ `ime-observation-prereg-macos` のクリーンな worktree から `export.internal.py --allow-missing-license` → **98 ファイル・一覧の SHA-256 `29b183ba…6c49`**。一覧は `freeze-export-list-macos.txt` のコミット済みの blob とバイト一致（作業コピーとは差が出る —— この機械は `core.autocrlf=true` で作業コピーが CRLF になる。比べる相手は blob）。→ **3 台目の機械でも一致**。
- ビルドと selftest（書き出した側）: ロガーと `refinput-windows` を `cargo build --release --locked`・`bash kit/check.sh` 27 本緑・`--compile` 28 ファイル・`cargo test`（logger 121 ほか・refinput 9 ＋ 17）緑・`refinput_imm.exe` / `refinput_tsf.exe --selftest` を `validate_logs.py --kind gt` に通して exit 0・`emit.py --selftest --full` 49 件緑（送出の遅れの p95 0.06 ms）。
- 計画（コミットしない・`~/ime-pilot/`）: `plan_config.macos.json` を写して n = 3 にした仮の config（速さ 480 / 240 / 120 ms・think 0.2〜20 s・マーカー ← → ← →・`nav_count_max` 3 は凍結の値）。`--os windows` で S11 は既定で無効 → 13 シナリオ。短い試し `plan-short`（n = 1・39 試行・3 ブロック・seed 6）・本体 `plan-pilot`（n = 3・117 試行・6 ブロック・seed 5）。どちらも `--validate` exit 0。
- セルのファイル（`~/ime-pilot/cell-imm.json` / `cell-tsf.json`・`make_cells.py` で生成）: `refinput_cmd` は (a) `refinput_imm.exe --out {out}`・(b) `refinput_tsf.exe --out {out}`、`focus_window` は (a) `refinput_imm (gt/1 win_imm)`・(b) `refinput_tsf (gt/1 win_tsf)`、`away_window` は `ime-away`（下の所見 4）、`reset_cmd` は空。
- `focus_cmd`: 新しい `focus_front.py`（`~/ime-pilot/`・標準ライブラリだけ）。題が一致する窓がちょうど 1 つあることを確かめ、`SetForegroundWindow`（拒否されたら前面の窓のスレッドに `AttachThreadInput` して再試行）→ 前面を 0.2 秒おきに最大 5 回読み戻し、違えば exit 1 → **確かめてから** `VK_IME_ON`（0x16）を `SendInput` で押す。→ **MS-IME は `VK_IME_ON` でオンになった**（各ブロックの最初の打鍵から composition が始まる）。
- 電源: AC・DC ともスリープ 0・画面オフ 0・スクリーンセーバーなし → 変えていない（判断 136）。

## 短い試しの結果（`short-imm`・`short-tsf`・各 39 試行・約 8.4 分・打ち切りなし・3 ブロックとも前面の確認が取れた）

| 項目 | (a) IMM | (b) TSF |
|---|---|---|
| 届いた呼び出し | `start_comp` / `comp`（flags 0x1b9 で打鍵中・確定は 0x1e00 で `result_len` > 0）/ `end_comp` / `notify`（IMN 3・4・5 と私的な 15・269・270 ほか）/ `key_down`（IME が処理したキーは 229） | `tsf_start` / `tsf_update`（**`OnEndEdit` が来る・`ITfRangeACP` で長さが取れる**）/ `tsf_end` / `ui_begin` / `ui_end`（**候補の窓が candidate として来る**）/ `focus_in` / `focus_out`。`key_down` は 15 行だけ（IME が消費したキーは来ない・README のとおり） |
| 確定と取消の区別 | `GCS_RESULTSTR` の `comp`（`result_len` > 0）の有無で分かれる | **`tsf_end` の `result_len` で分かれる**（確定 > 0・取消 0） |
| フックへの到達（`reach.py`） | 送った押下 1,174 のうち 1,168（99.5%）。欠けは S14 の 3 試行の `ime_off` / `ime_on` の 2 押下ずつだけ（観測しないキー・Mac と同じ形） | 同じ（1,168 / 1,174） |
| 時計（`clock_sync.py`・中央値） | obs − oracle **1 ms**・gt − oracle 5 ms（壁）/ 5.3 ms（単調）・3 ブロックすべてで一致 | obs − oracle 1 ms・gt − oracle 5 ms / 4.8 ms |
| 1 試行の実時間 | 待ち込みで 505 s / 39 試行 = **約 13 s / 試行** | 同じ |

- ★ **2 経路の区間はほぼ同じ**（同じ計画の別の run で、試行ごとの最初の呼び出しの差 −17〜+9 ms・最後の呼び出しの差の中央値 −3 ms）。200 ms を超えて食い違ったのは S8・S14 の各 1 試行（持ち越しの絡む試行）。
- ★ 経路 (b) の停止条件（README の 4 点）は**どれも成り立った**: (1) `OnEndEdit` が来る・(2) 長さが取れる・(3) 候補の窓の `BeginUIElement` が来る・(4) `result_len` で確定と取消を分けられる。
- 呼び出し列の型は試行ごとにほぼ全部違う（`comp` と `notify` が打鍵ごとに交互に入り、「+」で畳めない）→ 型の数え方（畳み方）は M6 で正解の定義と一緒に決める。

## 所見（M6 の前に研究者が決める・直していない）

1. ★★★ **S4（Space → Esc 2 回）が MS-IME で取り消しにならない —— 凍結したコードの制約**。複数文節に変換した後は、Esc 1 回目で注目文節の変換が戻り、2 回目でひらがなに戻って予測の窓が開くだけで、**3 回目で取り消し**（`esc_probe3`・長い句・2 回とも同じ）。1 文節（`kaigi`）なら 2 回で取り消せた（間隔 120〜860 ms のどれでも・`esc_probe2`）。4 回目以降の Esc は IME を通らない Esc（`key_down` が 229 以外）になるだけ。短い試しでは S4 の 3 試行すべてで未確定の文字列が残り、次の試行へ持ち越された。⚠️ S4 の手順「`space`, `esc`, `esc`」は `generate_plan.py` の `_scenario_checks` に **OS を問わず固定**されており、`_PROFILES["windows"]` にも手順書の `os.windows` にも逃がせない（手順書だけ変えると生成器が計画を拒む）→ **事前登録 §8 の追補の範囲で直せない**。引き継ぎ §3 のとおり直さずに研究者に戻す（逸脱として `experiment/deviations.md` に記録するかを含めて）。
2. **S8（Space 2 回 → 数字）が確定しない**: MS-IME では数字は候補を選ぶだけで、確定には Enter が要る（`esc_probe` の digit の 2 例: 数字だけでは composition が残り、数字 ＋ Enter で `result_len` > 0）。→ `_PROFILES["windows"]["after_digit"]` を `["enter"]` にし、手順書の `os.windows` の S8 も合わせる（**§8 の範囲**・Mac の `after_digit` と同じ形）。
3. **S15（前面の切り替え）は、前面を外れた時点で確定される**: `focus_out` → `comp`（`result_len` > 0）→ `end_comp`。戻った後の Enter は IME を通らない Enter（参照入力欄に改行が 1 つ入る）。手順書の Enter は `_PROFILES["windows"]["commit"]` と共通なので S15 だけ外すことはできない（外すと S1 などの Enter も消える）→ 改行は残るが害は小さい。正解の定義（`gt_rules` の Windows のブロック）では「S15 の確定は `focus_out` の時点」と書く必要がある（M6）。
4. **S15 の移り先**: 最初はエクスプローラーの窓（題「ime-away - エクスプローラー」）にしたが、run の間に閉じられて 1 本目の TSF が打ち切られた（`short-tsf-aborted2`・キーは 4 試行目まで）。→ 移り先は自前の小さな窓（`away_window.py`・tkinter・題 `ime-away`）にした。M7 でも run の間だけ置く（Windows だけが使う新しいファイル・M6 で `kit/run/` に足すか研究者が決める）。
5. ★ **前面ロック**: `run_cell.py` を裏のシェル（Claude Code の Bash）から起動すると、送出器が開くときの `SetForegroundWindow` が拒否されることがある（返り値 0・読み戻しで止まる・キーは 1 つも送られない）。200 秒入力が無い状態を作っても拒否された（`ForegroundLockTimeout` の時間切れが原因ではない）。拒否されなかった 2 回は、どちらも直前にこちらで新しい窓を開いて前面にしていた。→ `run_cell.py` の外側から、参照入力欄の窓が現れた時点で `focus_front.bring`（`AttachThreadInput`）で前面にする薄いラッパー（`run_fg.py`）で起動した。凍結のコード（`run_cell.py`・`backend_windows.py`）は変えていない。S15 の `focus_back` は送出器自身が直前にキーを送っているので通る（短い試しで確認）。→ M7 の起動の手順（ラッパーを Windows だけの新しいファイルにするか、研究者が前面の端末から起動するか）を M6 で決める。
6. **S5（Esc 1 回）**: 打鍵の直後は予測の窓が開いており、Esc 1 回で取り消された（持ち越しの無い試行 2 / 2）。`_PROFILES["windows"]["cancel"]` は `["esc"]` のままでよい。
7. **IME のオン**: `VK_IME_ON` が効いた。持ち越しの影響で 1 ブロックの頭に前のブロックの未確定の文字列が残るかは、本体の結果で確かめる。

## 本体（`pilot-imm`・`pilot-tsf`・各 117 試行・6 ブロック・凍結の手順のまま）

- 2 本とも打ち切りなし・6 ブロックすべてで前面の確認が取れた（`run_fg.py` で起動）。所要 **27.6 分 / 117 試行 = 14.1 s / 試行**（待ち・マーカー込み・Mac の 10.9 s より長い）。試行の実時間は中央値 11.8 s・p95 28.6 s。→ 本番の n = 75（13 シナリオ × 3 速さ × 75 = 2,925 試行）なら **約 11.5 時間 / セル**。
- 到達: 3,900 押下のうち 3,882（99.5%）。欠けは S14 の 9 試行の IME キー 2 押下ずつだけ（設計どおり）。
- 時計（中央値・最小〜最大・ドリフト）: IMM は obs − oracle 1 ms（1〜2）・gt − oracle 4 ms（4〜5）・ドリフト ≈ 0。TSF は obs − oracle 1.5 ms（0〜2）・gt − oracle 4 ms（2〜5）・ドリフト 10.7 ms/h（残差は小さい）。観測側は 6 ブロックすべてでマーカーが一致。**gt 側はブロック 1・3・5 でマーカーが見つからない**（どちらの経路も）—— そのブロックの頭に前の試行の未確定の文字列が残っていて（所見 1・2 の持ち越し）、矢印が composition の中の移動として IME に取られたため（Mac の README の注記と同じ機序）。
- 持ち越し: S4 は 9 / 9、S8 は 9 / 9 で未確定の文字列が残った（所見 1・2）。持ち越しを受けた試行は IMM で 19（TSF の集計でも 19）。持ち越しの無い試行は、S1・S2・S3・S7・S10・S12・S13・S14・S15 が**すべて確定**、S5・S6 が**すべて取消**（意図どおり）。
- ★ **2 経路の比較**（同じ計画の 2 つの run・117 試行すべてで両方に呼び出しがあった）: 最初の呼び出しの時刻の差（TSF − IMM）は中央値 5 ms（p5 −5・p95 9・範囲 −29〜13）。最後の呼び出しの差は中央値 −1 ms（p95 9）で、200 ms を超えたのは 8 試行:
  - **S7 の 3 試行（経路で挙動が違う）**: TSF の参照入力欄（RichEdit）では、文節の数を超えて → を押すとその場で確定（`tsf_end` の `result_len` > 0）し、残りの → と Enter は IME を通らないキーとして入る（Enter は改行）。IMM の窓では同じ計画の同じ試行で Enter まで未確定のまま。→ **同じ MS-IME でも、入力欄の種類（TSF を使う RichEdit か、既定の入力コンテキストの窓か）で確定の時点が変わる**。正解の経路を選ぶとき（M6）の材料。
  - S14 の 5 試行: IMM だけが `ime_on` の後に `notify`（IMN 8 = 開閉の状態）を受けるので、最後の呼び出しが後ろにずれる。確定の時点は両経路で同じ（`ime_off` で確定）。
- ★ **持ち越しの扱いが経路で違う**: 持ち越した文字列の後に新しい読みを打って確定したとき、IMM は確定を 2 回（`result_len` > 0 の `comp` が 2 つ）と記録し、TSF は「確定のすぐ後の新しい composition」の規則で `result_len` の無い `tsf_end` ＋ 新しい `tsf_start` と記録する（9 件・README の仕様どおり・下流は取消として数える）。→ 持ち越しを無くせば消える差（所見 1・2 が直れば消える）。
- 封印（`seal.json`・原本の SHA-256・封印の時刻 UTC）: `short-imm` `e3c55e27…`（19:43:19Z）・`short-tsf` `16ce2bfc…`（20:06:24Z）・`pilot-imm` `b188d3db…`（20:40:00Z）・`pilot-tsf` `d337e706…`（21:07:41Z）。計画の SHA-256: `plan-short` `a2192872…`・`plan-pilot` `01d8c811…`。生ログと封印は `~/ime-pilot/runs/`（git に入れない）。打ち切った run（キーを 1 つも送らずに止まった 2 本と、窓が閉じられて 4 試行で止まった 1 本）は `runs/aborted/`。
- 試験（`~/ime-pilot/probe/`・参照入力欄だけ・観測なし）: `esc_probe`（Esc の回数と数字の後の Enter）・`esc_probe2`（1 文節で Esc の間隔を 120〜860 ms に振る）・`esc_probe3`（長い句で Esc 2〜4 回）。

## 残り（研究者の判断が要る・M6 の前）

1. ★★★ **S4**（所見 1）: 凍結の生成器が S4 を「Space → Esc 2 回」に固定しており、MS-IME では複数文節の変換を取り消せない。選択肢の例: (a) 逸脱として生成器の S4 の照合を OS ごとにする（Windows は Esc 3 回以上）—— `experiment/deviations.md` に記録・(b) Windows のセルでは S4 を「取消になるとは限らない試行」として扱い、持ち越しを解析で処理する・(c) Windows のセルから S4 を外す。どれも §8 の範囲の外か、正解の定義に関わる。
2. **S8**（所見 2）: `after_digit` を `["enter"]` にする（§8 の範囲）→ 直した手順で短い確認の run（Mac の `verify-1` の形）を回す。
3. **正解の経路の選択**（M6）: (a) IMM と (b) TSF はどちらも確定と取消を分けられる。違いは S7 の確定の時点（入力欄の種類による）と、持ち越しの記録のしかた。
4. **起動の手順**（所見 5）: 前面ロックのため、M7 でも `run_fg.py` の形の起動か、研究者が前面の端末から起動するかを決める。`focus_front.py`・`away_window.py`・`run_fg.py` を Windows だけの新しいファイルとして `kit/run/` に足すかも（M6）。
5. 公開用の `experiment/pilot-windows.md`（英語）は、上が決まってから書く（Mac の `pilot-macos.md` も正解の定義の後に書いた）。→ M5 はまだ閉じない。

## 確認の run（2026-10-03・判断 137 で直した手順・`verify-imm`・`verify-tsf`）

- 手順の変更: S4 は Esc 3 回（逸脱 D1・`experiment/deviations.md`）、S8 は数字の後に Enter 1 回（`_PROFILES["windows"]["after_digit"]`・§8 の範囲）。コミット `f657509c`。
- 計画 `plan-verify`（n = 1・39 試行・3 ブロック・seed 8・SHA-256 `f02e046b…0154`）は直した生成器（LF の worktree `~/ime-pilot/wt-lf`）で作り、`--validate` exit 0。runner・送出器・ロガー・参照入力欄はタグの書き出しのまま（runner は計画を生成器で検証しない —— 検証は selftest の中だけ・確かめた）。起動は前回と同じ `run_fg.py`。2 本とも打ち切りなし・3 ブロックとも前面の確認が取れた・各 9.9 分。
- ★ **結果（2 経路とも同じ）**: 持ち越しは **0 件**（前回の本体は 19 件）。S4 は 3 / 3 で取消（IMM は 3 回目の Esc で `comp`〔結果なし〕→ `end_comp`、TSF は 3 回目で `tsf_end` の `result_len` 0 —— 1 回目・2 回目は composition が残る・所見 1 の機序どおり）。S8 は 3 / 3 で確定。S1・S2・S3・S7・S10・S12・S13・S14・S15 は確定、S5・S6 は取消（意図どおり）。
- 到達: 1,470 押下のうち 1,464（99.6%）。欠けは S14 の 3 試行の IME キー 2 押下ずつだけ（設計どおり）。
- 時計: **gt のマーカーが 3 ブロックすべてで見つかった**（前回の本体はブロック 1・3・5 で欠けた —— 持ち越しが消えたため）。IMM は obs − oracle 1 ms・gt − oracle 4 ms、TSF は obs − oracle 0 ms・gt − oracle 3 ms（中央値）。ドリフトの値（gt 側 約 40 ms/h）は 3 点・10 分からの外挿で当てにならない（範囲は 2〜9 ms）→ 本体の値（IMM ≈ 0・TSF 10.7 ms/h）を参照する。
- 残る既知の差: S7 の 1 試行で TSF だけ IME を通らない Enter が入った（所見の「S7 の経路差」と同じ）。S15 の戻りの Enter は両経路で IME を通らない（所見 3）。
- 封印: `verify-imm` `9e20cc4c…`（04:10:03Z）・`verify-tsf` `7c78eb1a…`（04:20:16Z）。生ログは `~/ime-pilot/runs/`。
- → 直した Windows の手順は**意図どおりに動く**。M5 に残るのは公開用の `experiment/pilot-windows.md`（正解の経路の選択・起動の手順・`gt_rules` の Windows のブロックが決まってから・M6 と一緒に）。
