# carryover-R2 — round 1 からの引き継ぎ（R2: 打鍵記録を使う書字研究の利用者と、公開の安全の立場）

作成: 2026-10-01（メイン）。あなた（R2 の立場）の round 1 の指摘 16 件（major 5・minor 8・nit 3）について、メインの裏取り・研究者の採否・対応・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行）、新しい穴を探してほしい。
「採らなかった」部分は研究者の選択で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

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

読んでよいファイルに、`kit\analysis\spec_predict.py`（予測）・`kit\analysis\delivery.py`（配送の報告）・`kit\emit\keymap_macos.json`・`kit\logger\src\driver_macos.rs`・`kit\logger\src\driver_macos\keymap.rs` を足した（context-A の一覧）。

## 指摘ごとの引き継ぎ

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。16 件すべて「真」。

### major-1 E2 の推奨は、合成の打鍵では時間のチャネルがもともと空なので、時刻を含む粒度が安全だという根拠にならない
- 裏取り: 真（`generate_plan.py` の間隔はキーによらず引かれる・攻撃は 600 ms 未満の間隔を捨てる）。
- 研究者の採否: あなたの (a) に近い形。ms の時刻を持つ集合（`all`・`no_runs`）は「この設計では評価できない」と事前に書き、推定だけを報告する。推奨の対象は、時刻を持たない集合（`no_time`・`counts_only`）と **1 秒のビンの集合（`bin1s`・`bin1s_count`）** の 4 つ。1 秒のビンを残した理由: 人の記録で内容を漏らす 2 字の組の間隔（数十 ms）は 1 秒のビンで消える。人の休止の型（語や句のあいだの休止）を模していないことは限界に書く。(b) の、キーに依存する間隔のモデルを攻撃者に足すことは採らない。
- 対応: §6.8 の第 4 段落（"The synthetic key intervals are drawn independently of the keys …"）・§3.3 Key intervals の最後の文・§7 "The input is synthetic"・`kit\e2\README.md` の追記。

### major-2 near chance の「Wilson の上端 ≤ 2/K」は K = 1000 ではほとんど満たせず、K = 10 では甘い
- 裏取り: 真（メインが二項分布で再計算: 偶然の水準の攻撃が通る確率は n = 2,925 で 0.210、n = 2,700 で 0.067。K = 10 は偶然の約 1.85 倍、K = 100 は約 1.47 倍まで通る）。
- 研究者の採否: K = 1000 を判定から外して記述にとどめる。K = 10・100 は 2/K のまま判定し、真の正解率が 1/K・1.5/K・2/K・3/K のときの「通る確率」の表を事前登録に載せる。推奨は 2 セルの両方・K = 10 と 100 の両方で near chance の集合に限る。
- 採らなかった: 余裕を n に応じて決め直すこと・平均順位や上位 n 位の正答（情報量）を判定に加えること。E2 で数える n は「S12 を除いた計画の試行数」（ON 2,925・OFF 2,700）として書いた。§6.2 の除外を E2 に当てるかは書いていない。
- 対応: §6.8 の near chance の段落と表。

### major-3 推奨の粒度がセッションの行を扱っていない
- 裏取り: 真（攻撃はセッションの行を読むが使わない・round 1 の §6.7 は攻撃者が「the session rows」を見ると書いていた）。
- 研究者の採否: セッションの行は**推奨の対象外**と明記する（攻撃は key 行の区分と時刻だけを使う）。
- 対応: §6.8 の第 1 段落の最後（"they do not use the session rows, so the session rows are outside the scope of the recommendation below"）・`kit\e2\README.md` の追記。
- 採らなかった: セッションの行を公開する形（丸める・削る）を決め、攻撃の入力にも同じ変換をかけること。

### major-4 仕様どおりの 20 秒の打ち切りを recall の分母と L2 の正解側に含めるかが書かれていない
- 裏取り: 真（`match.py`・`l2.py` は除かない）。メインが計画から数えると、観測器の定義の期間が 20 秒以上の試行は slow で約 32%、mid 約 11%、fast 約 9%（あなたの見積もり約 9% より、思考を挟む slow では大きい）。
- 研究者の採否: (i) 打ち切られない試行（`under_limit`）を問 1・問 2 の主の範囲にし、打ち切られる試行は `over_limit` で別に数える。範囲は送出の記録から観測器の定義で決定的に計算する（§4.5 の予測）。(ii) L2（問 3）は全試行（研究者が受ける偏り）を主、打ち切りの試行のセッションと行を両側から抜いた版を副にする。文は残す（文ごと捨てると slow の文はほぼ全部消える）。
- 対応: §1.2 の問 2 と最後の段落・§3.1 の最後の段落・§3.3 "Trials under the cut-off" の表・§4.5・§6.4・§6.6 Cut-off・§6.7（問 3 の範囲は §6.4 の Scopes の最後の段落）・§7 の最後の項目。
- 採らなかった / 書いていない: (iii) L2 の偏りを「打ち切りの分」と「それ以外」に分けて報告すること（主と副を並べるだけで、分解とは書いていない）・中央値か対数の平均の変換時間を足すこと。

