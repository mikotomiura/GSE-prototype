# Mac での作業（v2）: HP Z2 の後半が push された後の D6 の集計から先

> 作成: 2026-11-26（Mac のセッション）。worktree は `~/GSE-prototype-weight-eye`、枝は `exp/gse-per-person-weight-eye`。v2 の実験は `experiments/20261126-per-person-weight-eye-v2/`。
> 一次資料: v2 の `conditions.md`（v1 との差分）と `notes.md`、v1 の `conditions.md`（D6〜D8）、`decisions.md`（判断 44〜49）。ここに書くのは順番と止める所だけで、読みの基準は条件に従う。

## 入口の文（Mac の Claude Code に）

```
~/GSE-prototype-weight-eye の .steering/20261122-per-person-weight-eye/handoff-mac-v2-d6.md を読んで、その手順を行って。
```

## ここまでの状態（この引き継ぎを書いた時点）

- v2 は v1 の D8 に当たる「定義を変えた版」で、探索として扱う（判断 49）。結果は確認の主張に使わない。
- V1 は両方の機械で緑（code_hash `1665a0b2f83f…`）。D5 では E1 を選んだ（8c21235d・段 4 の決まり）。
- 報告の組はどちらも回し終えている。Mac の第 1 の帰無は 66d8ef95、HP Z2 の第 2 の帰無は 225dd49e。
- D9 は、第 1 の帰無が `results/d9_null1.json`、第 2 の帰無が `results/hpz2/d9_null2.json`。
- 書き手の水準の量は、Mac の分を c と率ありの版で出してある（988c09c9）。HP Z2 の分は後半で c と率ありの版になる。HP Z2 は合図のファイル `signals/mac-quant-null1.ready` を待ってから後半を回す（手順は `handoff-hpz2-v2-report2.md` の後半）。
- 実データ（CoAuthor・CS1）は、どの版でもまだ読んでいない。

## 手順

### 1. HP Z2 の後半が来たかを確かめる

```bash
cd ~/GSE-prototype-weight-eye && git status --short   # 探索の大きな json（results/explore/*.json）だけが ?? で出るのは既知
git pull --ff-only
git log --oneline -5
cd experiments/20261126-per-person-weight-eye-v2
python3 -I -c "import json; d=json.load(open('results/hpz2/report/d6_local_null2.json')); print(sorted(d.keys()))"
```

- 「重みを見る目 v2 の第 2 の帰無の書き手の水準の率（c と率あり）」というコミットがあり、`d6_local_null2.json` に c と率が入っていれば進む。
- 来ていなければ、ここで止めて研究者に返す。HP Z2 の作業を Mac で代わりにしない（memory の `feedback-ggear-tasks-stay-on-ggear`）。

### 2. D6 を集計する（機械的・ここで初めて結果を読む）

```bash
~/venvs/weight-eye/bin/python -I -X utf8 scripts/d6_report.py results
```

- 出力は `results/report/d6.json`。最後の 4 行（選んだ案 E1 の門・12 の判定・追記 3 の判定）をそのまま控える。
- 表示の「追記 3 … 論文 3 に統合する／統合しない」は v1 の文言のまま出る。v2 では、v2 の `conditions.md` の「論文 3 への入れ方」に読み替える。「統合する」は、事前に条件をコミットした探索の分析として補足に入れ、本文は 1〜2 文で触れることを指す。
- 選んだ案は E1 なので、v1 D7 (2) の「E1 を別に出す」は選んだ案の読みと重なる。
- 例外が出たり、判定の数が 12 にならなかったりしたら、そこで止めて出力を研究者に返す。

### 3. notes と判断 50 を書いてコミットする

- v2 の `notes.md` に「## D6 報告の組（2026-11-2x）」の節を足す。v1 の notes の D6 の節と同じ形で、次を書く。
  - 入力の HEAD と run_id（`results/provenance.report.null1.json` と `results/hpz2/` の provenance）
  - E1 の 55 の門（赤の数と、赤のセル）
  - 12 の判定（拾った・境目・拾わなかった）と論文 3 との並べ
  - 書き手の水準の率（両機）と D9 の g1
  - 追記 3 に当たる判定
- 比べるときは v1 の値（`experiments/20261122-per-person-weight-eye/results/report/`）を並べる。揃えない表を新しく計算しない（v2 の D1）。
- `decisions.md` に判断 50（D6 の結果と、次の分岐のどれに当たるか）を足す。
- コミットしたら push だけする（PR は作らない）。

