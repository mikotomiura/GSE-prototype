# 次セッション（★ Mac 実機で始める）— G1 / O1 の収集開始準備（ゲートを緑にする・配布 zip・実機確認）

> 作成: 2026-09-26（Windows 機のセッション・D〔P1 本体の準備〕完了直後）。⚠️ **このメモを一次資料にしない。**
> 数字はすべて **2026-09-26 に Windows 機で測った値**（各行に測り方を書いた）。★ Mac で**もう一度測り直す**こと —— 過去に「メモの数字を信じず走らせたから見つかった」事故がある（後述 §4）。
> ⚠️★★★ **このタスクは macOS 実機でしか完結しない**（`hdiutil` / `codesign` / `ditto`・TCC の許可・Mac ランナーでの Release ビルド）。Windows 機では途中で必ず止まる。

## §0 打ち込む用（★ Mac で `git pull` してから `/clear`、モデルは Sonnet。裁定が絡む所は Opus に切り替える）

```
.steering/_handoff/next-session-g1-o1-mac-collection-prep.md を読んで、G1 / O1 の収集開始準備を進めてください。

⚠️ まず Mac で main を最新にし（git pull --ff-only・HEAD は ad1bae3d 以降）、/start-task（task 名: g1-o1-mac-collection-prep）を実行する。
   docs/agent-shared.md のリンクハブから該当 docs を先に読む。Skill: verify-before-claiming（★ メモの数字を写さない）・data-privacy・subagent-delegation。
★ 最初に §3-0 の「Mac での全ゲートの実測」を行い、Windows の値（§1）との差を取る。差は macOS 固有の欠陥の可能性（§4-5）。
⚠️ 研究者の裁定・作業が要る項目（§3 の [研究者]）は、私が埋めない。一覧にして渡し、答えを待つ。
⚠️ 被験者向け文書（同意文書・participant-guide・課題ページ・README）は契約。研究者の承認なしに文面を変えない。
⚠️ タグの push・Drive / フォームの差し替え・被験者への送付は共有状態を変える。実行前に必ず確認を取る。
⚠️ 凍結物（docs/preregistration-p1-episode.md・src-tauri/prereg/p1-episode.json）と G1 の事前登録（experiments/.../preregistration.md）の既存の版は書き換えない（改訂は append-only）。
⚠️ URL・Google の ID・氏名・メール・セッション時刻を repo に書かない（repo は一時 public にする運用がある）。
⚠️ git add -A / git add <dir> は使わない。.steering/20260921-media-expression-theory-audit/（別トラック C）は触らない・コミットしない。
⚠️ .codex/budget.json は台帳（git checkout -- で戻さない）。
★ 完了時は /finish-task（レビューは model 明示・範囲/禁止/締切つき → /cross-review 2 巡）→ git-workflow ルール 6。
応答は日本語。
```

## §1 現在の状態（2026-09-26・Windows 機で実測）

| 何 | 値 | 測り方 |
|---|---|---|
| main | `ad1bae3d`（PR #229 = D の merge・main の CI 成功） | `git log` / `gh run list --branch main` |
| 最新のリリースタグ | **`v0.1.35`**。⚠️ HEAD は **476 コミット先**。O1 ゲートは「**タグ以降にコードが 71 コミット動いた**」と赤 | `git tag --sort=-v:refname` / `git rev-list --count` / O1 ゲート |
| **G1 ゲート** `scripts/check-g1-collection-readiness.sh` | rc=1・**通過 14 / 未達 6** | 実行 |
| ├ 前提条件 3 | ❌ 同意文書・参加案内の記録項目表に `starve_window` が無い（2 件） | 同上 |
| ├ 前提条件 7 | ❌ 「途中でやめた人の数え方」が未決（事前登録は**第 19 版**・**第 20 版以降の記録が要る**） | 同上 |
| └ 人手確認の記録票 A / B / C | ❌ 3 件とも「未実施」（`experiments/20260801-controlled-friction-task/collection-readiness-record.md`） | 同上 |
| **O1 ゲート** `scripts/check-o1-release-readiness.sh` | rc=1・**通過 21 / 未達 2**（① 同意文書の状態表に「⚠️ 未了」が残る ② リリースタグが古い） | 実行 |
| ADR-031 / ADR-032 | **Proposed**（同意文書 §3 の改訂は研究者の承認待ち）。ADR-034 は **Accepted**（2026-09-20） | 各 ADR の 3 行目 |
| 配布スクリプトの既定タグ | `make-distribution.sh` = **`v0.1.23`** ／ `make-common-app-zip.sh` = **`v0.1.24`**（⚠️ 素で実行すると古いものを配る） | `grep -n` |
| G1 課題ページの生成器 | 生の `**` が **0 枚（10 枚中）**・`<strong>` が全 10 枚（ゲート [5]）。記録用紙に「文字数」欄あり（[6]） | G1 ゲート |
| ⚠️ Drive 上の課題ページの実物 | **未確認**（ゲートは生成器しか見ない。記録票 C が未実施） | — |
| G1 の `config.json` | `status = CONFIRMATORY_IN_PROGRESS_1_OF_3`・`revision.version = 19`・`design.n_subjects = 3` | 読み取り |

