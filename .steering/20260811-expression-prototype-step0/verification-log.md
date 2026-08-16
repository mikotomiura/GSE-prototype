# Step 0 実測ログ — `toeexpand` / `toecollapse` 往復検証

> 実施: 2026-08-11 / 実機: Windows 11 Home 10.0.26200 (this machine) / shell: git-bash
> TouchDesigner **2025.33070** (`C:\Program Files\Derivative\TouchDesigner`)
> 作業ディレクトリ: scratchpad 配下（★ **Program Files 内では作業していない**）
> ⚠️ 本ファイルは**実行したコマンドと生出力**の記録である。判定は `decisions.md` にある。

---

## 0. 実体の存在確認（★ 引き継ぎメモを根拠にせず、このセッションで実測）

```bash
$ ls -la "/c/Program Files/Derivative/TouchDesigner/bin/toeexpand.exe" \
         "/c/Program Files/Derivative/TouchDesigner/bin/toecollapse.exe"
-rwxr-xr-x 1 johnd 197611 2551072  7月 16 16:00 .../bin/toecollapse.exe
-rwxr-xr-x 1 johnd 197611 2941208  7月 16 16:00 .../bin/toeexpand.exe

$ ls -la "/c/Program Files/Derivative/TouchDesigner/Samples/Setup/Base/NewProject.toe"
-rw-r--r-- 1 johnd 197611 770  1月 23  2026 .../Samples/Setup/Base/NewProject.toe
```

★ 3 点とも存在する（引き継ぎ §3 の記述と一致）。同梱サンプルは **`.tox` 795 本 / `.toe` 8 本**。

---

## 1. ⚠️★★★ 最重要 — `toeexpand` の終了コードは **反転している**（成功=1 / 失敗=0）

引き継ぎ §3 は「`toeexpand` は引数なしで usage を出して **exit 0** を返す」と書いていたが、
**実測ではそうならない。** 3 通りの測り方で確認した:

```bash
$ "$TOEEXPAND" >/dev/null 2>&1; echo "exit=$?"          # → exit=1
$ set +e; "$TOEEXPAND" >/dev/null 2>&1; rc=$?; ...       # → exit=1
$ powershell -Command "& '...\toeexpand.exe' *> $null; $LASTEXITCODE"   # → 1
```

★ **さらに調べたところ、事態は引き継ぎの警告より悪い。** 4 状態で実測:

| 実行 | 終了コード | 出力の 1 行目 | 実際に起きたこと |
|---|---|---|---|
| `toeexpand`（引数なし） | **1** | `Usage: ...toeexpand.exe [-b] filename [pattern]` | 何もしない |
| `toeexpand nosuch.toe` | ★★ **0** | `Error opening file: nosuch.toe` | ★ **失敗**（dir は作られない） |
| `toeexpand ok.toe` | ★★ **1** | `ok.toe expanded into directory ok.toe.dir and` | ★ **成功**（dir + toc を生成） |
| `toeexpand junk.toe`（中身が `not a toe`） | ★★ **0** | `r is 4` | ★ **失敗**（dir は作られない） |

> ★★★ **`toeexpand` は「成功したら 1・失敗したら 0」を返す。**
> `if toeexpand f.toe; then ...` と書くと **全ての失敗を成功と判定し、全ての成功を失敗と判定する**——
> **単に無意味なのではなく、正確に逆になる。**

`toecollapse` は**正常**である（0=成功 / 1=エラー）:

| 実行 | 終了コード | 出力 1 行目 |
|---|---|---|
| `toecollapse`（引数なし） | 1 | `Usage: ...toecollapse.exe filename` |
| `toecollapse nosuch.dir` | 1 | `This application requires:` |
| `toecollapse ok.toe.dir` | **0** | `ok.toe moved to ok.toe.bkp1` |

★ **判定に使ってよい信号**:

- **expand**: 標準出力に **`expanded into directory`** が出ること ＋ `*.dir` と `*.toc` が実在すること
- **collapse**: **exit 0** ＋ 標準出力に **`moved to`** が出ること（バックアップ退避のメッセージ）

