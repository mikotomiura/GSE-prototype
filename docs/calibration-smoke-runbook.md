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

### 1.1 起動モード: 被験者 vs 研究者デバッグ (二重 gate)

デバッグ機能（プローブ/Nudge 強制表示・第2週モデル出力表示）は **2 つのフラグ**で守られる。
**被験者はフラグなしで起動 = 完全ブラインド**、**研究者だけが両方を足す**という非対称になる。

| フラグ | 種別 | 効果 |
|---|---|---|
| `VITE_GSE_DEBUG=1` | Vite **ビルド時** env (フロント JS に焼き込み) | デバッグボタン描画・第2週モデル出力表示 |
| `GSE_DEBUG=1` | **実行時** env (Rust backend が `ensure_debug_enabled` で読む) | `force_wall`/`force_nudge`/`debug_force_probe` を許可。未設定だと DevTools から直接 invoke しても Err で拒否 |

- **被験者配布 (本番)**: CI 本番バイナリ (.app/.dmg/nsis) を**フラグなしでそのまま起動**。盲検は両 env 既定 OFF で守られる。
- **研究者デバッグ (dev)**: 同一コマンドで両方渡す (vite/cargo 両プロセスが継承):
  ```bash
  VITE_GSE_DEBUG=1 GSE_DEBUG=1 npm run tauri dev
  ```
- **本番ビルドでスモーク**: `VITE_GSE_DEBUG=1 npm run tauri build` でビルド → 起動時に `GSE_DEBUG=1` を渡す。
  - ⚠ macOS の `open App.app` は env を渡さない。実体を直接実行するか launchctl を使う:
    ```bash
    GSE_DEBUG=1 "App.app/Contents/MacOS/<bin>"      # 直接実行
    # または: launchctl setenv GSE_DEBUG 1 してから起動
    ```
  - Windows は起動前のシェルで `set GSE_DEBUG=1` (or System 環境変数)。

### 1.2 デバッグトリガと fail-loud バナーの確認 (#1 検証)

研究者デバッグ起動 (§1.1) の Dashboard には以下が出る:
- **📝 プローブ強制表示 / 💡 Nudge 強制表示** ボタン。プローブ → 回答/skip →
  `record_realtime_*`、Nudge → dismiss → `record_intervention_dismiss` の経路を能動的にテストできる。
  > ⚠️★★★ **2026-09-01 訂正 —— 旧文が挙げていた「🧱 Wall 強制発動」ボタンは存在しない。**
  > ★ ADR-015 (2026-08-23) で Wall ごと削除された (実測: `src/components/Dashboard.tsx:564-587` に
  > 残るのは `debug_force_probe` と Nudge の 2 つのみ。デバッグ強制 Wall のテスト
  > `force_wall_decision_returns_wall_and_starts_cooldown` も
  > `src-tauri/src/analysis/intervention.rs:570` の記録どおり削除済み)。
  強制発火は `reason="debug_force"` で NDJSON に残り、解析時に除外可能。
- **fail-loud バナー**: ログ書込先が temp フォールバック / 無効に縮退した場合、Dashboard 上部に警告
  バナーが常時表示される (静かな全損の撲滅)。**本番 .app/.dmg は dev と TCC 文脈が異なるため、
  macOS Documents 権限未付与の repro はこの本番ビルドでこそ顕在化しやすい** → 必ず本番でスモークする。

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
  研究者は §1.1 のデバッグ起動で **📝 プローブ強制表示** ボタンを使えば即座に出せる。
- デバッグボタンを押しても効かない / `debug command disabled` エラー: `GSE_DEBUG=1` 未設定 (§1.1)。
  本番 .app は `open` で env が渡らない点に注意 (実体直接実行 or `launchctl setenv`)。
- **fail-loud バナーが出る** (「ログを一時フォルダに保存しています」/「ログを保存できません」):
  primary 書込先に書けず temp フォールバック or 無効化されている。原因は `GSE_DATASET` の誤指定 /
  未マウント、または **macOS の Documents アクセス権限未付与** (本番 .app の TCC)。バナーの保存先パスを
  確認し、権限付与 or `GSE_DATASET` 修正後に再起動する。temp に落ちたデータも回収可能。
- `raw/P*/` が見つからない: `GSE_DATASET` 未設定 (fallback の Documents 下に出ている)。`--root` で明示するか env 設定。
- 権限 (キャプチャ無効): Dashboard の権限バナー / 診断に従う (macOS Input Monitoring / Accessibility)。
