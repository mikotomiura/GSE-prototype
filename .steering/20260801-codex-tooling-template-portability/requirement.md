# codex-tooling-template-portability — Codex 連携ツールの移植性バグをテンプレート側で根治

## 背景

2026-08-01、GSE-prototype で `codex-consult` を初めて使おうとして 2 段構えの静かな故障が発覚した
(詳細な単一真実源: `.idea/issue-commands-setup-flock-portability.md`)。

1. `scripts/secrets-filter.sh` に実行ビットが無く (`100644`)、`run-codex-consult.sh` が
   `Permission denied` で fail-closed → codex-consult は一度も動いていなかった。
2. 実行ビットを付けたら、今度は予算更新が `flock` + `jq` 方式で、**macOS に `flock` が無い**ため
   `flock: command not found`。生成スクリプトは `set -uo pipefail` (= `set -e` 無し) なので
   **処理は継続**し、続く `jq -r 'select(.type=="usage") | .usage.total_tokens // 0'` が 0 を返して
   `budget.json` に `tokens_used=0` が記録された。

結果「Codex を呼んでも消費が積み上がらない」= **予算ガードが実質無効**。exit code は 0 なので誰も
気づかない。実際 `.codex/budget.json` の `tokens_used` は 116283 のまま 1 ヶ月以上放置されていた。

**配備済みスクリプトは PR #78 (main `8ed6076`) で修正済み。しかしテンプレートは未修正**のため、
新規プロジェクトを bootstrap すると同じバグを再生産する。

## ゴール

新規 bootstrap したプロジェクトが、**macOS でも Windows git-bash でも予算ガードが正しく効く**
状態になる。テンプレートと `verify-setup` の検証項目が整合する
(現状のままだと、正しく直したプロジェクトほど検証に落ちる)。

## スコープ

### 含むもの

`.claude/commands/commands_setup/` 配下のテンプレート:

- `setup-codex-bridge.md` (554-576 / 945-959 / 1049-1063) — `flock`+`jq` 予算更新ブロック 3 箇所
- `setup-hooks.md` (653-678) — `token-report-stop.sh` 生成部の `flock` ブロック 1 箇所
- `setup-hooks.md` (543-554) — `codex-budget-guard.sh` の `jq` 予算読み取り (同一の静かな故障モード)
- `verify-setup.md:342` — 「atomic budget update (flock)」検証項目の改訂
- 実行ビットの担保 (`verify-setup` に検証項目を追加)
- 散在する散文の「atomic + flock」記述 (`setup-agents.md` / `setup-skills.md` / `setup-commands.md`)

### 含まないもの

- `sed -i` の修正 — テンプレートは既に `sed -i.bak` で正しい (GSE-prototype 配備済みファイルの
  ドリフトだった)。**ドリフトが他にも無いか確認するだけ**。
- 他 6 コピー (masyuu / CDLE / Etajima 等) への配布 — `.idea/issue-...` の管轄。
  本タスクは GSE-prototype 内テンプレートの修正 + issue への「参照実装ができた」追記まで。
- `setup-hooks.md:800` の `jq` — 生成物ではなくセットアップ時の対話的 settings.json 編集。
- Rust / TypeScript 本体コードの変更 (一切無し)。

## 受け入れ条件

- [ ] 4 箇所の `flock`+`jq` 予算更新ブロックが python 方式に置換されている
- [ ] トークン抽出が `total_tokens` の再帰探索 (`find_tokens()`) になり、
      見つからなければ `WARN` を stderr に出す (黙って 0 を書かない)
- [ ] 生成スクリプト冒頭に `PYTHON=$(command -v python3 || command -v python || true)` 検出 +
      不在時 fail が入っている
- [ ] `verify-setup.md` の検証項目が「予算更新が atomic かつ `flock`/`jq` 非依存 (python)」に改訂され、
      修正後の GSE-prototype 実物に対して **pass** する
- [ ] 生成物の実行ビットが `verify-setup` で検証される
- [ ] 生成されるスクリプトを書き出して `bash -n` が通り、`flock`/`jq` が実コマンドとして残っていない
- [ ] 予算更新の read-modify-write が macOS の python 単体で通る
- [ ] `.idea/issue-commands-setup-flock-portability.md` の「進捗」が更新されている

## 関連ドキュメント

- `.idea/issue-commands-setup-flock-portability.md` — 本件の単一真実源
- `scripts/run-codex-review.sh` — 元から python 方式。**正解の形**
- `scripts/run-codex-consult.sh` — PR #78 で同方式へ統一 (`git show 8ed6076`)
- Skill: `git-workflow` / `implementation-workflow`

## 運用メモ

- /reimagine 適用: **No**
- 理由: 修正方針が issue で確定済みで、参照実装 (`run-codex-review.sh` / PR #78 の差分) が
  既に手元にある。設計の選択肢が開いていないため代替案生成の価値が無い。
