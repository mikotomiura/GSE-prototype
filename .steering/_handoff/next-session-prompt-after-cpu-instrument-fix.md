# 次セッション開始プロンプト — **計測器を直したあと**（★ 未決 4 件を閉じる）

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ ★★★ **実行マシン: mac**（⚠️ 理由は §0-0）。
> ★ モデル: **Sonnet** で足りる（⚠️ §4 の取り込み方針の判断だけ Opus）。
> ⚠️★★★ **本メモは `next-session-prompt-intake-windows-and-continue.md` の後継である。**

---

===

## §0-0 ★★★ **どのマシンでやるか —— mac**

★ 残っている作業は **ほぼ全部 mac 側**である。

| ★ 作業 | ★ マシン | ⚠️ 理由 |
|---|---|---|
| ★★★ **計測用バイナリを v0.1.33 相当で作り直す**（§3-2） | ⚠️ **mac 必須** | ★ `npx tauri build --target aarch64-apple-darwin` は mac でしか通らない |
| ★ macOS の 8h 再測（§2） | ⚠️ **mac 必須** | ★ 測る対象が mac の GSE |
| ★ スリープ跨ぎ検証（§3） | ⚠️ **mac 必須**・★ **研究者が叩く** | ⚠️ Claude が sleep assertion を握るので**エージェントからは実行できない** |
| ★ G-GEAR の残り取り込み（§4） | ★ どちらでも（mac 推奨） | ★ `analysis/` は OS 非依存。⚠️ 両 OS の検証は CI がやる |
| ★ ブランチ棚卸し（§5） | ★ どちらでも | ★ git だけ |

⚠️★★★ **Windows 側に回すものは、いま無い。**
★ §1（CPU% 規約）は 2026-09-10 に Windows 実機で**決着済み**（PR #173）。
⚠️ 唯一 Windows に残るのは `.steering/20260904-windows-orphan-verify/blockers.md` #3
（★ 測定窓直後のフック飢餓クラスタ・原因未特定）だが、
★ **mac 側の診断バイナリを作り直す方が先**（§3-2）—— ⚠️ 同じ現象を mac で追える体制がまだ無い。

---

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ⚠️ このメモを一次資料にしない

★ 2026-09-10 のセッションで、**自分の測定器を 2 回壊した**（⚠️ 通算 11 回目・12 回目）:

| ★ 手掛かり | ⚠️ 見つかったもの |
|---|---|
| ★ **陽性対照を置いた**（1 コアを飽和させた） | ⚠️★★★ `top -l 2` が **47.6 %** と報告（★ 地上真実 99.7 %）＝ **8h×2 本の macOS CPU 実測が無効化**された |
| ★ **出力の日付が 11 日前だった** | ⚠️ 点検スクリプトが基線ファイル名の食い違いで `PRE` を空にし、`tail -n +1` で**ログを頭から全部**「基線以降」として出していた |

→ ⚠️★★★ **このメモも同じ確率で間違っている。**
→ ★ **レート系（%・/秒・/日）の指標は、使う前に必ず陽性対照で校正する。**
  `bash experiments/20260903-o1-runtime-cost/scripts/calibrate-cpu.sh`

### 0-2. ★ 現状を測る（⚠️ 下は「書かれた時点」の値）

```bash
cd /Users/johnd/GSE-prototype
git fetch --all --prune && git checkout main && git pull --ff-only
git log --oneline -1                    # ★ 2026-09-10 時点 0b211d2 (PR #170)
git tag --sort=-v:refname | head -1     # ★ v0.1.33
bash scripts/check-o1-release-readiness.sh | tail -3   # ★ 20 件 / 0 件
pgrep -x gse-next && ps -o etime= -p $(pgrep -x gse-next)   # ⚠️ **止め忘れが続いているかもしれない**
ls -l ~/Documents/GSE-sessions/gse_o1_*.ndjson             # ⚠️ 2026-09-10 11:50 時点で 7.8 MB
```

