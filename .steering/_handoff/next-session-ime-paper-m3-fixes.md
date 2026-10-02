# 次セッション — IME 論文: M3 の attack-me round 1 の直し → round 2 → 完了時レビュー → PR

> 作成: 2026-10-01（G-GEAR で、attack-me round 1 と予測器を終えたセッションの最後に・コンテキスト約 50% で区切った）。
> 前の引き継ぎ `next-session-ime-paper-m3.md` の §2（attack-me）の後継。§3 以降（完了時レビュー・PR・凍結）は前の引き継ぎも見る。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 99〜106**）・`tasklist.md`（M3 の「round 1 の直し」）・`attack-me/prereg-ime-macos/round-1/verdict.md`（指摘ごとの裏取りと直す順）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（G-GEAR 推奨: round 1 の接地の本文 `round-1/tmp/sources/` は G-GEAR にだけある）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m3-fixes.md を読んで §2 から始めてください。
一次は decisions.md の判断 99〜106 と round-1/verdict.md §3。直しは研究者が承認済み（判断 105）。
実装の細部はメインの実装上の選択として決めて decisions.md に書く（研究者に問わない）。設計を変える判断が要るときだけ問う。
Skill: implementation-workflow・verify-before-claiming・subagent-delegation・citation-ssot・attack-me（round 2）・data-privacy。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-01 の終わり・G-GEAR・枝 `feature/ime-m3-prereg`・push 済み・PR はまだ）

- このセッションのコミット（Mac の `bc3324ac`・`d0cf4343` の後）:
  - `c5bfbc65` attack-me round 1 の記録（`attack-me/prereg-ime-macos/round-1/`: context-A/B・panel・brief 4・review 3・audit・verdict）
  - `35d4aa92` 判断 99〜105 ／ `f08e0494` 判断 106
  - `f3c08a68` **`kit/analysis/spec_predict.py`**（予測器・selftest 8 件・`kit/check.sh` 28 本緑）
  - （このメモと tasklist の追記は、このメモと同じコミット）
- round 1 の判定: **major revision**（3 人とも major・fatal 0）。研究者の判断（すべて推奨どおり）:
  - 99 20 秒の打ち切り → 推定の対象を分ける（Q1・Q2 の主は打ち切りに当たらない試行・L2 は全試行が主）
  - 100 仕様の予測を参照として登録し 2 段で報告（正解 対 予測／予測 対 観測）
  - 101 near chance は K = 1000 を判定から外し、性質の表を載せ、2 セルの両方を求める
  - 102 E2 の推奨は ms の時刻を持つ集合（`all`・`no_runs`）を対象外・セッションの行も対象外
  - 103 精度の幅の表・推定値を形容しない・Q3 を how closely に・n の根拠を書き直す
  - 104 L2 に試行ごとの差をシナリオ × 速さ別に
  - 105 脅威と限界の節（畳まない規則での感度の解析は足さない）・`verdict.md` §3 の minor 19・nit 9 を承認・pooled は本文をコードに合わせ「件数の和」
  - 106 他の IME と他のアプリでの転移は**別の研究**。追補は Windows（と E3 の Windows）だけ
- Codex の台帳: 10-01 は main で 354,180 / 上限 300,000（超過）。日が変われば戻る。回す前に origin/main の台帳の当日分を見る。

## §2 直しの順（tasklist の「round 1 の直し」）

### A. pipeline への組み込み（判断 99・100）— いちばん大きい

