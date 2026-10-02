# 次セッション — IME 論文: M3（事前登録の下書き → attack-me → 完了時レビュー → PR → 凍結）

> 作成: 2026-10-01（G-GEAR で、M2 の確認と M3 の下書きを行ったセッションの最後に）。
> 前の handoff（`next-session-ime-paper-m2.md`）の後継。M2 の残り（生ログの預け方・Mac）は前の handoff の §0 B と `tasklist.md` を見る。
> ★ **2026-10-01 追記**: §2 の attack-me round 1 と §4 の Mac の確認は済んだ。続きは **`next-session-ime-paper-m3-fixes.md`**（round 1 の直し → round 2）。§3・§5 はこのメモのまま使う。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（判断 90〜98）・`tasklist.md`（M3 の項目）と、枝の `papers/ime-observation/experiment/preregistration.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

### A. attack-me（どちらの機械でも。G-GEAR を推奨: 封印物 `sealed/` は Mac にしか無い）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m3.md を読んで §2 から始めてください。
Skill attack-me を stage prereg で回す（査読者役 3 人＋意図の監査役・paper-reviewer・Opus）。
起動の前に研究者に知らせる（Read は構造で縛れない）。指摘はメインが一次で裏取りし、直す一覧は研究者が承認する。
Skill: attack-me・verify-before-claiming・subagent-delegation・citation-ssot。応答は日本語。コミットは git add パス指定（-A 禁止）。
```

