# T4 の文献の探索の記録（2026-11-11・サブエージェントの報告の写し・未検証）

> サブエージェント（opus・WebSearch・OpenAlex・arXiv・ACL・medRxiv・EDM・JSiSE）の報告を写したもの。カード化と references.md への登録は、メインが一次で確かめてから literature-card と citation-ssot で行う。ここは根拠に使わない。

## 結論（報告の要旨）
- 打鍵の記号列に個人ごとの系列モデルを当て、本人の 1 次マルコフ連鎖と同じ構造の共通に比べ、構造と縮みを他の人で選ぶ、という同じ比べは見つからなかった。
- いちばん近い: Uto ら 2020（IJAIED・doi 10.1007/s40593-019-00189-9・学習者と時間に依存する HMM を打鍵ログの 30 秒窓の特徴量に当てた・未来のセッションでの予測評価と本人の連鎖との比べは無い。2020 年版は抄録だけ・本文は Chrome が要る。前身の JSiSE 2018 は本文で確かめた）。
- 「比べの相手（本人の平均など）しだいで個人化の利得の見え方が変わる」という論点そのものには先例: DeMasi ら 2017（PLoS ONE・doi 10.1371/journal.pone.0184604・抄録だけ）、LiKamWa ら 2013（MoodScope・本文・本人の平均の strawman 73% が全員モデル 66% を上回る・10 日で hybrid 優位・30 日を過ぎて個人モデル優位）、Naegelin ら 2025（medRxiv・doi 10.1101/2025.08.02.25332538・打鍵とマウスと心拍でストレス・本文・個人モデルの平均 MAE が本人の平均のダミーより高い）、Hammelrath ら 2026（抄録だけ）。
- 個人モデルが常に勝つわけではない例: Leenaerts ら 2024（Psychol Med・doi 10.1017/s0033291724000862・抄録だけ・pooled が person-specific を上回る）。
- そのほか: Huang ら 2018（dpMood・本文）・Kołakowska 2015（抄録）・Wetherell ら 2023（抄録）・Ghosh ら 2019（抄録）・Lee と Brunskill 2012（EDM・BKT の個人化・本文の一部）・Welch ら 2022（ACL・本文）・Tasnim ら 2026（抄録）・Monaco と Tappert 2018（打鍵の HMM・認証・本文の一部）・Soyster ら 2021（抄録）。

## 新規性の文の直し案（報告の案）
比べの相手の効き目は気分とストレスの推定で報告がある（LiKamWa 2013・DeMasi 2017・Naegelin 2025）こと、打鍵ログに学習者依存の HMM が当てられている（Uto 2020）ことを先に書き、新しいのは「打鍵の系列モデルへの本人の連鎖と他人で選んだ共通への比べの適用」と「比べるモデルの構造を改善すると見える上積みが縮むことの報告」に絞る。cold-start は MoodScope と Leenaerts を並べ「切り替えの時期は分野とラベルの量しだい」。

## 残り（一次で確かめること）
- Uto 2020 の本文（Chrome）・DeMasi 2017 の本文（PLoS ONE は OA のはず）・Naegelin 2025 の該当の文・LiKamWa 2013 の数値。
- 既に references.md にあるかの照らし（重複防止キー DOI）。
