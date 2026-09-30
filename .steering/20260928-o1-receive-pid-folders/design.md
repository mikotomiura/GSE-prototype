# design — o1-receive-pid-folders

## アプローチ
- 受け口 `GSE_O1_Submit.gs`: `sanitizeName_` を通った後、`pidOfName_`（名前の先頭 `_` 区切り）で P-ID を取り、
  `pidFolder_(root, pid)` が `LockService.getScriptLock().tryLock(30s)` の中で
  `getFoldersByName(pid)` → ごみ箱を除いた最古 → 無ければ `createFolder(pid)`。ロック不可なら `{ok:false,error:"busy"}`（保存しない）。
  重複判定（`saveWithoutOverwriting_`）は P-ID フォルダの中で行う（関数自体は不変）。
- 台帳 `GSE_O1_Ledger.gs`: `o1LedgerAllFiles_(root)` = 直下 ＋ ごみ箱でないサブフォルダ 1 段のファイルを順に返す
  イテレータ。`o1LedgerSync_` / `o1LedgerCheck` の `folder.getFiles()` を置き換えるだけ（時間予算・冪等・ごみ箱ファイルの扱いは不変）。

## 変更対象
| ファイル | 変更 |
|---|---|
| `Form_O1/GSE_O1_Submit.gs` | V-3 追記・`doPost` の保存先・`pidOfName_` / `pidFolder_` / `PID_FOLDER_LOCK_MS` |
| `Form_O1/GSE_O1_Ledger.gs` | `o1LedgerAllFiles_`・走査 2 箇所・冒頭注記 |
| `Form_O1/o1_submit_guard_test.cjs` | Drive 偽物をサブフォルダ対応に・§11（8 ケース） |
| `Form_O1/o1_ledger_test.cjs` | 偽 Drive に `getFolders`・§10（6 ケース） |
| `Form_O1/o1_ledger_mutation_test.sh` | 変異 3 本 |
| `Form_O1/o1_submit_mutation_test.sh`（新規）＋ `.gitignore` の `!` 行 | 受け口の変異 12 本 |
| `docs/o1-deletion-ledger.md` | A-1 |

## テスト戦略
- Node の guard test（陽性・陰性対照つき）＋ 変異検査（新ガードを壊すと赤）。
- 実配備の確認は研究者の手順（`researcher-steps.md`）。

## 配備順（研究者）
1. **台帳を先に**差し替える（新台帳は直下も読むので、旧受け口のままでも正しく動く）。
2. 次に受け口を差し替え・新バージョンでデプロイ。
⚠️ 逆順だと、その間に届いた分を旧台帳が数えず「未受領・途絶」通知が出うる。
