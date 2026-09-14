# 設計 — worktree への `permissions.deny` 注入

## 実装アプローチ

### 置き場: `<worktree>/.claude/settings.local.json`（★ §8c の確定事項・再導出しない）

| # | 根拠（★ 実測 2026-09-13 / 本セッションで再確認） |
|---|---|
| 1 | `.claude/settings.local.json` は `.gitignore:46` で ignore 済み → **worktree ごとに別物にできる** |
| 2 | `.claude/` 自体は git 追跡 → worktree には `settings.json` / agents / commands / skills が複製される |
| 3 | ⚠️★★★ main checkout の `.claude/settings.json` に入れると**対話セッションでも `git push` が塞がれる** |

### 配線先: `scripts/loop-spawn.sh`（注入）＋ `scripts/loop-run.sh`（毎 attempt の再保証）

★ `loop-run.sh:275` は worktree 生成を **`loop-spawn.sh --no-exec` へ委譲している**。
→ ★ **注入点**は `loop-spawn.sh` に置く。そうすれば **モード A（人が spawn）とモード C（無人）の両方**が
1 箇所で通る（⚠️ `loop-run.sh` だけに置くとモード A が素通りする）。

⚠️★★★ **ただし作成時 1 回では閉じない**（★ 2026-09-14 に code-reviewer / security-checker が
**両方 HIGH** で指摘）:
- ★ 既定 `permission_mode=acceptEdits` は **Edit/Write を自動承認**する。
- ⚠️ 必須 deny 7 件に **`Edit` / `Write` 系は 1 件も無い**（★ `rm -rf` は塞ぐが `rm <file>` は塞がない）。
- → ⚠️ attempt N で deny に阻まれた worker が `<worktree>/.claude/settings.local.json` を消せば、
  **attempt N+1 は新しいセッションなので deny 無しで起動する**。

→ ★ `loop-run.sh` の `run_issue` の attempt ループ先頭と `run_watchdog` の冒頭に
`ensure_deny()`（注入は冪等なので再実行してよい）を置き、⚠️ **保証できなければ `blocked` にして起動しない**。

### 分離: 独立スクリプト `scripts/loop-worktree-deny.sh`

★ `loop-spawn.sh` に直書きせず独立させる理由:
- ★ **git worktree を作らずにテストできる**（テストは一時ディレクトリに対して直接叩ける）
- ★ 検査のみモード（`--verify`）を切り出せる → **陰性対照が書ける**

インタフェース:

```
bash scripts/loop-worktree-deny.sh <dir>            # 注入（マージ）＋ 検査。exit 0 = 保証できた
bash scripts/loop-worktree-deny.sh --verify <dir>   # 検査のみ（書かない）
bash scripts/loop-worktree-deny.sh --print          # 必須 deny を 1 行ずつ stdout へ
```

★ `--print` を置くのは **契約の二重定義**を検出するため —— テストが
`loop-config.README.md` の逐語リストと突き合わせる（⚠️ 片方だけ増やす事故を止める）。

### 3 状態の扱い（⚠️ `verify-before-claiming` ルール 5b）

| 状態 | 振る舞い | 理由 |
|---|---|---|
| **不在** | 必須 7 件だけを持つ JSON を新規作成 | ★ 通常経路（git worktree add は ignore ファイルを複製しない） |
| **正常（有効 JSON）** | `.permissions.deny` に**和集合**をマージ。⚠️ 他のキー・`allow` / `ask` は保持 | ★ §8c 注意 1「他のキーを消さない」 |
| **壊れている（不正 JSON）** | ⚠️★★★ **上書きせず非 0 で終了**（ファイルに触れない） | ★ 安全装置なので **fail-closed**。⚠️ 人の設定を黙って捨てない |

★ いずれの成功経路でも**最後に検査段を通す**（書いた結果を読み直して 7 件を数える）。
⚠️ 「書いたから入っているはず」で終わらせない。

#### ⚠️★★★ 検査は **sentinel を要求する**（★ 初版は fail-open だった）

★ 初版の `verify_deny` は `jq ... 2>/dev/null || true` で **jq の実行時エラーを握りつぶしていた**。
⚠️ `{"permissions": "nope"}` のように `.permissions.deny` を評価できない形では
jq が落ちて出力が空になり、★ **「欠けなし」＝ 緑**と報告した（＝ deny 0 件のファイルを合格にした）。
⚠️★★★ しかも `--verify` は「既存 worktree を手で点検する」手段として**人に案内している経路**である。

→ ★ 対策は 2 段:
1. jq プログラムを **total** にする（★ 型が想定外なら必須 7 件を全部「欠け」として出す）。
2. **`__ALL_PRESENT__` という sentinel を要求する** —— ⚠️ 出力が空なら**自動的に不合格**になる。

★ 回帰テストとして 6 形（`{"permissions":"nope"}` / `["not","an","object"]` / `{"permissions":["a"]}` /
`{"permissions":42}` / `{"permissions":{}}` / `{}`）を陰性対照に置いた。

### jq を必須にする

