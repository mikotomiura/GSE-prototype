# M0 凍結：較正ラベル収量の是正 ＋ 提出摩擦の排除

## 背景

リリース版（HMM 0.3.0）の pilot 2 提出を実データ復号・定量した結果、GATE2（有効ラベル ≥20 件/人）を桁違いに下回った。

- **P006＝研究者自身のテスト**: 8.1 分・random-probe 発火 **0 回**・有効ラベル **0 件**。
- **P007＝実参加者**: 37.2 分・発火 3 回 @ 7.0 / 28.4 / 37.2 分（7→28 で **21 分 drought＝枯渇バグ署名**）・有効 **3 件**・self-marker **0**。

原因は複合的:
1. (i) probe 枯渇バグ【PR#56 で修正済】
2. (ii) **較正の発火レートが低すぎてラベル収量不足**（λ=2/30分では 20 件/人 ≈ 5〜6 時間/人で非現実的）
3. (iii) **self-marker 未使用**（参加者起動ラベルが 0）
4. (iv) **提出が CLI＋パス手打ちで参加者に不可能**
5. (v) **`.age` ファイル名に実名が漏れる**（Dropbox File Request が投稿者名を付与）

被験者 pilot の**取り直しの効かないデータ**を集める前に、(ii)〜(v) を 1 本のクリーンビルド（M0 凍結）＋運用に束ね、P007（実参加者）を confirmatory として再走できる状態にする。

## ゴール

(ii)〜(v) を是正し M0 を凍結。リリース版データは shakedown に格下げ、prereg にバージョンカットを前向き宣言する。コード（Rust 較正プロファイル）＋ツール（提出ラッパー）＋docs（prereg/ガイド）の混合タスク。

## スコープ

### 含むもの
- T0: 落合フォーマット軽量サーベイ（較正密度・within-person サンプルサイズ・compliance）→ §2 数値根拠
- T1: 較正専用 ProbeConfig プロファイル（Rust）
- T2: 提出ラッパー（最新 NDJSON 自動検出→.age 化、CLI 手打ち排除）
- T3: `.age` ファイル名 実名漏れ対策（docs/運用 SSOT）
- T4: self-marker 導線改善（教示・UX）
- T5: docs バージョンカット宣言（prereg / experiment-tracking / research-positioning）
- M0 凍結宣言 ＋ P007 confirmatory 再走準備

### 含まないもの
- smoke test（`.steering/20260627-pilot-smoke-verify/` 残 A〜E）＝本タスク（M0 凍結）の**後**
- empirical-prompt-tuning（.claude skills/commands 改善）＝別トラック・後続
- 非侵襲レート（Phase2 配備用プロファイル）の本実装＝較正プロファイルと分離設計のみ確認
- 実機操作（ユーザー担当。エージェントは手順提示・ログ解析・コード修正）

## 受け入れ条件

- [ ] T0 落合カード ≥2 本作成・`docs/literature/_index.md` 追記・`docs/references.md`(V) append、§2 数値判断に T0 を引用（裏取り不能な値は概算と明示）
- [ ] T1 較正 ProbeConfig プロファイル追加・seed 決定性・引数注入・純ロジック維持・収量/分散を模擬検証
- [ ] T2 提出ラッパー（mac/Win ダブルクリック）・匿名化保証（VK→KeyCategory・本文非保存）不変
- [ ] T3 実名漏れ対策を participant-setup-guide / pilot-runbook に明記（data-privacy SSOT）
- [ ] T4 self-marker 導線を教示/UI に追加
- [ ] T5 prereg バージョンカット前向き宣言・experiment-tracking 記録・research-positioning §6/§8 更新
- [ ] `cargo test --workspace` ＋ `gse-replay --snapshot`（byte-equal）が通る
- [ ] code-reviewer ＋ /cross-review → commit → /finish-task

## 関連ドキュメント

- `docs/preregistration-v0.3.md`（PreReg-2/-3 の GATE2 測定法）
- `docs/research-positioning.md §5/§6/§8`（GATE2/3・WBS M0-M5・成功基準）
- `docs/participant-setup-guide.md` / `docs/pilot-runbook.md` / `docs/experiment-tracking.md`
- `docs/literature/20260628-probe-timing-interruptibility.md`（既存 probe-timing サーベイ [V18]-[V23]）
- `src-tauri/src/analysis/probe_scheduler.rs`（PR#56 で導入済 soft max-gap）

## 運用メモ
- /reimagine 適用: No（個別トラックは方針明確。ただし §2 の較正レート設計は T0 所見＋power 観点で数値確定してから T1 着手）
- 理由: タスク全体の設計は next-session-prompt.md で確定済み。各トラックは独立で実装案も比較的自明。較正レートのみ数値の根拠付けが必要だが、これは /reimagine（案の破壊再生成）ではなく T0 サーベイで対応する。
