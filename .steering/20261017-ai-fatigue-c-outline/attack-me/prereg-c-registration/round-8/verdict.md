# verdict（prereg・round 8・2026-10-20）

対象物: round 7 の直しの差分（TRACE `059664b` → `05e31ac`・登録版 0.20・外枠 11 版・草稿・添付 6 の call.md と README・コードブック）。

## 1. 編集者の判定

**minor revision（直してから凍結。再査読は要らない）**。有効な査読 3 本とも minor で、3 本とも「設計を変える必要は無く、数文の直しで閉じる」と見た。fatal は無い。

round 7 の指摘は、R1 が 11 件中 9 件、R2 が 15 件中 14 件、R3 が 10 件中 9 件消えた。消えなかったものは次の 4 つ。

- C2b の stem の対象（R1 の N4）: 一部。印は入ったが、対象の分布が印で分かれていない。
- 一致の低い符号の印（R1 の N7）: 一部。単位と最小件数が決まっていない。
- 草稿の \tbd（R3 の F・監査の 3-h）: 一部。片方の群だけの分岐が無い。
- C7 の行の「not verifiable」（R2 の 15）: 消えていない。同じ場合を 2 度書いている。

査読者が major とした指摘が 2 つある。どちらも 1 人だけの指摘で、表の殻か規則の 1 段落で閉じる。

- R1: C2b の対象の分布で、stem から取った対象と、項目が自分で名指す対象が混ざる。
- R2: 監査の推定が 2 つの群を混ぜている。

## 2. 裏取り

- 引用の箇所はすべて対象物にあった（Grep で確かめた）。
  - registration-en.md: 197・284（2 か所）・GSRR-11 の RQ4・GSRR-12・GSRR-16・GSRR-2 の表の「as reading aids only」・GSRR-33 の監査・確かめの標本・「Its records are never part of the main set or the late stratum」・GSRR-56 の対象の分布
  - main.tex:「the first author wrote the earlier narrative review」
  - tables.tex:「in place of the reconciled values」「reconciled values with the AI draft」（2 か所）
  - outline.md: 抄録の規則の段 4
  - call.md:「One line was changed after round 3」
  - codebook-c2b-en.md:「remains after the third pass」
- 接地は本文を Grep して、次の文がすべて在った。
  - R1: Lintner「only a few have been tested for content validity…」・Elson「preregistered with code rather than a narrative」
  - R2: Perrig「independently verifiable」「so readers and reviewers can judge their legitimacy」・Bach「generalization of findings may not be feasible」
  - R3: round 7 と同じ文（Garritty・Waffenschmidt・Khraisha・GSRR・Nuijten）。11.6% と 1.2% の検算も合っている。
- 偽陽性は無かった。
  - R1 の nit「the four C5 categories と not_verifiable」は事実。not_verifiable は他の符号と同じく分母の外の値で、4 つの区分の外にある。
- 逸脱:
  - R1 と R2 は manuscript/ を Grep し、一覧の外の abstract-mock.md の行を結果で目にした（根拠に使っていないと申告）。保存の検査では、応答に出た絶対パスは無かった。
  - R1 の接地の本文（Elson）は、抽出のときに語の途中で切れていた。
- 注入の疑い: なし。
- 保存の検査: 4 本とも secrets-filter.sh の終了コード 0。

## 3. 2 人以上が一致した指摘と対応の案（分母は有効な査読 3）

| ID | 指摘 | 誰 | 対応の案 |
|---|---|---|---|
| A | 締切を遅らせるときに上限が無い。著者 2 が返せない場合の打ち切りが無く、GSRR-9 の終わりの日とも結ばれていない | R1・R3 | 〔設計〕問 1 |
| B | 確かめの標本の記録の E5 に時間の窓が無い。締切の後に本体の RQ4 の数が増えうる。GSRR-33 の「never part of the main set or the late stratum」と GSRR-35 の「enters a count of the main set」が食い違う | R1・R2・R3（監査 1-5・2-1・3-3） | 〔設計〕問 2 |
| C | 2 人の一致が 80% 未満の印に、最小の件数と単位が無い（較正の側には「at least 5 comparisons」がある） | R1・R2・R3 | 印の横に n を必ず添え、比べた数が 5 未満なら印を付けずに「n < 5」と添える。行ごとの単位は道具の対応表（GSRR-64）で固定すると書く |
| D | 網の記録は、混ぜても中身（迷いうる記録）や冊の比率から推しうる。2 群を合わせて混ぜるので、群の割合からも透けうる | R1・R3（監査 1-3） | GSRR-65 に 1 文。群の割合は問 3 に関わるので、混ぜる記録を網の記録と同じ群の比で抜くかを、問 3 と一緒に決める |
| E | 草稿の \tbd に、片方の群だけ著者 2 が全部を判定する分岐が無い | R1・R3（監査 3-h） | 3 つ目の分岐を足す |
| F | C5_other_record の相手が候補の外のとき ID が無い | R1・R2 | 候補の外の相手は DOI か書誌を書く |
| G | 下書きを開く時の「for the records author 2 coded」が、GSRR-4 の表と main.tex で落ちている | R3（監査 3-8） | 2 か所に足す |

