# angle A1: 打鍵の生体認証（Q1 と Q3 が中心・2026-11-23）

読み方の凡例: 「本文」は PDF を pdftotext で読んだもの、「抄録」は抄録・書誌ページだけ、「書誌のみ」は Crossref などで書誌だけ確かめたもの。DOI は自分で開いて（Crossref / arXiv / 出版社ページ）確かめたものだけを「確認」とした。

## 先に結論（正直に）

- Q1（26 記号のような粗いリズムの記号列・遷移の表で書き手を見分けた先行）は、**直接の先例を見つけられなかった**（検索式は末尾）。近いのは (a) 時刻の絶対値でなく順位や粗い時間の分解能で識別する系（Gunetti & Picardi の R 距離・clock resolution・timestamp 精度の研究）と (b) 遷移の行列を画像状の特徴にして識別する系（Sharma ら）。どれも 30 秒窓の要約値を量子化した記号列の遷移表ではない。
- Q3 のうち「日をまたぐ低下」は先例が厚い。ただし**ほぼ全部が固定文・短い入力・登録と照合の検証（verification）**で、自由作文の長い窓の要約が間を空けて落ちるかを測ったものは見つかっていない。
- 反証側（粗い特徴・長い窓では識別できない）は見つからなかった。逆に「粗くしても識別は保たれる」側の報告があり（Dehling ら）、**新しさを減らす側に効く**。ただし粗くしたのは時刻の分解能であって、窓の要約や量子化ではない。

## 1. Dehling, Koch, Lo Iacono & Federrath — You Are as You Type（本文を読んだ）

- 書誌: Dehling, F., Koch, S., Lo Iacono, L. & Federrath, H. — You Are as You Type: Investigating the Influence of Timestamp Accuracy on the Robustness of Keystroke Biometrics. IEEE TrustCom 2024, pp. 469-480。DOI 10.1109/TrustCom63139.2024.00082（Giessen 大学の研究ポータルの表示。doi.org は未開）。本文 PDF は jlupub.ub.uni-giessen.de の preprint。
- 設計: 公開の固定文データ（CMU の 51 人 × 400 回）と自由文データ（Gunetti & Picardi 系・28 人 × 15 サンプル）。ブラウザの timestamp 精度（既定・Firefox の resistFingerprinting 16.667 ms〜200 ms）を再生で再現し、Euclid / Manhattan / 尺度つき Manhattan / Mahalanobis と R・A 距離の分類を回した。
- 逐語:
  - "they are surprisingly resilient to larger timestamp modifications, which results in a serious threat to users' privacy"
  - "the variances of the timestamps resulting from the manipulation experiments are still smaller than the variance required to differentiate individuals based on typing behavior"
  - "Using RFP-modified data only, the EER for the fixed-text algorithm only decreases by up to 10% while the FRR of the free-text algorithm increases by 25%, both if timestamp precision is limited to 200 ms"（※ 文中 "decreases" は原文のまま。増加の意味と思われる）
- 数: 自由文の誤分類率は元データで 2.96%、既定のブラウザ丸めで 2.2〜3.2%（Table III）。RFP 200 ms を使った改変データだけで 24% まで上がる。登録を元・照合を改変にすると固定文の Mahalanobis の EER は 91%（200 ms）。**登録も照合も同じ丸めなら劣化は小さい**。
- Q1: 近いが違う（粗い**時刻の分解能**でも識別が保たれる。窓の要約・量子化した記号列ではない）。重要な含意として、登録と照合で粗さが違うと壊れる（この研究の「間を空けた」でなく「粗さの食い違い」）。
- 照合: references.md に無し。

## 2. Killourhy & Maxion — The Effect of Clock Resolution on Keystroke Dynamics（書誌のみ・抄録は取れず）

