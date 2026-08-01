# タスクリスト

## 準備
- [x] 引き継ぎ `.steering/_handoff/next-session-prompt-architecture-consolidation.md` を読む
- [x] `docs/architecture/gse-v2-overview.md`（SSOT）
- [x] `docs/architecture/domain-adapter-boundary.md` / `intervention-decision-engine.md`
- [x] `docs/adr/README.md` + ADR-001〜007（ADR-006 含め全 7 本）
- [x] `docs/research-positioning.md` §5 / §8
- [x] `docs/preregistration-v0.3.md` PreReg-5（凍結・参照のみ）
- [x] `docs/references.md`（採番方式・末尾番号の確認 → P28 / V53 が末尾）
- [x] Skill: `citation-ssot` / `git-workflow` / `literature-card`
- [x] `.idea` doc#1 / doc#2 の再読

## 裁定
- [x] `/reimagine`: #6 潜在状態（初回案を破棄 → 再生成 → 比較）→ `decisions.md` 判断 1
- [x] ユーザー裁定 4 点（#6 / B-1 / ステータス / (D)）
- [x] #2 online EM の降格理由の明文化 → 判断 2
- [x] #3 ラベル計器（別チャネルとして両立）→ 判断 3
- [x] #4 PreReg-5（情報の出所で切る）→ 判断 4
- [x] #5 ADR-006 は拡張せず新 ADR が参照 → 判断 5
- [x] (E) `progress_proxy` の operational definition → 判断 8
- [x] ICC 訂正の反映方針 → 判断 11

## 引用（citation-ssot）
- [x] 外部 9 本の書誌を一次ページで確認（捏造しない）
- [x] `[P29]`–`[P32]` / `[V54]`–`[V58]` を `references.md` に append-only 登録
- [x] 未確認の巻号・頁を除去（[P32] 号数 / [V58] Suppl 表記の是正、[P31] に訂正論文を注記）
- [x] `[V55]`（DOI 無し）/ `[V56]`（preprint）を provisional に
- [x] 一意件数を 66 → 84 へ更新
- [x] 落合フォーマット文献カード 9 枚 + `_index.md` 追記

## 執筆
- [x] `docs/architecture/personalization-and-online-learning.md`（統合設計文書・Proposed）
- [x] `docs/adr/ADR-008-online-learning-boundary.md`（Proposed）
- [x] `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md`（Proposed）
- [x] `docs/adr/README.md` 一覧へ追加

## 周辺 SSOT の整合
- [x] `docs/glossary.md` に 6 用語追加（Receptivity の層の明示を含む）
- [x] `gse-v2-overview.md` §関連文書にリンク行（本文は不変）
- [x] `domain-adapter-boundary.md` に additive 拡張候補のポインタ
- [x] `intervention-decision-engine.md` に「Receptivity は Layer 5」の明示
- [x] `.idea` 2 本に「→ 昇格済み」ヘッダと是正点

## 検証（コードが無いため不変条件チェックで代替）
- [x] `src-tauri/` `src/` に変更が無い（コード変更ゼロ）
- [x] 凍結対象（schema / engine / intervention 定数 / probe_scheduler / App.tsx / prereg）に変更が無い
- [x] `docs/research-positioning.md` の差分は**既存の未コミット作業**であり本タスク由来でない（確認済み）
- [x] ADR-001〜007 に変更が無い
- [x] 本文の全 `[Pn]`/`[Vn]` が `references.md` に実在（15 種・欠落ゼロ）
- [x] 新規 9 本すべてに使用箇所がある（citation-ssot ルール 6）
- [x] `references.md` の番号が末尾連番（P1–32 / V1–58・renumber なし）
- [x] `.idea` の ICC 4 値を**訂正の文脈以外で**引いていない
- [x] 「KTO 的」を**撤回の文脈以外で**使っていない

## レビュー
- [x] 自己レビュー（受け入れ条件 11 項目との突合）
- [ ] ~~`code-reviewer` サブエージェント~~ — **本セッションではサブエージェント委譲を行わない設定のため skip**
- [ ] ~~`/cross-review`（Codex 独立レビュー）~~ — **`.codex/budget.json` 日次予算超過（363,718/200,000）で skip**。
      `CLAUDE.md` の縮退条件（予算超過）に該当。完了報告に skip 理由を明記済み

## 完了処理
- [x] `requirement.md` / `design.md` / `decisions.md` の最終化
- [ ] git commit（パス指定で add。**`git add -A` / `git commit -a` を使わない**
      — ユーザーの Loop Engineering 導入作業が未コミットで並行しているため）
