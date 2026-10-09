# 次セッション（Surface Pro 8・Windows の計測機）— IME 論文: Windows のセルの閉じた集合（逸脱 D8）と E3 の要約

> 作成: 2026-10-05（G-GEAR）。**新しい計測はしない。** 録り終えた Windows のデータ（この Surface の `~/ime-m7/`）の解析の残りだけを回す。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 155・156**、
> 凍結した事前登録 `papers/ime-observation/experiment/preregistration.md`（§6.8・§10.7・§10.9）、`experiment/deviations.md` の **D8**、
> `experiment/data.windows.md`、前の引き継ぎ `next-session-ime-paper-m7-windows.md` §2.11。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（Surface の Claude Code に）

```
git fetch → origin/docs/ime-manuscript-outline から枝 docs/ime-m8-windows-closed-set を切って作業する（PR は出さず push だけ。G-GEAR が論文の枝に取り込む）。
.steering/_handoff/next-session-ime-paper-surface-d8.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 155・156、事前登録 §6.8・§10.7・§10.9、deviations.md の D8、data.windows.md。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない（D8 で kit/e2/closed_set.py だけを commit 14c85e6e のものに差し替える）。封印（sealed/）は開けない。生ログ・キーコードを外部の LLM に出さない。
⚠️ 長い処理は Claude Code のバックグラウンドのタスクにしない（この機械はメモリ不足で shell が止められた・D7）。PowerShell の Start-Process で独立したプロセスにする。
⚠️ 判断の番号はこの Surface では 161〜164 を使う（Mac が 157〜160）。逸脱が要りそうなら止まって研究者に聞く（番号は D11 を使う・Mac が D10）。
⚠️ この機械の注意: 作業コピーは core.autocrlf=true。凍結の書き出し（~/ime-m7/export・LF）から回す。python3 は Store のスタブ → ~/ime-pilot/bin を PATH の先頭か python を使う。Codex CLI は無い。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。git show <ref>:<path> は MSYS_NO_PATHCONV=1 を付ける。
```

## §1 状態（2026-10-05 夕・G-GEAR で確かめたこと）

- Windows のセルは測り終えて解析済み（問 1〜3・問 4 の開いた集合: `experiment/results/windows/`・PR #304）。残りは **問 4 の閉じた集合** と **問 5 の要約ファイル**。
- ★ **D8**（研究者の選択 2026-10-05・判断 155）: 事前登録は S12 の試行を数えない（Windows は 2,700 試行）が、凍結の `closed_set.py` はコーパスの句の S12 の試行（74）を残し、K = 100 でおとりが足りず止まった。→ `closed_set.py` に `--skip-scenario` を足した（commit **`14c85e6e`**・枝 `docs/ime-manuscript-outline`）。スイッチなしの出力は凍結のコードと同じ。G-GEAR で Windows の計画をタグから再生成し、SHA-256 `b7bdf8fc…36b0` と 225 / 74 を確かめた。
- 解析に使うもの（この Surface）: 書き出し `~/ime-m7/export`（タグ `ime-observation-prereg-windows`・108 ファイル・一覧 `f61af353…87b7`）、run の展開 `<repo>/papers/ime-observation/experiment/runs/windows-msime-tsf-2`（書庫 `f2287a74…cd06`・`run.json` `5c74a1fa…3d82`）、E3 の `~/ime-m7/runs/e3-idle`・`~/ime-m7/runs/e3-working`（場所は着手時に確かめる）。

## §2 やること

1. **準備**: `git fetch` → `git switch -c docs/ime-m8-windows-closed-set origin/docs/ime-manuscript-outline` → `git merge-base --is-ancestor 14c85e6e HEAD` が exit 0。⚠️ 作業コピーに未コミットの変更があれば先に見る（`experiment/runs/` は gitignore なので枝を替えても残る）。
2. **D8 の `closed_set.py` を書き出しの写しに入れる**（書き出しそのものは変えない）:
   ```
   cd ~/ime-m7
   cp -r export export-d8
   MSYS_NO_PATHCONV=1 git -C <repo> show 14c85e6e:papers/ime-observation/kit/e2/closed_set.py > export-d8/kit/e2/closed_set.py
   MSYS_NO_PATHCONV=1 git -C <repo> diff ime-observation-prereg-windows 14c85e6e -- papers/ime-observation/kit/e2/closed_set.py   # 差が --skip-scenario と selftest と docstring だけであることを目で確かめる
   cd export-d8 && python kit/e2/closed_set.py --selftest   # selftest OK (157 checks)
   ```
   ⚠️ `export-d8/kit/e2/closed_set.py` が LF のままであること（`grep -c $'\r'` が 0）。