- 書誌: Killourhy, K. S. & Maxion, R. A. — The Effect of Clock Resolution on Keystroke Dynamics. RAID 2008, LNCS 5230, pp. 331-350。DOI 10.1007/978-3-540-87403-4_18（Crossref・Semantic Scholar で確認。出版社の抄録は閉じていて本文未読）。
- 内容は題からの推定にとどまる（クロックの粗さが検出器の誤り率にどう効くかを測った研究）。**数と結論は未読。** Dehling らの本文が先行として挙げているのに近い系統なので、メインが本文を取れるなら最優先で読む価値がある（粗くしたときの落ち方の古典的な先例になりうる）。
- Q1: 近いが違う可能性（未読のため断定しない）。
- 照合: references.md に無し。

## 3. Gunetti & Picardi — Keystroke analysis of free text（抄録のみ）

- 書誌: Gunetti, D. & Picardi, C. — Keystroke analysis of free text. ACM TISSEC 8(3):312-347, 2005。DOI 10.1145/1085126.1085129（Crossref で確認）。
- 逐語（Crossref の抄録）: "a few lines of text, even collected in different working sessions, are sufficient to reach a high level of accuracy, which improves proportionally to the amount of available information"。205 人・False Alarm 5% 未満・Impostor Pass 0.005% 未満。
- 設計の要点（Dehling 本文の記述より）: R 距離は **時間間隔の順位**の食い違いを数える。絶対値でなく順位という粗い要約で自由文の識別ができる、という意味で Q1 に近い。ただし n-graph（二連・三連の文字列）ごとの時間であって、時間窓の要約ではない。
- Q3: 「異なる作業セッションにまたがっても可」とあるが、**間隔の長さを変えて落ち方を測ったものではない**（抄録の範囲）。
- 照合: references.md に無し。
- 同じ著者らの関連: Gunetti, D., Picardi, C. & Ruffo, G. — Dealing with Different Languages and Old Profiles in Keystroke Analysis of Free Text. AI*IA 2005, LNCS, pp. 347-358, DOI 10.1007/11558590_36（書誌のみ確認・抄録は閉じていて未読）。題が「古い profile」を扱うので **自由文での template aging の最も古い先例の候補**。本文を取って、間隔と低下の数を確かめる価値が高い。

## 4. Ayotte, Banavar, Hou & Schuckers — Study of Intra- and Inter-user Variance in Password Keystroke Dynamics（本文を読んだ）

- 書誌: Ayotte, B., Banavar, M. K., Hou, D. & Schuckers, S. — Study of Intra- and Inter-user Variance in Password Keystroke Dynamics. ICISSP 2021, pp. 467-474。DOI 10.5220/0010235504670474（SciTePress の本文ページで確認）。
- 設計: CMU の固定文データ（51 人・8 セッション・各 50 回・セッション間は少なくとも 1 日）。固定のパスワード 1 つ・31 特徴。
- 逐語:
  - "overall typing time for a provided password “.tie5Roanl” changes significantly over time, decreasing by almost 30%"
  - "Features typed frequently such as monographs and common digraphs are more invariant through time"
- 数: 総打鍵時間は 1 セッション目から 8 セッション目で 29.8% 短くなる。更新なしの EER はセッションとともに単調に上がる（値は図のみ）。
- Q3: 支持（日をまたぐ揺れの実測）。**ただし固定文・練習効果が混じる**。頻出の組は安定、稀な組ほど動く、という知見は「窓の要約値は稀な事象に依存しないので漂いにくい」と「休止の数など稀な事象は漂う」のどちらの仮説にも使える。
- 照合: references.md に無し。

## 5. Parkinson, Khan, Liu & Xu — Template Ageing and Longitudinal Verification in Fixed-Text Keystroke Dynamics（本文を読んだ・近刊の preprint）

