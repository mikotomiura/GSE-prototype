# 要求: 位置づけへの加工と照合の論文の反映（A）・スライドの枝の PR（C）・照合を防ぐ形の文献ラウンド（E）

入口: `.steering/_handoff/next-session-gse-positioning-pr-and-defense-scoping.md`（2026-11-16）。

## 背景

- research-positioning §1.4 と ADR-054 の「漏れ」の材料は IME 論文 1（合成入力・候補の照合）だけで、ADR-054 D3 は「人の打鍵では確かめていない」と書く。
- 加工と照合の論文（枝 `docs/public-keystroke-matching-manuscript`・`papers/keystroke-log-release-matching/`・未公開）は、公開の人の打鍵（KLiCKe 500 人・ENJA15）で、公開の前の加工の形を照合と書く過程の 10 の指標の両方で比べた。どの形も照合を偶然に近づけつつ指標を残すことはできなかった。
- ADR-039 D6 は、人の日本語 IME の記録を出す前に照合などの関門を通ることを前提にしている。守れて使える形は未解決。

## ゴール

- A: research-positioning（§1.2・§1.4・§11 ほか）と ADR-054（日付の注）に、照合の論文の結果と限定を反映する。ADR-053 の作法（旧版を docs/history/ へ逐語で写す）に従う。`docs/agent-shared.md` の Windows の作業機の記述を直す。
- C: 枝 `docs/gse-slides-detail` の PR を、研究者に確かめてから出す。
- E（時間があれば）: 照合を防ぎつつ指標を残す公開の形の先行研究を `/literature-review` で 1 ラウンド。

## 受け入れ条件

- research-positioning の数値がすべて原稿（origin/docs/public-keystroke-matching-manuscript の sections）と一致する（一次で照合した記録が decisions.md にある）。
- 投稿先と投稿の状態を書かない。
- ADR-054 の本文（Decision 以下の既存の文）を書き換えていない（`git diff` で追記だけ）。
- 旧版の research-positioning が docs/history/ に逐語であり、`docs/history/README.md` に行がある。
- A の枝は `docs/project-outputs.md` を触らない（C の枝と衝突させない）。
- /cross-review を通す（Codex の縮退時は理由を書く）。

## スコープ外

- 照合の論文の原稿・その枝への書き込み（投稿が 2026-11-30 締切で先）。
- E の計算・新しい評価。
- push と PR は研究者に確かめてから。

## 運用メモ
- /reimagine 適用: No
- 理由: 決定は変えず、既存の決定の材料を更新する docs の改訂。案の分岐は AskUserQuestion で閉じた（decisions.md 判断 1〜3）。
