# verdict（stage: manuscript・原稿の全体・round 4・2026-11-17）

対象: commit bf0d2450。査読者役 3 人・編集者 E・監査役 1 人（paper-reviewer・Opus）。Codex を加えた（直列・既知の未決 13 件の一覧を添えた・§2 の別枠）。

## 1. 編集者の判定: major revision

- R1 minor・R2 major・R3 major・E「直してから回す」。E が「直してから回す」なので major 以上（Skill の 4b）。
- 新しい計算を要する指摘は R1 m2（探索の変種の陰性対照）と R3 m1（学習用の prompt で λ を選ぶ）だけで、どちらも受理の条件ではない（R1 自身が明記）。他はすべて本文の言い換え・限定・付録への移動・まとめで直せる。
- 有効な査読 4/4（R1・R2・R3 が 2〜3 本、E が一次＋1 本の文献から基準を逐語で抜き出した）。
- 判定の推移: round 1 major → round 2 major → round 3 major → round 4 major。round 4 の指摘の中心は、round 3 の後に入れた探索 6・7 の書き方（C2 の要約）から出ている。

## 2. 一致（分母 = 有効な査読 4。監査・Codex は別に書く）

| 指摘 | R1 | R2 | R3 | E | 監査 | 裏取り |
|---|---|---|---|---|---|---|
| A C2 の要約の「within four times chance」が登録に無い事後の切りで、登録した二次の解析（λ = 4・N = 1,000）で R4(4) が 4.5%（45 倍）になっていることを抄録・序論・§8 冒頭・結論が書かず、崩したのが探索だけに読める | major ×2（M1・M2） | major（1） | major（M1） | major（M1） | 2-A・3-A | 真。「four times」は abstract.tex:14・17、introduction.tex:49、results.tex:154、discussion.tex:11、conclusion.tex:8。preregistration.en.md に該当の語なし、protocol.tex:13「No pass or fail criterion is set」。λ = 4 は登録の Secondary（preregistration.en.md:203）で results.tex:69 に 4.5%。main-1000.tex の R4(4) は 0.35 [0.07, 0.73]（上端 7.3 倍） |
| A′ 全員（4,992 人）では R4(4) が 0.65% [0.47, 0.87]（6.5 倍）で、本文と付録 E の「one changes」がそれに触れない | — | major（1） | — | — | — | 真（all-writers.tex:12・appendix-results.tex の当該の文） |
| B 抄録 348 語・未定義の語（segment values・main penalty）・登録と探索の 2 系統が 1 段に | m4 | minor（7） | （d）・nit n2 | major（M3） | — | 真 |
| C 但し書き・限定の繰り返し（探索の文で増えた。§8 冒頭と結論がほぼ同文） | — | minor（6） | （d） | major（M4） | — | 真（位置は review-E.md・review-R2.md） |
| D 探索は R3-u を強めておらず、強めた後の支配・前線（R7(0.25) が R3-u を支配・「40% 未満」）が非対称 | major（M3） | major（2）・minor（8） | — | — | 2-C | 真（appendix-exploratory.tex:69・results.tex:145・discussion.tex:67–69・explore-strongest.tex の R7(0.25) 62.3%） |
| E 探索の結果が C2 の段落・問い 2 の答えに入り、「問いに使わない」の宣言（protocol.tex:161）と食い違う | — | — | minor（m6） | （M1） | 2-B | 真 |
| F §7.2 の段落が過積載（主・λ = 4・窓・探索） | minor（m4） | — | — | minor（m1） | — | 真（results.tex:67–79） |
| G related.tex:46–47 の重複 | nit | minor（6） | nit | nit | 3-E | 真 |
| H 探索の N の範囲が抜ける（結論・§8 冒頭・§7.2 の λ = 4 の文。N = 10 では探索でも R4(8) 30.3%、R4(4) は 78.1%） | minor（m1） | — | — | — | 2-D | 真（explore-strongest.tex） |

