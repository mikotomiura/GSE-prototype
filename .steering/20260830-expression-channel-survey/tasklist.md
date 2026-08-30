# タスクリスト

## Phase 0: 棚卸し（完了）
- [x] `.idea/20260819-smartphone-computational-media-channel.md` 全文精読
- [x] repo 側の議論到達点を実測（`docs/` に表現チャネル系の記述ゼロ・ADR なし・議論セッション未実行）
- [x] 既存サーヴェイ 20 ラウンドの棚卸しと「やり残し」抽出
- [x] 採番の現在地確認（`P132` / `V86`・`check_citations.py` 違反なし）

## Phase 1: サーヴェイ（完了・並列探索 → 直列 SSOT 登録）
- [x] R-1 スマホをアンビエント表現面にする — 探索（★ 一次全文自読 10 本 / 否決 8）
- [x] R-2 自動開始の受容と安全条件 — 探索（★ 一次全文自読 3 本 / 否決 5）
- [x] R-3 計測なき身体回帰の支柱 — 探索（★ 一次全文自読 3 本 / 否決 6）
- [x] R-4 研究コンセプトの理論骨格 — 探索（★ 一次全文自読 11 本 / 否決 3）
- [x] R-2 カード生成 → references append → `_index` 追記 → §3 還元 → **分離コミット** `5113b65`
- [x] R-1 同上 → `5100bfd`
- [x] R-3 同上 → `23b3444`
- [x] R-4 同上 → `1b35668`
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` が違反なし（★ 各ラウンド後に実施）

### ★ 登録の実績
- [x] **[P133]–[P191] / [V87]–[V88]** を append-only（★ renumber ゼロ・欠番なし）
- [x] 既存行の更新（★ 二重登録の回避）: **[P101] [P102] [P77] [P113] [P104] [P6]**
- [x] `docs/literature/_index.md` に 4 行
- [x] `docs/research-positioning.md` **§3 のみ** に 4 ブロック（⚠️ **§4 / §5 は触っていない**）

## Phase 2: 次セッションへの引き継ぎ（完了）
- [x] `.steering/_handoff/next-session-prompt-expression-channel-ssot.md` を作成
      （★ 論点 6 件 / 既決の制約 / 触ってはいけないもの / 落とし穴を埋め込んだ）
- [x] 旧引き継ぎ `next-session-prompt-smartphone-expression-channel.md` との関係を明記
      （★ 上書きするが破棄ではない。§2 の「併せて読む」表と §6 の落とし穴は有効）

## ⚠️ 本タスクでやらないこと（★ 次セッション）
- [ ] ~~ADR 新設・SSOT 昇格~~ → 次セッション
- [ ] ~~全体アーキ再構築（境界クラスの再設計）~~ → 次セッション
- [ ] ~~`research-positioning` §4 差分 / §5 仮説の改訂~~ → 次セッション（⚠️ §5 は研究者確認が要る節）
- [ ] ~~`physical-anchor` / `data-privacy` Skill の D11 整合~~ → ⚠️ **`.steering/20260815-physical-anchor-d11-alignment/` が未着手のまま。次セッション §5 で裁くか切り出す**
- [ ] ~~`docs/architecture.md` の ADR-015 追随~~ → 次セッション §5

## ⚠️ 本ラウンドが残した「やり残し」の最優先（★ 次のサーヴェイの入口）
- [ ] **[P6] の書誌確定**（★ "Proc. Design Society, 2019" に該当が見つからない。★ `provisional` に落とした）
- [ ] **[P170] 図 1 の Objective / Subjective 分類**（★ 判定不能 U-1。⚠️ GSE の headline と益カテゴリがずれる可能性）
- [ ] **[P144] 装着検出の F1**（★ MDPI 403。⚠️ これが取れるかで音声自動開始の可否が単独で決まる）
- [ ] **[P168] Kulik & Kulik 1988 の一次**（★ 応用場面では即時優位＝ GSE に不利。取れるまで不利な材料としても使わない）
- [ ] **RQ-1a(ii) の空白を別 angle で検算**（★ 「推定された内的状態を常在面に非断定的に写す」実証はゼロ）
