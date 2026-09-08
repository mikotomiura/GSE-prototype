# 次セッション開始プロンプト（**Windows / G-GEAR 専用**）— 孤児回収の実機検証と稼働コスト実測

> ★ このファイルの「===」以下をコピペして Windows 側の Claude Code に渡す。
> ⚠️ **新セッション**（`/clear` 後）で始めること。
> ★ モデル: **Sonnet** で足りる（⚠️ ただし §1 の判断だけは迷ったら Opus）。
> ⚠️★★★ **これは Windows でしかできない仕事だけを集めてある。** Mac 側では代替できない。

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ⚠️ このメモを一次資料にしない

★ 2026-09-03 の Mac 側セッションでは、引き継ぎメモの主張のうち **1 件が完全な誤り**で、
**1 件は見積もりが甘すぎた**。⚠️ **このメモも同じ確率で間違っている。**

| 例 | ⚠️ 実体 |
|---|---|
| 「トレイが『記録していません』と嘘をつく」 | ⚠️ **誤り。** 1 週間前に修正済みだった。★ **呼び出し側だけ見て受け側を読まなかった**のが原因 |
| 「OS の正常終了なら `session_end` が書かれるかも」 | ⚠️ **甘い。** ★ `ExitRequested` / `SIGTERM` / `WM_ENDSESSION` のハンドラは repo に **0 件** |

→ ★ **数字・状態・手順は必ず自分で確かめ直すこと。**

### 0-1b. ⚠️★★★ **2026-09-05 に前提が変わった**（★ この節が最新・上の 0-1 より優先）

★ Mac 側で 8 時間の再測を 2 本回し、⚠️ **計器の欠陥を 6 件**見つけて直した。
→ ⚠️ **このメモの下半分（§1 以降）は 2026-09-03 に書かれたもので、手順が古い。**

| ★ 変わったこと | ⚠️ Windows でどう効くか |
|---|---|
| ★ 指標 3 が「バッテリー %」→ **プロセス単位のエネルギー影響** (`top -stats power`) | ⚠️ **Windows には相当する公開指標が無い。** ★ `sample-windows.sh` は 7・8 列目を**空**で出し、集計は「**windows では測れない**」と表示する（⚠️ 「壊れている」ではない）。→ ★ **総合は必ず `DataInsufficient` になる。それが正しい。** |
| ⚠️ **対照 (`without-gse`) は廃止**した | ★ **回さないこと。** ⚠️ GSE が居ない条件では全列 0 になるだけで、8 時間が無駄になる（★ Mac で実際に無駄にした） |
| ★ `run.sh` が **開始時のスナップショット** (`ndjson-size-start.tsv`) を取るようになった | ★ これが無いと集計は NDJSON を**判定しない**（⚠️ 推定を実測として返さないため）。★ 新しい `run.sh` を使えば自動で取れる |
| ⚠️ **順序が指標 5（起動コスト）を決める** | ★ **サンプラを先に起こし、1 分の基線（全列 0）を取ってから GSE を起動する。** ⚠️ 起動後から測ると起動コストは**原理的に測れない** |
| ⚠️ **35 秒間隔では起動の山を拾えない**（★ 孤児回収の走査は約 1.5 秒） | ★ 8 時間の本測とは**別に**、`GSE_COST_DURATION_S=300 GSE_COST_INTERVAL_S=1` の短い run を 1 本足すと山が見える |
| ★ `request_reinstall()` の判定が変わった（PR #158） | ⚠️ 旧: 戻り値に関わらず 1 回で諦める → 新: **出せたときだけ済み・出せなければ上限 3 回**。★ Windows は元々 `true` を返すので**実質不変のはずだが、実機で確かめること** |
| ★ 送信 timeout が 180 → **300 秒**（PR #159） | ⚠️ `LOCK_STALE_AFTER >= timeout × 10` の不変条件がある（★ 600 秒にすると壊れる） |

### 0-1c. ⚠️★★★ **走らせる前に必ずやる 1 分スモーク**（★ これを飛ばさない）

⚠️ 2026-09-05 に、**Windows のサンプラが 6 列しか出さない**のに `run.sh` のヘッダが 8 列、という
欠陥を**渡す直前に見つけた**（★ そのまま 8 時間回していたら丸損だった）。→ ★ 直してあるが、
⚠️ **自分で確かめること**:

