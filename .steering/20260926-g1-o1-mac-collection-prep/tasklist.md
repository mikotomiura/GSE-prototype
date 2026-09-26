# タスクリスト

区分: [Mac] = このセッションで実施 ／ [研究者] = 私は埋めない ／ [確認] = 実行前に承認を取る

## 準備
- [x] 引き継ぎメモを読む
- [x] main を最新にする（58fb589）・作業ブランチ `chore/g1-o1-mac-collection-prep`
- [x] docs/agent-shared.md のリンクハブから該当 docs を読む（inventory.md は読了。ADR-034 と記録票は下流の着手時に読む）
- [x] Skill 参照: verify-before-claiming / data-privacy / subagent-delegation
- [x] ランナーのディスク空きを確認（現在 18Gi・前例: 2026-08-31 に枯渇）

## 0. [Mac] 全ゲートの実測
- [x] `check-g1-collection-readiness.sh`（＋ `--selftest`）
- [x] `check-o1-release-readiness.sh`（＋ `--selftest`）
- [x] `check-shell-portability.sh`
- [x] `make-common-app-zip.sh --selftest`
- [x] Windows 値との差分表を `evidence.md` に書く（macOS 固有の欠陥の有無）

## 1. [研究者] 裁定・作業の一覧
- [x] 前提条件 3 / 前提条件 7 / O1（ADR-031・032・事前登録・O1-5）/ G1（G1-9・10・11）を一覧化して渡す（`researcher-decisions.md`）
- [x] 回答待ち → 2026-09-26 に推奨案で回答（`decisions.md` 判断 1〜6）

## 2. [Mac][確認] 配布
- [x] タグ候補と main の状態を提示（`tag-candidate.md`）→ **研究者の承認待ち（「まず中身を見せて」）**
- [ ] Release ビルド → `make-common-app-zip.sh --mode g1|o1 --tag <新タグ>`  ⏭ **繰り越し**（本 PR の出荷後にタグ名を示して再承認 → 実施）
- [ ] 4 点 `codesign --verify --strict`・実行ビット・モード標識・実体の検算  ⏭ **繰り越し**（配布物ができてから）

## 3. [Mac] G1 課題ページ
- [x] `build_task_pages.py` で再生成 → 機械照合（Downloads の 200 枚と現行ジェネレータ出力が 200/200 バイト一致）。⏭ 目視は研究者
- [ ] Drive 差し替え（[研究者]）  ⏭ **繰り越し**

## 4. [研究者] 記録票 A / B / C  ⏭ **繰り越し**（研究者作業）

## 5. [Mac] 実機通し確認
- [ ] 初回起動（隔離属性・入力監視）→ 計測 → アプリ内提出（G1 / O1）→ 復号側受領  ⏭ **繰り越し**（配布物ができてから）

## レビュー
- [ ] code-reviewer + security-checker（並列・model 明示）
- [ ] /cross-review（必須）

## 完了処理
- [ ] design.md / evidence.md の最終化
- [ ] decisions.md（判断があれば）
- [ ] /finish-task → git-workflow ルール 6

## 追加で実施したこと（推奨案の採用）
- [x] 前提条件 3 → ゲート [3] の検査語を実体へ（`decisions.md` 判断 4）
- [x] 前提条件 7 → 事前登録 第 20 版・config revision 20・analyze PREREG_REVISION 20（判断 5）
- [x] O1-5 → `docs/o1-roster-operations.md` §5 に 1 行（判断 6）

## 完了時レビュー後の繰り越し
- [ ] 計器の対応（未完了マーカ・n 未達ゲート・登録/解析 n の報告）と G1 の人単位破棄手順 ⏭ 研究者が前提条件 8 として足すか裁定
- [ ] 取り消し規則を `protocol.md` へ ⏭ 研究者判断
