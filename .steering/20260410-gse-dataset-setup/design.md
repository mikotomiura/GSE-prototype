# 設計

## 実装アプローチ

GSE-prototype と同階層に `C:\gse-dataset\` を独立リポジトリとして作成する。
Phase 1（自分1人）の構造で作り、Phase 2（5名）に拡張可能な設計にする。

**なぜ別リポジトリか:**
- データとコードのライフサイクルが異なる（データは蓄積、コードは変更）
- 生データに VK コードが含まれるため、コードリポジトリに混ぜない
- Phase 2 で被験者データを含むため、private リポジトリとして管理

## ディレクトリ構造

```
C:\gse-dataset\
├── README.md                         # データ管理計画・利用ガイド
├── .gitignore                        # raw/ と anonymized/ のデータは git 管理外
├── schema/
│   └── v1.json                       # NDJSON スキーマ定義（JSON Schema）
├── raw/                              # 生ログ（被験者IDで分離）
│   └── P000/                         # 自分自身 = P000
│       └── .gitkeep
├── anonymized/                       # 匿名化済み
│   └── P000/
│       └── .gitkeep
├── labeled/                          # ラベル付け済み（Phase 2 以降）
│   └── .gitkeep
├── splits/                           # train/val/test 分割（Phase 2 以降）
│   └── .gitkeep
├── consent/                          # 同意書（Phase 2 以降）
│   └── .gitkeep
├── scripts/
│   ├── anonymize.py                  # raw → anonymized 変換
│   ├── validate_schema.py            # スキーマ準拠チェック
│   ├── import_sessions.py            # GSE-sessions → raw/ へのインポート
│   └── requirements.txt              # Python 依存（jsonschema のみ）
└── models/                           # 学習済みパラメータ（Phase 2 以降）
    └── .gitkeep
```

## 変更対象

### GSE-prototype への変更
- なし（独立リポジトリのため）

### 新規作成するファイル（gse-dataset 内）
- `README.md` — データ管理計画
- `.gitignore` — raw/, anonymized/ のデータファイルを除外
- `schema/v1.json` — logger.rs の出力に基づくJSON Schema
- `scripts/anonymize.py` — VKコード → キー種別カテゴリへの変換
- `scripts/validate_schema.py` — NDJSONファイルのスキーマ検証
- `scripts/import_sessions.py` — GSE-sessions/ → raw/P000/ へのコピー
- `scripts/requirements.txt` — jsonschema

## 匿名化設計

data-privacy 規約に準拠し、VKコードをキー種別カテゴリに変換する:

| VK 範囲 | カテゴリ | 説明 |
|---|---|---|
| 0x41-0x5A | `alpha` | アルファベット |
| 0x30-0x39 | `digit` | 数字 |
| 0x08 | `backspace` | バックスペース |
| 0x20 | `space` | スペース |
| 0x0D | `enter` | エンター |
| 0x09 | `tab` | タブ |
| 修飾キー群 | `modifier` | Shift/Ctrl/Alt/Win |
| 矢印キー群 | `arrow` | 方向キー |
| その他 | `other` | 上記以外 |

feat レコードはそのまま保持（特徴量・確率は個人特定に使えない）。

## テスト戦略

- `validate_schema.py` に既存ログ（gse_20260404_135519.ndjson）で動作確認
- `anonymize.py` の変換結果を目視検証（VKコードが残っていないこと）

## ロールバック計画

独立リポジトリのため、ディレクトリ削除で完全にロールバック可能。
