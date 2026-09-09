# 次セッション開始プロンプト — **G-GEAR の成果を取り込み、mac 側の続きへ**

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Opus**（⚠️ §1 の判定と §2 のマージ方針は推論深度が要る）。
> ⚠️★★★ **本メモは `next-session-prompt-post-windows.md` の後継である。**
> ★ 向こうは **G-GEAR が 2026-09-10 に実測結果で更新済み**なので、**両方読む**。

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ⚠️ このメモを一次資料にしない

★ 2026-09-04〜08 の mac 側セッションで、**自分の測定器を 9 回壊した**。
⚠️ G-GEAR 側も 2026-09-10 に「**チェックリストに書いてあった落とし穴を自分で踏んだ**」と
記録している。→ ⚠️★★★ **このメモも同じ確率で間違っている。**

★ 直近で効いた気づき方（⚠️ どれも「読んだ」ではなく「測った/対照を置いた」）:

| ★ 手掛かり | ⚠️ 見つかったもの |
|---|---|
| ★ **実行時間が想定と違う**（10.5 s vs 14.7 s） | ⚠️ CI でテストが **skip** されていた |
| ★ **docs だけの PR が赤** | ⚠️ `init_hook` に多重起動の門が無く **SIGSEGV** |
| ★ **陽性対照を置いた**（旧版にもある文字列） | ⚠️ `grep -c "^str$"` のアンカーで**全部 0** の偽陰性 |
| ★ **値が半分に減った** | ⚠️ 集計が 1 分のスモークを 1 日ぶんとして混ぜていた |
| ★ **符号・桁が変** | ⚠️ 「直したつもり」が 3.4 倍過小 → 1/120 に悪化 |

### 0-2. ★ 現状を測る（⚠️ 下は「書かれた時点」の値）

```bash
cd /Users/johnd/GSE-prototype
git fetch --all --prune && git checkout main && git pull --ff-only
git log --oneline -1                    # ★ 2026-09-10 時点 718225f (PR #167)
git tag --sort=-v:refname | head -1     # ★ v0.1.33
bash scripts/check-o1-release-readiness.sh | tail -3   # ★ 20 件 / 0 件
git log --oneline origin/main..origin/feat/resumption-outcome-arbitration | wc -l   # ⚠️ 88 のはず
```

### 0-3. ★ 先に読む一次資料（⚠️ この順で）

1. `.steering/_handoff/next-session-prompt-post-windows.md`
   （★ **G-GEAR が §1 を実測結果で書き換えている**。⚠️ §5 に新しい積み残し 3 件）
2. `experiments/20260903-o1-runtime-cost/notes.md` の **「6指標×2OS 一覧」**節
3. `.steering/20260904-windows-orphan-verify/blockers.md`（★ Windows 側の起票 2 件）

---

## §1 ⚠️★★★ 最優先 —— **Windows の「CPU FAIL 相当」は本当か**

### ★ 何が主張されているか

★ G-GEAR は Windows の CPU を **macOS 基準へ換算すると FAIL 相当**だと記録した:

| 指標 | Windows 実測 | ★ 主張された換算 |
|---|---|---|
| CPU 平均 | **2.06 %** | ⚠️ ×16 → **33.0 %**（★ 閾値 < 1 %） |
| CPU 最大 | **9.32 %** | ⚠️ ×16 → **149.1 %**（★ 閾値 < 15 %） |

★ 根拠は `sample-windows.sh` のコメント逐語:
「Get-Counter は**全コアに対する %**を返すので、コア数で割って 1 コア相当に揃えない」

### ⚠️★★★ **この前提を鵜呑みにしない。私（mac 側）は疑っている。**

⚠️ Windows の **PerfMon カウンタ `\Process(name)\% Processor Time` は、
一般に「全コアの合計」= マルチコア機で 100 % を超えうる**値である
（★ Task Manager が見せる「コア数で割った %」とは**別物**）。
→ ★ もしそうなら **macOS の `top`（1 コア = 100 %）と同じ規約**であり、
⚠️ **×16 は 16 倍の過大評価**で、「FAIL 相当」は**偽の警報**になる。

