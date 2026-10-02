# 次セッション — AI 疲労 文献 DB: 研究者の 34 件の判定（判定者 1）の続き（群 10・11）＋ 確認の結果・AI判定比較 ＋ 新規性の確認（B）＋ 完了

> 更新: 2026-10-01（2 つ目のセッションの終わり・コンテキスト 63% で群 9 の切れ目で区切った）。⚠️ **このメモを一次資料にしない。** 一次は `.steering/20261001-ai-fatigue-34-screening/` の requirement.md・design.md（聞く前に固定・書き換えない）・decisions.md 判断 1〜7・`screening-log.jsonl`・`measurement-issues.md`。
> ★ ユーザーは **判定者 1**。DB を作ったのは「相手の研究者」。研究者が決めることはユーザーに聞かない（「研究者の決定待ち」と書く）。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-34-screening-cont.md を読んで、AI 疲労 文献 DB の 34 件の判定（判定者 1）の続きをしてください。タスクは .steering/20261001-ai-fatigue-34-screening/（requirement.md・design.md・decisions.md 判断 1〜7・tasklist.md・measurement-issues.md を先に読む）。群 9 の抽出の確定（6 行）と群 10（AF026・AF028・AF027・AF025・AF029）の 1 回目から、design.md §3 の形で 2 段の AskUserQuestion を続ける。

