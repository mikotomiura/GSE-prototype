# gse-target-reframe —— 対象の捉え直しと招待の望ましさの扱い（D）

## 背景

2026-11-03 の設計の整理（`.steering/20261103-gse-design-consolidation/`・PR #381 で main 済み）の後、研究者は「詰まりではなく、PC 上の行動として停滞・デスク疲労に近いものを対象にし、招待をユーザー検証で望ましいかを見て直していく」案を出した。引き継ぎ `.steering/_handoff/next-session-gse-target-reframe-and-mhd-rethink.md` §3（consolidation の worktree にある）。

この結論は段 1 の同意文書（地図 R4）と問いの中身を変えうるので、同意文書を書く前に決める。

## ゴール

D-1（主の対象）・D-2（疲労に近い量）・D-3（招待の望ましさ）を研究者が 1 問ずつ決め、decisions.md に記録する。ADR が要るか（ADR-043 の読み替えになるか）を判断し、要るなら起票する。後続の A・B・C の出発点を引き継ぎに書き直す。

## スコープ

### 含むもの
- D-1〜D-3 の決定と記録
- 要る場合の ADR の起票と `docs/adr/README.md`・設計の地図の該当行の更新

### 含まないもの
- コードの変更
- A（MhD の再考の ADR 案）・B（CoAuthor の個人ごとの学習の試験）・C（詰まりの割合の幅）。別タスク
- research-positioning §1・WBS の改訂（ADR-041 Migration 4 の別タスク）
- O1 の 11-01 08:30 以降の記録・holdout.json を開くこと

## 受け入れ条件

- [ ] D-1〜D-3 が研究者の選択として decisions.md にある
- [ ] ADR の要否の判断と、要る場合の ADR が一次資料（ADR-031・033・041・043）と食い違わない
- [ ] A・B・C への引き継ぎが D の結論を反映している

## 関連ドキュメント

- ADR-031 D8・ADR-033 D3/D5・ADR-041 D3/D4・ADR-043・ADR-044
- `docs/architecture/gse-design-map.md`
- `.steering/20261102-gse-synthesis-redesign/synthesis.md` §5（H1〜H5）

## 運用メモ
- /reimagine 適用: No
- 理由: 文書の判断で、選択肢は研究者に 1 問ずつ聞いて比べる。コードの設計判断を伴わない