### 0-3. ★ 先に読む一次資料（⚠️ この順で）

1. `experiments/20260903-o1-runtime-cost/notes.md` の **末尾 2 節**
   （★「§ 2026-09-10 の訂正」と「8.87 時間連続 run」）
2. `.steering/20260910-intake-windows-and-cpu-convention/decisions.md`（★ D1〜D3）
3. `.steering/20260904-windows-orphan-verify/blockers.md`（★ #1 は方針が決まった・#2 は閉じた）

---

## §1 ✅ **決着済み** —— Windows の CPU% 規約は **1 コア = 100 % 基準**

⚠️★★★ **本項は 2026-09-10 に Windows 実機で決着した（PR #173）。★ 蒸し返さないこと。**

★ 1 コアを `while($true){}` で飽和させたプロセスの `CookedValue`（論理プロセッサ **16**）:

| # | CookedValue |
|---|---|
| 1 | **99.9586042201256** |
| 2 | **100.392972071849** |
| 3 | **97.1371636451479** |

→ ★ **≒ 100**（⚠️ ≒ 6.25 ではない）＝ **1 コア = 100 % 基準**。macOS と同じ規約。
★ Microsoft の逐語（「the % Processor Time reported for the **Process object can report
values over 100 percent**」）が**実測で裏付けられた**。

⚠️ **`×16` は誤り。「macOS 換算 33.0 % で FAIL 相当」は撤回済み。**
★ `run.sh` の `CPU_BASIS` は `one_core_100` に確定、`sample-windows.sh` の誤ったコメントも訂正済み。

### ★★★ で、結局 CPU はどうなのか（★ 両 OS を同じ基準で並べる）

| ★ OS | CPU 平均 | 閾値 < 1 % に対して |
|---|---|---|
| Windows（v0.1.33・8h） | **2.06 %** | ⚠️ **MARGINAL** |
| macOS（v0.1.31・直した計器・定常 6 分） | **1.31 %** | ⚠️ **MARGINAL** |

→ ★ **両 OS とも MARGINAL。** ⚠️ どちらも「軽い」とは言えず、**「FAIL」でもない**。
⚠️ macOS の 8h は **§2 で測り直し中**（★ 6 分の値は参考）。

## §2 ⚠️★★★ 未決 —— **macOS の 8h を直した計器で測り直す**

⚠️ **旧 2 本の CPU 値は無効**（★ `summarize.py` が `meta.json` の `cpu_source` 不在を見て
**CPU 2 指標を判定しない**ようにしてある）。★ 直した計器で回したのは **6 分だけ**。

| ★ 出どころ | CPU 平均 |
|---|---|
| ⚠️ 旧 8h（壊れた計器） | 0.95 / 0.98 % |
| ⚠️ ★ ×2.08 の**推定** | ≈ 2.0 % |
| ★ 直した計器の**直接実測**（定常 6 分） | **1.31 %** |

⚠️★★ **推定と実測が一致していない。** → ★ **8h を 1 本回して決める。**

```bash
cd experiments/20260903-o1-runtime-cost
# ⚠️ サンプラを先に起こしてから GSE を起動する（★ 起動前の基線が要る）
GSE_COST_LABEL=with-gse-YYYYMMDD-macos-8h nohup bash run.sh with-gse > /dev/null 2>&1 & disown
```

⚠️ **`GSE_COST_LABEL` を必ず付ける**（★ 付けないと `results/with-gse` に当たり、
ガードが `meta.json` を見て `exit 3` する ＝ 設計どおりだが回らない）。

---

## §3 ⚠️★★★ 未決 —— **スリープ跨ぎ検証は 1 度も試せていない**

★ 2026-09-10 に試みて**失敗した**。⚠️ **測定器の欠陥ではなく、環境が寝られなかった**:

| ★ 主体 | ★ アサーション |
|---|---|
| ⚠️★★★ `caffeinate -i -t 300`（親 = **`claude`**） | `PreventUserIdleSystemSleep` |
| ⚠️★★★ `pid …(Claude)` | **`NoIdleSleepAssertion named: "Electron"`** |
| ⚠️ Safari の **WebKit Media Playback** ×3 / `coreaudiod` | 同上 |

→ ⚠️★★★ **Claude Code / Claude デスクトップが動いている間、この Mac は寝ない。**
★ `pmset sleepnow` は `0xe00002e2`（rc=71）で拒否される。
→ ★ **蓋を閉じる**方が確実（⚠️ 検証としてはどちらでも成立する）。

★ 手順 `.steering/20260910-intake-windows-and-cpu-convention/sleep-test-procedure.md`。
⚠️ **基線を採り直してから寝かせること**（★ `post-wake-check.sh` は基線が無いと `exit 2` で止まる）。

### ⚠️★★★ §3-2 —— **「次の Down で決着する」は成立しない**（★ 2026-09-10 に反証した）

⚠️ 前のセッションまでの計画は逐語で「診断 `tap_enabled` を入れたので**次の Down のログで
機序が決着する**まで待つ」だった。→ ⚠️★★★ **走っているバイナリに `tap_enabled` が無い。**

| ★ 文字列 | `strings` の件数 |
|---|---|
| `starved_ms` / `rehook_requested` / `NOT delivering events` / `tap_mode` / `input_monitoring` | ★ **全部あり**（★ **陽性対照**） |
| ⚠️ **`tap_enabled`** | ⚠️ **0** |

★ 理由は日付: ⚠️ バイナリは **v0.1.31（mtime 2026-09-03）**、
診断が入ったのは **`cb1aa25`（2026-09-05）**。
★ NDJSON の **`meta.app_version = 0.1.31`** でも裏を取った。
→ ⚠️★★★ **すでに 3 回の Down を無駄にしている**（09-05 / 09-09 / 09-10）。

★ **2 段目の防御も動いていない**: `hook_health` **14 件すべて `rehook=false`**
（⚠️ `alive=false` の 2 件を含む）。★ `cb1aa25` 逐語「`request_reinstall` が定数 false だった」と一致。

★ **頻度を初めて数えた**: 作業中の **31 分で 10 件・うち Down 2 件**（★ 約 3 分に 1 回）。
⚠️ 打鍵の無い 8.6 時間は **0 件** → ★ **検知は活動量に強く依存する**
（⚠️「8 時間に 1 回」は打鍵が疎だっただけ）。★ ただし `dropped` は**全件 0**。

⚠️★★★ **もう 1 つの帰結 —— 測っている版が配布物と違う**:
★ macOS の稼働コストは全部 **v0.1.31**、Windows と**被験者配布は v0.1.33**。
→ ⚠️ **macOS 側は「配布物の稼働コスト」を測っていない。**

### ★ やること（⚠️ これが先。待っても何も分からない）

⚠️★★★ **ビルドは 8h 計測を汚す。** ★ 一次資料: notes.md「**CPU 最大 4.30 % は CI 窓の中だけで
出た値である。窓を除くと 1.80 %**」→ ★ **計測を止めてからビルドすること。**

```bash
# ① ⚠️ まず現状を機械で見る（★ 今日の実害をそのまま再現する）
bash scripts/check-measurement-binary.sh
#    → ⚠️ rc=3 / 版ずれ (repo 0.1.33 vs app 0.1.31) ＋ tap_enabled 0 件 が出るはず

# ② ★ 計測を止める（⚠️ 走っていれば）
pkill -f sample-macos.sh

# ③ ★ 作り直す
npx tauri build --bundles app --features package --target aarch64-apple-darwin

# ④ ⚠️★★★ **差し替える前にゲートを通す**
bash scripts/check-measurement-binary.sh src-tauri/target/aarch64-apple-darwin/release/bundle/macos/gse-next.app
#    → ★ 版一致 ＋ tap_enabled が 1 件以上 ＋ 陽性対照 4/4 でなければ差し替えない

# ⑤ ★ 差し替えて GSE を再起動し、**もう一度**ゲートを通す
#    → ⚠️ ③ の照合が「走っているのは別の版」と言うなら **再起動できていない**
bash scripts/check-measurement-binary.sh
```

