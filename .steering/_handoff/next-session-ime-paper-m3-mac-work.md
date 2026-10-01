# 次セッション — IME 論文: M3 の Mac の作業（凍結の前・測定機）→ G-GEAR で attack-me round 5 → 完了時レビュー → PR

> 作成: 2026-10-02（G-GEAR で round 4 の直しと作業中の点検を終えたセッションの最後に）。
> 前の引き継ぎ `next-session-ime-paper-m3-round4-fixes.md` の後継（その §2 は済み・§3〜§5 はこのメモが置き換える）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 113・117・119・120**）・`tasklist.md`（M3）と、事前登録 `papers/ime-observation/experiment/preregistration.md` の **§3.1・§3.4**。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（★ Mac〔測定機〕で。パイロットの生ログ・封印物・`keys-out` は Mac にだけある）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m3-mac-work.md を読んで §2 から始めてください。
一次は decisions.md の判断 113・117・119・120 と、事前登録 §3.1・§3.4。
Mac の作業（預ける基準・合わせ直しの診断・delivery.py で k とモードキーと焦点の喪失を確かめる）→ 定数と文を決める
→ 確認 → コミット・push。その後 G-GEAR で attack-me round 5（§3 のとおり絞る）。
Skill: verify-before-claiming・data-privacy・subagent-delegation・git-workflow。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-02 の終わり・G-GEAR・枝 `feature/ime-m3-prereg`）

- このセッションのコミット: `4bd6cacd`（round 4 の直し・判断 116・117・118）→ `ec2eef7b`（作業中の点検を受けた直し・判断 119・120）→ `9428bd98`（steering の記録）→ このメモのコミット。
- **round 4 の直しは済み**（Z1・Z2・minor 8・nit 8）。作業中の点検（code-reviewer ∥ security-checker）も済み。研究者に 2 問 → 判断 119（**`--pack` が完了・中止を問わず §3.4 の規則を当てる／S15 以外の焦点の喪失を中止に足す**）。
- §3.4 の中止の理由は 3 つ: 計画の SHA-256 の違い・参照の外からの打鍵（ブロックごとの区間の「説明されない key_down」が「印＋k〔最後のブロックの区間は印だけ〕」を超える）・S15 以外の焦点の喪失（`reference_focus_loss.n_loss_intervals_unplanned > 0`）。`delivery.py` が exit 2 なら中止。
- **暫定の定数が 2 つ**（`kit/analysis/pipeline.py`）: `RUNNER_KANA_PRESSES_PER_BLOCK = 1`（k）・`REFERENCE_RECEIVES_MODE_KEYS = True`（S14 のモードキーを送った打鍵に数えるか → `delivery.py` の区間の版 `all_presses` / `excluding_mode_keys` を選ぶ）。**Mac の作業で決める。**
- 確認（G-GEAR）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 0 件・`check_citations.py` 違反なし・`--check-prereg` exit 3・節の参照はすべて実在・本文 13,902 語（`round-4/tmp/measure.py <path>`）。

## §2 Mac の作業（判断 113 の Y4 ＋ 判断 117 の Z3 ＋ 判断 119・120・凍結の前）

対象の run は **`pilot2-on`・`pilot2-off`・`verify-off`**（矢印の印〔`left`・`right`・`left`〕を使った 3 本。`pilot-1` の F13・F14 の印は観測に行が無いので (2) の対象外。(3) は 3 本とも）。パイロットの生成の config は `~/ime-pilot/*-config.json`（2026-10-01 に Mac で確かめた・`tasklist.md` の M3「Mac で確かめる 3 点」）。run のディレクトリと `keys-out` の置き場所は Mac で確かめる（`pilot-macos.md` は「kept on the measuring machine」とだけ書く）。⚠️ パイロットの観測は `kit/pilot/seal_obs.py` で封印済み: **使うのは key 行だけの `keys-out` ファイル**。封印した元のファイル（セッション行を含む）は開けない・`--unseal` しない（判断 11）。正解と ImeShadow を突き合わせない。