---

## 2. (a) 展開ツリーはテキストとして読めるか → ★ **読める**

### 2.1 空プロジェクト `NewProject.toe`（770 B）

```
$ toeexpand NewProject.toe
NewProject.toe expanded into directory NewProject.toe.dir and
listed in file NewProject.toe.toc
```

生成物: `NewProject.toe.dir/`（9 ファイル）＋ `NewProject.toe.toc`。**全 10 ファイルが `ASCII text`。**

```
NewProject.toe.toc     ASCII text     ← 収録順を書いた目次
.application  .build  .grps  .start   ← ASCII text（デスク配置 / TD 版 / クロック設定）
perform.n  perform.parm               ← ASCII text
project1.n  project1.panel  project1.parm
```

中身の実例（**そのまま読めて、そのまま編集できる**）:

```
$ cat NewProject.toe.dir/project1.n
COMP:container
tile 200 100 400 244
flags =  picked on current on viewer 1 parlanguage 0
color 0.56 0.56 0.56
end

$ cat NewProject.toe.dir/.build
version 099
build 2023.11290
time Tue Dec  5 12:00:00 2023
```

### 2.2 実プロジェクト `PythonExamples.toe`（290,692 B）

**8,281 ファイル / 831 ディレクトリ**に展開される（元の 10 倍以上の実効サイズ・計 3,033,898 B）。

| 分類（先頭 8 KB の NUL 有無で判定・`classify.py`） | 件数 |
|---|---|
| **テキスト (UTF-8)** | ★ **7,908 / 8,281 = 95.5%** |
| NUL を含む | 373 |

拡張子の内訳: `.n` 2739 / `.parm` 2652 / `.panel` 1879 / `.cparm` 607 / `.text` 303 / `.table` 55 / ほか。

⚠️★ **「NUL を含む 373 件」の正体は完全なバイナリではない**——**`.text`（Python の DAT）が主**で、
構造は **先頭 ~25 バイトのバイナリヘッダ ＋ プレーンな Python 本文**である:

```
$ head -c 200 .../Callbacks/list1_callbacks.text | od -c
0000000   2  \n   *  \0  \0  \0 001  \0  \0  \0 001  \0  \0  \0 001  \0
0000020  \0  \0 001  \0  \0  \0 002  \0  \0 020 245   #       m   e
0000040   -       t   h   i   s       D   A   T  \n   #      \n   #
...                     ↑ ここから先は普通の Python ソース
```

→ ★ **Python 本文は grep でき、編集でき、git diff にも（ヘッダ以外は）意味のある差分として出る。**

### 2.3 `.tox`（`stoner.tox` 2,201,696 B）

**1,542 ファイル**に展開・**テキスト 1,420 / NUL 含み 122**。

⚠️★★ **ただし `.tox` には真のバイナリ blob が含まれうる**——実例:

| ファイル | サイズ | 中身 |
|---|---|---|
| `stoner/stoner/project/selectOffset.data` | ★ **7,372,827 B** | 真のバイナリ（CHOP/DAT データ） |
| `stoner/icon.data` | 230,428 B | 真のバイナリ（画像） |

→ ★ **`.data` は展開しても git が差分を取れない。**
  ⚠️ ただしこれは **既製の Palette コンポーネントを取り込んだ場合**の話であり、
  **自分で作るパッチが `.data` を持つかは自分で制御できる**（§5 の帰結を参照）。

---

## 3. (b) 往復で情報が失われないか → ★ **失われない**（ただし .toe の byte 一致は初回のみ）

### 3.1 素の往復（編集なし）

| 対象 | 元サイズ | 往復後 | sha256 一致 | ★ **展開ツリー同士の `diff -r`** |
|---|---|---|---|---|
| `NewProject.toe`（770 B） | 770 | 770 | ★ **一致** | — |
| `PythonExamples.toe`（290 KB） | 290,692 | 332,884 | ✗ 不一致 | ★★ **完全一致（差分 0 行）** |
| `stoner.tox`（2.2 MB） | 2,201,696 | 2,205,600 | ✗ 不一致 | ★★ **完全一致（差分 0 行）** |

