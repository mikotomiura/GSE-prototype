# 次セッション — AI 疲労 文献 DB: 研究者の 34 件の判定（判定者 1）の続き（群 3〜11）＋ 新規性の確認のまとめ

> 更新: 2026-10-01（1 つ目のセッションの終わり・コンテキスト約 4 割で群 2 の切れ目で区切った）。⚠️ **このメモを一次資料にしない。** 一次は `.steering/20261001-ai-fatigue-34-screening/` の requirement.md・design.md（聞く前に固定・書き換えない）・decisions.md 判断 1〜2・`screening-log.jsonl`。
> ★ ユーザーは **判定者 1**。DB を作ったのは「相手の研究者」。研究者が決めることはユーザーに聞かない（「研究者の決定待ち」と書く）。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-34-screening-cont.md を読んで、AI 疲労 文献 DB の 34 件の判定（判定者 1）の続きをしてください。タスクは .steering/20261001-ai-fatigue-34-screening/（requirement.md・design.md・decisions.md 判断 1〜2・tasklist.md を先に読む）。群 3（AF002・AF003）から design.md §3 の形で 2 段の AskUserQuestion を続ける。

⚠️ worktree C:\wt\ai-fatigue-judge-file のブランチ docs/ai-fatigue-34-screening（未 push・ローカルのコミットだけ）。git add -A / git add <dir> は使わない。
⚠️ 1 回目の問いには AI の判定・推奨を載せない（check_workbook.py が選択肢の固定と禁止の語を検査する）。1 回目に載せる事実はメインが本文で確かめてから。2 回目に GPT 版・Claude 版を見せる（scripts/ai_judgments.py で scratchpad に作り直す）。
⚠️ 研究者の元のファイル（09-18・48ba8b90…）は変えない。写しは scripts/write_workbook.py だけで書く（Downloads の写しが最後に書いたものと違えば止まる → 止まったら聞く）。
⚠️ 外部に出る操作（著者への照会・フォーム・OSF）はしない。学術 API にメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない（本文は git の外の C:\Users\johnd\Downloads\ai-fatigue-fulltext\）。有料の本文は使わない。
⚠️ Chrome（mcp__claude-in-chrome__*）を使う前に browser-verification Skill を読む。サブエージェントに渡すなら subagent-delegation Skill（model 明示・入れ子禁止・締切・Chrome の可否を書く）。
★ 完了時は code-reviewer ＋ security-checker（並列）・/cross-review 2 巡（Codex の当日の実消費を先に確かめる）・git-workflow ルール 6。応答は日本語。コンテキストが半分ほどで群の切れ目なら引き継ぎを書いて区切る。
```

## §1 いまの状態（2026-10-01）

| 何 | 状態 | どこ |
|---|---|---|
| 判定済み | 5 / 34（群 1・2） | `screening-log.jsonl` seq 1〜14・decisions.md 判断 2 の表 |
| 含める | AF001（中心-A）・AF007（中心-A）・AF008（中心-A） | 品質評価は 3 件とも確定（`data/quality-rows.json`） |
| 保留 | AF006（材料が足りない）・AF009（E6 全文なし） | — |
| 抽出の確定 | 5 件（AF001・AF006〜AF009） | `data/extract-rows.json` |
| 写し | 書き込み済み・`check_workbook.py` 違反 0 | `C:\Users\johnd\Downloads\AI_fatigue_database_2026-09-18_judge1.xlsx` と `archive/`（SHA は `archive/copy-sha256.txt`） |
| 波 1 の抽出（34 件＋Nobles・サブエージェントの下書き） | 済み | `wave1/extract-X1〜X5.md`（X1: AF001〜005・034／X2: AF006〜012／X3: AF019〜024／X4: AF013〜018・Nobles／X5: AF025〜033） |
| 本文 | 23 件ぶんは手元・取れなかった件は decisions.md 判断 2 | `C:\Users\johnd\Downloads\ai-fatigue-fulltext\<ID>\` |
| `判定者1_確認の結果` | 未作成 | `data/checks-rows.json` を作ると write_workbook.py がシートを足す |
| 新規性の確認（B） | 下書きだけ（X4）・`novelty-check.md` は未作成 | 下の §3 |

## §2 次にやること（順）

1. **群 3 AF002・AF003**（同じ著者・有料・抄録も未取得）: 出版社の抄録のページ（無料で表示される抄録・ハイライト）を Chrome で読めるか試す（browser-verification Skill を先に）。読めなければ材料なしで 1 回目を聞く（全文確認は `入手不可`）。ユーザーのメモ: AF003 の「大規模」の具体的な人数・AF002 の応答とプロンプトのどちらの不確実性が疲労と強く結びついたか・標本の独立。
2. **群 4 AF004・AF034**: どちらも gold OA だが curl は CAPTCHA。Chrome で全文を読めるか試す（AF004 の抄録は OpenAlex にある）。訂正の中身を原著の抽出に反映（『確認事項』）。
3. 群 5〜8（AF005・AF011・AF010／AF012・AF019・AF023／AF024・AF021・AF022／AF020）→ 群 9 既存レビュー（AF017→AF013→AF014→AF015→AF016→AF018）→ 群 10 尺度・理論（AF026→AF028→AF027→AF025→AF029）→ 群 11 方法論（AF030→AF031→AF033→AF032）。一次研究でない 16 件は design.md §3 の「一次研究でない件」の選択肢（固定）。
4. 34 件の後: 『AI判定比較』（write_workbook.py が 34 件そろうと自動で書く）・`data/checks-rows.json`（『確認事項』12 行・『AI適格性評価』の「次の確認・作業」34 行・ユーザーのメモの項目。材料は `wave1/` の各件の欄 12〜14）・`check_workbook.py --final`。
5. **B: `novelty-check.md`**（§3 の下書きを、結論に使う箇所だけメインが原文で確かめてから）→ 測定論の論文（C）に進むかはユーザーが次のタスクの始めに決める材料として書く。
6. 完了の手順（レビュー・/cross-review 2 巡・出荷）→ 次のタスク（D: 追加候補の絞り込み・C: 測定論・提案のドキュメント）の引き継ぎ。

### 聞き方の型（design.md §3 ＋ 判断 2 の逸脱）

- 1 回目: 1 件 1 問・最大 4 件/回。選択肢は固定（一次研究: `含める（中心-A）`／`含める（中心-B）`／`除外`／`保留`。一次研究でない件: `含める（一次研究として読む）`／`除外 E4（保持の区分は対応表で決まる）`／`除外（E4 以外）`／`保留`）。説明文も固定。問いの本文は 題名・材料／種類／P／C（AI への帰属の逐語）／AI／同じ群／基準 の順。`除外` は続けて E コードを聞く（stage `1e`）。
- 2 回目: GPT 版・Claude 版の判定と根拠＋全文で新しく分かったこと → `1 回目のまま`／`AI の判定に変える`（2 版が違えば分ける）／`別の判定に変える`。保留・変えた件は理由を複数選択で聞く。
- 含めた一次研究: 品質評価の下書き（JBI〈横断 8・質的 10・RCT 13〉・尺度開発は COSMIN・6 領域・合計点なし）に推奨と理由を添えて聞く（stage `q`）。群の終わりに抽出の行の確定（stage `x`・群の先頭の件で記録）。
- 記録: `scripts/log_add.py` に JSON の配列を標準入力で（scratchpad に .py で組んで json.dump → パイプ。`result` に verdict・use・ecode・basis〈全文/抄録〉・reason・reason_summary・next・date）→ `write_workbook.py` → `check_workbook.py`。

## §3 新規性の確認（B）の下書き（X4・⚠️ メインは未照合）

| 文献 | (A1) AI 疲労と一般の疲労の区別 | (A2) 単一項目・自己報告の批判 | (A3) 自由記述のコード化の妥当性 | (A4) 測り方の内訳の表 | (B) 自動化の人間工学の系譜 |
|---|---|---|---|---|---|
| AF013 | 節（概念図のみ） | なし | なし | なし | 1 文（complacency） |
| AF014 | 段落 | 1 文 | なし | なし | 1 文（overreliance） |
| AF015 | 未確認（抄録のみ） | 〃 | 〃 | 〃 | 〃 |
| AF016 | なし（認知負荷が対象） | 段落 | 1 文 | 節 | なし |
| AF017 | 節（対象はストレッサー） | 1 文 | なし | なし | 1 文（vigilance・over-reliance） |
| AF018 | なし | なし | なし | なし | 節（過信が主題）＋automation bias 1 文 |
| Nobles 2026 | 節（概念境界の表） | 段落 | 1 文 | なし | 1 文（passive reliance の語のみ） |

- X4 の報告: どの件も Parasuraman・Hancock・Matthews・Desmond の引用 0 件、passive fatigue・alarm fatigue・alert fatigue も 0 件。Nobles の表 03・04 に尺度・測定法の列は無い。
- ⚠️ 「新規性がある」とはまだ言えない（下書き・未照合・AF015 は抄録だけ）。結論に使う箇所はメインが原文で確かめる。

## §4 落とし穴（このセッションで起きたこと）

- 引き継ぎが `C:\GSE-prototype` に無いことがある → `git worktree list` と `git log --all -- <パス>`。
- git-bash の heredoc でバックスラッシュ（`C:\\Users`）が壊れて Python が `\U` で落ちた → Windows のパスは前向きのスラッシュにするか、スクリプトを Write で置く（記憶 `feedback_backslash_via_bash_heredoc`）。
- Python の出力は cp932 で落ちる → `PYTHONIOENCODING=utf-8`。openpyxl は `uv run --with openpyxl`。
- ScienceDirect は curl で 403・ブラウザで CAPTCHA（AF002・003・004・019・034）。回避しない。
- Bash の自動判定が一時的に止まることがある（「no verdict」）→ Read・Grep で代わりに読む。
- Codex: 2026-10-01 は当日の上限にほぼ到達（origin/main の台帳 291,174）。/cross-review は日を改めて（回す前に main と本ブランチの台帳を合算で見る）。
