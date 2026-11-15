# review-R1（round 3・paper-reviewer・opus）
接地: Chukharev-Hudilainen「(somewhat arbitrary) cut-off value」「tpause considerably varies across participants」「statistically significant differences ... were found for thresholds up to t = 1,200 ms ... from t = 1,300 ms and up, the difference in proportions is no longer significant」「those occurring after the input textbox had lost and regained keyboard focus」。Hanisch ら「implies a weak adversary」「attacker models should be made explicit」「Vassallo et al. [160] explore suppression of keystrokes to preserve the content」「Leinonen et al. [151] investigate the anonymization of keystroke timing data using two rounding approaches ... the identification drops from close to 100% to below 10%」「small group size with high data quality」「any PET poses a trade-off between privacy and functionality」。
carryover: N2 一部（漏れの結果は既に否定の答え・M1）／N1 解消／N3 一部（入力が足りない・完成の条件・M2・M3）／N4〜N6・N8〜N10 解消／N7 一部（伝統の内側の近い先例と比べていない・m1）。
評価: a3 b3 c3 d4 e4 f3。
- [major] M1 漏れの結果（どの粒度も規則を満たさず推奨は「なし」）は既に否定の答えを出しているのに、尖りは「決める」と言い §4 は「未決」と書く。道具の入力は時刻も取るので情報はさらに多い。解消: 今の結果から言えることを 1 文（キーの種類の列を外に出す範囲を限る）、未決なのは何か（時刻を粗くする幅・外に出す先）を分ける。できなければ尖りを「決める手順を作る」に弱める。自信 高。
- [major] M2 完成の条件「GSE 自身の記録に当てて地図が出ること」が、どの面で何を正解に出すのか読めない（点も内容の正解も無い・窓の切り替えの扱い）。解消: 面ごとに書き分け、正解の無い面は「未検査」と出すと明記、窓の切り替えと離席を定義の選択肢に。自信 中。
- [minor] M3 入力に結果の変数と事前登録の記録が無い。格は利用者の申告を写すと書く。自信 高。
- [minor] m1 閾値を動かすと有意性が変わることは既知。差は「向き」と報告の型にある、と §5 に。自信 中。
- [minor] m2 打鍵の内容保護（Vassallo ら）と時刻の丸め（Leinonen ら）の先行を「既にあること」に足し、差を「機能の側が作業の状態の推定」に絞る。自信 中。
- [minor] m3 地図の単位（観測 × 対象）を 1 文で。IME の行は注に。自信 中。
- [minor] m4 攻撃者の想定を本文の表に・段 1 の 3 名の記録の外に出す範囲を漏れの結果に従って決める。自信 中。
- [nit] n1 「作文の点」が CS1 に当てはまるか。自信 低。
総合: major（数文の書き直しで消えうる）。
読めなかった範囲: chukharev の 1,236 行以降・hanisch の一部・根拠のパス。注入の疑いは無い。