- 予測器は `spec_predict.predict(oracle_bytes, plan_bytes, keymap)` → `sessions`（`start_wall_ms`・`end_wall_ms`・`dwell_ms`・`nav`・`abandon`・`end` ∈ row / truncated / open・`start_trial`・`end_trial`）と `trials.by_trial[tid]`（`long`・`carried_out`・`n_started`・`sessions`）。`as_obs_rows(sessions)` が観測の行の形（`t` = 終わり）を返す。
- 照合の流れは `match.evaluate`（`match.py:742-`）: 除外 → `match()` → 層ごとの `detection_metrics`。`l1.py`・`l2.py` は match の出力を使い、`pipeline.py` が束ねる。
- 入れること（実装の細部はメインが決めて decisions.md に書く）:
  1. **打ち切りの分割**（99）: `long` の試行（予測で、その試行が始めたセッションが打ち切りになる）の正解のセッションと、その試行に割り当たる観測の行（打ち切りの後の断片を含む）を、Q1・Q2 の**主**から外し、別の塊（打ち切りの確認）で数える。全試行の値は副。L2 は全試行が主、`long` の試行を除いた版が副（文の中の試行をどう除くかは実装で決める）。
  2. **2 段の照合**（100）: (i) 正解のセッション 対 予測の行（`as_obs_rows`）、(ii) 予測のセッション（正解の形にして）対 観測の行。同じ `match()` と `detection_metrics` を使い、層ごとに出す。(i) は観測を読まないので凍結の前に計算できる量（パイロットの正解側でも計算可）。
  3. 診断の層: 予測で `carried_out` の試行と、その持ち越しを受けた試行（`n_started == 0`）・読みに終端のキー（`minus`・`comma`・`period`）を含む試行。
  - ⚠️ S6 の持ち越しは**次の試行（どのシナリオでも）を汚す**。分割（判断 99）は打ち切りだけに当てる。持ち越し・Tab・記号の分割は推論規則の限界で、段 (i) で数える実際の誤り（tasklist に書いた）。
  - `run.sh --synthetic` が 2 回でバイト一致のまま通ること。合成の観測は `inject.py` が正解から作る（予測器とは独立）。selftest と変異（`feedback_acceptance_self_test`: 判定式が常に真・経路に未到達、を変異で潰す）。
- 本番の計画での予測の値（擬似の oracle・tasklist に記録）: ON は `long` 677 / 3,150・`carried_out` 188・分割 314・なし 113。OFF は `long` 650 / 2,925・186・280・109。slow の `long` は ON 423 / 1,050。⚠️ 事前登録には「計画から凍結の前に計算した予測」として開示してよい（観測は読んでいない）。本番の値は測った oracle から出す。

### B. `l2.py` の試行ごとの差（判断 104）

- 4 量の試行版（変換の数の差・変換時間の和の差・取り消しの数の差）をシナリオ × 速さ別に。文ごとの値と ICC は「この設計の均等な混合の下での値」と明記。selftest・変異。

### C. 事前登録 `experiment/preregistration.md` の文

- §1.1 目的の文（105: 参照入力欄の呼び出しから §4.3 の規則で組み立てたセッションとの一致）・§1.2 Q3 を how closely に（103）・「(section 6.6)」→ 6.7。
- §1.3 範囲（106）: 追補は Windows のセルと E3 の Windows だけ。他の IME・他のアプリでの転移は「この研究の外」。§7 の追補の範囲（新しいファイルの追加を含む）を書き直す。
- 新しい節: 予測の行と 2 段の照合（100）・打ち切りの分割（99）・妥当性への脅威と限界（105: 参照入力欄・規則・合成入力・学習を戻さない〔判断 91〕・実行順・1 台・ソフトの時計・S9・物理キーの経路・回収の遅れ 0〜100 ms）。
- §3.3 n の根拠（103）と精度の幅の表。Wilson の半幅（95%）: n = 75 で p = 0.5 / 0.8 / 0.95 / 0.99 → 11.0 / 8.9 / 5.4 / 3.5 pt、n = 225 → 6.5 / 5.2 / 2.9 / 1.5、n = 1,050 → 3.0 / 2.4 / 1.3 / 0.6、n = 3,150 → 1.7 / 1.4 / 0.8 / 0.4。⚠️ 打ち切りの分割で slow の層の n は減る（S1 の slow は 75 → 約 34）→ その幅も書く。連続量は SD の関数で（ブロックのクラスタを考える）。
- §6.7 E2（101・102）: near chance の性質の表（下）・K = 1000 は記述・2 セルの両方・`all`・`no_runs` は対象外（推定だけ）・セッションの行は攻撃に使っていない（「the session rows」を正す）・人の休止の型は模していない。
  - P(Wilson の上端 ≤ 2/K | 真の正解率 = c/K)（予定の n・二項分布・メインが計算）:

    | n | K | c = 1 | 1.5 | 2 | 3 |
    |---|---|---|---|---|---|
    | 2,925（ON） | 10 | 1.000 | 1.000 | 0.024 | 0.000 |
    | 2,925 | 100 | 0.994 | 0.487 | 0.020 | 0.000 |
    | 2,925 | 1000 | 0.210 | 0.067 | 0.020 | 0.001 |
    | 2,700（OFF） | 10 | 1.000 | 1.000 | 0.025 | 0.000 |
    | 2,700 | 100 | 0.989 | 0.447 | 0.019 | 0.000 |
    | 2,700 | 1000 | 0.067 | 0.017 | 0.004 | 0.000 |
