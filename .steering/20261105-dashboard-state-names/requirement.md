# dashboard-state-names —— 被験者向けの注意書きから 3 状態の名前と「推定状態」を外す

## 背景

ADR-046 D1 は、3 状態（Flow / Incubation / Stuck）の名前を、研究の主張・被験者が見る画面・新しい文書の地の文で、推定した状態の名として使わないと決めた。Migration 6 が `src/components/Dashboard.tsx:492-493` の被験者向けの文の直しを別タスクにしていた。

確かめたこと（origin/main `be9f14de`・2026-11-05）:

- 被験者が見る画面で名前が出るのは `Dashboard.tsx:492-493` の注意書き 2 文だけ（O1 のモードと較正のモード）。
- 確率の帯・`Current State`・GT の数・英語の説明の文は `showModelOutput = !calibrationMode && debugView` のときだけ出る。`debugView` は `VITE_GSE_DEBUG === "1"` で、`.github/workflows` にこの変数を設定する行は 0 件。配布のビルドでは出ない。
- 「推定状態」の語は、スタート画面の週の説明 `src/App.tsx:118`（O1 以外のモードで表示）にもある。
- トレイの文は `src-tauri/src/tray.rs` のテスト `tray_labels_never_leak_cognitive_state` が状態名を禁止語にしている。
- O1 の同意フォーム（`Form_O1/GSE_O1_Form_Builder.gs:593`）は記録するものを「『作業の状態』の推定値」と書く。G1 の同意フォーム・`docs/participant-setup-guide.md`・O1 の配布の readme には状態名も「推定状態」も無い。

## ゴール

被験者向けの文を研究者が選んだ案 A（「推定の結果」）に直し、同じ語が戻ってきたら CI が赤になるようにする。

## スコープ

### 含むもの
- `Dashboard.tsx:492-493` の 2 文を案 A に直す。
- `App.tsx:118` の「推定状態も非表示」を「推定の結果も非表示」に直す。
- `docs/functional-design.md:249` の注を、確かめた結果で書き直す。
- `scripts/check_doc_lexicon.py` に、`src/` の日本語の文（コメントを除く）に 3 状態の名前・その片仮名・「推定状態」が無いことの検査を足す。

### 含まないもの
- O1 の配布物の作り直し（O1 は終了間近。直した文は次の配布から出る）。
- 同意フォームの文の変更。
- G1 の研究の説明（「作業がどれくらい詰まっているか」・G1 の契約）。
- 開発ビルドだけの確率の帯・英語の説明の文。
- 自己マーカーの「今とても詰まっている」ボタン（推定の名ではなく自己申告なので D1 の対象外）。
- コメント中の名前（地の文の直しは ADR-046 Migration 5 の別タスク）。

## 受け入れ条件

- [ ] 直す前の `python3 scripts/check_doc_lexicon.py` が 3 件（Dashboard 2・App 1）で exit 1 になる（陽性対照）。
- [ ] 直した後は exit 0。
- [ ] `npx tsc --noEmit` が緑。
- [ ] 画面で注意書きの文を見て確かめる（O1 のモード）。

## 関連ドキュメント

- `docs/adr/ADR-046-mhd-rethink-names-label-per-person.md` D1・Migration 6
- `.steering/_handoff/next-session-gse-m5-plan-and-dashboard-names.md` §2

## 運用メモ
- /reimagine 適用: No
- 理由: 文は研究者が案 A に決め、変更は文字列 3 か所と注 1 か所で設計の分かれ道が無い。

## バグの再現・期待・実際（/fix-bug Step 2）

- 再現: 配布のビルドを O1 のモード（または較正のモード）で起動し、ダッシュボードの注意書きを読む。O1 以外ではスタート画面の週の説明も読む。
- 期待: 被験者が見る文に 3 状態の名前も「推定状態」も無い（ADR-046 D1）。
- 実際: 「推定状態 (Flow / Incubation / Stuck) は表示していません。」と出る。スタート画面は「推定状態も非表示」。
- 原因: ADR-046（2026-11-05）より前に書いた文がそのまま残っている。Migration 6 が直しを別タスクにしていた。
- エラー・ログ: 無い（文の問題）。
