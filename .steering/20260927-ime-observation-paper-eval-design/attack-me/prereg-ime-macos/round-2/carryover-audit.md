# carryover-audit — round 1 からの引き継ぎ（意図の監査役）

作成: 2026-10-01（メイン）。あなた（監査役）の round 1 の指摘 27 件（1-1〜1-9・2-1〜2-5・3-1〜3-13）について、メインの裏取り・研究者の採否・対応・未解決を書く。採否の一次は `decisions.md` の判断 99〜107（context-B の範囲）。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行）、新しい食い違いを探してほしい。★ 判断 99〜107 が新しい意図なので、**判断 99〜107 と今の事前登録・公開物の食い違い**（決めたのに書かれていない・書き方が判断と違う）も見てほしい。

## 版と節番号の変化（round 1 の版 `d0cf4343` → 今の版）

⚠️ round 1 の行番号は使えない（本文は約 5,300 語から約 9,300 語に増えた）。節番号は次のとおり変わった。

| round 1 | 今 | 備考 |
|---|---|---|
| 題 "agreement of a content-free observer … with the input method's own state" | "agreement between an observer … that records no text and the input method's own calls" | |
| §3.3 Sample size and settings of the plan | §3.3 Sample size, precision and settings of the plan | 精度の表を足した |
| — | **§4.5 The observer's specified rows (prediction)** | 新設 |
| §4.5 Texts | §4.6 Texts | |
| §6.1 Units and intervals | §6.1 Units, intervals and wording | |
| §6.2 Exclusions | §6.2 Exclusions and other contingencies | |
| §6.3 Plan versus ground truth | §6.3 Plan versus ground truth, and delivery of the presses | |
| — | **§6.4 Scopes and comparisons** | 新設 |
| §6.4 Q1 / §6.5 Q2 / §6.6 Q3 / §6.7 Q4 | §6.5 / §6.6 / §6.7 / §6.8 | |
| §6.8 Clock / §6.9 Q5 / §6.10 Missing / §6.11 Exploratory | §6.9 / §6.10 / §6.11 / §6.12 | |
| — | **§7 Threats to validity and limitations** | 新設 |
| §7 Deviations and addenda / §8 Freeze | §8 / §9 | |

読んでよいファイルに、`kit\analysis\spec_predict.py`・`kit\analysis\delivery.py`・`kit\emit\keymap_macos.json`・`kit\logger\src\driver_macos.rs`・`kit\logger\src\driver_macos\keymap.rs` を足した（context-A の一覧）。

## 指摘ごとの引き継ぎ

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。3-2 だけ「部分的に真」、ほかは「真」。

### 1. 意図にあって対象物に無いもの

- **1-1 判断 91 の限界が無い** → 真。対応: §7 "The input method's learning is not reset"（ブロックの中の依存は区間が覆うが、ブロックをまたぐ依存は覆わない）・§3.2 に実行の順と理由（判断 107 の 7）。§6.1 の「trials in one block share the state of the input method」の文は残っている。
- **1-2 handoff §2 の 4（構造から予想できる偏り）** → 真。研究者の採否（判断 100）: 数の予想ではなく、決定的な「仕様の予測の行」を参照として登録し、正解 対 予測（`gt_pred`）・予測 対 観測（`pred_obs`）の 2 段で報告する。対応: §2.2・§4.5・§6.4・§7。
  - 未対応: あなたの付随の指摘（round 1 の §6.8「a session is still paired as long as the offset … stays at or below a third of its length」は 2 つの区間の長さが同じときにしか成り立たない）。今の §6.9 にも同じ文が残る。
- **1-3 think の目的が探索に回っている** → 真。対応: §2.3 Think time（設計上の役割は、セッションを 20 秒の打ち切りの両側に置くこと・登録した解析の要因ではない・依存の解析は探索）・打ち切りは `over_limit` の範囲で見る（§6.4・§6.6 Cut-off）。
- **1-4 連続量の精度の目標が無い・notes.md は在ると言う** → 真。研究者の採否（判断 103）: 幅の表＋形容しない。対応: §3.3 の精度の表と連続量の精度・§6.1 第 2 段落・`notes.md` の文を「予定の n で見込む精度」に。
- **1-5 E3 `working` の run を E1 と分けると書いていない** → 真。対応: §6.2 Other contingencies の最後（問 5 の `working` の run は問 1〜4 に使わない）・§3.2 の順・§3.4 の問 5 の条件のやり直し。
  - 書いていない: 8 時間で止めた後の計画の残り（§6.10 は「for eight hours」とだけ書く）。
