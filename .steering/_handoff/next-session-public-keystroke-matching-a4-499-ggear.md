# 次のセッション（G-GEAR）: 照合の論文 —— A4 の 499 人の版を集計する（逸脱 D3 の約束）

作成 2026-10-24（Mac・判断 79 の後）。**この作業は G-GEAR で行う。Mac では行わない。** 手順は Mac で書き、ブランチ `docs/public-keystroke-matching-manuscript` に push 済み。G-GEAR では、まずこのブランチを pull してから始める。

## 新しいセッションで最初に打ち込む文（G-GEAR で）

```
.steering/_handoff/next-session-public-keystroke-matching-a4-499-ggear.md を読んで、照合の論文の A4 の 499 人の版を集計して。
```

## なぜ要るか

notes.md の逸脱 D3 は「A4 の正答率は、CPU で生成した塊を含む全体と、その塊を含む書き手を除いた場合の両方を示す」と約束している。CPU で生成した塊は標本の 353 番目の書き手 1 人の 4 つだけで、除いた版は 499 人になる。書き手の ID は `raw/derived_a4_cpu_fallback_writers.json`（git に入らない）にある。

2026-10-24 に Mac でコードを読んだところ、`run_main.py` と `aggregate.py` には 1 人を除く集計が無い（`aggregate.reference_rows` は A4 のセルをそのまま返す）。`main_a4.json` は 500 人の版だけになる見込み。Mac の段 1（`next-session-public-keystroke-matching-manuscript-a4.md`）は、この 499 人の版が無ければ始めずに止まる。

## 0. 始める条件（この順で・飛ばさない）

1. `git fetch origin && git checkout docs/public-keystroke-matching-manuscript && git pull`（G-GEAR の worktree で）。
2. チェーンの `main_a4` の段が終了コード 0 で終わり、`results/main_a4.json` があること。まだ走っていれば待つ（止めない）。
3. **チェーンが次の段（`exploratory_unicity`・`exploratory_dp`・`main_all`）を走らせている間も、この作業はできる。ただし次の「やってはいけないこと」を守る。**

## やってはいけないこと（キャッシュの指紋）

`run_main.cache_fingerprint` は、`SEED`・`config.json`・このフォルダのコードのうち走行が読み込むもの（`run_main.py` を含み、`aggregate.py` を除く）・ライブラリの版・データの中身・A4 の復元の中身から作る（`scripts/run_main.py` の `cache_fingerprint`）。

- **`run_main.py`・`evaluate.py`・`matching.py` など、走行が読み込むファイルを変えない。** 変えると 500 人の段のキャッシュ（指紋の頭 `33fa95833296d7a5`）の指紋が変わり、全員の付録（`main_all`）がそれを使えなくなって、約 72 時間分を計算し直すことになる（D4）。走っている最中のチェーンの台本も書き換えない（2026-10-21 の code-reviewer HIGH）。
- `aggregate.py` は指紋の外だが、チェーンの `main_all` が後で読み込む。足すなら関数を足すだけにして、既存の関数の振る舞いを変えない。
- **新しい台本は別のファイルにする**（例 `scripts/a4_without_cpu_writer.py`）。`run_main.py` から読み込まれないので、指紋は変わらない。この台本の中で `cache_fingerprint` を呼ばない（呼ぶと、この台本自身がこのフォルダのモジュールとして指紋に入り、別の指紋になる）。A4 のキャッシュの場所は notes.md の記録（指紋の頭 `628d6e4e756e4b71`・`raw/derived/main_cache/` の下）を引数で渡す。

## 1. 何を出すか

- 出力: `results/main_a4_without_cpu_writer.json`（集計だけ・書き手ごとの値と ID を書かない）。
- 中身: A4 のセル（全文と窓・全部の形と N。`main_a4.json` の `main500.reference_A4` と同じ鍵と同じ量 —— 正答率・区間・$1/N$ の倍・副次の量）を、CPU の塊を含む書き手 1 人を除いた 499 人で計算したもの。
- A4 以外のセルは出さない（最も強い攻撃者は A4 を含まないので、499 人にする理由が無い）。

## 2. 実装案（Mac でコードを読んだ範囲・G-GEAR で実物を読んで確かめてから決める）

- `main_a4` の段の書き手ごとの結果は、キャッシュに 1 件ずつ pickle で残っている（D4）。新しい台本でそれを読み、標本の 500 人の件（窓を評価する件）から、`raw/derived_a4_cpu_fallback_writers.json` の書き手を除く。
- A4 のセルの集計は、`run_main.run` が `main500` について行っている手順（`aggregate.resamples` → セルの計算 → `aggregate.reference_rows`）をそのまま使う。関数を写して書き換えず、同じ関数を呼ぶ。
- 区間の抽出: 書き手が 499 人になるので、500 人の抽出の行列はそのまま使えない。`aggregate.resamples(seed, prompts, "<新しい名前>")` で、新しい名前（例 `main500_without_cpu_writer`）の抽出を作る（課題で層別・2,000 回）。使った名前を notes.md に書く。
- 確かめること:
  - 除く前の 500 人で同じ台本を回すと、`main_a4.json` の A4 のセルとバイト単位で（少なくとも全部の値が）一致すること。これが陽性対照になる。抽出の名前は `main500` を使う。
  - 除いた後の書き手の数が 499 で、除いたのが 1 人だけであること（数と標本の位置だけを印字し、ID は印字しない）。
- 自己検査と変異（`selftest_main.py` の作法）: 合成の結果で、(a) 除く書き手を指定しないと 500 人の値に一致する (b) 指定した 1 人が消える (c) 除く書き手が標本に無ければ止まる。変異ごとに赤を見る。
- レビュー: code-reviewer・security-checker・Codex（Codex には台本の diff だけ。記録・本文・書き手ごとの値・ID を送らない）。

## 3. 終わったら

- notes.md の D3 の節に、回した日時・コミット・出力の SHA-256・使った抽出の名前・陽性対照の結果を追記する。
- 出力を `results(experiment): ...` のコミットで freeze の枝に入れ、原稿の枝（`docs/public-keystroke-matching-manuscript`）へ merge する（7a515f81 と d3b7df70 と同じ形）。`main_a4.json` も同じ手順で入れる。
- push だけ。PR は出さない（G-GEAR の計算中は出さない）。
- Mac の段 1 はこの後に始める。

## 守ること

- A4 の復元の中身（生成した文）を開かない。キャッシュの中の書き手ごとの値・ID・本文を印字しない。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- 手順を変えたくなったら（例: 除き方・抽出の作り方）、変える前に研究者に AskUserQuestion で聞き、notes.md に書く。
- 応答は日本語。worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。
