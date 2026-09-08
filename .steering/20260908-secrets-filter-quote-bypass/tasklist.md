# タスクリスト

## 調査
- [x] ★ `secrets-filter.sh` を一次で読む
- [x] ★ 消費者を洗う（`run-codex-review.sh` / hooks / codex-* Skill / `loop-issue`）
- [x] ★ **陽性対照つきで再現**（★ ①実物 rc=0 / ②ASCII 名 rc=2 / ③引用符つき rc=0）
- [x] ★ `core.quotepath` を確認（★ 未設定＝既定 true → **常に引用符が付く**）

## 実装
- [x] ★ **回帰テストを先に足して、赤くなることを確かめた**（★ 6 件 NG）
- [x] ★ ヘッダ行の正規化（引用符 → 空白）
- [x] ★ proprietary 拡張子の終端を `([[:space:]]|$)` へ
- [x] ⚠️ 陰性対照を足す（★ 引用符つきの普通の `.rs` / `.md`・`.keyboard.rs` の誤爆防止）

## テスト
- [x] ★ `bash scripts/secrets-filter-test.sh` → **rc=0 / 全 32 ケース**
- [x] ⚠️ **実物の diff で再実測**（★ 合成で済ませない）
- [x] ⚠️ 陰性対照: 実験 diff 2130 行が **1 バイトも変わらない**

## レビュー / 完了処理
- [ ] `code-reviewer` ＋ `security-checker` を並列起動
- [ ] `/cross-review`（★ **Codex 使用の許可あり**・⚠️ パス限定）
- [ ] `/finish-task`

## ★ 研究者の判断（★ 2026-09-08 に確定）
- [x] ★★★ **`.pptx.md` / `.docx.md` を送信禁止に含める**（→ `decisions.md` 判断 2）
- [x] ★ `docs/external-skills.md` の「拡張子フィルタは不要」を実態に合わせて訂正（判断 3）
- [ ] ⚠️ `daily_token_budget` を 300000 のままにするか 200000 へ戻すか（判断 4）