## 4. 1 人だけの指摘と監査役

- R1
  - M1〔設計〕C2b の対象の分布で、stem から取った対象と項目が名指す対象が混ざり、C1 の区別を C2b が黙って戻す → 問 4。
  - m1: 流用の条件を、項目の側の性質（対象を代名詞で名指すか省く項目では stem も同じ）で書く。
  - nit: コードブックの target_from_stem の unresolved を「話し合いの後に残った不一致」に（GSRR-48 に合わせる）。
- R2
  - major〔設計〕監査の推定が 2 群を混ぜる → 問 3。
  - 「reconciled」の残り（GSRR-43 の C7 の行「derived by script from the reconciled codes」、tables.tex の 3 か所）→ final values に揃える。
  - 中心の最終値の古い文（GSRR-33 冒頭・GSRR-12・GSRR-16）→ unresolved を足す（監査 1-2・3-1 と同じ）。
  - 網の出力が壊れた束の記録と混ぜ方の関係 → その経路で渡す記録も「網が渡す記録」に数えて混ぜる。
  - C7 の行の「not verifiable」の重複 → 後ろの文を消す。
  - 添付 7 の答えを 10-20 の規則で見直したか → 確かめて、改訂記録に 1 行。
  - RQ4 に新しい値が無い（監査 1-1 と同じ）→ RQ4 と外枠 R4 に足す。
- R3
  - 2: 別の識別子が出たときの処置と、識別子の出どころ → 識別子は Claude Code の記録（サブエージェントの記録の model の欄）から取ると書く。別の識別子が出た束は「書式が 2 回落ちた束」と同じ扱い（第一著者の除外を全部著者 2 に回す）、以後は後継の確かめの規則、と書く（判断 57 の向き）。道具は既に止まる。
  - 4b: 下書きが人の誤りを示しても値を変えない代価 → GSRR-65 に、食い違いの件数を報告すると 1 文。
  - 6: 正の一致が 0/0 のとき → 未定義と報告。
  - 7: call.md の round 3 の後の 1 行の変更 → GSRR-37 に 1 文。
- 監査役
  - 1-4: 草稿の限界に 0.20 の GSRR-65 の項が無い → 足す。
  - 2-2: 「as reading aids only」は言い過ぎ → 「before registration」だけにして、読む助けと準備の作業を分けて書く。
  - 3-2: 草稿の「the first author wrote the earlier narrative review」→ both authors に。
  - 3-5: 外枠と草稿の表 12 の列 → 草稿は注で代えると外枠に書く（外枠の列を残す）。
  - 3-6: 抄録の規則の段 2・段 4・締めの文の C5・C6 の件数 → 段 4 で件数を表 12 に回すことを、締めの文に揃えて書く。
  - 3-7: 草稿の C6c・C7 (ii) の文に「or unresolved」と「全体の数は出さない」。
  - 3-9: 「a batch cut short by 2026-12-31」→ 締切の日に合わせる（問 1 と一緒に）。
  - 独立の語の残り（GSRR-33 冒頭・198 行・main.tex 338 行・登録版 476 行）→ 段の内の言い方に揃える。
  - 外枠 Scope に監査の N 倍の推定を足す。

## 5. 直す順

1. 設計: 問 1〜4
2. 3 節の A〜G と、4 節の規則の穴（R3 の 2・R2 の網の出力が壊れた束・R2 の中心の値・RQ4）
3. 語と草稿・外枠（reconciled・C7 の重複・独立の語・草稿の限界と著者・抄録の規則）
4. 道具（問 2〜4 と C で変わるもの）。検査を足してから直す
5. 全文を "independent" "reconciled" "2026-12-31" "centre-A or centre-B" で Grep して揃える。検査を全部走らせ、/cross-review をかける

## 6. 研究者に問うこと

1. 締切を遅らせるときの上限（A）
2. 確かめの標本の記録の E5 の窓と、本体の数に入れるか（B）
3. 監査の 30 件を群で層に分けるか（R2）、混ぜる記録の群の比（D）
4. C2b の対象の分布を target_from_stem で分けるか（R1）
5. 残りの直す一覧を案どおり進めてよいか
