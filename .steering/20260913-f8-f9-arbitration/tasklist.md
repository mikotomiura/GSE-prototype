# tasklist — F-8 / F-9

## Phase 0: 裁定 (✅)
- [x] 実測を提示して研究者が裁定（F-8 = 第三者 3 本のみ固定 / F-9 = 不変条件検査に置換）

## Phase 1: F-8 (✅)
- [x] 3 本の **commit** SHA を一次情報から解決（⚠️ annotated tag を commit まで解決）
- [x] ⚠️ `dtolnay` の `action.yml` 既定が `stable` のままであることを確認
- [x] ⚠️ `uses:` 行のみ置換（★ 一度全文置換で注記を壊し、やり直した）
- [x] `ci.yml` の古い follow-up 注記を書き直す（★ 残る本丸 = 鍵の退避 も明記）

## Phase 2: F-9 (✅)
- [x] `scripts/check_workflow_invariants.py`（4 不変条件 ＋ 空振り対照）
- [x] `scripts/tests/test_check_workflow_invariants.py`
- [x] T1〜T8 すべて期待どおり（★ 変異 4 種で赤を実証）
- [x] `frontend-check` へ配線（⚠️ 全 PR で走る場所）
- [x] `docs/verification-runbook.md` §1 (h)（★ 版上げ手順つき）
- [x] T9: `check-tests-are-wired.sh` = **14/14**

## Phase 3: レビューと完了
- [x] `code-reviewer` + `security-checker` を**並列**起動 → ⚠️ HIGH 3 / MEDIUM 7 / LOW 8 を反映
- [x] ⚠️★★★ **4 条件のうち 2 つが実質機能していなかった**（hosted 判定の否定リスト／
      permissions の存在だけ判定）→ ★ 許可リストへ反転・広さ判定へ。変異で実証
- [x] ⚠️ composite action の死角・`actions/*` 免除の ref 未検査・PyYAML 未宣言を反映
- [x] ⚠️ 自分が入れた退行 2 件（合成 fixture への誤検出 / `KeyError`）も修正
- [x] 再検証: self-test 13 群 / unittest **34 件** / 全ゲート緑（86 テスト）
- [ ] `/cross-review`
- [ ] PR → CI 全緑 → ⚠️ `workflow_dispatch`（ブランチ）で `build-windows` 実機確認
- [ ] main へマージ（★ 研究者判断）

## ⚠️ 本タスク外で見つけたこと（★ 申し送り）
- [ ] ⚠️★★★ **`scripts/check-shell-portability.sh` が Windows で exit 1**（★ main の無変更ツリーでも再現）。
      ★ 陽性対照が `mktemp` の MSYS2 `/tmp` パスに書き、**ネイティブ Python が開けず** `FileNotFoundError`。
      ⚠️ CI は ubuntu なので**緑のまま**＝ **Windows ローカルでのみ番人が空回りする**。→ 別タスクで直す
- [ ] ⚠️ `~/.gse/age-identity.txt` をランナーと別マシン/別アカウントへ退避（★ `ci.yml:112` 候補 c・実機作業）
