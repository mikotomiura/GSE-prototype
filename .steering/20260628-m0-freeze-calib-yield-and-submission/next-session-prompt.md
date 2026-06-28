# 次セッション用 開始プロンプト（M0 凍結：較正ラベル収量の是正 ＋ 提出摩擦の排除）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> 被験者 pilot の**取り直しの効かないデータ**を集める前に、実データで判明した複数の阻害要因を
> **1 本のクリーンビルド（M0 凍結）＋運用**に束ね、P007（実参加者）を confirmatory として再走できる状態にする。
> コード（Rust 較正プロファイル）＋ツール（提出ラッパー）＋docs（prereg/ガイド）の混合タスク。

## 0. 一言ゴール
直近セッションで**実データ復号・定量済み**。リリース版（HMM 0.3.0）の2提出は GATE2（有効≥20件/人）を桁違いに下回った：
- **P006＝研究者自身のテスト**: 8.1 分・random-probe 発火 **0 回**・有効ラベル **0 件**。
- **P007＝実参加者**: 37.2 分・発火 3 回 @ **7.0 / 28.4 / 37.2 分（7→28 で 21 分 drought＝枯渇バグ署名）**・有効 **3 件**・self-marker **0**。
→ 原因は (i) probe 枯渇バグ【PR#56 で修正済】に加え、(ii) **較正の発火レートが低すぎてラベル収量不足**、
(iii) **self-marker 未使用**、(iv) **提出が CLI＋パス手打ちで参加者に不可能**、(v) **`.age` ファイル名に実名が漏れる**。
本タスクで (ii)〜(v) を是正し M0 を凍結。リリース版データは **shakedown** に格下げ、prereg に**バージョンカット**を宣言する。

## 1. 最初にやること
1. `/start-task` で `.steering/20260628-m0-freeze-calib-yield-and-submission/` を本格化（requirement/design/tasklist。本ファイルは同ディレクトリにある）。
2. サブエージェント並列で先読み（要点だけ回収）:
   - `src-tauri/src/analysis/probe_scheduler.rs`（`ProbeConfig`・soft max-gap、PR#56 で導入済み）＋ `lib.rs` のプローブ駆動（seed/プロファイル供給箇所）。
   - `src-tauri/src/bin/package.rs`（gse-package＝匿名化＋age暗号化 CLI）＋ `unpack.rs`。
   - `docs/preregistration-v0.3.md`（PreReg-2/-3 の GATE2 測定法・回答率/latency/有効件数）、`docs/research-positioning.md §5/§6/§8`（GATE2/3・WBS M0-M5・成功基準）。
   - `docs/participant-setup-guide.md` / `docs/pilot-runbook.md` / `docs/experiment-tracking.md`（提出フロー・鍵運用・対応表）。
   - skill: `literature-card`・`citation-ssot`（T0 用）／`hmm-analysis`・`rust-standards`・`architecture-rules`・`data-privacy`・`intervention-design`。
3. **実施順**: **T0 落合サーベイ → §2 で数値確定 → T1〜T5 実装 → §4 M0 凍結 → 再走**。T0/§2 を飛ばして実装に入らない。
4. 必要なら実データを再確認（生 NDJSON は外部送信禁止・ローカルのみ）。`.age` は `/Users/johnd/Downloads/P006_..._mikoto miura.age` / `P007_..._mikoto miura.age`。
   復号: `gse-unpack`（ビルド済み: `src-tauri/target/release/gse-unpack`）`--input <age> --identity ~/.gse/age-identity.txt --out <dir>`。

## T0. 落合フォーマット 情報収集（このタスクの最初に実施・実装判断の前提）

