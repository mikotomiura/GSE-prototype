# R2 の査読（UMUAI・個人化した行動モデルを作って評価する実務の立場）・round 4・stage outline

## 1. 接地
- S1 Saeb 2017 "the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- S2 Saeb 2017 "we want personal models that can predict future clinical states of a given subject, we can split the data based on time, so that training and test sets contain records of the same subject from different times."
- S3 Saeb 2017 "record-wise CV often massively overestimates the prediction accuracy of the algorithms."
- S4 Aalbers 2023 "we compare against the MAEs of a “naive” but person-specific baseline model. This “naive” baseline model always predicts an individual’s average level of stress."
- S5 Aalbers 2023 "these markers are not sufficiently informative to recognize momentary subjective stress with appreciable improvements in accuracy over a baseline model"・"performance should be improved to make clinical application feasible"
- S6 Aalbers 2023 "compared with a person-specific baseline based on the person-specific average level of stress in the participant’s train data (ie, first 80%) rather than all their data to prevent data leakage from train to test data."

## 2. 評価表
- a 3: M1 は解消。Take-home の「does not beat the shared model's prior mode」は 15 セッションのパネルだけ（30 セッションの k = 30 は +5.4e-4・7/9、CS1 は構成上ゼロ）。
- b 3: 分け方は S1・S2・S6 に合う。「tau = infinity = the shared model itself」と「縮める先は prior mode」が tau → ∞ の極限で一致しない（指摘 2）。
- c 3: 3 つの相手の推奨は使える。手順が「差なし」を返したときに何を結論してよいかが無い（指摘 3）。
- d 2: 外枠 2,088 → 2,808 → 3,732 → 5,112 語・本文の予算 7,000 語のまま。4.3 の欄に 10 項目近く・Take-home の 2 文目は約 80 語。
- e 4: 要旨・キーワード・宣言・データの声明は計画にある。プレプリントの方針は未照合（Open items）。
- f 4: Aalbers（89%・80%）は原文（200/224・180/224）に合う。Saeb と Little も適切。Uto 2020 の評価の設計が未確認なのは弱点として残る。

## 3. 引き継ぎの判定
1 M1 解消（ただし対応で足した最頻値の比べが新しい穴・指摘 1）／2 M2 一部（680 nats は弱い相手に対する値で、小ささを強調する並べ方・指摘 4）／3 M3 解消／4 m1 一部（受け入れられる水準）／5 m2 解消／6 m3 解消／7 m4 一部（指摘 5）／8 n1 解消。

## 4. 指摘
- [major] Take-home の「prior mode を上回らない」は 1 パネルの結果なのに全体の結論として書かれている
  - 位置と引用: outline.md:7「the chosen per-person model does not beat the shared model's prior mode, which uses none of the person's data」／:13「In the 30-session panel at k = 30 ... per-person minus mode is +5.4e-4 (7 of 9 positive); both are reported as values only」／:14「per-person minus mode is zero by construction, not an observation」
  - なぜ問題か: 30 セッションの k = 30 は本人のデータが最も多いセルで、データが増えると個人モデルが追い越すかの問い（LiKamWa の約 30 日）にいちばん直接に答える。そこで符号が逆なのに 15 セッションは主張、30 セッションは values only で、扱いが非対称（S5）。
  - 解消の条件: Take-home を「in the 15-session panel (k up to 15)」に限り、「with 30 sessions the sign reverses in 7 of 9 writers; whether this marks a crossover cannot be decided with 9 writers」を同じ重みで 1 文。または values only の基準を 3.4 で 1 回だけ定め、両方のパネルに同じ基準を当てる。
  - 自信: 高