★ **9/20 の棚卸しのまま・今回は再確認していない**もの（`.steering/20260920-g1-o1-inventory/inventory.md`）: G1-9（`status` が実態 0/3 と食い違う）・G1-10（確証標本の `roster` が 2 名）・G1-11（週セレクタ）・O1-3（O1 の事前登録文書が無い・ADR-034 Migration 6）・O1-5（募集〜配布間に O1 参加者へ何を約束するか）・前提条件 1・2・4・6 の実体（機械検査が無い）。

## §2 なぜ Mac か・Mac 側の前提

- **この Mac が CI の self-hosted ランナー `gse-mac`**（MacBook Air・arm64）。`v*` タグを push すると `build-macos` がこの Mac 上で走り、**ad-hoc 署名**の `.app` を作る（`.github/workflows/ci.yml` の署名ステップ・`.idea/20260801-self-hosted-runner-setup.md`）。
- **署名は現状 ad-hoc（Developer ID・公証なし）**。ネスト bin（`gse-submit` ほか）→ 本体の順に個別署名し、`--options runtime` は使わない（TCC 過剰検証の原因・`ci.yml` のコメント）。被験者は初回だけ**研究者同席**で `初回セットアップ_mac.sh` を実行して隔離属性を外す（`dist-readme-macos.txt`）。
  ⚠️ **署名方式（Developer ID・公証）を変えるかは未決**。変えるなら研究者の裁定と、上の TCC の前提の読み直しが要る。本タスクで勝手に変えない。
- 配布 zip の作成は `hdiutil` / `ditto` / `codesign` を使うので macOS 専用。**署名に触らない**（dmg 内 → コピー後 → zip → 展開後の 4 点で `codesign --verify --strict`）。⚠️ **Windows 向け zip を `ditto` で作ってはならない**（UTF-8 フラグが落ちて文字化けする・2026-08-07 実測。スクリプトは対応済み）。
- 入力監視（TCC）の許可ダイアログ・アプリ内提出（`gse-submit` 同梱・送信 timeout 300 秒）は**実機でしか確かめられない**。
- 環境: `rust-toolchain.toml` = **1.98.1 固定**／ `jq`・`python`（duckdb は解析用）・`gh`（認証済み）／ データ repo は `GSE_DATASET`（既定 `$HOME/gse-dataset`・HTTPS clone）。
- ⚠️ **ランナーのディスクが枯渇して CI が落ちた前例**（2026-08-31・`.steering/_handoff/mac-runner-disk-cleanup-prompt.md`）。ビルド前に空きを確認する。

## §3 タスク（★ 区分: [Mac] = このセッションで実施 ／ [研究者] = 私は埋めない ／ [確認] = 実行前に承認を取る）

**0. [Mac] 全ゲートを Mac で実測する**（★ 最初）
`bash scripts/check-g1-collection-readiness.sh` ／ `bash scripts/check-o1-release-readiness.sh`（＋ `--selftest`）／ `bash scripts/check-shell-portability.sh` ／ `bash experiments/20260801-controlled-friction-task/make-common-app-zip.sh --selftest`。
Windows の値（§1）との差を表にし、**macOS でだけ壊れる検査**（bash 3.2・BSD の `sed` / `od`）が無いかを見る。過去は Windows 16/1 に対し Mac 15/2 で、差はすべて macOS 固有の欠陥だった（PR #128）。

**1. [研究者] 裁定・作業の一覧を作って渡す**（★ 答えが返るまで下流を止める）
- 前提条件 3: 同意文書・参加案内の記録項目表に `starve_window` / `app_version` を追記（被験者向け文書＝契約）。
- 前提条件 7: 「途中でやめた人」の (a) 同意撤回に当たるか (b) n に数えるか (c) 補充するか ×（本人の申し出以外で完了しない人／やめた後に削除を求めた人／「中断」と「やめる」の区別）。→ 事前登録**第 20 版**として記録（append-only）。
- O1: ADR-031 / ADR-032 を Accepted にするか（同意文書 §3 の改訂の承認・承認マーカ `<!-- o1-esm-consent: approved -->`）／ O1 の事前登録文書（Migration 6）／ 募集〜配布間の約束（O1-5）。
- G1: 確証標本の 3 人目（G1-10）・`config.json` の `status` の食い違い（G1-9）・週セレクタ（G1-11）。

