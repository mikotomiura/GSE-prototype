# 次セッション — AI 疲労 文献 DB: /cross-review 2 巡（Codex）→ 出荷、無料の本文 4 件

> 作成: 2026-09-30（`.steering/20260930-ai-fatigue-judge-file/` の完了処理の途中）。⚠️ **このメモを一次資料にしない。** 数字は 2026-09-30 の値で、出どころを書いた。
> ★ 研究者の決定（2026-09-30）: Codex の `/cross-review` は**日付が変わってから新しいセッションで 2 巡**（当日の実消費が台帳の合算で約 304,946 / 上限 300,000 だったため）。無料の本文 4 件も次のセッションに繰り越し。

## ★ 完了（2026-09-30 の同日の次のセッション）—— 以下の §0〜§2 は済んだ

- 研究者の決定で、日付を待たずに Codex の上限を一時的に引き上げて /cross-review 2 巡を回した（判断 14・16・19。Codex 計 3 回・241,255。上限は 300,000 に戻した。同日の合算は feature/ime-eval-kit の 74,317 を足して 546,201 / 9 回）。
- 無料の本文 4 件（B5・B9・B10・B12）を読んだ（判断 15）。B9 の採択 32 件の突き合わせから候補 2 件（S-02 §7）。
- 研究者の決定（判断 17）で、S-04 の「作業負荷・時間だけを測った比較研究」を候補にした。抽出の表のラベルの取りこぼしも抄録で確かめて足した（判断 20）→ **追加候補 206 件**（S-04 §3.1 34 件・§3.2 13 件）。
- 判定者 1 用のファイルを作り直した（毎回、Downloads の写しが未記入であることを SHA-256 で確かめてから）。`check_judge_xlsx.py` の golden を、語も塗りも使わずに候補を隠す手段（文字色・tint・字体・罫線・配置・行や列の非表示・リッチテキスト・コメント）まで広げた（selftest 57 項目）。
- 完了時のレビュー: code-reviewer 2 回・security-checker 1 回（判断 18・20）。
- ★ 次は §3（判定者 1・2 の判定 → 不一致の調整 → 送付用・N-05 への論点・B 群のサーヴェイ）。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-crossreview.md を読んで、AI 疲労 文献 DB のタスク（.steering/20260930-ai-fatigue-judge-file/）の完了処理の続き（/cross-review 2 巡 → 指摘の対応 → 出荷）と、無料の本文 4 件を進めてください。