`.toc` も `diff` で完全一致（両ケースとも exit 0）。

> ★ 引き継ぎ §3 手順 4 の「byte-equal にならなくても直ちに失格ではない。展開ツリー同士で比較して判定する」
> がそのまま適用される場面である。**判定は「ツリーが完全一致」＝情報は失われていない。**

### 3.2 ★★ 多世代往復 — **gen1 以降は byte-equal で安定する（不動点）**

`PythonExamples.toe` を 3 世代連続で往復させた（`gen_test.sh`）:

```
gen  size       sha256_16          collapse_ok tree_vs_gen0
0    290692     dbd348ed8c22f0b9   -           -           ← TD 同梱の原本
1    332884     d34858c337c7d471   YES         base        ← 1 回目で再書き出し
2    332884     d34858c337c7d471   YES         IDENTICAL   ← ★ 以降サイズもハッシュも動かない
3    332884     d34858c337c7d471   YES         IDENTICAL
--- tree0 vs tree3: IDENTICAL ---
```

→ ★★ **サイズ変化は「原本を書いた TD の版が違う」ことによる 1 回きりの再書き出しであり、
往復のたびに劣化・肥大するのではない。** `toecollapse` の出力は**不動点**である。
★ **展開ツリーは全世代で完全一致**なので、**git の差分は綺麗に保たれる**
（そもそも D6 に従い `.toe` はコミットせず、ツリーをコミットする）。

### 3.3 ⚠️★ この検証を 1 回失敗している（記録として残す）

初回の多世代テストは **`gen1 = gen0` で byte-equal** という結果を出したが、**これは空振りだった**。
原因: スクリプトが `.toc` を退避した状態で `toecollapse` を呼んでおり、**collapse が失敗して
元ファイルがそのまま残っていた**ものを「往復後のファイル」として測っていた。

★ 追試で原因を確定させた:

```
$ mv NewProject.toe.toc toc.hidden && toecollapse NewProject.toe.dir
exit=1
This application requires:
  directory NewProject.toe.dir
  file NewProject.toe.toc
$ sha256sum NewProject.toe        # → 元のまま。bkp ファイルも作られない
```

→ ★★ **`toecollapse` は `<name>.dir` と `<name>.toc` の両方を要求する。**
  **`.toc` も一緒に git へコミットしなければ、collapse できないツリーを置くことになる。**
- ⚠️ **教訓**: これは `verify-before-claiming` ルール 5b の silent pass そのものである。
  **出力を見ずに「ハッシュが一致した＝往復は完全」と書きかけた。** 出力を見る形に直して再測した。

---

## 4. ★★ 編集は往復に耐えるか（(a) の実務的な意味）

**素の往復が保存的でも、「編集したものが往復するか」が別問題である**ため、2 通り試した。

### 4.1 編集テスト A — `.n`（純テキスト・同じ長さ）

`NewProject.toe.dir/project1.n` の `color 0.56 0.56 0.56` → `color 0.11 0.22 0.33` に書き換え、
collapse → 別ディレクトリで再 expand:

```
$ cat NewProject.toe.dir/project1.n     # 往復後
COMP:container
tile 200 100 400 244
flags =  picked on current on viewer 1 parlanguage 0
color 0.11 0.22 0.33          ← ★ 編集が生きている
end
$ diff -r <編集後ツリー> <往復後ツリー>   # → exit 0・差分 0 行
```

### 4.2 ★★ 編集テスト B — `.text`（Python 本文・**長さを変える**編集）

★ **バイナリヘッダが長さを持っていたら壊れる**はずなので、意図的に**行を 34 バイト長くした**。
対象: `PythonExamples.toe.dir/project1/Callbacks/list1_callbacks.text`（4,288 → 4,322 B）

```
# text                 str            cell contents
        ↓
# text                 str            GSE-STEP0-EDIT-MARKER-longer-than-original-line
```

collapse → 再 expand の結果:

