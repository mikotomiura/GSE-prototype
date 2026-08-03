# タスクリスト

## 準備
- [x] 凍結文書一式を読む（`preregistration.md` / `README.md` / `config.json` / `notes.md` / `SEED` / `env.md` / `data.md`）
- [x] `.steering/20260802-g1-preregistration/decisions.md`（判断 1〜9）を読む
- [x] 既存の NDJSON 集計実装（`20260802-within-person-scope-detector/analyze.py`）を読む
- [x] NDJSON の実スキーマを一次確認（`logger.rs` / `anonymize.rs` / `~/gse-dataset` 実データ）
- [x] `ime_shadow` の OS ゲートを一次確認（`lib.rs` `#[cfg(target_os = "windows")]`）

## T-A 事前登録の改訂（判定基準は変えない）
- [x] §2.1 書換 — 論述は「代表例」ではなく**ベストケース**（`✗` の射程が全ドメインに及ぶ理由）
- [x] §2.4 訂正 — n はパイロット後に凍結（★ 追記ではなく**訂正**と明記）
- [x] §2.7 新設 — 題材↔条件の被験者間 counterbalance
- [x] §2.8 新設 — パイロット条項（研究者本人 1 名・確証標本に入れない）
- [x] §2.9 新設 — ブロック水準の最小打鍵（**適格性ゲート**・除外ではなく解析対象から外す）
- [x] §3.3 — 補助基準の分母を**割合**で固定（4/5 → ≥80%）
- [x] §3.7 拡張 — 結論の非対称性と `✗` の場合の具体的分岐（Adapter B へ資源を移す）
- [x] §3.8 新設 — 生態学的妥当性の限界（**測定可能性の下限チェック**である）
- [x] §3.9 新設 — n=1 は全数列挙で厳密検定・Fisher は n≥2 のみ
- [x] §5 訂正 — Tier 0/1 はオフラインで計算でき凍結解除を待たない
- [x] `config.json` を同期

## T-B 実施プロトコル
- [x] `protocol.md` — ブロックの切り方 (a) を理由つきで確定
- [x] ラベル対応表の様式と取り違え防止（ログからの検算手順）
- [x] 操作チェック用紙の実物（強制比較・リッカート不使用）
- [x] 進行台本（読み上げ文・タイマー・休憩）
- [x] 課題文を研究者本人が読まずに使う手順

## T-C 課題文
- [x] `materials/copy.md`（positive control 用の中立・退屈な定型文）
- [x] `materials/topic01_lo.md` / `topic01_hi.md`（パイロット用 1 題材 × 2 版）
- [x] `materials/README.md`（様式・命名・作成規約）
- [x] `validate_materials.py`（資料本数・総文字数一致・産出要求の機械検証）

## T-D / T-E 解析
- [x] `analyze.py` — ブロック単位 FS-A（`feat` 中央値）
- [x] `analyze.py` — Tier 0/1（`keys` / `bs_rate` / `external_paste_chars` / `ime_dwell_med` /
      `silence_*` / `burst_*`）を匿名化 NDJSON から計算
- [x] L2 罰則ロジスティック（λ=1.0 固定・Newton 法・標準ライブラリのみ）
- [x] 被験者内 leave-one-block-pair-out / out-of-fold AUC
- [x] 並べ替え **全数列挙**（G1: C(8,4)=70 / positive control: C(10,2)=45）
- [x] Fisher 統合（n≥2 のみ）
- [x] 完全分離の診断値・産出量交絡の報告・`keys` 単独 AUC
- [x] `assign.py`（SEED からの割付表生成）
- [x] `run.sh` を実施前チェックに置換

## T-F 倫理・同意
- [x] `consent.md`（copy ブロックの存在を事前開示・欺瞞なし）

## テスト
- [x] `analyze.py --selftest` が緑
- [x] `assign.py --selftest` が緑
- [x] `validate_materials.py` が緑
- [x] `run.sh` が緑（資材が揃っている状態）／欠けると赤
- [x] `src-tauri/` `src/` に変更が 0 行

## レビュー
- [~] code-reviewer / security-checker（★ 本セッションは subagent 起動が運用指示で禁止。手動レビューで代替）
- [ ] `/cross-review`（Codex 独立レビュー）★ **未実施**。次セッションで掛ける
- [x] 手動レビューでの指摘に対応（空 blocks の例外・in-sample 係数の明示・母標準偏差の固定・verify-blocks の整形と常時 exit 0）

## 完了処理
- [x] `decisions.md` の作成
- [x] `env.md` / `data.md` の訂正
- [x] git commit
- [x] 研究者判断が要る残件を引き継ぎに記録
