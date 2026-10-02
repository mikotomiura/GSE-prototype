# 次セッション — IME 論文: M3 の attack-me round 2 → 完了時レビュー → PR

> 作成: 2026-10-01（G-GEAR で round 1 の直しを終えたセッションの最後に・コンテキスト約 50% で区切った）。
> 前の引き継ぎ `next-session-ime-paper-m3-fixes.md` の §2 F・G の後継。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 99〜107**）・`tasklist.md`（M3）・`attack-me/prereg-ime-macos/round-1/verdict.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（G-GEAR 推奨: round 1 の接地の本文 `round-1/tmp/sources/` は G-GEAR にだけある）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m3-round2.md を読んで §2 から始めてください。
一次は decisions.md の判断 99〜107 と round-1/verdict.md。round 1 の直しは済み（判断 107）。
attack-me round 2 → 研究者に判定と採否を問う → 直す → 完了時レビュー → PR。
Skill: attack-me・verify-before-claiming・subagent-delegation・citation-ssot・implementation-workflow・git-workflow。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-01 の終わり・G-GEAR・枝 `feature/ime-m3-prereg`）

- このセッションのコミット（`b682abad` の後）:
  - `1fbd7942` feat(paper-kit): 範囲（`under_limit` / `all_trials` / `over_limit`）と 3 つの照合（`gt_obs` 主・`gt_pred`・`pred_obs`）・診断の層・L1 の LoA / kappa の区間と速さ別・L2 の試行ごとの差・`delivery.py`（新規・配送の報告と焦点の喪失）・合成の run の打鍵
  - `29372289` docs(paper-kit): 事前登録の書き直し（節番号を振り直した: 予測 §4.5・範囲と比較 §6.4・E2 §6.8・脅威と限界 §7・追補 §8・凍結 §9）・`config.json` / `gt_rules.json` の `_note`（凍結のハッシュに入る）・公開物の古い記述
  - （decisions 判断 107・tasklist・このメモは、このメモと同じコミット）
- 確認（このセッション）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイル（`e1_l1` / `e1_l2` / `e1_detection` / `e1_delivery`）ともバイト一致・`_style_check.py` 違反 0 件（★ **repo 直下から相対パス `papers/ime-observation` で回す**。絶対パスで渡すと逐語コピーの除外が効かず 1,274 件と出る）・`check_citations.py` 違反なし・`--check-prereg` exit 3（未凍結）。変異 31 本（判断 107 の 9）。
- **完了時レビューはまだ**（round 2 で直しが出るので後に回した）。⚠️ 作業中の点検（code-reviewer ∥ security-checker）もまだ。`delivery.py` は Sonnet の作業用エージェントが書き、メインが読んで selftest を回し、焦点の喪失を足した。
- Codex の台帳: 10-01 は main で 354,180 / 上限 300,000（超過）。日が変われば戻る。回す前に origin/main の台帳の当日分を見る（memory: Codex ledger split by branch）。

## §2 attack-me round 2（Skill attack-me）

- 対象物: `papers/ime-observation/experiment/preregistration.md`（`29372289` 以降の版）。stage `prereg`・投稿先 BRM。
- 置き場 `.steering/20260927-ime-observation-paper-eval-design/attack-me/prereg-ime-macos/round-2/`。
- 同じ立場（R1 計測の道具の検証・R2 書字研究の利用者と公開の安全・R3 統計と事前登録）と意図の監査役。同じ接地の文献（本文は `round-1/tmp/sources/` を使ってよい。⚠️ `tmp/` は attack-me を閉じるまで消さない）。
- 役ごとの `carryover-R1.md`〜`R3.md`・`carryover-audit.md` を作る: その役の round 1 の指摘・メインの裏取り（verdict の真偽）・研究者の採否（判断 99〜106）・対応（判断 107 と事前登録の節番号）・未解決（群 M の文献の段落は原稿へ回した・パイロットの生ログの基準は Mac の M2 の残り）。⚠️ 他の役の指摘は渡さない。依頼文に「再掲を求めない・解消を 1 件ずつ判定してから新しい穴」。
- ⚠️ round 1 からの**節番号の変化**を carryover に書く（例: 旧 §6.6 Q3 → §6.7、旧 §6.7 E2 → §6.8、旧 §7 → §8、旧 §8 → §9、新 §4.5・§6.4・§7）。
- **起動の前に研究者へ知らせる**（この機械に Zenodo のトークンがある・`sealed/` は無い）。
- 返ってきた指摘はメインが一次（コード・計画・事前登録）で裏取りしてから verdict に書く。採否は研究者（AskUserQuestion・推奨と理由を添える）。

## §3 その後

- 直し → 確認（§1 と同じ一式）→ **完了時レビュー**: code-reviewer ∥ security-checker ∥ Codex（`scripts/run-codex-review.sh <base>..<head> -- papers/ime-observation docs/references.md`・出力は scratchpad・2 巡）。範囲は `git merge-base origin/main HEAD`..HEAD のコミット済みだけ。⚠️ `pipeline.py --selftest` は約 25 秒、`kit/check.sh` は約 2 分（レビューの作業用エージェントには回させない）。
- origin/main を取り込み → push → PR → CI 緑なら merge → main の CI（git-workflow ルール 6）。⚠️ 凍結は研究者の別の段（OSF の登録は研究者）。

## §4 気をつけること

- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印は開けない。人の打鍵データを使わない。予測器と配送の報告は観測のセッションの行を読まない（配送は key 行だけ）。
- ⚠️ 事前登録 §3.1・§3.3 の予測の値（ON `long` 677 / 3,150 など・打ち切りの後に残る試行数の表）は、計画の時刻から組んだ擬似 oracle（送出の遅れなし・ブロックの間 2 s）から出した。再計算の手順は判断 107 の 7（使い捨てのスクリプトは scratchpad で、repo に無い）。§9 の SHA-256 の表は、計画の設定・手順書・コーパス・キーマップが凍結の前に変わったら更新する。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。
- ⚠️ main は別の worktree が checkout している（`C:\GSE-prototype` で `git switch main` はできない）。
- ⚠️ git-bash で `git show origin/main:<path>` は MSYS がパスを書き換える → `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない（Write ツールで書く）。
