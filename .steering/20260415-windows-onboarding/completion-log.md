# Completion Log — Windows Onboarding

> Windows 実機での検証完了時に本ファイルを記入する。

## 実行環境

- 実行日時 (Windows 側): _YYYY-MM-DD HH:MM_ (実施時記入)
- 実行日時 (macOS 側集約確認): _YYYY-MM-DD HH:MM_
- Windows PC:
  - OS: _Windows 11 (Build _)_
  - CPU: _<例: Intel Core i7-12700H>_
  - メモリ: _<GB>_
  - キーボード配列: _<US / JIS>_
- gse-prototype commit: _720b2bb 以降_
- gse-dataset commit: _9d2c4ed 以降_

## Stage A: 環境構築
- [ ] A-1: Visual Studio 2022 Build Tools (C++ workload)
- [ ] A-2: Rust stable
- [ ] A-3: Node.js 22 LTS
- [ ] A-4: Git for Windows
- [ ] A-5: SSH 鍵セットアップ
- [ ] A-6: git 設定 (autocrlf=input 等)
- [ ] A-7: Python 3.10+ + jsonschema

所要時間: _<分>_

## Stage B: Clone
- [ ] B-1〜B-4 (両 repo pull 済み)

## Stage C: Build + Test
- [ ] C-1 cargo build — 所要 _<分>_
- [ ] C-2 cargo test — _51 tests passed_
- [ ] C-3 snapshot regression — _OK_
- [ ] C-4 schema drift check — _一致_
- [ ] C-5 tsc + vite build

## Stage D: 実機スモークテスト
- [ ] D-1 Tauri dev 起動
- [ ] D-2 Counter 初期表示
- [ ] D-3 Flow ラベル (デバウンス確認含む)
- [ ] D-4 Inc / Stuck ラベル
- [ ] D-5 セッション終了
- [ ] D-6 NDJSON 生成確認
- [ ] D-7 meta / user_label 内容確認

セッションファイル: `_<basename>.ndjson_`

## Stage E: Metrics + dataset commit
- [ ] E-1 pretty-print 確認
- [ ] E-2 JSON 配置
- [ ] E-3 validate_schema 成功
- [ ] E-4 commit + push — commit hash: `_<hash>_`

Metrics サマリ (pretty-print の抜粋):
```
_<ここに `gse-replay --metrics` の出力を貼り付け>_
```

## Stage F: macOS 側集約確認
- [ ] F-1 git pull
- [ ] F-2 aggregate_metrics.py — session_count: _<数>_ (前回 2 → 今回 _<3以上>_)
- [ ] F-3 `--os windows` / `--os macos` フィルタ動作

## 発見したブロッカー

数: _<0 / N>_。詳細は `blockers.md` 参照。

## 所要時間 (全体)

- 環境構築: _<分>_
- 検証本体: _<分>_
- ドキュメント: _<分>_
- 合計: _<分>_

## 次アクション
- [ ] Windows 側で継続的に GT ラベル付きセッションを収集
- [ ] Phase 2a Go/No-Go 判定の対象セッションに含める (n>=5 を目指す)
- [ ] Stage H (sync-session.ps1 雛形) を別タスクで実行する場合の判断