```bash
cd /path/to/GSE-prototype
D=experiments/20260903-o1-runtime-cost
# ★ GSE を起動した状態で 1 分だけ回す
GSE_COST_DURATION_S=60 GSE_COST_INTERVAL_S=10 bash $D/run.sh with-gse
cat $D/results/with-gse/samples.tsv
#   ★ 期待: **8 列**。1〜6 列目に実値、7・8 列目は **空**（⚠️ 0 ではない）
awk -F'\t' 'NR==2{print "列数 =", NF}' $D/results/with-gse/samples.tsv   # ★ 8 のはず
rm -rf $D/results/with-gse    # ★ スモークは捨てる
```

⚠️ **CPU% の意味が macOS と違う**（★ `sample-windows.sh` のコメント）:
Windows の `% Processor Time` は**全コア合計に対する %**、macOS の `top` は **1 コア = 100%**。
→ ⚠️ **2 つの OS の CPU 平均を直接比べない。** ★ 比べるならコア数で割って揃える。

### 0-2. ★ 現状を測る（⚠️ 下は「書かれた時点」の値）

```bash
# ⚠️★★★ Windows では **git-bash** を使う（PowerShell では hook もスクリプトも動かない）
cd /path/to/GSE-prototype
git fetch origin && git checkout main && git pull --ff-only
git log --oneline -3                      # ★ 2026-09-05 時点 8541497 (PR #158/#159 マージ済み)
cd src-tauri && cargo test --features package --workspace   # ★ 同 583 緑 (⚠️ --features package を落とすと 34 件走らない)
```

### 0-3. ⚠️★★★ **最初に読む一次資料**（★ これを読まずに始めない）

- `src-tauri/src/o1.rs` の `close_orphaned_sessions` の doc コメント（★ 今回検証する対象）
- `.steering/20260903-o1-preflight-4/decisions.md` 判断 2 / 判断 6（★ なぜこの設計か）
- `experiments/20260903-o1-runtime-cost/README.md`（★ 何をどう測るか・判定表）

---

## §1 ⚠️★★★ **孤児回収（PR #151）を実機で検証する** — ★ 本セッションの主題

### なぜ Windows でしかできないか

★ 2026-09-03 に入れた修正は「アプリが正常終了できなかったとき、次回起動で
セッションを閉じ直す」というもの。⚠️ **その「正常終了できない」を作るのが実機作業**であり、
★ **Windows の `WM_ENDSESSION` が Tauri/tao 経由で `CloseRequested` に翻訳されるかは
コードからは決められない**（⚠️ memory `windows-only-code-needs-ci`: 手元の検査は相手 OS を 1 行も
コンパイルしない）。

### ⚠️★★★ 検証の前に —— **自動提出を必ず外す**

★ O1 は **48 時間後に承認なしで自動提出する**。⚠️ 検証で作ったゴミが**研究データに混ざる**。

```bash
# ⚠️ 提出経路を閉じる（★ auto_submit_enabled() は o1_consent_ack を要求する）
mv ~/.gse/o1_consent_ack ~/.gse/o1_consent_ack.bak   # ★ 検証後に必ず戻す
ls ~/.gse/          # ⚠️ o1_participant_id が何になっているかも記録する
```

⚠️★★ **これを飛ばすと、あなたの検証セッションが被験者データとして送信される。**
★ 2026-06 に「研究者の test セッション (P006) が確証標本に混ざった」前例がある
（memory `pilot-calibration-label-yield-gap`）。

### ★ 手順（⚠️ 3 状態を全部やる）

★ 対象は **O1 モードのビルド**（`o1.mode` マーカーの隣に置いた `gse-next.exe`）。
⚠️ **ビルドの版を先に記録すること**（★ PR #151 を含む版でないと検証にならない）。

