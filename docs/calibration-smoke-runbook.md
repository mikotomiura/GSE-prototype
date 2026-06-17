# v0.3 較正スモーク 実行ランブック (自己ドッグフード → 3-5名スモーク)

> 対象: v0.3 較正の計測基盤 (A schema / B probe scheduler / C collect UI / D offline解析 /
> E cohort判定 / blind dashboard) を**実データで駆動**し、PreReg 判定を出すまでの運用手順。
> 解析パイプラインの非GUI部分は `scripts/run-calibration-cohort.sh` に集約済み。
> 契約は `docs/preregistration-v0.3.md` (PreReg-1..8) で凍結。**閾値はデータに合わせて動かさない。**

---

## 0. 前提・プライバシー

- **git-bash 必須** (Windows)。helper / hook はすべて bash 前提。
- **保存先**: `GSE_DATASET` を gse-dataset に向ける (永続化推奨)。
  ```bash
  # PowerShell (User 環境変数として永続化)
  [Environment]::SetEnvironmentVariable('GSE_DATASET', 'C:\gse-dataset', 'User')
  ```
  未設定時は `~/Documents/GSE-sessions/` に fallback。起動時 tracing log の `resolved_log_dir` で確認。
- **プライバシー (厳守・§10 / data-privacy)**: セッション NDJSON 生ログ・キーストローク内容は
  **本リポにも gse-dataset にもコミットしない／外部送信しない**。端末ローカル保持。
  共有してよいのは `metrics/` の `*.calib.json` と `cohort/` の判定 JSON (集計値のみ) だけ。

---

## 1. ビルド

```bash
# Rust バックエンド + 解析バイナリ
cd src-tauri && cargo build --release --bin gse-replay --bin gse-cohort && cd ..
# フロントエンド型チェック+ビルド
npm run build
# アプリ起動 (収集に使う)
npm run tauri dev      # もしくは cargo tauri build で配布ビルド
```

---

## 2. Phase A — 自己ドッグフード (1名・end-to-end 検証)

目的: 収集→解析の通し動作を 1 人で確認する (本番ではなく配線確認)。

1. `npm run tauri dev` で起動。メイン画面が **blind dashboard** (較正モード既定 ON) になっていることを確認
   — 推定状態 / Flow・Incubation・Stuck 確率 / GT カウンタが**出ない**こと。
2. Start 画面で task_kind を選び、**「介入を有効にする」はオフのまま**(較正既定)・**較正モード ON** で開始。
3. しばらく自然に作業する。ランダムプローブ (ProbeCard) が出たら Q1 摩擦 / Q2 前進を回答。
4. セッション終了。`raw/P000/gse_*.ndjson` が生成されたことを起動ログ (`resolved_log_dir`) で確認。
5. 解析を通す:
   ```bash
   ./scripts/run-calibration-cohort.sh --no-cohort        # P000 の calib.json を生成
   ```
   `metrics/P000/<os>/P000.calib.json` が出れば end-to-end 成功。
   ※ `input/` の OS フック (キャプチャ) は実機でしか検証できない。打鍵が記録されているか NDJSON 行数で確認。

---

## 3. Phase B — 3-5名スモーク

### 3.1 収集 (各参加者)
- 各参加者の端末/アカウントでセッションを収集。**`interventionEnabled=false` / `calibrationMode=ON`** を厳守
  (測定独立性: モデル出力を見せない)。
- **PreReg-5 最低要件 (1人あたり)**:
  - 評価セッション **≥6 回**。先頭 2 本は β 較正 holdout に充てるため **main セッション ≥8 本**が必要。
  - ランダムプローブ **≥16 件/人** (提示ベース)。プローブは ≤2回/30分なので 8 本×平均2 で到達目安。
- **PreReg-2 被験者要件** (満たさないとモデルゲート母数から除外): 回答率 ≥0.80 / 回答時間中央値 ≤10s /
  有効プローブ ≥20。
- 尺度理解テスト (ビネット) は現行最小スコープでは延期 (PreReg-1 は比較条件実装段で発効)。

### 3.2 整理 (P000 固定問題の吸収)
logger は **常に `raw/P000/` に書く**。多人数ぶんを 1 つの gse-dataset に集約するには、各参加者の
NDJSON を被験者番号ディレクトリへ手動で振り分ける:
```bash
# 例: 参加者2人目の収集ぶんを P001 へ
mkdir -p /c/gse-dataset/raw/P001
mv /c/gse-dataset/raw/P000/gse_2026XXXX_*.ndjson /c/gse-dataset/raw/P001/
# (P000 は1人目、P001/P002/... を割り当てる。取り違えに注意)
```

### 3.3 判定
```bash
./scripts/run-calibration-cohort.sh           # 全 P*/ を解析 → cohort 判定
```
- 出力: `cohort/cohort_<timestamp>.json` (stdout にも表示)。`overall` を読む:
  | overall | 意味 | 次アクション |
  |---|---|---|
  | `go` | モデルゲート Go (全充足者 C-index 中央値≥0.65 & 全員>0.55) | 核検証フェーズへ |
  | `kill` | 測定法 Kill (回答率) または モデル Kill (`decision_reason` で区別) | ラベル方式 / モデルを差し戻し |
  | `inconclusive` | 閾値未達・尺度理解未達・充足が一部のみ | データ拡充・設計見直し |
  | `data_insufficient` | 主指標0名 / 提示プローブ0件 / PreReg-5 充足者なし | **データ拡充** (正直に報告) |
- **無理に `go` と言わない** (§11 主張限界)。PreReg-5 未達なら `data_insufficient` のまま「データ拡充が必要」と報告。
- `notes` / `mnar_*_count` / `bidimensionality_verifiable_count` で MNAR (PreReg-7)・二軸性 (PreReg-8) を併走報告。

### 3.4 共有
- `metrics/` と `cohort/` の集計 JSON のみ gse-dataset へ commit/push。**NDJSON は置かない。**

---

## 4. トラブルシュート
- プローブが出ない: probe_scheduler は warm-up ガードあり。短すぎるセッションでは発火しない。十分な作業時間を確保。
- `raw/P*/` が見つからない: `GSE_DATASET` 未設定 (fallback の Documents 下に出ている)。`--root` で明示するか env 設定。
- 権限 (キャプチャ無効): Dashboard の権限バナー / 診断に従う (macOS Input Monitoring / Accessibility)。
