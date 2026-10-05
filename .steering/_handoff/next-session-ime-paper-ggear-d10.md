# 次セッション（G-GEAR）— IME 論文: Windows のセルの直した解析（逸脱 D10）を G-GEAR で回す → 結果の節へ

> ✅ **2026-10-05 午後に実施済み（判断 166）**。寄託先は判断 167（データ = Zenodo・コード = GitHub）。続きは `next-session-ime-paper-results-2.md` §5。

> 作成: 2026-10-05 午後（G-GEAR）。研究者の提案で、Surface の代わりに **G-GEAR で** Windows の D10 を回す
> （`next-session-ime-paper-surface-d10.md` は使わない・手順はそれを G-GEAR 向けに直したもの）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 157・165**、
> `experiment/deviations.md` の **D10**、事前登録 §10.7、`experiment/data.windows.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 枝 docs/ime-manuscript-outline（origin と一致していること）で作業する。
.steering/_handoff/next-session-ime-paper-ggear-d10.md を読んで §2 を上から実行してください。終わったら .steering/_handoff/next-session-ime-paper-results-2.md（§4 の追記を含む）に進む。
一次は decisions.md の判断 157・165、deviations.md の D10、事前登録 §10.7、data.windows.md。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない（D10 で kit/analysis/match.py だけを commit 115cd5ff のものに差し替えた書き出しの写しを使う）。封印（sealed/）は開けない。生ログ・キーコードを原稿や外部の LLM に出さない。experiment/runs/ は git に入れない。
⚠️ 結果を見てから命令・種・設定を変えない。失敗したら原因を 1 回だけ見て止まり、研究者に聞く。
⚠️ 判断の次の番号は 166（Surface の 162〜164 は欠番のまま）、逸脱の次は D12。公開物（data.windows.md）に内部の番号（判断・M・issue）を書かない。_style_check.py を回す。
⚠️ 長い解析は Claude Code のバックグラウンドで回してよいが、G-GEAR は Windows の CI の self-hosted runner でもある（解析は時刻に依らない）。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。heredoc にバックスラッシュを含めない（Write / Edit）。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
```

## §1 状態（2026-10-05 午後・このセッションで確かめたこと）

- 研究者が Surface の書庫を G-GEAR に写した: `C:\Users\johnd\Downloads\windows-msime-tsf-2.zip`（55,165,625 B）。
  ✅ SHA-256 **`f2287a7494b108a7b827f96da48f523e84e1a9478121d03fa82dca2c8749cd06`**（`data.windows.md` の Deposits と一致）・中身は `run.json`・`plan.jsonl`・`oracle.jsonl`・`gt.jsonl`・`obs.jsonl` の 5 つ。
- ✅ `C:\GSE-prototype\papers\ime-observation\experiment\runs\windows-msime-tsf-2\` に展開済み（gitignore を確かめた）。`run.json` `5c74a1fa…3d82`（`data.windows.md` の `run_dir` の行と一致）・`plan.jsonl` `b7bdf8fc…36b0`（§10.6）・`obs.jsonl` `58f0bda6…2562`（`results/windows/e1_detection.json` の記録と一致）。→ `data.windows.md` の `- run_dir: runs/windows-msime-tsf-2` の行がそのまま使える。
- G-GEAR の Python は **3.11.9**（Surface の登録の解析と同じ）。`core.autocrlf` は `input`。
- `match.py` は macOS と Windows の 2 つのタグでバイト一致、`115cd5ff` が変えたのは `match.py` だけ（判断 165）。

## §2 やること

1. **Windows のタグの書き出し**（LF）: `git -c core.autocrlf=false worktree add --detach <scratch>/wt-win ime-observation-prereg-windows` → その中で `export.internal.py --allow-missing-license`（M7 と同じ手順・場所と引数は `kit/export/` の README か docstring で確かめる）→ 一覧の SHA-256 が **`f61af353301e1370ac27c4a7425e8c2eb32991df9f7a2a765a26948da87787b7`**（108 ファイル）と一致すること。
2. **写しに D10 の `match.py`**: 書き出しを `export-d10` に写し、`MSYS_NO_PATHCONV=1 git show 115cd5ff:papers/ime-observation/kit/analysis/match.py > export-d10/kit/analysis/match.py`。`git diff ime-observation-prereg-windows 115cd5ff -- papers/ime-observation/kit/analysis/match.py` の差が D10（防御・スイッチ・selftest）だけ。`python kit/analysis/match.py --selftest`・`python kit/analysis/pipeline.py --selftest`。LF のまま（Python で CR を数えて 0）。
3. **登録の解析の再現**（環境変数なし・出力は一時の場所）: `export-d10` で
   ```
   python kit/analysis/pipeline.py --runs-from C:/GSE-prototype/papers/ime-observation/experiment/data.windows.md \
     --config experiment/config.json --seed 20260929 --seed-file experiment/SEED --prereg experiment/preregistration.md \
     --out <scratch>/check-registered
   ```
   → 4 ファイルが `experiment/results/windows/e1_*.json` と**バイト一致**すること（Surface と G-GEAR・同じ Python 3.11.9 での再現も兼ねる）。一致しなければ止まって研究者に聞く。
4. **D10 の直した解析**: 同じ命令に環境変数 `IME_MATCH_MERGE_RECOUNT=obs`、`--out C:/GSE-prototype/papers/ime-observation/experiment/results/d10/windows`（無い場所）。exit 0・1 run・中止 0・`e1_detection.json` の `config` に `merge_recount: obs`（数を記録）。
5. **D10 の主張の突き合わせ**: 直した解析と登録の `e1_detection.json` で、主の範囲（`windows_def`・`gt_obs`・`under_limit`）と全試行の層ごとの `recall`・`precision`・`split_rate` が同じで、違うのは `merge_rate` だけ。`e1_delivery.json` は同じバイト。macOS の `results/d10/macos/` と同じ形であること。
6. **記録と push**: `data.windows.md` に「Analysis under deviation D10」の節（G-GEAR で回したこと・書庫の SHA-256 で照合したこと・命令・環境変数・exit・出力 4 ファイルの SHA-256・`match.py` は `115cd5ff`・手順 3 のバイト一致）。`decisions.md` に判断 166。`next-session-ime-paper-surface-d10.md` の冒頭に「G-GEAR で実施済み・使わない」と 1 行。`git add` はパス指定で `experiment/results/d10/windows/e1_*.json`・`data.windows.md`・`decisions.md`・その引き継ぎだけ。push（PR は結果の節の後・判断 155-3）。
7. 書庫 `Downloads\windows-msime-tsf-2.zip` は消さずに置く（寄託は研究者・`~/ime-m7/deposit/` の元と同じ SHA）。
8. 続き: `next-session-ime-paper-results-2.md` §2 の 2（道具を広げる: 閉じた集合と推奨・E3・届き方・L2・開いた集合・**D10 の併合の率の登録と直した解析の並べ**）→ §2 の 3（結果の節）。
