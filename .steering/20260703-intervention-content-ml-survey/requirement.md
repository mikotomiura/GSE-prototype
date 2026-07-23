# Requirement: 介入コンテンツ・文脈シグナル・ML裏付けの先行研究サーヴェイ

## 背景

- GSE の介入は Need×Opportunity ゲート(トリガー条件)の検証枠 (`intervention_eval.rs`) は
  整備済みだが、**介入の「中身」(Nudge に何を表示し何を言うか・Wall/Zen Timer の処方内容)** に
  理論的裏付けがない。
- Opportunity 層は keyboard idle + F3/F4/F6 のみで、文境界等の writing analytics 由来
  シグナルの併用可能性が未調査。
- Stage 2 昇格 (HMM→ロジスティック回帰、~50セッション+3%) は WBS §7 で「デッキ参考値・
  要定義」のまま文献的裏付けがない。
- 既存書誌 (P1–P18 / V1–V29) は方法論・タイミング・身体性をカバーするが、上記 3 領域が空白。

## ゴール

先行研究サーヴェイ (deep-research workflow) + 落合フォーマット精読カードで以下に答える:

- RQ1: stuck 時に有効な介入コンテンツ (メタ認知プロンプト・自己距離化・implementation
  intentions・マイクロブレイク内容・フレーミング) の実証
- RQ2: 本文非保存制約下で併用可能な文脈シグナル (pause 位置・文境界 breakpoint)
- RQ3: キーストローク→認知/感情状態推定 ML の到達点と Stage2 昇格設計の妥当性
- RQ4: designed friction / 段階的エスカレーションの実証と Lv1–Lv4 への含意

## 受け入れ条件

- [x] docs/literature/ に落合フォーマットカード (既存 3 枚と同形式) を追加
- [x] 改善提案を「すぐ実装可能 / Phase2以降 / 不採用(理由)」に振り分け
- [x] 出典 DOI/arXiv ID 付き・既存 P/V 書誌と重複しないものを明示
- [x] プライバシー制約 (本文・ウィンドウタイトル・カメラ・マイク不可) 違反の提案は不採用理由を明記
- [x] 検証状態 (adversarial verify 通過 / 未検証) をカードに明示
