# 次セッション — IME 論文: M3 の attack-me round 5（G-GEAR）→ 完了時レビュー → PR

> 作成: 2026-10-02（Mac で凍結の前の測定機の作業を終えたセッションの最後に）。
> 前の引き継ぎ `next-session-ime-paper-m3-mac-work.md` の後継（その §2 は済み・§3〜§5 はこのメモが置き換える）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 117・119〜122**）・`tasklist.md`（M3）と、事前登録 `papers/ime-observation/experiment/preregistration.md` の **§3.1・§3.4**。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（★ G-GEAR で）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m3-round5.md を読んで §2 から始めてください。
一次は decisions.md の判断 117・119〜122 と、事前登録 §3.1・§3.4。
本文の語数を測る → attack-me round 5（§2 のとおり絞る）→ 研究者の採否 → 直し → 完了時レビュー → PR。
Skill: attack-me・verify-before-claiming・citation-ssot・subagent-delegation・git-workflow。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-02 の終わり・Mac・枝 `feature/ime-m3-prereg`）

- このセッションのコミット: `e7b7958e`（Mac の作業の直し）→ `07b1206c`（steering の記録）→ このメモのコミット。
- **Mac の作業は済み**（判断 122）:
  - 合わせ直しの診断: `pilot2-on`・`pilot2-off`・`verify-off` で 15 / 15 ブロック採点・282 試行・割り当てのない打鍵 0。コードは変えていない（⚠️ ログに欠けも足しも無いので再同期は試していない・§3.1 にそう書いた）。
  - `pipeline.py` の定数を確定: `RUNNER_KANA_PRESSES_PER_BLOCK = 0`・`REFERENCE_RECEIVES_MODE_KEYS = False`（版は `excluding_mode_keys`）。根拠は §3.1 の 2 つ目の項目。
  - 滑りの最小 1,582 ms。3 本とも区間の規則に当たらない。
- **焦点の規則を変えた**（判断 121・研究者の選択）: `pilot2-off` に S15 以外の焦点の喪失が 1 回（31 ms・打鍵なし・6 本で約 87 分に 1 回）。判断 119 の規則（S15 以外の喪失はすべて中止）では 12 時間のセルがほぼ全部中止になりうる → **「S15 以外の喪失の区間〔前後 500 ms〕に観測の key 行があるときだけ中止」** に改めた。
  - `delivery.py`: 定数 `FOCUS_MARGIN_MS = 500`、`reference_focus_loss` に `n_loss_intervals_unplanned_with_presses`・`n_presses_in_unplanned_losses`、`params.focus_margin_ms`。
  - `pipeline.py`: `reference_abort_reasons` は `n_loss_intervals_unplanned_with_presses > 0` で中止。`abort_rule` の `unplanned_focus_loss_aborts` は `unplanned_focus_loss_with_presses_aborts` と `focus_margin_ms` に置き換え。
  - 余裕の 500 ms はメインの選択（判断 122 の 6・研究者が覆せる）。
- 文: §3.1（結果）・§3.4（3 つ目の理由・k と版の値・焦点の段落・記録する数・盲点から「かなキー」を外す）・§6.2（焦点の項）・§7（キーを押さずに焦点を移して戻る人）・`data.md`（Run checks の前置き・列・手順 1）・`pilot-macos.md`（Raw logs を本計測と揃えた預ける基準に置き換え・監査役 3-E の「every key row … matched」を削除）。
- 確認（Mac・Python 3.14.4）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 0 件・`check_citations.py` 違反なし・`--check-prereg` exit 3・節の参照はすべて実在・変異 4 本すべて赤。
- ⚠️ **本文の語数は未測定**（`round-4/tmp/measure.py` が Mac の Python で SyntaxError）。

## §2 やること（G-GEAR）

