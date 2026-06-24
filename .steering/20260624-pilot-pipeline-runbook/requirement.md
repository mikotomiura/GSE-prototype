# M1 パイロット パイプライン結線 + Y 運用 runbook (Phase C→F bridge)

## 背景

Phase A/B/C の**コードは全完了** (#18/#20 捕捉 / #19 (a)(b) 指標 / #27 anonymize+age /
#29 replay D6 / **#6 DuckDB join = PR #30**)。logger の参加者 ID 設定可能化も実装済。
残るのは **個々の部品を end-to-end に結線し、M1 パイロット (n=3-5) を実際に回せる運用
パイプライン化**。これが Phase F (通しパイロット) の直前ステップ。実データ不要で合成
session により先行構築・検証できる。

親: `roadmap-xy.md` Phase C/F / `decisions.md` D5(分析DB)・D6(匿名化→age→Dropbox) /
#6 DuckDB join (PR #30) / transfer-pipeline `decisions.md` D1-D7。

### 結線されていない GAP (本タスクの主眼)
1. **研究者側 decrypt 経路が無い**: 受領した `.age` → 匿名化 NDJSON にする手順/ツールが未整備
   (`gse-package` は暗号化のみ)。これが無いと sync-session に渡せない。
2. **`sessions.csv` (phase manifest) を作る手段が無い**: `build_analysis_db.py` は pre/post 割当に
   `sessions.csv` を要求するが、生成テンプレート/ヘルパが無い (P-ID×session×os×phase)。
3. **survey CSV の配置規約が運用に無い**: `survey/*.csv` をどこに置き誰がいつ入れるかが未文書。
4. **通し runbook が無い**: 被験者 step (gse-package→Dropbox) + 研究者 (decrypt→sync-session→
   survey 配置→sessions.csv→build_analysis_db) を 1 本に束ねた Y パイロット運用手順書が未作成。
5. **end-to-end 統合検証が無い**: 合成 session を package→decrypt→replay metrics→build_analysis_db に
   通すスモークが無く、結線が壊れても気づけない。

## ゴール

合成 session を `gse-package` → decrypt → `gse-replay --metrics` → `build_analysis_db.py` に
end-to-end で通し、`cross_section` を生成できる。研究者が runbook 通りに被験者データを受領→
匿名化 NDJSON→metrics→survey→sessions.csv→analysis.db まで迷わず辿れる。

## スコープ

### 含むもの
- 研究者側 **decrypt 手段** (`.age`→匿名化 NDJSON)。鍵は repo 非格納。
- **`sessions.csv` 生成ヘルパ** (gse-dataset の metrics/ を走査し P-ID×session×os 行を吐き、
  phase 列は研究者が pre/post 記入)。`build_analysis_db.py` とキー整合。
- **survey CSV 配置規約**の明文化 + テンプレート。**散歩受容 (D8)**: post survey に WoZ
  自己申告列 (歩いたか/作業に戻れたか/不便益として受容できたか) を最小スキーマに含める。
- **Y パイロット運用 runbook** (`docs/pilot-runbook.md`): 被験者手順 + 研究者手順を end-to-end。
  Dropbox File Request 手順 (D6)。**散歩は WoZ (D8)**: 計測コードは作らず post survey で受容性を拾う。
- **end-to-end 統合スモーク**: 合成 session を全段に通し `cross_section` が出るまで検証 (実データ不要)。

### 含まないもの
- PreReg 凍結の中身・実 Google Form 作成 (= ユーザー操作。schema は最小プレースホルダ追従)。
- **Physical Anchor (Lv3/Lv4 計測) の実装**: Phase 1 は散歩 = WoZ + 自己申告で受容性のみ (D8 決定済)。
- 統計解析・効果量推定 (Phase F 本体) / 可視化ダッシュボード。
- HMM/features/engine ロジック変更・anonymize/replay/gse-package の機能変更 (完了済)。

## 受け入れ条件

- [ ] 合成 session が package→decrypt→metrics→join の全段を通り `cross_section` を生成できる。
- [ ] 研究者が runbook 通りに被験者データを受領→匿名化 NDJSON→metrics→survey→sessions.csv→
      analysis.db まで迷わず辿れる (被験者向け Dropbox 3 step も記載)。
- [ ] 復号後の平文・生 NDJSON・age 秘密鍵が repo / 出力 (DB/CSV) / commit に混入しない (data-privacy)。
- [ ] 既存 `cargo test --workspace` / `gse-replay --snapshot` / `emit_schema` parity が不変。
- [ ] CRITICAL/HIGH なし (code-reviewer + security-checker + /cross-review)。

## 関連ドキュメント
- `docs/calibration-smoke-runbook.md` (X 側先例)
- `.steering/20260624-transfer-pipeline/decisions.md` (D1-D7: age 自己完結 bin)
- `docs/development-guidelines.md` §10 (gse-dataset 連携)
- `scripts/build_analysis_db.py` (#6) / `scripts/sync-session.{sh,ps1}` / `src-tauri/src/bin/package.rs`

## 運用メモ
- /reimagine 適用: No
- 理由: 設計は既存パターン (gse-package / sync-session / build_analysis_db) に強く規定され、
  唯一非自明な「decrypt の形態」も検証ゲート前提 (age CLI 未導入の本機で smoke を通す必要)
  から Rust 自己完結 bin (gse-unpack) に一意に定まる。複数案の比較余地が小さい。
