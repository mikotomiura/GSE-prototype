## 背景

CPU の内訳で、記録中の増分の大部分は画面の 500ms ごとの取得と見立てた（相関）。確かめると、取得を全部止めても記録中の合計は約 0.5 ポイントしか下がらなかった。本当の使い手は画面のタイマーによる描き替え（主に 1 秒ごとの経過秒の表示）だった。

## 変更点

- `App.tsx` の統合ポーリングから使っていない分を削った。overlay は判定の結果だけを取る。O1 の主窓は見える間だけ無打鍵の時間を取り、見えない間は何も取らない。通常運用と G1 の主窓は、見えない間だけ表示用の 2 本を取らない。
- 主窓の `get_intervention_decision` は介入の判定を進める時計なので、通常運用と G1 では見えなくても呼ぶのを止めない。介入の振る舞いは変えていない。

## 検証

- 一時的な計装で呼び出しの回数を数えた（O1 の主窓は 0 回、通常運用で最小化すると表示用が 0 回で判定は続く）。
- CPU の測り（直す前・取得を全部止めた版・直した版）と、タイマーを間隔ごとに止める測りは `.steering/20261031-trim-ui-polling/results.md`。
- `tsc` 緑。Rust は変えていない。

## レビュー

code-reviewer・/cross-review（Codex）とも HIGH なし。採ったのはコメントの 2 点（判断 3）。

## 残り

- 通常運用で窓を最小化すると、WebKit の間引きで介入の判定が 1 秒に 1 回になる（既存の振る舞い）。Windows の WebView2 は未確認。

Refs: .steering/20261031-trim-ui-polling/

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01BUBYRxTQSivZDKJTppgVtQ
