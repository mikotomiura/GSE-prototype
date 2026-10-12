# 引き継ぎ: EH3 の招待の契機の値（試作の段）を決める

作成 2026-10-12（Windows・Surface）。PR #356（`513affb4`）を main に merge した後のセッションで書いた。
返答・記録は日本語で書く。絵文字や記号（★・⚠️）を多用しない（研究者の指摘）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-eh3-trigger-values.md を読んで、EH3 の招待の契機の値（試作の段）を決めるタスクを始めて。
```

## 1. なぜやるか

- EH3 の招待は `p_stuck ≥ 0.60` が 30 秒続いたときに出る（`src-tauri/src/analysis/invitation.rs:43` の `TRIGGER_P_STUCK`、`:45` の `TRIGGER_HOLD_MS`）。値は稿 `experiments/20261011-portrait-eh3/preregistration-draft.md:216-217`（F-2）にあり、研究者が `.steering/20261011-portrait-eh3-after-impl/decisions.md` の判断 1 #3 で認めた。
- 同じ decisions.md の判断 3（Windows の実機・2026-10-12）では、この契機を意図した打ち方で作れなかった。`p_stuck ≥ 0.6` が続いたのは最長 16 秒だった。手を止めると 0.54 で頭打ちになり、速く打ち直し続けると 0.01 まで下がった。実際の使い方でも招待がほとんど出ない恐れがあり、そうなると PC-12・M-2〜M-4 が測れない。
- 判断 4（研究者の逐語は decisions.md にある）で、試作と利用者の検証の段では招待を出やすい側に調整し、記録を見て詰める方向だけが決まった。具体の値と、段の値をどこで切り替えるかは決まっていない。

## 2. このタスクのゴール

1. 試作の段の契機の値の案を、根拠の数字とともに研究者に示し、研究者に決めてもらう（AskUserQuestion。推奨と理由を添える）。
2. 段の値を切り替える方法を決めて実装する。候補は次の 2 つ。
   - 定数を書き換える: 単純だが、本番の値に戻すのを忘れる恐れがある。
   - `eh3.mode` に目印を足す（例: `trigger=proto`）: `src-tauri/src/eh3.rs:183` の `parse_assignment` に足す。記録の `eh3_day` に値が残るので、解析で段を区別できる。
   - Claude の見立てでは後者がよい。ただし決めるのは研究者。
3. 稿 F-2 に「試作の段の値」と「本番の値（凍結の前に決める）」を分けて書く。本番の値は試作の記録を根拠にする（判断 4 の Claude の見立て）。

範囲外: 本番の値の凍結、ADR-035 の Accepted、F-1・F-3・F-6、Windows の実機の残り（招待の図像・失効・スリープ・再起動・複数モニタ）。これらは `.steering/20261011-portrait-eh3-after-impl/tasklist.md` に残っている。

## 3. 始める前に確かめること

1. `git fetch` して、PR #356 が main に入っていること（`513affb4` 以降）を確かめる。作業は新しいブランチを main から worktree で切って行う（作業ツリーには常に別ブランチの未コミット作業がある。`git add -A` は使わない）。
2. `/start-task` で `.steering/20261012-eh3-trigger-values/` を作る（日付は実施日に合わせる）。
3. 先に読むもの:
   - `.steering/20261011-portrait-eh3-after-impl/decisions.md` の判断 1・3・4（全文）
   - `src-tauri/src/analysis/invitation.rs` の冒頭の doc（契機・1 区間 1 回・離席候補の扱い）と `:256`・`:697` の判定
   - 稿 §10.1 の表（`preregistration-draft.md:210-240` あたり・F-2 は 216 行から）
   - `docs/adr/ADR-035-invitation-choice-principles.md`（招待の制約）
4. 0.60 は招待だけの値ではない。`src-tauri/src/analysis/metrics.rs:166` の `p_stuck_trigger: 0.60` は Stuck エピソードの定義（ADR-024 など）でも使われている。招待の契機だけを変えるなら、この 2 つが別の値になることを稿と decisions.md に明記する。metrics 側は変えない（変えると事前登録済みの指標の定義が動く）。

## 4. 値の案の作り方（推奨）

勘で決めず、記録から「その値だと 1 日に何回くらい契機に届くか」を数えてから示す。

- 材料は手元の記録だけを使う（研究者の自分の O1 の記録や、判断 3 の実機の記録が残っていればそれ）。どれを使うかは研究者に聞く。NDJSON の生ログやキーストロークの内容は外部 LLM（Codex を含む）に送らない（`data-privacy` Skill）。
- `gse-replay` で `feat` 行の `p_stuck` の列を出し、閾値 {0.50, 0.55, 0.60} と継続 {10, 15, 20, 30 秒} の格子で、契機に届く回数を作業時間 1 時間あたりで数える。1 区間 1 回・60 秒で区間を閉じる・離席候補 180 秒の除外は `invitation.rs` と同じ規則で数える。できれば `invitation.rs` の判定関数をそのまま呼ぶ小さなテストかバイナリで数える（規則を書き直すと食い違う）。
- 判断 3 の観察から、0.54 の頭打ちを越えない値（0.55 以下）にしないと、手を止めた停滞では届かない見込み。ただし、停滞でない時点で出ると M-4 の読みが濁る（判断 4 の Claude の見立て）。示すときは、回数と一緒にこの代償も書く。
- 量は 1 日の上限（既定 2）と 30 分の間隔が抑える。契機を緩めて主に変わるのは「どの時点で出るか」。

## 5. 守ること（CLAUDE.md・Skill から）

- 実装の前に `/start-task`。Rust を書く前に `rust-standards`・`architecture-rules`、介入の判定を触るので `intervention-design`、記録の材料を使うので `data-privacy`、事実を断定する前に `verify-before-claiming` を読む。
- `analysis/` に OS API を入れない。`println!` / `eprintln!` を使わない（`tracing`）。
- テストは `cd src-tauri` してから（repo 直下に `Cargo.toml` は無い）。値を変えたら、境界（閾値ちょうど・継続ちょうど）のテストを足し、変異を入れて落ちることを確かめる。
- `eh3.mode` に目印を足すなら、未知の値・重複の扱いを既存のキーと揃え、記録の `eh3_day` に残ることをテストで確かめる。
- 完了時は code-reviewer と security-checker を並列で、/cross-review（Codex）を 2 巡（パスを限定）。`.codex/budget.json` は `git checkout --` で戻さない。
- 出荷: commit → push → PR → CI 緑なら merge → main の CI の確認（`git-workflow` ルール 6）。計測の run が走っている証拠があるときだけ PR を控える。
- 研究者への質問は AskUserQuestion で、推奨と理由を添え、日本語で。

## 6. 終わったら

- `.steering/20261011-portrait-eh3-after-impl/tasklist.md` の「招待の契機の値」の行に、新しいタスクのディレクトリを書き添える（チェックは本番の値が決まるまで付けない）。
- 次は Windows の実機の残り（日中の自然な作業で招待の図像・失効・押して窓が開く）。試作の値で招待が出るようになってから行うと、判断 3 #8 で確かめられなかった項目を確かめられる。
