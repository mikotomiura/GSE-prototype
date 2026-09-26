# 設計

## 実装アプローチ

コード変更を前提としない準備タスク。順序は引き継ぎメモ §3 に従い、**実測 → 一覧化 → 承認 → 実行** とする。

1. 最初に Mac で全ゲートを実測し、Windows 値（メモ §1）との差を取る。差は macOS 固有の欠陥（bash 3.2 / BSD `sed`・`od`）の可能性が高い（前例: PR #128）。
2. 研究者の裁定が要る項目は私が埋めず、一覧にして渡す。答えが返るまで下流（タグ・配布）を止める。
3. 共有状態を変える操作（タグ push・Drive / フォーム・被験者送付）は実行前に必ず承認を取る。
4. 配布物は「ゲート緑」でなく**実体**で検算する（`LC_ALL=C grep -a`。`strings` は日本語で偽陰性）。

## 変更対象

### 修正するファイル
- 実測で macOS 固有の検査欠陥が見つかった場合のみ、該当の `scripts/*.sh`（見つかってから決める）

### 新規作成するファイル
- `.steering/20260926-g1-o1-mac-collection-prep/evidence.md` — Mac 実測値と Windows 値との差分表
- `.steering/20260926-g1-o1-mac-collection-prep/decisions.md` — 判断が出た場合

### 削除するファイル
- なし

## 影響範囲

- 被験者向け文書・凍結物・事前登録の既存版には触れない。
- タグ push は `build-macos`（この Mac 上のランナー）を発火する。ディスク空きを事前確認する。

## 既存パターンとの整合性

- 配布は `make-common-app-zip.sh` / `make-distribution.sh`（`--tag` 必須）。署名は ad-hoc のまま（`ci.yml` の署名ステップ）。
- 記録票は申告。緑にしても実物（Drive・フォーム・CI）は別途確認が要る。

## テスト戦略

- 各ゲートの `--selftest`（陽性・陰性の対照）
- 配布 zip: `codesign --verify --strict` を 4 点（dmg 内 → コピー後 → zip → 展開後）・実行ビット・モード標識
- 実機通し確認: 初回起動・TCC・計測・アプリ内提出・復号側受領

## ロールバック計画

- コミット前の変更は `git restore`（ただし `.codex/budget.json` は台帳なので戻さない）。
- 誤ったタグは push 前なら `git tag -d`。push 後は共有状態なので研究者に相談する。

## 実施結果（2026-09-26・最終化）

- **コード変更**は `scripts/check-g1-collection-readiness.sh` のみ（Mac 固有の selftest 欠陥の修正 ＋ 検査 [3] の検査語 ＋ 検査 [7] の selftest を緑から壊す形へ）。Rust / TypeScript の変更は無い。
- **文書**: `preregistration.md` 第 20 版（append-only）・`config.json` revision 20・`analyze.py` `PREREG_REVISION` 20・`docs/o1-roster-operations.md` §5 の 1 行。被験者向け文書・凍結節（§3.1/3.2/3.4/3.5/3.6）は変えていない。
- **ゲートの実測（Mac）**: G1 = 通過 17 / 未達 3（残りは記録票 A/B/C＝研究者の人手確認）。selftest 34/0。O1 = 21/2（同意文書の「未了」・タグ陳腐化）・selftest 59/0。移植性 12/0。`check_frozen_sections.py` 緑・`analyze.py --selftest` 緑・`run.sh` GREEN。
- **設計上の学び**: 実 repo が前提条件を満たした瞬間に、`expect_green` 型の変異は空回りになる（ゲート自身のコメントが予告）。→ 緑から壊す形＋ `expect_stays_green`。
- **未実施（繰り越し）**: Release ビルド・配布 zip・実機通し確認（タグ名の再承認後）／ Drive 差し替え・記録票（研究者）／ `validate_blocks.py` の未完了マーカ（第 20 版が別タスクと明記）。
