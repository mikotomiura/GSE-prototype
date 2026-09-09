# 次セッション開始プロンプト — **Windows の実測が終わったあと**（mac 側で再開する）

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Sonnet** で足りる（⚠️ §3 の研究設計の判断だけ Opus）。
> ⚠️★★★ **Windows 側の作業が終わってから**開くこと（★ §1 が Windows の結果を前提にする）。

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ⚠️ このメモを一次資料にしない

★ 2026-09-04〜05 のセッションで、**自分の測定器を 9 回壊した**。⚠️ **このメモも同じ確率で間違っている。**

| # | 壊れ方 | ★ どう気づいたか |
|---|---|---|
| 1 | 集計が 7・8 列目（`energy_impact`）を**読んでいなかった** | ★ 8 時間回す**前**にコードを読んだ |
| 2 | `ndjson_mb_per_day` が **1 分のスモークを 1 日ぶん**として平均に混ぜた（5.98 ← 真値 20.5） | ★ 1 回目の 11.05 から**半分に減った**のが変だった |
| 3 | ⚠️ **2 を直したつもりが悪化**（0.17＝真値の 1/120） | ★ 直した直後に値を見た |
| 4 | ⚠️ **Windows サンプラが 6 列**しか出さない（ヘッダは 8 列） | ★ 引き継ぎを書く直前に点検した |
| 5 | ⚠️ 結合テストが **CI で skip** されていたのに緑（★ skip はログに残らない） | ★ **実行時間 10.5 秒**が skip の待ち時間と一致した |
| 6 | ⚠️ `grep -c "^str$"` のアンカーで**全部 0**（★ 実在する文字列まで 0） | ★ **陽性対照**（旧版にもある文字列）を置いた |
| 7 | ⚠️ `strings` で**関数名**を探した（★ release ビルドには残らない） | ★ 同上 |
| 8 | ⚠️ starvation の実害を **1〜2 割**と誤報告（★ 実際は誤検知の型） | ★ 研究者の指摘 → `liveness.rs` を読み直した |
| 9 | ⚠️ バックグラウンド監視が 2 回とも `[killed]`（★ 計測自体は無傷） | ★ 生死を別途 poll した |

→ ⚠️★★★ **異常値・全件一致・符号の変な値を見たら、まず測定器を疑う。**
→ ⚠️ **「直した」と言った直後に、直した器で値を見る。**
→ ⚠️ **緑を見たら「何が走ったか」をログで確かめる**（★ skip も 0 件マッチも緑になる）。

### 0-2. ★ 現状を測る（⚠️ 下は「書かれた時点」の値）

```bash
git checkout main && git pull --ff-only
git log --oneline -3                                   # ★ 2026-09-05 時点 a700bdc
git tag --sort=-v:refname | head -2                    # ★ v0.1.32 が最新
bash scripts/check-o1-release-readiness.sh | tail -4   # ★ 20 件 / 0 件（✅ 配布してよい）
ls ~/Documents/GSE-sessions/gse_o1_*.ndjson 2>/dev/null || echo "★ O1 ログは 0 本（正しい）"
ls ~/.gse/o1_consent_ack                               # ⚠️ **戻してある**（自動提出は再武装済み）
```

### 0-3. ★ 先に読む一次資料

- `experiments/20260903-o1-runtime-cost/notes.md`（★ **末尾の訂正節まで読む**）
- `experiments/20260801-controlled-friction-task/o1-upload-timeout-measurement.md`
- `.steering/20260905-macos-hook-rehook-second-defense/decisions.md`（★ D5＝CI では skip される）

---

## §1 ⚠️★★★ 本セッションの主題 —— **Windows の結果を受けて締める**

### ⚠️★★★ 2026-09-10 追記: Windows実測は完了した。結果と、本節が事前に警告していた通りに実際踏んだ落とし穴を記録する

★ Windows側は最終的に `.steering/20260904-windows-orphan-verify/` タスクとして
`next-session-windows-runtime-cost-8h.md`（本ファイルが指す上記メモの後継・§2だけを
切り出した引き継ぎ）で実施された。**「返ってきたものを鵜呑みにしない」の実践結果を含め、
下記1-1の各項目にチェック済みの答えを埋めた。**

### 1-1. ★ Windows から返ってくるはずのもの（★ 2026-09-10 実測で確認済み）

★ Windows 側には（最終的に）`.steering/_handoff/next-session-windows-runtime-cost-8h.md`
を渡した。⚠️ **返ってきたものを鵜呑みにしなかった結果、以下が判明した**:

