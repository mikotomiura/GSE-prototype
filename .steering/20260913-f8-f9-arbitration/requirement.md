# 申し送り F-8 / F-9 の裁定と実装

> ★ 出自: `.steering/_handoff/next-session-followups-f1-f5.md`（F-1〜F-5 の作業中に起票）
> ★ 裁定: 2026-09-13・研究者（★ 実測を提示したうえで選択してもらった）

## 背景

F-1〜F-5 の作業中に 2 件を新規起票し、未決のまま残していた。

### ⚠️ F-8: GitHub Actions の版が可動参照のまま

★ 実測（2026-09-13・両 workflow を yaml パースして全数列挙）:

| 実測 | 値 |
|---|---|
| SHA 固定されている action | ⚠️ **0 本**（全部タグ参照） |
| ⚠️★★★ `dtolnay/rust-toolchain@stable` | **タグですらなく*ブランチ*参照**（最も可変） |
| self-hosted で走る第三者 action | `dtolnay/rust-toolchain` / `Swatinem/rust-cache`（`check` / `build-macos`） |
| ★ その機械にあるもの | `~/.gse/age-identity.txt`（⚠️ **被験者提出物を全部復号できる鍵**）/ `Form_O1/o1_submit.json`（実 endpoint ＋ secret） |
| `softprops/action-gh-release@v2` | hosted だが `contents: write`（⚠️ **被験者が落とすバイナリを差し替えうる**） |

⚠️ `ci.yml:132` に **自分で「follow-up: self-hosted で走るジョブの action を commit SHA でピン留めする」と書いてある**。
→ ★ 「回す場所が無い手順は回らない」の実例になりかけていた。

### ★ F-9: workflow の構文検査が無い

⚠️ ただし **事故実績は 0 件**（直近 40 コミットの `.github/workflows/` 変更はすべて semantic な修正）。
⚠️★★★ **起票の契機になった Codex の HIGH 指摘は false positive だった**
（★ secrets-filter が伏字化した diff を見て「構文エラー」と判定したもの。実ファイルは健全）。
⚠️ さらに actionlint 導入は**第三者 action / バイナリ配布を増やす** —— ★ F-8 が減らそうとしている面と正面衝突する。

## ゴール

1. ★ **F-8**: 第三者 action 3 本を commit SHA へ固定する。
2. ★ **F-9**: 汎用 linter は入れず、**守りたい不変条件を機械で検査する**形に置き換える。
3. ⚠️★★★ **「決めた」で終わらせない** —— ★ F-8 の決定自体が*検査されていない前提*にならないよう、
   **新しい第三者 action が可動参照で入ってきたら CI が赤くなる**ようにする。

## スコープ

### 含むもの

- `ci.yml` / `supply-chain.yml` の第三者 action 3 本を SHA 固定（★ 版名をコメントで併記）
- ⚠️ `actions/*`（GitHub 自社所有）は**タグのまま**とし、**その理由をファイルに書く**（★ 無言で非対称にしない）
- `scripts/check_workflow_invariants.py`（★ `--self-test` ＋ `scripts/tests/test_*.py`・repo の既存作法）
- ★ `frontend-check` への配線（⚠️ `paths` 限定でない場所 = 全 PR で走る）
- 更新手順（⚠️ dependabot 無しなので**人が回す**）を `docs/verification-runbook.md` に置く

### 含まないもの

- ⚠️ **actionlint / 汎用 workflow linter**（★ F-9 の裁定 = 入れない）
- ⚠️ **dependabot**（★ D12 で入れないと裁定済み）
- ⚠️ `actions/*` の SHA 固定（★ 今回は対象外・理由を明記）
- ⚠️ **`~/.gse/age-identity.txt` の退避**（★ `ci.yml:112` の候補 c）——
  **実機作業が要るので本タスクでは行わない**。★ 申し送りに残す。

## 受け入れ条件

- [ ] 第三者 action 3 本が **40 桁 commit SHA** で固定されている（⚠️ annotated tag のオブジェクト SHA ではない）
- [ ] ⚠️ `dtolnay/rust-toolchain` の固定先が **`stable` ブランチ上のコミット**であり、
      その `action.yml` の `toolchain` 既定値が **`stable` のまま**であること（★ 意味を変えない）
- [ ] `scripts/check_workflow_invariants.py` が **現状で exit 0**
- [ ] ⚠️ **変異テストで赤になること**を実証（第三者をタグに戻す / permissions を外す /
      supply-chain を self-hosted に向ける / 走査 0 件）
- [ ] `bash scripts/check-tests-are-wired.sh` が緑（★ 新テストが配線されていること）
- [ ] CI 全緑（⚠️ **`build-macos` / `release` は tag でしか走らない**ので、
      ★ **`workflow_dispatch` をブランチ指定で発火して `build-windows` を実機確認する**）
- [ ] `code-reviewer` + `security-checker` を**並列**起動 → 反映
- [ ] `/cross-review`（⚠️ ラッパー・パス限定。★ `GH_TOKEN` 行で BLOCKED になるので研究者確認のうえ `--ack-filtered`）

## 運用メモ

- **/reimagine 適用: No**
- 理由: ★ 方式は**研究者が裁定済み**（第三者 3 本のみ固定 / 汎用 linter は入れず不変条件検査）。
  残りは実装の詳細であり、複数案の比較は閉じている。