```
$ tr -d '\000' < .../list1_callbacks.text | grep -n "GSE-STEP0-EDIT-MARKER"
10:# text                 str            GSE-STEP0-EDIT-MARKER-longer-than-original-line

$ diff -r <編集後ツリー> <往復後ツリー>   # → exit 0・差分 0 行（8,281 ファイル中の副作用ゼロ）
```

→ ★★★ **Python 本文を長さごと書き換えても往復する。ヘッダは長さを持っていない。**
  **8,281 ファイルのツリーで、編集箇所以外に副作用が 1 件も出ない。**

---

## 5. git に載せられるか（`data-privacy` / レビュー可能性）

`leakcheck.py` で展開ツリー全体（NUL を除去してから）を走査:

| 検査 | `PythonExamples.toe.dir`（8,281 file） | `stoner.tox.dir`（1,542 file） |
|---|---|---|
| ユーザー名 `johnd` の混入 | ★ **0 件** | ★ **0 件** |
| 絶対パス `C:\` / `C:/` | ★ **0 件** | ★ **0 件** |
| 正規表現 `[A-Za-z]:[\\/]...` の生ヒット | 143 件 → ★ **全て `https://www.derivative.ca` 等の URL の誤検出** | 2 件 → 同上 |

`.build` は **保存した TD の版と時刻**を持つが（例 `time Tue Sep 13 00:06:11 2022`）、
★ **往復では書き換わらない**（3.2 で全世代のツリーが一致している）。
→ **往復のたびにタイムスタンプ差分が出る、という git 上の雑音は発生しない。**
⚠️ ただし **TD 本体で保存し直せば `.build` は更新される**（それは意味のある差分である）。

---

## 5.5 ★★★ TD 本体（GUI）で開けるか → **確認済み**（研究者の承認を得て実機実行）

> 当初は「未確認として残す」判断だったが、研究者の指示（2026-08-11）で実機確認した。

**手順**（★ TD に渡す前に、編集が入っていることを自前で確認している）:

```bash
$ cp .../Samples/Setup/Base/NewProject.toe GseStep0Check.toe
$ toeexpand GseStep0Check.toe
GseStep0Check.toe expanded into directory GseStep0Check.toe.dir and
listed in file GseStep0Check.toe.toc
                                            # ★ 出力で判定（終了コードは見ない）

# 一目で分かる編集をテキストで加える
$ sed -i 's/^color .*$/color 1 0 0 /'         GseStep0Check.toe.dir/project1.n
$ sed -i 's/^tile .*$/tile 400 300 400 244/'  GseStep0Check.toe.dir/project1.n
$ cat GseStep0Check.toe.dir/project1.n
COMP:container
tile 400 300 400 244
flags =  picked on current on viewer 1 parlanguage 0
color 1 0 0
end

$ toecollapse GseStep0Check.toe.dir
exit=0
GseStep0Check.toe moved to GseStep0Check.toe.bkp1

$ # 再展開して編集が生きていることを先に自前確認 → OK（同じ内容）
$ TouchDesigner.exe <往復後.toe>
```

**観測**:

```
process Id=10016 Responding=True
MainWindowTitle=[TouchDesigner 2025.33070: .../scratchpad/td-gui/GseStep0Check.toe]
```

| 画面で確認したこと | 意味 |
|---|---|
| タイトルバーが**往復後ファイルのパス**を表示 | ★ **開いている** |
| ネットワークエディタで **`project1` コンテナが赤** | ★★ **テキスト編集が GUI に反映されている** |
| 右パネルに `Container project1` / Component `/project1` | 構造が正しく読めている |
| `Realtime` ON・**FPS 49** で稼働 | エラー状態ではない |

⚠️ ステータスバーの `Warning: No drop contents for node /ui/dialogs/palette/palette/list/viewer` は
**TD 自身の UI（`/ui/dialogs`）についての警告**で、開いたファイルとは無関係。

> ★★★ **これで往復が「作業ループ」として閉じたことが示された**——
> **`toeexpand` → Claude Code がテキストを編集 → `toecollapse` → TD が読んで反映**。
> **「開けた」だけでなく「書いた変更が出た」ことまで確認している。**