### B. Mac で確かめること（A と並行してよい）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない。このメモと plan_config.macos.json はこの枝にだけある）。
.steering/_handoff/next-session-ime-paper-m3.md の §4 の 3 点を Mac で確かめ、結果を tasklist.md に書く。
push の前に git fetch → git pull --no-rebase（G-GEAR も同じ枝に attack-me の記録を push する）。
M2 の残り（パイロットの生ログの預け方）は、この枝ではなく main から別の枝を切って行う。前の handoff（next-session-ime-paper-m2.md）の §0 B を見る。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow。応答は日本語。
```

## §1 状態（2026-10-01 の終わり・G-GEAR）

- main は `538517a1`（PR #286 まで）。
  - #285（Mac）: M2 の大半（正解の定義・持ち越し・`pilot-macos.md`・判断 85〜89）。
  - #286（G-GEAR）: M2 の G-GEAR の確認（024 の一覧の SHA-256 が Mac の `bc2e6816…5f3c`〔94 ファイル〕と一致・Windows で回る 22 本は SCOPE / GUARD を除いて失敗 0 件）と、研究者の判断 90〜97。
- 枝 **`feature/ime-m3-prereg`**（push 済み・**PR はまだ**）。main の merge コミット `538517a1` はまだ取り込んでいない（中身の差は無い）。
  - `c290e3d3` feat: `gt_sessions.py` に `n_continued_commits`、`l1.py` に `abandon_by_continued_commit`（判断 96）。`l1.py` / `l2.py` の `dwell_ms == 0` の文言（判断 95）。
  - `8d62ea17` docs: `pilot-macos.md` の時計（判断 94）・`e2/README.md` の推奨の粒度（判断 97）・`cell.example.json` と `run/README.md`（判断 91）・`notes.md` の書き直し（判断 98 の 8）。
  - `8ec48cb0` docs: **`experiment/preregistration.md`（下書き）**・`experiment/plan_config.macos.json`・`docs/references.md` の `[V184]`〜`[V189]`。
  - `706f3333` steering: 判断 98・tasklist。
- 確かめたこと（G-GEAR・Python 3.11.9）: `kit/check.sh` 27 本緑・`run.sh --synthetic` 2 回でバイト一致・変異 6 本が赤・`--check-prereg` は exit 3（未凍結）・`_style_check.py` 違反 0 件・`check_citations.py` 違反なし。
- ⚠️ **完了時レビュー（/cross-review）はまだ**。attack-me の対応で下書きが変わるので、その後にまとめて回す（§3）。
- Codex の台帳: main の 2026-10-01 は 354,180 / 9 回（上限 300,000 を超えている）。この枝は台帳を変えていない。

## §2 attack-me（stage `prereg`）

- 対象物: `papers/ime-observation/experiment/preregistration.md`（下書き・commit 済み）。投稿先は BRM（Behavior Research Methods）。
- ★ Skill の「読んでよいファイルの一覧」に、固定の根拠のファイルまで入れる（前の handoff §4）:
  `experiment/` の `preregistration.md`・`plan_config.macos.json`・`config.json`・`gt_rules.json`・`SEED`・`run.sh`・`notes.md`・`pilot-macos.md`・`data.md`／
  `kit/analysis/` の `pipeline.py`・`gt_sessions.py`・`match.py`・`l1.py`・`l2.py`・`stats.py`／`kit/gen/README.md`・`recipes.json`・`recipes.macos-live-off.json`／
  `kit/e2/README.md`・`kit/e3/README.md`・`kit/run/README.md`・`kit/pilot/README.md`・`kit/logger/README.md`。
- ⚠️ 生ログ・`runs/`・`sealed/` は渡さない（G-GEAR には無い。Mac で回すなら特に注意）。
- 意図の監査役に渡す B（内部の意図）: `requirement.md`・`design.md`・`decisions.md` の判断 85〜98・この handoff。
- 査読の記録は `.steering/20260927-ime-observation-paper-eval-design/attack-me/`（Skill の置き場の規則に従う）。公開物の中に置かない。
- 下書きで、こちらが特に確かめてほしい点（自己申告）:
  1. 推定の書き方で「何が分かれば informative か」が §3.3 の Wilson の半幅だけで、連続量（dwell の誤差・ICC）には精度の目標が無い。
  2. E2 の「2/K」の判定は Wilson の上端で、ブロック内の相関を一部しか吸収しない。
  3. 学習をリセットしない（判断 91）ことの影響の書き方。
  4. 観測側（macOS）は Return 1 回でセッションを閉じるが、ライブ変換 ON の手順は Return 2 回（正解は 2 回目で閉じる）。dwell の偏りはこの構造から予想できる → 事前登録に「予想」を書くか（書けば検定の形になる・書かなければ後付けの説明に見える）は研究者の判断。⚠️ 観測の値は見ていない（構造はコードの仕様から分かる）。
  5. E3 の `working` で ON のセルの計画（約 11.9 時間）を流し、8 時間で止める（判断 98 の 4）。

## §3 attack-me の後

1. 直す一覧を研究者が承認 → 直す → 必要なら 2 巡目。
2. 完了時レビュー: code-reviewer ∥ security-checker ∥ Codex（`scripts/run-codex-review.sh <base>..<head> -- papers/ime-observation docs/references.md`）。回す前に origin/main の台帳の今日の値を見る。
3. origin/main を取り込む → push → PR → CI 緑なら merge → main の CI（git-workflow ルール 6）。
4. ⚠️ 凍結は PR の merge とは別の段（研究者）。

## §4 Mac で確かめること

1. 本番の計画を Mac で生成し、SHA-256 を G-GEAR の値と比べる（生成器の README は「バイト一致は同じ機械・同じ Python でだけ保証」）。コマンドは事前登録 §2.4（`--seed 20260929`）。G-GEAR（Python 3.11.9）の値: ON（`recipes.json`）`c7a5469de0febbbc2e90259e477900ab0eb68c74b86f420b1e9491799a1210ba`・OFF（`recipes.macos-live-off.json`）`3759ebf7832ba561820abab504929dbadd7e775a33e22ba0e89b92e4800009a2`。食い違えば、本番は Mac で生成した計画を使い、事前登録の書き方（「計画の SHA-256 は run の manifest に記録」）で足りるかを研究者と確かめる。
2. パイロットの生成の config の全体（`cand_index_max`・`key_hold_ms`・`iki_sigma`・`inter_trial_ms`・`marker_gap_ms`）。repo の記録は速さ・think・n・マーカーだけ（判断 90）。本番の値（判断 98）と違うものがあれば、事前登録 §3.1 に書く。
3. `gt_sessions.py --selftest`・`l1.py --selftest`・`kit/check.sh` を macOS（Python 3.14）で回す。

## §5 凍結の手順（研究者・attack-me と PR の後）

1. 下書きの直しが済み、main に入っていること。
2. `python3 kit/analysis/pipeline.py --freeze-hash --config experiment/config.json --seed-file experiment/SEED` の値を `sha256:` の行に、日付を `frozen_at:` の行に書く（コメントとコードフェンスの外・各 1 行）。
3. `run.sh` の門が通ること（`--check-prereg` が exit 0）を確かめて commit → タグ。
4. 024 の書き出しの一覧の SHA-256 を測る（両機械で一致）。
5. OSF Registries に登録（研究者・すぐ公開・判断 93）。URL と日時を `experiment/notes.md` に書く。登録の日時が最初の本計測より前。
6. その後に M4（macOS 本計測・1 晩 1 セル・約 12 時間）。

## §6 気をつけること

- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印は開けない。人の打鍵データを使わない。
- ⚠️ `pilot-macos.md` は Mac の M2 の残り（Raw logs の節）とこの枝（Clocks の 1 文）の両方が触る。merge の衝突に注意（節が違うので自動で済むはず）。
- ⚠️ Codex の台帳は枝ごとに記帳される。merge では両側の増分を合算する（`git checkout --` で戻さない）。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。
- ⚠️ main は別の worktree（`C:/wt/p321-submission`）が checkout しているので、`C:\GSE-prototype` で `git switch main` はできない。検証は `git worktree add --detach <dir> origin/main` で clean な worktree を作る（今回は `C:/wt/clean-m2`・片付けてよい）。
