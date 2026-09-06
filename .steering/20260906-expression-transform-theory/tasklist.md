# タスクリスト

## 準備
- [x] `.idea/20260905-data-to-social-media-expression-theory.md` を読む
- [x] `docs/architecture/expression-channel.md` 全文（§0〜§8）を読む
- [x] `docs/research-positioning.md` §4（差分 = 研究の所在）を読む
- [x] `docs/adr/README.md` / ADR-017 / 018 / 020 / 021 / 022 の該当決定を確認
- [x] `.idea` 過去 4 本（20260806 / 20260810 / 20260819 / 20260901）を subagent で棚卸し
- [x] `src-tauri/src/` を実測（`WorkStateEstimate` / `uncertainty` / `evidence_quality` / `record_dismiss` / replay のモード群）

## 記録（本タスクの本体）
- [x] `requirement.md` — 背景・ゴール・スコープ・受け入れ条件
- [x] `design.md` — アプローチ・変更対象・影響範囲・サーヴェイ対応表
- [x] `decisions.md` — 判断 (a)〜(h) ＋ 切り分けの要点先出し
- [x] `tasklist.md` — 本ファイル

## SSOT 訂正（★ スコープはここまで）
- [ ] `docs/architecture/expression-channel.md` §2.1 の事実誤りを訂正する
      （⚠️ **ADR-021 D9 が現時点で実行不能**であることを明記。★ D9 の結論自体は変えない）
- [ ] §7.5 の **A10** に「現時点では検査できない」旨の前方参照を置く

## サーヴェイ（★ 別コミット）
- [x] RQ0（形式的な写像理論の先行）第 1 報を受け取り、`decisions.md` §RQ0 に反映
      （★ **「あり」** → 判断 (h) を置き直し。⚠️ **subagent の「ゼロ確定」は採らず `PLAUSIBLE BUT UNPROVEN` へ降格**）
- [x] RQ0 **追検証**の結果を受け取り `decisions.md` §RQ0-追検証 に反映
      （★ AVD の 3 原理は**忠実性型**で GSE の許容条件を含まない → **直交は生存**。
       ⚠️★★★ ただし**許容条件の内容は [P45] / [P75] / Barrass & Vickers からの輸入で、発明ではない**。
       ⚠️ ゼロ主張は `確定` → **`判定不能`** へ格下げ。空白の実体は **3 モダリティ統合 ＋ 潜在推定状態**の 2 条件のみ）
- [x] RQ2 / E-8 → `decisions.md` §RQ2 に反映（★ **核心のゼロは支持**。⚠️ 文言は過大で訂正候補。
      ⚠️★★★ **Robertson 2008 が「動的は静的より悪い」を反証として出した** → `.idea` §2 の前提が不利側に立つ。
      ★ 手続きの型は**借りられる**ので**発明は貢献にならない**。★ 既存ハーネスは既に Robertson / Harrison 型）
- [x] RQ3 → `decisions.md` §RQ3 に反映（★ **(e) 維持**。★ ゼロは**分野自身が 2 回独立に自認**＝ RQ0 より質が高い。
      ⚠️★★★ **代償が 2 本に増えた** —— 計器の自作 ＋ **「観客が存在する場」の設営**（G1 / O1 は展示でない））
- [x] RQ4 → `decisions.md` §RQ4 に反映（★ **(b) を層で割って確定**。
      ⚠️★★★ **層 A = C へ縮退**（最有力候補 HOPs は **ADR-022 D1 の持続アニメーション禁止**・Robertson 2008・
      2 秒制約の 3 本で使えない ＋ **そもそも `evidence_quality` が未実装**）。
      ★ **層 B / 展示 = B 維持**（HOPs 型の時間軸退避を自前検証。既存の混同テスト方法論を流用）。
      ⚠️ **Dries et al. 2025 が「先行信念と一致するほど不確実性開示は信頼を悪化させる」を事前登録で実測**）
