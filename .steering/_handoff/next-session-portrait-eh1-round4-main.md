# 引き継ぎ — 肖像の EH1 第 4 回の本番を回し、結果を照合して解釈する

> 作成: 2026-10-10（第 4 回の設計・固定・計器・下見・スモークをしたセッション・G-GEAR）。
> このメモを一次資料にしない。基準は `.steering/20261010-portrait-eh1-round4/design.md` §3（`1fa6c833` で固定）、研究者の決定と Claude の細部は同 `decisions.md` 判断 1〜4、下見とスモークの値は design §8。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh1-round4-main.md を読んで、肖像の EH1 第 4 回の本番を G-GEAR で回してください。
ブランチは docs/portrait-eh1-round4（worktree C:\wt\portrait-eh1-round4）です。
```

## §1 いまの状態（2026-10-10 14:10 ごろ）

- design §3 は固定済み（`1fa6c833`）。計器は `b505ab44`、下見で選んだ λ（4 つの形とも 0.35）は `62b951fe` で `config.json` に固定した。その後に §8・notes・tasklist にスモークの記録を足した（コミットは本メモと同じ）。
- 下見（P 40）: L300 の形の PC は λ = 0.35 で点推定 +0.047〜+0.057、土台 `PCsize0` の上限は +0.006〜+0.015。L60 の `lattice-none` は土台の下限が 0 を上回った（+0.005）。L1800 は土台の上限が 0.03 を超え、PC1 も届かない。
- スモーク（P 12）: 全段が通った。selftest は 0 failed・0 soft-failed。第 3 回と同じ名前の値は第 3 回のスモークと一致した。
- 本番はまだ回していない。結果は 1 つも見ていない。

## §2 やること

1. 走らせる前に確かめる: G-GEAR で計測の run が走っていないか、self-hosted CI（`g-gear-win-x64`）が busy でないか（`gh api repos/mikotomiura/GSE-prototype/actions/runners`）。走っているかを推測しない。
2. 本番を回す（約 3 時間。`checks.py` は約 2.8 時間の見込み = 第 3 回 5604 s × スモークの比 1.8）。
   ```bash
   cd C:/wt/portrait-eh1-round4/experiments/20261010-portrait-eh1-round4
   GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe \
   PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python \
   bash run.sh --jobs 6 > C:/wt/_eh1r4-main.log 2>&1
   ```
   - Bash の `run_in_background` で回す（絶対パスで。`cd` が効かないことがある）。開始と終了の時刻を `C:/wt/_eh1r4-main.start` に残す。
   - メモリ: 組が 17 本から 27 本に増えた。第 3 回は `--jobs 6` で使えるメモリの最低が約 4.1 GB だった。1 分ごとの空きメモリを `C:/wt/_eh1r4-main.mem` に記録する（PowerShell: `while ($true) { "{0} {1}" -f (Get-Date -Format HH:mm:ss), [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024) | Add-Content C:/wt/_eh1r4-main.mem; Start-Sleep 60 }`）。2 GB を切りそうなら止めて `--jobs 4` で回し直す（結果は `--jobs` に依らない・design §3.8）。止めたことは §8 に書く。
   - selftest が FAIL（止める検査）で止まったら、design §3.7 の「落ちた場合の扱い」に従う: 直してよいのは文言どおりでない実装だけ。SOFT-FAIL は止めずに §8 に値を書く。
3. 本番の後:
   - `results/v2/`（`e13.json`・`summary.json`・`material_info.json`・`provenance.json`・`capabilities.json`・`compare_round3.json`）をコミットする。`work-*/` はコミットしない。
   - 判定を、`e13.json` の区間と並べ替えの値から design §3.2〜§3.4 の式だけで計算し直し、`summary.json` と照合する（第 3 回は 51 件一致。第 4 回は 27 本 × 3 ラベル）。照合のスクリプトは scratchpad に Write で書く（heredoc を使わない）。
   - `compare_round3.json` で、第 3 回と同じ名前の値の差（期待は 0）と、判定が変わった組を見る。変わった組は design §3.6 の (a)〜(c) に分けて書く。
   - selftest の SOFT-FAIL と、λ = 0 の形の PC の値（本番の work の P 先頭 60 本）を §8 に書く。
   - 下見と本番の形の PC・土台を §8 に並べる（design §3.3 の宣言）。`shape_baseline` で判定不能になった形があれば、下見の土台の値を並べる。
4. notes の「結果」を書き、decisions に判断 5（結果と読み方）を書く。読み方の限定は design §3.4・§3.5 のとおり（形の PC が示すのは大きさの水準に乗る漏れまで・神託は指定した 4 本と固定した攻撃者での値まで・8 組の値は第 3 回で見ている）。
5. まとめの `/cross-review` を 2 巡回す（範囲は本番の後のコミット。Codex に `e13.json`・NDJSON・`work-*/` を渡さない）。予算ガードは `C:\GSE-prototype\.codex\budget.json` を読む。10-10 は 388,659 / 450,000 で埋まりかけている。日付が変われば足りる。
6. 研究者に親の判断 8 の扱いを聞く（AskUserQuestion・推奨と理由を添える）。第 3 回の判断 8 の 1 で「第 4 回の結果を見てから決める」とした問いである。人の了承は検証の不足を補わない。
7. 出荷（push → PR → CI → merge）。`.steering` と `experiments/` だけの変更。

## §3 守ること

- 応答は日本語。AskUserQuestion には推奨と理由を添える。★・⚠️ を多用しない。
- `git add` はファイルを名指しする。main checkout（`C:\GSE-prototype`）の git には触らない（並行セッションの未コミットの変更がある）。
- 生成した NDJSON・`work-*/`・PNG を Codex や外部の LLM に送らない。
- EH0 の主張の格: 「検査した範囲で見つからなかった」まで。合成した停滞は打鍵の統計の型で、認知の状態ではない。
- 第 2 回・第 3 回の判定は書き換えない。design §3 の基準・§1.4 の定義・判断 2〜4 の細部は、どの結果を見ても変えない。逸脱は §8 に書く。
- 結果を見る前に、第 3 回の値が再現すれば L300 の 8 組は赤にならないことが分かっている（design §3.3）。緑か判定不能かは形の PC で決まる。その事情を報告に書く。

## §4 片付け（任意・研究者の判断）

- `experiments/20261010-portrait-eh1-round4/work-*/`・`results/pilot-v2/`・`results/v2-smoke/`（コミットしない）と `C:/wt/_eh1r4-*.log`・`.start`・`.mem`。