3. **入力の照合**: `<run>` = `<repo>/papers/ime-observation/experiment/runs/windows-msime-tsf-2` で `sha256sum <run>/plan.jsonl <run>/obs.jsonl` が
   `b7bdf8fc120036f18ceff53d2bf8def43ef11a818a119bc24b0c7f4fbc4836b0`（計画・§10.6）と `58f0bda61fa4310c58a643bb605a68c360f34378b651a3b85d58290fabcd2562`（観測・`results/windows/e1_detection.json` の `runs.list[0].logs_sha256.obs`）。違えば止まる。
4. **閉じた集合を回す**（§6.8 の命令・§10.7 の Windows の差し替え・D8 のスイッチ。所要の目安は数十分〜1 時間余り・`Start-Process` で独立に）: 作業ディレクトリ `~/ime-m7/export-d8` で
   ```
   python kit/e2/closed_set.py --obs <run>/obs.jsonl --plan <run>/plan.jsonl --corpus kit/corpus/data/phrases.jsonl \
     --recipes kit/gen/recipes.json --config experiment/plan_config.windows.json \
     --K 10,100,1000 --seed 20260929 --bootstrap 2000 --markers-in-obs --skip-scenario S12 \
     --out <repo>/papers/ime-observation/experiment/results/windows/e2_closed_set_windows-msime-tsf.json
   ```
   標準出力と標準エラーは `~/ime-m7/runs/closed-set.out` / `.err` へ。⚠️ `--out` は既存のファイルを上書きしない（無いことを先に確かめる）。
5. **出力を確かめる**: exit 0・`skipped_scenarios` が `{"S12": 225}`・`n_trials` が 2,925・各 K と各特徴量の `n` が 2,700（全ブロックが採点されたとき。採点されないブロックがあれば `alignment` の数を記録）・`n_skipped` が 0。チャンスとの比較（判定の規則 §6.8）は読むだけで、ここでは書かない（結果の節で G-GEAR が書く）。
6. **E3 の要約ファイル**（§10.9・`notes.md` の表の名前）: `samples.tsv` の SHA-256 が idle `43ab3b39…5f59`・working `638da0ea…f88f` であることを確かめてから、書き出しで
   `python kit/e3/summarize_e3.py idle=<idle>/samples.tsv working=<working>/samples.tsv > <repo>/papers/ime-observation/experiment/results/windows/e3_windows.txt`。両方 `status: measured`・working の `cpu_all_zero: false` を確かめる（M7 の記録と同じ値になるはず）。
7. **前の引き継ぎの残り（§2 の 5）**: (a) Windows の試み 2（2026-10-04 01:57〜13:03 JST）の間に計測機で何が動いていたか（タスクスケジューラ・Windows Update の履歴・Claude Code のセッション・Defender の走査など、記録で分かる範囲）→ `data.windows.md` に 1 段落。(b) `data.windows.md` の §10.8 の点検の計画の SHA-256 を全桁に（点検の run の manifest から）。
8. **記録と push**: `data.windows.md` に閉じた集合と E3 の行（命令・exit・出力の SHA-256・`closed_set.py` は `14c85e6e` のもの）、`decisions.md` に判断 161〜（このセッションの選択）。`git add` はパス指定で、`results/windows/e2_closed_set_windows-msime-tsf.json`・`results/windows/e3_windows.txt`・`data.windows.md`・`decisions.md` だけ。⚠️ `experiment/runs/` は gitignore（入れない）。push して G-GEAR に知らせる（PR は出さない）。
9. ⚠️ 寄託（OSF）は研究者の作業のまま。`--pack` の書庫は `~/ime-m7/deposit/` にある。

## §3 気をつけること

- ⚠️ 閉じた集合の結果を見てから命令・K・種・スイッチを変えない（D8 以外の変更は逸脱になる）。
- ⚠️ 失敗したら原因を 1 回だけ見て止まり、研究者に聞く（再実行で通るまで回さない）。
- ⚠️ `.codex/budget.json` は台帳（触らない）。
- ⚠️ 番号の割り当て（2026-10-05）: 判断は Mac 157〜160・Surface 161〜164・G-GEAR 165〜。逸脱は Mac D10・Surface D11・G-GEAR D12〜（使わなかった番号は欠番のままにする）。
