# debug-force-wall (デバッグ用 Wall 強制トリガー)

## 背景

調査 (前タスク) で、Wall 発動は「p_stuck≥0.70 を30s累積 (= 高 friction: 修正/BS/低速打鍵) かつ
opportunity≥0.45 (= 2-8秒の短い休止)」の **2 条件同時**が必要と判明。p_stuck は到達可能だが
条件が狭く、実機で Wall を意図的に出すのが難しい。このため:
- A2 (介入応答=Wall 解除の NDJSON 捕捉) の検証ができない。
- probe-card-ui の Wall 全画面維持の検証ができない。
- Wall→QR→スマホ解除→A2 捕捉 の end-to-end 動作確認ができない。

## ゴール

**dev/較正モードから Wall を即時に強制発動**でき、HMM と切り離して
Wall→QR→スマホ解除→A2 `intervention_response` 捕捉 の全経路を検証できるようにする。

## スコープ

### 含むもの
- backend: `force_wall` Tauri コマンド + `FORCE_WALL` フラグ。`get_intervention_decision` が
  これを消費して action=wall の決定を返す (両ウィンドウが既存 polling で wall を拾う)。
- frontend: Dashboard に **較正モード時のみ表示**するデバッグボタン「Wall 強制発動」。
- 強制 wall の decision は `reason="debug_force"` でログ → 解析時に除外可能。

### 含まないもの
- HMM の閾値/emission/transition 変更 (別タスク・要設計判断)。`HMM_VERSION` 不変。
- Wall/Zen/解除の挙動変更 (発動経路の追加のみ)。
- schema 変更 (reason は既存 String・新カテゴリ不要)。

## 受け入れ条件

- [ ] 較正モードのデバッグボタンで Wall が即発動し、QR→スマホ解除→A2 捕捉まで通る
- [ ] 強制 wall は `reason="debug_force"` でログされ通常判定と区別できる
- [ ] 通常 (ボタン非押下) では一切挙動が変わらない (pilot 非汚染)
- [ ] `cargo test --workspace` 緑・`--snapshot` byte-equal (HMM 不変)・tsc+vite build 緑
- [ ] code-reviewer / cross-review で CRITICAL/HIGH なし

## 関連ドキュメント
- 調査結果: [[project-wall-not-idle-trigger]] / `analysis/intervention.rs` (decide 条件)
- Skill: `intervention-design` / `rust-standards` / `typescript-standards`
- 別 PR (feature/debug-force-wall・main 基点)。A2(#20)・probe-ui(#21) と独立。

## 運用メモ
- /reimagine 適用: No (小規模・debug 経路追加。設計は backend フラグ + polling 再利用で自明)