- 書誌: arXiv:2609.29851v1 [cs.CR], 24 Sep 2026（IEEE TBIOM のテンプレートで書かれた preprint。査読を通ったかは未確認）。DOI 10.48550/arXiv.2609.29851（PDF の metadata）。
- 設計: 40 個の固定パスワードを週 1 回・各 4 回・連続 8 週。約 85 人（5 分割・1 分割あたり約 17 人）。M1 尺度つき Manhattan・M2 勾配ブースティング・M3 TypeNet 型・M4 TypeFormer 型。登録と照合の間隔 Δ = 0〜7 週を同じ検定の設計で動かす。
- 逐語: "The verification error increases monotonically with Δ for every mechanism, from an EER of 14.6–27.2% at Δ=0 to 25.5–37.1% at Δ=7" / "the choice of mechanism matters more than its rate of ageing" / "this result should be read as evidence that measurable drift begins early and grows monotonically from the first weeks, not as a claim about years of continued use"
- Q3: 支持（登録と照合の間隔 Δ を変えた**間を空けた評価**の最も整った近い先例。Δ ごとの低下を 1 週あたり 1.7 ポイントと報告）。**ただし固定文・短い入力・verification・EER**であり、自由作文の長い窓の要約の識別ではない。「漂い」と「安定した個人差」の分離は試みていない（検証の誤りが Δ とともに増える、までで、安定成分の抽出はない）。この論文は、先行を「更新して抑える側」と「素の低下を測る側」に分けており（関連研究の節）、素の低下の測定が少ないという主張も使える。
- 照合: references.md に無し。

## 6. Çeker & Upadhyaya — User Authentication with Keystroke Dynamics in Long-Text Data（本文の冒頭を読んだ）

- 書誌: Çeker, H. & Upadhyaya, S. — User Authentication with Keystroke Dynamics in Long-Text Data. Univ. at Buffalo 技術報告 2016-07（cse.buffalo.edu/tech-reports/2016-07.pdf。IEEE BTAS 2016 の同名論文と同系統とみられるが、**同一かは未確認**）。
- 逐語: "we can authenticate legitimate users and reject impostors with negligible error (close to 0% equal error rate) by setting a one-class SVM for each user using a dataset of 34 users in a controlled environment"
- 設計: 34 人。書き写しと自由回答。**長い文を処理する特徴抽出**（アライメントの問題を避ける）で本人ごとの one-class SVM。
- Q1: 近いが違う（長い入力を窓や要約でまとめる系。書き手ごとのモデル。ただし特徴は digraph の統計）。Q3: 同じセッション内の評価で、日をまたぐ評価は読んだ範囲に無い。
- 照合: references.md に無し。

## 7. Sharma, Jureček & Stamp — Keystroke Dynamics for User Identification（抄録のみ）と Chang, Li & Stamp — Machine Learning-Based Analysis of Free-Text Keystroke Dynamics（抄録のみ）

- 書誌: Sharma, A., Jureček, M. & Stamp, M. — Keystroke Dynamics for User Identification. arXiv:2307.05529, 2023-07-07（cs.LG・cs.CR）。DOI 10.48550/arXiv.2307.05529（arXiv ページで確認）。
- 書誌: Chang, H.-C., Li, J. & Stamp, M. — Machine Learning-Based Analysis of Free-Text Keystroke Dynamics. arXiv:2107.07409, 2021-07-01（cs.LG）。DOI 10.48550/arXiv.2107.07409。
- Sharma ら: 自由文・148 人・多クラス識別。**4 つのタイミング特徴を、連続する 2 打鍵ごとに（頻出 42 キーに限って）4 チャネルの遷移行列に並べ**、CNN で 0.78・Random Forest で 0.93。逐語は "the more challenging multiclass user identification problem, based on free-text data" と、Random Forest で accuracy 0.93。
- Chang ら: Buffalo の自由文データ（157 人・3 セッション・セッション間 28 日と本文検索結果は述べるが、一次の本文では未確認）で CNN + GRU。
- Q1: 近いが違う（遷移の「行列」を特徴にするが、**キーの対の遷移**であって時間窓の状態の遷移ではない。量子化もしない）。Q3: Buffalo のデータはセッション間 28 日と報告される点で「間を空けた」データとして使える先例候補だが、**2 本とも訓練/テストの分け方を本文で確かめていない**ので、日をまたぐ低下を測ったかは未確認。
- 照合: references.md に無し。TypeNet は [V250]（既）。自由文の RNN の識別 Kim & Kang は [P510]（既）。

