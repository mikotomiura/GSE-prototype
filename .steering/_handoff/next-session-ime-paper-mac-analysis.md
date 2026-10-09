# 次セッション（Mac・macOS の計測機）— IME 論文: macOS の 2 セルの解析（問 1〜4・閉じた集合は逸脱 D8）・E3 の要約・SDK のヘッダの確認

> 作成: 2026-10-05（G-GEAR）。**新しい計測はしない。** 録り終えた macOS のデータ（この Mac の `~/ime-m4/`）を書庫にし、解析する。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 151・155・156**、
> `tasklist.md` の M4 の行、凍結した事前登録 `papers/ime-observation/experiment/preregistration.md`（§5・§6・§6.8・§6.10・§9）、
> `experiment/deviations.md` の **D6・D8**、`experiment/data.md`（寄託の手順）・`env.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（Mac の Claude Code に）

```
git fetch → origin/docs/ime-manuscript-outline から枝 docs/ime-m8-macos-analysis を切って作業する（PR は出さず push だけ。G-GEAR が論文の枝に取り込む）。
.steering/_handoff/next-session-ime-paper-mac-analysis.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 151・155・156、tasklist.md の M4、事前登録 §5・§6・§6.8・§6.10・§9、deviations.md の D6・D8、data.md の寄託の手順。
⚠️ 新しい計測はしない。解析は macOS のタグ（ime-observation-prereg-macos）の書き出し ~/ime-m4/export-ff122e32 から。凍結のコードと事前登録は変えない（D8 で kit/e2/closed_set.py だけを commit 14c85e6e のものに差し替えた写しを使う）。封印（sealed/）は開けない。生ログ・キーコードを外部の LLM に出さない。
⚠️ 判断の番号はこの Mac では 157〜160 を使う（Surface が 161〜164）。逸脱が要りそうなら止まって研究者に聞く（番号は D10 を使う・Surface が D11）。
⚠️ 結果を見てから命令・K・種・スイッチを変えない。失敗したら原因を 1 回だけ見て止まり、研究者に聞く。
⚠️ この Mac は CI の self-hosted runner を兼ねる（解析は時刻に依らないので止めなくてよい）。
Skill: verify-before-claiming・reproducibility-discipline・data-privacy（書庫）・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-05 夕・G-GEAR で確かめたこと）

- macOS は ON・OFF・E3 `idle`・E3 `working` とも測り終えた（M4・打ち切り 0）。生の run は `~/ime-m4/runs/`（`on-1`・`off-1`・`e3-working-run`）、書き出しは `~/ime-m4/export-ff122e32/`（一覧 `29b183ba…6c49`）。`run.json` の SHA-256: ON `0257755c…c268`・OFF `4ac581cb…f519`（全桁は `tasklist.md` の M4 の行か各 `run.json` から）。
- ⚠️ **まだ書庫にしていない**（`data.md` の Deposits と Machine の表は空・`- run_dir:` の行も無い）。
- ★ **D8**（研究者の選択 2026-10-05・判断 155）: 事前登録は S12 の試行を数えない（ON 2,925・OFF 2,700）が、凍結の `closed_set.py` はコーパスの句の S12 の試行（どの計画も 225 のうち 74）を残し、K = 100 でおとりが足りず止まる（Windows で実際に止まった）。→ `closed_set.py` に `--skip-scenario` を足した（commit **`14c85e6e`**・枝 `docs/ime-manuscript-outline`）。スイッチなしの出力は凍結のコードと同じ。G-GEAR で macOS の 2 計画をタグから再生成し、`c7a5469d…`・`3759ebf7…` と 225 / 74 を確かめた。
- 結果の表の道具 `papers/ime-observation/manuscript/tools/results_tables.py`（判断 156）は `experiment/results/` の上の段（macOS）と `results/windows/` を読む。

## §2 やること