1 人だけ（＋監査）・すべて真（偽陽性なし）:
- E: M2「In that release」（discussion.tex:12・conclusion.tex:8）は試していない実際の公開への断定に読める（監査は round 3 の一般化の項として解消と判定。評価は KLiCKe に同じマスクを当てたもの）／m2 本文から移せる方法の細部（attackers.tex:22–27・97–101、data.tex:91–100、protocol.tex:83–88・102–106・137–141、threat-model.tex:99–110）／m3 公開する側の行動につながる 1 文が無い／m4 序論が問い 4（ENJA）の答えを示さない／nit 抄録の「computing no measure」。
- R1: m2 探索の変種に陰性対照が無い（新しい計算）／m3 余裕の大きい照合は当たる（R7(0.25) の上位 10% で 57.2%・explore-margin.tex:28）が持ち帰りに無い・Narayanan の eccentricity との関係／n2 表 2 の R3-t の行（data.tex:81）。
- R2: 3 効用の軸（中央値）が得点との関係の変化を隠す（utility-score.tex の平均ポーズ −0.11 → −0.36〔R7(0.25)〕→ −0.50）／4 得点の帯の偏り（explore-band.tex）が持ち帰りに無い／5 SDC との対応がリスクの測り方（外部ファイルとの record linkage）に結び付かない／10 ai-use.tex:10 が付録の label（appendix-checks.tex:8）を指す（E も同じ）。
- R3: M2 名指しした公開の側（主催者・Kaggle）への通知が倫理の節に無い（ethics.tex に通知の文なし。判断 91 で「知らせない・理由の文は足さない」と決めた事項）／m1 探索の λ を評価の記録で選び格子の端／m2 登録した Inputlog の照合を行えなかったことが逸脱の「4 件」に数えられていない（protocol.tex:102–104・173、preregistration.en.md:299）／m3 害 (a) の名の付け替え（threat-model.tex:144・152–153）／m4「below 0.5」の根拠が付録だけ（results.tex:155–156）／m5 倫理の「before acquiring」は返事を待ったように読める（登録は "acquired without waiting for the reply"・preregistration.en.md:304。問い合わせ 14:41 UTC・取得 19:29 UTC・返事は 2026-10-13〔判断 54〕）／m7 図 1 の見出しの "near chance" が未定義。
- 監査: 1-A 抄録に「両方を満たす形は無かった」が逐語で無い／1-B 抄録の ENJA に A0（11.9%）が無い／3-B 序論「lower matching came with fewer process measures」に反例（R7(0.25) と R3-u・R3-t）／3-C §7.2 の N = 10 の文と付録 E の全員（500 人と本文冒頭で覆われる）／3-D KeyTAR の書き手ごとの公開の例外が逸脱の一覧に無い。

### Codex（別枠・major・台帳 281,401 → 335,512）
- Claude の査読者の一致と重なる: 1（主罰則の前線が登録分析全体の前線に見える = A・D）・2（「4 倍以内」は点推定の分類・R4(4) の上端 7.3 倍 = A）・4（「In that release」の断定 = E の M2）。
- Codex だけ（すべて真）: 3 探索の選び方の単位（λ・攻撃者・塊の位置を抽出ごと・ログごとのどちらで選ぶか、区間が何を表すか）が本文から読めない（results.tex:75–79。付録 D には「selected again in every resample」がある）／5 protocol.tex:69–70「the coarsest rounding, $w = 1{,}000$\,ms, stands in for it」は時刻の削除の代わりにならない／6 ethics.tex:83–84「These values can be recomputed by anyone … so they add no information」は言い過ぎ。
- 既知の未決の一覧と重なる指摘は無かった。

## 3. 裏取り

- 接地の引用: 各役 1 件以上を本文で確かめた（空白を正規化）。narayanan "tolerate some mistakes in the adversary’s background knowledge"（曲がった引用符）・stadler "under any potential privacy adversary"・rocher "can be accurately estimated, and is often high"・borgman "depending on the time, purpose, or entity requesting access"・hanisch "knows the anonymization technique and its parameters"・arp "Test snooping occurs when the test set is used for experiments before the final evaluation"・kohno "what rights different stakeholders have"・mensh "each subject should be covered in only one place"。捏造なし。
- 原稿側: 上の表と一覧の位置をすべて grep で開いて確かめた（four times の 6 か所・protocol.tex:13・preregistration.en.md:203・299・304・results.tex:69・128・143–145・all-writers.tex:12・main-1000.tex:12–13・explore-strongest.tex・explore-margin.tex:20・28・utility-score.tex の平均ポーズ・appendix-exploratory.tex:69・ethics.tex:3–8・80・ai-use.tex:10・appendix-checks.tex:8・44–49・related.tex:46–47・discussion.tex:12・conclusion.tex:8）。
- 応答に出た一覧の外のファイル（R2: outline.md・R3: make_tables.py）は grep の出力に偶然現れたもので、根拠に使われていない。

## 4. 直す順（案）

本文の余白は約 0.3 頁。まず移して・まとめて空け、空いた分で足す。

移す・まとめる・消す（紙面を空ける）
1. 但し書きの繰り返し（C）を §3.5 と §6 の 1 か所に。§8 冒頭は結論と重ならない 2 文に。related.tex の重複（G）を消す。
2. §7.2 を分ける（F）: 窓の値を §7.4 へ、λ = 4 の二次と探索を段落の末に 1 段落で。
3. 本文から付録へ（E m2）: attackers.tex の Control・Meta の扱いと A1′ の再生の規則・data.tex のドラッグの長さ・protocol.tex の産出速度の分母と開いた世界の面積の集め方。threat-model.tex:99–110 は 2 文に。
4. 抄録を書き直す（B）: 250〜280 語。未定義の語を外し、登録と探索を 1 文ずつ。ENJA に A0 を添える。