```bash
git add experiments/20261126-per-person-weight-eye-v2/results/report/d6.json experiments/20261126-per-person-weight-eye-v2/notes.md .steering/20261122-per-person-weight-eye/decisions.md
git commit   # docs(experiments): 重みを見る目 v2 の D6 —— <一言>（判断 50）＋ Refs と Co-Authored-By
git pull --rebase && git push
```

### 4. 結果で分かれる

D6 の結果によって、次の 3 つのどれかに進む。

**A. E1 の門が 1 つでも赤**
- v1 D8 の止めに当たる。実データには進まない。
- 確率的な検査の赤は、原因未確定として調べる。コード・生成・入れ替えを見て、実装の誤りがあれば直す。見つからなければ、新しい種で回し直さない（D8・判断 28）。
- 論文 3 には、v1 の限界の 1 文と補足の 1 節に、v2 も門で止まったことを添える。
- 次の手（閉じるか、さらに版を変えるか）は研究者が決める。推奨と理由を添えて、AskUserQuestion で日本語で聞く。

**B. 門はすべて通り、12 の判定に「拾った」が 1 つもない**
- 論文 3 には入れない。v1 の限界の 1 文と補足の 1 節に、v2 は門を通ったが拾わなかったことを添える。
- 実データに進むか（読むとしても論文 3 には入れない）、ここで閉じるかは研究者に聞く。推奨を添えて AskUserQuestion で聞く。

**C. 門はすべて通り、「拾った」が 1 つ以上ある**
- 実データに進む前に、5 → 6 → 7 の順で行う。

### 5. /cross-review（B・C のとき。A でも、原因の調べにコードを読むなら先に回す）

- 範囲: v1 の scripts・run.sh からの差分。`git diff --no-index experiments/20261122-per-person-weight-eye/scripts experiments/20261126-per-person-weight-eye-v2/scripts`（`__pycache__` と `explore_*.py` は除く）と、run.sh も同じ形で比べる。v2 を作ったのはコミット 41c46f53。
- Claude と Codex の両方で回す（memory の `feedback-attack-me-include-codex`）。結果と生ログは外部に送らない。
- Codex に渡す既知の未決: v1 の E3 の門の赤は判断 44 で扱い済み。探索のスクリプト `explore_*.py` は門に使わない。揃えで量の多い書き手の記録を捨てること・CS1 の検出力を上に見積もることは、v2 の `conditions.md` の「読まないこと」に書いてある。
- 結果を変える誤りが見つかったら、v1 D8 の「再開」のとおりに扱う。新しい code_hash で V1 からやり直す。報告の組を見た後なので、選ばれる案が変われば、その版も探索になる。
- 対応は判断 51 に書く。

### 6. D7 の追記（C のとき・実データを読む前）

- v2 の `conditions.md` に「## 追記 1: D7 実データの読みの基準」を書く。v1 D7 の (1)〜(5) を中身にする。
  - (1) 門を通ったときだけ進む。
  - (3) 間を空けたセルと隣り合うセルを並べ、g = 0・5・10 の並びを合成の ρ ごとの並びと比べる。
  - (4) 見分けと予測の得の対比の並べ方。
  - (5) 書き手の水準は D6 と同じ閾値の作りで判定する。
- CS1 は「1e-2 以上の差なら拾える」範囲で読み、判断 48 の表を添える（v2 の「読まないこと」）。
- attack-me（prereg・Codex を加える）で攻めさせてから直す。回すたびに判定の推移を見て、minor が続けば閉じる（memory の `feedback-attack-me-stop-when-minor`）。
- 追記をコミットして push する。このコミットが実データを読む前の凍結になる。

### 7. 実データへの適用の引き継ぎ（C のとき）

- 実データの読み込みは別のタスクにする。この枝の `.steering/20261122-per-person-weight-eye/` に、次のタスクの引き継ぎを書く。
  - データの置き場と読み方は、論文 3 の S2 と `data.split`・`ml.pool_units` を見る。CS1 は著者が承諾済み。
- 打鍵の中身と NDJSON の生ログは外部の LLM に送らない。

## してはいけないこと

- HP Z2 の作業を Mac で代わりに回さない。`results/hpz2/` を書き換えない。
- D6 を見てから、門の閾値・判定の基準・論文 3 への入れ方を変えない。変えるなら新しい版で、探索として扱う。
- D7 の追記をコミットする前に、実データ（CoAuthor・CS1）を読まない。
- v1 のディレクトリに書き込まない（v1 の notes に v2 への参照を 1 行足すだけなら可）。
- PR を作らない。push だけして、PR は研究者に確かめる。
- npz の値を出さない。