1. **準備**: `git fetch` → `git switch -c docs/ime-m8-macos-analysis origin/docs/ime-manuscript-outline` → `git merge-base --is-ancestor 14c85e6e HEAD`。書き出しの一覧が `29b183ba…6c49` のままであることを確かめる（M4 と同じ手順）。
2. **書庫にする**（`data.md` の寄託の手順 4〜5）: 書き出しで、ON と OFF のそれぞれに
   ```
   python3 kit/analysis/pipeline.py --pack ~/ime-m4/runs/on-1 --out ~/ime-m4/deposit/macos-standard-live-on-1.zip --also-user <login> --also-home <home>
   python3 kit/analysis/pipeline.py --pack ~/ime-m4/runs/off-1 --out ~/ime-m4/deposit/macos-standard-live-off-1.zip --also-user <login> --also-home <home>
   ```
   exit 0 と表示された SHA-256 を `data.md` の Deposits の表（場所と日付は「未寄託」）と Machine の表（機械・`--also-user` / `--also-home` の値の数・日付。⚠️ 値そのものは書かない）に。⚠️ `e3-working-run` の観測ログを預けるかは未決（外枠の Open items）→ このセッションでは書庫にしない。
3. **展開と `run_dir` の行**: 書庫を `<repo>/papers/ime-observation/experiment/runs/macos-standard-live-on-1` と `…-off-1`（gitignore）に展開し、`run.json` の SHA-256 が上と一致することを確かめ、`data.md` に
   `- run_dir: runs/macos-standard-live-on-1  manifest_sha256: <64 桁>`（OFF も）を足す（`data.windows.md` の Windows の行と同じ形）。
4. **問 1〜3**（§5・`run.sh` の本番の命令と同じ）: 書き出しで
   ```
   python3 kit/analysis/pipeline.py --runs-from <repo>/papers/ime-observation/experiment/data.md --config experiment/config.json \
     --seed 20260929 --seed-file experiment/SEED --prereg experiment/preregistration.md \
     --out <repo>/papers/ime-observation/experiment/results
   ```
   exit 0・2 run・中止 0 を確かめる（`e1_detection.json`・`e1_l1.json`・`e1_l2.json`・`e1_delivery.json` が `results/` の上の段にできる・`results/windows/` は触らない）。⚠️ 既存のファイルは上書きされないので、失敗のやり直しは研究者に聞いてから。
5. **問 4 の開いた集合**（§6.8 の命令）: 書き出しで、ON は `--recipes kit/gen/recipes.json`、OFF は `--recipes kit/gen/recipes.macos-live-off.json`
   ```
   python3 kit/e2/open_set.py --obs <run>/obs.jsonl --plan <run>/plan.jsonl --corpus kit/corpus/data/phrases.jsonl \
     --recipes kit/gen/<procedure file> --split-seed 20260929 --seed 20260929 --eval-fraction 0.2 --split both --n 3 \
     --smoothing wb --beam 8 --length-info both --bootstrap 2000 --markers-in-obs \
     --out <repo>/papers/ime-observation/experiment/results/e2_open_set_<cell>.json
   ```
   （`<cell>` = `macos-standard-live-on` / `macos-standard-live-off`・`<run>` は §2 の 3 の展開先）。
