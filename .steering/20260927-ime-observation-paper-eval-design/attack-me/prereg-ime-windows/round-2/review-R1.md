# round 2 — R1（推奨 minor）

接地: Plant 2016（289–296 "researchers self-validate their own timing accuracy using external chronometry … The only way to be sure of timing accuracy is to check it when paradigms are running in-situ, on the experimenter's own equipment"／156–160 "Worryingly the log files suggested that the test had run normally"／210–219 "a growing trend toward 'checking' timing accuracy by proxy"／165–169 "simplified scripts is counterproductive"）・Pinet 2017（107–115 "The impact of this intermediate layer of software on keyboard chronometry is not known."）・Bridges 2020（"the only way to know about the timing quality of your audio stimuli is to test with hardware devices."）。

引き継ぎ: R1-1 部分的に解消（§10.3 がコードと 4 点で食い違う）・R1-2〜R1-7 解消・R1-8 部分的に解消（1.17 が再計算できない・Windows 固有の区間のずれ）・R1-9〜R1-12 解消（節番号のずれは別）。

評価: a3 b3 c4 d3 e4 f3 g4。

新しい指摘:
- [major] §10.3 と §10.7 の観測器の記述がコードと 4 点で食い違う: (i) WinEvent の経路で 25 秒の弁が `emit_ime_shadow(..., true)` を呼び、dwell ≈ 25 秒の行を書いて start を 0 に（main.rs 271–283・189–195）→ §10.7「on the other there is none」は誤り。(ii) `legacy_path_is_driving` は WinEvent が一度も来ていなければ偽（cloak.rs 160–162）→ run の始めから cloak の経路が動く。(iii) セッション中の SHOW は行を書かずに start・nav・abandon をやり直す（ime_winevent.rs 75–79）→ S4 の予測窓の開き直しが当たる。(iv) 前の要約が回収される前（≤100 ms）に次のセッションが始まると失われる（cloak.rs 247–249）。→ §10.3 に (i)〜(iv)、§10.7 を直し、20〜25 秒と 25 秒以上を分けて数える診断を登録。自信 高
- [major] cloak の経路では観測区間の終わりが 150 ms 以上遅れ、IoU の照合を系統的にずらす（dwell は空になった時刻で終わるが行の t は ≥150 ms 後〔ime_cloak.rs 309〕・match.py は `[t − dwell_ms, t]`・`obs_end_offset_ms` 0）。§6.9 の計算は macOS のもの。→ §10.11 にずれと帰結、対の「終わりの差」の分布を経路の推定と合わせて記述の診断に（設定は変えない）。自信 中
- [minor] 参照の時刻が外部の基準で検証されていない（G1・G5）→ §10.11 に。自信 中
- [minor] D3 の「10 of 10」は 1 つの計画の 10 試行。S15 は送出の幅が合成の長さを含まない → 書き直し、`n_differ` を層ごと（特に S15）に読む方針。自信 中
- [minor] 比 1.17 が報告の数（15.2/13.3 = 1.14）から再計算できない。自信 高
- [minor] IME の版がパイロットと違ったときの規則が無い → 版が違えば 39 試行の点検を先に回し 39/39 でなければ測らない、など。自信 中
- [minor] 測定が登録の後である証拠が時刻同期を切った機械の manifest の日付に頼る → run の直後に manifest の SHA を外部の時刻つきの場所へ。自信 中
- [nit] 節番号の参照のずれ（data.windows.md 23・26・pipeline.py 262・scope_windows.py 22・105）。

総合: minor。N2 の対処で照合の設定を変えるなら §8 の外の逸脱で major。

読めなかった範囲: §1〜§7 の大半、多くのコードと文書（応答に列挙）。一覧の外は開いていない。注入の疑い: なし。
