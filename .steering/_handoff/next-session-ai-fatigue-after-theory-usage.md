# 次セッション — AI 疲労 文献 DB: S-09・S-11 の後（研究者の決定待ちの論点と、残る B 群・判定者 2）

> 作成: 2026-09-30（`.steering/20260930-ai-fatigue-theory-and-usage/` の完了時）。⚠️ **このメモを一次資料にしない。** 数字は 2026-09-30 の値で、出どころを書いた。
> ★ いまも研究者（判定者 1）の判定の段。判定者 1 は判定の前に AI の評価版と見立てのファイルを読んでよい（`../20260930-ai-fatigue-judge-file/decisions.md` 判断 21）。判定者 2 は見立てのファイル（`survey-S-*-ai-judgments.md`）を開かない。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-after-theory-usage.md を読んで、AI 疲労 文献 DB の次の段（研究者に確かめてから）を進めてください。/start-task から始めます。

⚠️ 作業は worktree（C:\wt\ai-fatigue-judge-file など）で、origin/main から新しいブランチを切って行う。main の作業ツリー（C:\GSE-prototype）には別トラックの未コミット作業がある。git add -A / git add <dir> は使わない。
⚠️ 研究者が判定中のファイル（Downloads の AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx）には触らない。259 件の鍵・題名・DOI は repo の archive の写し（SHA-256 6984472e…）から読む。
⚠️ 先に git fetch → origin/main を確かめる。Codex を回す前に当日の実消費を確かめる（台帳はブランチごと・合算で上限 300,000・.codex/budget.json は git checkout -- で戻さない）。
⚠️ 外部に出る操作（著者への照会・フォーム）はしない。学術 API に研究者のメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない。有料のデータベース・有料の本文は使わない。候補を AI の見立て（E1〜E3）で絞らない。
★ 完了時は code-reviewer ＋ security-checker（並列）・/cross-review 2 巡・git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI 発火確認）。応答は日本語。
```

## §1 現在の状態（2026-09-30 夜）

| 何 | 値 | 出どころ |
|---|---|---|
| S-11 語の用法 | ✅ 259 件の抄録で、語（AI fatigue など）を使う記録 16 件＋目で見た補い 3 件。語を使わない 240 件のうち 212 件は一般の構成概念の語（燃え尽き 108・疲労 59・消耗 49 など）が出る。用法の区分（U1 利用の疲労 14・U2 3・U3 3・U4 1・区分できない 4）と定義文の案 A/B/C | `.steering/20260930-ai-fatigue-theory-and-usage/survey-S-11.md`・`survey-S-11-ai-judgments.md` |
| S-09 理論の節 | ✅ 原典 16 件と 5 件以上の枠組みの原著を抄録で読み、理論の節の草稿（約 1.5 頁）と DB の『尺度・理論』への追加の提案（15 行） | `survey-S-09.md`・`survey-S-09-ai-judgments.md` |
| issue の記述で確かめられなかったこと | 「AF004 は自我消耗理論に依拠」（抄録に語なし・本文は 403） | `issue-status.md` §2 |
| [研究者] への依頼 | AF004・S14-25 の本文（どちらも無料だが出版社のサイトがスクリプトに 403）・プロンプト疲れの概念分析の本体の書誌 | `issue-status.md` §3 |
| 残る B 群 | S-06 警報疲れ・S-01 本検索（どちらも N-05 に依存） | `../20260929-ai-fatigue-db-readable-and-gaps/scripts/issues_data.py` |
| 判定者 2 | 未定（前のタスクの時点） | `../20260930-ai-fatigue-judge-file/decisions.md` 判断 2 |

## §2 研究者に先に聞くこと（研究者が決める論点）

1. **サーベイの定義文**（S-11）: 案 A（利用の疲労・狭い）／B（利用と導入の要求）／C（傘の語）。AI の見立ては「A を定義文に、C を DB の範囲の語に分けて使う」（`survey-S-11-ai-judgments.md` §2）。
2. **DB の『尺度・理論』に理論の文献を足すか**（S-09）と、足すなら形（「理論」の区分を足す案）。
3. **次に何を進めるか**: (a) N-05（プロトコル・範囲の論点）→ S-01／S-06、(b) 判定者 2 が決まっていれば判定者 2 のファイル、(c) 判定が終わっていれば判定者 1 と 2 の突き合わせ、(d) 研究者が本文を置いてくれたら AF004・S14-25 を読んで事実のファイルを足す。

## §3 落とし穴（2026-09-30 に実際に起きたこと）

- git-bash では `git show origin/main:<path>` のパスが書き換わる（`MSYS_NO_PATHCONV=1` を付ける）。
- Semantic Scholar の匿名の API は、同時に別の取得が走っていると 429 を返す（2 回とも 429 だった）。
- WebFetch は PDF を読めないが、原本を repo の外（`~/.claude/projects/…/tool-results/`）に保存する。pypdf で読める。ScienceDirect・SAGE はスクリプトに 403。
- 固定した正規表現の取りこぼし（AI の語の一覧に「generative artificial intelligence」が無い・前置詞の一覧に「brought by」「elicited by」が無い）は、回し直さずに目で見た補いとして別に記録した（判断 4）。次の検索の正規表現を固定するときに足す。
- 検査器は事実のファイルの見出しの「判定案」「除外」も赤にする（書き換えた）。
- ⚠️ **Codex の予算ガードの hook は、セッションの作業ディレクトリ（C:/GSE-prototype）の台帳を読む**（worktree の台帳ではない）。worktree で作業するときは、記帳する台帳（worktree）とガードが読む台帳（main の作業ツリー）が食い違う。2026-09-30 は 2 巡目がこれで止まり、研究者の決定で Claude 単独に縮退した（判断 14）。台帳を merge するときは起点からの差分の和を採る（09-30 の合算は 892,237 / 16 回）。
- ⚠️ heredoc で Windows のパス（バックスラッシュ）を JSON に書くと壊れる（台帳を壊してコミットした・判断 14）。パスは `/` で書くか Edit を使う。コマンドを `;` でつなぐと、検証が失敗してもコミットまで進む（`&&` でつなぐ）。
- ⚠️ 変異試験の仕掛けは、まず陰性対照（変異なし）が緑になることを確かめる（写した先から import が解決できず、全部の「赤」が無効だった・判断 12 の補足）。