★ マージと検査は JSON の意味で行う必要がある（⚠️ grep では `"deny"` 以外の配列の要素を誤検出する）。
→ ★ jq 不在なら **die**。⚠️ 「jq が無いから deny 無しで続行」は安全装置の意味を消すので採らない。
（★ `loop-run.sh:32` が既に jq を必須にしており、モード C の前提は変わらない。
 ⚠️ モード A は新たに jq 必須になる —— これは**意図した縮退の禁止**である。）

## 変更対象

### 修正するファイル
- `scripts/loop-spawn.sh` — `git worktree add` の直後に deny 注入を呼ぶ。⚠️ 失敗したら `die`
- `.github/workflows/ci.yml` — 新テストのステップを追加（★ `check-tests-are-wired.sh` の要求）

### 新規作成するファイル
- `scripts/loop-worktree-deny.sh` — 注入 / 検査 / 一覧出力
- `scripts/loop-worktree-deny-test.sh` — 3 状態 ＋ 冪等 ＋ 陰性対照 ＋ 契約二重定義の検査

### 削除するファイル
- なし

## 影響範囲

| 影響先 | 内容 | 対処 |
|---|---|---|
| `loop-run.sh:275` | ⚠️★★★ `loop-spawn.sh --no-exec` の **stdout 最終行 = worktree 絶対パス**という契約 | ★ 追加の出力はすべて **stderr** へ出す。★ `pwd` を最終行のまま保つ（テストで検査） |
| `loop-run.sh` の attempt ループ | ★ 毎 attempt で `ensure_deny` を通す（注入は冪等） | ⚠️ 保証できなければ `blocked` を emit して起動しない |
| 注入に失敗した worktree | ⚠️ 残すと人が手で `cd` して deny 無しで起動でき、同 id の再実行も恒久的に死ぬ | ★ `loop-spawn.sh` が **worktree と branch ごと撤去してから** die する |
| モード A の人間運用 | jq が無い環境では新たに落ちる | ★ エラーメッセージに導入方法を書く |
| 既存 worktree | 変更なし（★ 次に作られる worktree から効く） | ★ 既存 worktree には手で `--verify` を叩ける |
| main checkout | ⚠️ **触らない** | — |

## 既存パターンとの整合性

- ★ `scripts/check-tests-are-wired.sh` / `check-shell-portability.sh` と同じく、
  **陽性対照と陰性対照を内蔵**し、「検査が空振りしていない」ことまで見る
- ★ `set -euo pipefail` ／ `die()` ／ 日本語コメントで**なぜそう書いたか**を残す既存様式に合わせる
- ★ 変数の直後に多バイト文字が来るなら `${name}` と括る（`check-shell-portability.sh` の規約）

## テスト戦略

`scripts/loop-worktree-deny-test.sh`（一時ディレクトリのみ。★ git worktree を作らない）:

| # | ケース | 期待 |
|---|---|---|
| 0 | ⚠️ **fail-open 回帰 6 形** ＋ 部分適用（1 件だけ） | ★ すべて `--verify` が非 0 |
| 1 | 不在 → 注入 | exit 0 / 有効 JSON / deny がちょうど必須 7 件 |
| 2 | 正常（他キーあり）→ 注入 | exit 0 / `env` と `permissions.allow` が残る / deny = 既存 ∪ 必須 / 重複なし |
| 3 | 壊れている → 注入 | ⚠️ exit ≠ 0 / **ファイルの中身が 1 バイトも変わらない** |
| 4 | 冪等性（2 回実行） | 2 回目も exit 0 / deny の件数が増えない |
| 5 | ⚠️ 陰性対照: 1 件抜いて `--verify` | ★ exit ≠ 0（＝ 検査が空振りしていない） |
| 6 | 陽性対照: 正しい状態で `--verify` | exit 0 |
| 7 | 契約の二重定義 | `--print` の 7 件が `loop-config.README.md` の逐語リストと**集合一致** |
| 8 | `loop-spawn.sh` の配線 | ★ `loop-worktree-deny.sh` を呼ぶ行があり、★ `pwd` が stdout 最終行のまま |

★ **配線の検査は「grep で呼び出し行を探す」ではなく、実際に worktree を作って行う**
（#8 / 陰性対照 2 本）。⚠️ ただし作るのは **`mktemp -d` 配下の一時 git repo** であり、
★ **本 repo には 1 バイトも触れない**（実行後に `git worktree list` が 1 件・`git status` 不変であることを確認済み）。

⚠️★★★ **それでも残る未検証**: ★ 「worktree に deny が *書かれている*」ことまでしか見ていない。
★ **`claude -p` が実際にその deny を読んで `git push` を拒むか**は本テストの範囲外である。
→ ★ そこは **着手順 4「最も安い issue 1 本を parallel=1 で回す」** が担う
（⚠️ SSOT 逐語「`--dry-run` では権限・cwd 境界・hook 発火が観測できない」）。
⚠️ かつ `permission_mode` を `auto` / `bypassPermissions` へ昇格させた場合の挙動も**未検証**である。

## ロールバック計画

★ 新規 2 ファイルの削除 ＋ `loop-spawn.sh` の追加ブロック（1 箇所）と ci.yml の 1 ステップを revert すれば戻る。
⚠️ **既存の挙動を書き換えていない**（追加のみ）ので、revert の影響は注入が消えることだけ。
