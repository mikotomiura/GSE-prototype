# 引き継ぎ: IME 論文の counts_only の記述を直し、連なりの長さを本当に捨てた組を事後の解析で測る

作成 2026-10-10（Windows の機 G-GEAR・`C:\GSE-prototype`）。新しいセッションで `/clear` の後に始める。応答・記録・完了報告は日本語で書く。記号（★・⚠️）を多用しない（研究者の指摘）。

このメモは一次資料ではない。一次は次の 3 つで、状態は着手時に測り直す。

- `.steering/20261009-matching-attack-prototype/decisions.md` の判断 2（見つけた経緯と確かめ方）
- `papers/ime-observation/kit/e2/closed_set.py`・`simulate_obs.py`
- IME 論文の作業記録 `.steering/20260927-ime-observation-paper-eval-design/decisions.md`（2026-10-10 の時点で判断 223 まで）

## §0 打ち込む用

```
git fetch → 状態を測る:
- IME 論文の decisions.md の最後の判断の番号（main と並行の枝・Mac・Surface の記帳）
- 公開 repo mikotomiura/ime-conversion-logging の main と最新のタグ
- 次の出し先（プレプリントと BRM）について研究者が決めたこと（§2）
.steering/_handoff/next-session-ime-counts-only-fix.md を読んで §3 を上から実行してください。
```

## §1 何が起きたか

IME 論文の closed set の攻撃（`kit/e2/closed_set.py`）で、`runs = "count"` を使う特徴量の組（`no_runs`・`bin1s_count`・`counts_only`）は、英字の連なりの長さを捨てていない。実装の流れは次のとおり。

- `simulate_obs.apply_features(..., runs = "count")` は、連なりの英字の行に同じ時刻を付けるだけで、行は消さない。
- `closed_set._tokens(..., runs = "count")` は、その行を 1 トークンにまとめ、トークンの count に連なりの長さを入れる。
- `_distance` は、同じカテゴリのトークンの count の差を費用にし、トークンの列の順序も使う（編集距離）。

2026-10-10 に実行して確かめた（G-GEAR・`closed_set.py` の SHA-256 `364cc833…`）。

| 比べた 2 つの記録 | `counts_only` の距離 |
|---|---|
| 英字 10 打と 20 打（後ろに Space と Enter） | 10.0（`no_time` でも 10.0） |
| 英字 8 打と 12 打 | 4.0 |
| 同じカテゴリの数で、順序だけが違う（英字 5・記号・英字 3 と、英字 3・記号・英字 5） | 4.0 |

一方、記述は次のように書いている。

- 事前登録 §6.8: 「no lengths of letter runs（`no_runs`）」「neither（`counts_only`）」
- 原稿 `manuscript/sections/recoverability.tex`:
  - 方法の節（38〜40 行付近）: 「no run lengths（`no_runs`）」「neither times nor run lengths（`counts_only`）」
  - 結果の節: 「the numbers of key presses of each category in a trial, without their order or times」
- `kit/e2/README.md` の表: 「run length removed」

記述と実装が違う。実装した組について測った値と判定（どちらの組も偶然の水準の近くではない）は正しい。しかし、読者が読む「連なりの長さ（と順序）を捨てても偶然の水準に届かない」は測られていない。推奨の規則は `no_time` と `counts_only` だけを見るので、長さを本当に捨てた組が近くに来れば、推奨（「推奨できる粒度なし」）が変わりうる。

参考の見積もりがある。照合攻撃の試作（`experiments/20261009-matching-attack-prototype/`）の Windows のセルで、同じカテゴリの連なりをすべて 1 トークン・個数 1 にした組（`S_rleinf`・BackSpace などの連なりも捨てる・同点は 1/m・候補の引き方も違う）を k = 1 で測った。N = 100 で 44.3% → 1.68%、N = 10 で 90.6% → 11.2% だった。IME 論文の条件ではないので、論文の結果として引かない。

## §2 研究者の決定と、その後に分かったこと（2026-10-10）

- 研究者は、PsyArXiv に審査待ちで出しているプレプリントを取り下げ、次の 2 つを直してから出し直すと決めた（AskUserQuestion で推奨どおり）。
  - (1) `no_runs`・`bin1s_count`・`counts_only` の説明をコードどおりに直し、逸脱として記録する。
  - (2) 連なりの長さを本当に捨てた組を、事後の解析として 3 セルで、IME 論文の攻撃のまま測る。
