# 設計 / 調査結果

## アプローチ
コード変更なし（前タスク #1 層2 はマージ済み）。本タスクは
(1) 機械的検証、(2) 実機スモーク手順書化、(3) advice.md 3 issue への回答。

## 機械的検証結果（main / 2026-06-25）
| 検証 | 結果 |
|---|---|
| `cargo test --lib` | ✅ pass |
| `gse-replay --snapshot tests/snapshots/minimal.json` | ✅ pass（HMM 不変） |
| `tsc --noEmit` | ✅ pass |

## advice.md issue 1: dev/被験者で初期 Dashboard が変化しない → **設計通り・問題なし**
`src/components/Dashboard.tsx` の gate:
- `debugView = import.meta.env.VITE_GSE_DEBUG === "1"`（190 行）
- `showModelOutput = !calibrationMode && debugView`（195 行）

dev と被験者で**変わるのは VITE_GSE_DEBUG gate の 2 点だけ**:
1. デバッグボタン 3 種（force_wall / debug_force_probe / force_nudge、522-560 行）
2. モデル出力（推定状態/確率/GT/状態説明）= `showModelOutput`（第2週かつ debugView 時のみ）

それ以外（初期 Dashboard の内容・UI）が **dev と被験者で同一なのは意図的**:
Phase1 較正は被験者・研究者とも同じ **minimal blinded dashboard**（v0.4 §5.2）を見ることで
アンカリングを排除する設計。第1週（`calibrationMode=true`）は **debugView でも常時ブラインド**。
→ 「初期 Dashboard が変化しない」は正しい挙動。**確認方法**: 研究者デバッグ時に
`VITE_GSE_DEBUG=1 npm run tauri dev` で起動すれば 3 ボタンが出る。出ないならフラグ未設定が原因。

## advice.md issue 2: 被験者の起動方法 → `launch-method-decision.md` 参照
推奨 = **A（CI 本番バイナリ）＋ C（初回研究者同席）**。codex consult 一致。ユーザー確定待ち。

## advice.md issue 3: 事後アンケート GAS → **コードは既に実装済み**
`Form_Phase1/GSE_Phase1_Form_Builder.gs` の `buildF5()`（508 行〜）が事後アンケート:
- P-ID、一般性自己効力感（GSE-10 公式版・F2-B と byte 一致）、作業再開感・自己調整感
  （F2-C と matched 4 項目）、GSE 利用体験・継続意向、NASA-TLX short、総括（プライバシー不安）。
- 固定フォーム ID `openById(F5_FORM_ID)` ＋ 再実行時 `CLEAR_EXISTING` で重複防止。
- `buildAllSupportForms()`（651 行〜）で F2-F5 一括生成。
- 前タスク `20260624-phase1-form-survey-design` #D まで完了（FD9）。コミット済（0d1b2d8 / 4dd93ff）。
→ **残るは研究者の Apps Script 実機確認のみ**（`buildAllSupportForms` 実行 → 不適格分岐の送信終了・
  メール非収集・F5 が openById 固定フォームに投入を確認）。新規 GAS 作成は不要。

## follow-up 候補（codex 由来・未着手）
launch-method-decision.md の「codex が指摘した盲点」1-4 を参照。
特に #1 first-run self-check・#2 ログ堅牢化（fsync/heartbeat/異常終了検出）は Phase1 配布前に
着手するか Phase2 送りか、ユーザー判断。
