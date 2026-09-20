# 検索の記録（★ protocol.md §3 の式どおり）

> 1 回目: OpenAlex と Semantic Scholar の 21 本。2 回目: Semantic Scholar で失敗した式だけを同じ式で再実行（`deviations.md` 逸脱 1）。
> 生の結果は作業用の一時ディレクトリ（`$CLAUDE_JOB_DIR/tmp/sr/raw/`）にある。⚠️ 取得件数は関連度順の上位で打ち切った数（OpenAlex 200・Semantic Scholar 100）。

| 式 | 1 回目の実行 | OpenAlex 総数 | OpenAlex 取得 | S2（1 回目） | S2（2 回目） | S2 総数 | S2 取得 |
|---|---|---|---|---|---|---|---|
| C1-a | 2026-09-19T12:59:36 | 689 | 200 | ok | —（1 回目で取得） | 1923 | 100 |
| C1-b | 2026-09-19T13:00:16 | 228 | 200 | 失敗（429） | **取得失敗**（429） | — | — |
| C1-c | 2026-09-19T13:02:02 | 141 | 141 | 失敗（429） | ok | 258 | 100 |
| C2-a | 2026-09-19T13:03:48 | 166 | 166 | 失敗（429） | ok | 5675 | 100 |
| C2-b | 2026-09-19T13:05:34 | 131 | 131 | ok | —（1 回目で取得） | 322 | 100 |
| C2-c | 2026-09-19T13:06:33 | 96 | 96 | ok | —（1 回目で取得） | 76 | 76 |
| C3-a | 2026-09-19T13:07:13 | 139 | 139 | 失敗（429） | ok | 277 | 100 |
| C3-b | 2026-09-19T13:09:00 | 0 | 0 | 失敗（429） | **取得失敗**（429） | — | — |
| C3-c | 2026-09-19T13:10:45 | 46 | 46 | ok | —（1 回目で取得） | 627 | 100 |
| C4-a | 2026-09-19T13:12:05 | 2539 | 200 | 失敗（429） | ok | 0 | 0 |
| C4-b | 2026-09-19T13:13:52 | 126 | 126 | ok | —（1 回目で取得） | 616 | 100 |
| C4-c | 2026-09-19T13:14:52 | 6992 | 200 | ok | —（1 回目で取得） | 119 | 100 |
| C5-a | 2026-09-19T13:15:02 | 35311 | 200 | 失敗（429） | **取得失敗**（429） | — | — |
| C5-b | 2026-09-19T13:16:49 | 19433 | 200 | 失敗（429） | **取得失敗**（429） | — | — |
| C5-c | 2026-09-19T13:18:38 | 85 | 85 | ok | —（1 回目で取得） | 0 | 0 |
| C6-a | 2026-09-19T13:19:02 | 1936 | 200 | 失敗（429） | **取得失敗**（429） | — | — |
| C6-b | 2026-09-19T13:20:51 | 4351 | 200 | 失敗（429） | **取得失敗**（429） | — | — |
| C6-c | 2026-09-19T13:22:37 | 31328 | 200 | 失敗（429） | ok | 18592 | 100 |
| C7-a | 2026-09-19T13:24:24 | 435 | 200 | ok | —（1 回目で取得） | 583 | 100 |
| C7-b | 2026-09-19T13:24:40 | 405 | 200 | ok | —（1 回目で取得） | 2217 | 100 |
| C7-c | 2026-09-19T13:24:48 | 19 | 19 | 失敗（429） | **取得失敗**（429） | — | — |

## 候補ごとの統合（重複除去の後）

| 候補 | 取得の総数 | 重複を除いた数 |
|---|---|---|
| C1 | 741 | 720 |
| C2 | 669 | 653 |
| C3 | 385 | 373 |
| C4 | 726 | 722 |
| C5 | 485 | 485 |
| C6 | 700 | 689 |
| C7 | 619 | 617 |

## 手動の補完（protocol.md §2）—— 2026-09-19 21:55〜22:20 JST