| 確認 | 結果 |
|---|---|
| ★ `samples.tsv` が **8 列**か | ✅ **8列を確認**（`cpu_pct`/`rss_kb`/`threads`/`battery_pct`/`rss_alt_kb`/`energy_impact`/`ref_energy_impact`） |
| ★ 7・8 列目が **空**か（`0` ではない） | ✅ **空を確認**（Windowsにはエネルギー影響相当の指標が無いため） |
| ★ 集計が「**windows では測れない**」と出すか | ✅ `summarize.py`が「⚠️ エネルギー影響は**windowsでは測れない**」と正しく出した |
| ⚠️ **CPU% をそのまま mac と比べていないか** | ⚠️★★★ **これを最初は見落とした。** Windows実測結果を書き終えて`/finish-task`まで済ませた**後**、ユーザーに「引き継ぎ内容が反映されているか」と問われて本ファイルを読み返し、この行の警告どおりの見落としを自分がしていたことに気づいた。`sample-windows.sh`は全16論理コア基準の%をそのまま出しており、macOSの1コア=100%基準に換算すると**CPU平均2.06%→33.0%、最大9.32%→149.1%**とFAIL相当になる。`experiments/20260903-o1-runtime-cost/notes.md`の「6指標×2OS一覧」節と`decisions.md`判断5に訂正記録済み。**教訓: このチェックリストは実際に効く。次回は最初から全項目を確認すること** |
| ★ 孤児回収の逐語（`O1 orphan sweep ... closed=N failed=0`） | ✅ 確認済み（`.steering/20260904-windows-orphan-verify/evidence-s1-A-B.md`。§1は本タスクの前半で別途実機確定済み） |

⚠️★★★ **本節に書かれていなかったが実際に踏んだ追加の落とし穴**（次にWindows実測をする
セッションのために記録）:
1. **`run.sh`の上書きガードは`samples.tsv`しか見ない**ため、別OS実測の`meta.json`/`finished_utc`
   （git管理下）を黙って上書きできてしまう。今回はmacOS 2回目実測のメタデータを上書きしかけ、
   `git checkout`で復旧した（`blockers.md`にMEDIUM起票。CPU%正規化の方はHIGH起票）。
2. **測定窓の直後（GSE稼働継続中）にフック飢餓クラスタ**（30秒×6・120秒完全停止×1）が発生した。
   当初「窓内1回のみ・以降再発なし」と誤記し、`/finish-task`のレビューで訂正した。
   ⚠️ **§2-1のスリープ跨ぎ検証で「復帰直後にフック飢餓が出た」場合、スリープが原因と即断しない
   こと**——Windows側では通常稼働中（スリープと無関係）にも同種のクラスタが起きている
   （原因未特定・CPU/スケジューラ競合の可能性を含め相関のみ記録）。

### 1-2. ★ 締め方（★ 完了済み）

★ Windows の結果を `experiments/20260903-o1-runtime-cost/notes.md` に**追記した**
（「結果（2026-09-09/10・Windows・初実測）」節）。⚠️ 「6 指標 × 2 OS」の表も
**埋まっている所と空いている所が一目で分かる形**で作成した（notes.mdの当該節の直前、
「★★★ 6指標×2OS 一覧」見出し）。⚠️ 「問題なし」とは書いていない —— 「6指標中5指標で
両OSの数値が揃ったが、うちCPU平均/CPU最大はOS間定義差により単純比較不可（Windows換算
FAIL相当）、エネルギー影響はWindowsで原理的に測定不能、起動時のコスト/バッテリーは
両OS未測定」と明記した。詳細は`notes.md`該当節・`decisions.md`判断4/5・
`.steering/20260904-windows-orphan-verify/blockers.md`（次タスクへのTODO）を参照。

---

## §2 ★ mac 側でできる小さな残り（⚠️ 優先度順）