⚠️ **私はこれを Windows で確かめていない**（★ この Mac に `powershell.exe` が無い）。
→ ⚠️★★★ **どちらが正しいかは、次のセッションが Windows で実測して決める。**

### ★ 決着させる実験（⚠️ 5 分・Windows 側に依頼する）

```powershell
# ★ 1 コアを 100% 占有するプロセスを作る
$job = Start-Process powershell -PassThru -ArgumentList '-NoProfile','-Command','while($true){}'
Start-Sleep 5
# ★ 同じカウンタで読む（⚠️ サンプラと同じ式にすること）
(Get-Counter "\Process(powershell*)\% Processor Time").CounterSamples |
  Select-Object InstanceName, CookedValue
Stop-Process -Id $job.Id
# ★ コア数も出す
(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
```

| ★ 読み値 | ⚠️ 意味 | ★ 帰結 |
|---|---|---|
| **≒ 100** | ★ 合計基準（macOS `top` と同じ） | ⚠️ **×16 は誤り。Windows の CPU 平均 2.06 % は PASS**。★ 「FAIL 相当」の記述を訂正する |
| **≒ 6.25**（= 100/16） | ★ コア数で割られている | ★ **G-GEAR の換算が正しい**。⚠️ **CPU は本当に FAIL** → 配布判断をやり直す |

⚠️★★ **どちらに転んでも、`sample-windows.sh` と `summarize.py` に
「どちらの規約で記録したか」を列か meta に残す**こと（★ 今は**コメントにしか無い**）。
→ ⚠️ 次に読む人がまた同じ推測をする。

### ⚠️ これが効く範囲

★ 「FAIL 相当」が正しければ、⚠️ **O1 の配布ゲート（20/0）は Windows について嘘をついている**
（★ ゲートは CPU の OS 間比較を見ていない）。→ ⚠️ **配布可否の再判断が要る。**

---

## §2 ★ G-GEAR ブランチの取り込み（⚠️ **単純マージではない**）

### ⚠️ 規模を先に見る

```bash
git log --oneline origin/main..origin/feat/resumption-outcome-arbitration | wc -l   # ⚠️ 88
git diff --stat origin/main...origin/feat/resumption-outcome-arbitration | tail -1  # ⚠️ 199 files / +28054
```

⚠️★★★ **Windows 実測だけのブランチではない。** ★ 中身は少なくとも:

| 系統 | 内容 |
|---|---|
| ★ ADR | **ADR-023〜028**（★ 出口への結合 / 招待の配送 / 層 A に数値を添えない / チャネルの生存） |
| ★ 実装 | `analysis/metrics.rs` **+909 行**（`receipt_free_resumption` 追加・`recovery` → `pflow_exit` 改名） |
| ★ 実験 | `experiments/20260906-p321-resumption-baseline/`（★ 新規） |
| ★ 表現層 | 層 A 試視ハーネス・周辺視ブロック |
| ★ ツール | `secrets-filter.sh` の穴 4 件・`md2pptx.py` **+1313 行**・`svg2png.py` |
| ★ 本タスク | Windows 実測（`.steering/20260904-windows-orphan-verify/`） |

### ⚠️ 取り込み方の判断（★ 研究者に諮ること）

⚠️ **私（次セッション）が独断でマージしない。** ★ 選択肢:

| 案 | ★ 内容 | ⚠️ 代償 |
|---|---|---|
| **A** | ★ **PR を 1 本立てて丸ごとマージ** | ⚠️ 28k 行を 1 度に入れる。★ CI は通るはずだが、**レビューの粒度がゼロ**になる |
| **B** | ★ **Windows 実測ぶんだけ cherry-pick** して先に入れ、残りは別 PR | ★ §1 の判定を先に進められる。⚠️ ブランチが長生きし続ける |
| **C** | ★ 系統ごとに PR を割る（ADR / metrics / 表現層 / ツール / 実測） | ★ 一番きれい。⚠️ **手間が大きく、依存順序を解く必要**がある |