⚠️ **後始末**: 起動した TD プロセス（Id 10016・16:45:55 起動）は `Stop-Process` で終了済み。
★ 起動前に TD は動いていなかったので、**研究者の作業中セッションは壊していない**（プロセス一覧で確認）。

## 6. ⚠️ 本セッションで検証**していない**こと（★ 未確認は未確認と書く）

1. ~~`toecollapse` が書いた `.toe` を TouchDesigner 本体（GUI）が開けるか~~
   → ★★ **本セッション中に研究者の指示で実機確認し、解消した（§5.5）。**
2. **TD で作ったパッチを Claude Code が新規に「書き起こす」ことができるか。**
   本検証が示したのは**既存ツリーの編集が往復する**ことまで。ゼロから `.n` / `.parm` を書いて
   有効なパッチになるかは別問題（**Step 1 以降で GUI 併用が現実的**）。
3. **`.data` blob を含むパッチを git でどう扱うか**（自作パッチで発生させない限り問題にならない）。
4. macOS 側の挙動（本機は Windows のみ）。

## 6.5 ★ Step 1 / Step 2 も実施した（本セッション）

Step 0 が PASS したので、引き継ぎ §4 の順序どおり **Step 1（CSV 化）・Step 2（平滑化）**まで進めた。
以下はその実測。**Step 3 以降は未着手**（理由は `tasklist.md` §未了）。

### 6.5.1 ⚠️★★ `--snapshot` は「出力」ではなく「比較」だった（ドキュメントの誤りを実測で訂正）

引き継ぎ §4 / `20260810-.../design.md` §1.1 / `media-expression-spec.md` §7 の 3 箇所が
`--snapshot out.json` を**出力する手段**として書いていたが、**誤りである**:

```
$ cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot .../snapshot.json
MISMATCH: cannot read .../snapshot.json: 指定されたファイルが見つかりません。 (os error 2)
error: process didn't exit successfully: ... (exit code: 1)
```

一次資料（`src-tauri/src/bin/replay.rs:9-10` の逐語）:

```
//! gse-replay <session.ndjson>                        # stdout に JSON 配列を出力
//! gse-replay <session.ndjson> --snapshot <file>      # 既存スナップショットと完全一致比較
```

★ **正しい取り出し方**（実測 exit 0・5,782 B / 15 行）:

```bash
cd src-tauri && cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson > out.json
```

→ 3 箇所すべてに訂正注記を入れた（S0-D6）。

### 6.5.2 ★★ サンプル間隔は 1000 ms 固定ではない

| fixture | 行数 | 期間 | dt の実測 |
|---|---|---|---|
| `minimal.ndjson` | 15 | 14.0 s | **1000 ms × 14**（均一） |
| `phase1_ime_heavy.ndjson` | 6 | 6.691 s | ★ **1000 ms × 4 ＋ 2691 ms × 1** |

→ ★★ **固定 alpha の EWMA を使うと、サンプルが飛んだとき実効時定数が変わる。**
  表現層の平滑化は **alpha = 1 - exp(-dt/tau)** として **dt を毎回見る**形にした（S0-D7）。

⚠️ **fixture はいずれも短い**（最大 14 秒）。tau=60 s の挙動を実データで見るには足りない。
  → Step 2 の検算は**合成信号**で行った（そう明記した）。**実セッションでの確認は Step 3 以降。**

### 6.5.3 ★★★ 1Hz 階段が 4 Hz の「隣」に実エネルギーを乗せる（spec §1.2 の実証）

`expr_smooth.py --selftest` の実測（Hann 窓付き DFT・合成信号 300 s @ 200 Hz）:

| 周波数 | 階段（1Hz をそのまま当てる） | 平滑後（tau=60 s） | 比 | 解析解 |
|---|---|---|---|---|
| **3.995 Hz** | ★ **5.009e-04** | 3.328e-07 | ★ **-63.6 dB** | -63.6 dB |
| **4.005 Hz** | ★ **4.997e-04** | 3.312e-07 | ★ **-63.6 dB** | -63.6 dB |
| 4.000 Hz ちょうど | 2.677e-06 | 1.788e-09 | — | — |