書き直す（設計の判断）
5. C2 の要約（A・A′・E・H）: 「within four times chance」をやめ値で書く。主の解析（全文・N = 1,000・λ = 8）と、登録の二次（λ = 4 で R4(4) 4.5%）と、探索を書き分ける。登録のどの罰でも A0 を超えなかった粗い形は R4(8) だけ。全員では R4(4) 0.65% を §7.2 に 1 句、付録 E の「one changes」を直す。探索の文は C2 の段落の外へ。探索の結果に N = 1,000 を付ける。
6. 支配と前線（D）: §7.3 の支配の文に「主の解析で」、R3-u は探索で強めていないことを §7.2 と §8.3 に 1 句。図 1 の見出しを値で（R3 m7）。
7. 倫理の通知（R3 M2）: 研究者に問う。

小さな直し（判断不要）
8. 「In that release」を「同じマスクを KLiCKe に当てると」に限る（E M2・Codex 4）。
9. 探索の選び方の単位を本文に 1 句（Codex 3）・λ は評価の記録で選び格子の端（R3 m1）を 1 句。
10. 「stands in for it」を消す（Codex 5）・「so they add no information」を限る（Codex 6）。
11. 登録した Inputlog の照合を行えなかったことを、逸脱 4 件と並べて書く（R3 m2）・KeyTAR の書き手ごとの公開の例外を逸脱の一覧から参照（監査 3-D）。
12. 害 (a) の名の付け替え（R3 m3）・「below 0.5」の範囲を §7.3 に 1 句（R3 m4）・倫理の問い合わせと取得と返事の順（R3 m5）。
13. 序論に問い 4 の答えを 1 文（E m4）・「lower matching came with fewer process measures」を直す（監査 3-B）・ai-use.tex の参照（R2 10）・表 2 の R3-t の行（R1 n2）・抄録の「computing no measure」。

持ち帰りに足す（研究者に問う）
14. 余裕の大きい照合は当たる（R1 m3・R7(0.25) の上位 10% で 57.2%）・効用の軸に得点との関係の変化を 1 句（R2 3・平均ポーズ −0.11 → −0.36）・得点の帯の偏り（R2 4）・SDC のリスクの測り方との対応 1 文（R2 5）・公開する側の行動につながる 1 文（E m3）。

任意（新しい計算）
15. 探索の変種の陰性対照（R1 m2）・学習用の prompt で λ を選ぶ（R3 m1）。G-GEAR は 11 月ふさがり。

## 4b. 編集者 E の判定: 直してから回す

C2 の要約が定義の無い「4 倍」に依り探索がそれを打ち消す・抄録が伸びた・試していない実際の公開への断定。どれも書き直しと移動で直せる。

## 4c. 本文の分量

本文 11,009 語（texcount を本文の 9 節に当てた和・commit bf0d2450）。前の round の版（commit c3f3f5b5）は同じ数え方で 11,086 語（−77）。抄録 348 語（前の round 242 語・+106）。本文は 12 頁目の右段で終わり、余白は約 0.3 頁。

## 5. 逸脱・注入の疑い

- 投稿規程と CfP を 2026-11-17 に curl で取り直し、判定に使う文を原文で照合した（照合済み）。同時に、PoPETs 2027 は査読中のプレプリントの公開を "While not expressly forbidden, we discourage authors from publicly posting pre-prints of their submissions while under review" としていることを確かめた（判断 88 の「確かめていないこと」。研究者に伝える）。
- 保存の形: 5 本の応答は、tmp/*.raw.md に写すときにメインが言い回しを縮めた（指摘・位置・逐語・解消の条件・自信は残した）。保存の検査（secrets-filter rc=0・応答の中の絶対パス 0）は 5 本とも通った。
- 注入の疑い: 5 本とも「なし」。
- 失敗した役: なし（5 本とも初回で返った）。

## 6. 研究者に問うたこと

- C2 の要約の直し方（A・A′）／倫理の通知の文（R3 M2）／新しい計算（R1 m2・R3 m1）／持ち帰りに足す 1 文（R1 m3・R2 3・R2 4・R2 5・E m3）

## 7. 研究者の採否（2026-11-17・判断 94）

- C2: 値で書き、主の解析・登録の二次（λ = 4）・探索の 3 段を分ける（推奨）。
- 倫理の通知: 判断 91 のまま書かない（推奨は「事実と理由を 1 文」だった）。
- 新しい計算: 「時間による。数時間かかるなら限界にしよう」。見積もり（陰性対照は分析 7 の約 1/16 で約 40 コア時間・打鍵のデータとキャッシュは Mac に無い・台本と検査に半日）で数時間を超えるので、計算せず限界として書く。
- 持ち帰りに足す: 余裕の大きい照合は当たる・得点との関係の変化（推奨の 2 つ）。得点の帯と SDC のリスクの測り方・公開する側の行動の 1 文は足さない。
- 小さな直し（§4 の 8〜13）と、移す・まとめる（§4 の 1〜4）は一括で入れる。