⚠️★★★ **`strings` で 0 件を見ても、それだけで「無い」と書かない。**
★ ゲートは **同じ経路でログに出る文字列 4 つを陽性対照**に置き、
⚠️ **それらが出ることを先に確かめてから**目的の文字列の不在を主張する
（★ 陽性対照が欠けたら `rc=2`＝**判定しない**）。

★ そのうえで次の Down を待つ。

★ 詳細は `.steering/20260910-intake-windows-and-cpu-convention/starvation-diagnostic-finding.md`。

### ⚠️★★★ 陰性対照は **すでに崩れている**

★ 実測: **スリープなしで** GSE 起動の **65 秒後**に `starved_ms=30074`。
→ ⚠️ **復帰直後に飢餓を見ても、スリープが原因とは言えない。**

★ 一方で 8.87 時間の連続 run では `feat` **31,943 行・穴は最大 1 秒・30 秒超 0 個**、
`hook_health` 7 件すべて **`dropped=0`**。
⚠️★★ **ただし「打鍵の取りこぼしは無かった」とは言えない** ——
★ `feat` は打鍵が無くても 1 Hz で出るので、**解析ループの生存しか示さない**。
★ この 8.87 時間の `key` は **160 件だけ**（⚠️ 打鍵が疎だと飢餓の検知自体が疎になる）。

---

## §4 ★ G-GEAR ブランチの残り（★ 案 C）

★ `origin/feat/resumption-outcome-arbitration` から **Windows 実測ぶんだけ**を取り込み済み（案 B 完了）。
⚠️ **残り 4 系統は未取り込み**:

| 系統 | ⚠️ 取り込み前に見るもの |
|---|---|
| ★ ADR-023〜028 | ★ 本文は書き換えない規約。⚠️ 番号の衝突を先に見る |
| ⚠️★★★ `analysis/metrics.rs` **+909 行** | ⚠️ **`recovery` → `pflow_exit` の改名**。★ `HMM_VERSION` の bump が要るか／⚠️ **ゴールデンが割れないか**（`gse-replay --snapshot`） |
| ★ 表現層（層 A 試視ハーネス・周辺視ブロック） | ★ ADR-021 / ADR-022 まで読む（⚠️ ADR-017 単独では古い契約を掴む） |
| ★ ツール（`secrets-filter.sh` の穴 4 件・`md2pptx.py` +1313 行・`svg2png.py`） | ⚠️ `scripts/secrets-filter-test.sh` を**走らせる** |

★ `scripts/build_analysis_db.py` を入れるなら ⚠️ **schema parity**（`emit_schema` ↔ `schema/current.json`）。

---

## §5 ★ ブランチ棚卸し（⚠️ **私は 1 本も消していない**）

★ 実物まで降りて調べた結果は `decisions.md` **D3**。

| ブランチ | ★ 判断 |
|---|---|
| `docs/handoff-post-pr132` | ★ **削除可**（⚠️ 失うのは古い引き継ぎメモの一版だけ・後継が 20 本以上ある） |
| `feature/phase1-reminder-and-dashboard` | ⚠️ **そのままでは消さない** —— ★ コードは **main が上位互換**（関数 84→86・branch 固有関数 **0**・固有行は 7 行＝**べた書き exec URL** で main は意図的に Script Properties へ移した）。⚠️ だが `.steering/20260708-*` **3 ディレクトリ**＋ `_handoff/next-session-prompt-phase1-prep.md` が **main に無い** → ★ **記録だけ救出してから削除** |
| `feat/phase1-cindex-attainability` | ⚠️ 遅れ 191。★ cherry-pick か作り直し |
| `docs/g1-verdict-and-friction-survey` | ⚠️ 遅れ 261。★ 文献カードは `citation-ssot` の **採番衝突を先に見る** |