1. **`experiment/pilot-macos.md` の Raw logs に預ける基準を書く**（時点は「before the freeze」に揃え済み）。基準は本計測と揃える（判断 112・119）: 計画から runner が始めた run・manifest がある・(3) の §3.4 の 2 つの規則（パイロットの印は 3 打鍵・k とモードキーの設定は (3) で決めたもの）に当たらない・`pipeline.py --check-deposit` が通る。観測の余分な行は預けるのを止めない（観測器の結果）。根拠: 人の打鍵は参照に届くか（区間の規則）、参照以外に打つなら参照の焦点が外れる（焦点の規則）。⚠️ 今の下書きの「every key row of the observation … is matched … by a press the executor recorded as sent」は本計測と食い違う（監査役 3-E）ので置き換える。盲点（§7: 置き換わった打鍵・焦点を動かさないショートカット）も 1 文。「封印したセッション行は凍結と本計測の後に預けるためにだけ開け、解析しない」も書く（§3.1 と同じ）。手で打った確認（参照の入力欄と TextEdit・Enter と Escape の試し）は run ではなく預けない（既に書いてある）。
2. **合わせ直しの診断**（§3.1 の 1 つ目の項目）: 使い捨てのスクリプトを scratchpad に置き（repo に入れない）、`kit/e2/closed_set.py` の `read_obs(keys-out)` → `[c for _t, c in events]`、`read_plan(plan)`、`align_plan(cats, rows, obs_os, markers_in_obs=True)` だけを呼ぶ（攻撃・コーパス・手順書は使わない）。run ごとに `n_blocks`・`n_blocks_unscored`・`n_trials_unscored`・`n_presses_unassigned` を出し、**採点したブロックの割合**を §3.1 に書く。⚠️ パイロットの印は 3 打鍵で、S7 の矢印 3 つと同じ区分の並びになる（錨の候補が試行の中にも立つが、ブロック全体が合わない所は飛ばすので診断としては使える）。欠陥が見つかれば凍結の前に直し、直す前と後の割合を書く。
3. **`delivery.py` で §3.4 の設定を決める**（§3.1 の 2 つ目の項目）: 3 本それぞれに §3.4 の命令行（`--pre-ms 20 --tail-ms 300`・`--obs` は `keys-out`）を当て、次を数と時間だけで書く（**キーコードを読まない・写さない**。`delivery.py` は key_down の時刻しか読まない）:
   - (a) かなキー: 参照の `segments`（両版）の最初の区間（block_id null）の `n_unexplained` と、最後でない区間の `n_unexplained_beyond_markers` の分布 → ブロックの前のかなキーが参照に key_down を残すか → **k（0 か 1）**。
   - (b) S14 のモードキー: 参照の `reach` の `all_presses` と `excluding_mode_keys` の差（S14 の試行の数 × 2 と比べる）→ **`REFERENCE_RECEIVES_MODE_KEYS`**。⚠️ 片方のキー（`ime_on`＝104 か `ime_off`＝102）だけ届く場合は、2 版のどちらでも合わない → 研究者に問う（安全側は `excluding_mode_keys`〔届いたモードキーは説明されない行になり中止になりうる〕・または all_presses で S14 に 1 打鍵の余裕を残して §7 に開示）。
   - (c) 滑り: 最後でない区間の `ms_from_last_row_to_next_block` の最小（`focus_cmd` は押した後 0.3 s 待つ）。
   - (d) 焦点: `reference_focus_loss.n_loss_intervals_unplanned`。⚠️ **0 でなければ研究者に戻す**（判断 119: 焦点の規則を考え直す。起動の時・終了の時に参照が focus_out を書くかもここで分かる）。
   - (e) (a)〜(b) で決めた設定で、3 本それぞれに §3.4 の区間の規則が当たらないか（パイロットの印は 3 打鍵として）。
   - **決めたら同じコミットで**: `pipeline.py` の 2 つの定数（「Provisional」のコメントを根拠の短い説明に置き換える）・事前登録 §3.1 の 2 つ目の項目（値と根拠: (a)〜(e) の数）・§3.4 の「k (0 or 1)」「whether the input-mode keys of S14 count」を決めた値の文に・`data.md` の Run checks の前置き（どちらの版か）。selftest は k = 0 / 1 の両方で回る形にしてある（`_case_reference_abort_rule`）。⚠️ 定数と文の食い違いを機械で検査する仕組みは無い（判断 120 の 9）ので、目で照合する。
4. **確認**: `kit/check.sh`（Mac の Python）・`run.sh --synthetic` 2 回でバイト一致・`_style_check.py`（repo 直下から `papers/ime-observation`）・`check_citations.py`・`--check-prereg` exit 3・節の参照の実在。
5. コミット（`docs(paper-kit)` か `fix(paper-kit)`・パス指定）→ `tasklist.md` の Mac の項目を更新 → push。

## §3 その後（G-GEAR）: attack-me round 5 → 完了時レビュー → PR