★ **実測が解析解と 0.1 dB で一致した。**

⚠️★★★ **初稿の主張は誤りだったので訂正した** —— 私は
「零次ホールドは 1 Hz の**整数倍に線スペクトルを持つ**ので、ちょうど 4 Hz に線が立つ」と書いたが、
**整数倍ちょうどは ZOH の sinc の零点**であり、**逆にエネルギーがほとんど無い**（実測 2.7e-06、
側帯波の 1/190）。**エネルギーが乗るのは整数倍の両脇 `k*1Hz ± f_signal`** である。
→ ★ **selftest がこの誤りを検出した**（初回実行で FAIL 3 件）。**書いた主張を検査するものを
同時に置いていたので気づけた**（`verify-before-claiming` ルール 6 の実例）。

### 6.5.4 ⚠️★★ 窓を掛けない DFT は**比較の符号を逆にする**（Step 6 への申し送り）

同じ信号の 4.0 Hz 成分:

| 測り方 | 階段 | 平滑後 | 結論 |
|---|---|---|---|
| **窓なし** | 1.86e-17 | 4.46e-05 | ✗ 「平滑化すると**増える**」という**誤結論** |
| **Hann 窓** | 2.68e-06 | 1.79e-09 | ★ -63.5 dB（解析解と一致） |

原因: 表現層の信号は低域に非常に強い成分を持つ（状態の波は 0.001-0.02 Hz）ため、
**窓を掛けないと低域からの漏れが -80 dB 帯を埋め尽くす**。
⚠️ **一様に周波数を刻んだ「帯域 RMS」も誤る**——階段のエネルギーは極めて細い線に集中しているので、
一様サンプリングは**そのほとんどを跨いでしまい**、帯域 RMS は逆に「平滑後のほうが +1.7 dB 高い」と出る。
→ ★★ **Step 6（音そのものの変調スペクトル）でも同じ罠がある。窓を掛け、線の位置で比べること。**

### 6.5.5 検算の結果（`expr_smooth.py --selftest`・21 検査）

| 検査 | 結果 |
|---|---|
| t=tau で 63.2% に到達（fps 30/60/240） | PASS（誤差 <= 2.6e-13） |
| ★ dt 不規則（1.0 / 2.691 s 混在）でも到達点が同じ | PASS（差 1.11e-16） |
| 4 Hz の減衰 <= -60 dB | PASS（**-63.6 dB**） |
| 0.5 / 20 / 70 Hz の減衰 <= -40 dB | PASS（-45.5 / -77.5 / -88.4 dB） |
| ★ 段差の低減 | PASS（**403 倍 = 52.1 dB**） |
| 1 フレームあたり最大変化 < 1e-3 | PASS（60 fps で 2.78e-04） |
| tau < 60 を拒否する | PASS |

★ **検査自体を壊れた実装で試した**（ルール 5b）——
**dt を無視する固定 alpha**（よくある実装ミス）を注入すると **FAIL 11 件 / exit 1**。
**検査は空回りしていない。**

## 6.9 ★★★ 実セッションでの検証（研究者提供の Phase1 データ・2026-08-11）

> ★ 研究者から Phase1 の実打鍵データの提供を受けた。**fixture が最大 14 秒しかなく
> tau=60 s の挙動を実データで確認できない**という穴（§6-3）が、これで埋まった。
> ⚠️ **P013 はタイピングゲームなので、課題内容ではなく「単に実打鍵データ」として扱う**（研究者指示）。
>
> ⚠️★★ **データの取り扱い**: 提供ディレクトリは 17 ファイル（`.age` 暗号化 14 / 平文 NDJSON 3）。
> **平文 3 本のみを使い、`.age` は復号していない。**
> ★ **リポジトリにコミットしていない**（`.gitignore` の `*.age` / `P[0-9]*_*.ndjson` が既に塞いでいる。
> `git check-ignore` で実測確認）。★ **外部 LLM（Codex）へは一切送っていない**（`data-privacy`）。
> 出力は全て scratchpad 配下。

