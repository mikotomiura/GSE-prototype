# macos-ax-marked-text-correction

## 背景

GSE 本体の文書は「macOS には他プロセスの IME 変換状態を観測する**公開 API が存在しない**」と書いている
（`docs/agent-shared.md` 技術的制約 7 の末尾・調査メモ `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §3.2・§7.5・§7.6）。
根拠は調査メモ §7.5 の「Accessibility の全定数 135 個を全数確認してゼロ」だった。

IME 論文の §3 を書くために Apple の一次文書を取得したところ（2026-10-05・IME 論文のタスクの判断 151・153）、
その 135 個は **C（Carbon）の Accessibility の定数**（属性 101・パラメータ付き 9・通知 25）だけで、
**AppKit の定数**（属性 131・パラメータ付き 18・通知 42）を見ていなかった。AppKit には
`textInputMarkedRangeAttribute`（変換中の範囲）と `NSAccessibilityTextInputMarkingSessionBegan` / `…Ended`
（変換の開始・終了）がある（3 つとも macOS 10.6 から・説明の文なし）。WebKit のソースはこの 2 つの通知を出し、
変換中の範囲を位置と長さで返す。→ 「公開 API が存在しない」は一次が支えるより広い。

研究者の選択（判断 151-2・2026-10-05）: GSE 本体の文書は論文の枝に混ぜず、別の小さなタスクで一次に戻して直す。

## ゴール

GSE 本体の現行の文書が、macOS の IME 変換の観測可能性を一次の文書が支える範囲で書いている状態にする:
「アプリを問わない公開の経路は見つかっていない。アプリが用意する Accessibility の経路はあり、WebKit は出す
（AppKit の NSTextView が出すかは未確認）」。

## スコープ

### 含むもの
- `docs/agent-shared.md` 技術的制約 7 の末尾（★ Codex も読む共通文書なので最小の変更）
- 調査メモ `survey-input-channels.md` §3.2・§7.5・§7.6（一次に戻す・旧記述は訂正の印で残す）
- 同じ主張を現行の説明として持つ消費者（grep で洗う）のうち、ADR 本文・過去の記録・凍結物でないもの

### 含まないもの
- ⚠️ 設計の結論（macOS は打鍵から推す）を変えること —— 変えるかは研究者
- ⚠️ 凍結物（IME 論文の事前登録・凍結のタグ）・ADR の本文（書き換えない規約）・過去の作業記録（その時点の記録）
- AppKit の経路を実装・計測すること（新しい信号は ADR-013 D1 の記録仕様の変更）
- Windows 側の UIA TextEdit パターンの記述（このタスクは macOS の言い過ぎだけを直す）
- `docs/references.md` への登録（[V206]・[V224]〜[V229] は IME 論文の枝で登録済み・main には未 merge）

## 受け入れ条件

- [ ] 消費者の grep（`公開 API が存在しない`・`公開 API が無い`・`公開の API が無い`・`no public interface` など）の結果と、直す / 直さないの判断を `decisions.md` に残す
- [ ] `docs/agent-shared.md` 制約 7 の末尾と調査メモ §3.2・§7.5・§7.6 が上のゴールの言い方になっている（数は AppKit 131 / 18 / 42・C 101 / 9 / 25）
- [ ] 設計の結論（打鍵から推す）の文は変わっていない
- [ ] `python scripts/check_citations.py` が違反なし
- [ ] code-reviewer ∥ security-checker ＋ /cross-review（パス限定）

## 関連ドキュメント

- IME 論文のタスク `.steering/20260927-ime-observation-paper-eval-design/decisions.md` 判断 151・153（枝 `docs/ime-manuscript-outline`）
- `docs/references.md` [V206]・[V224]〜[V229]（同じ枝）

## 運用メモ
- /reimagine 適用: No
- 理由: 文書の事実の訂正で、設計判断を伴わない（設計の結論は変えない）。範囲と言い方は研究者が判断 151-2 で決めている。