| # | 何 | ★ 見積 | ⚠️ 注意 |
|---|---|---|---|
| **A** | ⚠️ **起動時の山を 1 秒間隔で測る** | ★ 5 分 | ★ 8 時間の再測は**不要**。`GSE_COST_DURATION_S=300 GSE_COST_INTERVAL_S=1` で 1 本。⚠️ **サンプラを先に起こしてから GSE を起動**する（★ 35 s 間隔では孤児回収の 1.5 秒の山を拾えないと実測済み） |
| **A2** | ⚠️★★★ **スリープ跨ぎの検証**（★ 下の §2-1 に手順） | ★ 30 分 | ⚠️ **完全な空白である** —— ★ grep で確認: スリープ/復帰を扱うコードは **0 行**。⚠️ しかも 2026-09-04 の計測では**私が意図的に避けた**（★ バッテリー時は 1 分でスリープするので AC に挿してもらった）→ **1 度も試していない**。⚠️ O1 は数日〜数週間ノート PC で回す研究なので、**ここが抜けたまま配るのは危険** |
| **B** | ★ 未マージ 2 ブランチの処遇 | ★ 30 分 | `feat/phase1-cindex-attainability`（先 3 / 遅れ **172**）・`docs/g1-verdict-and-friction-survey`（先 7 / 遅れ **242**）。⚠️ **遅れが大きいので単純 merge は危険**。★ cherry-pick か作り直しを検討する |
| **C** | ★ 廃棄してよい 2 ブランチを消す | ★ 5 分 | `docs/handoff-post-pr132`（先 1 / 遅れ 136）・`feature/phase1-reminder-and-dashboard`（先 5 / 遅れ **713**）。⚠️ **消す前に「先」の中身が main にあるか確かめる**（★ memory: 84 関数すべて main にある、は**当時の**確認） |
| **D** | ★ 引き継ぎ §3 の古い持ち越し | — | 管理シートの死リンク / `validate_blocks.py --dataset` 17 件赤 / Drive の sha256 照合 / 所要時間が 3 通り |


### §2-1 ⚠️★★★ スリープ跨ぎの検証（★ A2 の手順）

★ **何を疑うか**（⚠️ 「動いていそう」で済ませない）:

| # | 疑い | ★ なぜ |
|---|---|---|
| 1 | ⚠️ **CGEventTap がスリープで失効する** | ★ memory `macos-tap-idle-away-probe-bug`: tap 失効 → `LAST_KEY_MS=0` → **idle/away が壊れ、ランダムプローブが誤発火**した実績がある |
| 2 | ⚠️ **復帰直後に starvation の誤検知** | ★ 判定は「システムに入力があるのにフックが呼ばれない」。⚠️ 復帰の瞬間は**入力があってフックがまだ立っていない**ので、**構造的に誤検知しやすい** |
| 3 | ⚠️ **日次ローテートの起点がずれる** | ★ 起点 `O1_LOG_OPENED_MS` は**メモリ上の Atomic**。⚠️ スリープ中も壁時計は進むので、**復帰した瞬間に 24 h を超えている**ことがありうる |
| 4 | ⚠️ **NDJSON にスリープ中の偽の行が出る / 巨大な穴が開く** | ★ 1Hz ゲートがスリープ中どう振る舞うか未確認 |
| 5 | ⚠️ **孤児回収が時計の巻き戻りで止まる** | ★ `.o1_clock_hwm` が `now_ms < hwm` で **sweep を拒否**する（`o1.rs:546`）。⚠️ スリープ復帰で時計が同期し直すと巻き戻りうる |

★ **手順**（⚠️ AC に挿したまま・`pmset` は変更しない）:

```bash
D=experiments/20260903-o1-runtime-cost
# ① サンプラを先に起こす（★ 起動前の基線を取る）
nohup bash $D/run.sh with-gse > /dev/null 2>&1 & disown     # ⚠️ 既存 results があれば先に退避
sleep 60
# ② GSE をバイナリ直叩きで起動（⚠️ `open -a` は使わない）
~/Desktop/O1_計測用_macOS/gse-next.app/Contents/MacOS/gse-next &
sleep 120                                   # ★ 定常になるまで待つ
# ③ ★ スリープ前の基線を控える
date +%s; pgrep -x gse-next
grep -c "" ~/Documents/GSE-sessions/gse-app.log
ls -l ~/Documents/GSE-sessions/gse_o1_*.ndjson
# ④ ★ スリープさせる（⚠️ 3 通り試す）
pmset sleepnow           # (a) 短い: 5 分後に復帰
#   (b) 長い: 30 分以上（★ standby へ落ちる）  (c) 蓋を閉じる
```

★ **復帰後に見るもの**（⚠️ 全部見る。1 つでも欠けたら「確かめた」と書かない）:

