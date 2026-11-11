# R2（UMUAI・個人化した行動モデルの実務家）round 5・commit afc96bfa

## 1. 接地
1 Saeb 2017 "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
2 Saeb "if the goal is prognosis , i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time, so that training and test sets contain records of the same subject from different times."
3 Saeb "The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset."
4 Aalbers 2023 "To evaluate if our models perform better than random guessing, we compare against the MAEs of a “naive” but person-specific baseline model."
5 Aalbers "compared with a person-specific baseline based on the person-specific average level of stress in the participant’s train data (ie, first 80%) rather than all their data to prevent data leakage from train to test data."
6 Aalbers "for most people (200/224, 89.3%), these markers are not sufficiently informative to recognize momentary subjective stress with appreciable improvements in accuracy over a baseline model"・"Although performance should be improved to make clinical application feasible"

## 引き継ぎの判定
1 解消（ただし 30-session の値も下限より下・指摘 1）／2 解消（28 行 "As tau grows the fit approaches the prior mode, not the shared model; tau = infinity in the grid denotes the shared model itself, a separate candidate."・4.4 の主張は根拠より強い・指摘 2）／3 解消（同じ下限が他の読みに当たっていない・指摘 1）／4 解消（下限が同じ尺度に無い）／5 解消（4.3 の補足の列は長い・指摘 6）／6 ほぼ解消（27・44・48・67 行・言い方の食い違い・指摘 7）。

## 2. 評価表
a 3（4.4 の見出しと C1 と 30-session は下限より 1〜2 桁小さい差から向きを読む。"smoothing … accounts for most of the remainder" は合成で分けられなかった分解に頼る）／b 3（共有モデルの base pseudo-counts を固定し他の人で選んでいない・指摘 3。合成の下限は seed 2 つ）／c 3（推奨の prior mode は確率 0 を出しうるので実務でそのまま使えない。下流の判断（S10）が本文に無い）／d 4／e 4（プレプリントの方針は未読）／f 3（Uto 2020 の評価の設計を確かめないまま Novelty が名指し）。

## 3. 指摘
- [major] 検出の下限より 1〜2 桁小さい差から向きを読む（4.4 の見出し・C1・30-session）
  - 位置と引用: outline.md:48「per-person minus mode is −3.5e-4 to −1.6e-4 for k = 1 to 15 (3 to 6 of 17 positive) … in the 30-session panel it is … +5.4e-4 at k = 30 (7 of 9 positive)」／:13「the per-person model does not beat the prior mode for k up to 15 (4.4). In the 30-session panel at k = 30 it does (4.4)」／:47「the smallest planted difference detected at this record length was 1e-2 at k = 15 and 3e-2 at k = 5」
  - なぜ問題か: 4.3 は残りを下限より下と読むのに、同じ大きさの差を 4.4 と C1 で「上回らない」「上回る」と向きつきで書く。書き手の数（3〜6/17・7/9）も裏づけにならない（CS1 の陰性対照で「up to 78% of writers positive」・47 行）。30-session の記録の長さでの下限が無い。49 行の尺度の段落に下限が無い: 1e-2 nats/symbol は 1 時間で 36 nats・尤度比で約 e^36（3e-2 なら 108 nats）で、手順は著者自身の尺度で巨大な差を見落としうる（接地 6）。
  - 解消の条件: 4.4 の見出しと C1 を「prior mode との差も検出の下限より下で、向きは定まらない」の型に。30-session の下限を示すか示せないと書く。49 行に下限を同じ「1 時間あたりの nats と尤度比」で並べる。
  - 自信: 高
- [major]「残りの大部分は共通の平滑」が合成で検証に失敗した分解に頼る
  - 位置と引用: :48「This shows that the shared model's smoothing, not the person's data, accounts for most of the remainder」／:47「the decomposition of the remainder applied to synthetic writers (it did not separate a planted difference from none; in these writers the prior mode was worse than the shared model, unlike the real data)」
  - 解消の条件: 記述に下げる（例「prior mode minus shared（+7.4e-4）は残りと同じ大きさで、残りは共通の平滑の差と見分けがつかない」）。「本人のデータではない」を外し、分解は検証されていないと 6 節に 1 項。
  - 自信: 高