- [x] RQ5 / RQ6 → `decisions.md` §RQ5-6 に反映（★ **mlf-core** が byte-equal 達成の査読実例。
      ⚠️★★★ **「seed 固定は必要条件だが十分条件でない」** → (g-1) に 3 条件を追加。
      ⚠️★★★ **横展開は中立〜やや反証寄り**（CcNav / Walker&Kramer）→ **Writing/Coding 反証テストが (h) の必須前提に昇格**）
- [ ] ⚠️ **5 本を 1 ラウンド 5 angle として 1 枚のカードにまとめる**（`docs/literature/20260906-*.md`）
- [ ] ⚠️ `docs/references.md` へ **メインが直列で append-only 登録**（`citation-ssot` 準拠・`[Pn]`/`[Vn]`）
- [ ] ⚠️ `docs/literature/_index.md` へ追記
- [ ] ⚠️ `check_citations` を **「違反なし」まで是正 → 再実行**を繰り返す（★ 1 回で全件出ない）
- [ ] ⚠️ **サーヴェイは別コミットにする**（★ 本タスクの記録と混ぜない）

## 検査
- [ ] `git diff --stat` で **`src-tauri/` と `src/` に変更が無い**ことを確認（受け入れ条件）
- [ ] (c) の訂正が主張する grep 結果を**再実行して一致を確認**する

## レビュー
- [ ] `code-reviewer` と `security-checker` を**並列**起動
- [ ] `/cross-review`（Codex 独立レビュー）—— ⚠️ **パス限定で回す**
      （`run-codex-review.sh -- <paths>`。★ 無関係な未コミット変更 25 件があるため、
      全体だと 2000 行超 / secret 名ヒットで **BLOCKED** になる）
- [ ] HIGH 指摘への対応（⚠️ **backlog へ punt しない。本タスクで消化する**）

## ★ サーヴェイ後に判断すること（本タスクのスコープ外・忘れると落ちる）
- [ ] **ADR-023 を起こすか** —— ★ RQ0 の結果次第。起こすなら (a)(b)(d)(f) ＋ A16 が候補
- [ ] **受け入れ観点 A16（媒体不変性）を `expression-channel.md` §7.5 に足す**（判断 g-2）
- [x] ~~`research-positioning.md` §4 に「観客という第三の宛先」を書くか~~ → ⚠️★★★ **判断 (i) で (e) を降格。書かない**
- [ ] ★ **中断 → 再開の観測を `experiments/` として設計する**（★ 既存 O1 データで回せる・WoZ 不要）
- [ ] ⚠️ **「慣れているか（習慣化）」を扱うかを別途決める**（★ 扱うなら ADR-020 に当たる）
- [ ] ★★★ **判断 (i) ＋ その精緻化を ADR-023 の主軸にするか** —— 測る対象を可読性 → 出口への結合へ移し、可読性を manipulation check へ降格する
- [ ] ★ `experiments/20260902-expression-layerA-visual/` の `notes.md` に**位置づけの変更**を書く（★ 設計は不変・「合否」→「操作チェック」）
- [ ] ⚠️★★★ **SSOT 訂正候補 2 件**（★ 本タスクのスコープ外・**一次確認してから**直す）:
      (i) §8 **PS-Q5**「3 段の分類学は文献上存在しない」→ **Holmquist 2004 が自己一般化している**（⚠️ 一次未確認）
      (ii) §8 **E-8**「文献に存在しない」→ 正確には**「手続きの型はある。GSE の対象への適用例がゼロ」**
- [ ] ⚠️ **判断 (g-1) に 3 条件を追記**（PRNG 品質 / 並列・GPU 非決定性 / モデル記述の完全性）
- [x] ~~判断 (b) を C へ縮退させるか~~ → ★ **層 A のみ C へ縮退で確定**（§RQ4-5）
- [ ] **Writing / Coding 間の一般化テスト**を `experiments/` として設計するか（判断 h・★ 新規データ収集ゼロで回せる）

## 完了処理
- [ ] `design.md` の最終化
- [x] `decisions.md` の作成
- [ ] `/finish-task` で git commit（⚠️ **記録と SSOT 訂正で 1 コミット、サーヴェイで別コミット**）