| # | 何をする | ★ 期待する結果 | ⚠️ 見るところ |
|---|---|---|---|
| **A: 正常終了** | GSE を起動 → 数分打鍵 → **トレイの「GSE を終了」** | ★ その場で `session_end` が書かれる | `gse_o1_*.ndjson` の末尾 |
| **B: 強制終了** | 起動 → 数分打鍵 → **タスクマネージャで「タスクの終了」** → **再起動** | ⚠️ **ここが本番。** ★ 再起動時に前のファイルが閉じられる | `gse-app.log` に `O1 orphan sweep: closed` |
| **C: OS 再起動** | 起動 → 数分打鍵 → **GSE を終了せずに Windows を再起動** → GSE を起動 | ⚠️★★★ **未知。** ★ `session_end` が既にあれば tao が翻訳している／無ければ B と同じ経路で回収される | 同上 |

```bash
# ★ ログの場所（★ Documents/GSE-sessions/gse-app.log）
grep -F "O1 orphan sweep" ~/Documents/GSE-sessions/gse-app.log

# ★ 各 NDJSON が閉じているか（⚠️ 「文字列が在るか」ではなく **数値が取れるか**で見る）
for f in ~/Documents/GSE-sessions/gse_o1_*.ndjson; do
  printf '%s  ' "$(basename "$f")"
  grep -o '"session_end":[0-9]\+' "$f" | tail -1 || echo "(閉じていない)"
done
```

### ⚠️ 3 状態で「壊れ」も試す

- ⚠️ **書き込めないファイル**: 1 本を読み取り専用にして起動 →
  ★ `gse-app.log` に `cannot close` が出て、⚠️ **`closed` に数えられていない**こと
- ⚠️ **既に閉じたファイル**: もう一度起動しても `session_end` が **2 行にならない**こと（べき等）
- ⚠️ **時計を戻す**: ★ **やらなくてよい**（⚠️ Windows の時刻変更は他を壊す）。
  ★ 単体テスト `a_clock_that_went_backwards_closes_nothing` で担保してある

### ★ 記録すること

⚠️ **C の結果は「未知の解消」なので必ず書く。** →
`.steering/<日付>-windows-orphan-verify/` を作り、⚠️ **A / B / C それぞれの生ログ**を残す。
★ 終わったら `~/.gse/o1_consent_ack.bak` を**戻す**（⚠️ 戻し忘れると自動提出が永久に止まる）。

---

## §2 ⚠️ **稼働コストの実測**（★ 8 時間 × 2 本・放置でよい）

★ 器は `experiments/20260903-o1-runtime-cost/` にある。⚠️ **実測はまだ 1 秒もされていない。**

### ⚠️★★★ Windows 側は **一度も実行されていない**

★ `scripts/sample-windows.sh` は **macOS 上で書かれ、Windows で走らせたことが無い**
（⚠️ 中で PowerShell を呼ぶ）。→ ★ **必ず短時間のスモークから入る:**

```bash
cd /path/to/GSE-prototype
# ⚠️ GSE を起動した状態で 1 分だけ
GSE_COST_DURATION_S=60 GSE_COST_INTERVAL_S=10 \
  bash experiments/20260903-o1-runtime-cost/run.sh with-gse
cat experiments/20260903-o1-runtime-cost/results/with-gse/samples.tsv
```

⚠️★★ **`cpu_pct` / `rss_kb` が全部 `0` なら失敗している。** ★ 疑うのは 3 つ:

1. ⚠️ **プロセス名**: `pgrep -x 'gse-next'` が当たっているか →
   `powershell.exe -Command "Get-Process | Where-Object {\$_.ProcessName -like '*gse*'}"` で実名を見る
2. ⚠️ `Get-Counter` のカウンタ名が**日本語ロケールで違う**可能性
   （★ `\Process(...)\% Processor Time` は英語名。⚠️ 日本語 Windows では
   `\Process(...)\% Processor Time` が引けないことがある → `Get-Counter -ListSet Process` で確認）
3. ⚠️ `Win32_Battery` は**デスクトップ機では null**（★ G-GEAR がデスクトップなら
   `battery_pct` は空で正常。→ ⚠️ **バッテリー指標は Windows では測れないと明記する**）

★ スモークが通ったら本番（⚠️ **既存の結果があると `run.sh` は止まる**ので先に消す）:

```bash
rm -rf experiments/20260903-o1-runtime-cost/results/with-gse
bash experiments/20260903-o1-runtime-cost/run.sh with-gse      # ★ 8 時間・GSE 起動中
# ★ 翌日、対照（GSE を終了した状態で同じ時間）
bash experiments/20260903-o1-runtime-cost/run.sh without-gse
python3 experiments/20260903-o1-runtime-cost/scripts/summarize.py
```