§2 の設計判断（較正レート・GATE2 件数・self-marker・提出 compliance）は現状**概算**なので、**先に文献で裏取り**してから数値を確定する。`literature-card` skill＋`citation-ssot` で落合カード化（捏造禁止・WebSearch 実在確認・provisional 可）。
- **既存資産を起点に拡張**（重複カード化は避ける）: probe-timing サーベイ [V18]-[V23]（`docs/literature/20260628-probe-timing-interruptibility.md`）。今回は **density / 収量 / compliance / 個人内サンプルサイズ**へ踏み込む。
- 調べる問い（§2 の各判断に 1:1 で対応）:
  1. **ESM/EMA のサンプリング密度**: 1 日/1 時間あたり何回の signal が標準か、**頻度 vs 応答率(compliance)・負担**のトレードオフ（高密度較正は何回まで許容されるか）。
  2. **個人内較正に必要なラベル数**: within-person の順序一致/C-index・single-case/N-of-1 デザインで**安定推定に要するサンプル数**の目安（GATE2 ≥20 件の妥当性検証）。
  3. **event-contingent（self-report 起動）の compliance**: 参加者起動ラベル（self-marker）の遵守を上げる条件・既知の脱落要因。
  4. **データ収集 UX と retention**: 提出摩擦・通知負担が compliance/離脱に与える影響（T2/T4 の裏付け。実証が薄ければ provisional）。
