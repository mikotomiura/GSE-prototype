# タスクリスト

⚠️★★★ **`_survey-*.md` は索引であって原本の代替ではない。**
2026-09-11 の調査で、`20260908`（48KB・40 見出し）を 250 行に要約したら
**§5 / §6 / §9 が丸ごと落ちた**。掘り直して初めて出てきた。**同じことがこのタスクでも起きる。**

## §0 準備 — ★ `.idea` 原本の熟読（**省略しない**）

`.steering/_handoff/idea-coverage-20260911.md` を開き、本タスク担当分（T4）の状態を確認する。

- [ ] **`20260908`**（48KB）— ✅ 深掘り済み。★ 着手時に `grep -n "^#\{1,3\} " .idea/20260908-*.md` で
      見出し一覧を出し、`_survey` 2 本が拾った節と**突き合わせる**（落ちが無いか）
- [ ] **`20260909-content-evanescent`**（63KB）— ✅ 深掘り済み。同上の突き合わせ
- [ ] **`20260909-pigment`**（14KB）— ✅ 深掘り済み。同上
- [ ] **`20260806`**（45KB）— 🔄 2026-09-11 に深掘り実施。★ **結果ファイルの有無を確認**し、
      無ければ節を指定して survey subagent を投げ直す
- [ ] **`20260810`**（55KB）— 同上
- [ ] **`20260901`**（54KB）— 同上（★ T3 と共有。**層・段の呼称は却下済みだが中身は生きている可能性**）
- [ ] ⚠️ **`20260907`**（9.8KB）— 🔶 **要約のみ。小さいので原本を直接読む。**
      用語改訂提案（`physical return` → `self-chosen pause and resumption opportunity` 等）が残っている
- [ ] ⚠️ **`20260819-smartphone`**（29KB）— 🔶 本文が「SSOT へ昇格した」と明記。
      ★ **無効化対照表だけ**を読んで、昇格漏れが無いか確認する（全文は不要）
- [ ] **`20260909-physical-foreground`**（14KB）— 🔶 D 区分（ハードウェア試作）。★ 読むが issue にはしない
- [ ] 読んだ結果で `idea-coverage-20260911.md` を更新する

## §1 T1 の完了を確認

- [ ] ⚠️★★★ **T1（`20260911-intake-arbitration-branch`）が完了している**こと
- [ ] 取り込み後の `docs/architecture/expression-channel.md`（+337 行）の**見出し構成を出す**
- [ ] ADR-025 / 026 / 027 / 028 を読み、**既に閉じた論点の一覧**を作る
- [ ] 取り込み後の `docs/glossary.md`（+27 行）で**新たに追加された禁止用語**を確認する
- [ ] ⚠️ **上記 3 つと `_survey-*.md` の A 区分を突き合わせ、重複を除く**
      （★ これをやらないと既に書かれている内容に重複 ADR を書く）

## §2 issue 分解

- [ ] `issue-slicing` skill を読む（**Opus** で実行）
- [ ] `_survey-*.md` 3 本の A 区分 / B 区分から縦切り issue を作る
- [ ] `issues/00X.md` ＋ `_issue-plan.md`（DAG・Allowed Files 交差表）を出力
- [ ] ⚠️ **`acceptance.sh` を書く**（`check_doc_lexicon.py` は何も書かなくても緑になる）
- [ ] `/clear` して新セッションで実行する

## §3 実行

- [ ] A 区分（規約・境界・禁止事項・主張範囲）を docs / ADR へ反映
- [ ] ⚠️ **B 区分の `Temporal Primitive` の定義を一本化**（§3.4 の 7 項目 vs §4.8 の 6 項目）
- [ ] ⚠️ **§4.8–4.10 に層ラベル（層 A / 層 B / 将来拡張）を付け直す**
- [ ] `data-privacy` Skill に `embedding inversion`（`[P1]`）を追記
- [ ] ⚠️ **A 判定の項目を既存の一次資料と突合してから転記**（`.idea` の記述を無条件に正としない）

## §4 検証

- [ ] `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` が exit 0
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が exit 0（★ **緑になるまで是正 → 再実行を繰り返す**）
- [ ] `code-reviewer` + `security-checker` を**並列**起動
- [ ] ⚠️ **`/cross-review`**（skip した場合は理由を完了報告に明記）

## §5 完了処理

- [ ] `idea-coverage-20260911.md` を最終更新（✅ に変えた節を記録）
- [ ] `design.md` / `decisions.md` の最終化
- [ ] `/finish-task`
- [ ] git commit（⚠️ `git add -A` 禁止。パス明示）