- minor・nit の残り: `verdict.md` §3 の一覧（pooled は「件数の和」・凍結の範囲に plan_config・手順書・計画の SHA-256〔ON `c7a5469d…`・OFF `3759ebf7…`〕・除外の網羅性と分岐・打鍵 1 つずつの忠実度・kappa と LoA の区間・S3 と S11・思考の時間・盲検の開示・題の「content-free」・パイロットの手打ち・K0 / K1・§4.2 のキーコード・持ち越しの件数・`dwell_ms == 0` の文・ICC の名前・ブートストラップの回数・2 つの定義）。

### D. 公開物とハッシュに入るファイル

- ⚠️ **`experiment/gt_rules.json` と `experiment/config.json` の `_note`**（凍結のハッシュに入る・凍結の後は直せない）: 「revised … before the freeze」「provisional」を段階凍結（判断 92）に合わせる。
- `pilot-macos.md`（所要時間 L148-154・学習 L20・Raw logs の基準は Mac の M2 の残り）・`kit/run/README.md:160-161`（時計を合わせると書いている）・`notes.md`（結果のファイル名・informative の文・E3 は標準出力）・`kit/gen/README.md:37-38, 189`（「not yet fixed」）・`kit/e2/README.md`（推奨の範囲）・`data.md`（本計測の預け方に key 行と `key_down` の対応の検査）。

### E. 確認

- selftest 全部・`kit/check.sh`・`run.sh --synthetic` 2 回でバイト一致・`_style_check.py`（`.steering/.../issues/_style_check.py`）・`check_citations.py`。

### F. attack-me round 2（Skill attack-me）

- 置き場 `attack-me/prereg-ime-macos/round-2/`。同じ立場・同じ接地の文献（本文は `round-1/tmp/sources/` を使ってよい・または取り直す。⚠️ `tmp/` は attack-me を閉じるまで消さない）。
- 役ごとの `carryover-R1.md`〜`R3.md`・`carryover-audit.md`（その役の round 1 の指摘・裏取り・採否・対応・未解決。⚠️ 他の役の指摘を渡さない）。依頼文に「再掲を求めない・解消を 1 件ずつ判定してから新しい穴」。
- 起動の前に研究者へ知らせる（この機械に Zenodo のトークンがある）。

### G. その後（前の引き継ぎ §3・§5）

- 完了時レビュー（code-reviewer ∥ security-checker ∥ Codex〔`scripts/run-codex-review.sh <base>..<head> -- papers/ime-observation docs/references.md`〕）→ origin/main を取り込み → push → PR → CI 緑なら merge → main の CI。⚠️ 凍結は研究者の別の段。

## §3 気をつけること

- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印は開けない。人の打鍵データを使わない。予測器は観測を読まないので、計画・パイロットの正解側に当ててよい。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。
- ⚠️ main は別の worktree が checkout している（`C:\GSE-prototype` で `git switch main` はできない）。
- ⚠️ git-bash で `git show origin/main:<path>` は MSYS がパスを書き換える → `MSYS_NO_PATHCONV=1` を付ける。heredoc にバックスラッシュを書かない（Windows のパスは Write ツールで）。
