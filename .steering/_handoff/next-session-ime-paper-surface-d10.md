# 次セッション（Surface Pro 8・Windows の計測機）— IME 論文: Windows のセルの直した解析（逸脱 D10）

> 作成: 2026-10-05（G-GEAR）。**新しい計測はしない。** Windows の問 1〜3 を、D10 の直した数え方でもう一度回すだけ。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 157・165**、
> `experiment/deviations.md` の **D10**、事前登録 §10.7、`experiment/data.windows.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（Surface の Claude Code に）

```
git fetch → origin/docs/ime-manuscript-outline から枝 docs/ime-m8-windows-d10 を切って作業する（PR は出さず push だけ。G-GEAR が論文の枝に取り込む）。
.steering/_handoff/next-session-ime-paper-surface-d10.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 157・165、deviations.md の D10、事前登録 §10.7、data.windows.md。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない（D10 で kit/analysis/match.py だけを commit 115cd5ff のものに差し替えた写しを使う）。封印（sealed/）は開けない。生ログ・キーコードを外部の LLM に出さない。
⚠️ 長い処理は Claude Code のバックグラウンドのタスクにしない（PowerShell の Start-Process で独立に）。
⚠️ 判断の番号はこの Surface では 162〜164（161 は使用済み）。逸脱が要りそうなら止まって研究者に聞く（D11）。結果を見てから命令や設定を変えない。
⚠️ この機械の注意: 作業コピーは core.autocrlf=true。書き出し（~/ime-m7/export・LF）の写しから回す。python3 は Store のスタブ → python。PowerShell の -File は cygpath -w、git -C は C:/... の形。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
```

## §1 状態（2026-10-05 午後・G-GEAR で確かめたこと）

- Mac が macOS の解析で凍結の `match.py` の欠陥に当たった（θ の数え直しの併合を、分母〔対の正解の層〕と違う層に数え、分子が分母を超えて止まる）。研究者の選択で **D10**（判断 157）: (1) 分子 > 分母の割合は値なし（登録の解析）、(2) 環境変数 `IME_MATCH_MERGE_RECOUNT=obs` で数え直した併合を対の観測の層に数える（直した解析）。両方を報告する。コードは commit **`115cd5ff`**（`kit/analysis/match.py` だけ）。
- Windows の登録の結果（`experiment/results/windows/e1_*.json`）は凍結の `match.py` で回した。Windows には予測の層が無く止まらなかったので、(1) の防御は働かない（分子 > 分母が 1 つでもあれば凍結のコードは止まっていた）。
- ★ `match.py` は macOS と Windows の 2 つのタグでバイト一致（G-GEAR で `git diff` が空）。`115cd5ff` を Windows のタグの書き出しに入れてよい。
- 足りないのは **Windows の (2)**（`experiment/results/d10/windows/`）。macOS の (2) は `results/d10/macos/` にある。

## §2 やること

1. **準備**: `git fetch` → `git switch -c docs/ime-m8-windows-d10 origin/docs/ime-manuscript-outline` → `git merge-base --is-ancestor 115cd5ff HEAD` が exit 0。
2. **D10 の `match.py` を書き出しの写しに入れる**（書き出しそのものは変えない）:
   ```
   cd ~/ime-m7 && cp -r export export-d10
   MSYS_NO_PATHCONV=1 git -C C:/<repo> show 115cd5ff:papers/ime-observation/kit/analysis/match.py > export-d10/kit/analysis/match.py
   MSYS_NO_PATHCONV=1 git -C C:/<repo> diff ime-observation-prereg-windows 115cd5ff -- papers/ime-observation/kit/analysis/match.py   # 差が D10 の防御・スイッチ・selftest だけ
   cd export-d10 && python kit/analysis/match.py --selftest && python kit/analysis/pipeline.py --selftest
   ```
   `match.py` が LF のまま（Python で CR を数えて 0）。
3. **(2) 直した解析**（§10.7 の命令・出力だけ別の場所・環境変数つき・`Start-Process` で独立に）: PowerShell で `$env:IME_MATCH_MERGE_RECOUNT = 'obs'` を設定してから、作業ディレクトリ `~/ime-m7/export-d10` で
   ```
   python kit/analysis/pipeline.py --runs-from C:/<repo>/papers/ime-observation/experiment/data.windows.md --config experiment/config.json \
     --seed 20260929 --seed-file experiment/SEED --prereg experiment/preregistration.md \
     --out C:/<repo>/papers/ime-observation/experiment/results/d10/windows
   ```
   確かめる: exit 0・1 run・中止 0・`e1_detection.json` の `config` に `merge_recount: obs`（数を記録）。
4. **(1) 登録の解析が変わらないことの確かめ**（推奨・同じ写しで環境変数なし・出力は一時の場所 `~/ime-m7/check-d10-registered`）: 同じ命令から `IME_MATCH_MERGE_RECOUNT` を外して回し、4 つのファイルが `experiment/results/windows/e1_*.json` と**バイト一致**することを確かめる（一致しなければ止まって研究者に聞く）。一時の出力は commit しない。
5. **D10 の主張の確かめ**: (2) と登録の `e1_detection.json` で、主の範囲（`windows_def`・`gt_obs`・`under_limit`）の層ごとの `recall`・`precision`・`split_rate` が同じで、違うのは `merge_rate` だけであること（Python で突き合わせて数を記録）。`e1_delivery.json` は両方で同じバイトのはず。
6. **記録と push**: `data.windows.md` に「Analysis under deviation D10」の節（命令・環境変数・exit・出力 4 ファイルの SHA-256・`match.py` は `115cd5ff`・(1) のバイト一致の結果）、`decisions.md` に判断 162〜。`git add` はパス指定で `experiment/results/d10/windows/e1_*.json`・`experiment/data.windows.md`・`decisions.md` だけ。push して G-GEAR に知らせる（PR は出さない）。⚠️ 公開物（`data.windows.md`）に内部の番号（判断・M・issue）を書かない（前回「the record of M7」が文体検査で赤になった）。

## §3 気をつけること

- ⚠️ 結果を見てから命令・種・設定を変えない。失敗したら原因を 1 回だけ見て止まり、研究者に聞く。
- ⚠️ `--out` の場所が既にあると上書きしない作りかもしれない（無い場所を指す）。
- ⚠️ `.codex/budget.json` は台帳（触らない）。
