# G1 モードの残タスク — follow-up 3 件 / Windows 検証の準備 / 配布手順の確定

## 背景

2026-08-05 に G1 モード (第 1 段＋第 2 段・`preregistration.md` 第 10 版) を実装し、
`feature/g1-app-mode-and-log-rotation` に 4 コミットで入れた。実装とレビュー
(code-reviewer / security-checker / `/cross-review`) は着地しているが、
`.steering/_handoff/next-session-prompt-g1-followups.md` が 3 つの残件を明示している。

⚠️ ★ **実装をやり直さない。** 前セッションの成果は緑で着地している
(`cargo test --workspace` 277 / `--features package` 269 / golden replay 4 本 /
`emit_schema` byte-equal / `tsc` 緑 / `run.sh` GREEN / 実機 2 ブロック通し確認済み)。

## ゴール

| # | 何 | このセッションでの到達点 |
|---|---|---|
| 1 | Windows 検証 | ⚠️ **実機は触れない** (この環境は macOS)。★ 研究者判断で **CI で Windows ビルドを作るところから**。検証手順書を成果物として残し、実行できたところまでを「やった / やっていない」で書き分ける |
| 2 | 配布の署名・公証 | ★ **研究者判断で案 A (現状維持・ad-hoc 署名) に確定**。→ 被験者が Gatekeeper を越える手順を配布文書に明記する |
| 3 | follow-up 3 件 | コード修正 3 件 (下記スコープ) |

## スコープ

### 含むもの

- **F-1**: 二重起動の検査が起動 1 回だけ (code-review M6)。
  → ★ **測ってから入れる** (`start_session` の応答時間に子プロセス起動が載る)
- **F-2**: `start_session` が `log.lock()` を関数末尾 (`win.show()`) まで保持している (LOW)。
  → `guard` のスコープを縮める
- **F-3**: 止められた 2 個目のプロセスが空の NDJSON を作ってから死ぬ。
  → ★ 本筋は `SessionLogger::start` を single-instance 判定の後ろへ動かすこと
- **W-1**: Windows 検証手順書 (`§1` の 6 項目) の作成
- **W-2**: CI での Windows ビルド生成の段取り
- **D-1**: 配布手順 (案 A 確定) の文書反映 — Gatekeeper 初回回避の明記

### 含まないもの

- ⚠️ ★ **他の producer (self-marker / user_label / intervention_response) への session ゲート追加**
  — `decisions.md` R-9 で「直さない」と根拠つきで決めた。★ **蒸し返さない**
- 案 B / 案 C (Apple Developer Program / 機関公証) の手続き — ★ 研究者が案 A で確定した
- `preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` の変更 (★ 凍結)
- 判定基準の変更 (`§2.3` を含む)

## 受け入れ条件

- [ ] F-1 / F-2 / F-3 が「入れた」か「測った上で入れなかった」かのどちらかで決着し、根拠が残る
- [ ] Rust を触った場合: `cargo test --workspace` 緑 / `gse-replay --snapshot` golden 緑 /
      `emit_schema` byte-equal / `npx tsc --noEmit` 緑
- [ ] ★ **検査を足したら、その場でわざと壊して赤を実測する** (後回しにしない)
- [ ] `bash run.sh` が GREEN に戻る。各 `--selftest` が緑
- [ ] Windows 検証手順書が「操作 → 何を見る → 記録欄」の形で存在する
- [ ] 配布文書 (案 A) に Gatekeeper 初回手順が入っている
- [ ] ★ 実測していないことを「実測していない」と書いてある

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-g1-followups.md` (このタスクの入口)
- `.steering/20260805-g1-app-mode-and-log-rotation/decisions.md` R-7 / R-8 / R-9
- `.steering/20260805-g1-app-mode-and-log-rotation/tasklist.md` §9 / §10
- `docs/architecture.md` §4.12 (`g1`) / §4.7 (logger ローテート)
- `experiments/20260801-controlled-friction-task/protocol.md` §1 / §1.1 / §4.4
- `experiments/20260801-controlled-friction-task/preregistration.md` 第 10 版 / §5.4-5 / §5.4-6

## 運用メモ

- /reimagine 適用: **No**
- 理由: 設計判断は前セッションで確定済み (D-6 / D-7 / R-1〜R-9)。本タスクは
  「決まった方針の残作業」であり、複数案が競合する局面ではない。
  ★ ただし **F-1 は「測ってから決める」** ので、測定結果次第で入れない判断もありうる。
