# 設計

## 実装アプローチ
`src/App.tsx` の `TASK_KINDS` 配列を **論述 1 要素のみ**にし、他 3 種をコメントアウトで保持
（自己文書化・復活が trivial）。セレクタは 1 ボタン＝固定表示になる。見出しに「Phase1 は論述に固定」を明記。
型 `TaskKind`（probeTypes・4 変種）と backend は不変。既定 `taskKind="argumentative"` のまま整合。

## 変更対象
- `src/App.tsx` — `TASK_KINDS` を論述のみに制限（他はコメントアウト）＋見出し文言。

## 影響範囲
- フロントの選択肢のみ。session_meta.task_kind は引き続き `argumentative` を記録（非回帰）。
- backend・型・スキーマ・analysis 不変。

## テスト戦略
- `npx tsc --noEmit`（型）。手動: スタート画面に論述のみ表示・選択され session_meta が argumentative。

## ロールバック
- コメントアウトを戻すだけで 4 種に復帰。
