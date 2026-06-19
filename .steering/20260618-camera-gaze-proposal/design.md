# Design

Date: 2026-06-18

## 方針

既存の `.idea/need-opportunity-improvement-plan.md` は上書きせず、カメラ視線に絞った独立案として `.idea/camera-gaze-need-opportunity-proposal.md` を追加する。
内容は「実装する前の設計判断メモ」とし、研究プローブとしての価値、プロダクト投入の条件、GSE アーキテクチャへの接続点を分けて記述する。

## 現行設計との整合性

- Need は引き続き HMM の `p_stuck` を主軸にする。カメラ視線は `p_stuck` を置き換えず、初期段階では shadow score / suppression signal として扱う。
- Opportunity は「介入してよいタイミング」の判定であり、視線情報を介入発火の強化には使わず、主に抑制・延期に使う。
- OS / カメラ API と推論ランタイムは `input/` または将来の `sensors/` に閉じ、`analysis/` は固定カテゴリを受け取る純粋計算に保つ。
- logger は raw frame、顔画像、gaze 座標、pupil、face embedding を保存しない。将来 schema を増やす場合も固定 enum / bucket のみ。
- frontend は opt-in / status / kill switch の UI に限定し、Need / Opportunity 閾値判定を持たせない。

## 成果物構成

- `.idea/camera-gaze-need-opportunity-proposal.md`: 本体。採否判断、設計案、評価計画、参考文献を含む。
- `.steering/20260618-camera-gaze-proposal/`: 本作業の記録。

## 検証

ドキュメント追加のみのため、cargo / npm のテストは実行しない。
作成後にファイル存在、主要見出し、git diff を確認する。
