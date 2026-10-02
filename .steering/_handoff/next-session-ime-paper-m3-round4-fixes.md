# 次セッション — IME 論文: M3 の round 4 の直し → Mac の作業 → attack-me round 5 → 完了時レビュー → PR

> 作成: 2026-10-02（G-GEAR で attack-me round 4 を回し、研究者の採否まで終えたセッションの最後に・コンテキスト約半分で区切った）。
> 前の引き継ぎ `next-session-ime-paper-m3-round4.md` の後継。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 116・117**）・`tasklist.md`（M3）・`attack-me/prereg-ime-macos/round-4/verdict.md`（§2 の裏取り・§3 の直す一覧）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用（直しは G-GEAR でも Mac でもよい。round 5 は G-GEAR〔接地の本文 `round-1/tmp/sources/` と round 1〜4 の生の応答 `round-*/tmp/` は G-GEAR にだけある〕）

```
git fetch → git switch feature/ime-m3-prereg → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m3-round4-fixes.md を読んで §2 から始めてください。
一次は decisions.md の判断 116・117 と attack-me/prereg-ime-macos/round-4/verdict.md §2・§3。
round 4 の直し（Z1・Z2・minor 8・nit 8）→ 確認 → 作業中の点検（code-reviewer ∥ security-checker）→ Mac の作業（判断 113 ＋ 117）→ G-GEAR で attack-me round 5（絞る）→ 完了時レビュー → PR。
Skill: implementation-workflow・subagent-delegation・verify-before-claiming・attack-me・citation-ssot・git-workflow。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-02 の終わり・G-GEAR・枝 `feature/ime-m3-prereg`）

- このセッションのコミット（`159a2ec8` の後）: `40ad7801` docs(steering): attack-me round 4 の記録（`round-4/` の 16 ファイル）と研究者の採否（判断 116・117）。（このメモは、このメモだけのコミット）
- round 4 の結果: R1 major・R2 major・R3 minor・fatal 0・捏造 0 → 判定 major revision。研究者に 5 問 → すべて推奨どおり（判断 116・117）。
- 公開物とコードは round 3 の直しのまま（`88d96553`）。**round 4 の直しはまだ何もしていない。**
- 事前登録の本文は 12,143 語（測り方は `round-4/tmp/measure.py`〔git が無視する〕）。投稿規程は round 4 で取り直し、17 文とも逐語で在った（`round-4/context-A.md`）。

## §2 round 4 の直し（判断 116・117・`verdict.md` §3）

★ 進め方は round 3 と同じ: コードは Sonnet の作業用エージェント（model を明示・範囲と禁止と締切・`subagent-delegation`）に割り、メインが差分を読み、selftest・抜き取りの変異・合成の結果で確かめる。⚠️ round 3 では**作業中の点検（code-reviewer ∥ security-checker）を飛ばした**。今回はコードの直しの後に必ず回す。

### Z1 §3.4 の中止の規則（判断 116・〔コード〕・最重）

- 何が問題か（裏取り済み）: runner のかなキーは oracle に行が無い。`run_cell.py:585-595` は前のブロックの `em.run_block` の直後に次のブロックの `focus_cmd` を走らせ、`emit.py` の `run_block` は最後の `trial_end` の直後に `block_end` を書いて返る（待ちが無い）。`delivery.py` の窓は `trial_end` + 300 ms で、`CUT_KINDS` は `reset`・`block_begin`・`marker`（`block_end` で切らない）。参照は `keyDown(with:)` に来たすべてを `key_down` に残す（`RefInput.swift:175-176`）。→ かなキーが参照に残り窓に入れば、外からの入力の無い run が `excess_rows` で中止になる。
- 直し方（研究者の選択）:
  - `delivery.py` に、ブロックごとの区間（`block_begin` から次の `block_begin` まで。最初のブロックの前を 1 区間）で「参照の `key_down` のうち、送った打鍵で説明されない数」（区間の行の数 − その区間の試行で到達した打鍵の数〔`min(sent, received)` の和〕）を出させる。かなキーが最後の試行の窓に落ちても外に落ちても同じ数になる。観測の側も記述として同じ数を出してよい（観測の余分な行は中止の理由にしない・判断 112）。
  - 規則（§3.4）: どれかの区間で、この数が「その区間に計画が置く印の打鍵の数＋かなキーの数」を超えたら中止。⚠️ **かなキーを数えるか（1 か 0）は、Mac でパイロットの参照のログに当てた結果で決める**（§3 の (3)）。それまで規則の文とコードは「かなキーの数」を 1 つの定数として持ち、値を決めたら §3.1 に根拠（パイロットの数）を書く。最初の区間（最初のブロックの前）は印が無く、かなキーだけ。最後の区間はかなキーが無い。
  - §3.4 に: 命令行（`--pre-ms 20 --tail-ms 300` を明示）・`delivery.py` が入力を拒んだ（exit 2）run は中止に数える・検査の対象（2 つのセルの run と `working`。`idle` は計画が無い）・外からの入力で中止にした run は預けない（参照のログが key code を持つ・監査役 1-A）・報告の場所（`data.md` の Run checks の表）。§6.3 の最後から 2 文目は「§3.4 の規則で決める」と参照するだけにする（R1 新-3）。§3.2 の「each run」も範囲を合わせる（R1 新-8）。
  - `pipeline.py` も同じ規則を、`analyse` が既に計算する配送の報告から当て、当たる run を拒む（exit 2・メッセージに値を出しすぎない）。selftest に陽性・陰性の対照（説明されない行が上限ちょうど／上限 + 1・かなキーが最後の試行の窓に入る場合と外の場合で同じ判定）。
  - `data.md` の Run checks の表に、区間ごとの最大の「説明されない数」と上限・計画の SHA-256 の欄（監査役 2-A）を。手順 1 も新しい規則に。
  - §7 か §3.4 に「規則は余りの行を数えるので、同じ試行で失われた打鍵と外からの打鍵が入れ替わったものは検出しない」（R3 nit・minor 7）。
- ⚠️ `delivery.py` は記述の道具のまま判定の欄を足さない、という判断 115 の 2 を、区間の数を出すことは破らない（判定は §3.4 と pipeline に置く）。

### Z2 問 3 のテキストの大きさ（判断 116・文だけ）

- §6.7 と §7 に: 主の範囲の一致の限界と ICC は、この設計のテキストあたりの範囲の試行の数（k）の分布の上の値で、速さのあいだで比べない／偏りはテキストに等しい重みの平均／k が小さいほど、片側で値が計算できずに落ちるテキストが増える。メインの計算（計画と予測から）: k の平均は ON で slow 4.60・mid 6.49・fast 7.17、OFF で 4.56・6.43・7.21。slow で k ≤ 3 が 30 / 126・27 / 117、k = 8 は 4・0。k = 0 は無い（数を本文に書くなら、再現できる形にする〔minor 5 の出力に足すなど〕）。

### minor（`verdict.md` §3 の番号）

1. 〔コード〕合わせ直しの錨を右に揃える（`closed_set.py` の `_is_anchor` の左端の条件をやめ、「直後が印の最後の区分でない、印と同じ区分の並び」に）。selftest に「ブロック末の S7（ライブ変換 OFF・`right` × n → think → `enter`）の Enter の欠け」の対照（失うのはそのブロックだけ）。§6.8 と `kit/e2/README.md` の Usage の保証の文を合わせる（「next block」の場合も・監査役 3-G）。`open_set.py` も同じ `align_plan` を使う。⚠️ 今の selftest に「左端の条件」を前提にした対照があれば、意味を確かめてから直す。
2. 〔コード〕`l2.py` の `per_trial` が、計画にある層で試行の無いものを null と理由で出す（§6.11）。§6.7 に「汚染の無い版では S6 が両セル・全速さで 0 試行、S13 は範囲に残らない。その場面は重み付けし直せず、この版は試行をまたぐ持ち越しの食い違いを含まない」。
3. §6.4 の読者向けの文: 「key 行は打ち切りの候補（どのセッション行も覆わない英字の連なり）を示すが、macOS では入力モードが残らないので確定できない」に。打ち切りが 4 つの量を動かす向き（平均の変換時間と時間の割合は下がる・件数と放棄の率はどちらにも動きうる）を 1 文ずつ。§7 の打ち切りの項にも参照（round 3 の入れ漏れ）。
4. §6.6 の「read from the numbers of rows per trial」を、コードが出す数（`pred_obs` の `over_limit` の層ごとの予測の行と観測の行の数）で読む形に（新しい統計は足さない）。
5. 〔コード〕`spec_predict.py --from-plan` の出力に層ごとの Σm²/Σm とブロック数（計画の層・主の範囲の層）を足し、§3.3 の値をそこから再現できるようにする。§3.3 の「usually near 1」を消す（か「near 1 when rho is small」）。最小の主の層（31）の半幅（約 0.35 × SD）を添える。主の範囲の層でも上限の内であること（メインの計算: 最大 ON 3.05〔S14 mid〕・OFF 3.22〔S15 mid〕）を書く。⚠️ 出力の形式 `spec_predict/2` を読む `match.parse_prediction` が未知のキーをどう扱うかを先に確かめる（形式を上げるなら match も）。
6. §3.4 に「預けない」と報告の場所（Z1 に含めた）。
7. 置き換わった打鍵は検出しない（Z1 に含めた）。
8. §3.1 の 2 つの約束の文: 1 つ目を「基準は凍結の前に `pilot-macos.md` に書く。それを満たす run の生ログを預ける」と 2 文に。`pilot-macos.md` の Raw logs の時点も「before the freeze」に揃える（文だけ・中身は Mac）。2 つ目に対象の run（`pilot2-on`・`pilot2-off`・`verify-off`）・`--markers-in-obs`・パイロットの 3 打鍵の印・使い道（診断。コードの欠陥が見つかれば凍結の前に直し、前後の割合を書く）。3 つ目の約束（参照のログに `delivery.py` を当て、かなキーと S14 のモードキーが残るか・区間ごとの説明されない数を書き、Z1 の上限を決める）を足す。

### nit（`verdict.md` §3）

§6.7「none of the four layers」→「the trials of the layer none (section 6.4)」（⚠️ round 4 の `context-A.md` の要約にも同じ誤り。round 5 の context-A で直す）／§6.2 の Not excluded の古い言い方／§1.2 の問 4 に §6.8 への参照／§3.1 の OFF の 186（185 が後の試行で終わる）／`data.md` の表に計画の SHA-256／§3.2 の検査の範囲／§6.8「Presses outside every block are counted」→ 採点したブロックが覆わない打鍵／（任意）§7 の「judges one phrase at a time」の項を §6.8 の参照に縮める。

### 確認（round 3 と同じ一式）

`kit/check.sh`（約 1.5 分）・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py`（repo 直下から相対パス `papers/ime-observation`）・`check_citations.py`・`--check-prereg` exit 3（未凍結）・§9 の SHA-256 の表の 5 ファイル・本文の「section N」の実在・変異（作業用エージェントの自己申告＋メインの抜き取り）。⚠️ `pipeline.py --selftest` 約 25 秒・`closed_set.py --selftest` 約 20 秒。

