# Mac での作業（v2）: 凍結した D7 の読みの基準で実データを読む

> 作成: 2026-11-27（Mac のセッション）。worktree は `~/GSE-prototype-weight-eye`、枝は `exp/gse-per-person-weight-eye`。v2 の実験は `experiments/20261126-per-person-weight-eye-v2/`。
> 一次資料: v2 の `conditions.md` の「追記 1: D7 実データの読みの基準」（凍結 b0f5821a・判断 52）、v2 の差分の節、v1 の `conditions.md`（D1〜D3・D6）。ここに書くのは順番と止める所だけで、計算と文は追記 1 に従う。

## 入口の文（Mac の Claude Code に）

```
~/GSE-prototype-weight-eye の .steering/20261122-per-person-weight-eye/handoff-mac-v2-realdata.md を読んで、その手順を行って。
```

## ここまでの状態

- D6: 選んだ案 E1 の門はすべて通り、12 の判定で 8 つ拾った（判断 50）。/cross-review で結果を変える誤りは無かった（判断 51）。
- D7 の追記 1 は attack-me（round 1 major → 2 minor → 3 minor）で直してから凍結した（判断 52・b0f5821a・push 済み）。
- 実データ（CoAuthor・CS1）は、どの版でもまだ読んでいない。

## 手順

### 1. 凍結を確かめる

```bash
cd ~/GSE-prototype-weight-eye && git pull --ff-only && git log --oneline -3
git log -1 --format=%H b0f5821a   # 凍結のコミット
git diff b0f5821a -- experiments/20261126-per-person-weight-eye-v2/conditions.md   # 空であること
```

- 追記 1 が凍結の後に変わっていたら止めて研究者に返す。

### 2. 読み込みのコードを書く（実データを開く前）

- 置き場: v2 の `scripts/` に新しいスクリプト（例 `realdata.py`）と、run.sh に段（例 `realdata`）を足す。合成の `eye.py`・`run_eye.py` の関数（`count_writers`・`a_idx`・`b_idx`・`cell_tables`・`equalize`・`draw_perms`・E1 の近さと T・p）をそのまま呼ぶ。`eye.py` は変えない（code_hash が変わる）。
- データの読み方: 論文 3 の作り（`experiments/20261104-timeseries-tau-extend/run.sh` と `scripts/data.py`・`ml.py`）。置き場は `$HOME/gse-public-data`（CoAuthor は `landscape/coauthor_work_obs`、CS1 は `cs1/work2021_obs`、CS1 の取り置きの一覧は `cs1/holdout.json`・SHA-256 `a5a32fce…`）。補足 S2 の 15-session パネルと five-assignment パネルの作り、30% の取り置きがどこで外れるか（作業ディレクトリを作る段か、読む段か）を、論文 3 のコードで確かめてから書く。データの中身は開かない。
- 追記 1 (2) の「固定するもの」を出力に入れる: MUT が空であることの確かめ、入力のファイルと取り置きの一覧の SHA-256、パネルの書き手の ID の列の SHA-256、code_hash、Python と numpy の版、`results/report/d6.json` の SHA-256。
- 乱数の鍵は追記 1 (2) のとおり（揃え [SEED + 93, 0, 7, 形, k, g, r, 側, v]、入れ替え [SEED, 0, 7, 形, k, g, 0]・σ は全 r で共有）。
- E2・E3 の値は出力に書かない。
- 合成の入力で 1 回通す（例: 合成の 1 複製を同じ読み込みの経路に入れ、run_eye の値と一致するかを見る）。ここまでをコミットしてから実データを読む。

### 3. 計算の前に出す量を出してコミットする

- 追記 1 (2) の「計算の前に出す量」（パネルの人数・揃えた後の n_A・n_B・量の比・パネル外の人数と単位の数・単位の数の分布）を出し、(5) の範囲の表と「CS1 の読みの範囲」の比の範囲に照らした「範囲の内／外（下・上）」の印を付けて、notes に書きコミットする。T と p はまだ計算しない。

### 4. 計算して、追記 1 の文で書く

- 9 セル × r = 0〜20 と頻度だけの基準線。止めと直しは追記 1 (2) の (a)〜(c) の順。
- notes に「## D7 実データ（2026-11-2x）」の節を足し、追記 1 (3)〜(5) と「CS1 の読みの範囲」の文の型のとおりに書く。拾わなかったセルに並べる合成の値は `results/report/summary_null1.json`（と CoAuthor は `results/hpz2/report/summary_null2.json`）から引く。
- `decisions.md` に判断 53 を足す。push だけして、PR は作らない。

### 5. 論文 3 への入れ方

- v2 の「論文 3 への入れ方」のとおり、事前に条件をコミットした探索の分析として補足に入れ、本文は主のセル（CoAuthor k = 5 の間なし）の 1〜2 文（追記 1 (3) の最後から 3 つ目の項）。論文 3 の側の書き直しは `~/GSE-prototype-paper3` の `.steering/20261125-paper3-next-venue/` で、研究者に確かめてから行う。

## してはいけないこと

- 追記 1 を実データを見た後に変えない。変えるなら v1 D8 の「定義を変えた版」として新しく凍結し、探索として扱う。
- 打鍵の中身と NDJSON の生ログ、実データの書き手ごとの値を外部の LLM（Codex を含む）に送らない。/cross-review をかけるのはコードの差分だけ。
- 書き手の名や ID を notes・コミット・報告に出さない（ID の列は SHA-256 だけ）。
- `results/hpz2/` を書き換えない。v1 のディレクトリに書き込まない。PR を作らない。
