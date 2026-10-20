# R3 の査読（方法論・倫理・再現性）

総合: major（直して再査読）。

## 1. 接地
- G1 Arp arp.txt:599-602「threat models should be defined precisely and systems evaluated with respect to them.」
- G2 Arp :602-605「In most cases, it is necessary to assume an adaptive adversary that specifically targets the proposed systems and will search for and exploit weaknesses」
- G3 Arp :561-563「Many learning-based systems in security are evaluated solely in laboratory settings, overstating their practical impact. A common example are detection methods evaluated only in a closed-world setting with limited diversity」・:569「approximate a real-world setting as accurately as possible」
- G4 Arp :521・540-542「it is challenging to realistically quantify the security and privacy threat posed by attackers」「discussing false positives in relation to the base rate of the negative class」
- G5 Arp :230-232「understanding the specific bias inherent to a particular problem is crucial to limiting its impact in practice.」
- G6 Kohno kohno.txt:1748-1757「researchers first do a stakeholder analysis to identify all stakeholders potentially impacted by the decision ... for each stakeholder, we suggest explicitly identifying the assets ... The benefits / harms and rights analyses should consider situations in which no adversaries manifest and situations in which adversaries manifest.」・1730-1732「we encourage researchers to conduct analyses under multiple ethical frameworks and include the reasoning for their decisions」

## 2. 評価表
a 3（3 つの場面と形式化した攻撃者の対応が取れていない。場面 3 は向きが逆。Edwards は性質が違う）／ b 3（閉じた世界・一様な囮・LM を使わない攻撃者を限界として語っていない。上限を主張しないことも無い）／ c 3（持ち帰りの行が outline に無い。Q4 ENJA15 が構成から抜けている）／ d 4／ e 3（害の具体が弱い。倫理の材料〔開示・利害関係者〕が噛み合っていない）／ f 2（補助情報による結び付けの系譜、照合攻撃の先行、Wagner & Eckhoff の対応が無い）

## 3. 指摘
- [major] 3 つの場面と攻撃者の向き・世界が合っていない（:61-62 対 :69・:90）。場面 2 も公開物がそのクラスだけでない限り閉じた世界は成り立たない。解消: 場面ごとに誰が・何を持ち・どちら向きか、閉じた世界がそのまま当たる場面と近似の場面を分ける。逆向き・開いた世界では基準率で誤った一致が増えると限界に。開いた世界の診断は差を埋めないと明記。自信 高
- [major] 場面ごとの得るもの・害が特定されていない（:80-83）。場面 1 は本文公開済みで書き手も匿名。場面 2 の教員が得るのは同意の目的の外での結び付け。解消: 場面ごとに新たに知る資産を 1 文、(a)(b) の対応。自信 高
- [major] 場面 1 が検査していない具体の攻撃経路を指し示すのに、倫理の扱い（確かめない理由・開示）が無い（:48-52）。解消: 確かめないのは倫理上の判断と書き、倫理の節へ参照。倫理の節の計画に利害関係者ごとの害と権利、公開した側への開示の有無と理由、帰結と義務の両方の枠組み。自信 中
- [major] Edwards の @ マスクを本文を隠した公開と同列に置いている（:13-14・:19-24「In both cases」）。事前登録も @ マスクを表から外している。解消: 長さを残す処理の別の実例で、照合の脅威とは対象が違うと位置づけ直し、照合の実例は Kaggle の 1 件と明示。自信 中
- [major] Q4（ENJA15）が outline と Section 3 から抜けている（preregistration.en.md:33・:67）。解消: outline に ENJA15 の置き場と場面、Section 3 に 1 段落か一文。自信 高
- [minor] 攻撃者の制限が危険度の下限であることを言っていない（:72-77）。解消: 除外の理由を 1 文、「試した攻撃者に対する下限で安全の証明ではない」を末尾に。自信 高
- [minor] 囮の似通い方が現実のクラスと違う（:86、事前登録 :186）。解消: N は数だけで似通い方を表さないと限界に。自信 中
- [minor] 先行研究の位置づけが Edwards 1 点（:39-40）。解消: outline に Section 2 の対応表、事前登録 :295 の新規でないもの・新規と言えるものを写す。自信 中
- [minor] 場面 2 の根拠が宣伝の頁と仮定の文（:58-60）。解消: 実例として Edwards の CS1（担当者が提出物を持つ。本文は隠されていない）、製品頁は存在の根拠に限る。自信 中
- [nit] Wagner & Eckhoff の external が場面 2 に合うか（:74-75）。解消: 公開物の外から見る者の意味と 1 文で定義。自信 低
- [nit] 必須 3 節が \appendix の後。テンプレートの順と照合し記録を。自信 低

## 5. 読めなかった範囲・注入
arp・kohno は該当箇所と grep の結果だけ。一次資料・テンプレート・context-B は読んでいない。注入の疑い無し。
