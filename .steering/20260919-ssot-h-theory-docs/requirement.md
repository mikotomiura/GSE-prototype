# 単位 h: 理論本体を docs/theory/ へ移して改訂する

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **h**。

## 背景

- 理論本体（理論体系とロードマップ・生成的返権論・計測終端型実践肖像論）は `.idea/`（gitignore の対象・版管理なし）にあり、改訂を `/cross-review` に通せなかった。
- 段 3 判断 1 #4（研究者）: **`docs/theory/` を新設**し、冒頭に「theory candidate（確証 L0）・SSOT の主張ではない」を明記する。
- 引き継ぎ §2 h: 返権の負荷逆説の定義に先行と差分を書く／改名を反映する／GR-H11 は境界条件として保留する（J-7）。

## ゴール

- 3 本を `docs/theory/` へ写し、リンクを直し、研究者が裁定した事項と機械的な規則だけを本文へ反映する。
- `docs/theory/README.md`・`docs/agent-shared.md`・`docs/repository-structure.md` を更新する。

## スコープ

### 含むもの
- `docs/theory/{theory-architecture-and-roadmap,generative-relinquishment-theory,measurement-terminating-practice-portraiture,README}.md`
- `docs/agent-shared.md`・`docs/repository-structure.md` のディレクトリの記述（★ ついでに古い「ADR-001〜026」「ADR-001〜018」を ADR-034 まで直した）

### 含まないもの
- ⚠️ 批判的レビューの判定（提案・未採否）を本文へ当てること
- ⚠️ 研究計画（`.idea/20260916-gse-mitou-research-plan.md`）の移設 —— 理論本体ではない
- ⚠️ 本文の著者・年の引用を `docs/references.md` へ登録すること（→ 引き継ぎ）

## 受け入れ条件

- [ ] 各文書の冒頭に位置づけ（theory candidate・EH0・SSOT ではない）と改訂の一覧がある
- [ ] 本文に当てたのが研究者の裁定と機械的な規則だけである（レビューの提案を当てていない）
- [ ] リンクが壊れていない
- [ ] `check_citations.py` 違反なし
- [ ] `/cross-review` 2 巡

## 関連ドキュメント

- `.steering/20260918-theory-critical-review/`（`review-A.md` / `review-B.md`・`decisions.md` 判断 1 / 2）
- `.steering/20260919-theory-ssot-promotion/decisions.md` 判断 1

## 運用メモ

- /reimagine 適用: **No**
- 理由: 移設と、裁定済みの事項の反映だけである
