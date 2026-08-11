# 設計: 表現層の試作 Step 0（+ Step 1/2 への接続）

> 上位: `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md` §7
> 既決: D6 / D18 / D21 / S0-D1〜S0-D5（`decisions.md`）
> ⚠️ **MhD（推論層）の設計議論は行わない**（研究者指示・2026-08-11）。
> `p_stuck` / `ewma_x` / `ewma_y` は**入力として使うだけ**。

---

## 0. アプローチ

**Step 0 は設計ではなく計測である。** 作るものを決める前に、
**道具がこのプロジェクトの作業プロトコル（`.steering/` 記録・`git diff`・`/review-changes`・
`/cross-review`）に載るか**を先に確かめる。載らなければ**表現層トラックの道具選定をここで畳む**——
これは失敗ではなく、**安く畳むために関門を先頭に置いた**という設計どおりの結果である。

★ **関門の質問は 2 つだけ**（`20260810-.../design.md` §1.3 の未検証点）:

1. **(a)** 展開されたツリーがテキストとして読めるか（Claude Code が編集できる形か）
2. **(b)** 往復（expand → collapse）で情報が失われないか

⚠️ **(a) は「読めるか」だけでは足りない。** D6 が求めているのは
「**Claude Code が書き・git が差分を取り・レビューできる対象**にできること」なので、
★ **「編集したものが往復するか」まで確かめないと (a) に答えたことにならない**——
本設計はここを明示的に検証項目に足した（下記 §2 の検証 4）。

## 1. 変更対象

★ **GSE 本体（Rust / TypeScript）は 1 行も変更しない**（`git diff -- src-tauri/ src/ package.json` が空）。
本タスクが触るのは以下の **12 ファイル**だけ:

| パス | 種別 | 内容 |
|---|---|---|
| `.steering/20260811-expression-prototype-step0/{requirement,design,tasklist}.md` | 新規 | 作業記録 |
| `.../verification-log.md` | 新規 | 実測ログ（コマンドと生出力） |
| `.../decisions.md` | 新規 | 判定 **S0-D1〜S0-D13** |
| `.../scripts/step0-verify.sh` | 新規 | 往復の再現スクリプト（**28 検査**） |
| `.../scripts/classify.py` | 新規 | 展開ツリーの text/binary 分類 |
| `.../scripts/gen_test.sh` | 新規 | 多世代往復（不動点の検査） |
| `.../scripts/leakcheck.py` | 新規 | 混入検査（ユーザー名 / 絶対パス） |
| `.../scripts/snapshot_to_csv.py` | 新規 | **Step 1**（標準ライブラリのみ） |
| `.../scripts/expr_smooth.py` | 新規 | **Step 2**（標準ライブラリのみ・`--selftest` **51 検査**） |
| `.gitignore` | 変更 | `.toe`/`.tox` 除外 ＋ **`logs`/`dist` の錨止め**（S0-D9）＋ 派生成果物 |
| `.steering/20260810-.../design.md` | 変更 | ★ 訂正注記のみ（`--snapshot` の誤記・S0-D6） |
| `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md` | 変更 | ★ 訂正注記のみ（同上） |
| `.steering/_handoff/next-session-prompt-expression-prototype.md` | 変更 | ★ 訂正注記のみ（同上） |

⚠️ **`experiments/` は起こさない**（S0-D5 / D18）。**`.toe` / `.tox` はコミットしない**（D6 / S0-D3）。

## 2. 検証項目（実施したもの）

| # | 検証 | 手段 | 出典の要求 |
|---|---|---|---|
| 1 | 実体の存在 | `ls` で 3 バイナリ/テンプレートを確認 | `verify-before-claiming` ルール 1（引き継ぎを根拠にしない） |
| 2 | **(a)** ツリーの可読性 | 空 `.toe` の全ファイル `cat` ＋ 実プロジェクト 8,281 ファイルの text/binary 分類 | 引き継ぎ §3 検証 1 |
| 3 | **(b)** 往復の保存性 | sha256 比較 →（不一致なら）**展開ツリー同士の `diff -r`** | 引き継ぎ §3 手順 4 |
| 4 | ★ **編集の往復耐性** | `.n` の値書き換え / `.text` の Python 本文を**長くする**書き換え | ★ **本設計で追加**（§0 の理由） |
| 5 | ★ **多世代安定性** | 3 世代連続往復でサイズ・ハッシュ・ツリーを追跡 | ★ **本設計で追加**（git 差分の衛生） |
| 6 | `.tox` でも同じか | `stoner.tox`（2.2 MB）で 2〜3 を再実行 | 引き継ぎ §3 手順 5 |
| 7 | 終了コードの意味 | **正常 / 不在 / 破損 / 引数なし**の 4 状態で実測 | `verify-before-claiming` ルール 5b |
| 8 | git 衛生 | ユーザー名・絶対パス・タイムスタンプの混入検査 | `data-privacy` |

★ **判定に終了コードを使わない**（S0-D2）。**expand は出力の `expanded into directory` で判定する。**

