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
- [x] `code-reviewer` ＋ `security-checker` を並列起動（2026-09-09）
- [x] HIGH 指摘への対応（⚠️ backlog へ punt しない・両者独立に一致した `mitou_docs/` 漏れを含め全 3 件消化）
  - [x] HIGH（両者一致）: `docs/mitou_submission/mitou_docs/`（提案書/技術設計書/検証レポートの
        `.docx`/`.docx.md` 置き場）が `deck-assets` 規則から漏れ、`.md`/`.svg` 等が rc=0 で素通り
        → 規則に追加 ＋ `docs/external-skills.md` 表を同期 ＋ 回帰テスト2本追加
  - [x] HIGH（security-checker）: `.env`/`.pem`/`.key` の境界 `([[:space:]]|$)` が狭く
        `.env.local`/`.env.production`/`.pem.bak`/`.key.pub` が素通り → `.ndjson` と同じ
        `([^a-z0-9]|$)` 境界へ統一 ＋ 回帰テスト4本追加
  - [x] HIGH（code-reviewer・security-checker 双方が別角度で指摘）: `secrets-filter-test.sh`
        （70ケース）が CI で一度も実行されていなかった → `check` ジョブ（Win/mac 両方）に追加
  - [x] 副次: proprietary 拡張子 `(\.md)?` が1段しか許さず `deck.pptx.gz`/`.txt`/`s.docx.md.bak`
        が素通り（security-checker 実測）→ `(\.[a-z0-9]+)*` へ拡張 ＋ 回帰テスト3本追加
  - MEDIUM/LOW は次回タッチ時へ繰り越し（`decisions.md` 参照）: report の非ASCII値
        未置換の誤表示・非 `diff --git` 入力での skip 解除漏れ・diffstat/rename 行の
        パス流出・awk 実装差の自己診断
- [x] 全 70 ケース再検証（`bash scripts/secrets-filter-test.sh` → 全緑）
- [x] ★ Codex の第二意見（⚠️ **生 diff は渡せない** —— フィルタ本体は自分のファイル名で
      hunk ごと除去されるため。★ `run-codex-consult.sh` に要点テキストで相談した）
- [x] `/finish-task`（Step3: `run-codex-review.sh` を再実行し rc=2 で自己遮断を再確認 →
      Claude 単独 (code-reviewer+security-checker) へ縮退。schema parity check は対象外で skip）

## ★ 研究者の判断（★ 2026-09-08 に確定）
- [x] ★★★ **`.pptx.md` / `.docx.md` を送信禁止に含める**（→ `decisions.md` 判断 2）
- [x] ★ `docs/external-skills.md` の「拡張子フィルタは不要」を実態に合わせて訂正（判断 3）
- [x] ★ `daily_token_budget` は **300000 のまま**（★ 研究者裁定・判断 4）
- [x] ★★★ `.svg` など本文を持つ別形式は **置き場で塞ぐ**（★ 案 C・判断 7）
