# 引き継ぎ: 核 2 を磨く —— AI 疲労・デジタル疲労・一般の疲労の弁別を確かめる研究の実現性（倫理審査の経路を先に）

作成 2026-10-14（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。AskUserQuestion には推奨と理由を添える。

## 0. 始め方

worktree `/Users/johnd/GSE-prototype-af-core2`（ブランチ `docs/ai-fatigue-core2-discriminant`・`docs/ai-fatigue-motivation-claims` から切った）で新しいセッションを開き、次を打ち込む。

```
.steering/_handoff/next-session-ai-fatigue-core2-discriminant.md を読んで、/start-task でタスクを立て、§3 の問いを grill で確定してから §4 を進めて。研究にするか・質問紙を集めるかは研究者が決める。
```

- `.idea/` は版管理の外なので worktree には無い。読むときは `/Users/johnd/GSE-prototype/.idea/20261005-motivation-fatigue-reentry-surface.md` を開く。
- 核 1 の引き継ぎ（`next-session-ai-fatigue-core1-item-analysis.md`）とは別のタスク。並行してよいが、`docs/references.md` の採番が衝突するので、両方で出典を足すときは片方を先に main へ入れてから、もう片方を取り込んで採番する。

## 1. 前のタスクで分かったこと（一次は各ファイル）

- タスク: `.steering/20261014-ai-fatigue-motivation-claims/`（summary.md・decisions.md 判断 1〜6）。カード: `docs/literature/20261014-ai-fatigue-motivation-discriminant.md`（S-AF2・カード 3〜5・[P485]–[P497]）。
- 核 2「AI 疲労とデジタル疲労が両方高い人がいる。ただしそれは画面越しの作業に共通する 1 つの疲労の 2 つの呼び名かもしれない」。
  - 同じ標本で AI 疲労・デジタル疲労・一般の疲労・燃え尽きを合同に検定した研究は、S-AF2 の網では 0 件（判定不能 11。本文中にしか書かれない検定は拾えていない可能性がある）。
  - 隣の材料は「重なりは大きいが同一ではない」側: AI 疲労と画面疲労 r = .60・SNS 疲労 .63・一般・臨床の疲労 .52〜.63、他に足して AI の利用の説明が ΔR² = .08 [P362] [P485]／デジタル疲労と燃え尽きの HTMT 0.83 [P491]／ビデオ会議疲労と燃え尽き r = .51 [P492]／テクノストレスの尺度の中の疲労は固有の信頼性が小さい（ωh 0.22）[P493]／2024 年の ESM でビデオ会議と疲れの関係が見られない [P495]。神経症傾向 .49・否定的感情 .47 [P362]（共通の原因の候補・AI 疲労 DB の M2）。
  - Lau et al. 研究 3（Prolific・N = 290）は必要な変数をほぼ全部持つが、公開データ [P486] は AI 疲労の合計点だけ。
  - 研究の形: 確かめるには同じ人で 5〜6 の尺度を測る質問紙が要る。相関のメタ分析は AI 疲労の研究が足りず今は成り立たない。
  - 倫理: PLOS ONE は事前承認を求め、免除も委員会の規則で判定される [P496]。Taylor & Francis は所属の無い著者に近隣の大学の IRB への相談を勧め、所属の無い研究者を審査する IRB を置く国もあると書く [P497]。所属の無い個人が使える経路は S-AF2 では特定できなかった（判定不能 15）。
- 研究者の決定（判断 3）: 核 2 は候補として温め、倫理審査の経路を先に調べる。今すぐ設計を始めることは退けた（経路が無ければ出せない）。
- 核 2 は C（AI 疲労 DB の測定論の論文）の範囲の外（判断 6）。

## 2. このタスクのゴール（案・grill で確定する）

核 2 を確かめる研究が、所属の無い個人の研究者として実行・投稿できるかを、倫理審査の経路・尺度の使用許諾・投稿先の規程・調査の場の要件の 4 つで一次に当てて表にする。あわせて核 2 の主張を、検定できる仮説の形に磨く。研究にするか・集めるかは研究者が決める。

## 3. grill で確かめたい問い（Claude の案）