⚠️ 作業は worktree C:\wt\ai-fatigue-judge-file（ブランチ docs/ai-fatigue-judge-file）で。main の作業ツリーには別トラックの未コミット作業がある。git add -A / git add <dir> は使わない。.steering/20260921-media-expression-theory-audit/ は触らない。
⚠️ 先に git fetch → origin/main との差を確かめ、必要なら origin/main を merge（.codex/budget.json が衝突したら和を採る・二重に数えない）。
⚠️ Codex を回す前に当日の実消費を確かめる（実消費 = 共通祖先の当日分 ＋ Σ（各ブランチの当日分 − 共通祖先の当日分）。ほかのセッションの worktree の台帳〈例: C:/GSE-prototype の feature/ime-eval-kit〉も見る。上限 300,000）。.codex/budget.json は台帳（git checkout -- で戻さない）。
★ 研究者は判定者 1。完了報告・チャットに 1 件ごとの判定案・評価を書かない（件数だけ）。サーヴェイの新しい候補の判定案（survey-S-1x-ai-judgments.md・db-proposals.md）を研究者に見せない。
⚠️ 外部に出る操作（著者への照会・フォーム）はしない。学術 API に研究者のメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない。有料のデータベース・有料の本文は使わない。
★ 完了時は git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI 発火確認）。応答は日本語。
```

## §1 現在の状態（2026-09-30 07:50）

| 何 | 値 | 出どころ |
|---|---|---|
| ブランチ | `docs/ai-fatigue-judge-file`（origin/main `15c2af2b` から）。コミット 4 本（3ea10d34・25e6aaf4・44acd04f・40a76db5）＋ 引き継ぎのコミット。**push 済み・PR は未作成** | `git log` |
| 研究者のメモの issue | 7 件（S-13〜S-15・N-11〜N-14）。N-12 と S-13〜S-15 は済み | `memo-issues.md` の「状態」 |
| 判定の範囲の決定 | (a) S-04 の比較研究 34 件すべて・(b) AI の監督だけ・(c) 別シートで判定・判定者 2 は未定・有料は使わない | `decisions.md` 判断 2・3 |
| サーヴェイ | S-15（過信と疲労）・S-14（燃え尽き）・S-13（組織の水準）を 1 ラウンドずつ。事実・AI の判定案・GSE の含意の 3 ファイル | `survey-S-1x*.md` |
| 判定者用ファイル | DB 34 件 ＋ 追加候補 157 件（別シート）。`archive/judge/AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx` と Downloads の写し（同一・違反 0） | `decisions.md` 判断 11・13 |
| レビュー | code-reviewer（HIGH 1・MEDIUM 11・LOW 7）・security-checker（LOW 4）→ すべて対応または記録 | `decisions.md` 判断 13 |
| 検査 | `scripts/check_judge_xlsx.py --selftest` 43 項目 PASS（約 3 分）・`scripts/check_surveys_here.py` 違反 0・前タスクの `check_survey_files.py` 違反 0 | `tasklist.md` |
| 未了 | ① `/cross-review` 2 巡 ② 無料の本文 4 件 ③ 出荷 | `tasklist.md` |

## §2 やること

1. **`/cross-review` 1 巡目**: `scripts/run-codex-review.sh 15c2af2b..HEAD -- <パス>` で**パスを限る**（2,000 行を超えると確認が要る・前タスクの判断 16）。
   - 対象: `scripts/*.py`・`evidence/search_round.py`・事実のファイル 3 本・判定案のファイル 3 本・`memo-issues.md`・`decisions.md`・`design.md`・`researcher-requests.md`・`survey-S-08.md`。
   - ⚠️ `evidence/**/*.json`・`*.tsv`・`archive/**/*.xlsx` は対象にしない（大きな生成物）。
   - 文書と Python を 2 回に分けると 1 回が小さくなる（前タスクで 1 回 20k〜45k）。
2. **2 巡目**: 1 巡目の直しの境界条件だけ（記憶 `project_cross_review_two_rounds`）。今回なら `check_judge_xlsx.py` の golden と許す列（書誌の列の評価の語）・`judge_xlsx.place()`・候補の選び方の規則（判断 13）。
3. ⚠️ **判定者用ファイルを作り直すとき**: 研究者が Downloads の写しに記入を始めている可能性がある。`judge_xlsx.py --force` は記入のあるファイルを上書きしない（止まる）。★ 記入を引き継いで作り直す仕組みは**まだ無い**。直しが要るときは、先に研究者に確かめる（記入の引き継ぎを実装するか、差分だけを伝えるか）。
4. **無料の本文 4 件**（`researcher-requests.md` の B5・B9・B10・B12）:
   - B5 は CC BY。ScienceDirect はスクリプトでは届かないので、ブラウザで読む（研究者の許可あり・読むだけ）。
   - B9 は Zenodo。
   - B10・B12 は PubMed Central に投稿版がある。
   - 読んだら、S-02・S-04 の事実のファイルに要点を足す（判定の語・評価の語を使わない・`check_survey_files.py` を当てる）。
   - ⚠️ 事実のファイルを変えると、追加候補の要点（S-02 #3・#8 など）が変わる。判定者用ファイルとの一致の検査（golden・structure）が赤になるので、作り直しが要る → 上の 3 と同じ注意。
5. **出荷**: push → PR → CI 緑なら merge → main の CI 発火確認（git-workflow ルール 6）。CI の Windows は 18 分ほどかかる。

## §3 その後の段（このセッションではやらない）

- 判定（判定者 1・2）→ 不一致の調整 → 相手先に送る判定後のスプレッドシート。
- 判定者 2 が決まったら `judge_xlsx.py --judge 2 --out …` で判定者 2 用のファイルを作る（『はじめに』に開かないものの指示が入る）。
- N-05 に「組織の水準の疲れ（変化の疲れ・制度の消耗）を範囲に入れるか」を足す（`survey-S-13-ai-judgments.md` §4 の材料・研究者の判断）。
- B 群のサーヴェイ（S-01 本検索・S-06・S-09・S-11）。S-01 には「AI awareness」「AI anxiety」「STARA」と燃え尽きの組の検索ブロックを置く（S-14 の判定案 §4）。
- 新しい issue の `issues_data.py` への反映（評価版の xlsx を作り直すとき・`memo-issues.md` §3 の直しの候補も）。

## §4 落とし穴（★ 2026-09-30 に実際に起きたこと）

- **検索式の漏れは種文献で見つかる**: S-14 は種文献 3 件がどれも当たらず、単独の `AI` と `job stress` の語が無かった（判断 8）。種文献の選び方も確かめる（S-13 の Jeong ほか 2024 は疲労を測っていなかった・判断 9）。
- **AI の見立てで候補を絞らない**: 「表に載せなかった」行を判定者用ファイルから落としていた（code-reviewer HIGH・判断 13）。
- **変異試験の空振り**: zip のパーツが無いと変異が作られずに緑になった（共有文字列のパーツが無い版の openpyxl）。検査を分け、単独の検査で赤になることを確かめる。
- **題名の著者の語が評価の語に当たる**（「…No Longer Sufficient」）。書誌の列では評価の語を許し、書き換えは golden で捕まえる。
- **掲載誌の名前を DOI から推して書かない**（一次で確かめていない略称を事実のファイルに書いた → 消した）。
- **heredoc**: `python - <<'EOF'` は通るが、`cat >> … <<'EOF'` で長い文を足すのは失敗した。長い文は Write/Edit で書く。
- **openpyxl は `uv run --no-project --with openpyxl python …`** で動かす（素の python には無い）。LibreOffice は `C:/Program Files/LibreOffice/program/soffice.exe`（数式の再計算の確認に使える）。