- **round 5**（判断 117）: 同じ立場・同じ接地（原本 8 本の SHA-256 を `round-1/panel.md` と照合）。対象は round 4 の後に変わった箇所: 事前登録の §2.1・§3.1・§3.3・§3.4・§5・§6.2・§6.3・§6.4・§6.6・§6.7・§6.8・§7、`data.md`・`pilot-macos.md`・`kit/e2/README.md`・`delivery.py`（区間・2 版・焦点の分類）・`pipeline.py`（中止の規則・預ける前の強制）・`closed_set.py`（錨）・`l2.py`（`per_trial` の空の層）・`spec_predict.py`（`plan_figures`）。`git diff 40ad7801..<head> -- papers/` から測り直す。
- 資料は round 4 の `round-4/context-A.md` ほかを写して「変わった箇所」を差し替える。⚠️ round 4 の context-A の §6.7 の要約に「none of the four layers」の誤りがある（直す）。役ごとの `carryover-*.md` は round 4 の新しい指摘・判定の解消／未解消・裏取り（`round-4/verdict.md` §2）・採否（判断 116・117・119）・対応（判断 118・120）。⚠️ 他の役の指摘は渡さない・他の役を名指ししない。採らなかったもの（k の階級ごとの報告・主を k ≥ m に限る・runner を変える・題の nit・設計効果の式の出典・定数と §3.1 の機械照合）を正直に書く。作業中の点検（code-reviewer・security-checker）の指摘も、査読者の指摘と同じく「採否と対応」に含めてよいが、点検した者を名指ししない。
- 応答の保存は round 4 と同じ（本文をメインが Write で `round-5/tmp/<名>.raw.md` に書き写し、`scripts/secrets-filter.sh` と `round-4/tmp/check_resp.py` を `RD` を `round-5` にした写しで検査）。⚠️ 依頼文の「読んでよいファイル」に「Grep は一覧のファイルだけを対象にする（ディレクトリ全体を Grep しない）」を足す（round 2・4 の偽陽性の型）。一覧の外のファイルを Read したと申告したら、写さずに研究者に問う。
- 接地の引用の照合は `round-4/tmp/quote_check.py`。裏取りで計画と予測を使うときは §2.4 のコマンドで scratchpad に作る（SHA-256 は ON `c7a5469d…`・OFF `3759ebf7…`）。予測と `plan_figures` は `spec_predict.py --from-plan --plan <plan> --out <file>`。⚠️ Windows の Python に `/c/...` のパスを渡さない（`C:\...`）。
- 起動の前に研究者へ知らせる（G-GEAR に Zenodo のトークンがある・`sealed/` と生ログは無い）。
- **完了時レビュー**: code-reviewer ∥ security-checker ∥ Codex（`scripts/run-codex-review.sh <base>..<head> -- papers/ime-observation docs/references.md`・出力は scratchpad・2 巡）。範囲は `git merge-base origin/main HEAD`..HEAD のコミット済みだけ。Codex の台帳は回す前に origin/main の当日分も見る。⚠️ レビューの作業用エージェントに `kit/check.sh`・`pipeline.py --selftest`（約 35 秒）を回させない。
- origin/main を取り込み → push → PR → CI 緑なら merge → main の CI（git-workflow ルール 6）。⚠️ 凍結は研究者の別の段（OSF の登録は研究者）。

## §4 気をつけること

- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印は開けない。人の打鍵データを使わない。参照のログのキーコードを表示・転記しない（数と時間だけ）。
- ⚠️ 名前（round 3・4 で変えたもの）: `delivery.py` の出力は各側の `segments` が `{"all_presses": …, "excluding_mode_keys": …}` の 2 版で、各版に `max_beyond_markers_before_last_block`・`beyond_markers_last_block`・区間ごとの `ms_from_last_row_to_next_block`。`reference_focus_loss` に `n_loss_intervals_planned` / `n_loss_intervals_unplanned`。`l2.py` の `per_trial` の各行に `status`（`ok` / `no_trial`）と層ごとの `trials_not_used`。`spec_predict.py --from-plan` の出力に `plan_figures`。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。G-GEAR では main は別の worktree が checkout している。
- ⚠️ git-bash で `git show origin/main:<path>` は MSYS がパスを書き換える → `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない（Windows のパスや行末の `\` を含む文書は Write / Edit で書く）。
- ⚠️ round 1〜4 の `tmp/` は attack-me を閉じるまで消さない。
