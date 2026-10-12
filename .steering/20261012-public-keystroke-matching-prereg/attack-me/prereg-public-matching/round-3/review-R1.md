# R1 査読 round 3（打鍵の側路攻撃と打鍵データの匿名化の立場）

## 1. 接地
- 基準 1 monaco2017.txt:384-388 "there is a direct tradeoff between time lag and the obfuscation capability of the mix. As the lag decreases, the dependence between the arrival process and the generating process increase."
- 基準 2 monaco2017.txt:655-659 "In each fold, a single user's samples are used as the testing set and the remainder of the population as the training set. This emulates an open system, in which soft attributes for the target user are classified without having previously observed that user's keystrokes."
- 基準 3 monaco2019.txt:993-995 "compare this to a baseline attack in which the timing and language model probabilities are ignored" ／ :1018-1019 "Note that this baseline still uses information gained through keystroke detection and tokenization."
- 基準 4 monaco2019.txt:1312-1316 "it is sufficient to prevent keystroke detection or key identification to counter the attack. We consider the tradeoffs of several countermeasures and how they affect each source of information leakage." ／ :1323-1324 "padding may not be effective to mitigate keystroke detection and does not provide any protection against a timing attack."
- 基準 5 keytar2026.txt:241-243 "its reconstruction capabilities were primarily benchmarked against a random baseline, which might not fully capture the nuances of more sophisticated reconstruction challenges."
- 基準 6 keytar2026.txt:1370-1373 "input reconstruction is extremely sensitive to the accuracy of retrieved inter-keystroke timings. Making matters worse, detection errors propagate to consecutive detections"

## 2. 引き継ぎの判定（8 件）
解消 6（#3・#4・#5〔検証は凍結の前〕・#6・#7・#8）。一部 2: #1（R7 の検査が「道が切れる割合」のままで費用の歪みを捉えない → 指摘 2）・#2（R3-u の A3 の採点に長さの偏りと間隔の未定義 → 指摘 1）。#5 の補足: align.py の `ORDER` は固定で `max_group` は絞る方向にしか効かない（align.py:8・13）。R7 の群は `ORDER` の差し替えが要る。

## 3. 評価表
a 4（R3-u の予測の理由 :224 が手順に無い絞り込みを前提）／ b 3（R3-u の A3 の長さの偏り・R7 の検査）／ c 4 ／ d 3（R3-u の A3 が全文と窓で別の仕組み）／ e 4 ／ f 4 ／ g 3（R3-u の A3 の採点式・R7 の検査の量）

## 4. 指摘
- [major] 指摘 1 R3-u の A3 は候補によって尤度を足す項の数が違い、どの間隔を使うかも決まっていない（prereg:143「長さが違えば短い方の長さまで」・config.json:75）。項の数に比例して和が動き、長さで系統的に有利・不利。予測の理由（:224「全文字の数が合う候補の中で」）と手順が食い違う。最終稿で隣り合う 2 字が連続した押下でなかったときの間隔が未定義。再生の不確定で 1 対 1 の対応が以降すべてずれる。R3-u では Enter が「字」なので A1' の「行は Enter で区切る」が働かない。向きは R3-u が「効く」側（基準 4）。解消: (i) 項あたりの平均か、長さの尤度を足した合成の得点に固定 (ii) 使う間隔の定義 (iii) Enter の扱い (iv) 予測の理由を手順に合わせる。自信 高（偏りの存在）／中（向きと大きさ）。
- [minor] 指摘 2 R7 の検査が「道が切れる割合」（:112）だけでは上限を超えた群の害を捉えない。DP は群の境界をずらして吸収するので道は切れにくく、起きるのは正解の費用の膨らみ。p = 0.5 で 6 回以上続く箇所は 300 語で約 2.3 回、p = 0.25 で 4 回以上は約 0.9 回。費用 |x − (1−p)y| は二項の分散を無視し、尤度の攻撃者より弱い可能性（基準 6）。解消: 合成の記録で「真の群が上限を超えた割合」と「正解の費用と真の対応での費用の差」を報告・上限の決め方を固定・R7 の攻撃者が尤度に基づかないことを限定に書く。自信 中。
- [minor] 指摘 3 R7 の群の並びの変更が config で `ORDER` の差し替えとして書かれていない（config.json:63・align.py:8・13）。`max_group` を上げても (1,4) 以上は現れない。解消: R7 の群の列を明示・合成の記録に (1,4) 以上が選ばれる記録を含める。自信 高。
- [nit] 指摘 4 A4 の「20 区間ずつの塊」（:144・config.json:76）が語の区間か間隔 20 個か曖昧。
- [nit] 指摘 5 窓の R3-u の A3 は揃えの基礎が全文（A1' の再生）と違う（:159・:143）ことの注が無い。

変えていない箇所に fatal・major は無い。「最も強い攻撃者」が別々の攻撃者の最大で、長さと時刻を合わせた攻撃でない点は :270 の限定で開示の範囲と読む。

## 5. 総合の推奨: major
引き継ぎ 8 件のうち 6 件解消。新しい R3-u の A3 の採点式は項の数の偏りと間隔の未定義で凍結できる精度に無く、主な表で唯一「効く」見込みの行を良く見せる向き。直し方は局所的。直した文と合成の記録の検査の結果を合わせて再査読すれば凍結に進めると見る。

## 6. 読めなかった範囲・注入
context-B・round 1・2 の記録・decisions.md・書誌の本体・data.md・SEED は読んでいない。接地の本文は検索で当たった節だけ。注入の疑い: なし。
