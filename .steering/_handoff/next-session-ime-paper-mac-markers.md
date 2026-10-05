# 次セッション（Mac）— IME 論文: macOS の 2 セルの印の時刻（§6.9）を計算して記録する

> 作成: 2026-10-05 夜（G-GEAR）。Windows のセルは G-GEAR で済んだ（判断 171・`data.windows.md` の「Marker times of section 6.9」）。
> macOS の run のデータは Mac にしか無い（`experiment/runs/macos-standard-live-{on,off}-1`・gitignore・判断 159）ので、ここだけ Mac で行う。
> ⚠️ **このメモを一次資料にしない。** 一次は `decisions.md` の**判断 171**（Windows で行った手順）、`kit/pilot/README.md` の `clock_sync.py` の節、
> 事前登録 §6.9、`data.md`・`data.windows.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（Mac）

```
git fetch → PR #306（docs/ime-manuscript-outline）が merge 済みなら main から、まだなら origin/docs/ime-manuscript-outline から、
枝 docs/ime-macos-marker-times を切って作業する。
.steering/_handoff/next-session-ime-paper-mac-markers.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 171、kit/pilot/README.md（clock_sync.py の節）、事前登録 §6.9、data.windows.md の「Marker times of section 6.9」。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。封印（sealed/）は開けない。experiment/runs/ の中は変えない（obs.jsonl は repo の外の写しを使う）。生ログ・キーコードを原稿や外部の LLM に出さない。
⚠️ 印の時刻の値は出力を読む前に仕様を決め、出したら規則を変えない。値は画面に出さない（形と数だけ見る）。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・内部の番号（判断・M・issue）を書かない。_style_check.py を回す。
⚠️ 判断の番号は Mac が 177〜179 を使う（G-GEAR の次のセッションは 180〜）。逸脱は作らない（登録の手順どおり）。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。git show <ref>:<path> は MSYS_NO_PATHCONV=1 は不要（macOS）。
```

## §1 状態

- 道具 `manuscript/tools/results_tables.py` は `results/clock_sync_<cell>.json` があれば読み、無ければ表 7 に「not computed」と出す（判断 171）。本文の `\rv{macos-standard-live-{on,off}.markers.obsgt.{median,range}}` は今は生成されていない（`build.sh` の「result values not generated: 4」）。
- 印は計画の設定 `plan_config.macos.json` の `marker`（left, right, left, right）。macOS のキーコードは left = 123・right = 124（`kit/pilot/README.md` の例）。

## §2 やること

1. **入力を確かめる**: `experiment/runs/macos-standard-live-on-1` と `-off-1` の `run.json` の SHA-256 が `data.md` の `run_dir` の行（on `0257755c…`・off `4ac581cb…`）と一致し、`oracle.jsonl`・`gt.jsonl`・`obs.jsonl` が run の manifest の SHA-256 と一致すること。
2. **道具はタグから**: `git -c core.autocrlf=false archive ime-observation-prereg-macos papers/ime-observation/kit/pilot papers/ime-observation/kit/formats | tar -x -C <repo の外>` （★ `kit/formats` が無いと `seal_obs.py --selftest` が検証器の不在で 1 件赤・判断 177）→ `clock_sync.py --selftest`・`seal_obs.py --selftest` が緑。今の commit とタグで 2 つのファイルに差が無いことも `git diff ime-observation-prereg-macos HEAD -- <2 files>` で確かめる。
3. **キーの行だけの写し**: `obs.jsonl` を repo の外へ写し、`seal_obs.py --obs <写し>/obs.jsonl --keys-out <写し>/obs.keys.jsonl --sealed-dir <写し>/sealed`（元の run は触らない）。`obs.keys.jsonl` の SHA-256 を記録する。
4. **印の仕様**（出力を読む前に固定・Windows と同じ形）: `{"oracle_keys": ["left", "right", "left", "right"], "gt_vks": [123, 124, 123, 124], "obs_categories": ["navigation", "navigation", "navigation", "navigation"], "max_gap_ms": 300}`（1 行・SHA-256 を記録）。窓は既定の 3,000 ms。
5. **実行**（セルごと）: `python3 <タグ>/kit/pilot/clock_sync.py --oracle <run>/oracle.jsonl --gt <run>/gt.jsonl --obs-keys <写し>/obs.keys.jsonl --marker <仕様> --out experiment/results/clock_sync_<cell>.json`（cell = `macos-standard-live-on` / `macos-standard-live-off`）。exit 0・**2 回目とバイト一致**・出力にパス・ホスト名・ログイン名が無いこと・LF。形だけ見る（`oracle.blocks`・`with_marker`・`gt.matched`・`obs.matched` の数・`missing`）。⚠️ ON は持ち越し（carry-over）のあるブロックで参照の側の印が見つからないことがある（README の注）—— それは `missing` に出るのが正しい。
6. **記録**: `experiment/data.md` に節「Marker times of section 6.9」（`data.windows.md` の同じ節の形・命令・入力と出力の SHA-256・見つかったブロックの数）。`manuscript/outline.md` の Open items の macOS の印の時刻を「Done on …」に直す。
7. **生成し直す**: `python3 manuscript/tools/results_tables.py --selftest`（109 件）→ `--results experiment/results --out manuscript/generated` → `--check` 一致。`values.json` に `macos-standard-live-{on,off}.markers.*` が入り、本文の生成されていない値が 0 になるはず（LaTeX が Mac に無ければ組版は G-GEAR に任せる）。文体の検査 `python3 .steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py papers/ime-observation` が違反 0。
8. **判断 177** を `decisions.md` に（Windows の判断 171 の形）。`tasklist.md` の「Mac で: macOS の 2 セルの印の時刻」に ✓。
9. **出荷**: 完了時レビューは code-reviewer ∥ security-checker（コードの変更が無ければ記録と結果のファイルだけを見る）。`/cross-review` は送るコードが無ければ省略し、理由を完了報告に書く。→ git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI）。

## §3 気をつけること

- ⚠️ `seal_obs.py` は元のファイルを封印の場所へ**移す**。必ず repo の外の写しに対して使う。
- ⚠️ 結果の JSON・記録に Mac のホームのパスを書かない（`<run>`・`<results>` のように書く）。
- ⚠️ zsh で `PIPESTATUS` が空だったことがある（判断 159）→ exit の確かめは別の命令で。
