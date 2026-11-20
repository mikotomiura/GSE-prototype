# 設計

## アプローチ

/literature-review の 1 ラウンド。問いごとに angle を分けた Sonnet のサブエージェント 10 本を並列で回し（入れ子なし・各 25 分）、メインが一次で照合して 3 票を付け、カードと登録を直列で書く。共通の依頼文は scratchpad の `cx/common-brief.md`（リポジトリには入れない）。

| angle | 問い | 向き |
|---|---|---|
| 1a | 1 | 認知心理・神経科学（所有感と主体感の分離・自他の帰属・分身） |
| 1b | 1 | HCI（social presence・生き物らしさ・more-than-human） |
| 1c | 1 | 人文・メディアアート（data double・extended self・鏡の作品） |
| 1d | 1 | 反証（共存感覚を不要にする最も近い既存の概念） |
| 2a | 2 | 実験心理（遅れ・混合の比率・時定数と帰属の切り替わり） |
| 2b | 2 | HCI・HRI・作品（追従と自律の度合いと伴侶らしさ） |
| 3a | 3 | 知覚心理（時間の構造だけでの自己認識） |
| 3b | 3 | デザイン・作品（行為のリズムの表現とその評価） |
| 4a | 4 | 反証（慣れ・新奇性の減衰・煩わしさ） |
| 4b | 4 | 反証（監視・不気味さ） |

## 変更対象

- docs/literature/20261120-handmark-coexistence-concept.md（新規）
- docs/references.md（P594〜P616 を append）
- docs/literature/_index.md（1 行）

## 照合の方針

- 断定に使う逐語は、サブエージェントが保存した本文テキストをメインが検索して一致を確かめる。書誌は Crossref / OpenAlex / arXiv。
- 3 票はメインが 3 つの視点（内的妥当性 / 共存感覚への外挿 / 探索の網の粗さ）で付ける（S-EA と同じ逸脱）。
- カードに「名前の衝突の表」（候補の概念名・同じ所・違う所・判定）を置く。

## テスト戦略

- `python3 scripts/check_citations.py` が「違反なし」になるまで是正と再実行を繰り返す。
- /cross-review（Codex を含む）でカード・索引・references の diff を見る。