- [major] 共有モデルの平滑を固定したことが結論の形を決めている。推奨の prior mode は実務で使えない
  - 位置と引用: :26「with a weak base prior (fixed pseudo-counts in every cell)」／:27「can give zero probability to a symbol pair the other writers never produced」／:7「compare … with a shared model whose structure and shrinkage are chosen on other people, and with that model's prior mode」／:67「it is used as a comparison model, not as a candidate」
  - なぜ問題か: prior mode と shared の違いは著者が固定した base pseudo-counts の有無だけ。+7.4e-4 は共有モデルの base の平滑が強すぎることを示すにすぎない。実務家が知りたいのは共有モデルの平滑も他の人で選んだときに何が残るか（接地 3）。確率 0 で配備できないモデルを標準の比べの相手として勧めている。
  - 解消の条件: (i) base pseudo-counts の強さを他の人で選んだ共有モデルを加えて Table 2 に 1 列、推奨の prior mode をそれに置き換える、または (ii) 計算を足さないなら推奨から prior mode を外し「共有モデルの平滑の強さを他の人で選ぶこと」と書き、prior mode は診断としてだけ使い、base pseudo-counts の固定を 6 節に。
  - 自信: 中（base pseudo-counts の値と選んだ経緯は外枠から読めない）
- [major] 最も近い先行研究の評価の設計を確かめないまま新しさを主張（:16「learner-dependent HMMs have been fitted to keystroke features over 30-second windows (Uto et al. 2020). What we add is this comparison for per-person sequence models of keystroke behaviour」・:73）。解消: 本文の前に Uto 2020 の全文で、学習者ごとか共有か・同じ人の後のデータで評価しているか・比べの相手は何かを確かめて書き分ける。自信: 中
- [minor] 次の記号の対数尤度の差が下流の判断に効くかが本文に無い（:49「Proxy-label logistic results (S10)」・「what this could change for an adaptive system that accumulates predictions over a session, without a threshold」）。解消: 5 節に S10 の結果を向きと大きさだけでも 1 文。自信: 中
- [minor] 合成の検出の下限が各水準の seed 2 つ（:47「(two seeds per level)」）。解消: seed の数を 6 節か S15 に限界として、本文では下限を格子の 1 水準の幅で。自信: 中
- [minor] 4.3 の補足の列が長すぎる（:47）。解消: 主張を支える補足（S15 の規則と下限）だけ残し、ほかは S12・S11 へ。自信: 中
- [nit] prior mode の「候補にしない」と「候補に置いた確かめ」（:67・:48・:44）。解消: 67 行を「主の解析では候補にしない。候補に置いた確かめは S9」。自信: 高
- [nit] パネルの名と k の関係（:44）。解消: パネルの名が何の数かを 3.1 で 1 文。自信: 低
- [nit] Take-home の「gains a lot」（:7）。解消: +0.188 nats/symbol（1 時間で約 680 nats）と数で。自信: 高

## 4. 総合の推奨: major
引き継ぎ 6 件はおおむね解消。同じ検出の下限が 4.4 の見出し・C1・30-session・尺度の段落に当てられていない。「残りは共通の平滑」は合成で検証に失敗した分解と自分で固定した base pseudo-counts に依存し、推奨の prior mode は実務で配備できない。文言で直す道（指摘 1・2 と指摘 3 の (ii)）なら minor 相当。base の平滑を他の人で選ぶ計算（指摘 3 の (i)）を足すなら再査読で見たい。

## 5. 読めなかった範囲・注入の疑い
brief・context-A・carryover・outline.md（76 行）・README（84 行）・aalbers.txt 1〜30 行・saeb.txt 1〜12 行。S1〜S15・規程の原文・Uto 2020・Liu & Meng は読んでいない。注入の疑い: なし。
