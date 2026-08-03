# architecture-consolidation — `.idea` 2 本を単一の設計へ統合し ADR-008/009 を起票する

## 背景

Phase1 較正分析（GATE2 pass / GATE3 DataInsufficient）と信号診断の結果を受けて、
`.idea/` に 2 本の設計メモが書かれた。

- **doc#1** `.idea/20260801-architecture-signal-and-online-learning.md`
  — 実測に基づく故障の同定（X 軸が偶然水準・φ のレール飽和・写像係数の個人差）と
  online 潜在学習（online EM）の検討、Codex 第二意見 8 件。
- **doc#2** `.idea/20260801-behavioral-context-online-latent-ml-design.md`
  — X 軸を `self_directed_recovery_risk` へ再定義し、行動経済学的コンテキスト収集と
  オンライン個人適応（PersonalizationStore / OnlineUpdater / ContextBuilder）を提案。

`.idea/` は gitignore・追跡外であり SSOT ではない。両者は同じ問題に別の角度から答えており、
**6 件の実質的な不一致**を持つ。そのまま merge すると「両論併記だが何も決まっていない文書」になる。

さらに前セッションの精査で、**doc#2 をそのまま SSOT へ昇格させてはいけない**ことが判明した
（引き継ぎ `.steering/_handoff/next-session-prompt-architecture-consolidation.md` §SSOT 昇格の前提）:

- (A) 4 状態（Progress / Stagnation / ExternalizationPressure / Receptivity）の定式化が 5 点で破綻
- (B) 行動経済学の接地に装飾的な引用と SSOT 同士の矛盾（§2.1-F が `[V40]` と正面衝突）
- (C) 外部引用 9 本が `docs/references.md` に 1 本も登録されていない（citation-ssot 違反）
- (D) 「PreReg を変更しない」と「X 軸を再定義する」の緊張（H-X1 の対象が変わる）
- (E) doc#2 の最大の長所（行動から自己ラベル付けできる軸）が本人に過小評価されている。
  ただし `progress_proxy` の operational definition が未確定

## ゴール

`.idea` 2 本を、既存の v2 アーキテクチャ SSOT に接地させた **単一の設計文書 + ADR 2 本**へ統合する。
「統合」の本体は 2 本の間の不一致を**裁定すること**であり、両論併記ではない。

**コード変更ゼロ**（Epic 1 と同じ形）。凍結対象には触れない。

## スコープ

### 含むもの
- 統合設計文書 `docs/architecture/personalization-and-online-learning.md`（Proposed）
- `docs/adr/ADR-008-online-learning-boundary.md`（オンライン学習の境界・Proposed）
- `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md`（X 軸再定義と潜在状態・Proposed）
- 未裁定 5 件（#2〜#6）の裁定
- 昇格の前提条件 8 項目 (A)〜(E) の処理
- 外部 9 本の `[Pn]`/`[Vn]` 採番と `docs/references.md` への append-only 登録
- 落合フォーマットの文献カード 1 枚（本ラウンド分）と `docs/literature/_index.md` 追記
- `docs/glossary.md` への新規用語追加
- `gse-v2-overview.md` / `domain-adapter-boundary.md` へのリンク行追加（本文は変更しない）
- `.idea` 2 本への「→ 昇格済み」ヘッダ追記

### 含まないもの
- 統制タスク実験（doc#1 §7.3 優先1）の**実施**。設計文書に反証ゲートとして書くところまで
- `probe_scheduler.rs` のラベル計器の**実装**（凍結対象）
- Epic 2 以降の実装着手・コード変更
- ADR-006 の再検討（Accepted・下位決定 #2/#3 も確定済み）。**拡張の要否**だけ #5 で判断する
- `preregistration-v0.3.md` の改訂（凍結）。PreReg-5 衝突は「次バージョンで何を変えるべきか」のメモまで
- `research-positioning.md §5` への新仮説追記（研究者確認必須節・提案に留める）

## 受け入れ条件

- [x] 未裁定 5 件（#2 online EM / #3 ラベル計器 / #4 PreReg-5 / #5 ADR-006 / #6 潜在状態）が全て裁定され、
      「未裁定」のまま残っていない（Deferred とする場合はその旨と再訪条件を明記）
- [x] (A) 4 状態が定式化し直され、相互排他性 / 放出モデル / `WorkStateEstimate` への写像 /
      状態数の根拠 / 退化検出の 5 点すべてに答えている
- [x] (B-1) §2.1-F が `[V40]` と突き合わせて採否を決め直されている
- [x] (B-2)(B-3)(B-4) 装飾的な引用・無引用主張・KTO の誤用が是正されている
- [x] (C) 外部 9 本が `docs/references.md` に append-only で登録され、本文に inline `[n]` がある
- [x] (D) H-X1 と新軸の関係が明示されている
- [x] (E) `progress_proxy` の operational definition が閉じている
- [x] `.idea` の ICC 4 値（0.060/0.055/0.159/0.156）を**根拠として引いていない**。
      新規文書では「概ね 0.05–0.30・5 名で不確実性大」と書き、4 値は**「η² であって ICC ではない」という
      訂正の文脈でのみ**言及する（正しい ICC(1) は 0.080/0.073/0.204/0.200・LOO 範囲 0.050–0.302）
- [x] 凍結対象のファイルに 1 バイトも変更が無い
- [x] コード変更ゼロ（`src-tauri/` `src/` に変更が無い）

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-architecture-consolidation.md` — 本タスクの引き継ぎ（入力）
- `docs/architecture/gse-v2-overview.md` — アーキテクチャ SSOT（統合先）
- `docs/architecture/domain-adapter-boundary.md` — Layer 0-3 詳細
- `docs/architecture/intervention-decision-engine.md` — Layer 5-7 詳細
- `docs/adr/README.md` + ADR-001〜007
- `docs/research-positioning.md` §5 / §8
- `docs/preregistration-v0.3.md` PreReg-5（凍結・参照のみ）
- `experiments/20260801-signal-diagnostics/notes.md` §2-C — ICC 訂正の一次根拠

## 運用メモ

- /reimagine 適用: **Yes**（#6 潜在状態の定義。アーキテクチャ判断で複数案がある）
- 理由: 引き継ぎ §進め方-2 が明示的に要求。初回案（3 モード代案）を破棄して再生成した結果、
  **状態数を手で決めること自体が §SSOT-(A)-5 の轍を繰り返す**という欠陥を発見した。詳細は `decisions.md` 判断 1。
- `codex-consult` / `/cross-review`: **予算超過のため skip**（`.codex/budget.json` 2026-08-01 時点
  363,718 / 200,000）。Claude 単独へ縮退。