⚠️ worktree C:\wt\ai-fatigue-judge-file のブランチ docs/ai-fatigue-34-screening（未 push・ローカルのコミットだけ）。git add -A / git add <dir> は使わない。
⚠️ 1 回目の問いには AI の判定・推奨を載せない（check_workbook.py が選択肢の固定と禁止の語を検査する）。1 回目に載せる事実はメインが本文で確かめてから。2 回目は GPT 版・Claude 版の『適格性評価』だけでなく『方法論評価』の懸念・引用の範囲も見せる（scratchpad の ai_detail.py を作り直す・判断 4 の 3）。
⚠️ 研究者の元のファイル（09-18・48ba8b90…）は変えない。写しは scripts/write_workbook.py だけで書く（Downloads の写しが最後に書いたものと違えば止まる → 止まったら聞く）。
⚠️ 外部に出る操作（著者への照会・フォーム・OSF）はしない。学術 API にメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない（本文は git の外の C:\Users\johnd\Downloads\ai-fatigue-fulltext\）。有料の本文は使わない。出版社のページが人間確認で止まったら、Chrome でタブを開いてユーザーに通してもらう（Claude は触らない・記憶 feedback_captcha_user_passes）。
⚠️ Chrome（mcp__claude-in-chrome__*）を使う前に browser-verification Skill を読む。サブエージェントに渡すなら subagent-delegation Skill（model 明示・入れ子禁止・締切・Chrome の可否を書く）。
★ 完了時は code-reviewer ＋ security-checker（並列）・/cross-review 2 巡（Codex の当日の実消費を先に確かめる。足りなければ上限を引き上げてよい＝2026-10-01 ユーザーの指示・判断 3）・git-workflow ルール 6。応答は日本語。コンテキストが半分ほどで群の切れ目なら引き継ぎを書いて区切る。
```

## §1 いまの状態（2026-10-01・2 つ目のセッションの終わり）

| 何 | 状態 | どこ |
|---|---|---|
| 判定済み | **25 / 34**（群 1〜9）。ログ seq 1〜71 | `screening-log.jsonl`・decisions.md 判断 2・4〜7 の表 |
| 含める（中心-A 6） | AF001・AF005・AF007・AF008・AF010・AF011 | 品質評価は全件確定（`data/quality-rows.json`） |
| 含める（中心-B 3） | AF004・AF012・AF019 | 同上 |
| 保留 | AF002・AF003・AF009（E6）／AF006・AF024 | — |
| 除外 E2（背景保持） | AF020・AF021・AF022・AF023 | — |
| 除外 E4 | AF034（訂正連結）／AF013〜AF018（既存レビュー・背景保持） | — |
| 抽出の確定 | 群 1〜8 は確定（stage x）。**群 9 の 6 行は data に足したが確定の問いは未** | `data/extract-rows.json`（25 行） |
| 写し | 書き込み済み・`check_workbook.py` 違反 0・`--selftest` PASS | Downloads と `archive/`（SHA は `archive/copy-sha256.txt`） |
| 測定の論点メモ | M1〜M7（帰属の段階・依存症型の尺度・言い換え・構成概念の境界・報告の不整合・標本の独立・名前と中身のずれ） | `measurement-issues.md`（ユーザーの指示で作った・C の材料） |
| コミット | 53bef894（群 3・4）→ 75437159（群 5・6）→ 442e8de6（群 7・8）→ ff341ca3（群 9） | ブランチ docs/ai-fatigue-34-screening（未 push） |

## §2 次にやること（順）

1. **群 9 の抽出の確定**（AF017・AF013・AF014・AF015・AF016・AF018 の 6 行・stage x・群の先頭 AF017 で記録）を、群 10 の 1 回目と同じ AskUserQuestion で聞く。
2. **群 10 尺度・理論**（AF026 → AF028 → AF027 → AF025 → AF029）・**群 11 方法論**（AF030 → AF031 → AF033 → AF032）。一次研究でない件の固定の選択肢（`含める（一次研究として読む）`／`除外 E4（保持の区分は対応表で決まる）`／`除外（E4 以外）`／`保留`）。材料は `wave1/extract-X5.md`（AF027・AF028・AF031 は抄録のみ）。尺度の原著は E4（2026-10-01 の読み方）。方法論は対応表で「方法論保持」。
3. 34 件の後: 『AI判定比較』（write_workbook.py が 34 件そろうと自動で書く）・`data/checks-rows.json`（『確認事項』12 行・『AI適格性評価』の「次の確認・作業」34 行・ユーザーのメモの項目。材料は `wave1/` の各件の欄 12〜14 とログの `next`）・`check_workbook.py --final`。
4. **B: `novelty-check.md`**（§3 の下書き。結論に使う箇所だけメインが原文で確かめる。既存レビュー 6 件は群 9 で全文を読める状態〈AF015 は抄録のみ〉）→ C（測定論）に進むかをユーザーが次のタスクの始めに決める材料として書く。`measurement-issues.md` の M1〜M7 を「既存レビューが扱っているか」の軸に使える。
5. 完了の手順（レビュー 2 本並列・/cross-review 2 巡・出荷）→ 次のタスク（D: 追加候補の絞り込み〈AISeL の Bunt & Venter「Prompt Fatigue in Generative AI」ICIS 2025 TREO を候補に〉・C: 測定論・提案のドキュメント）の引き継ぎ。

### 研究者の決定待ち（提案のドキュメントに入れる）

- AF002 の PDF の共有（研究者の DB に「既出PDF」「元Library全文参照」の記録・判断 4）。AF003 は誰も本文を持っていない。
- 基準の読み方: 定義の段の AI 帰属だけで中心-A にしてよいか（M1・AF008・AF002）。学習の燃え尽きの代理項目を疲労に含めるか（AF024・AF019 の扱いと揃える）。
- 著者への照会（AF004 の交互作用の向き・AF011 の解析の単位・AF012 の倫理・AF006 の分母・AF010 の倫理と一致度）。

### 聞き方の型（design.md §3 ＋ 判断 2・4 の逸脱）

- 1 回目: 1 件 1 問・最大 4 件/回。選択肢と説明文は固定（一次研究の 4 つ・一次研究でない件の 4 つ）。`除外`・`除外（E4 以外）` は続けて E コードを聞く（stage `1e`・選択肢 E1／E2／E3／E5）。
- 2 回目: GPT 版・Claude 版（適格性＋方法論の懸念・引用の範囲）＋全文で新しく分かったこと。保留・変えた件は理由を複数選択で聞く。
- 記録: scratchpad に `.py` で組んで `json.dump` → `scripts/log_add.py`。抽出・品質の行も同じ `.py` の `--data` で `data/*.json` に足す（列数は assert）。→ `write_workbook.py` → `check_workbook.py`。

## §3 新規性の確認（B）の下書き（波 1 の X4・⚠️ メインは未照合）

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
- ⚠️ 「新規性がある」とはまだ言えない。結論に使う箇所はメインが原文で確かめる。ただし AF004 は考察で Parasuraman & Riley 1997（automation bias）を引く（一次研究の側には系譜への言及がある）。

## §4 落とし穴（2 つのセッションで起きたこと）

- 引き継ぎが `C:\GSE-prototype` に無いことがある → `git worktree list` と `git log --all -- <パス>`。
- git-bash の heredoc でバックスラッシュが壊れる → パスは前向きのスラッシュ・スクリプトは Write で置く。Python の出力は `PYTHONIOENCODING=utf-8`。openpyxl は `uv run --with openpyxl`。
- `ai_judgments.py` の出力先に `GSE-prototype` を含むパス（scratchpad）は拒否される → `C:/Users/johnd/AppData/Local/Temp/ai34-judgments.json` に出した。2 回目の材料は scratchpad の `ai_detail.py`（GPT・Claude の適格性・方法論・スクリーニング案を件ごとに出す）を使った。
- **2 回目の Claude 版は『方法論評価』まで見る**（AF004 で「AI の 2 版とも触れていない」と誤って書き、訂正して聞き直した・判断 4）。
- 1 回目の問いに項目文の逐語「ChatGPT」を載せると禁止語 `GPT` に当たった → 規則を `(?<!Chat)GPT` に絞った（判断 4）。
- 問いの誤字はログに逐語で残し、decisions と次の問いで知らせた（AF012「判別妙当性」・AF020「皆に無い」）。
- ScienceDirect: ユーザーが人間確認を通すと、同じセッションで他の論文のページも開けた。OA の本文（AF004・AF019・AF034）は Chrome の `get_page_text`／`javascript_tool` で読める。有料の論文は抄録・ハイライト・序論・節の冒頭（Article preview）が無料で読める（AF002・AF003）。
- ページのテキストをローカルの受け口（127.0.0.1 の HTTP サーバ）に送って保存する方法は権限の判定で拒否された → 使わない。メモは Write で短い逐語だけ。
- `javascript_tool` の返り値に URL の query string が入ると `[BLOCKED: Cookie/query string data]` になる。そのときは **query を返さない**（`new URL(u).origin + new URL(u).pathname` だけを返す）。⚠️ 区切り文字（`?&=`）の置き換えで遮断をくぐらない —— 値（トークン・署名）はそのまま残る（2026-10-02 の Codex の指摘で訂正・`20261001-ai-fatigue-34-screening/decisions.md` 判断 14）。
- Codex: 2026-10-01 は当日の上限にほぼ到達（origin/main の台帳 291,174）。ユーザーの指示（判断 3）で、足りなければ `.codex/budget.json` の `daily_token_budget` を上げてよい（`tokens_used` は触らない・理由と前後の値を `_comment_budget_<日付>` に残してコミット）。予算ガードの hook は `C:\GSE-prototype` の台帳を読むので、上げるのはそちらにも要るかを回す前に確かめる。
