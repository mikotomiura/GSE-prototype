# transfer-pipeline (anonymize + package-session 自己完結 bin)

## 背景
WBS 0.15 / decisions D6 / punch-list #3,#4。外部被験者 (M1 Phase 1a, n=3-5) が raw NDJSON を
安全に研究者へ転送する手段が未実装 (scripts は sync-* のみ)。data-privacy「生 NDJSON 外部送信禁止・
暗号化ローカルのみ」を満たす **匿名化→暗号化→提出** のワンコマンドが要る。

## ゴール
被験者 (Mac/Win 混在・非技術者) が **1 つの自己完結 exe** で:
raw NDJSON → 匿名化 (VK→KeyCategory・時刻相対化) → **age 暗号化** (研究者公開鍵同梱) →
`P###_<date>.age` を生成し、Dropbox File Request に提出するだけにする。Python/age CLI 不要。

## スコープ
### 含むもの
- `age` crate を Cargo.toml に追加 (X25519 recipient 宛暗号化)。
- 匿名化モジュール `analysis/anonymize.rs`: NDJSON 行を変換 (key: vk→KeyCategory、全イベント: 絶対
  epoch 時刻フィールドを session_start 相対に)。anonymization.md 準拠。**本文・VK・タイトルを残さない**。
- 新 bin `src/bin/package.rs` (`gse-package`): 入力 raw NDJSON + participant ID + recipient 公開鍵 →
  匿名化 → age 暗号化 → `P###_<YYYYMMDD>.age` 出力。recipient は同梱ファイル/引数 (研究者が自分の
  age 公開鍵を入れる・配布安全)。
- 単体テスト: vk→category・時刻相対化・VK 非残留・age 暗号復号ラウンドトリップ (テスト鍵)。

### 含まないもの
- replay の category 対応 (匿名化 NDJSON での特徴量再計算=D6) は **follow-up** (データは暗号化保存され
  不可逆ではない・解析ツールは後付け可)。本タスクは捕捉=匿名化保存まで。
- Dropbox 自動アップロード (被験者が手動提出・D6 運用)。tar (複数セッション束ね) は単一ファイルなら不要。
- 鍵生成 (研究者が age keypair を生成し公開鍵を提供=運用)。

## 受け入れ条件
- [ ] gse-package が raw NDJSON を匿名化+age 暗号化し `P###_<date>.age` を出力
- [ ] 匿名化出力に VK 生値・絶対 epoch・本文が残らない (テストで検証)
- [ ] age 暗号→復号ラウンドトリップ (テスト鍵) 成功
- [ ] cargo test --workspace 緑・既存 --snapshot byte-equal (logger/replay 不変)・build 緑

## 関連
- `anonymization.md` (VK→KeyCategory・相対時刻・チェックリスト) / decisions D6 / WBS 0.15
- data-privacy Skill / rust-standards / Skill: git-workflow

## 運用メモ
- /reimagine: No (仕様準拠)。実装形態=Rust 自己完結 bin (ユーザー承認)。別 PR・main 基点。
- age recipient 公開鍵は研究者が生成・提供 (本実装は placeholder + 引数/ファイル指定)。