---

## §6 ★ もう決着したもの（⚠️ 蒸し返さない）

| 項目 | ★ 結論 |
|---|---|
| ⚠️ macOS の CPU 計測器 | ★ **壊れていた**（`top -l 2` が 0.48 倍）。**直して校正済**（`calibrate-cpu.sh`） |
| ⚠️ Windows の「×16 → FAIL 相当」 | ★ **撤回済**（⚠️ 実機実測だけが残っている） |
| ★ 起動時のコスト | ★ **初めて測れた**: 起動直後 **2.08 %** / 定常 **1.31 %**（差 +0.77 pt） |
| ★ 指標 5（NDJSON/日） | ★ **確定**。3 本が **20.1〜20.5 MB/日**に収束（★ macOS 今回は前提なしで確定） |
| ⚠️ `run.sh` の上書きガード | ★ **閉じた**（blockers #2。`meta.json` 等も見る・`GSE_COST_LABEL` 追加） |
| ⚠️ `.gitignore` の穴 | ★ `ndjson-size-start.tsv` を追加（⚠️ 既追跡分は意図して残す） |
| ★ O1 の配布ゲート | ★ **20 件 / 0 件**（⚠️ ただし **CPU 2 指標は「要再測」に降格**した。★ 配布可否は研究者判断） |
| ⚠️★★★ starvation の機序 | ⚠️ **「待つ」は成立しない**（★ 2026-09-10 に実測・下の §3-2） |

## §7 ★ 触らないもの

- ⚠️ 事前登録の凍結節（`docs/preregistration-v0.3.md §3`）
- ⚠️ `Form_G1/` / `Form_O1/`（★ 変えるなら**再デプロイまでが 1 単位**）
- ⚠️ `docs/adr/` の**既存本文**（★ 新しい ADR を足す規約）
- ⚠️ **G1 の zip**（Aug 版で確定）/ Drive の O1 zip（v0.1.33 で確定）

## §8 ★ 完了報告に必ず書くこと

- [ ] ⚠️ **外界に触った操作**を列挙（★ GSE 起動/停止・ファイル削除・push・merge・タグ・実送信・Drive）
- [ ] ⚠️ **未検証が残っているうちは「問題なし」と書かない**（★「N 件中 M 件を実測、未検証 K 件」）
- [ ] ⚠️ **書いたつもりのものが書かれたか** `git show --stat` で確かめる
- [ ] ⚠️ **緑を見たら「何が走ったか」をログで確かめる**
      （★ 2026-09-10 実測: `ci.yml` に `experiments` はコメント 2 箇所のみ ＝
       ⚠️ **CI は `summarize.py` もサンプラも 1 度も走らせていない**。
       ★ ただし `check-shell-portability.sh` は `.sh` を repo 全体で見ている）
- [ ] ⚠️★★★ **レート系の指標を出したら、陽性対照で校正したかを書く**

## ⚠️★★★ 作業規約（★ CLAUDE.md より・省略しない）

1. `.steering/[YYYYMMDD]-[task-name]/` に `requirement.md` / `design.md` / `tasklist.md` を作る。
2. 必須 Skill を読んでから手を動かす: `verify-before-claiming` / `reproducibility-discipline` /
   `data-privacy` / `git-workflow` /（フックを触るなら）`hook-constraints`。
3. ⚠️★★ **「緑だから正しい」と書かない。** 検査は**正常 / 不在 / 壊れ**の 3 状態で試し、
   ★ **陰性対照**（壊していないものが緑のままか）も置く。
4. ⚠️ **main に直接コミットしない**。
5. ⚠️★★★ **`rm -rf` の前に必ず `git status` でそのパスを見る**。