★ **推奨は B → C**（⚠️ §1 が配布可否に直結するので、実測ぶんを最短で main に載せる）。

### ⚠️ マージ前に必ず見るもの

- ⚠️ `analysis/metrics.rs` の **識別子改名**（`recovery` → `pflow_exit`）→ ★ **`HMM_VERSION` の
  bump が要るか**／⚠️ **ゴールデンが割れないか**（`gse-replay --snapshot`）
- ⚠️ `scripts/build_analysis_db.py` と `gse-dataset/metrics/**` の変更 →
  ★ **schema parity**（`emit_schema` と `schema/current.json`）
- ⚠️ `secrets-filter.sh` の変更 → ★ `scripts/secrets-filter-test.sh` を**走らせる**

---

## §3 ⚠️ Windows 実測が残した宿題 3 件

★ `.steering/20260904-windows-orphan-verify/blockers.md` に起票済み。

| # | 何 | ★ 対処 |
|---|---|---|
| 1 | ⚠️★★★ **CPU% の OS 間定義差を正規化していない**（HIGH） | ★ **§1 の実験で規約を確定してから**直す（⚠️ 先に直すと間違った向きに直す） |
| 2 | ⚠️ `run.sh` の上書きガードが **`samples.tsv` の有無しか見ない**（MEDIUM） | ★ `samples.tsv` は `.gitignore` 済みなので、⚠️ **git 管理下の `meta.json` / `finished_utc` を黙って上書きできる**（★ 実際に踏んで `git checkout` で復旧）。→ ★ ガードを `meta.json` にも広げる **or** 既定のディレクトリ名に **os を含める** |
| 3 | ⚠️ **測定窓直後のフック飢餓クラスタ**（30 s × 6・120 s 完全停止 × 1・原因未特定） | ⚠️★★ **§4 のスリープ検証で「復帰直後に飢餓」を見ても、スリープが原因と即断しない** —— ★ Windows では**通常稼働中**にも同型が起きている |

---

## §4 ★ mac 側の残り（⚠️ 優先度順）

| # | 何 | ★ 見積 | ⚠️ 注意 |
|---|---|---|---|
| **A** | ⚠️★★★ **スリープ跨ぎの検証** | ★ 30 分 | ★ 手順は `next-session-prompt-post-windows.md` **§2-1**（★ 疑う対象 5 つ・陰性対照つき・python は 3 状態で検査済み）。⚠️ **完全な空白**であり、⚠️ ノート PC の研究で**毎日通る経路**である |
| **B** | ★ 起動時の山を **1 秒間隔**で測る | ★ 5 分 | `GSE_COST_DURATION_S=300 GSE_COST_INTERVAL_S=1`。⚠️ **サンプラを先に起こしてから GSE を起動**。★ 両 OS とも 35 s 間隔では 1.5 s の走査を拾えないと実測済み |
| **C** | ★ 未マージ 2 ブランチの処遇 | ★ 30 分 | `feat/phase1-cindex-attainability`（遅れ 172）/ `docs/g1-verdict-and-friction-survey`（遅れ 242）。⚠️ 単純 merge は危険 |
| **D** | ★ 廃棄可 2 ブランチ | ★ 5 分 | `docs/handoff-post-pr132`（遅れ 136）/ `feature/phase1-reminder-and-dashboard`（遅れ 713）。⚠️ **消す前に「先」の中身が main にあるか確かめる** |
| **E** | ⚠️ G1 の文書の食い違い | ★ 1 時間 | ★ **印刷用同意書 docx が旧版**（⚠️ 2026-09-08 に md を直したので**さらにずれた**）／⚠️ **所要時間が 3 通り**（protocol 62 分 / consent・guide 70 分 / guide「1 時間ほど」）／`validate_blocks.py --dataset` が **17 件で赤** |

