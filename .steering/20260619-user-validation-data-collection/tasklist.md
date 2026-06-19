# タスクリスト

## 本タスク (設計議論) — 完了
- [x] 参加者 ID 割り当て方式の決定 (D1: ランダム採番)
- [x] 送付チャネル分離方針の決定 (D2: 調査票=フォーム / NDJSON=暗号転送)
- [x] (c) 自己効力感の尺度確定 (D3: Schwarzer & Jerusalem GSE 10項目)
- [x] クリップボード監視のプライバシー制約決定 (D4: 回数のみ・中身禁止)
- [x] 収集〜DB 保存経路の決定 (D5: ファイル真実源 + DuckDB)
- [x] 端末→研究者の出力方式決定 (D6: 匿名化 NDJSON を age 暗号化)
- [x] 転送経路の決定 (Dropbox ファイルリクエスト, Mac/Win 両対応)
- [x] decisions.md / design.md / requirement.md 記録

## 下流の実装タスク (別タスクで /start-task) — 未着手
- [ ] ① `logger.rs:920` の P000 ハードコード解消 → 参加者 ID 設定可能化 ★他の前提・起点
- [ ] ② クリップボード・ペーストイベント計測 (回数のみ・中身禁止) を NDJSON に追加
- [ ] ③ 外部被験者向け anonymize.py 整備・出力検証
- [ ] ④ scripts/package-session.{ps1,sh} (anonymize→tar→age 暗号化ワンコマンド)
- [ ] ⑤ (a)(b) 指標算出を gse-replay --metrics 拡張 or 解析スクリプトで (diff連携・Mehta KS)
- [ ] ⑥ DuckDB 解析ハーネス (metrics ⋈ survey on P-ID)
- [ ] フォーム本体 (チャネルA) 項目設計: 同意・尺度理解ゲート・GSE pre/post・デブリーフ
- [ ] gse-dataset レイアウト拡張 (survey/, _keymap/) + 研究者 age 鍵ペア生成・公開鍵配布

## 推奨着手順
①(前提) → ②③④(収集経路) → ⑤⑥(分析) と、フォーム設計は並行可。
