# loop-spawn-cleanup-fix — 起票 18: `--cleanup` が撤去できないのに「完了」と報告する

## 背景

⚠️ 一次資料は `.steering/20260914-mhd-feature-offline-tiers/blockers.md` の **起票 18**
（2026-09-20 に `.steering/20260920-loop-foundation-fixes/` の実測 M4 で発見）。

`scripts/loop-spawn.sh --cleanup <id>` は worktree を **ブランチ名だけ**で引いている
(`scripts/loop-spawn.sh:57` 逐語):

```bash
wt="$(git worktree list --porcelain | awk -v id="$id" '/^worktree /{p=substr($0,10)} /^branch /&&$0 ~ ("loop/" id){print p}')"
```

→ ⚠️ 起票 10 の形で **`loop/<id>-*` から逸脱した worktree は 1 件もヒットしない**。
★ しかも **branch だけは削除され**、worktree は登録に残り、**`cleanup 完了` と exit 0 を返す**。

### ★ 2026-09-21 に本セッションで再現させた（⚠️ 直す前に再現させること、の実行）

```text
$ LOOP_FORCE=1 bash scripts/loop-spawn.sh --no-exec zzz      # → worktree + branch loop/zzz-issue
$ (cd ../wt/GSE-prototype-zzz-issue && git switch -c deviated-repro-zzz)   # ★ 逸脱させる
$ bash scripts/loop-spawn.sh --cleanup zzz
loop-spawn: worktree 見つからず (既に撤去?)
Deleted branch loop/zzz-issue (was ca7764f).
loop-spawn: cleanup 完了 issue zzz        ← ⚠️ 嘘
exit=0                                     ← ⚠️ 嘘
$ git worktree list
C:/GSE-prototype              a5c53a0 [main]
C:/wt/GSE-prototype-zzz-issue ca7764f [deviated-repro-zzz]   ← ★ 残っている
```

### 実害（起票 18 逐語）

1. ⚠️ **同じ id の再実行が恒久的に死ぬ**（`loop-spawn.sh:90`「同名 worktree が既に存在」）。
2. ⚠️ **main checkout が `main` をチェックアウトできなくなる**（同一ブランチの二重チェックアウト拒否）。
3. ⚠️★★★ **失敗が誰にも見えない**（`verify-before-claiming` の型）。

## ゴール

`--cleanup` が **(a) 逸脱した worktree も撤去でき**、**(b) 撤去できたことを確かめてから
「完了」と書き、撤去できなければ非 0 で止まる**こと。
★ 回帰は `bash scripts/loop-spawn-cleanup-test.sh` が exit 0 になることで判定する
（⚠️ 陰性対照込み ＝ 実装を殺したら赤くなることまで確認する）。

## スコープ

### 含むもの
- `scripts/loop-spawn.sh` の `--cleanup` 分岐（引き方 ＋ 撤去の事後確認 ＋ exit code）
- `scripts/loop-spawn-cleanup-test.sh`（新規・一時 git repo で実際に worktree を作る）
- `.github/workflows/ci.yml` への配線（⚠️ `check-tests-are-wired.sh` が未配線を赤にする）
- `scripts/loop-run.sh:204` の `detail` 文言（★ 修正後は「撤去できない」が**嘘になる**ため）
- 起票 18 への是正追記（`.steering/20260914-mhd-feature-offline-tiers/blockers.md`）

### 含まないもの
- ⚠️ 起票 19（`RUSTSEC-2026-0285`）— 研究者裁定で**別タスク**
- ⚠️ `--cleanup` 以外の分岐（spawn 本体 / `--no-exec` / deny 注入）の挙動変更
- ⚠️ `resolve_base` が `.steering/*/_loop-config.json` の **最後の 1 件**を拾う挙動
  （★ 本セッションの再現中に `docs/adr-030-stall-onset-definition` を base に取ったのを観測した。
   ⚠️ 起票 18 の範囲外なので**別途起票**する）
- ⚠️ 未登録の残存ディレクトリの**自動削除**（★ `rm -rf` は破壊的なので人に渡す）

## 受け入れ条件

- [ ] AC1: 逸脱した worktree（`loop/<id>-*` 以外を指す）を `--cleanup <id>` が撤去できる
- [ ] AC2: 撤去できなかったとき「完了」と書かず、**非 0** で終了する
- [ ] AC3: 正常系（`loop/<id>-<short>` のまま）も従来どおり撤去でき、exit 0
- [ ] AC4: 対象 0 件は **exit 0**（冪等 ＝ 2 回叩いても赤くならない）
- [ ] AC5: ⚠️ **main checkout を撤去しない**（★ どの経路でも）
- [ ] AC6: ⚠️ 別 id（`loop/zzz2-*`）を巻き込まない（★ 現行の部分一致の穴）
- [ ] AC7: `bash scripts/check-shell-portability.sh` が緑
- [ ] AC8: `bash scripts/check-tests-are-wired.sh` が緑（★ 新テストが CI に配線されている）

### ★ レビューで足りないと分かった受け入れ条件（2026-09-21 追加）

- [ ] AC9: `--cleanup <id>-<short>`（完全一致の渡し方）でも撤去できる
- [ ] AC10: ⚠️★★★ **linked worktree の中から叩いても**撤去でき、main checkout が無傷で、
      報告と事実が一致する（★ code-reviewer HIGH。メインが独立に再現して確認した）
- [ ] AC11: ⚠️★★★ **未コミット変更がある worktree を黙って捨てない**（★ security-checker MEDIUM）
- [ ] AC12: ⚠️★★★ id に glob メタ文字（`*`）や `..` を渡しても、**無関係な `loop/*` ブランチを
      1 本も消さない**（★ security-checker MEDIUM）

## 関連ドキュメント

- `.steering/20260914-mhd-feature-offline-tiers/blockers.md` 起票 18（一次）
- `.steering/20260920-loop-foundation-fixes/measurements.md` M4（実測ログ）
- `docs/loop-engineering.md`（Loop の用語・モード A/B/C）
- `.claude/skills/git-workflow/SKILL.md:193`（stale cleanup の運用）

## 運用メモ
- /reimagine 適用: **No**
- 理由: 起票 18 が直し方を 2 点で逐語指定しており（パスでも引く / 確かめてから書く）、
  実装案が分岐しない。★ アーキテクチャ判断も公開 API 変更も伴わない小修正である。
