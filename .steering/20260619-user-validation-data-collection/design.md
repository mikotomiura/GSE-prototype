# 設計: ユーザー検証データ収集パイプライン

本タスクは**設計判断のみ** (実装は下流の別タスク)。確定した判断は `decisions.md` (D1-D6 + 転送経路) を参照。

## アプローチ要約

外部被験者 (P001+) のデータを、プライバシー制約 (data-privacy Skill) を守りつつ収集・保存する
エンドツーエンド経路を設計した。芯は GSE の「Replay-as-Truth (ファイルが真実源)」哲学の踏襲。

### 検証の2層
1. **v0.3 較正スモーク** (RH1, 状態分離精度): 真値 = アプリ内ランダムプローブ `realtime_label`
2. **Phase 4 βテスト効果検証** (RH3): 指標 (a) AI依存度 / (b) 自力解決率 / (c) 自己効力感

### 3 データストリーム (P-ID で結合)
| 系統 | 中身 | 発生 | 機微度 | 経路 |
|---|---|---|---|---|
| ① セッション NDJSON | 打鍵動態・realtime_label・介入ログ | 端末アプリ | 高 | 匿名化→age暗号→Dropbox |
| ② フォーム CSV | 同意・尺度理解ゲート・デモグラ・GSE pre/post・デブリーフ | Google フォーム | 低〜中 | フォーム→Sheet→CSV |
| ③ 派生メトリクス | gse-replay --metrics 集約値・(a)(b)指標 | ①から計算 | 低 | private repo に commit |

### エンドツーエンド・フロー
```
[被験者端末]                          [研究者 (暗号化ローカル)]            [gse-dataset private repo]
1. アプリ→ raw/P###/ に NDJSON
2. package-session: anonymize.py
   (VK→カテゴリ/時刻相対化)→tar→age
   → P###_<date>.age (暗号塊)
        │ 3. Dropbox ファイルリクエスト
        └────────────────────────────►  4. 復号→ anonymized/P###/
                                         5. gse-replay --metrics → metrics/P###/<os>/
                                         6. (a)(b) 算出 (diff連携 + Mehta KS)
                                         7. metrics + survey/P###.csv を commit ─► metrics/ survey/
                                         8. duckdb で analysis.db 再生成
                                            (metrics ⋈ survey on P-ID)
```

## 変更対象 (下流タスクでの実装範囲)
- `src-tauri/src/logger.rs` (参加者 ID 設定可能化)
- `src-tauri/src/` 入力系 (クリップボード・ペーストイベント計測、回数のみ)
- `scripts/anonymize.py` (外部被験者向け整備)
- `scripts/package-session.{ps1,sh}` (新規)
- `src-tauri/bin/gse-replay` or 解析スクリプト ((a)(b) 指標)
- DuckDB 解析ハーネス (新規)
- gse-dataset レイアウト拡張 (`survey/`, `_keymap/`)

## テスト戦略
- 実装は各下流タスクで Replay-as-Truth (gse-replay --snapshot byte-equal) により回帰保護。
- anonymize.py は data-privacy 送信前チェックリスト (VK カテゴリ化・タイムスタンプ相対化・
  ウィンドウタイトル/プロセス名除外・匿名 ID) で検証。
- 本タスク自体は設計のみのためコード変更なし・テスト対象なし。

## 非対象 / 保留
- 心理尺度の具体的日本語版項目の転記 (公式ソースで利用条件確認後、フォーム設計タスクで)
- フォーム本体 (チャネルA) の項目設計
- サーバ DB は採用しない (N=3-10 規模、ファイル真実源 + DuckDB で十分)
