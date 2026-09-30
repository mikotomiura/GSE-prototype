# 次セッション — AI 疲労 文献 DB: 追加候補 206 件の AI 評価版（判定者 1 の判断材料）

> 作成: 2026-09-30（PR #271 のマージの後）。⚠️ **このメモを一次資料にしない。** 数字は 2026-09-30 の値で、出どころを書いた。
> ★ 研究者の決定（2026-09-30・逐語「一応その信版のスプレッドシートを作成しましょう.私がジャッジする際の判断材料にします」）: 追加候補 206 件についても、元の DB 34 件の評価版（2026-09-29）と同じ形の **AI の評価版のスプレッドシート**を作る。**判定者 1 が判定の前に判断材料として読む。**
> ⚠️ これは `.steering/20260930-ai-fatigue-judge-file/decisions.md` 判断 1（新しい候補の判定案は判定の前に見せない）を変える決定である（判断 21 に記録）。DB 34 件と同じく、判定の記録に「判定の前に AI の評価を読んだ」と書く。判定者 1 を外す提案はしない。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-candidates-appraisal.md を読んで、AI 疲労 文献 DB の追加候補 206 件の AI 評価版のスプレッドシート（判定者 1 の判断材料）を作ってください。/start-task から始めます。

⚠️ 作業は worktree C:\wt\ai-fatigue-judge-file で、origin/main から新しいブランチを切って行う。main の作業ツリー（C:\GSE-prototype）には別トラックの未コミット作業がある。git add -A / git add <dir> は使わない。.steering/20260921-media-expression-theory-audit/ は触らない。
⚠️ 先に git fetch → origin/main を確かめる。Codex を回す前に当日の実消費を確かめる（台帳はブランチごと・合算で上限 300,000・.codex/budget.json は git checkout -- で戻さない）。
★ 研究者は判定者 1 で、今回は判定の前に AI の評価を読むと決めた（判断 21）。評価版は判定者用ファイルとは別のファイルにし、判定者用ファイルには AI の評価を載せない（check_judge_xlsx.py の words 検査を壊さない）。
⚠️ 判定者用ファイルを作り直すときは、先に Downloads の写しが未記入か SHA-256 で確かめる（記入があれば止まって研究者に聞く）。
⚠️ 外部に出る操作（著者への照会・フォーム）はしない。学術 API に研究者のメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない。有料のデータベース・有料の本文は使わない。
★ 完了時は code-reviewer ＋ security-checker（並列）・/cross-review 2 巡・git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI 発火確認）。応答は日本語。
```

## §1 現在の状態（2026-09-30 13:00 ごろ）

| 何 | 値 | 出どころ |
|---|---|---|
| 判定者 1 用のファイル | DB 34 件 ＋ 追加候補 **206 件**。AI の評価は載せていない | `.steering/20260930-ai-fatigue-judge-file/archive/judge/AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx`（Downloads の写しと同じ SHA-256 `4adc4dd9…72bb1`） |
| 元の DB 34 件の評価版 | Claude のシート 7 枚（Claude適格性評価・Claude方法論評価・Claude領域別評価・Claude照合事項・Claudeスクリーニング案・Claude×GPT比較・Claude評価基準）ほか | Downloads の `AI_fatigue_database_with_AI_appraisal_2026-09-29_claude.xlsx`・作り方は `.steering/20260929-ai-fatigue-db-readable-and-gaps/scripts/build_readable.py` |
| 追加候補の AI の判定案 | サーヴェイごとの Markdown。表の行数は S-02 19・S-04 7・S-05 5・S-08 16・S-12 27・S-13 16・S-14 10・S-15 19 と、`db-proposals.md`。⚠️ **1 件ずつそろっていない**（S-04 などは種類ごとのまとめの行がある） | `.steering/20260929-ai-fatigue-surveys/survey-S-*-ai-judgments.md`・`.steering/20260930-ai-fatigue-judge-file/survey-S-1*-ai-judgments.md` |
| 1 件ずつの案が確実に無いもの | S-04 §3.1 の 34 件・§3.2 の 13 件（2026-09-30 に足した・S04-41〜S04-87）と S-02 §7 の 2 件（S02-12・S02-13） | 判断 15・17・20 |
| 候補の一覧（SSOT） | `scripts/candidates.py`（206 件・cid の重複なし） | `.steering/20260930-ai-fatigue-judge-file/` |
| 判定者用ファイルの『はじめに』 | 判定者 1 の行は「元の DB 34 件の AI の評価を読んでいる」。★ 共通の行に「追加候補の AI の出力は、判定が終わるまで開かない」とある → 今回の決定と合わない | `scripts/judge_xlsx.py` の `intro_rows()` |

## §2 やること

1. **`/start-task`**（タスク名は研究者に聞く。案: `ai-fatigue-candidates-appraisal`）。requirement.md に研究者の決定（逐語）と判断 21 を書く。
2. **形を決める**（design.md に固定してから作る）: 9/29 の評価版の Claude のシートの列（`build_readable.py` と xlsx を先に読む）にそろえ、206 件用の別ファイルにする（例: `AI_fatigue_candidates_AI_appraisal_<日付>_claude.xlsx`）。最低限の列の候補: cid・出どころ・題名・DOI・AI の題名・抄録段の案（プロトコル v1.0 §3 の語）・理由（E コード）・全文段の案・中心の見立て（§2）・質の懸念（判定には使わない）・根拠のファイルと節。
3. **材料をそろえる**: 206 件を cid で、各 ai-judgments.md の行（1 件ずつの行・種類ごとの行）と突き合わせる。1 件ずつの案が無いものは、抄録で確かめて書く（抽出をサブエージェントに任せる場合は model を明示し、メインが抄録で検算する・Skill `subagent-delegation`）。種類ごとの案を 1 件ずつに写すだけにしない（評価は 1 件ずつ。候補そのものは AI の見立てで絞らない・判断 13）。
4. **判定者用ファイルの『はじめに』を直す**: 判定者 1 の行に「追加候補についても、判定の前に AI の評価版を読んだ（2026-09-30 に研究者が決めた）」を足し、共通の「開かない」の行を判定者 2 だけに移す。判定者 2 の「開かないもの」に新しい評価版の名前を足す。→ 作り直す（Downloads の写しが未記入かを先に確かめる）。
5. **検査**: 評価版の cid が `candidates.py` の 206 件と同じ順・同じ数、判定者用ファイルは `check_judge_xlsx.py` 違反 0・`--selftest` PASS。評価版そのものの検査（cid の一致・空の欄・根拠の節が事実のファイルにあるか）を足す。
6. **完了**: code-reviewer ＋ security-checker・/cross-review 2 巡・出荷。

## §3 研究者に確かめること（先に聞く）

- **S-04 の「作業負荷・時間だけの比較研究」の範囲**: 決定は「36 件すべて」だったが、Claude が「この種類をすべて」と解釈して 47 件（§3.1 34・§3.2 13）にした（判断 20）。36 件に絞るかどうか。
- **判定の順番**: B 群のサーヴェイ（S-01 本検索・S-06・S-09・S-11）を判定の前にするか。記入を引き継いで判定者用ファイルを作り直す仕組みはまだ無いので、判定を始めた後の新しい候補は別のファイルになる。

## §4 落とし穴（2026-09-30 に実際に起きたこと）

- 抽出の表のラベル（`fatigue_measure`・`load_measure`）だけで種類を分けると取りこぼす（21 件中 12 件）。境界の行は抄録で確かめる。
- 事実のファイルに判定の語・評価の語（誤り・十分・べき・保留・全文段・E6 など）を書くと `check_survey_files.py` が赤になる。評価版は事実のファイルではないが、判定者用ファイルに漏らさない。
- 抄録の取得で文が欠けることがある（「P」の後が切れる）。欠けた値は書かない。
- Codex の 1 回の実消費は、1,100〜1,700 行で 9 万〜10 万トークン、270 行で 5.5 万（2026-09-30）。予算の見積もりはこの実測で。
- heredoc の中のバックスラッシュは崩れる。長い文は Write/Edit で書き、Python で置換するときはバックスラッシュを文字コードで組み立てる。