## 3. テスト戦略

★ **GSE 本体に触らないので `cargo test --workspace` / snapshot 回帰への影響はゼロ**
（影響が出る変更をしたら、それはスコープ逸脱である —— `20260810-.../design.md` §5 の逐語）。

代わりに **Step 0 の主張自体を検査するもの**を同じ版に置く（`verify-before-claiming` ルール 6）:

```bash
bash .steering/20260811-expression-prototype-step0/scripts/step0-verify.sh
```

★ **検査自体を 3 状態で試した**（ルール 5b）:

| 状態 | 作り方 | 結果 |
|---|---|---|
| **正常** | そのまま実行 | `step0-verify.sh` **28 PASS / exit 0** ／ `--selftest` **51 PASS / exit 0** |
| **不在** | `TD_ROOT=/c/nonexistent-touchdesigner` | **exit 1**（3 件 FAIL して中断） |
| **壊れている** | 実バイナリ ＋ 中身が `not a toe` のテンプレート | **PASS=4 / FAIL=9 / exit 1** |
| **壊れている（Python）** | **dt を無視する固定 alpha** を注入 | **FAIL=11 / exit 1** |

★ **空回り検出**も入れた —— 検査が 1 件も走らなかったら赤にする。

⚠️★★ **レビューで silent pass が 2 件見つかり、直した**（両方とも「成功に見える失敗」）:

1. **`collapse_ok()` が欠損を PASS にしていた** —— `toecollapse` はツリーが欠けても
   **exit 0 ＋ `moved to`** を返し（`Warning` 1 行だけ）、**壊れた `.toe` を書く**。
   → `Warning` / `Unable to find` を FAIL にし、**実際に壊して検出できることを検査に足した**（§5b）。
2. **§3 の往復検査が collapse 成否でガードされていなかった** —— collapse が失敗すると `.toe` は
   原本のまま残るので、再展開したツリーが一致して**往復していないのに PASS** していた。
   → 入れ子にし、**バックアップ生成を「往復が起きた証拠」として要求**した。

★ **どちらも `verification-log.md` §3.3 で自分が 1 度踏んだ形の再発**である。

---

## 4. ★ Step 0 の結果が Step 1 以降に課す制約

| 実測した事実 | 以降への制約 |
|---|---|
| ★★ `toeexpand` の終了コードが**反転**（成功=1 / 失敗=0） | **全スクリプトで expand の exit code を見ない。** 出力文字列 ＋ `.dir`/`.toc` の実在で判定する |
| `toecollapse` は `.dir` と **`.toc` の両方**を要求する | ★ **`.toc` も追跡下に置く。** 落とすと collapse 不能なツリーになる |
| 往復は **gen1 以降 byte-equal の不動点** | `.toe` はコミット不要（ツリーから決定的に再構成できる）。`.gitignore` に `.toe`/`.tox` を足す |
| `.tox` には **7.4 MB の `.data` blob** が入りうる | ★ **既製 Palette を丸ごと取り込まない。** データは**外部 CSV を Table DAT で読む**形にする |
| `.text`（Python DAT）は**ヘッダ + 本文**で本文は編集自由 | ★ **ロジックは Python DAT に置く**のが git 上で最も差分が読める。ノードのパラメータ弄りに寄せない |
| 展開ツリーに絶対パス・ユーザー名の混入なし | `data-privacy` の観点で追跡下に置いてよい |

★★ **最後の 2 行が Step 1 以降の作り方を決める** ——
**「TD のノードグラフで凝る」より「Python DAT ＋ 外部 CSV」に寄せるほうが、
git 差分・レビュー・再現性のすべてで有利**である。これは実測から出た制約であって、好みではない。

---

## 5. ⚠️ Step 1 以降で守ること（既決の再掲・ここで閉じない）

- **GSE 本体（Rust）を変更しない。OSC / WebSocket を実装しない**（D5 / `data-privacy` の境界を増やさない）
- **凍結対象に触れない**: `docs/preregistration-v0.3.md` / `engine.rs` / `probe_scheduler.rs` /
  `schema_dto.rs` / `App.tsx`
- ★ **表現層の平滑化（時定数 ≥60 秒）を Step 3 より先に実装する**（`media-expression-spec.md` §1.3）——
  1Hz のステップがそのまま振幅のオンセットになり、**オンセットは分節を作る**［P64］＝ISE の条件
  （既存のヒステリシスは **≈2.5 秒**＝`engine.rs:113` で不足）
- ★ **状態の波は 0.001–0.02 Hz**。**4 Hz 付近は最悪**（fluctuation strength のピーク）・15–70 Hz も避ける。
  書き方は「緩慢だから安全」ではなく **「禁止帯から離れているから安全」**
- **`experiments/` は Step 3 から**（SEED 固定が効く＝グラニュラー合成は乱数を使う・D18）
- **ユーザーが止められること／音量を変えられること**は交渉不可の必須要件（D3d / [P71]）