- その直後に、PsyArXiv が提出を却下していたことが分かった（研究者が伝えた）。理由は対象範囲の外で、モデレーターの文言は次のとおり。
  - 「primarily intended for contributions to scientific psychology. It may be better suited to a computer science repository (e.g. arXiv, TechRxiv). This moderation decision is final. Please do not resubmit.」
  - 異議の申し立ての案内（https://blog.psyarxiv.com/about-psyarxiv#appeals）が付いていた。
- → 取り下げの手順は要らない。直す 2 つは変わらず、次にどこへ出す前にも済ませる。
- 次の出し先は研究者が決める。候補は arXiv・TechRxiv・プレプリントを出さずに BRM へ、など。
  - arXiv は、2026-01-21 から所属のメールだけでは自動の endorsement にならず、研究者には個人的な endorsement が要る（memory `project_arxiv_endorsement_2026`）。
  - 前の引き継ぎ -11 の「PsyArXiv の審査の後 → BRM への投稿」は、この却下で前提が変わった。

## §3 やること（上から）

1. `/start-task` から入る（CLAUDE.md）。作業記録は IME 論文の既存の作業記録（`.steering/20260927-ime-observation-paper-eval-design/`）に判断を足すか、新しいディレクトリにするかを最初に決める（推奨: 既存に足す。判断の番号は着手時に測る）。
2. 直す範囲を一次で洗い出し、表にする。
   - 原稿の方法と結果の節、補遺、表と図の見出し
   - `kit/e2/README.md`、`closed_set.py` の docstring と `FEATURE_SETS` の注、`simulate_obs.py` の docstring
   - `experiment/deviations.md`（D13 として足す）
   - OSF の事前登録は書き換えない（逸脱で扱う）
   - 「without their order」のような、ほかの言い換えも全文を grep する（verify-before-claiming のルール 7・8）
3. 事後の解析の設計を、結果の前に固定する。AskUserQuestion で、推奨と理由を添えて聞くこと。
   - 組の定義の候補:
     - (a) 英字の連なりだけを 1 トークン・個数 1 にする（登録の意図に近い）
     - (b) 同じカテゴリの連なりすべてを個数 1 にする（S6 の BackSpace の数も捨てる）
     - (c) 両方
   - 時刻: 使わない。
   - K = 10・100・1,000。候補と同点の決め方・種は IME 論文と同じ。
   - 推奨の規則（Wilson の上端 ≦ 2/K）を当てるが、推奨そのものを登録どおりのままにするか、事後の判定として並べるかも聞く（推奨: 登録の推奨は変えず、事後の判定として並べる）。
   - `closed_set.py` は変えず、新しいスクリプトを kit に足して関数を import する（試作の `scripts/distances.py` の作り方が参考になる）。
4. データ:
   - macOS の 2 セルは Mac にある。Zenodo の寄託（DOI 10.5281/zenodo.23183438）からも取れる。
   - Windows のセルは G-GEAR の `papers/ime-observation/experiment/runs/windows-msime-tsf-2/` にある。
   - どの機で回すかを決める（memory「Handoff per machine」）。
   - NDJSON の生ログは Codex など外部の LLM に送らない。
5. 測ってから原稿を直す。推奨が変わるかを、測る前に言わない。
6. 公開 repo の新しい版（v1.0.2）と Zenodo の新しい版は、`kit/export/README.internal.md` の手順で行う（判断 222・223 の v1.0.1 の先例）。
7. `/finish-task`: code-reviewer と `/cross-review` を 2 巡。原稿の外枠を変えるので、`attack-me` を回すかも研究者に聞く。
8. 次の出し先への提出は研究者が行う（PsyArXiv には再投稿しない）。README・原稿・CITATION.cff などに PsyArXiv のリンクや予定を書いた箇所があれば、それも直す範囲に入れる（grep で洗う）。

## §4 してはいけないこと

- OSF の事前登録・凍結された結果のファイルを書き換えない（逸脱として足す）。
- 推奨が変わるかどうかを、測る前に Claude が言わない。試作の Windows の数値を、論文の結果として引かない。
- O1・G1・Phase1 の記録を読まない。
- `git add -A` / `git add <dir>` を使わない。

## §5 関連

- memory: `project_ime_counts_only_keeps_run_length.md`
- 試作の結果: `experiments/20261009-matching-attack-prototype/notes.md`（「関連して見つけたこと」）
- 前の IME 論文の引き継ぎ: `.steering/_handoff/next-session-ime-paper-manuscript-11.md`（v1.0.1・PsyArXiv の審査の後・BRM への投稿）