### 6.9.1 replay は 3 本とも通る

| セッション | NDJSON 行数 | 期間 | `feat` 行 | `gse-replay` | snapshots |
|---|---|---|---|---|---|
| P010 (2026-06-29 提出分ではなく 07-21) | 7,350 | 39.4 分 | 2,416 | exit 0 | 480 |
| P011 | 12,768 | 28.7 分 | 1,909 | exit 0 | 350 |
| P013（タイピングゲーム） | 4,646 | 3.3 分 | 633 | exit 0 | 181 |

### 6.9.2 ★★★ 最大の発見 — **経過時間の 42–71% が「離席ギャップ」だった**

`snapshot_to_csv.py` の `dt_s` を集計した実測（閾値は production の
`intervention.rs:15 AWAY_IDLE_MS = 180_000` に接地）:

| セッション | 最大 dt | dt<=5s | 5s<dt<=180s | **dt>180s（離席）** | **経過に占める割合** |
|---|---|---|---|---|---|
| **P010** | ★★ **994 s** | 474 | 3 | **2 件・計 1749 s** | ★★★ **71%** |
| **P011** | 282 s | 334 | 12 | **3 件・計 788 s** | ★ **42%** |
| P013 | 15 s | 179 | 1 | 0 件 | 0% |

⚠️★★★ **fixture（最大ギャップ 2.691 s）からは絶対に見えない桁である。**

**そのままだと何が起きるか**（実測）:

```
$ expr_smooth.py P010.csv P010.smooth.csv --tau 60 --fps 60   # ギャップ分割なしの版
wrote ...: 147,329 frames @ 60.0 fps
→ うち 1749s * 60fps = 104,940 フレーム（71% / 16.5 MB）が **本人が居ない間の捏造フレーム**
```

→ ★ **S0-D11 で `max_gap_s`（既定 180 s）を超える間隔を segment 境界にした。**
実測: P010 は **147,329 → 42,391 フレーム**（16.5 MB → 4.9 MB）、segment 3 個。
**復帰時の段差は 8.08e-05 < 1e-03**（値を持ち越すのでオンセットを作らない）。

### 6.9.3 ★★ 本題 — tau=60 s は「危険を落とす」と「表現が残る」を両立するか

最長 segment（離席で切れていない連続区間）で測った:

| セッション | 区間 | 列 | raw の範囲 | 平滑後の範囲 | **レンジ保持** | **SD 保持** | **3.995 Hz** |
|---|---|---|---|---|---|---|---|
| P010 | 9.9 分 | `ewma_x` | [0.062, 1.000] | [0.228, 0.852] | **66.5%** | 59.2% | ★ **-63.5 dB** |
| P010 | 〃 | `ewma_y` | [0.000, 0.867] | [0.079, 0.713] | **73.0%** | 55.0% | ★ **-63.5 dB** |
| P010 | 〃 | `p_stuck` | [0.008, 0.921] | [0.031, 0.759] | **79.8%** | 63.0% | ★ **-63.5 dB** |
| P011 | 12.7 分 | `ewma_x` | [0.009, 0.547] | [0.047, 0.336] | 53.7% | 61.8% | ★ **-63.5 dB** |
| P011 | 〃 | `ewma_y` | [0.284, 0.937] | [0.485, 0.737] | 38.6% | 54.4% | ★ **-63.5 dB** |
| P011 | 〃 | `p_stuck` | [0.008, 0.511] | [0.009, 0.251] | 48.1% | 68.0% | ★ **-63.5 dB** |
| P013 | 3.3 分 | `ewma_x` | [0.000, 0.228] | [0.014, 0.137] | 54.2% | 45.6% | ★ **-63.5 dB** |
| P013 | 〃 | `ewma_y` | [0.323, 0.647] | [0.490, 0.717] | 70.1% | 42.1% | ★ **-63.5 dB** |

