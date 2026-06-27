# タスクリスト: パイロット投入前 統合実機スモーク

## 0. 前提確認 (エージェント)
- [x] feature ブランチのマージ要否確認 → **PR#46 でマージ済み・デプロイ不要**
- [x] .gs 作業ツリーが main HEAD と一致確認 (clean)
- [x] AUTO_SEND=true / 主要関数 (buildForm/buildF5/installF1Trigger/onF1Submit/refreshRosterStatus) 存在確認

## 1. 自動検証 (エージェント実行可・gate) — ★全 PASS (2026-06-27)
- [x] `cargo test --workspace` パス (228 tests, 0 fail)
- [x] `gse-replay --snapshot` 一致 (15 snapshots match, HMM 不変)
- [x] `emit_schema` 出力が schema/current.json と一致 (drift なし)
- [x] `tsc --noEmit` エラー 0
- [x] `cargo fmt --check` / `clippy` クリーン (was_active 未使用変数 / collapsible_match・ptr_arg style warn のみ・非ブロック)

## 2. macOS 機能検証 (ユーザー実機)
- [ ] §2.1 介入カードのクリック受理 + フォーカス非奪取
- [ ] §2.2 記録着地 + 窓反転バグ非回帰 (起動5s以内)
- [ ] §2.3 Wall 全画面ブロック→QR→Zen Timer→unlock
- [ ] §2.4 日本語 IME 合成 非回帰
- [ ] F4: 長時間 Idle で idle カウンタ 0 復帰なし / 離席中ランダムプローブ誤発火なし / CGEventTap warn 減

## 3. Windows 差分 (ユーザー実機)
- [ ] クリック受理 / 記録着地 / Wall / IMM 非回帰

## 4/B. Google Form 自動化 (ユーザー Apps Script)
- [ ] B.1 buildForm 2回連続で Invalid data なし / buildF5 単独 / GSE-10・TSE_ITEMS pre-post byte一致
- [ ] B.2 installF1Trigger() → 「フォーム送信時」トリガ / スコープ承認
- [ ] B.3 適格ドライラン: ロスター行+P-ID / baseline / NDA署名=署名済(F1) / 自動メール受信
- [ ] B.4 冪等性: 同一メール再提出でスキップ (♻️ 既発番)
- [ ] B.5 不適格スキップ: IME/OS/同意で発番されない (⛔ 適格外)
- [ ] B.6 管理シート集計: refreshRosterStatus() で F2/F4/F5 ・進捗ダッシュボード更新
- [ ] B.7 配布情報の最終確認

## 発見不具合 / follow-up
- [ ] **F-1 (要対応・pilot前)**: `APP_DOWNLOAD_INFO` がプレースホルダのまま (.gs L44-46)。
      AUTO_SEND=true なので適格 F1 提出で被験者へプレースホルダ文面が自動送信される。
      実配布先 (gse/gse-package/pubkey.txt の DL リンク) に書き換え必須。→ findings.md 参照
