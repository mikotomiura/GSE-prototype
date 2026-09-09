# decisions

## D1 ⚠️★★★ macOS の CPU 測定器が壊れていた（★ 本セッション最大の発見）

★ `sample-macos.sh` が使っていた `top -l 2 -pid P -stats cpu -n 1 | tail -1` は、
⚠️ **1 コアを飽和させたプロセスを 47.6 % と報告する**。

| ★ 計器 | ★ 読み値（1 コア飽和のプロセス） |
|---|---|
| ★ 地上真実（`ps -o cputime` の増分 / 実時間） | **99.7 %** |
| ★ `ps -o %cpu`（起動以降の平均） | **99.7 / 100.0 %** |
| ⚠️ **`top -l 2`（旧サンプラ）** | **47.6 ± 0.4 %**（n=6） |
| ★ `top -l 3` | **99.0 ± 1.1 %**（n=6） |

★ **機序も特定した**: 2 フレーム目の分母に **top 自身の起動時間 ≈ 1.1 s** が混ざる。
→ `-s` を 1 / 2 / 5 / 10 s と伸ばすと **47.8 → 62.5 → 79.1 → 88.3 %** と 100 % に漸近する
（★ 予測式 `delay/(delay+1.1)` と一致）。⚠️ 偶然のノイズではない。

### ⚠️ 効き方

★ **8 h × 2 本の macOS 実測（CPU 平均 0.95 % / 0.98 %・最大 5.20 % / 4.30 %）はこの影響下にある。**
⚠️ ★ 平均は約 2.08 倍の過小報告なので、**真値はおおむね 2.0 %** と推定される。
→ ⚠️ **閾値 < 1 % に対して PASS ではなく MARGINAL** になる。

⚠️★★ **ただし「×2.08 して確定」とは書かない。**
★ 分母だけが誤っている（＝定常なら定数倍）が、⚠️ **サンプル窓が実時間の約半分しか覆っていない**ので、
**最大値は取りこぼしのぶんだけ別に歪む**（★ 平均の補正と最大の補正は同じ係数ではない）。
→ ★ **正しい数字が要るなら再測する**（⚠️ 本セッションでは 8 h の再測はしていない）。

### ★ 直したもの

- `scripts/calibrate-cpu.sh`（新規）—— ★ 陽性対照（1 コア飽和）と陰性対照（不在）つき
- `sample-macos.sh` —— ★ CPU を `ps -o cputime` の増分 / 実時間へ。
  ⚠️ 累積カウンタなので **サンプル間隔より短い山も落とさない**。`top` は mem/th/power 専用（`-l 3`）
- `summarize.py` —— ★ 空欄の CPU を 0 と読まない / **CPU% の基準を印字**
- `run.sh` —— ★ 上書きガードを `meta.json` 等へ拡張（blockers #2）/ `GSE_COST_LABEL` /
  `meta.json` に `cpu_source` `cpu_pct_basis` `logical_processors`（blockers #1）

⚠️ **旧サンプラの `power`（エネルギー影響）も同じ分母の誤りを受けている**
（★ 陽性対照で `-l 3` は 98.6〜101.5 と出た）。→ ★ 既存 2 本のエネルギー影響も過小。

---

## D2 ★ Windows の「×16 → FAIL 相当」は **一次資料と矛盾する**（⚠️ 実機実測は未了）

★ G-GEAR の主張の根拠は `sample-windows.sh` の **コメント逐語**であり、
⚠️ **一次資料でも実測でもない**（★ 自分で書いたコメントを引用している）。

★ Microsoft *Examining Processor Time Data* の**逐語**:

> On multiprocessor systems, the Processor\\% Processor Time value reported by System Monitor
> will never exceed 100 percent for any particular processor or thread. On the other hand,
> **the value of the % Processor Time reported for the Process object can report values over
> 100 percent**; if such values occur, this could indicate that threads of the process are
> cumulatively using more than 100 percent of a processor.

→ ★ **Process オブジェクトの `% Processor Time` は「1 コア = 100 %」基準**（＝ macOS `top` と同じ規約）。
⚠️ **`×16` は 16 倍の過大評価**であり、「FAIL 相当」は**偽の警報**である可能性が高い。

### ⚠️ ただし確定はしていない

⚠️ **この repo は Windows 実機でこれを確かめていない**（★ この Mac に `powershell.exe` が無い）。
→ ★ 決着実験の手順を `windows-cpu-convention-probe.md` に用意して研究者へ渡した。
★ 結果が出るまで `meta.json` の値は `one_core_100_unverified` にしてある。

### ★ 三角測量（⚠️ 証明ではない）

★ D1 で macOS の真値が **約 2.0 %** に補正されると、⚠️ Windows の **2.06 %** と**ほぼ一致する**。
→ ★ 同じソフトが両 OS で同じくらいのコストなのは自然であり、**「×16 は誤り」を支持する**。
⚠️ ただしこれは状況証拠であって、★ 決着は実機実測に委ねる。

### ⚠️ どちらに転んでも変わらないこと

★ Windows の 2.06 % は、**そのままでも閾値 < 1 % を超えている**（＝ `MARGINAL`）。
→ ⚠️ **「Windows は PASS」とは書けない。** ★ 覆るのは「FAIL 相当か MARGINAL か」だけ。

---

## D3 ★ ブランチ棚卸し（⚠️ 削除は研究者の判断・私は消していない）

| ブランチ | 先 / 遅れ | ★ 実測した中身 | ★ 判断 |
|---|---|---|---|
| `docs/handoff-post-pr132` | 1 / 155 | ★ `next-session-prompt-o1-v0-1-31-and-timeout.md` への +31 行のみ。⚠️ 当該メモは main に**存在し**、★ その後 20 本以上の後継メモが出ている | ★ **削除可**（⚠️ 失うのは古い引き継ぎメモの一版だけ） |
| `feature/phase1-reminder-and-dashboard` | 5 / 732 | ★ コードは **main が上位互換**（関数 84 → 86・branch 固有関数 **0**）。⚠️ branch 固有行は **7 行**＝ `REMINDER_WEBAPP_URL` の**べた書き exec URL** で、★ main は**意図的に Script Properties へ移した**（履歴に URL を残さないため） | ⚠️ **そのままでは削除しない** —— ★ `.steering/20260708-*` **3 ディレクトリ**と `_handoff/next-session-prompt-phase1-prep.md` が **main に無い**（作業記録の運用ルール違反になる）。→ ★ **記録だけ救出してから削除** |
| `feat/phase1-cindex-attainability` | 3 / 191 | ★ `analysis` の C-index 到達可能性診断（実装 2 + steering 1） | ⚠️ **遅れ 191**。★ 単純 merge しない。→ ★ 別タスクで作り直すか cherry-pick |
| `docs/g1-verdict-and-friction-survey` | 7 / 261 | ★ 文献カード 4 本 + G1 確証コホート N=3 の判定 + 計器変更の宣言機能 | ⚠️ **遅れ 261**。★ 文献カードは `citation-ssot` の append-only 規約があるので、**採番の衝突を先に見る**必要がある |

⚠️★★★ **`git cherry` は patch-id で見るので「名前が同じで中身が違う」を検出しない。**
→ ★ 上表は **関数名の集合 + 差分行の実物**まで降りて確かめた（⚠️ memory の
`name-lookup-only-works-within-one-source` の教訓）。
