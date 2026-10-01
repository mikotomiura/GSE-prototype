# 次セッション — IME 論文: M3 の attack-me round 4 → Mac の作業 → 完了時レビュー → PR

> 作成: 2026-10-02（G-GEAR で round 3 と、その直しを終えたセッションの最後に・コンテキスト約半分で区切った）。
> 前の引き継ぎ `next-session-ime-paper-m3-round3.md` の後継。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 112〜115**）・`tasklist.md`（M3）・`attack-me/prereg-ime-macos/round-3/verdict.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（G-GEAR 推奨: 接地の本文 `round-1/tmp/sources/` と round 1〜3 の生の応答 `round-*/tmp/` は G-GEAR にだけある）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m3-round4.md を読んで §2 から始めてください。
一次は decisions.md の判断 112〜115 と attack-me/prereg-ime-macos/round-3/verdict.md。round 3 の直しは済み（判断 115）。
attack-me round 4（round 3 の直しで変わった節とコードに絞る）→ 研究者に判定と採否を問う → 直す → Mac の作業（判断 113）→ 完了時レビュー → PR。
Skill: attack-me・verify-before-claiming・subagent-delegation・citation-ssot・implementation-workflow・git-workflow。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-02 の終わり・G-GEAR・枝 `feature/ime-m3-prereg`・push 済み）

- このセッションのコミット（`abc5d7f9` の後）:
  - `5fd17972` docs(steering): attack-me round 3 の記録（`round-3/` の 16 ファイル）と研究者の採否（判断 112〜114）
  - `88d96553` fix(paper-kit): 問 3 の量を範囲の上で定義し直す（`l2.py`）・`uncontaminated_trials`（`match.py`）・`align_blocks` の欠陥（`closed_set.py`）・焦点の喪失の区間（`delivery.py`・`pipeline.py`）・事前登録 / `data.md` / `notes.md` / `kit/e2/README.md`
  - `f961175b` docs(steering): 判断 115（実装上の選択）と tasklist
  - （このメモは、このメモだけのコミット）
- round 3 の結果: R1 minor・R2 major・R3 major・fatal 0・捏造 0 → 判定 major revision。研究者に 6 問 → すべて推奨どおり（判断 112〜114）。
- 確認（このセッション）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 違反 0 件（repo 直下から相対パス `papers/ime-observation` で）・`check_citations.py` 違反なし・`--check-prereg` exit 3（未凍結）・§9 の SHA-256 の表の 5 ファイルは今の値と一致・本文の「section N」はすべて実在。変異は判断 115 の 6a と tasklist に記録。
- コードは Sonnet の作業用エージェント 3 本が書き（A `l2.py`・`match.py`／B `closed_set.py`・`kit/e2/README.md`／C `delivery.py`・`pipeline.py`）、メインが差分を読み、selftest・抜き取りの変異・合成の結果で確かめた。⚠️ **作業中の点検（code-reviewer ∥ security-checker）と完了時レビューはまだ**。
- 事前登録の本文は 12,143 語（round 2 の版 9,326・round 3 の版 11,217。測り方は `round-3/tmp/measure.py`〔git が無視する〕）。
- Codex の台帳: 10-01 は main で 354,180 / 上限 300,000（超過）。回す前に origin/main の台帳の当日分を見る（memory: Codex ledger split by branch）。

## §2 attack-me round 4（Skill attack-me・判断 114: round 3 の直しで変わった箇所だけ）

- 対象物: `papers/ime-observation/experiment/preregistration.md`（`88d96553` 以降の版）。stage `prereg`・投稿先 BRM。置き場 `.steering/20260927-ime-observation-paper-eval-design/attack-me/prereg-ime-macos/round-4/`。
- 同じ立場（R1 計測の道具の検証・R2 書字研究の利用者と公開の安全・R3 統計と事前登録）と意図の監査役。同じ接地（本文は `round-1/tmp/sources/`。着手時に原本 8 本の SHA-256 を `round-1/panel.md` と照合）。⚠️ `round-1/tmp/`〜`round-3/tmp/` は attack-me を閉じるまで消さない。
- **絞り方**（`git diff abc5d7f9..f961175b -- papers/` から測った）: 事前登録は §1.2・§3.1・§3.2・§3.3・§3.4・§4.5・§4.6・§6.1・§6.2・§6.3・§6.4・§6.6・§6.7・§6.8・§6.9・§6.11・§7。公開物は `data.md`（手順 1 と Run checks の表）・`notes.md`・`kit/e2/README.md`。コードは `l2.py`（`text_layout`・`aggregate`・`mixture_bias`・`_outside_report`・`evaluate`・`MEASURES`）・`match.py`（`parse_prediction`・`evaluate`）・`delivery.py`（`_loss_intervals`・`_focus_losses`・`evaluate`）・`pipeline.py`（`_focus_loss`・`run_stages`・`analyse`）・`closed_set.py`（`align_blocks`）。context-A の一覧のファイルは round 3 と同じ（増減なし）。round 3 の context-A を写して「変わった箇所」を差し替える。
- 役ごとの `carryover-*.md`: その役の **round 3 の新しい指摘**（`round-3/review-*.md` §4・`audit.md` §1〜3）と、round 3 の判定で「部分的に解消／未解消」だったもの・メインの裏取り（`round-3/verdict.md`）・研究者の採否（判断 112〜114）・対応（判断 115 と事前登録の節）・採らなかったもの。⚠️ 他の役の指摘は渡さない・他の役を名指ししない。
  - 採らなかった・残したもの（carryover に正直に書く）: 題の nit（任意・変えていない）・設計効果の式の出典（足していない）・冗長さは設計効果と打ち切りの規則だけ 1 か所に寄せた（`all_trials` の依存は §6.4・§7・`notes.md`・`PRIMARY_NOTE` に残る）・R2 minor-5（中間の粒度・round 1 から未採用）・R2 B の (b) テキスト単位の解析（今後の課題）・R2 A / R3 1 の (b)(c)・R1 N-1 の (1)〜(5) のうち (1) 重複の許容幅（観測の余分な行は中止の理由にしない、で包んだ）・`delivery.py` に判定の欄を足すこと（記述の道具のまま）。
  - ⚠️ §3.1 の Mac の 2 つ（預ける基準・パイロットの key 行の合わせ直し）は**約束の文だけ**で、中身はまだ無い（判断 113。§3 の Mac の作業）。round 4 の carryover にそう書く。
- 文脈 B: 判断 85〜115（判断 112〜115 が新しい意図）。round 3 の context-B を写し、持ち帰り 2 の範囲の書き方（問 3 の量は範囲の中の試行の上）と既知の限界（Mac の約束）を足す。
- **起動の前に研究者へ知らせる**（この機械に Zenodo のトークンがある・`sealed/` と生ログは無い）。
- 応答の保存: round 3 では 4 本とも**転写ファイル（`tasks/*.output`）が 0 行**だったので、届いた報告の本文をメインが Write で `round-4/tmp/<名>.raw.md` に書き写し、`scripts/secrets-filter.sh` と `round-3/tmp/check_resp.py` を round 4 用に写したもの（`RD` を `round-4` に）で検査してから写した（round 3 の verdict §5 の逸脱 1）。一覧のファイルの**親ディレクトリ**だけを書いた行は検査が一覧の外と判定する（偽陽性・round 2 の逸脱 2）。
- 接地の引用の照合は `round-3/tmp/quote_check.py`。⚠️ PDF の頁の柱・頁番号・行末のハイフン・合字「ﬁ」が挟まると外れる。外れたら断片で `tr '\n' ' ' | grep -o` して確かめる（round 3 で 6 件がこれ・捏造は 0）。
- 返ってきた指摘はメインが一次（コード・計画・事前登録）で裏取りしてから verdict に書く（★ round 3 では合わせ直しの欠陥を `align_blocks` を合成の列で動かして確かめた・設計効果は計画を生成して計算した。計画は §2.4 のコマンドで scratchpad に作る: SHA-256 は ON `c7a5469d…`・OFF `3759ebf7…`）。採否は研究者（AskUserQuestion・推奨と理由を添える）。

## §3 その後

- 直し → 確認（§1 と同じ一式＋変異）。
- **Mac の作業（判断 113・凍結の前）**: (1) `pilot-macos.md` の Raw logs に預ける基準と「封印したセッション行は預けるときだけ開け、解析しない」を書く。(2) パイロットの観測の key 行に `align_plan` だけを流し（攻撃はしない・セッション行に触れない。`--markers-in-obs` 相当。パイロットの印は F13/F14/F13 か ← → ← の 3 キーで、`marker_categories` は計画の印から作る）、採点されたブロックの割合を事前登録 §3.1 の最後の文の後に書く。⚠️ round 4 の後に Mac で行うと、この 2 つは attack-me の査読を通らない（小さいので、メインの確認と完了時レビューで足りるかを研究者に確かめる）。
- **完了時レビュー**: code-reviewer ∥ security-checker ∥ Codex（`scripts/run-codex-review.sh <base>..<head> -- papers/ime-observation docs/references.md`・出力は scratchpad・2 巡）。範囲は `git merge-base origin/main HEAD`..HEAD のコミット済みだけ。⚠️ `pipeline.py --selftest` は約 25 秒、`closed_set.py --selftest` は約 20 秒、`kit/check.sh` は約 1.5 分（レビューの作業用エージェントには回させない）。
- origin/main を取り込み → push → PR → CI 緑なら merge → main の CI（git-workflow ルール 6）。⚠️ 凍結は研究者の別の段（OSF の登録は研究者）。

## §4 気をつけること

- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印は開けない。人の打鍵データを使わない。予測器と配送の報告は観測のセッションの行を読まない（配送は key 行だけ）。
- ⚠️ 名前が変わった: L2 の `n_conversions`（テキストの量）→ `conversions_per_trial`（試行ごとの `per_trial` の `n_conversions` は変えていない）・配送の報告の `reference_focus_out` → `reference_focus_loss`（`trials_with_focus_loss`）。`mixture_bias.by_stratum` は区間を持たない（登録の区間は `agreement_by_stratum`）。
- ⚠️ pipeline に S15 の除外を書き戻す変異は pipeline の selftest で赤にならない（合成の run は焦点を失わない）。S15 の判定は `delivery.py` の selftest が守る（判断 115 の 3）。
- ⚠️ 事前登録 §3.1・§3.3 の予測の値は `python3 kit/analysis/spec_predict.py --from-plan --plan <plan> --out <file>` で再現できる。§3.3 の設計効果の値（層あたり 33〜39 / 30〜37 ブロック・Σm²/Σm は 2.4〜3.1 / 2.5〜3.4・区間で最大約 1.8 倍）は 2 つの計画から計算した（使い捨てのスクリプト。必要なら層ごとにブロックの数を数えて Σm²/Σm を取る）。
- ⚠️ `gt_rules.json` は今回変えていない。凍結のハッシュは凍結の段で `--freeze-hash` を取り直す。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。
- ⚠️ main は別の worktree が checkout している（`C:\GSE-prototype` で `git switch main` はできない）。
- ⚠️ git-bash で `git show origin/main:<path>` は MSYS がパスを書き換える → `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない（Windows のパスを含む文書は Write / Edit で書く）。