> ★★★ **両立している。**
> **(a) 危険側**: 4 Hz 近傍（3.995 Hz）の減衰は **実データでも -63.5 dB** で、
> **解析解 -63.6 dB・合成信号での実測とも一致した**（3 被験者 × 3 列すべてで同値）。
> **(b) 表現側**: **レンジの 39–80% / SD の 42–68% が残る。**
> → ★ **tau=60 s は「安全にしたら何も動かなくなる」形ではない。**
> **表現層に使える変動は十分に残る。**

⚠️ **P013 の `p_stuck` だけレンジ保持 148.7% と 100% を超えた**が、これは**私の比較窓の副作用**である——
先頭行（seed に使う値 0.0355）が**以降の範囲 [0.0095, 0.0253] の外**にあり、
平滑後の系列だけがその値から始まるため。**平滑器の欠陥ではない。**
★ なお P013 の `p_stuck` は範囲そのものが極めて狭い（0.009–0.025）——
**タイピングゲームなので「詰まり」がほぼ立たない**、と読める（⚠️ ただし本セッションでは
**単に実打鍵データとして扱う**方針なので、これ以上の解釈はしない）。

### 6.9.4 ⚠️ 実データでも変わらなかったこと

- **1 フレームあたり最大段差**: 3 セッションとも **1.9e-04 以下**（上限 1e-03 を大きく下回る）
- `snapshot_to_csv.py` / `expr_smooth.py` とも **3 本すべてで exit 0**

## 7. ★ 再現手順と、どの主張をどのスクリプトが再現するか

⚠️★ **1 本のスクリプトで全部が再現するわけではない**（レビュー指摘）。**主張ごとに担当を書く。**

```bash
# 往復の中核（28 検査）
bash .steering/20260811-expression-prototype-step0/scripts/step0-verify.sh

# 展開ツリーの text/binary 分類（§2.2 の 8,281 ファイル・95.5%）
python .steering/20260811-expression-prototype-step0/scripts/classify.py <name>.toe.dir

# 多世代往復＝不動点であること（§3.2）
bash .steering/20260811-expression-prototype-step0/scripts/gen_test.sh <workdir> <src.toe>

# 混入検査（§5 のユーザー名 / 絶対パス）
python .steering/20260811-expression-prototype-step0/scripts/leakcheck.py <name>.toe.dir

# 表現層の数値検算（51 検査。Step 1/2 の主張すべて）
python .steering/20260811-expression-prototype-step0/scripts/expr_smooth.py --selftest
```

| 主張 | 再現するもの |
|---|---|
| §1 終了コードの反転（成功=1 / 失敗=0） | `step0-verify.sh` §1 |
| §2.1 空 `.toe` の全ファイルがテキスト | `step0-verify.sh` §2 |
| §2.2 実プロジェクト 8,281 ファイル・95.5% がテキスト | `classify.py` |
| §3.1 素の往復でツリーが保存される | `step0-verify.sh` §3 |
| §3.2 多世代で不動点 | `gen_test.sh` |
| §4 編集（長さ変更を含む）が往復に耐える | `step0-verify.sh` §4 |
| §5 混入 0 件 | `leakcheck.py` |
| §5.5 TD GUI で開ける | ⚠️ **手動**（GUI 起動が要る。手順は S0-D4） |
| §6.5 の数値（-63.6 dB / 403 倍 / 段差 / ギャップ分割） | `expr_smooth.py --selftest` |

★ `experiments/` は起こしていない —— D18 / `design.md` §5 に従い、
Step 0 は「実験」ではなく**実機の事実確認**であるため。

### ★ 検査自体の 3 状態試験（`verify-before-claiming` ルール 5b）

| 状態 | 作り方 | 結果 |
|---|---|---|
| 正常 | そのまま | `step0-verify.sh` **28 PASS / exit 0** ／ `--selftest` **51 PASS / exit 0** |
| 不在 | `TD_ROOT=/c/nonexistent-touchdesigner` | **exit 1**（3 FAIL で中断） |
| 壊れている | 実バイナリ ＋ 中身が `not a toe` のテンプレート | **9 FAIL / exit 1** |
| 壊れている（Python 側） | **dt を無視する固定 alpha** を注入 | **11 FAIL / exit 1** |