6. **問 4 の閉じた集合（D8）**:
   ```
   cd ~/ime-m4 && cp -R export-ff122e32 export-d8
   git -C <repo> show 14c85e6e:papers/ime-observation/kit/e2/closed_set.py > export-d8/kit/e2/closed_set.py
   git -C <repo> diff ime-observation-prereg-macos 14c85e6e -- papers/ime-observation/kit/e2/closed_set.py   # 差が --skip-scenario と selftest と docstring だけ
   cd export-d8 && python3 kit/e2/closed_set.py --selftest   # selftest OK (157 checks)
   ```
   それから `export-d8` で、セルごとに（所要は 1 セル数十分〜1 時間余り・`nohup` で切り離す）
   ```
   python3 kit/e2/closed_set.py --obs <run>/obs.jsonl --plan <run>/plan.jsonl --corpus kit/corpus/data/phrases.jsonl \
     --recipes kit/gen/<procedure file> --config experiment/plan_config.macos.json \
     --K 10,100,1000 --seed 20260929 --bootstrap 2000 --markers-in-obs --skip-scenario S12 \
     --out <repo>/papers/ime-observation/experiment/results/e2_closed_set_<cell>.json
   ```
   確かめる: exit 0・`skipped_scenarios` が `{"S12": 225}`・`n_trials` が ON 3,150 / OFF 2,925・各 K と各特徴量の `n` が ON 2,925 / OFF 2,700（採点されないブロックがあれば `alignment` の数を記録）・`n_skipped` 0。⚠️ 推奨（§6.8 の判定）は読むだけで書かない（結果の節で G-GEAR が書く）。
7. **E3 の要約ファイル**（§6.10・`notes.md` の表の名前）: `samples.tsv` の SHA-256 が `tasklist.md` の M4 の記録（idle `f2fc37ef…`・working `32fb0782…`）と一致することを確かめ、書き出しで
   `python3 kit/e3/summarize_e3.py idle=<idle>/samples.tsv working=<working>/samples.tsv > <repo>/papers/ime-observation/experiment/results/e3_macos.txt`。両方 `status: measured`。
8. **SDK のヘッダ**（外枠の Open items・判断 151・153）: macOS 27.0.1 の SDK（`xcrun --show-sdk-path`・その版を記録）で、(a) AppKit の `NSAccessibilityConstants.h` の属性・パラメータ付き属性・通知の数（文書の JSON では 131・18・42）と `NSAccessibilityTextInputMarkedRangeAttribute`・`NSAccessibilityTextInputMarkingSessionBeganNotification` / `…EndedNotification` の有無、(b) C の `AXAttributeConstants.h`・`AXNotificationConstants.h` の数（文書では 101・9・25）と marked text を表す定数が無いこと、(c) `TextInputSources.h` を読み、11.3 の写しで読んだこと（入力ソースと入力モードだけ）が変わっていないか。数え方（何を 1 つと数えたか・grep の式）も記録する。→ `decisions.md` に。原稿の文は G-GEAR が直す。
9. **結果の表を生成し直す**: `<repo>/papers/ime-observation` で `python3 manuscript/tools/results_tables.py --results experiment/results --out manuscript/generated` → `--check` が緑。macOS の 2 セルが `values.json` の `cells` に入ること。
10. **記録と push**: `data.md`（Deposits・Machine・`run_dir`・問 1〜5 の命令と exit と出力の SHA-256・`closed_set.py` は `14c85e6e`）、`decisions.md` に判断 157〜。`git add` はパス指定で、`experiment/results/e1_*.json`・`experiment/results/e2_*_macos-standard-live-*.json`・`experiment/results/e3_macos.txt`・`experiment/data.md`・`manuscript/generated/*`・`decisions.md` だけ。⚠️ `experiment/runs/`・`~/ime-m4/deposit/` は git に入れない。push して G-GEAR に知らせる（PR は出さない）。
11. ⚠️ 寄託（OSF）は研究者の作業。書庫は `~/ime-m4/deposit/` に置いたまま。

## §3 気をつけること

- ⚠️ macOS の解析は Windows のタグから回さない（逆も）。手順のファイルの SHA-256 がタグで違い、`closed_set.py` は計画の `recipes_sha256` と照合して止まる。
- ⚠️ `.codex/budget.json` は台帳（触らない）。
- ⚠️ 番号の割り当て（2026-10-05）: 判断は Mac 157〜160・Surface 161〜164・G-GEAR 165〜。逸脱は Mac D10・Surface D11・G-GEAR D12〜（使わなかった番号は欠番のままにする）。
