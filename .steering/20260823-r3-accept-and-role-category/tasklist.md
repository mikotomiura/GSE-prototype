# タスクリスト — R3 の Accept と役割カテゴリの技術調査

> 2026-08-23 / ★ **前半は文書のみ。⚠️ 後半（判断 6 の実装）で `src-tauri/` を変更した。**

## 完了

- [x] **grill** — 研究者判断 6 件＋追加 3 件を確定（`requirement.md §研究者判断`）
- [x] **G-1 ADR-014 を Accepted にする**
  - [x] ステータス行を `Proposed` → **`Accepted`**（+ Accepted 日）
  - [x] §研究者判断 を「未確定」→ **「2026-08-23 に確定」** に差し替え（判断 1〜6 を本文化）
  - [x] Migration 1 を「G1 **判定**を待つ」→ **「G1 の *収集完了* を待つ」** に改訂（判断 4）
  - [x] Migration 7〜10 を追加（宣言 UI / 判断 6 の実装 / 役割カテゴリの扱い）
  - [x] 作業記録の参照に本タスクを追加
- [x] **ADR-013 D6 へ条件付き解除を追記**（ADR-014 §Consequences が要求していた）
  - [x] 「非打鍵モダリティの信号本体」行 —— 解除条件 3 つを明記・**R1 / R2 では解除しない**と明記
  - [x] 「毎分の `starve_window`」行 —— **R3 は定義上この連続タイムラインを作る**と明記
- [x] **`docs/adr/README.md`** の ADR-014 行を Accepted に更新（判断 5 件を要約）
- [x] **G-2 メモを `docs/architecture/workspace-behavior-observation.md` へ昇格**
  - [x] §0 位置づけ / §1 問い / §2 観測空間（段 1・記録しないもの・天井 3 分類）/ §3 既決の再記述 /
        §4 ラベル / §5 評価設計 / §6 文献の帯 / §7 `vibe_coding` 候補 / §8 空いているもの
  - [x] ⚠️ **禁止語チェック**（`効果` / `精度が上が` / `有効性` / `利得`）→ ★ **該当 1 行のみ・規約の *宣言* 箇所**
  - [x] `docs/agent-shared.md` のリンクハブへ追加（★ 併せて `ADR-001〜007` の陳腐化を `〜014` へ訂正）
  - [x] ⚠️ **`citation-ssot`**: §6 の数値 4 件は **[P118] / [P120] に登録済みだった**（★ 追加採番は不要・D-10）
- [x] **G-3 役割カテゴリの技術調査** → `role-category-feasibility.md`
  - [x] Windows: ★ **`GetClassNameW` 経路が成立・repo に出荷済みの前例あり**（前段サーヴェイの結論を訂正）
  - [x] ⚠️★★★ macOS: ~~識別子ゼロの経路は無い~~ → **D-12 で訂正**。`AXUIElementCreateSystemWide()` は
        **引数を取らない**。★ さらに **Windows/macOS の非対称そのものが幻だった**（どちらもアプリ指紋）
  - [x] `EVENT_CONSOLE_*` を一次確認 → ⚠️ **公式 Event Constants ページに 1 つも掲載が無い**（不採用）
  - [x] 3 案（R-1 / R-2 / R-3）＋ **macOS の 3 案（M-1 / M-2 / M-3）**と、閉じるための 4 条件を書いた
  - [x] ⚠️ **ADR-009 D2 の順序は 1 文字も変えていない**
- [x] **G-4 `vibe_coding` の段 2 判定量の候補**（V-1 / V-2 / V-3・分母と成立条件つき）
- [x] **G-5 判断 7 の帰結を記録**（★ `manual_contribution_ratio` の過小評価・decisions D-7）
- [x] `.idea` メモへ昇格の追記 ＋ **2026-08-21 追記の誤り 2 件を訂正**

## ✅ 完了（後半・判断 6 の実装）

- [x] ✅ **`KeyCategory` に `Punctuation` / `SentencePunctuation` / `Tab` を足した**（14 カテゴリ）
- [x] ✅ **判断 6 の実装** — VK 量子化を **logger の書き出し境界へ移した**
      （★ 464 tests 緑 / ゴールデン replay 一致 / schema parity 同期 / extract.py selftest 緑）

## ⚠️ 残（★ 研究者判断または次セッション）

- [ ] ⚠️ **gse-dataset 側の `schema/current.json` をコミットする**（★ ファイルは配置済み・parity 緑・別 repo）
- [ ] **自然作業の `task_kind` 宣言 UI の設計**（★ R3-b の前提・ADR-014 Migration 7-ii）
- [ ] **R3 の事前登録**を `experiments/<YYYYMMDD>-<name>/preregistration.md` に凍結（ADR-014 D3 / Migration 4）
- [ ] **R3 の同意文書**（D7 の 3 点セット）＋ ⚠️ **`data-privacy` Skill の拡張**（区間指定削除・非打鍵チャネル）
- [ ] **6 段階 ablation の事前宣言**（⚠️ n と検出力の算術・B-a プール倍率の実数が未了）
- [ ] **`vibe_coding` 判定量の凍結**（⚠️ Epic 4 の着手ゲートが先）
- [ ] ⚠️ **次セッション**: B 案（スマホ表現チャネル）／「計測なき身体回帰」の研究コンセプト追加

## ⚠️ 検証

- [x] 禁止語 grep（昇格文書）→ ★ 該当 1 行のみ・規約の *宣言* 箇所
- [x] `cargo test --workspace` → ★ **464 passed / 0 failed**
- [x] ゴールデン replay（Replay-as-Truth）→ ★ **15 snapshots 一致**
- [x] `emit_schema` → gse-dataset parity → ★ **in sync (27145 bytes canonical)**
- [x] `extract.py` selftest（沈黙分解実験）→ ★ **全項目 ok**
- [x] `cargo fmt --all -- --check` / clippy（変更ファイル）→ ★ **無警告**
- [ ] ⚠️ **`/cross-review` 未実施** —— ★ 実施を推奨（`logger.rs` / `anonymize.rs` の変更が入ったため）