## §3 Mac の作業（判断 113 の Y4 ＋ 判断 117 の Z3・凍結の前・測定機）

1. `pilot-macos.md` の Raw logs に、預ける基準と「封印したセッション行は預けるときだけ開け、解析しない」。時点は「凍結の前」。観測の余分な行の扱いは本計測と揃える（判断 112: 観測器の結果で、中止・保留の理由にしない。根拠: 観測の key 行は区分と時刻だけで key code を持たない／人の打鍵は参照が受けて Z1 の規則で捕まる。⚠️ 区分と時刻からの復元は問 4 の問いそのものなので、この根拠の書き方は慎重に・必要なら研究者に問う〔監査役 3-E〕）。
2. `pilot2-on`・`pilot2-off`・`verify-off` の観測の key 行に `align_plan` だけを `--markers-in-obs` とパイロットの 3 打鍵の印で流す（攻撃はしない・セッション行に触れない・`marker_categories` は計画の印から作る）。採点されたブロックの割合を診断として §3.1 に。最初のパイロット（F13・F14 の印）は観測に行が無いので対象外。
3. 同じ run の参照のログに `delivery.py`（§3.4 と同じ引数）を当て、かなキー（104）と S14 のモードキー（102・104）が参照の `key_down` に残るか・区間ごとの「説明されない数」を §3.1 に書き、Z1 のかなキーの数を決める（パイロットの印は 3 打鍵）。⚠️ 参照のログは key code を持つ。値（key code）を表示・転記しない。数と有無だけを書く。
- ⚠️ パイロットの観測のセッション行は封印のまま（判断 11）。正解と ImeShadow を突き合わせない。予測器と配送の報告は観測のセッション行を読まない。