## 8. Giot, Dorizzi & Rosenberger — Analysis of template update strategies for keystroke dynamics（書誌のみ）

- 書誌: IEEE CIBIM 2011, pp. 21-28。DOI 10.1109/CIBIM.2011.5949216（Crossref で確認。抄録・本文は未読）。GREYC のデータ（複数セッション・固定文）で template 更新を比べた研究と、Parkinson らの関連研究の節が書いている（"Giot et al. [6] apply a semi-supervised update with multi-session evaluation"）。
- Q3: 近いが違う（更新して低下を抑える側であって、素の低下を測る側ではない）。
- 補足: Giot, El-Abed & Rosenberger の GREYC / Web-based benchmark（arXiv:1207.0784, IIHMSP 2012）は、複数セッションの固定文データの先例だが、抄録に低下の数は無い。Pisani ら（Computers & Security 60:134-153, 2016, DOI 10.1016/j.cose.2016.04.004）は更新の系（書誌のみ）。
- 照合: いずれも references.md に無し。

## 参考: 反証側（粗い・長い窓では識別できない）の検索結果

- 該当する研究は **0 件**。見つかったのは逆向き（粗くしても識別は保たれる）の Dehling ら（本資料の 1）。
- 唯一の「悪い側」は、登録と照合で粗さが食い違うと壊れる（Dehling ら）と、間を空けると単調に悪くなる（Parkinson ら・Ayotte ら）。**識別が偶然まで落ちるという報告は見つからなかった。**

## 検索式と 0 件の記録

1. "free-text keystroke dynamics identification aggregated statistical features long window"（WebSearch）→ Çeker、Chang、Ayotte 2019/2020、Gunetti 系
2. "keystroke dynamics template aging longitudinal session variability authentication degradation over weeks"（WebSearch）→ Parkinson、Ayotte 2021、Dorizzi らの更新の評価
3. "keystroke dynamics discretized timing quantized features Markov chain user identification"（WebSearch）→ **離散化・量子化・マルコフ連鎖で識別した研究は 0 件**。出たのは特許（HMM・連続値）、Sharma ら（遷移行列を CNN）。
4. "keystroke dynamics reduced timing resolution coarse temporal features effect on identification accuracy"（WebSearch）→ Dehling ら、Killourhy & Maxion（clock resolution）
5. "typing behavior profiles histogram of inter-key intervals free text writer identification unseen sessions months later keystroke logs"（WebSearch）→ **ヒストグラムの profile を数か月先のセッションで試した研究は 0 件**（Buffalo の 28 日間隔が最長）
6. 書誌の裏取り: Crossref（Gunetti & Picardi・Killourhy & Maxion・Giot ら・Pisani ら）、Semantic Scholar（抄録は出版社が閉じていて取れず）
- 未実施: OpenAlex・arXiv の直接検索、Google Scholar、Monaco & Tappert の長期の自由文の研究（references.md に POHMM [V506] と SoK [V194] が既にある）、Killourhy & Maxion clock resolution と Gunetti らの "Old Profiles" の本文。時間切れで未読。

## 位置づけへの効き方（メインの判断用の要点）

- 「粗い要約の記号列・遷移の表で書き手を見分けた」ことが新規だと主張する余地は残る（0 件）。ただし「粗くしても識別が残る」（Dehling）・「順位だけで識別できる」（R 距離）が先行なので、**粗い特徴で識別が成り立つこと自体を新規とは言えない**。新規は、粗い記号列の遷移の表を 30 秒窓の重なりのまま使い、**入れ替えで検定し、A と B の間を空けて漂いと分ける**ところにある。
- Q3 の先例は固定文・verification・EER・短い入力に偏る。**自由作文・長い窓・書き手ごとの遷移表・間を空けた評価**の組は先例が無い、と言える範囲は、本資料の検索の範囲に限る。
- 入れ替え検定そのものの先例は本 angle の範囲外（他の angle に任せる）。
