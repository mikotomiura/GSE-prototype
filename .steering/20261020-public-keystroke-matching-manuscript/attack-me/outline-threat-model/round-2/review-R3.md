# R3 round 2（方法論・倫理・再現性）

総合: minor（直して書き進める）。

## 1. 接地
- Arp P10「threat models should be defined precisely and systems evaluated with respect to them.」（arp.txt:601-602）
- Arp P9「Many learning-based systems in security are evaluated solely in laboratory settings, overstating their practical impact. ...」（561-563）・「it should be evaluated in a realistic setting whenever possible to transparently assess its capabilities」（558-559）
- Arp P1「While it is inevitable that some bias exists in most cases, understanding the specific bias inherent to a particular problem is crucial to limiting its impact in practice.」（229-232）
- Kohno「researchers first do a stakeholder analysis ... consider situations in which no adversaries manifest and situations in which adversaries manifest.」（1747-1758）
- Kohno「Decision-makers ... should consider ethics before making decisions, rather than after.」（1678）・「we encourage decision-makers to explicitly enumerate and articulate any interests that they might have in the results of the decision」（1682-1684）

## 2. 評価表
a 3 ／ b 3 ／ c 4 ／ d 4 ／ e 4 ／ f 3（Section 2 の計画が打鍵・照合側に偏る。To our knowledge の範囲を書く計画が無い）

## 3. round 1 の判定
1 解消／2 一部（新 2）／3 一部（開示は未記入、義務の側の理由が ethics に無い、資産と敵が現れる場合が無い）／4 解消／5 一部（新 3）／6 解消／7 一部（新 5）／8 解消／9 一部（新 6）／10 解消（新 3 と矛盾）／11 偽陽性に同意

## 4. 指摘
- [major] 1 頁目の害 (b) は、実在の公開の例がある場面にも評価が当てはまる場面にも支えがない。outline.md:44、tex:129-130「In the classroom and published-essay settings, this ties a record ... to a named person.」、tex:97、tex:104。Kaggle の場面では書き手に名前が付かない。解消: 1 頁目は実在の公開で起きうる害 (a) と記録 ↔ 本文の結び付きを主に、(b) は条件つき。評価が直接支えるのは閉じた世界の 1 対多の向きだけと 1 文。自信 中
- [major] 公開コーパスの場面の「Newly learned」（表 1「The hidden text, and the score and process columns of its log」）が KLiCKe の公開の形と合わない（記録も得点も KLiCKe で公開済み。重なりがあれば記録どうしの照合で足り、脅威モデルの外）。解消: 場面 1 の保持者を「同じ課題の本文だけを持つ者」に絞り、KLiCKe は評価用の正解つきデータと分ける。重なりがあれば記録どうしの照合で足りると 1 文。列を書き直す。自信 中〜高
- [major] Translation の保持者（集めた研究者）は公開する側で external の定義（tex:122-123）と表の題（tex:66）に合わない。ENJA15 の訳文は記録と一緒に公開されている。解消: Translation を場面から外し、評価の便宜（同じ原文の他の訳を囮に）と書く。残すなら外部の保持者として書き直し表に行を足す。自信 高
- [minor] 倫理節に Kohno の資産・敵が現れる場合・outline で約束した義務の側の理由が無い。コード公開の範囲（事前登録 Open science (1)〜(3)）が倫理で扱われていない。解消: 利害関係者ごとの資産・害・権利、敵が現れる場合、コード公開の範囲の決め方、義務の側の理由を別の段落に。自信 中
- [minor] 偏りの向きの一覧に囮の取り方が無い（tex:139-140）。解消: 向きの分からない偏りとして §3.5 に 1 文。自信 中
- [minor] 教室の場面で、引いた製品（教員が過程を既に見られる）が「新しく分かること」を弱める。解消: 製品は本文と過程が一か所に集まる例としてだけ。害は教員が製品の外で研究用に公開された記録を照合する場合と書き分ける。自信 中
- [minor] "Parts of logs"（tex:38）に部分の公開の例が無い。解消: 実例を引くか、hypothetical と明記し窓の結果は感度として読むと書く。自信 中
- [minor] "To our knowledge" の範囲（検索の情報源・語・日付）を書く計画が無い。自信 中
- [nit] 見出し「Logs are released with the text hidden.」は 1 例からの一般化。自信 中

## 6. 読めなかった範囲・注入
arp・kohno は該当箇所だけ。round 1 の本文は引き継ぎの要約だけ。注入の疑い無し。