```bash
# ★ 1. プロセスは生きているか
pgrep -x gse-next || echo "⚠️ 落ちている"
# ★ 2. 復帰直後のログ（⚠️ starvation の誤検知 / tap の失効）
grep -E "starved_ms|delivering events again|CGEventTap|orphan sweep|rotate"   ~/Documents/GSE-sessions/gse-app.log | tail -20
#   ⚠️★★★ **`tap_enabled` を見る**（★ 2026-09-05 に入れた診断が初めて役に立つ場面）
#     Some(false) → tap が disable された（★ 層 2 の担当）
#     Some(true)  → disable されていないのに飢えている（⚠️ 再有効化では直らない）
# ★ 3. NDJSON の連続性（⚠️ 中身は読まない・型と時刻だけ）
python3 - <<'PY2'
import json, collections, glob, sys
fs = sorted(glob.glob('/Users/johnd/Documents/GSE-sessions/gse_o1_*.ndjson'))
if not fs:                                    # ⚠️ 不在: 落とさずに言う
    sys.exit("⚠️ O1 の NDJSON が 1 本も無い。★ GSE が O1 モードで動いていない。")
f = fs[-1]
ts = []; c = collections.Counter(); bad = 0
for line in open(f, encoding='utf-8', errors='replace'):
    if not line.strip():
        continue
    try:
        o = json.loads(line)
    except Exception:                          # ⚠️ 壊れ: 黙って捨てず数える
        bad += 1; continue
    c[o.get('type')] += 1
    t = o.get('t') or o.get('timestamp')
    if isinstance(t, (int, float)):
        ts.append(t)
print("★ 対象:", f.rsplit('/', 1)[-1])
print("★ 型:", dict(c))
if bad:
    print(f"⚠️★★★ JSON として読めなかった行: {bad}")
ts.sort()
if len(ts) < 2:
    sys.exit("⚠️ 時刻を持つ行が 2 行未満 → 穴は測れない（★ 0 と書かない）")
gaps = [(ts[i] - ts[i-1]) / 1000 for i in range(1, len(ts))]
print(f"★ 最大の穴: {max(gaps):.0f} 秒  （★ スリープ時間とほぼ一致するはず）")
print(f"⚠️ 30 秒超の穴: {sum(1 for g in gaps if g > 30)} 個")
PY2
# ★ 4. 打鍵が拾えるか（⚠️ 実際に何か打ってから）
#     → `key` 行が増えること。⚠️ 増えないなら tap が死んでいる
# ★ 5. サンプラの列（★ スリープ中の行がどうなったか）
tail -20 $D/results/with-gse/samples.tsv
```

⚠️ **陰性対照**: ★ 同じ長さだけ**スリープさせずに**放置した区間と比べる
（⚠️ 「復帰後に starvation が出た」だけでは、**スリープのせいか元々出るのか**が分からない
—— ★ 2026-09-04 の実測では、**スリープなしでも 120 s 級の DOWN が出ている**）。

★ **判定の書き方**: ⚠️ 「問題なし」と書かない。
★ 上の 5 項目について **「見た / 見ていない」** と **「期待どおり / 違った」** を分けて書く。

---

## §3 ⚠️★★★ 研究者判断が要ること（★ 私は実行していない）

| # | 何 | ⚠️ 効き方 |
|---|---|---|
| 1 | ~~Drive の O1 zip を差し替える~~ | ✅ **完了**（2026-09-06）。★ 研究者が **v0.1.33** を上げ、⚠️ サイズと更新時刻が手元と**秒まで一致**することを確認済み（mac 10,301,795 / win 5,960,321・14:10:20-21Z）。★ 重複なし・`anyone: reader`。⚠️ **md5 は MCP から取れない**ので「バイト同一の証明」ではない。★ G1 の 2 本は **sha256 不変**で温存 |
| 2 | ~~Drive の `TIMEOUTTEST_*` を削除~~ | ✅ **完了**（2026-09-07）。★ **7 本（≈106 MB）をゴミ箱へ**（⚠️ 完全削除ではないので戻せる）。★ 削除前に**受け口フォルダの全件を確認**し、⚠️ **本物の提出物が 0 件**であることを確かめた（＝ 巻き添えなし）。★ 削除後にフォルダが**空**であることも確認 |
| 3 | ⚠️★★★ **`Form_O1/GSE_O1_Submit.gs` を実 Apps Script へ再デプロイする** | ★ source は **32 MB に変更済み**（PR #165・ガード検査 **45 件**緑・⚠️ 陽性対照で両側を挟んだ）。⚠️★★★ **しかし実物の受け口はまだ 48 MB のまま** —— ★ 再デプロイは**研究者の手作業**である。⚠️ **配備するまで「直した」と読まない**（memory `gate-green-but-artifact-broken`）。★ 配備後は `checkSubmitConfig()` が緑であることを確かめる |
| 4 | ⚠️★★★ **G1 の計器の版をどうするか** | ★ G1 zip は **Aug 23（v0.1.29 相当）のまま**。⚠️ P017/P018 に v0.1.32 を配ると、**既収集の 3 名（P007/P014/P016）と版が違う**。★ 直っているので配る方が良いとも、揃える方が良いとも言える |
| 5 | ★ **G1 の配布関門 3 件** | ⚠️ ①P017/P018 のフォルダ共有設定が**未設定**（★ 実測で `owner` 1 件のみ ＝ **被験者は開けない**）②管理シートの配布URL列が**死リンク** ③同意文書・デブリーフの**連絡先が空欄**（`consent.md:133,134` / `debrief.md:98,99`） |

