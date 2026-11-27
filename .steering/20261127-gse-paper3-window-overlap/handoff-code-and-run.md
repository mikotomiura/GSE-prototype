# 次のセッション: 窓の歩みの用量反応のコード・合成の門・本計算

> 作成: 2026-11-28。worktree `~/GSE-prototype-window-overlap`、枝 `exp/gse-per-person-window-overlap`（origin に push 済み）。条件は第 7 版で凍結した（commit 298d56e7・判断 9）。

## 入口の文

```
~/GSE-prototype-window-overlap の .steering/20261127-gse-paper3-window-overlap/handoff-code-and-run.md を読んで、その手順を行って。
```

## ここまで

- 条件: `experiments/20261127-window-overlap-dose/conditions.md`（第 7 版・凍結）。attack-me（stage prereg）は round 1〜4 major、round 5・6 minor で閉じた。記録は `.steering/20261127-gse-paper3-window-overlap/attack-me/prereg-window-overlap/round-1/`〜`round-6/`（各 verdict.md）。判断は同じ dir の `decisions.md` の判断 1〜9。
- 書いたコード（凍結の前・下書き）: `experiments/20261127-window-overlap-dose/scripts/masks.py`（列 A の印と列 B の位相）と `scripts/load_dose.py`（列 A・B・C・C′ の読み込み・data.py と同じ並べで時刻を読み obs を照らす）。どちらも未検査。第 7 版の条件に合わせて見直すこと（列 C′ は名前 "P1-<s>"・"P3-<s>"、列の番号 c は D2 の表）。
- 研究者が決めたこと: 計算は Mac（repo の外の仮想環境・Python 3.11・numpy 2.4.4）。端の再現の門が外れたら許容を変えずに HP Z2 で全部を回し直す。見積もりが 10 時間を超えたら列 B を外す。

## 手順

1. `reproducibility-discipline`・`verify-before-claiming`・`subagent-delegation` を読む。CLAUDE.md のモデル選択では実装は Sonnet（研究者が決める）。
2. 条件の第 7 版を全部読む（特に D1〜D5・V1〜V3・限界）。条件を変えない。曖昧な所は実データの前に `decisions.md` に判断として書き、条件の末尾「条件の後の変更（実データを見る前）」に足す（意味と語の強さを変えない直しだけ）。
3. 仮想環境: `uv venv ~/.venvs/window-overlap --python 3.11` と `uv pip install numpy==2.4.4`（repo の外）。版を provenance に書く。
4. コードを書く（S13 の試験の `scripts/` を写さずに読み込む。SHA-256 は条件 D3 の値で照らす）。
   - 駆動: S13 の `fit.py` の `run()` を、列の読み込みだけを `load_dose.load_column` に差し替えて回す。fit.py は `import load as L` を使うので、駆動の先頭で `sys.modules["load"]` をこの試験の読み込みに置き換えてから fit を読み込む（macOS の spawn は子で主のモジュールの先頭を実行し直すので、置き換えは子にも効く。P-SWAP で確かめる）。
   - 足すもの: M と M_shuf（20 回）・D_s・ρ_h（S13 の residual.py を同じ差し替えで）・頭を除く採点（npz から読み戻し）・対応のある差の集計と φ・D5 の語と決定表と本文の英文の組み立て（`readings.json`）・区間と 1 人抜き・P-ROWS・P-REPRO-U／N。
   - 陽性対照と変異: 条件 V2 の表（P-STRIDE〜P-READ・m61〜m83）。変異の門は S13 と同じ作法。
5. 合成のデータだけで selftest・変異・配管の通しを通す。Mac の合成で時間を測り、見積もりを「条件の後の変更（実データを見る前）」に足す（10 時間を超えたら列 B を外す）。
6. 本計算（実行の順は条件 D6）。端の再現の門（列 A30 → A1）を最初に通す。書き手ごとの値と母数は repo の外。人は開かない。
7. notes.md を書く（`readings.json` の語と型と英文をそのまま写す。D5 の外の読みを足さない）。/cross-review（Codex を加える）。
8. 論文の枝（`docs/gse-paper3-per-person-learning`・worktree `~/GSE-prototype-paper3`）に結果の要約だけを持ち込み、本文に条件 D5 の英文と図 1 つ、S12・S13 の結論を足す（paper-write Step 4・length-log）。そのあと論文 3 の引き継ぎ `~/GSE-prototype-paper3/.steering/20261125-paper3-next-venue/handoff-mechanism-dose-response.md` の手順 6・7（attack-me round 2 の revision-integrated・venue-fit の当て直し）。

## してはいけないこと

- 凍結した条件（歩み・列・量・語・型・本文の英文）を変えない。変えるなら新しい版として凍結し直す。
- 実データを見てから読みの語や英文を選ばない。外れたら止めて研究者に聞き、逸脱として notes に書く。
- 実データの書き手ごとの値・打鍵の中身・生ログを外部の LLM（Codex を含む）に送らない。送るのは条件・コードの diff・集計値だけ。
- S14 の数と読みの文（論文 3 の追記 1・b0f5821a で凍結）を変えない。
