# g1-o1-mac-collection-prep — G1 / O1 の収集開始準備（Mac 実機）

> 出典: `.steering/_handoff/next-session-g1-o1-mac-collection-prep.md`（2026-09-26・Windows 機で作成）。
> ⚠️ そのメモの数字は「書かれた時点の値」。本タスクでは Mac で測り直した値を一次とする（`evidence.md`）。

## 背景

G1（統制タスク実験）と O1（継続的自然作業収集）は ADR-034 で並行実施が決まっている。収集開始の前に、
機械ゲート（`check-g1-collection-readiness.sh` / `check-o1-release-readiness.sh`）を緑にし、
配布 zip を作り、実機で通し確認する必要がある。2026-09-26 時点（Windows 機の実測）は
G1 ゲート 通過 14 / 未達 6、O1 ゲート 通過 21 / 未達 2。
配布 zip の作成（`hdiutil` / `codesign` / `ditto`）・TCC 許可・Release ビルドは macOS 実機でしか完結しない。
この Mac は CI の self-hosted ランナー `gse-mac`（arm64）でもある。

## ゴール

1. Mac で全ゲートを実測し、Windows 機の値との差（macOS 固有の欠陥）を特定する。
2. 研究者の裁定・作業が要る項目を一覧にして渡す（私は埋めない）。
3. 承認が得られた範囲で、最初の配布（タグ・配布 zip）と G1 課題ページの再生成・目視、実機通し確認まで進める。
4. 未達が残る場合は、何が・誰の待ちで残るかを明示して終える。

## スコープ

### 含むもの
- [Mac] 全ゲートの実測と Windows 値との差分表（macOS 固有の検査欠陥の修正を含む）
- [Mac] 研究者の裁定・作業の一覧化
- [Mac][確認] タグ決定 → Release ビルド → `make-common-app-zip.sh --mode g1|o1 --tag <新タグ>` → 4 点の `codesign --verify --strict`・実行ビット・モード標識の検算
- [Mac] G1 課題ページの再生成と全 10 枚の目視
- [Mac] 実機通し確認（初回起動・TCC・計測・アプリ内提出・復号側での受領）

### 含まないもの
- 署名方式（Developer ID・公証）の変更を裁定なしに始めること
- 被験者向け文書（同意文書・participant-guide・課題ページ・README）の文面変更（研究者の承認なしに）
- 凍結物（`docs/preregistration-p1-episode.md`・`src-tauri/prereg/p1-episode.json`）と G1 事前登録の既存の版の書き換え（改訂は append-only）
- 実データを開く／P1 の PG-1 の値を決める／C トラック（媒体表現）への着手
- 承認なしの、タグ push・Drive / フォームの差し替え・被験者への送付
- URL・Google の ID・氏名・メール・セッション時刻を repo に書くこと
- `.steering/20260921-media-expression-theory-audit/` に触れる・コミットする

## 受け入れ条件

- [ ] Mac での全ゲート実測が `evidence.md` に表で残り、Windows 値との差の原因が説明されている
- [ ] 研究者の裁定・作業の一覧（項目・選択肢・推奨・下流への影響）が渡されている
- [ ] （承認後）新タグの配布 zip が、4 点の `codesign --verify --strict`・実行ビット・モード標識・実体（`LC_ALL=C grep -a`）で検算されている
- [ ] （承認後）G1 課題ページ 10 枚を目視し、結果が記録されている
- [ ] （配布物ができた後）実機通し確認の結果が記録されている。できなかった項目は「未実施」と明記
- [ ] 完了報告に「緑にした」ものと「研究者待ちで残る」ものが混ざらずに分けて書かれている

## 関連ドキュメント

- `.steering/20260920-g1-o1-inventory/`（inventory.md / decisions.md / evidence.md / merge-plan.md）
- `experiments/20260801-controlled-friction-task/collection-readiness-record.md` / `preregistration.md` / `participant-guide.md`
- `docs/adr/ADR-034-g1-o1-parallel-conduct.md`（Accepted）・ADR-031 / ADR-032（Proposed）
- `docs/o1-roster-operations.md` / `docs/participant-setup-guide.md`
- `.github/workflows/ci.yml`（`build-macos` の署名ステップ）
- Skill: verify-before-claiming / data-privacy / subagent-delegation

## 運用メモ
- /reimagine 適用: No
- 理由: 新規の設計判断を伴わない準備・検証作業（既存ゲートの実測、既決の配布手順の実行）。裁定が要る箇所は研究者へ渡す（私が設計しない）。
