# 設計

## 実装アプローチ

一次に戻す（memory「古い記述は新しい方に揃えるのでなく一次へ戻す」）。各所で旧文を消さず、訂正の日付と旧文を添えて
「アプリを問わない公開の経路は見つかっていない。アプリが用意する Accessibility の経路はあり、WebKit は出す
（AppKit の NSTextView が出すかは未確認）」に直す。設計の結論（macOS は打鍵から推す）は変えない。

一次（このセッションで取り直して確かめた・2026-10-05）:

1. Apple の文書の JSON（`https://developer.apple.com/tutorials/data/documentation/appkit/nsaccessibility-swift.struct/{attribute,notification,parameterizedattribute}.json`）:
   `init(rawValue:)` を除くと属性 131・通知 42・パラメータ付き 18。`textInputMarkedRangeAttribute` と
   `NSAccessibilityTextInputMarkingSessionBegan` / `…Ended` があり、3 つとも `introducedAt` は macOS 10.6、`abstract` は無い。
2. C の定数（`…/applicationservices/carbon_accessibility/{attributes,notifications,parameterized_attributes}.json`）:
   101・25・9。変換を表すものは無い（語 mark に当たるのは `kAXMenuItemMarkCharAttribute` だけ）。
   パラメータ付きに `kAXStringForRangeParameterizedAttribute` がある（範囲から文字列を読める）。
3. WebKit（commit `1a5a134d14845e9bf54a67049a36a2585e62897c`・raw で取得・SHA-256 は IME 論文の枝の [V206] の記録と一致）:
   `AXObjectCacheMac.mm` 361〜366 行・`WebAccessibilityObjectWrapperMac.mm` 2290〜2295 行。

[Vn] の扱い: [V206]・[V224]・[V225] は IME 論文の枝（未 merge）で登録されている。`check_citations.py` は `docs/` を走査するので、
`docs/` の文書には番号を書かず URL と文書名で引く（制約 7 の既存の書き方と同じ）。番号は `.steering/` の調査メモにだけ「IME 論文の枝で登録」と添える。

## 変更対象

### 修正するファイル
- `docs/agent-shared.md` — 技術的制約 7 の末尾（括弧の中の言い方 ＋ 訂正の 2 行）
- `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` — §3.2 の表の macOS のセル・§7.5（見出し・訂正の注・C と AppKit の行を分け、WebKit の行を足す）・§7.6（非対称はアプリを問わない経路のことだと注）
- `docs/architecture.md` — macOS 固有の設計判断の「IME 状態機械」の理由の文
- `src-tauri/src/input/ime_compose.rs` — モジュールの doc コメントの 1 文（振る舞いは変えない）

### 新規作成するファイル
- `.steering/20261005-macos-ax-marked-text-correction/` の requirement / design / tasklist / decisions

## 影響範囲

コメントと文書だけ。コードの振る舞い・スキーマ・`capabilities` は変えない。

## 既存パターンとの整合性

制約 7 の 2026-08-22 の訂正と同じ形（旧文を示し、何が誤っていたかと結論が変わるかを書く）。

## テスト戦略

- `python scripts/check_citations.py`（違反なし）
- `cargo fmt --check`（`ime_compose.rs` のコメントの変更）
- grep で、直した文書に「公開 API が存在しない」が訂正の印つきの旧文としてだけ残ることを確かめる

## ロールバック計画

この枝の commit を revert する。