## §4 attack-me round 5（G-GEAR・判断 117）

- 同じ立場・同じ接地（原本 8 本の SHA-256 を `round-1/panel.md` と照合）。対象は round 4 の直しと Mac の作業で変わった箇所: §3.4・§3.1・§3.2・§6.3・§6.4・§6.6・§6.7・§6.8・§7・`data.md`・`pilot-macos.md`・`kit/e2/README.md`・`delivery.py`・`pipeline.py`（中止の規則）・`closed_set.py`（錨）・`l2.py`（`per_trial`）・`spec_predict.py`（Σm²/Σm）。`git diff 40ad7801..<head> -- papers/` から測り直す。
- round 4 の資料（`round-4/context-A.md` ほか）を写して「変わった箇所」を差し替える。役ごとの `carryover-*.md` は round 4 の新しい指摘・判定の部分的に解消／未解消・裏取り（`verdict.md` §2）・採否（判断 116・117）・対応。⚠️ 他の役の指摘は渡さない・他の役を名指ししない。採らなかったもの（k の階級ごとの報告・主を k ≥ m に限る・runner を変える・題の nit・設計効果の式の出典）を正直に書く。
- 応答の保存は round 4 と同じ（報告の本文をメインが Write で `round-5/tmp/<名>.raw.md` に書き写し、`scripts/secrets-filter.sh` と `round-4/tmp/check_resp.py` を `RD` を `round-5` にして写したもので検査）。⚠️ 親ディレクトリだけの行は偽陽性の型（round 2・round 4）。⚠️ 査読者が一覧の外のファイルを Read で開いたと申告したら、写さずに研究者に問う（round 4 の R3・判断 117 は「写す」）。依頼文の「読んでよいファイル」に、Grep の対象を一覧のファイルに限る（ディレクトリ全体を Grep しない）と足すと、この逸脱が減る。
- 接地の引用の照合は `round-4/tmp/quote_check.py`（PDF の柱・頁番号・行末のハイフン・合字「ﬁ」・表の 2 列の交互の抜き出しで外れる。外れたら断片で `tr '\n' ' ' | grep -o` して確かめる）。
- 裏取りで計画と予測を使うときは §2.4 のコマンドで scratchpad に作る（SHA-256 は ON `c7a5469d…`・OFF `3759ebf7…`）。予測は `spec_predict.py --from-plan --plan <plan> --out <file>`。⚠️ Windows の Python に `/c/...` のパスを渡すと開けない（`C:\...` で渡す・スクリプトは Write で scratchpad に置く）。
- 起動の前に研究者へ知らせる（G-GEAR に Zenodo のトークンがある・`sealed/` と生ログは無い）。

