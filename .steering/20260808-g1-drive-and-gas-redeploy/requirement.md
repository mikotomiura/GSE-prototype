# 課題ページの差し替えと GAS 再配備

## 背景

2026-08-08 に **課題ページのゲート化と事前開示の撤回**（第 11 版）を
`.steering/20260808-g1-start-gate-and-predisclosure-withdrawal/` で完了し、
`b49685d` としてコミットした。

⚠️ ★ **repo は直ったが、外界（Drive の 15 フォルダ・GAS・G1-S フォーム）は古いままである。**
外界を repo に追いつかせるのが本タスクである。

引き継ぎ元: `.steering/_handoff/next-session-prompt-g1-drive-and-gas-redeploy.md`

## ゴール

| | 内容 |
|---|---|
| A | Drive の 15 フォルダ（全 150 ファイル）を新版に差し替え、byte 照合が緑になってから共有し直す |
| B | GAS を再配備し、`buildPostSurveyForm()` だけを実行して G1-S の `Q_S_PREREAD` を作り直す |
| C | 「登録 → メール受信 → 展開 → 起動 → 1 ブロック → 提出」を P015 で実働検証する |

## 受け入れ条件

- [ ] A-1: Drive の古い 15 フォルダが消え、`dist/_drive` の 15 フォルダに置き換わっている
- [ ] A-2: 15 フォルダすべてで `verify-drive-upload.py` が緑（byte 一致）
- [ ] A-3: 15 フォルダそれぞれが「リンクを知っている全員（閲覧者）」／親フォルダは制限付きのまま（D-7）
- [ ] B-1: `buildPostSurveyForm()` が完了し、G1-S の `Q_S_PREREAD` が「当日より前に押して中を見たか」になっている（`§2.12-4`）
- [ ] B-2: `FORM_ID_SURVEY` が固定 ID のままで、配布済み URL が変わっていない
- [ ] B-3: `checkMaterialsProvisioning()` が 15 件緑
- [ ] C-1〜C-6: 引き継ぎ `§5` の 6 項目

## 事前検証（★ A の前に前倒しで実施・完了）

引き継ぎ `§2` の「⚠️ 確かめていない」のうち、**アップロード前なら安い**ものを先に潰した。
結果は `decisions.md` / 完了報告に記す。

## やらないこと

- ⚠️ `setupG1Forms()` の実行（`buildConsentForm()` の `clearForm()` が G1-C の同意記録を壊す）
- ⚠️ 事前開示（第 8 版）の復活。第 11 版の撤回は凍結済み
- ⚠️ `git push`（deny 設定）