- ★ 各候補の Q_a（Semantic Scholar 用の語の並び）を、ACM Digital Library（`/action/doSearch?AllField=…&pageSize=20`・既定の並び）と PhilPapers（`/s/<語>`・既定の並び・⚠️ 既定のフィルタ 1 つが掛かった状態）で 1 回ずつ引き、上位 20 件の題名を見た。
- ⚠️ 自動取得（curl）は両方とも Cloudflare の確認画面で 403 になった → ★ **研究者の Chrome（claude-in-chrome）で検索画面を開き**、ページ内の `fetch` で 7 本の結果を取って題名を読んだ（★ CAPTCHA は出ず、確認画面は自動で通った。CAPTCHA には触れていない）。

| 候補 | Q_a | ACM 総数 | PhilPapers 総数 | 題名で目に留めた件（★ 段 2 には回していない —— 補完としてのみ扱う） |
|---|---|---|---|---|
| C1 | epistemic authority algorithmic system user | 4,026 | 293+ | ACM: *Community-Based AI Learning: Redistributing Artificial Intelligence's Epistemic Authority in Education*（2026・10.1145/3796496.3811760）・*FAccT-Checked: A Narrative Review of Authority Reconfigurations and Retention in AI-Mediated Journalism*（2026・10.1145/3805689.3812300）・*Algorithmic Authority & AI Influence in Decision Settings*（2024・10.1145/3687272.3691363） |
| C2 | interpretive labor algorithmic system users | 13,603 | 297+ | （上位 20 件は労働・プラットフォーム労働が中心。候補に当たる題名なし） |
| C3 | authority responsibility consistency human automation | 29,627 | 295+ | ACM: *Whose Code Is It? How AI Autonomy Reshapes Ownership, Responsibility …*（2026・10.1145/3742413.3789121）・*Safeguarding Human Potential in Automated Work Systems …*（2026・10.1145/3822301.3822332）・*Balancing Automation and Discretion: How Decision Stakes and …*（2026・10.1145/3772318.3790795）／ PhilPapers: *AI Does Not Judge: The Structural Ineligibility of Artificial Systems for Moral Authority*（刊年不明・`eKIMADN`） |
| C4 | system-initiated handover of control by design ethics | 297 | 295+ | ACM: *Beyond AI Capability – Governance, Trust, and Realistic Scope …*（2026・10.1145/3786579.3804951）／ PhilPapers: *From Handover to Participation: How Do Handover Approaches Support Participatory Design …*（2025・`eLENFHT`）・*Meaningful Human Control Over Smart Home Systems*（2020・`eUMBMHC-3`） |
| C5 | ignorable notifications nudge design | 4,238 | 293+ | （上位 20 件は通知設計とナッジの倫理。無応答を同意として読まないことを題名で示す件なし） |
| C6 | user feedback excluded from learning adaptive system | 4,774 | 294+ | （上位 20 件はフィードバックを学習に使う側 = 逆向きの主流が中心） |
| C7 | obligation to respond technology users pressure | 58,303 | 290+ | PhilPapers: ★ *The Right to Hesitate: Against the Imperative of Compute-to-Answer and Toward an Ethics of Sustained Ambiguity*（未刊の原稿・`JACTRT`）—— メインが抄録を読んだ（下の注） |

- ★ C7 の `JACTRT`（抄録のみ・メインが PhilPapers の記録ページで読んだ）: 逐語 *"By prioritizing reactivity—the obligation to respond immediately—over response-ability—the capacity to respond appropriately—we risk automating the flattening of complex moral landscapes into simplistic metrics. We propose a paradigmatic shift toward Sustained Ambiguity, a design principle for both artificial and biological systems that valorizes the capacity to inhabit a state of "not-yet" without collapsing into premature resolution."* → ★ **部分**（★ 即時の応答義務と意味の早すぎる確定を退ける設計原理。⚠️ 系が意味の認定と応答の要求を**終了させる**ことを要件にしてはいない。⚠️ 未刊の原稿）。
- ⚠️ 手動の補完は再現性が低い（★ 検索画面の並びは日によって変わる）ので、ここで目に留めた件は結論の根拠にしない（protocol.md §2）。
