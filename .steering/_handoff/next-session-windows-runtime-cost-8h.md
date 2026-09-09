# 次セッション用プロンプト — Windows 実機の稼働コスト実測 (§2・8時間)

> ★ このファイルを新セッションの最初のメッセージとして貼ること。
> ★ 対象タスク: `.steering/20260904-windows-orphan-verify/`（★ 新規タスクではない。**継続**）
> ★ 作成: 2026-09-09（前セッションの続き）

---

## 0. ⚠️ 最初にやること（この順・省略しない）

1. **`CLAUDE.md`** と **`docs/agent-shared.md`** はセッション開始時に自動で読まれる。読まれていなければ読む。
2. ★ これは**新規タスクではなく継続**なので `/start-task` は起動しない。代わりに以下を読む:
   - `.steering/20260904-windows-orphan-verify/requirement.md` / `design.md` / `tasklist.md` / `decisions.md`
   - `.steering/20260904-windows-orphan-verify/evidence-s1-A-B.md`（§1 の実測記録・今回は読むだけでよい）
   - `experiments/20260903-o1-runtime-cost/README.md`（§2 のやり方・判定基準の SSOT。⚠️ **mac 前提の記述が多い** ので Windows 用に読み替える。下記 §2 に読み替え済みの手順がある）
   - `experiments/20260903-o1-runtime-cost/env.md`（Windows 行が空欄。埋めるのがこのセッションの仕事の一部）
3. ★ 該当 Skill を読む: `reproducibility-discipline`（実験の記録規約）、`verify-before-claiming`（このメモの数字を鵜呑みにしない）。
4. `git status` / `git log -3` で現在地を確認する。★ 想定: ブランチ `feat/resumption-outcome-arbitration`、直近コミットは `2388d10` 前後。作業ツリーはクリーンのはず。

---

## A. ★ 前セッションで確定済み（★ 再検証・再着手しない）

| # | 状態 |
|---|---|
| §1（孤児回収の実機検証: 正常終了/強制終了/壊れ/べき等/OS再起動） | ✅ **全ケース実機確定済み**。結論: `WM_ENDSESSION` は `CloseRequested` に翻訳されず、次回起動時の orphan sweep のみが回収する。詳細 `evidence-s1-A-B.md`、判断 `decisions.md` 判断1・判断2 |
| §3（overlay クリック透過） | ✅ **idle 状態は確認済み**（四隅+中央 hit-test 5/5 箇所で GSE が奪っていない）。⚠️ **表示状態（Nudge/プローブ中）の hit-test は GUI 自動化手段が無く未検証のまま**（次に GUI 自動化手段が使えるセッションへ引き継ぎ済み。**本セッションで無理に埋めなくてよい**） |
| ★★★ ビルド手順の欠陥 | ⚠️★★★ **素の `cargo build --release`（`--features package` 付きも含む）では Tauri の `custom-protocol` feature が付与されず、release プロファイルでもメインウィンドウが Vite devUrl (`http://localhost:1420`) 依存のまま残る。** 実機で発覚・修正済み。★ **必ず `npm run build && npm run tauri build -- --no-bundle`（リポジトリ直下から）でビルドする。** 詳細 `decisions.md` 判断3、恒久的な注意は `docs/development-guidelines.md` §3 にも追記済み |

★ 上記は一次資料（`decisions.md` / `evidence-*.md`）で裏を取ってから使うこと（`verify-before-claiming`）。このメモ自体は三次資料。

---

## B. ★ 本セッションでやること: §2 稼働コスト実測（8時間・Windows）

### B-0. ビルド確認（★ 前セッションと同じ落とし穴を踏まない）

```bash
cd /c/GSE-prototype
git log -1 --format=%H -- src-tauri/ package.json vite.config.ts tauri.conf.json src/ 2>/dev/null
ls -la src-tauri/target/release/gse-next.exe src-tauri/target/release/o1.mode 2>/dev/null
```

- 上の `git log` が示すコミットより `src-tauri/target/release/gse-next.exe` の mtime が新しければ既存バイナリを使ってよい。
- ⚠️ 迷ったら**必ず作り直す**（安いコストで踏み外しを防げる）:
  ```bash
  npm run build
  npm run tauri build -- --no-bundle
  ```
  ビルド後、コミットハッシュ（`git rev-parse --short HEAD`）を `env.md` に記録する。
- `o1.mode`（中身 `marker`）が `src-tauri/target/release/` に無ければ作る:
  ```bash
  printf 'marker' > src-tauri/target/release/o1.mode
  ```
- ★ **起動して目視確認する**（devUrl エラーが出ないこと）:
  ```bash
  cd src-tauri/target/release && (./gse-next.exe > /dev/null 2>&1 &) ; sleep 5; tasklist | grep -i gse-next
  ```
  ダッシュボードが正常表示されることをユーザーに確認してもらってから、**測定用にいったん終了する**（`taskkill //F //IM gse-next.exe`）。★ B-2 で「起動時のコストから測る」ため、ここで起動したままにしない。

### B-1. 1分スモーク（8列に実値が出るか）

```bash
cd /c/GSE-prototype
D=experiments/20260903-o1-runtime-cost
GSE_COST_DURATION_S=60 GSE_COST_INTERVAL_S=10 bash $D/run.sh with-gse
cat $D/results/with-gse/samples.tsv
awk -F'\t' 'NR==2{print "列数 =", NF}' $D/results/with-gse/samples.tsv
rm -rf $D/results/with-gse
```

