# 次セッション — IME 論文: M3 の attack-me round 3 → 完了時レビュー → PR

> 作成: 2026-10-01（G-GEAR で round 2 と、その直しを終えたセッションの最後に・コンテキスト約 50% で区切った）。
> 前の引き継ぎ `next-session-ime-paper-m3-round2.md` の後継。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 108〜111**）・`tasklist.md`（M3）・`attack-me/prereg-ime-macos/round-2/verdict.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（G-GEAR 推奨: 接地の本文 `round-1/tmp/sources/` と round 2 の生の応答 `round-2/tmp/` は G-GEAR にだけある）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m3-round3.md を読んで §2 から始めてください。
一次は decisions.md の判断 108〜111 と attack-me/prereg-ime-macos/round-2/verdict.md。round 2 の直しは済み（判断 111）。
attack-me round 3（変わった節とコードに絞る）→ 研究者に判定と採否を問う → 直す → 完了時レビュー → PR。
Skill: attack-me・verify-before-claiming・subagent-delegation・citation-ssot・implementation-workflow・git-workflow。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-01 の終わり・G-GEAR・枝 `feature/ime-m3-prereg`）

- このセッションのコミット（`384712ee` の後）:
  - `76a1d439` docs(steering): attack-me round 2 の記録（`round-2/` の 16 ファイル）と研究者の採否（判断 108〜110）
  - `0bb61430` feat(paper-kit): `long` を打鍵が入った試行すべてに（`spec_predict/2`・`--from-plan`）・問 3 の主を `under_limit` に・`l2.py` の区間と `per_trial_layer_none`・E2 のブロックでの合わせ直し・焦点の喪失の行・範囲の組成
  - `6fa79171` docs(paper-kit): 事前登録の直し（判断 108〜110 と `verdict.md` §3 の minor 26・nit 12）・公開物・`gt_rules.json` の `_note`
  - （判断 111・tasklist・このメモは、このメモと同じコミット）
- round 2 の結果: R1 minor・R2 major・R3 minor（条件つき）・fatal 0・捏造 0 → 判定 major revision。研究者に 10 問 → すべて推奨どおり（判断 108〜110）。
- 確認（このセッション）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 違反 0 件（repo 直下から相対パス `papers/ime-observation` で）・`check_citations.py` 違反なし・`--check-prereg` exit 3（未凍結）・§9 の SHA-256 の表は今の値と一致・本文の「section N」はすべて実在。変異 17 本すべて赤（判断 111 の 9）。
- **完了時レビューはまだ**（round 3 で直しが出うるので後に回した）。⚠️ 作業中の点検（code-reviewer ∥ security-checker）もまだ。`l2.py` と `kit/e2/*` は Sonnet の作業用エージェントが書き、メインが差分を読み、selftest と抜き取りの変異で確かめた。
- 事前登録の本文は 11,217 語（round 1 の版 5,307・round 2 の版 9,326。測り方は `round-2/tmp/measure.py`〔git が無視する〕）。
- Codex の台帳: 10-01 は main で 354,180 / 上限 300,000（超過）。日が変われば戻る。回す前に origin/main の台帳の当日分を見る（memory: Codex ledger split by branch）。

## §2 attack-me round 3（Skill attack-me・研究者の選択: 変わった節とコードに絞る＝判断 110）

- 対象物: `papers/ime-observation/experiment/preregistration.md`（`6fa79171` 以降の版）。stage `prereg`・投稿先 BRM。置き場 `.steering/20260927-ime-observation-paper-eval-design/attack-me/prereg-ime-macos/round-3/`。
- 同じ立場（R1 計測の道具の検証・R2 書字研究の利用者と公開の安全・R3 統計と事前登録）と意図の監査役。同じ接地の文献（本文は `round-1/tmp/sources/` を使ってよい。原本の SHA-256 を着手時に `round-1/panel.md` と照合する）。⚠️ `round-1/tmp/`・`round-2/tmp/` は attack-me を閉じるまで消さない。
- **絞り方**: context-A に「round 2 から変わった箇所」の一覧を書く（`git diff 384712ee..HEAD -- papers/ime-observation/experiment/preregistration.md` から節ごとに。§1.1・§1.2・§3.1・§3.2・§3.3・§3.4・§4.4・§4.5・§6.1・§6.2・§6.4・§6.6〜§6.10・§7・§8・§9 と題）。依頼文に「今回の直しが作った穴を重点に」「変わっていない節は round 2 の判定のまま再掲しない」と書く。コードは `spec_predict.py`・`match.py`・`pipeline.py`・`l2.py`・`closed_set.py`・`open_set.py`・`delivery.py` の変わった関数を名指す（判断 111）。
- 役ごとの `carryover-*.md`: その役の **round 2 の新しい指摘**（`round-2/review-*.md` §4・`audit.md`）と round 2 の判定表で「部分的に解消／未解消」だった round 1 の指摘・メインの裏取り（`verdict.md`）・研究者の採否（判断 108〜110）・対応（判断 111 と事前登録の節）・採らなかったもの。⚠️ 他の役の指摘は渡さない・他の役を名指ししない。
  - 採らなかった・残したもの（carryover に正直に書く）: R2 minor-5（中間の粒度・round 1 から未採用。§7 に「評価していない」と書いた）・R2 nit 3（説明の重複を寄せる・任意で未着手）・R3 M2 の「2/K の根拠」（§7 に「設計の選択で、プライバシーの基準から導いていない」と書いた）・パイロットの生ログを預ける基準そのもの（Mac の残りの作業。事前登録には預ける約束を戻した）。
- 文脈 B: 判断 85〜111（判断 108〜111 が新しい意図）。持ち帰り 1 の「決定の規則」は `no_time`・`counts_only` だけに変わった（判断 109）ので context-B を直す。
- **起動の前に研究者へ知らせる**（この機械に Zenodo のトークンがある・`sealed/` は無い）。
- 応答の保存は `round-2/tmp/check_resp.py` を round 3 用に写して使う（一覧のファイルの**親ディレクトリ**だけを書いた行は検査が一覧の外と判定する＝偽陽性。round 2 の逸脱 2）。
- 返ってきた指摘はメインが一次（コード・計画・事前登録）で裏取りしてから verdict に書く。採否は研究者（AskUserQuestion・推奨と理由を添える）。

## §3 その後

- 直し → 確認（§1 と同じ一式＋変異）→ **完了時レビュー**: code-reviewer ∥ security-checker ∥ Codex（`scripts/run-codex-review.sh <base>..<head> -- papers/ime-observation docs/references.md`・出力は scratchpad・2 巡）。範囲は `git merge-base origin/main HEAD`..HEAD のコミット済みだけ。⚠️ `pipeline.py --selftest` は約 25 秒、`closed_set.py --selftest` は約 20 秒、`kit/check.sh` は約 2 分（レビューの作業用エージェントには回させない）。
- origin/main を取り込み → push → PR → CI 緑なら merge → main の CI（git-workflow ルール 6）。⚠️ 凍結は研究者の別の段（OSF の登録は研究者）。

## §4 気をつけること

- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印は開けない。人の打鍵データを使わない。予測器と配送の報告は観測のセッションの行を読まない（配送は key 行だけ。焦点の喪失の行を数えるのは pipeline）。
- ⚠️ 事前登録 §3.1・§3.3 の予測の値は `python3 kit/analysis/spec_predict.py --from-plan --plan <plan> --out <file>` で再現できる（計画は §2.4 のコマンドで生成。SHA-256 は ON `c7a5469d…`・OFF `3759ebf7…`）。§3.3 の精度の表は `stats.wilson(round(p*n), n)` の半幅。§9 の SHA-256 の表は、計画の設定・手順書・コーパス・キーマップが凍結の前に変わったら更新する。
- ⚠️ `gt_rules.json` の `_note` を直したので、凍結のハッシュの値は変わった（凍結の前なので問題ない。凍結の段で `--freeze-hash` を取り直す）。
- ⚠️ 予測の形式は `spec_predict/2`（`match.py` は `received_carry` を必須にした）。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。
- ⚠️ main は別の worktree が checkout している（`C:\GSE-prototype` で `git switch main` はできない）。
- ⚠️ git-bash で `git show origin/main:<path>` は MSYS がパスを書き換える → `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない（Write / Edit ツールで書く。このセッションでも heredoc の `\` で置換が 1 回空振りした）。
