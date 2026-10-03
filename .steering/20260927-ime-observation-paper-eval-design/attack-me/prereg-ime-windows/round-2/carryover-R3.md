# carryover-R3 — あなたの round 1 の指摘と、その扱い（attack-me・Windows の追補・round 2）

各指摘について: 裏取り（メインが一次で確かめた結果）／研究者の採否／今の版での対応と位置。⚠️ 再掲は求めない。解消したかを 1 件ずつ判定してください。

| # | round 1 の指摘（severity） | 裏取り | 採否 | 対応（今の版の位置） |
|---|---|---|---|---|
| R3-1 | Windows の観測器のセッションの規則が無く、説明が実装と違う。D3 の根拠がそれに依る（major） | 真 | 採る | §10.3「The observer on Windows」を新設（2 経路・切り替えの条件・150 ms・打ち切りは cloak の経路だけで窓の表示から 20 秒・WinEvent の経路は 25 秒の安全弁だけ・どちらが動くかは凍結の前に分からず、20 秒以上の行があれば WinEvent の経路と分かる）。D3 は観測器の規則に依らない形に改めた（R3-5） |
| R3-2 | 逸脱が macOS を変えない根拠が再現できる形で無い（minor） | 真 | 採る | `deviations.md` の最後の節「The macOS cells are unchanged」: 両方のチェックアウト（LF）での命令、タグからの計画が §2.4 の SHA と一致すること、変更後の計画の SHA-256 と、手順書の SHA を伏せてバイト一致、合成の macOS の run の結果 4 ファイルの SHA-256 とバイト一致（bootstrap 2000）、selftest が検査しないこと |
| R3-3 | §9 の SHA の表が Windows のタグで古くなる（minor） | 真 | 採る | §10.6 に Windows のタグのファイルの SHA の表（設定・2 つの手順書・コーパス・`keymap_windows.json`）と「§9 の表は macOS のタグのもの」 |
| R3-4 | Windows の解析に並べる run と手での照合（minor） | 真 | 採る（研究者の選択: 別の一覧と結果の置き場） | `experiment\data.windows.md`（新規）に Windows の run を並べ、§10.7 に命令（`--runs-from experiment/data.windows.md … --out experiment/results/windows`）。macOS のセルは Windows のタグから解析せず、そうして出た macOS の結果は報告しない。手での照合は §10.6 の SHA と（`data.windows.md`） |
| R3-5 | D3 は比べる片側の値で範囲を選ぶ（minor） | 真 | 採る（研究者の選択: 主を oracle の送出の幅に） | D3: 試行で送った押下の最初から最後が 20 秒以上なら長い（oracle と計画だけ）。正解の長さの版は感度。境界の帯（参照のセッションが 19〜21 秒）と分類の違う試行を層ごとに数える。パイロットの 2 run は同じ計画（seed 8）と明記 |
| R3-6 | Windows の n と精度を層ごとに（minor） | 真 | 採る（一部） | §10.7 に層ごとの表（範囲に残る試行・S13 は 0・50 未満が 8 層・最小は S6 slow の 30・速さごとの数）。⚠️ Windows の計画の Σm²/Σm は計算していない（`spec_predict.py --from-plan` は macOS の計画用） |
| R3-7 | 問 5 の Windows の量と `cpu_all_zero`（minor） | 真 | 採る | §10.9: CPU は読む時点の約 1 秒の標本・メモリは working set・系の間で比べない・`cpu_all_zero` の条件は不十分として §3.4 で測り直す |
| R3-8 | 所要時間（minor） | 真 | 採る | §10.6: 比は 1.06（117 試行・直す前）〜1.17（39 試行・直した後・ブロックの間の時間の比重が大きい）→ 12〜13 時間 |
| R3-9 | 参照の経路を機械で検査していない（minor） | 真 | 採る | D2 に含めた: Windows の run は gt のヘッダの `src` が `win_tsf` でなければ中止（`pipeline.py` `WINDOWS_GT_SRC`・`_gt_src`）。§10.8 |
| R3-10 | nit（§10.1 の一覧・過去形・`python3`/`python`・LF の確保と照合した OS・封をした行・IMM を含む run の数） | 真 | 採る | §10.1 の一覧を網羅・凍結の時に真になる形・命令は `python`・§10.6 に LF と Windows 11 で 2 つの Python・§10.10 に「not even in an exploratory analysis」・§10.7 は TSF の 2 run |

⚠️ 新しく足した部分（§10.3・D3 の新しい規則・D4・§10.7 の感度と診断と問 4・解析の入口・`scope_windows.py`・`pipeline.py` の変更）に新しい分岐や穴が無いかも見てください。
