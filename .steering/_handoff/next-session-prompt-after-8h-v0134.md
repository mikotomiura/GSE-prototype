# 次セッション開始プロンプト — **8h 完了後の集計 → PR → merge**

> ★ 「===」以下をコピペして開始する。⚠️ 前セッションから `/clear` すること。
> ★ 実行マシン: **mac**。★ モデル: **Sonnet** で足りる。

---

===

## §0 ⚠️ このメモを一次資料にしない

★ 2026-09-10 のセッションで**自分の測定器・検査を 6 回壊した**（★ 通算 13〜18 回目）。
→ ⚠️ **このメモも同じ確率で間違っている。** ★ 数字は必ず自分で引き直すこと。

## §1 ★ まず状態を測る

```bash
cd /Users/johnd/GSE-prototype
git branch --show-current            # ★ feat/measurement-binary-gate のはず
git log --oneline origin/main..HEAD | wc -l   # ★ 21 コミット前後
D=experiments/20260903-o1-runtime-cost/results/with-gse-20260910-1528-macos-8h-v0134
cat $D/summary.txt                   # ★ 8h の集計（★ watcher が自動生成しているはず）
cat ~/Documents/GSE-sessions/crash-watch.tsv   # ⚠️★★★ **crash 行があるか**
bash scripts/check-measurement-binary.sh       # ★ rc=0 か
python3 scripts/check_collection_continuity.py ~/Documents/GSE-sessions/
```

## §2 ★ やること（★ この順）

### 2-1. ⚠️★★★ **集計の前に計器を校正する**

```bash
bash experiments/20260903-o1-runtime-cost/scripts/calibrate-cpu.sh
```

⚠️ **レート系（% / 秒 / 日）を出したら、校正したことを報告に書く**（★ 作業規約）。

### 2-2. ★ 8h の分析（⚠️ 何が言えて何が言えないかを分ける）

★ 見るもの:
- ★ `cpu_mean_pct` / `cpu_max_pct` —— ⚠️ **Windows (2.06 %) と同じ基準 `one_core_100` か**を
  `meta.json` の `cpu_pct_basis` で確かめる（★ 違う基準の数字を並べない）
- ★ `rss_slope_mb_per_h` / `rss_final_mb`
- ★ `ndjson_mb_per_day` —— ★ 既存 3 本は 20.1〜20.5 MB/日に収束している
- ⚠️ **CI 窓などの外れ値**が入っていないか（★ notes.md 逐語「CPU 最大 4.30 % は CI 窓の中だけ」）

### 2-3. ⚠️★★★ **クラッシュ台帳を読む（★ これが今回いちばん重要）**

★ `crash-watch.tsv` に `crash` 行が **0 件**なら、
→ ★ **v0.1.34 が 8 時間クラッシュしなかった**と言える。
⚠️ v0.1.33 は **37 分と 10 分**で落ちていた（★ `.ips` 2 件が一次資料）。
→ ★ これが **SIGSEGV 修正が効いた唯一の実証**になる。

⚠️ `crash` 行が**あった**なら: ★ `.ips` を読んで **同じスタックか**を見る。
★ 同じなら修正は不十分（⚠️ 別経路が残っている）。★ 違うなら別のバグ。

⚠️★★ **「crash 行が 0 件」だけで満足しない。** ★ 台帳の `start` 行と `end` 行を見て、
**監視が 8 時間ちゃんと走っていた**ことを確かめる（⚠️ 途中で死んでいたら 0 件は無意味）。

### 2-4. ★ notes.md / decisions.md に結果を書く

★ `experiments/20260903-o1-runtime-cost/notes.md` に §を足す。
⚠️ **推定と実測を混ぜない。**

### 2-5. ★ push → PR → CI → merge（⚠️ 研究者が 2026-09-10 に承認済み）

```bash
git fetch origin && git rebase origin/main    # ⚠️ 競合したら止めて相談
git push -u origin feat/measurement-binary-gate
gh pr create --base main --title "..." --body "..."
gh pr checks --watch
```

⚠️★★★ **CI が緑でも「何を検証したか」は別**（★ memory `github-pr-ci-mechanics`）。
★ merge の前に **実際に走ったジョブ名を列挙**して報告すること。
★ 特に今回の追加ぶんが走ったかを見る:
  - `Collection continuity self-test`（★ 今回 ci.yml に足した）
  - `Tests-are-wired gate`
  - `check (macOS)` / `check (windows)`（⚠️ **hook_macos.rs を触ったので macOS が本命**）

★ 緑なら merge。⚠️ **merge 後に main で CI が発火したかまで見る**
（★ `/finish-task` Step 5 の「2026-08-27 の取りこぼし事象」）。

## §3 ⚠️ 今回のブランチで何をしたか（★ PR 本文の材料）

| コミット群 | 内容 |
|---|---|
| `ab20fdb` `27861f2` | ★ 計測用バイナリのゲート / CI 未配線テスト 7 本の配線（★ 前セッション） |
| `3e14269` | ⚠️★★★ **macOS CGEventTap の use-after-free 修正**（★ SIGSEGV の本丸） |
| `e54cb1f` | ★ v0.1.34 / 受領 NDJSON の連続性検査 |
| `71bd8de` | ★ `--self-test` 内蔵 script が番人をすり抜ける穴を塞ぐ |
| `5889db0` | ★ クラッシュ台帳の見張り |
| `7a3e9c5` | ★ 完了待ちが別 run を誤読するのを直す |
| steering 各種 | ★ SIGSEGV の機序 / 配布経路の穴 / スリープ検証の成立 |

## §4 ★ 未着手（⚠️ PR には含めない）

- ⚠️ **被験者配布**: `~/Desktop/O1_配布_v0.1.34/` に zip がある。
  ★ 研究者が d&d する。⚠️ **CI 製ではない**（★ ローカルビルド + CI と同じ ad-hoc 署名）。
  → ★ CI 製に揃えるなら **v0.1.34 をタグして push**。
- ⚠️ **`SleepDisabled` を 1 に戻すか**は研究者判断（★ 元は 1・2026-09-10 15:07 に 0 にした）。
- ⚠️ **G-GEAR 取り込み（案 C）**: `origin/feat/resumption-outcome-arbitration`
  **214 ファイル / +26,664 行**。★ 系統ごとに分けること。
  ★ 下調べ済み: `engine.rs` / `schema_dto.rs` に差分ゼロ →
  ⚠️ `HMM_VERSION` bump 不要・ゴールデン不割れの**見立て**（★ 実測していない）。
- ⚠️ **SIGSEGV を意図的に再現していない**（★ tap 失効を繰り返す陽性対照が要る）。

## §5 ⚠️ 触らないもの

- ★ 事前登録の凍結節 / `Form_G1/` / `Form_O1/` / `docs/adr/` の既存本文
- ⚠️ **走っている bash script を編集しない**（★ bash は逐次読みするので壊れうる。今日踏んだ）
