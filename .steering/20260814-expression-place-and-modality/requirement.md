# 表現の「場所」とモダリティ — 設計議論（★ 実装タスクではない）

> ⚠️★★★ **本ディレクトリは「議論の記録」であり、実装タスクではない。**
> ★ したがって `design.md` / `tasklist.md` は**意図的に置いていない**
> （★ preflight hook が欠落を警告するが、これは**正しい状態**である）。
> ★ 根拠: 入口の引き継ぎ `.steering/_handoff/next-session-prompt-expression-place-and-modality.md` §8
> —— **「議論だけなら `/start-task` は不要。実装に入るなら先に `/start-task`。」**

## 背景

2026-08-14 に表現層の「音」を理論から問い直すサーヴェイが完了し
（`docs/literature/20260814-sound-necessity-and-target-state.md`）、
その結果を受けて**研究者が設計の方向そのものを問い直し始めた** ——
**表現の場所 / 常時性 / 音の要否 / コンピュータ外の物理オブジェクト**の 4 点。

## ゴール

★ **判断材料を一次資料まで降りて揃え、研究者が決められる形にすること。**
⚠️ **エージェントが決めることではない。**

## スコープ

### 含むもの
- 4 つの直感の検討と、一次資料による裏付け／反証（`discussion.md`）
- 第二意見（`codex-consult`）の取得と 3 分類での処理（`decisions.md` PM-D8）
- ★ サーヴェイ 1 ラウンド（`docs/literature/20260815-portable-ambient-object-and-activity-coupling.md`・[P98]–[P107]）
- ★ 具体案 A-1〜A-12 の提示（`discussion.md` §11）

### 含まないもの
- ⚠️ **実装**（★ 一切行っていない）
- ⚠️ **既決の改訂**（★ D10 / D11 / D19 / D17 いずれも変更していない）
- ⚠️ **`physical-anchor` Skill の修正** → ★ **`.steering/20260815-physical-anchor-d11-alignment/` へ切り出した**（PM-D12）

## 受け入れ条件

- [x] 4 つの直感それぞれに、一次資料に降りた回答がある
- [x] ★ **引き継ぎ文書の誤りを見つけたら訂正する**（★ PM-D1 予算 / PM-D2 D17 の理由 / PM-D9 pull の符号化）
- [x] ★ **自分の推奨が否決されたら、その事実を記録する**（★ 否決 S-2 = PM-D8 の私の推奨）
- [x] 決定していないものを「決定した」と書いていない
- [ ] ⚠️ **研究者が PM-Q1 / Q2 / Q3 / Q6 / Q7 / Q8 を判断する**（★ 未決のまま残っている）

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-expression-place-and-modality.md`（入口）
- `.steering/_handoff/next-session-prompt-post-survey.md`（★ 実装側の引き継ぎ）
- `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md`
- `docs/literature/20260814-sound-necessity-and-target-state.md` / `20260815-portable-ambient-object-and-activity-coupling.md`
- `docs/references.md` [P45] [P46] [P48] [P54] [P65] [P76] [P77] [P85] [P86] [P98]–[P107] / [V40]