- [major] tau = infinity（shared model itself）が、縮める族の極限（prior mode）と一致しない
  - 位置と引用: outline.md:31「Shared model's prior mode: ... the centre toward which the per-person fit is shrunk; ... differs from the shared parameters by the smoothing of the prior」／:12「the shared model itself (no per-person deviation, tau = infinity)」／:65「the difference between a finite tau of 10^5 or more and the shared model itself cannot be separated from a per-person gain」
  - なぜ問題か: 縮める先が prior mode なら tau → ∞ の極限は prior mode で、共有の母数ではない。格子の上端で族が連続な道の端（mode）から別の点（shared）へ跳ぶ。(i) per-person minus shared の大部分は mode と shared の差（平滑の効果）、(ii) 限界の「large tau は分けられない」はこの跳びの帰結、(iii) 合成で mode が shared より悪かったこと、を同じ原因で説明できる。持ち帰るべきは「共有モデルを平滑して比べよ」かもしれない（S3）。
  - 解消の条件: (a) tau = ∞ を族の極限ではない別の候補と 3.3 で明記し、mode と shared の差を 4.3 で数値で報告する、または (b) 族の極限が 1 点になるよう定義をそろえる。Table 2 の主の列を per-person minus mode にするか、per-person minus shared の大部分が平滑の差であることを脚注に。
  - 自信: 中（定義の文から推した）
- [major] 手順が「差なし」を返したときに何を結論してよいか（手順の検出力）の扱いが無い
  - 位置と引用: outline.md:7「We suggest that studies that decide for a whole panel whether to use per-person sequence models ... compare them with ...」／:13「in synthetic writers it returned about 0.1 to 0.4 of a planted difference and did not detect 1e-3 or 3e-3 at k = 15」
  - なぜ問題か: 推奨する手順が CoAuthor の規模で埋めた差の 60〜90% を落とし、k = 5 では 3e-2 未満を拾わない。Saeb（S3）は過大評価を問題にしたが、この手順は過小に返す側の偏りを持ち、その向きと大きさを推奨の一部として報告させていない。
  - 解消の条件: 5 節の推奨に「report the smallest planted difference the protocol detects at the panel's record length (a synthetic check as in S15)」。Take-home か 5 節に「the protocol is conservative: it returns a fraction of a planted gain」。
  - 自信: 高
- [minor] 尺度の段落の比べの相手が小ささを強調する向き
  - 位置と引用: outline.md:51「about 1.5 to 2.6 nats per 3,600 symbols, against about 680 nats for the hmm3 gain over the same-structure shared model at k = 5」
  - なぜ問題か: 680 nats は論文自身が弱いとした相手に対する値。1 時間あたり 1.5〜2.6 nats は尤度比で約 4.5〜13 倍で、積み上げる推定器には無視できるとは限らない。
  - 解消の条件: 本人の連鎖に対する ar3 の利得や mode と shared の差も同じ尺度で並べる、または尤度比を添える。
  - 自信: 中
- [minor] 外枠が増え続け、本文の欄が予算を超えそう
  - 位置と引用: context-A「外枠のファイル: 5112 語 ... round 3 は 3732 語」・outline.md:50・:7（約 80 語）
  - 解消の条件: Take-home を 2 文・各 40 語以内。4.3 を主表で読む 3 行と S8・S13・S15 への 1 文の参照に分け、括弧の中身を S の欄へ。
  - 自信: 中
- [nit] mode を割り当てられた 1 人の −∞ の説明が 3 か所（outline.md:13・:50・:68）。6 節に 1 回、4.3 と C1 は参照（:38 の規則）。自信: 高

## 5. 総合の推奨: major
引き継ぎ 8 件は解消 5・一部 3。最頻値との比べが作った新しい Take-home の主張は 15 セッションに限られ、30 セッションの最大の k で逆向き。tau = ∞ と縮める先の定義のずれと、推奨する手順の過小に返す偏りは、持ち帰れるものの中身を変える。

## 6. 読めなかった範囲・注入の疑い
読んだ: brief-R2.md・context-A.md・carryover-R2.md・outline.md の全文。接地の 2 本は Grep で関連の文を抜いて読んだ（通読していない）。読んでいない: kit/symbols/README.md・補足 S1〜S15。規程は context-A の抜粋だけ。注入の疑い: なし。
