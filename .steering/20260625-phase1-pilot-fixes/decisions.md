# 重要な設計判断

## 判断 1: #2 第2週ダッシュボードのモデル出力ブラインド化（採用 A）

- **判断日時**: 2026-06-25
- **背景**: 第2週 (calibrationMode=false) は state-card＋3状態バー＋GT＋助言 info-box を常時表示。
  プローブは第2週 (post_intervention プール) でも発火するため、背後の常時 3 状態表示が
  プローブ回答をアンカリングする恐れ。v0.4 §5.2「Phase 1 は blind/minimal dashboard」。
- **選択肢**:
  - A: Phase 1 中は両週ともモデル出力を隠す（`import.meta.env.DEV` gate、force_wall と同方式）
  - B: 第2週を Need ベースの単一 STUCK 指標に置換
  - C: 3 状態表示のみ DEV gate（GT/info-box は残す選択も可）
- **採用**: A（ユーザー確定）
- **理由**: アンカリングを完全排除＋V2 Need 整合＋v0.4 minimal dashboard 整合。
  DEV ビルドではデバッグ用に従来表示を温存。
- **実装**: `Dashboard.tsx` に `const showModelOutput = !calibrationMode && import.meta.env.DEV;`
  を導入し、state className / kbd-status / モデル出力分岐 / info-box の 4 箇所を切替。
  blind notice（「較正モード」）は両週で再利用（Phase 1 全体が較正フェーズのため文言は妥当）。
- **トレードオフ**: 第2週でも被験者は推定状態を一切見られない（pilot バンドル）。
- **影響範囲**: `src/components/Dashboard.tsx` のみ。HMM/schema 不変。
- **見直しタイミング**: Phase 2 以降で被験者へ状態提示する設計に移る場合。

## 判断 2: #1 失敗時の挙動を「成功時のみ閉じる + カード保持 + インラインエラー + リトライ」に統一

- **判断日時**: 2026-06-25
- **背景**: 旧実装は失敗 catch で `setNudgeDismissed(false)` し、nudge effect が action=nudge のまま
  即再表示 → 「押す→消える→即再表示」無限ループ＝「反応せず出っぱなし」。ProbeCard は失敗時カード保持で
  「死んだボタン」化。
- **採用**: 両カードとも backend 成功時のみ閉じ、失敗時はカードを保持してインラインの固定和文エラーを表示し、
  ボタン再押下をリトライ手段とする。無限再表示ループ（dismissed 解除）を廃止。
- **理由**: 「較正データを静かに失わない（MNAR 回避）」意図を維持しつつ、無限ループと死んだボタンを解消。
  生エラー文字列は UI に出さず console.error のみ（data-privacy）。
- **silent 失敗時の回復経路**: silent タイマー送信が失敗した場合もカードを保持しエラー表示。
  ユーザーは手動 dismiss ボタンで再送可能（= 回復経路）。silent の自動再武装は複雑性回避のため行わない。
- **二重送信の相互排他**: 手動ボタン経路と silent タイマー経路が同時に発火し得る（code-reviewer HIGH）ため、
  `dismissInFlightRef`（useRef）で同期的に相互排他（state はタイマー closure 内で stale になるため ref）。
- **未解決**: backend 側の「なぜ try_send が毎回失敗するか」の根本修正は実機 repro のエラー文字列待ち（blockers B1）。