1. 倫理審査の経路の候補をどこまで調べるか: 日本の第三者の倫理審査委員会で個人が申請できるもの／米国の商用 IRB の社会調査の免除・非該当の判定の料金／英国 SRA などの有料の倫理の意見／所属のある共同研究者を立てる形（大学の IRB に乗る）。照合の論文（`.steering/20261012-public-keystroke-matching-judgement/`）・BRM（ADR-039）と同じ論点なので、結果を共通に使えるようにするか。
2. 投稿先の候補と、誌ごとの規程の本文を当てる範囲（*Computers in Human Behavior Reports*・*Collabra: Psychology*・*Behaviour & Information Technology*・*Meta-Psychology*・*Royal Society Open Science*・*PLOS ONE*・*Assessment*・*European Journal of Psychological Assessment*）。登録型報告は承認がデータ収集の前か段階 1 の投稿の前か。
3. 調査の場: Prolific の Researcher Terms（所属の要件・倫理承認の提出）。他の場（CloudResearch・国内のパネル）を入れるか。
4. 核 2 の仮説の形: 共通因子（bifactor の一般因子が大半）か、相関はあるが別の因子か。比べる尺度の組（AI 疲労 [P362]・画面疲労 Ocak et al. 2023・SNS 疲労・ZEF [P437]・一般の疲労 FAS / MFI / Chalder・燃え尽き・神経症傾向と否定的感情）。核 1 の残り（得点の動機の成分）をこの質問紙に入れるか（MFI reduced motivation などを並べる）。
5. 尺度の使用許諾: 各尺度の使用条件と、日本語版が要るなら翻訳の手続き（無検証で改変しない）。
6. 公開データの再探索: AI ではないデジタル疲労どうし（ZEF・SNS 疲労・画面疲労・燃え尽き）の弁別なら、項目単位の公開データがあるか（OSF・PsychArchives）。あれば倫理審査なしで核 2 の半分を確かめられる。
7. Lau et al. の著者への依頼（研究 3 の相関の表かデータ）: 核 1 の側と合わせて、後で決める（前のタスクの決定）。

## 4. 進め方（案）

1. grill で §3 を確定する。
2. 調べる（サブエージェントは Sonnet・並列・入れ子禁止・締切を書く。規程・料金・使用条件の逐語はメインが一次で開く）。
3. 表にまとめる: 経路ごとに「申請できるか・費用・期間・どの誌が受け入れるか」、尺度ごとに「使用条件・日本語版」、場ごとに「所属の要件」。
4. 核 2 の仮説と分析の案（bifactor・ESEM・HTMT・測定不変性・標本の大きさ）を、事前登録の前の素案として書く（凍結しない。凍結の前に `attack-me`）。
5. 研究にするか・集めるかを研究者が決める。決定は `decisions.md` に。

## 5. 守ること

- 人のデータを集めない（このタスクは実現性の確認まで）。質問紙を配らない。外部（倫理審査の窓口・著者・調査の場）に連絡しない。連絡が要るなら文面の下書きまでにして、送るかはユーザーが決める。
- AI 疲労を GSE が検出・診断する、とは書かない。GSE の O1 に質問紙を足す話にしない（ADR・`data-privacy`・同意文書の変更になる・`.idea` §10）。
- 尺度を無検証で短縮・改変しない。
- DB の研究者の判断に属することを決めない。
- 出典は `citation-ssot`（append-only）。`git add -A`・`git add <dir>` を使わない。PR は研究者が確かめてから（push だけで止める）。

## 6. 一次資料

- `.steering/20261014-ai-fatigue-motivation-claims/`（summary.md の「研究の形ごと」の表・decisions.md）
- `docs/literature/20261014-ai-fatigue-motivation-discriminant.md`（カード 3〜5・否決リスト N4・N5）
- `docs/adr/ADR-039`・`.steering/20261012-public-keystroke-matching-judgement/`（所属なしの倫理審査の先例）
- `.steering/20261001-ai-fatigue-34-screening/measurement-issues.md`（M2 共通の原因）
- PLOS ONE: `https://journals.plos.org/plosone/s/human-subjects-research`／T&F: `https://authorservices.taylorandfrancis.com/editorial-policies/research-ethics-guidelines-for-arts-humanities-and-social-sciences-journals/`
