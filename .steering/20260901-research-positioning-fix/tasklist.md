# タスクリスト

## 準備
- [x] 引き継ぎメモ `.steering/_handoff/next-session-research-positioning-fix.md` を読む
- [x] 一次証拠 `.steering/20260830-mitou-2027-proposal-slimming/survey-notes.md`（331 行）を読む
- [x] 必須 Skill を読む（`citation-ssot` / `literature-card` / `verify-before-claiming`）
- [x] `docs/adr/ADR-018` / `docs/glossary.md` / `docs/references.md` 採番方式を実測
- [x] 機械検算のベースラインを取る（`check_citations.py` = 違反なし / P1..P191 / V1..V88）
- [x] `.steering/20260901-research-positioning-fix/` を作成
- [x] 研究者裁定 3 件を `decisions.md` に記録

## 一次資料の取得（サブエージェント並列・★ メインで抱えない）
- [x] de Jong et al. (2020) PLOS ONE 全文（OA）— カードの素材 + 逐語 2 本の実在確認
- [x] Bell et al. (2025) J. Environ. Psychol. 104:102632 — ★ 「約 30 分が最適」の一次確認
      （⚠️ 取れなければ **provisional 登録 + 本文で断定しない**）
- [x] DOI 未確定 12 件の書誌確定（★ 確認できなければ `provisional`・捏造禁止）

## 実装（★ この順で。逆順だと未登録参照で check_citations.py が赤になる）
- [x] `docs/references.md` に `[P192]` から append（約 24 件・**メインが直列で**）
- [x] `docs/references.md` の `[P8]` / `[P10]` 接地列を訂正（★ 番号・key・状態は変えない）
- [x] 是正 (1): ART を「Physical Anchor の理論基盤」から外す（L209 ほか）
- [x] 是正 (2): [P8] の誤用を 6 → 1 箇所へ（L111 / L211 / L657 / L667 / L749）
- [x] 是正 (3): Wall を現行機能から外す（L228 / L597 / L602 / L667）— ★ 実体名へ
- [x] 是正 (4): [P166] の読みを取り下げ、L457 の未解決矛盾を用量で説明（★ Bell 取得が前提）
- [x] 是正 (5): 完了条件を ADR-018 D1・D2 に追随（L752 / L1119）
- [x] ★ **宣言外の付随修正**: 指標名 `external_paste_after_stuck` → `paste_after_stuck_rate` を 3 箇所
      （★ 実装に存在しない名前。実体は `src-tauri/src/analysis/metrics.rs:215`。→ `decisions.md` 判断 4）
- [x] `docs/literature/20260901-typing-dynamics-mental-fatigue.md` を作成（落合 6 項目）
- [x] `docs/literature/_index.md` に追記（★ 件数の手書きがあれば実測値に合わせる）

## テスト（★ 予測しない。走らせる）
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` → **違反なし**
- [x] `git status --porcelain src-tauri src` → **空**
- [x] `grep -nE 'Lv2 *Wall' docs/research-positioning.md` → 現行機能としての記述ゼロ
- [x] `grep -n '完了条件' docs/research-positioning.md` → glossary の禁止用語に一致
- [x] 追加 `[Pn]` が `[P192]` から欠番なしで連続

## レビュー
- [x] `code-reviewer` + `security-checker` を **並列**起動
- [ ] ★ `/cross-review` を **パス限定**で実行。⚠️★★★ **起動形は次の 1 行**（2026-09-01 に実測で是正）:
      `bash scripts/run-codex-review.sh HEAD -- docs/references.md docs/research-positioning.md docs/glossary.md docs/literature/ .steering/20260901-research-positioning-fix/`
      > ⚠️ **旧文の `-- <paths>` だけの形は空振りする** —— `run-codex-review.sh:86` は `git diff "$@"`（＝**未ステージ**）を見るため、
      > 全件ステージ済みの状態では **0 行**になり `:91` の `FAILED: 指定した差分が空です` で落ちる（実測）。
      > ⚠️ **`--cached` は付けられない** —— `:55-59` が `-` 始まりの引数を一律拒否する。
      > ★ **`HEAD` は `-` 始まりでないのでガードを通り、`git diff HEAD` が 1160 行を出す**（実測）。
      > ⚠️ **旧文のパス列は `docs/glossary.md` と `.steering/` を欠いており、945 行中 406 行（43%）が無レビューで通っていた。**
      ⚠️ 安全ゲートで BLOCKED なら **skip 理由を完了報告に明記**する
- [x] HIGH 指摘への対応
      - CRITICAL/HIGH は 0 件。
      - MEDIUM 6 件を確認し、`docs/research-positioning.md` の
        Vision 語彙 / H-PA 引用接地 / 身体状態推定 / 完了率 / 早期解除を是正済み。
      - `/cross-review` は sandbox 内のネットワーク制限で失敗し、権限付き再実行は
        外部サービスへの diff 送信の明示承認不足で auto review に拒否。ユーザー承認待ち。

## ドキュメント
- [x] `docs/glossary.md` への用語追加（★ 「関与の再開」を入れるか判断）
- [x] ⚠️ 凍結文書 `preregistration-v0.3.md` とのずれを発見したら `blockers.md` に記録（★ 直さない）

## 完了処理
- [ ] `design.md` の最終化
- [x] `decisions.md` の作成
- [ ] git commit（`docs(positioning): ...` / `Refs: .steering/20260901-research-positioning-fix/`）
- [ ] `/finish-task`
