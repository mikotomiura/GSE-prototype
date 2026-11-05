# 設計: 打鍵の外の信号を持つ公開データの調べ

## アプローチ
`/literature-review` の 1 ラウンドとして回す。下位問いは §3 の対象ごとに割る（証拠の種類が対象ごとに違うため）。
- Q1 ポインタの連続した動き ＋ 打鍵
- Q2 ウィンドウ・アプリの切り替え ＋ 打鍵
- Q3 自己申告（詰まり・フラストレーション・作業の状態）＋ 打鍵
- Q4 1 人あたり長い・セッションが多い打鍵
- Q5 日本語 IME の変換の過程（新しい候補があるかだけ）

探索は angle ごとに general-purpose（model: sonnet）へ並列で渡す。Q1〜Q4 は 1 本ずつ、Q5 は短く 1 本。反証 angle（「無い」ことの確認・利用条件で使えない例）を各依頼に含める。references.md への登録はメインが直列で行う。断定に使う利用条件（ライセンス・同意の範囲）はメインが一次のページで確かめる。

## 変更対象
- `docs/literature/20261102-public-data-beyond-keystrokes.md`（新規）
- `docs/references.md`（追記）
- `docs/literature/_index.md`（1 行）
- `.steering/20261102-gse-public-data-signal-survey/`

## テスト戦略
- `python3 scripts/check_citations.py` を違反なしまで
- 利用条件の断定はメインが一次で確かめた候補だけに付ける。確かめていないものは「未確認」と書く
