# 次セッション — AI 疲労 文献 DB: N-05 プロトコルの研究者の答えの反映 → プレ査読 → 英語の登録版

> 更新: 2026-10-01 10:30（`.steering/20261001-ai-fatigue-protocol-cont/` は完了。PR で main に入れる）。⚠️ **このメモを一次資料にしない。** 決定は `.steering/20261001-ai-fatigue-protocol-cont/decisions.md` 判断 1〜7、プロトコルは `.steering/20260930-ai-fatigue-protocol/protocol-ja.md`（草稿 v0.2・登録していない）、研究者に聞くことは `.steering/20261001-ai-fatigue-protocol-cont/researcher-check.md`（確認票）。
> ★ ユーザーは **判定者 1 の立場**。確認票の項目（判定者 2 の人選・盲検の条件・資金・利益相反ほか）は研究者が決める。ユーザーに聞かない（「研究者の決定待ち」と書く・記憶 `project_ai_fatigue_judge1_saw_appraisal`）。
> ★ 判定者用ファイル（判定者 1）は `10107fcf…`（2026-10-01 10:21・archive と Downloads で同じ・未記入）。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-researcher-answers.md を読んで、AI 疲労 文献 DB の N-05 プロトコルの次の段を進めてください。まず §1 の 1（研究者の確認票が返ってきているか）から。

⚠️ この引き継ぎは origin/main にある。C:\GSE-prototype のチェックアウトは別の枝のことがあるので、worktree C:\wt\ai-fatigue-judge-file で origin/main から新しいブランチを切って読む（docs/ai-fatigue-protocol-cont は PR で merge 済みのはず。gh pr list --head docs/ai-fatigue-protocol-cont --state all で MERGED を確かめる）。git add -A / git add <dir> は使わない。
⚠️ Downloads の AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx は、作り直す直前の SHA-256 の確認（10107fcf… のままか）と judge_xlsx.py の --copy-to 以外で触らない。記入が始まっていれば止まって聞く（記入のあるファイルは道具が上書きしない）。
⚠️ 外部に出る操作（著者への照会・フォーム・OSF への登録）はしない。学術 API に研究者のメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない。有料のデータベース・有料の本文は使わない。候補を AI の見立て（E1〜E3）で絞らない。
⚠️ Codex を回す前に当日の実消費を確かめる（台帳はブランチごと・合算で上限 300,000・予算ガードの hook は C:\GSE-prototype の台帳を読む）。
★ 完了時は code-reviewer ＋ security-checker（並列）・/cross-review 2 巡・git-workflow ルール 6。応答は日本語。
```

## §1 残っていること（順に）

1. **研究者の答えを待つ**（確認票 `researcher-check.md`・期限の早い順に §1〜§4・【案】の一覧は §6）。
   - 返ってきていなければ、このトラックは止まる（研究者の決定待ち）。ユーザー（判定者 1）に代わりに答えさせない。
   - ★ **期限が最も早いもの**: §1 の 2 点（F19・F10）と §6 の [GSRR-35] の E7 の当て方。判定者 1 の記入が始まる前でないと判定者用ファイルを作り直せない。答えが無い間は、判定者用ファイルの文のとおり暫定で当てる（確認票 §5）。研究者が覆す・変える場合は、Downloads の写しの SHA-256 を確かめてから `judge_xlsx.py --judge 1 --out ../archive/judge/… --copy-to <Downloads> --force` で作り直す。記入の後なら、確認票 §1 の F10・F19 の行の手順（基準の版を上げて読み直す）。
2. **答えを草稿に書き込む**: 答えを【決定】として `protocol-ja.md` に書き、付録 F の行を「決定」にし、確認票の回答の欄と突き合わせる。`check_here.py`（確認票の F の番号の節と【案】の数を草稿と突き合わせる）と `check_protocol_here.py` を回す。★ 決定にした F の番号は確認票の §1 に移す規則（`check_here.py` の検査 4）なので、答えの反映の形に合わせて検査を直すかを先に決める。
3. **プレ査読**（`attack-me` Skill・日本語の草稿の外枠が固まった後・事前登録を凍結する前）。
4. **英語の登録版**（GSRR の 65 項目・付録 E の対応表で 1 対 1 に写す。付録 A の出どころは作業記録のパスなので、登録版では書き方を決める）。
5. 登録（研究者が OSF で行う）。

## §2 いまの数（2026-10-01）

| 何 | 値 | 出どころ |
|---|---|---|
| プロトコル | 草稿 v0.2・GSRR 65 項目・付録 A〜G・確認待ち 18 項目（20 項目のうち F10・F19 は判定者 1 が決めた）・【案】31 項目（26 の節） | `protocol-ja.md`・`researcher-check.md` |
| 判定の対象（登録前の段） | 254 件（259 件から版違い 5 件を寄せた） | `.steering/20260930-ai-fatigue-protocol/dedup-259.md` §2 |
| 判定者用ファイル（判定者 1） | `10107fcf…`（10:21・未記入）。除外理由は E1〜E7、『判定基準』に E4 の尺度の原著の読み方と E7 の当て方（E7 は E6 より先・対象外の言語で英日の版も無いとき） | `decisions.md` 判断 2・5・6・7 |
| 検査 | `check_here.py` 違反 0・selftest（変異 33）PASS／`check_protocol_here.py` 違反 0・PASS／`check_judge_xlsx.py` 違反 0・selftest 76 PASS／`check_appraisal_xlsx.py` 違反 0・PASS | `decisions.md` 判断 7 |
| Codex | 2026-10-01 の実消費 291,174 / 300,000（7 回・本タスク 2 回・91,770）。上限は引き上げていない | `.codex/budget.json` |

## §3 落とし穴（本セッションで起きたこと）

- **引き継ぎが `C:\GSE-prototype` に無かった**: 現行の引き継ぎは origin/main と worktree にあり、`C:\GSE-prototype` のチェックアウトは別の枝（attack-me）だった。→ `git worktree list` と `git log --all -- <引き継ぎのパス>` で探す。
- **前のセッションが同じタスクを途中まで進めていた**（worktree に未 push のコミット 3 つ）。→ worktree の `git status`・`git log origin/main..HEAD`・`tasklist.md` を先に見て、続きから始める。
- **openpyxl はシステムの Python に無い**: 判定者用ファイル・評価版の道具と検査は `uv run --with openpyxl python …` で回す。`check_judge_xlsx.py` は xlsx のパスが要る（引数なしだと何も出さずに終わる）。
- **注の文に「【案】」と書くと【案】の数に入る**（`check_here.py` が草稿の 3・票の 2 で赤にした）。【案】を指すときは「§6 の項目」などと書く。
- **2 巡目の直しは Codex に回せなかった**（2 巡で当日 291,174）。2 巡目が 30,000 を超えうるので、1 巡目の前に当日の残りが約 100,000 あるかを見る。
- Codex の 2 巡とも、道具と草稿の「文の一致」だけの検査の穴を突いた（1 巡目: E7 の当て方の文を見ない、2 巡目: 両方から消えると通る）。→ 一致の検査には、固定の期待（`E7_RULES`）を道具と草稿のそれぞれに独立に当てる形を最初から入れる。