---

## §4 ★ 触らないもの

- ⚠️ 事前登録の凍結節（`docs/preregistration-v0.3.md §3`）
- ⚠️ `Form_G1/` / `Form_O1/`（★ GAS は実物と同期を取ってある）。★ 変えるなら**再デプロイまでが 1 単位**
- ⚠️ `docs/adr/`（★ 本文は書き換えない規約。★ 新しい ADR を足す）
- ⚠️ **G1 の zip**（★ 研究者が §3-4 を決めるまで作り直さない）

---

## §5 ★ 積み残し（⚠️ 本セッションの範囲外だが忘れないこと）

- [ ] ⚠️★★★ **starvation の機序は未確定** —— ★ 2026-09-05 に `tap_enabled` の診断を入れた
      （PR #158）。⚠️ **次に Down が起きたときのログで決着する**。それまで追加の対処をしない
      （★ 機序が分かる前に手を入れると、また間違ったものを直す）
- [ ] ⚠️ **層 2 / 層 3 は CI では検証されていない**（★ `decisions.md` D5。⚠️ 権限が無く skip される）。
      ★ 実機で確かめるなら `GSE_REQUIRE_HOOK_TESTS=1 cargo test --test macos_hook_rehook`
- [ ] ⚠️ **数日〜数週間のメモリリーク**（★ 8 時間 × 3 本（macOS×2, Windows×1）では
      「傾きほぼ 0」までしか言えない）
- [ ] ⚠️ **overlay の透明窓のクリック奪取**（★ Windows は2026-09-09に **idle状態は実機確認済み**
      （5/5箇所で奪っていない・`.steering/20260904-windows-orphan-verify/evidence-s3-overlay.md`）。
      ⚠️ **表示状態（Nudge/プローブ中）は両OSとも未検証のまま**）
- [ ] ⚠️ **CPU 最大 5.20 % の原因**（★ macOSの809行中1行・`gse-app.log`に対応する行が無い）
- [ ] ⚠️★★★ **Windows実測で新たに発見**（`.steering/20260904-windows-orphan-verify/blockers.md`参照）:
      (1) CPU%のOS間定義差を`sample-windows.sh`/`summarize.py`が正規化していない（HIGH）
      (2) `run.sh`の上書きガードが`samples.tsv`の有無しか見ない（MEDIUM）
      (3) 測定窓直後のフック飢餓クラスタ（30秒×6・120秒完全停止×1、原因未特定）

## §6 ★ 完了報告に必ず書くこと

- [ ] ⚠️ **外界に触った操作**を列挙（★ GSE 起動/停止・ファイル削除・push・merge・タグ・実送信）
- [ ] ⚠️ **未検証が残っているうちは「問題なし」と書かない**（★「N 件中 M 件を実測、未検証 K 件」）
- [ ] ⚠️ **書いたつもりのものが書かれたか** `git show --stat` で確かめる
- [ ] ⚠️ **緑を見たら「何が走ったか」をログで確かめる**（★ skip も 0 件マッチも緑になる）

## ⚠️★★★ 作業規約（★ CLAUDE.md より・省略しない）

1. `.steering/[YYYYMMDD]-[task-name]/` に `requirement.md` / `design.md` / `tasklist.md` を作る。
   ⚠️ 2026-09-05 に `decisions.md` だけ作って preflight に怒られた。
2. 必須 Skill を読んでから手を動かす: `verify-before-claiming` / `reproducibility-discipline` /
   `data-privacy` / `git-workflow` /（フックを触るなら）`hook-constraints`。
3. ⚠️★★ **「緑だから正しい」と書かない。** 検査は**正常 / 不在 / 壊れ**の 3 状態で試し、
   ★ **陰性対照**（壊していないものが緑のままか）も置く。
4. ⚠️ **main に直接コミットしない**（★ 2026-09-05 に 1 回やってブランチへ移し替えた）。