**2. [Mac] [確認] 「最初の配布」のタグを決めて配布物を作る**
- 前提: main に必要な修正が全部入っていること（§1: タグ以降にコード 71 コミット）。**タグ push は共有状態を変えるので、研究者の承認を取ってから**。
- タグを記録する場所は配布タスクで決める（ADR-034 Migration 3・G1-2）。以後 G1 はそのタグに固定する。
- Release ビルド（この Mac の `build-macos`）→ `make-common-app-zip.sh --mode g1|o1 --tag <新タグ>`（⚠️ **`--tag` を必ず明示**。既定は古い）→ 4 点の `codesign --verify --strict`・実行ビット・モード標識（`g1.mode` / `o1.mode`）の検算 → 被験者 1 人ぶん（`make-distribution.sh`）。
- 現在の O1 ゲートは「タグ以降にコードが動いたか」を見ている（9/01 の「タグに `o1.rs` が在るか」だけの述語からは改善済み）。⚠️ それでも配布物の実体で確かめる（§4-1）。

**3. [Mac] G1 課題ページ**
`build_task_pages.py` で再生成 → **全 10 枚を目視**（生の `**`・強調の反転・文面の誤り）→ Drive の差し替えは **[研究者]**（記録票 C）。⚠️ 文面の妥当性は機械では判定できない。

**4. [研究者] 人手確認の記録票 A / B / C**
A: 配布済み電子同意フォームとの突合 ／ B: 両 OS の対のテストが緑（CI の run 番号は Windows・macOS の**両方**）／ C: Drive の差し替え。⚠️ ゲートは「確認したと書いたこと」しか見ない。URL・ID は書かない。

**5. [Mac] 実機通し確認**（配布物ができてから）
初回起動（隔離属性の解除・入力監視の許可）→ 計測 → アプリ内提出（G1 / O1 の各モード）→ 復号側で受領できること。⚠️ O1 は「押してはいけないボタンが出ない・説明文が O1 用」を目視（§4-1）。

## §4 ⚠️ 見落としやすい点

1. **ゲート緑 ≠ 配布物が正しい**。過去に `v0.1.29`（`o1.rs` を含まない）が署名も実行ビットも正常に見えたまま通常モードで動いた。**タグが新しいことは機能が入っていることを意味しない**。配布物の実体（`LC_ALL=C grep -a`。⚠️ `strings` は日本語で偽陰性）で確かめる。
2. **既定タグが古い**（§1）。`--tag` を落とさない。
3. **記録票は申告**。緑にしても、Drive・フォーム・CI の実物は誰も見ていない。埋めた人が責任を持つ。
4. **repo は一時 public**になりうる。URL・ID・氏名・メール・時刻を書かない（ゲート [8] が機械で弾く）。
5. **macOS の bash は 3.2・BSD 系ツール**。GNU 前提の `sed -i`・`od`・多バイト文字を含む変数名が落ちる。Windows で緑でも Mac で赤になりうる（その逆も）。
6. **このメモの数字は「書かれた時点の値」**。特に 9/20 の棚卸しの項目は、着手時に一次（コード・ゲート）で確かめ直す。
7. 課題文の**内容の妥当性**は私が判定できない（生成器の `**` は機械検査済み）。研究者の確認が要る。

## §5 やらないこと

- 署名方式の変更（Developer ID・公証）を、裁定なしに始める ／ 被験者向け文書の文面を変える ／ 事前登録の既存の版を書き換える。
- 実データを開く ／ P1 の PG-1 の値を決める ／ C トラック（媒体表現）に着手する。
- 承認なしに、タグを push する・Drive / フォームを差し替える・被験者へ送る。

## §6 一次資料（読む順）

1. `.steering/20260920-g1-o1-inventory/inventory.md`（残タスク台帳・依存関係 §5）／ `decisions.md`（判断 1〜4）／ `evidence.md` ／ `merge-plan.md`
2. `experiments/20260801-controlled-friction-task/collection-readiness-record.md`（記録票）・`preregistration.md`（第 19 版）・`participant-guide.md`
3. `docs/adr/ADR-034-g1-o1-parallel-conduct.md`（Accepted）・`ADR-031` / `ADR-032`（Proposed）・`docs/o1-roster-operations.md`・`docs/participant-setup-guide.md`
4. `.steering/_handoff/next-session-prompt-o1-v0-1-31-and-open-fronts.md`（一部消化済みの後継）・`g1-o1-precollection-findings.md`（9/01・⚠️ 一部古い）
5. `.github/workflows/ci.yml`（`build-macos` の署名ステップ）・`.idea/20260801-self-hosted-runner-setup.md`