---

## §5 ★ もう決着したもの（⚠️ 蒸し返さない）

| 項目 | ★ 結論 |
|---|---|
| O1 の配布ゲート | ★ **20 件 / 0 件**（⚠️ ただし §1 が覆せば再判断） |
| O1 の配布物 | ★ **v0.1.33** が Drive に配備済み（★ サイズ・更新時刻を秒まで照合） |
| 受け口の `MAX_BYTES` | ★ **32 MB** で**再デプロイ済み**（⚠️ 実測: 33 MB → `too large`・陽性対照つき） |
| `TIMEOUTTEST_*` | ★ **7 本ゴミ箱へ**（⚠️ 削除前に受け口フォルダの全件を見て本物 0 件を確認） |
| G1 の計器の版 | ★ **Aug 版のまま**（研究者判断・既収集 3 名と揃える）。⚠️ **O1 と版が違うことを承知の上** |
| G1 の同意文書 | ★ 空欄 **0 件**（研究責任者 / 連絡先 / ⚠️ 謝礼は「**ありません**」と言い切り） |
| starvation の追加対処 | ⚠️★★★ **やらない** —— ★ 診断 `tap_enabled` を入れたので**次の Down のログで機序が決着する**まで待つ |
| CI での層 2/層 3 | ★ **実際に走っている**（`decisions.md` **D5 の訂正**を読むこと。⚠️ 権限は外れうるので門は残す） |

---

## §6 ★ 触らないもの

- ⚠️ 事前登録の凍結節（`docs/preregistration-v0.3.md §3`）
- ⚠️ `Form_G1/` / `Form_O1/`（★ GAS は実物と同期済み。★ 変えるなら**再デプロイまでが 1 単位**）
- ⚠️ `docs/adr/` の**既存本文**（★ 新しい ADR を足す規約）
- ⚠️ **G1 の zip**（★ Aug 版で確定済み）
- ⚠️ Drive の O1 zip（★ v0.1.33 で確定済み）

## §7 ★ 完了報告に必ず書くこと

- [ ] ⚠️ **外界に触った操作**を列挙（★ GSE 起動/停止・ファイル削除・push・merge・タグ・実送信・Drive）
- [ ] ⚠️ **未検証が残っているうちは「問題なし」と書かない**（★「N 件中 M 件を実測、未検証 K 件」）
- [ ] ⚠️ **書いたつもりのものが書かれたか** `git show --stat` で確かめる
- [ ] ⚠️ **緑を見たら「何が走ったか」をログで確かめる**（★ skip も 0 件マッチも緑になる）
- [ ] ⚠️★★★ **§1 の結論を必ず書く**（★ Windows の CPU は PASS か FAIL か。⚠️ 「分からない」なら**そう書く**）

## ⚠️★★★ 作業規約（★ CLAUDE.md より・省略しない）

1. `.steering/[YYYYMMDD]-[task-name]/` に `requirement.md` / `design.md` / `tasklist.md` を作る。
2. 必須 Skill を読んでから手を動かす: `verify-before-claiming` / `reproducibility-discipline` /
   `data-privacy` / `git-workflow` /（フックを触るなら）`hook-constraints`。
3. ⚠️★★ **「緑だから正しい」と書かない。** 検査は**正常 / 不在 / 壊れ**の 3 状態で試し、
   ★ **陰性対照**（壊していないものが緑のままか）も置く。
4. ⚠️ **main に直接コミットしない**（★ 2026-09-05 に 1 回やってブランチへ移し替えた）。
5. ⚠️★★★ **`rm -rf` の前に必ず `git status` でそのパスを見る**
   （★ 2026-09-10 に G-GEAR 側が違反し、`/finish-task` のレビューで指摘された）。