- 候補ソース（WebSearch で実在確認のうえ V 名前空間へ append）: ESM compliance のメタ分析系（例 van Berkel et al. の ESM サーベイ、Vachon/Wen 等の EMA compliance）、N-of-1/single-case methodology、JITAI/MRT の sample-size（[V4] Qian を起点）。
- 成果物: 落合カード ≥2〜3 本を `docs/literature/<date>-calibration-sampling-density.md`、`docs/literature/_index.md` 追記、出典を `docs/references.md`(V) に append-only。各カードに「GSE §6/§8 への含意（較正レート/GATE2 件数への示唆）」を付す。
- **使い方**: T0 の所見を**§2 の数値根拠**として引用（例「ESM compliance は 1 日 N 回超で急落 [V##] → 較正は M 分間隔・1 セッション K 件を上限」「N-of-1 で安定推定に約 L 件 [V##] → GATE2 ≥20 は妥当/要調整」）。裏取りできない数値は概算と明示。

> ⚠️ 「一応」の軽量サーベイで可。**§2 の判断に直結する問いに絞る**（density・サンプルサイズ・compliance）。網羅サーベイにしない。

## 2. 先に決める（実装前に確定する設計判断・T0 の所見を根拠に）
1. **較正 probe レート（最重要）**: 現行 λ=2/30分では 20件/人 ≈ 5〜6 時間/人で非現実的。
   - **較正専用プロファイル**を新設（例 λ≈1/6〜8 分・gap_min≈3〜4 分・max_gap≈10〜12 分・cap 緩め）。目標「20 件を約 1.5〜2 時間 or 2〜3 セッション/人」から逆算し、軽い power 観点で数値確定。
   - **非侵襲レート（Phase2 配備用）と分離**: 較正は構造化セッションなので収量優先、配備は侵襲最小。`ProbeConfig` は注入式なのでプロファイル追加で両立。31s 分析窓と重ならない gap_min を厳守。
   - measurement independence は維持（stratified random のまま・小休止合わせは入れない＝L0 較正の独立性）。
2. **GATE2 ≥20 件/人の妥当性**: 閾値の根拠とセッション数前提を prereg と突き合わせ、必要なら「件数 or セッション設計」を再定義（捏造でなく根拠付きで）。
3. **提出方式**: **A＝最新セッション自動検出のダブルクリック・ラッパー（推奨）** vs B＝アプリ内ページ。
   推奨理由: A は **age 依存を blind アプリ本体に載せず**（隔離・盲検維持）、参加者のパス手打ちミスを排除。B は最楽だが age 依存をバイナリに載せる審査が要る。
4. **self-marker 導線**: 教示・UX をどう変えれば participant が使うか（現状 0）。較正ラベル源を probe 単独依存から外す。

## 3. 実装トラック
- **T1 較正 ProbeConfig プロファイル**（Rust）: `probe_scheduler.rs` に calibration プロファイルを追加し、`lib.rs` で較正セッション時に選択。seed 決定性・引数注入・純ロジックを維持。`cargo test`＋模擬で収量/分散を検証、`gse-replay --snapshot` byte-equal。`hmm-analysis`/`rust-standards`/`architecture-rules` 参照。
- **T2 提出ラッパー（CLI 手打ち排除）**: `~/Documents/GSE-sessions/` の**最新 NDJSON を自動検出**→同梱 pubkey で `.age` 化するダブルクリック実行物（mac/Win）。`gse-package` ロジックを再利用。**匿名化保証（VK→KeyCategory・本文非保存）は不変**を確認（`data-privacy`）。
- **T3 ファイル名 実名漏れ対策**: Dropbox File Request が投稿者名を付与し `.age` ファイル名に実名が残る（中身は匿名化済）。提出時に名前を出さない設定 or 受領側で P### にリネームする手順を `participant-setup-guide.md`/`pilot-runbook.md` に明記。`data-privacy` 観点で SSOT 化。
- **T4 self-marker 導線**: 教示文・UI ヒントを `participant-setup-guide.md`＋（必要なら）frontend に追加。`intervention-design`/`typescript-standards`。
- **T5 docs（バージョンカット & 記録）**: `preregistration-v0.3.md` に「**リリース版(0.3.0 release)=shakedown / M0 凍結ビルド=confirmatory**」のカットを**前向き宣言**。`experiment-tracking.md` に P006=researcher test・P007=shakedown を記録。`research-positioning.md §6/§8` の M0/GATE2 ラベル収量前提を更新。出典は `citation-ssot`。

## 4. M0 凍結 & 再走
- T1〜T5 を**1 本のクリーンビルド＋運用**に束ね、frozen を宣言（CI 本番バイナリ＝配布の単一真実源を維持。debug フラグ既定 OFF の盲検を壊さない）。
- **P007（実参加者）を confirmatory として再走**。P006 は researcher test として扱う。リリース版 2 提出は shakedown 格付け（M1 配線・IME 健全性・UI 確認には使える）。

## 5. 制約・完了基準
- 純ロジック維持・seed 決定性・`analysis/` は OS API 非依存。`data-privacy`: プローブに本文/タイトルを載せない・匿名化保証維持。**生 NDJSON / `.age` 中身は外部 LLM 送信禁止**（Codex 入力にも入れない）。
- **T0 落合カード ≥2 本**作成・`_index` 追記・`references.md`(V) append、§2 の数値判断に T0 を引用（裏取り不能な値は概算と明示）。
- `cargo test --workspace` ＋ `gse-replay --snapshot`（byte-equal）が通る。
- **検証フェーズのコミット流儀**: 対象ファイルを**列挙して add**（`-A` 禁止・`.codex/budget.json` を混ぜない）。MEMO の方針に従う。
- code-reviewer ＋ `/cross-review`（自己ブロック回避はメモリ [[cross-review-codex-self-block]] 参照＝絞った diff を `bash scripts/secrets-filter.sh` 経由で手動 codex）→ commit → `/finish-task`。

## 6. 順序メモ
- これは smoke test（`.steering/20260627-pilot-smoke-verify/handoff-next-session.md` の残 A〜E）**の前**＝M0 凍結。凍結後に smoke→pilot。実機操作はユーザーが担当、エージェントは手順提示・ログ解析・コード修正。
- **empirical-prompt-tuning（.claude skills/commands 改善）は別トラック・後続**。本タスクに混ぜない。
- 直近 merge: probe スケジューラ枯渇是正＋落合サーベイ（**PR #56**・branch `fix/probe-scheduling-spread`）。層語彙 probe timing=L0 較正データ源 / opportunity 合わせ=L2' 介入機会 は確定済み（`docs/literature/20260628-probe-timing-interruptibility.md`）。
- 実データ所見（P006=8.1分/0件 ・ P007=37.2分/3件@7.0・28.4・37.2/21分drought）は本タスクの一次根拠。生データはコミットしない。