### major-5 L2 の「文」はシナリオを等しく混ぜた人工の 8 試行
- 裏取り: 真。
- 研究者の採否: あなたの解消の条件の前半を採った。3 つの試行ごとの差（変換の数・変換時間の和・取り消した変換の数。観測 − 正解）を、両側の平均とブロックのブートストラップの区間つきで、シナリオ × 速さ別に報告し、読者が自分の混合で重み付けし直せる形にする。文ごとの値と ICC は「この設計の均等な混合の下での値」と明記する。
- 対応: §6.7 の第 2 段落。
- 書いていない: 読者に向けた主の量を Bland-Altman の偏りと一致の限界（単位つき）に置くこと（§6.7 は偏り・一致の限界・ICC を並べ、速さ別を主とする）・シナリオの混合を変えた感度の解析。

### minor-1 キーの行の時刻の正確さが推定の対象に無い・注入はハードウェアの経路を通らない
- 裏取り: 真。
- 対応: §6.3 の配送の報告（記述・セルと速さごと）: 計画の予定に対する送出の遅れ・両方向の到達・送出の無い行・全部が届いた試行での「行の遅れ」と「打鍵間隔の誤差」・入力モードのキーを含む / 除く。§1.2 の最後の段落。物理キーの経路には主張しない（§6.3・§7）。
- 足していない: 時刻の量子化。

### minor-2 4 つの集計量を「書字の研究者が計算する」とする根拠が無い
- 裏取り: 真。
- 対応: 問 3 を "four aggregates a writing researcher might compute" に（§1.2）・§4.6 の最後の文（"The four measures are examples … they were not selected from a review of the writing literature."）。文献を引く段落は原稿に回した。

### minor-3 プールの重みが本文と実装で食い違う
- 裏取り: 真（`match.py` は件数を足す）。
- 研究者の採否: 本文を実装に合わせて「件数の和」と書く（各層の計画の試行数は等しいので、除外と範囲を除けば均等に近い）。
- 対応: §6.1 第 1 段落。

### minor-4 割合の区間がブロックを無視・n の根拠が L2 と E2 を含まない
- 裏取り: 真。
- 対応: §6.1（層の 75 試行は約 42 ブロックに散るので層の中では効果が小さい・pooled の割合は不確かさの下限と読む）・§3.3 の割合の精度の表と連続量の精度（SD と設計効果の関数・速さごとの文の数とブロック数）・E2 は §6.8 の通る確率の表。一致の限界・kappa・ICC の幅は「推定値に依存し、推定として報告する」と書いた。
- 採らなかった: 割合をクラスターに頑健な区間に揃えること。

### minor-5 粒度の候補が ms と 1 秒しかなく、その粒度で書字の指標が残るかが登録されていない
- 裏取り: 真。
- **対応なし**: 研究者が承認した直す一覧に入らなかった（中間の粒度〔100 ms・250 ms のビンなど〕も、各集合で計算できる書字の指標の表も足していない）。

### minor-6 本測定の預けの検査に「キーの行がすべて送った打鍵と対応すること」が無い
- 裏取り: 真。
- 対応: `data.md` の手順 4（配送の報告で、両方のログの送出の無い行が 0、試行の外の行がマーカーとかなの押下〔1 ブロック 5〕を超えないこと。満たさない run は説明がつくまで預けず、報告する）。

### minor-7 パイロットの生ログを預ける基準がまだ書かれていない
- 裏取り: 真。
- **未解決**: 基準はまだ書いていない（測定機での残りの作業）。`pilot-macos.md` の "Raw logs" の節は「基準をここに書く」のまま（`delivery.py` が両方向を数えることは書き足した）。⚠️ 事前登録の書き直しで、round 1 の §3.1 にあった「its raw logs will be deposited with the measurement data after the check that report describes」の文が落ち、今の事前登録には、パイロットの生ログを預けるという文が無い。

### minor-8 1 試行の時間と 1 run の時間が、パイロットの報告と計画書で違う
- 裏取り: 真。
- 対応: `pilot-macos.md` を直した（11.2 / 11.4 s はパイロットの間隔での推定・本番は 13.6 / 13.8 s と 11.9 / 11.2 h）。

### nit（3 件）
- macOS で 2 つの定義が同じセッションになる → §5: `macos_def` が解析の定義、`all` は同じセッションかの確認（`same_sessions_as_all`）だけ。
- bootstrap の回数 2,000 と 1,000 → open set も 2,000 に揃えた（§6.8 のコマンド）。
- 「non-zero duration」 → §4.6 を「over the rows with a non-zero `dwell_ms`; every session has a positive duration」に直した。