## §5 その後と気をつけること

- 完了時レビュー: code-reviewer ∥ security-checker ∥ Codex（`scripts/run-codex-review.sh <base>..<head> -- papers/ime-observation docs/references.md`・出力は scratchpad・2 巡）。範囲は `git merge-base origin/main HEAD`..HEAD のコミット済みだけ。Codex の台帳は回す前に origin/main の当日分も見る（memory: Codex ledger split by branch）。⚠️ レビューの作業用エージェントに `kit/check.sh` を回させない。
- origin/main を取り込み → push → PR → CI 緑なら merge → main の CI（git-workflow ルール 6）。⚠️ 凍結は研究者の別の段（OSF の登録は研究者）。`gt_rules.json` を変えたら凍結のハッシュは凍結の段で取り直す。
- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印は開けない。人の打鍵データを使わない。
- ⚠️ 名前（round 3 で変えたもの）: L2 の `conversions_per_trial`（試行ごとの `per_trial` の `n_conversions` は変えていない）・配送の `reference_focus_loss`（`trials_with_focus_loss`）。`mixture_bias.by_stratum` は区間を持たない。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。main は別の worktree が checkout している（`C:\GSE-prototype` で `git switch main` はできない）。
- ⚠️ git-bash で `git show origin/main:<path>` は MSYS がパスを書き換える → `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない（Windows のパスを含む文書は Write / Edit で書く）。
- ⚠️ round 1〜4 の `tmp/` は attack-me を閉じるまで消さない（`round-4/tmp/` に R1〜R3・監査役の生の応答・検査と照合のスクリプト・規程の原本）。