- 列数が 8 であること、`cpu_pct` / `rss_kb` / `threads` が非ゼロであることを確認する（⚠️ `battery_pct` / `energy_impact` / `ref_energy_impact` はこの機（デスクトップ・後述）では空 or 0 でよい）。
- 全部 0 なら測定器（`scripts/sample-windows.sh`）が壊れている。原因調査してから先へ進む。

### B-2. 8時間本番（★ 順序が「起動時のコスト」を決める。サンプラを先に起こす）

```bash
D=experiments/20260903-o1-runtime-cost

# 1) GSE が起動していないことを確認
tasklist | grep -i gse-next || echo "(GSE プロセスなし・OK)"

# 2) サンプラを先に起こす（★ 起動前の基線を取るため）
nohup bash "$D/run.sh" with-gse > /dev/null 2>&1 &
disown
# 1分ほど待って基線（全列 0 に近い行）が数行たまってから次へ

# 3) GSE をバイナリ直叩きで起動する（★ タスクバー等 UI から起動しない・直叩き）
( cd src-tauri/target/release && ./gse-next.exe > /dev/null 2>&1 & )
```

- ⚠️★★★ **対照 (`without-gse`) は回さない**（README「2026-09-04 以降、対照は回さない」の裁定どおり。指標3をエネルギー影響に替えたため対照に意味がない）。
- ⚠️ **8時間、研究者はいつもどおりこの機を使ってよい**（この実験は「ふだんの作業のあいだ」の負荷を測るのが目的）。★ 途中でこの bash セッション・端末を閉じないこと（`nohup`/`disown` 済みなのでプロセス自体は生き残るが、監視や `Ctrl+C` の事故を避けるため触らないのが安全）。
- Claude Code 側は `run_in_background` 付き Bash や長めの `ScheduleWakeup`（1〜数時間おき）で様子を見に行く運用にする。**8時間ずっと張り付く必要はない**。

### B-3. 集計（8時間後）

```bash
cd /c/GSE-prototype
D=experiments/20260903-o1-runtime-cost
python3 $D/scripts/summarize.py            # 既定 = with-gse
```

判定表（README より・**閾値はこの repo に根拠を持たない恣意的な値。測った後に動かさない**）:

| 指標 | 合格 | 要対処 |
|---|---|---|
| CPU 平均（アイドル） | < 1% | ≥ 3% |
| CPU 最大 | < 15% | ≥ 30% |
| RSS の傾き | < 5 MB/h かつ 8h 後に < 300MB | ≥ 20 MB/h（リーク疑い） |
| NDJSON / 日 | < 30 MB | ≥ 48 MB（`MAX_BYTES` に当たる） |
| エネルギー影響 | ⚠️ **macOS 専用指標**（`top -stats power`）。Windows では測れない・閾値なし | — |

逸脱したら原因を `notes.md`（`experiments/20260903-o1-runtime-cost/notes.md`）に書く。

### B-4. `env.md` の Windows 行を埋める

```bash
systeminfo | grep -i "OS 名\|OS バージョン\|システム製造元\|システム モデル" 2>/dev/null || systeminfo | head -20
wmic path Win32_Battery get BatteryStatus 2>/dev/null || powershell -Command "Get-CimInstance Win32_Battery" 2>/dev/null
```

- ★ **この機はデスクトップ機（MSI MS-7E66）で `Win32_Battery` が null（バッテリー無し）**。
  `env.md` の「OS (A: Windows)」「機種 / 電源 (Windows)」行にその旨を実測結果とともに記録する
  （★ 「バッテリーが無い＝エネルギー影響/バッテリー系の指標は測定不能」であることを明記する）。
- 測定バイナリのコミットハッシュ・ビルド日時も記録する（B-0 で確認済みのもの）。

### B-5. 完了処理

- [ ] §2 の tasklist 4 項目を `[x]` にする
- [ ] `decisions.md` に「判断4」として、Windows 実機での §2 結果（PASS/要対処の別）と、この機が
      デスクトップ機でバッテリー系指標が測定不能だった旨を記録する
- [ ] ⚠️★★★ **8時間の本番測定で生成される実 O1 セッション NDJSON（`~/Documents/GSE-sessions/gse_o1_*.ndjson`）の扱いを研究者に確認する**。
      本実験は `data.md` の設計上「NDJSON の内容は読まない・`results/` にコピーしない・記録するのはバイト数のみ」だが、
      ⚠️ **元ファイル自体を削除してよいかは前セッションで確定していない**（今回の 8 時間走行は研究者自身の実作業ログを含む実データであり、
      今回のセッションで診断のために作った使い捨てテストファイルとは性質が違う）。★ 削除する場合は必ず一度確認を取ってから。
- [ ] `.steering/_handoff/README.md` の該当行（本メモの行）を「完了」へ更新する
- [ ] git commit（★ `git add -A` を使わない。作業ツリーには常に他タスクの未コミット作業がある可能性がある）

---

## C. ⚠️ 本セッションでやらないこと

- ⚠️ §1・§3（idle 分）を再検証しない（確定済み）
- ⚠️ 対照 (`without-gse`) を回さない（README の裁定）
- ⚠️ 判定の閾値をその場で動かさない（README に固定済み。逸脱は原因を書くだけ）
- ⚠️ バッテリー系指標をこの機（デスクトップ）で無理に測ろうとしない（`Win32_Battery` null が正しい実測結果）
- ⚠️ 素の `cargo build --release` でビルドしない（§A のビルド欠陥を再現するだけ）

---

## D. 完了後

- `windows-orphan-verify` タスク全体（§1/§2/§3）の完了報告を作成し、`/finish-task` を実行する
  （§3 の表示状態 hit-test は「未検証のまま」と明記してよい。`design.md`/`requirement.md` も既にその前提で書かれている）
- 完了したら次タスクへ移る前に `/clear` する
