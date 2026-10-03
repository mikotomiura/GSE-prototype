# carryover-R1 — あなたの round 1 の指摘と、その扱い（attack-me・Windows の追補・round 2）

各指摘について: 裏取り（メインが一次で確かめた結果）／研究者の採否／今の版での対応と位置。⚠️ 再掲は求めない。解消したかを 1 件ずつ判定してください。

| # | round 1 の指摘（severity） | 裏取り | 採否 | 対応（今の版の位置） |
|---|---|---|---|---|
| R1-1 | Windows の観測器の「指定」が無く、§6.4 の macOS の指定が一括で継承される（major） | 真（`ime_winevent.rs`・`cloak.rs`・`ime_cloak.rs`） | 採る | §10.3「The observer on Windows」を新設（2 経路・切り替えの条件〔WinEvent が 60 秒来ないとき cloak〕・150 ms・20 秒の打ち切りは cloak だけで窓の表示から・25 秒の安全弁・`nav`/`abandon`・行の時刻・記録するキー・構成概念の違い）。§10.2 で §1.1 を置き換えると明記。§10.7 Scopes の末尾で、§6.4 の over_limit の指定は macOS のもので Windows では記述として報告すると書いた。§10.6・D3・コードの「composition events」を直した |
| R1-2 | D3 の長い試行が観測器の打ち切りと同じ規則でなく、範囲を基準の測定値で条件づける（major） | 真 | 採る（研究者の選択: 主の定義を oracle の送出の幅に） | D3 を書き直した: 試行で送った押下の最初から最後が 20,000 ms 以上なら長い（§6.4 と同じく oracle と計画だけで決まる）。正解の長さの版を感度（`under_limit_gt_duration`）として計算し、2 つの定義で分類の違う試行と、参照のセッションが 19〜21 秒の試行を層ごとに数える（`long_trials_from`）。§10.7・`deviations.md` D3・`kit\analysis\scope_windows.py` |
| R1-3 | `pilot-windows.md` の数が整合しない（minor） | 部分的に真: 1,174 は `short-tsf`（39 試行・直す前の手順）の送った押下で正しい。「key-downs」の意味が曖昧だった | 採る（言い方） | 「試行の中で送った押下のうち参照に key-down として届いた数（`reference.reach`）・印は別に数える」と書き、到達は「各 run」と書いた |
| R1-4 | 主にする定義（`windows_def` か `all` か）が決まっていない（minor） | 真 | 採る | §10.7 Definitions: §5 のとおり `windows_def` が解析の定義。予測の窓のせいでほぼ全セッションが入ることと、「候補窓あり」が Windows では変換を意味しないことを書いた |
| R1-5 | TSF の参照の合成の境界の推定が報告されない（minor） | 真（`tsf.rs`） | 採る | §10.4 に推定することを書き、§10.7 Diagnostics に result_len の無い `tsf_end` の数（シナリオごと）を登録した |
| R1-6 | パスの基準（minor） | 真 | 採る | `cell.windows.json` を公開物の根からの `kit/...` に直した。命令は `python` にそろえた |
| R1-7 | 外からの押下の規則がほぼ盲目になる帰結（minor） | 真 | 採る（研究者の選択: 逸脱 D4 で中止に数える） | D4: Windows の run は、観測の区間で送った押下に説明されない key 行が印を超えたら中止（`pipeline.py` `observation_abort_segments`）。§10.8・`deviations.md` D4 |
| R1-8 | 時計と所要時間の外挿（minor） | 真 | 採る | §10.11 Clocks（最大 25 分で測ったこと・§6.9 の macOS の値は当てはまらない）・§10.6 の所要時間を 1.06〜1.17 の比で 12〜13 時間に |
| R1-9 | S14 のキー・S4 の Escape・送出の経路（minor） | 真 | 採る | §10.5 に S14 の仮想キーと人のキーの違い、§10.7 Diagnostics に S4 の何回目の Escape で終わったか、§10.11 に手打ちとの比較をしていないこと |
| R1-10 | §10.1 の一覧がタグの差と一致しない・矛盾する注記（minor） | 真 | 採る | §10.1 の一覧を網羅（`notes.md`・selftest・説明文を含む）。`pipeline.py` の説明文を直し、`note_windows` に「note の Windows についての文を置き換える」と書いた |
| R1-11 | 観測器が行を 1 つも出さないとき（minor・自信 低） | 真（`pipeline.py` step 0 が拒む） | 採る | §10.7 Diagnostics: 拒まれ、セルは「測っていない」と報告する |
| R1-12 | nit（過去形・「39 of 39 in each of three runs」・run の数の食い違い） | 真 | 採る | §10.1 を凍結の時に真になる形に、§10.7 は TSF の 2 run と書き、README と記録の run の数をそろえた |

⚠️ 新しく足した部分（§10.3・D3 の新しい規則・D4・§10.7 の感度と診断と問 4・`scope_windows.py`）に新しい穴が無いかも見てください。
