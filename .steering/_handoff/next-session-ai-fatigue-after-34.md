# 次セッション — AI 疲労 文献 DB: 34 件の後（C に進むかの決定 → 研究者への提案のドキュメント → D: 追加候補の絞り込み）

> 作成: 2026-10-02（34 件の判定のタスクの 3 つ目のセッションの終わり）。⚠️ **このメモを一次資料にしない。** 一次は `.steering/20261001-ai-fatigue-34-screening/`（decisions.md 判断 1〜12・novelty-check.md・measurement-issues.md・screening-log.jsonl・data/*.json）。
> ★ ユーザーは **判定者 1**。DB を作ったのは「相手の研究者」（判定者 2 の人選・最終判定・登録型にするかを決める人）。研究者が決めることはユーザーに聞かない（「研究者の決定待ち」と書く）。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-after-34.md を読んで、AI 疲労 文献 DB の 34 件の後のタスクを始めてください。まず /start-task。前のタスクは .steering/20261001-ai-fatigue-34-screening/（decisions.md 判断 1〜12・novelty-check.md・measurement-issues.md を先に読む）。最初に、測定論の論文（C）に進むかを AskUserQuestion で聞く（推奨と理由を添える・材料は novelty-check.md §5）。次に、研究者への提案のドキュメントの中身と、D（追加候補の絞り込み）の範囲を決める。

⚠️ git add -A / git add <dir> は使わない。作業ツリーに別ブランチの未コミット作業がある（C:\GSE-prototype は feature/ime-m3-prereg）。新しいブランチは worktree で切る。
⚠️ 研究者の元のファイル（09-18・48ba8b90…）は変えない。判定者 1 の写し（Downloads\AI_fatigue_database_2026-09-18_judge1.xlsx・SHA は archive/copy-sha256.txt）は前のタスクの scripts/write_workbook.py だけで書く。
⚠️ 外部に出る操作（研究者・著者への送信・フォーム・OSF）はしない。学術 API にメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない（本文は git の外の C:\Users\johnd\Downloads\ai-fatigue-fulltext\）。有料の本文は使わない。
⚠️ 抄録だけの件・ボット検査で止まった件は、問いを組む前に Chrome で無料の版（機関リポジトリ・OA・出版社の無料の補足資料）を開き直す（記憶 feedback_captcha_user_passes・2026-10-02 に再指摘）。Chrome の前に browser-verification Skill、サブエージェントの前に subagent-delegation Skill を読む。
★ 完了時は code-reviewer ＋ security-checker（並列）・/cross-review 2 巡（Codex の当日の実消費を先に確かめる。足りなければ上限を引き上げてよい＝判断 3）・git-workflow ルール 6。応答は日本語。コンテキストが半分ほどで区切りなら引き継ぎを書いて区切る。
```

## §1 前のタスクで終わったこと（2026-10-02）

| 何 | 状態 | どこ |
|---|---|---|
| 34 件の判定（判定者 1） | **完了**。含める 9（中心-A 6: AF001・AF005・AF007・AF008・AF010・AF011／中心-B 3: AF004・AF012・AF019）・保留 5（E6: AF002・AF003・AF009／材料と構成概念: AF006・AF024）・除外 20（E2 背景 4・E4 既存レビュー 6・尺度の原著 5・方法論 4・訂正 1） | `screening-log.jsonl`（92 行）・decisions 判断 2・4〜9 |
| 写し | 『スクリーニング』の判定者 1 の欄・『AI判定比較』34 行・足したシート 6 枚（はじめに・問いと答え・全文抽出・品質評価・確認の結果） | Downloads と `archive/`（`check_workbook.py --final` 違反 0・`--selftest` PASS） |
| 新規性の確認（B） | 「AI 疲労の尺度は未検証・作るべき」「概念の境界」は既存（AF014・Nobles）。本文を読めた 6 本に無いもの = 研究を AI への帰属の段階で分けた表・言い換え尺度・依存症型尺度・標本の独立・報告の不整合・自動化の人間工学との橋渡し（数えた語と読んだ行の範囲・AF015 は未確認・系統的な探索の前の暫定） | `novelty-check.md` §5 |
| 確認の結果 | 確認事項 12・次の確認・作業 34・ユーザーのメモ 8（一次で確認 15・一部確認 26・入手不可 9・研究者の確認待ち 3・未着手 1） | `data/checks-rows.json`・判断 11 |

## §2 次にやること（順）

0. ⚠️★ **PR #288（`docs/ai-fatigue-34-screening`）がまだ merge されていなければ、これが先**（判断 13）。Codex は 2026-10-02 02:04 に提供元の利用上限で回らず、ユーザーの決定で「PR まで・merge は Codex 2 巡の後」。worktree `C:\wt\ai-fatigue-judge-file` で:
   - 1 巡目（道具）: `bash scripts/run-codex-review.sh 9f5796d5..<HEAD> -- <scripts 7 本・requirement.md・design.md>`（出力は scratchpad）。2 回目（記録）: `decisions.md・novelty-check.md・tasklist.md・measurement-issues.md・requirement.md・_handoff の 2 ファイル`。⚠️ `.xlsx`・`wave1/`・`screening-log.jsonl`・`data/*.json` は渡さない。
   - 2 巡目: 1 巡目の直しで足した規則の境界条件だけ（パスを絞る）。Claude 側の 2 巡は判断 12・13 で済んでいる。
   - 「codex exec error」なら、最小のプロンプトで `codex exec --json` を 1 回試して JSON の `error` を読む（ラッパーは標準エラーを捨てる）。上限なら止まって聞く。
   - 指摘に対応 → `check_workbook.py --final`・`--selftest` → commit・push → CI 緑 → `gh pr merge 288 --merge` → main の CI 発火確認（git-workflow ルール 6）。台帳（`.codex/budget.json`）の記帳もコミットに含める。
1. **C に進むか**（ユーザーが決める・推奨と理由を添えて聞く）。材料: novelty-check.md §5。前提: (a) 追加候補（D）の中の既存レビューを先に当たる、(b) 基準の読み方（M1: 定義の段の AI 帰属だけで中心-A か）は研究者の決定待ち、(c) Nobles の Zenodo の公開版を確かめる。
2. **研究者への提案のドキュメント**（判断 8 の「次のタスク」）。入れるもの:
   - 写しの渡し方: ⚠️ **判定者 2 に写しを渡さない**（『判定者1_はじめに』に書いた）。判定者 2 には元のファイルか、判定者 1 の列と `判定者1_` のシートを除いた版。
   - 研究者の決定待ちの一覧: AF002 の PDF の共有（研究者の DB に「既出PDF」「元Library全文参照」）／基準の読み方（定義の段の AI 帰属・学習の燃え尽きの代理項目 = AF024・AF019 と揃えるか）／著者への照会（AF004 の交互作用の向き・AF011 の解析の単位・AF012 の倫理・AF006 の分母・AF010 の倫理と一致度）／AF006〜AF009・AF002/AF003 の標本の独立（M6）／AF018 の 14 件の統一的な再抽出をするか（確認の結果の「未着手」）／判定者 2 の人選・本検索。
   - Claude の関与の開示（AF002・AF003 の見立て・AF004 の再計算・抽出と品質の下書き）。
   - 登録型のレビューにするなら（N-05 の草稿 v0.2 と確認票・判断 1）。
   - 元の『はじめに』の数式は写しでは計算済みの値を持たない（Excel で開けば再計算）。
3. **D: 追加候補の絞り込み**（220 件・判定者用ファイル `10107fcf…`）。新規性の確認の前提 (a) として、候補の中の既存レビューを先に当たる。候補に足すもの: AISeL の Bunt & Venter「Prompt Fatigue in Generative AI」ICIS 2025 TREO。
4. 完了の手順（レビュー 2 本並列・/cross-review 2 巡・出荷）。

## §3 落とし穴（34 件のタスクで起きたこと）

- 引き継ぎが `C:\GSE-prototype` に無いことがある → `git worktree list` と `git log --all -- <パス>`。
- git-bash の heredoc・`python -c` でバックスラッシュが壊れる → スクリプトは Write で置いて回す。Python の出力は `PYTHONIOENCODING=utf-8`。openpyxl は `uv run --with openpyxl`。
- **AskUserQuestion の問いを `\uXXXX` のエスケープで手打ちすると誤字が入る**（「抽録」「批判的吁味」が実際に出た）→ 問いの文は日本語のまま書く。ログには問いの逐語を残し、誤字は note と decisions に書く。
- 1 回目の問いに文献の中身として「推奨」「勧める」が入ると、検査の禁止語に当たる → 規則は件と逐語の句の対で除外する（`STAGE1_EXEMPT`・判断 9・12）。
- openpyxl: `ws.cell(r, c, None)` は値を書き換えない（空にするのは `.value = None`）。保存すると数式の計算済みの値が消える。
- Chrome: Tilburg・RGU の Cloudflare の待機は人手なしで通った。RGU・出版社のリンクを開くと Downloads に落ちる（本文置き場へ移す）。curl もページ内の取得も止まる PDF（INFORMS の補足資料）は、タブに表示してユーザーに Ctrl+S で保存してもらう。`javascript_tool` の返り値は `replace(/[?&=]/g,' ')` してから返す。
- サブエージェントの下書きは「メインが原文で」を付け過ぎる → 行ごとに経路を付け直す（判断 11）。
- Codex の台帳はブランチごと（記憶 project_codex_ledger_branch_split）。予算ガードの hook は `C:\GSE-prototype` の台帳を読む。