1. **語数を測る**: `round-4/tmp/measure.py <prereg のパス>`（前回 13,902 語）。
2. **attack-me round 5**（判断 117）: 同じ立場・同じ接地（原本 8 本の SHA-256 を `round-1/panel.md` と照合）。対象は round 4 の後に変わった箇所: 事前登録の §2.1・§3.1・§3.3・§3.4・§5・§6.2・§6.3・§6.4・§6.6・§6.7・§6.8・§7、`data.md`・`pilot-macos.md`・`kit/e2/README.md`・`delivery.py`（区間・2 版・焦点の分類・★ 喪失中の打鍵と余裕）・`pipeline.py`（中止の規則・預ける前の強制・★ 確定した定数）・`closed_set.py`（錨）・`l2.py`（`per_trial` の空の層）・`spec_predict.py`（`plan_figures`）。`git diff 40ad7801..HEAD -- papers/` から測り直す。
   - 資料は round 4 の `round-4/context-A.md` ほかを写して「変わった箇所」を差し替える。⚠️ round 4 の context-A の §6.7 の要約に「none of the four layers」の誤りがある（直す）。
   - 役ごとの `carryover-*.md`: round 4 の新しい指摘・判定の解消／未解消・裏取り（`round-4/verdict.md` §2）・採否（判断 116・117・119・**121**）・対応（判断 118・120・**122**）。★ **判断 121 で焦点の規則を変えた理由**（パイロットの 31 ms の喪失と、約 87 分に 1 回という頻度からの見積もり）と、**k と版を実ログで決めたこと**を書く。⚠️ 他の役の指摘は渡さない・他の役を名指ししない。採らなかったもの（k の階級ごとの報告・主を k ≥ m に限る・runner を変える・題の nit・設計効果の式の出典・定数と §3.1 の機械照合・短い喪失を閾値で許す案）を正直に書く。作業中の点検の指摘は「採否と対応」に含めてよいが、点検した者を名指ししない。
   - 応答の保存は round 4 と同じ（本文をメインが Write で `round-5/tmp/<名>.raw.md` に書き写し、`scripts/secrets-filter.sh` と `round-4/tmp/check_resp.py` を `RD` を `round-5` にした写しで検査）。⚠️ 依頼文の「読んでよいファイル」に「Grep は一覧のファイルだけを対象にする（ディレクトリ全体を Grep しない）」を足す。一覧の外のファイルを Read したと申告したら、写さずに研究者に問う。
   - 接地の引用の照合は `round-4/tmp/quote_check.py`。裏取りで計画と予測を使うときは §2.4 のコマンドで scratchpad に作る（SHA-256 は ON `c7a5469d…`・OFF `3759ebf7…`）。予測と `plan_figures` は `spec_predict.py --from-plan --plan <plan> --out <file>`。⚠️ Windows の Python に `/c/...` のパスを渡さない（`C:\...`）。
   - ⚠️ パイロットの生ログは G-GEAR に無い。§3.1 の数の裏取りが要る指摘は、Mac の作業として研究者に戻す（判断 122 の数は Mac で測った）。
   - 起動の前に研究者へ知らせる（G-GEAR に Zenodo のトークンがある・`sealed/` と生ログは無い）。
3. 研究者に採否を問う → 直し → 確認（`kit/check.sh`・`run.sh --synthetic` 2 回でバイト一致・`_style_check.py`・`check_citations.py`・`--check-prereg` exit 3・節の参照・語数）。
4. **完了時レビュー**: code-reviewer ∥ security-checker ∥ Codex（`scripts/run-codex-review.sh <base>..<head> -- papers/ime-observation docs/references.md`・出力は scratchpad・2 巡）。範囲は `git merge-base origin/main HEAD`..HEAD のコミット済みだけ。Codex の台帳は回す前に origin/main の当日分も見る。⚠️ レビューの作業用エージェントに `kit/check.sh`・`pipeline.py --selftest`（約 15〜35 秒）を回させない。
5. origin/main を取り込み → push → PR → CI 緑なら merge → main の CI（git-workflow ルール 6）。⚠️ 凍結は研究者の別の段（OSF の登録は研究者）。

## §3 気をつけること

- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印は開けない。人の打鍵データを使わない。参照のログのキーコードを表示・転記しない（数と時間だけ）。
- ⚠️ 名前（Mac で変えたもの）: `delivery.py` の `reference_focus_loss` に `n_loss_intervals_unplanned_with_presses`・`n_presses_in_unplanned_losses`、`params.focus_margin_ms`。`e1_delivery.json` の `abort_rule` は `{focus_margin_ms, pre_ms, reference_receives_mode_keys, runner_kana_presses_per_block, tail_ms, unplanned_focus_loss_with_presses_aborts}`。`data.md` の表の列は `n_loss_intervals_unplanned_with_presses`。
- ⚠️ 定数と文の食い違いを機械で検査する仕組みは無い（判断 120 の 9）。直しで §3.4 の値（k = 0・`excluding_mode_keys`・500 ms）を触るなら、`pipeline.py`・`delivery.py` と目で照合する。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。G-GEAR では main は別の worktree が checkout している。
- ⚠️ git-bash で `git show origin/main:<path>` は MSYS がパスを書き換える → `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない（Windows のパスや行末の `\` を含む文書は Write / Edit で書く）。
- ⚠️ round 1〜4 の `tmp/` は attack-me を閉じるまで消さない。