- **1-6 L2 のシナリオの混合が落ちている** → 真。研究者の採否（判断 104）: シナリオ × 速さ別の試行ごとの差を足し、文ごとの値と ICC は均等な混合の下での値と明記。対応: §6.7 第 2 段落。シナリオの混合を変えた合成テキスト母集団は足していない。
- **1-7 IME の異常終了** → 真。対応: §6.2 Other contingencies（入力法が応答しなくなった・再起動した試行は除かず、食い違いとして報告）。
- **1-8 計画の SHA-256** → 真。対応: §2.4（2 台・Python 3.11.9 と 3.14.4 でバイト一致・計画の SHA-256 が違う run は解析しない）。
- **1-9 E3 の Windows** → 真。対応: §1.3（追補は Windows のセルと Windows の問 5 だけ）・§8。

### 2. 対象物にあって意図に無いもの

- **2-1 題の content-free** → 真。対応: 題を "an observer of Japanese input-method conversion that records no text and the input method's own calls" に。
- **2-2 n の根拠の入れ替わり** → 真。対応: §3.3（精度で選び、その後で 1 晩に収まることを確かめた）。
- **2-3 盲検の言い方** → 真。対応: §2.5（読んだ key 行は macOS では観測器がセッションを推論する入力そのもので、盲検は出力を伏せたのであって入力を伏せたのではない）。
- **2-4 K0 / K1 の意味** → 真。対応: §6.8 Open set（K0 は 1 文字の頻度だけを知る・同じコーパスの学習側から推定／K1 は作品を除いた 3-gram）。
- **2-5 パイロットの手打ち** → 真。対応: §3.1 の「In addition, outside the runs, …」の段落（診断で、記録はデータに入らず預けない）。

### 3. 矛盾

- **3-1 判断 97 の「K = 1000 でも意味を持つ」が成り立たない** → 真（メインが二項分布で再計算: n = 2,925 で 0.210・n = 2,700 で 0.067）。研究者の採否（判断 101）: K = 1000 を判定から外し、通る確率の表を載せ、2 セルの両方を求める。対応: §6.8。
- **3-2 判断 92 と判断 98 の 6 が両立しにくい** → 部分的に真（round 1 の §7 が縛るのは Windows の追補だけで、他の追補は縛っていなかった。新しいファイルの追加が許されるかが読めない点は真）。研究者の採否（判断 106）: 他の IME と参照入力欄以外のアプリでの転移はこの研究の外（別の研究）。追補は Windows（セルと問 5）だけで、Windows のセルだけが使う新しいファイルの追加を許す。対応: §1.3・§8・`notes.md`。
- **3-3 ハッシュに入る `_note`** → 真。対応: `config.json`・`gt_rules.json` の `_note` を凍結の前に段階凍結に合わせて書き直した（凍結のハッシュの値は変わる）。
- **3-4 §1.2 の参照先** → 直した（今は "section 6.8"・節番号の振り直しの後の値）。
- **3-5 正解ログの中身** → §4.2 に「the key code of each key-down it receives, and each change of its focus」を足した。
- **3-6 持ち越しの件数** → §6.2「two carry-overs with live conversion on, in S8 and S10, excluded four trials」。
- **3-7 `dwell_ms == 0` の書き方** → §6.2（長さ 0 の区間として照合に残り、偽検出として数え、すべての箱で件数を出す）・§6.6（このような行は対にならない）。round 1 の §6.5 の「Pairs whose `dwell_ms` is zero are left out」は消した。
- **3-8 「Every estimate is reported with an interval」** → §1.2「Every proportion and every continuous estimate is reported with an interval; F1 and the counts are reported without one」。
- **3-9 `pilot-macos.md` の所要時間** → 直した。
- **3-10 `pilot-macos.md` の学習の記述** → 直した（リセットの方法は見つからず、本計測でもリセットしない）。
- **3-11 `kit/run/README.md` の時計** → 直した（runner も解析も合わせない・マーカーで測って報告）。
- **3-12 `notes.md` の結果のファイル名と informative** → 直した（`results/e2_closed_set_<cell>.json` など・E3 は `kit/e3/summarize_e3.py` の標準出力を `results/e3_<system>.txt` に・「予定の n で見込む精度」）。
- **3-13 `kit/gen/README.md` の「まだ決めていない」** → 直した。

## 未解決（意図の側で残したもの）

- 先行研究の位置づけの段落（書字の打鍵記録・時刻の検証の伝統）は、原稿に回した（判断 107 の 8）。事前登録には §7 の 1 つ目（基準をソフトの層に置く理由）と "Software clocks" だけ。
- パイロットの生ログを預ける基準は、まだ書いていない（測定機での残りの作業）。⚠️ 事前登録の書き直しで、round 1 の §3.1 にあった「its raw logs will be deposited with the measurement data after the check that report describes」の文が落ち、今の事前登録には、パイロットの生ログを預けるという文が無い（判断 99〜107 には、この文を消す判断は無い）。
