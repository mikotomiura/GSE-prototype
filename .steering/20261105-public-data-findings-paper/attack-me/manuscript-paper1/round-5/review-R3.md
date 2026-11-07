# review R3（manuscript round 5・事前登録・同等性の検定・機械学習の再現性・メインが要約して保存）

推奨: **minor**。接地: Lakens 2017（"equivalence bounds are prespecified"・"the abstract should also include the equivalence bounds"・"researchers often incorrectly conclude an effect is absent based a nonsignificant result"・"Researchers should report effect size estimates in addition to hypothesis tests."・"we can conclude equivalence for a specific operationalization of a hypothesis"）・Kapoor & Narayanan 2023（"We define a research finding as reproducible if the code and data used to obtain the finding are available"・"researchers decide which features are suitable for a modeling task and justify their choice using domain expertise"・"[L3.2] Nonindependence between train and test samples."）から逐語。評価 a4・b3・c3・d3・e4・f4。主・感度 17 行・H2・H3・閾値の表・床の割合を confirm_holdout.json と照合して一致。

引き継ぎの判定: 1〜8 すべて解消。

指摘:
- [minor] 引用している版 0.2.0 に X18 の記録が無い（README の表に round4-checks が無い・conditions-summary.md:3 の順の説明が round 4 の節を数えない）。→ 新しい版を出して DOI を差し替え、README と要約を直す。自信 高。
- [minor] 要旨・序論・結論の学習器との差（0.05--0.08）に停滞の定義との結びつきを添えていない。→ 3 か所に句を足すか要旨から外す。向きの扱いの違いも序論か結論で一度。自信 中。
- [minor] 閾値の表の「no separation」が区間なしの点推定（confirm_holdout.json の threshold_table は点だけ）。対照の 9.6% は作りの上で約 10%。→ 差に書き手の再標本の区間を付ける（[E-H]）か、点の記述に弱め、対照の率が作りの上で約 10% と 1 句。自信 中。
- [minor] 登録の外の探索の回し直しの入口と照合が公開物の README に無い。→ 探索ごとの命令と出力の SHA-256、または Materials に「the explorations are released as scripts without a rerun check」。自信 中。
- [nit] supplement 441-442 の (Section~\ref{sec:res-bounds}) は sec:res-learners。自信 高。
- [nit] X18 の外れの基準が本文（2 つ）と補足・条件（3 つ）で違う。自信 高。

読めなかった範囲: 事前登録・陽性対照 v2・比べ・ctrl_lo・kapoor は該当の行だけ。references.bib・papers の README・逸脱・notes・探索の conditions と多くの JSON・文献の記録は開いていない。注入の疑い: なし。