### ⚠️ 回す前に `env.md` を埋める

★ `experiments/20260903-o1-runtime-cost/env.md` の Windows 行:
**OS 版（`winver`）/ 機種 / ⚠️ AC かバッテリーか / GSE のビルド版**。
⚠️ **電源条件を書かないと対照が成立しない。**

### ⚠️ メモリの列は 2 つある

★ `rss_kb` = `WorkingSet64` / `rss_alt_kb` = `PrivateMemorySize64`。
⚠️★★ **macOS の値と絶対値を比べないこと**（★ 定義が違う。2026-09-03 に Finder で
`top`=546M vs `ps rss`=36MB の **15 倍差**を実測した）。★ **傾き (MB/h)** で見る。

---

## §3 ⚠️ **overlay の透明窓がクリックを奪わないか**（★ 15 分・Windows が本場）

⚠️★★★ **既知の制約を実測したのは Windows である**（memory `macos-overlay-clickthrough-bug`
の続報 4: 透明 WebView2 窓は `setIgnoreCursorEvents(true)` でも透明ピクセルでクリックを捕捉する。
Tauri #11461 / #13070 / #2090）。

★ O1 では介入が落ちている（`lib.rs:3241` `INTERVENTION_ENABLED.store(false, ...)`）ので
overlay は `show()` されないはずだが、⚠️ **窓自体は無条件に事前生成される**
（`lib.rs:4669` `transparent(true)` ＋ `always_on_top(true)` ＋ `visible(false)`）。

→ ★ **数週間ずっと出しっぱなしにする前に確かめる:**

1. O1 モードで GSE を起動して**放置**
2. ★ 画面の**四隅と中央**で、背後のアプリのボタンを普通に押せるか
3. ⚠️ 押せない場所があれば **座標を記録**（★ 「なんとなく変」で終わらせない）
4. `debug_overlay_window_state`（計装が番兵として残置してある）で窓の位置とサイズを読む

⚠️ **「たぶん大丈夫」と書かない。** ★ 押した場所と結果を列挙する。

---

## §4 ★ 触らないもの

- ⚠️ `Form_G1/` / `Form_O1/`（★ GAS は Mac 側と実物の同期を取っているので、**Windows から触らない**）
- ⚠️ 事前登録の凍結節（`check_frozen_sections.py` が守る `docs/preregistration-v0.3.md §3`）
- ⚠️ `gse-dataset` の履歴（★ 2026-09-03 に Mac 側で整理済み・`576b873`）

## §5 ★ 完了報告に必ず書くこと

- [ ] ⚠️ **§1-C（OS 再起動）の結果** —— ★ これが本セッション最大の成果
- [ ] ⚠️ `~/.gse/o1_consent_ack` を**戻したか**
- [ ] ⚠️ 検証で作った NDJSON を**どうしたか**（★ 消したなら消したと書く）
- [ ] ⚠️ §2 のスモークで **0 が出たか / 出なかったか**（★ 出たなら原因も）
- [ ] ⚠️ **未検証が残っているうちは「問題なし」と書かない**（★「N 件中 M 件を実測、未検証 K 件」）

## ⚠️★★★ 作業規約（★ CLAUDE.md より・省略しない）

1. `.steering/[YYYYMMDD]-[task-name]/` に `requirement.md` / `design.md` / `tasklist.md` を作る。
2. 必須 Skill を読んでから手を動かす: `verify-before-claiming` / `data-privacy` /
   `reproducibility-discipline`（★ §2 で必須）/ `git-workflow`。
3. ⚠️★★ **「緑だから正しい」と書かない。** 検査は**正常 / 不在 / 壊れ**の 3 状態で試し、
   ★ **陰性対照**（壊していないものが緑のままか）も置く。
4. ⚠️ 異常値・全件一致を見たら、★ **まず自分の測定器を疑う**
   （★ 2026-09-03 に Mac 側で測定器を 2 回壊した。詳細は
   `.steering/20260903-o1-preflight-4/decisions.md` 判断 8）。
5. ★ コード変更をしたなら `/cross-review` 必須。⚠️ **一致した指摘でも実コードに降りてから採否を決める。**
