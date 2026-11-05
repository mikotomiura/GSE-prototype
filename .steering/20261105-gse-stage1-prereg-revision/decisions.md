# decisions

## 判断 1: 枝を S-DQ の枝の上に切る

- 決定: 枝 `docs/gse-stage1-prereg-revision` を `docs/gse-daily-item-scale-literature`（e1a6c633）の上に切る。worktree は同じ `/Users/johnd/GSE-prototype-daily-scale`。
- 理由: 日の終わりの問いの項目（S1-F7）で S-DQ のカードと [V386]〜[V412] を引く。S-DQ は未 push・未マージなので、origin/main から切ると引けない。PR は S-DQ を先に出す。

## 判断 2: ADR-048 の「handmark-why-interesting 判断 14・15」の出典の書き間違いを記録する

- 事実: 枝 docs/tangibility-design の `.steering/20261017-handmark-why-interesting/decisions.md` は判断 12 までで、同期の感覚と速さの区別の話は無い。中身が合うのは `.steering/20261016-handmark-expression-design/decisions.md` の判断 13 (3)・14・15（同期の評定と、速さと止まりを正答で測る課題を同じ刺激で並べる・対照の条件・課題の順序・偶然水準）。棚卸し（`.steering/20261105-gse-overview-and-concept/expression-inventory.md` 未決 5）も同じ書き方。
- 決定: 事前登録（S1-F9）には正しい出典を書く。ADR-048 の本文は書き換えない規約なので触らず、ここに記録する。手跡を main に入れるタスク（引き継ぎ 2-4）で、ADR-048 を読む人のために注を足すかを決める。
