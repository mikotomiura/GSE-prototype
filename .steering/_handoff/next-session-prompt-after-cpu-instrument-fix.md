# 次セッション開始プロンプト — **計測器を直したあと**（★ 未決 4 件を閉じる）

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Sonnet** で足りる（⚠️ §2 の取り込み方針の判断だけ Opus）。
> ⚠️★★★ **本メモは `next-session-prompt-intake-windows-and-continue.md` の後継である。**

---

===

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

## §1 ⚠️★★★ 未決 —— **Windows の CPU% 規約を実機で確定する**

★ 状態: **一次資料では決着済み・実機実測は未了**。

★ Microsoft *Examining Processor Time Data* 逐語 ——
「the value of the % Processor Time reported for the **Process object can report values over
100 percent**」→ ★ **1 コア = 100 % 基準**（macOS と同じ）。⚠️ **×16 換算は誤り**。

⚠️ ただし `run.sh` は `cpu_pct_basis` を **`one_core_100_unverified`** のままにしてある。

### ★ やること（⚠️ 5 分・Windows 側）

★ 手順は `.steering/20260910-intake-windows-and-cpu-convention/windows-cpu-convention-probe.md`。
★ busy-loop に同じカウンタを当て、**≒100 なら合計基準 / ≒6.25 なら正規化基準**。

★ 決着したら:
1. `run.sh` の `CPU_BASIS="${GSE_COST_CPU_BASIS:-one_core_100_unverified}"` を確定値へ
2. `sample-windows.sh` の**古いコメント**（「全コアに対する % を返す」）を直す
   —— ⚠️ **このコメントが誤判定の発生源だった**
3. `notes.md` に実測値を追記（⚠️ 「未実測」の記述を消す）

### ⚠️ どちらに転んでも動かないこと

★ Windows の 2.06 % は**そのままでも閾値 < 1 % 超 ＝ MARGINAL**。
→ ⚠️ 「Windows の CPU は PASS」とは書けない。★ 覆るのは **FAIL 相当か MARGINAL か**だけ。

---

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
| ⚠️ starvation の機序 | ★ **まだ待つ**（`tap_enabled` の診断が入っている。⚠️ 次の Down のログで決着させる） |

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
