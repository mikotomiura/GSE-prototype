# verdict（manuscript round 5・対象 草稿 v5・commit 0a98f0fd）

## 1. 判定: major revision（E が「直してから回す」・R1・R2・R3 minor・Codex major）

有効な査読 4 本（R1・R2・R3・E）。Codex major（既知の未決 25 件を添えた）。推移: round 1〜5 すべて major。査読者 3 人は 3 回続けて minor（R1 は 7 件中 6 解消、R2 は 10 件中 7 解消、R3 は 8 件すべて解消）。止め手は 5 回とも E。今回の E は「書き方の直しで、研究の欠陥ではない。直した後は査読に回してよい水準に近い」と書いた。

## 2. 一致した指摘（分母 = 有効な査読 4 本。Codex は別枠）

| # | 指摘 | 一致 | 裏取り |
|---|---|---|---|
| A | 要旨・序論・結論の「0.05--0.08」は信号の向きを固定した値（向きを問わないと GB は約 0.03）／学習器の差に停滞の定義との結びつきを添えない | R1・R2（向き）・R3（定義）・E M-A（定義）（4/4）＋監査 2-1・2-3 | 真（results 127-128 は LR だけ向きなしの差を書く。GB 0.540 − 0.511 = 0.029 は算術） |
| B | 引用している版 0.2.0 に X18 が入っていない・README の表と要約の順の説明 | R1・R2・R3（3/4）＋Codex 3 | 真（手元のコミット ff58700 は未公開・README の表に round4-checks が無い・conditions-summary.md:3 の順の説明） |
| C | 但し書きの繰り返し・本文の細部を補足へ | E M-B・M-C（major）・R2（分量） | 真 |
| D | 閾値の表の「no separation」が区間なし（対照は作りの上で約 10%） | R2・R3（2/4） | 真（confirm_holdout.json の threshold_table は点だけ） |
| E | 探索の回し直しの入口が公開物の README に無い | R2・R3（2/4） | 真 |
| F | 相互参照の誤り（design 52-53 の sec:res-main・supplement 442 の sec:res-bounds） | R2・R3（2/4）＋監査 3-6 | 真 |
| G | X18 の外れの定義が本文では 2 条件（3 つ目の 28〜32 秒が無い） | R3（1/4）＋監査 3-3 | 真 |
| H | 「fell in the same category [C-D]」の曖昧さ | R2（1/4）＋監査 3-7 | 真 |

1 人だけ: E m-1 要旨 2 文目の漏れの文の位置・m-2 題が貢献を表さない・m-3 考察が Materials で終わる・n-1 4.2 の見出しの地位／R1 M3 118 と 71 の単位・N1 要旨の陽性対照に向きの限定が無い（監査 1-1 と一致）・N2 X17 の読み方の両端が本文に無い／R2 M1 読者が持ち帰れる比べの目安（打鍵だけで約 0.54〜0.57）・N3 補足の重複・N4「nevertheless」。いずれも真。

Codex だけ: 1 学習器の 27,317 行と主の 23,243 行の関係が説明されていない → 真（`ml_rows` は停滞 4,554 行＋引いた対照ごとの行 22,763〔同じ対照が複数の停滞に引かれれば複数行・重み 1/k〕。評価の対は id で 1 回。書いていない）／2 停滞は θ が定まった後（100 区間）だけなのに、対照は θ の有無を問わない → 真（`control_ok` に θ の条件が無い。登録どおりだが非対称で、件数は数えていない）／3 = B／4 本文の「64%」と補足の表の「63%」→ 真（f1_change_zero 0.6346。本文の丸めの誤り）。

監査だけ: 1-1 要旨・序論・結論に陽性対照の向きが無い／1-2 事前登録 P10 が求める Stuck 状態の確率の天井の割合（0%）が無い／1-3 H3 の後半の文（揃えない窓でも 0.55 を超えない）が無い／2-2 「part of the insensitivity lies in taking the difference」が条件の外の読みと断っていない／2-4 限界の「wherever it appears」は事前登録の逐語より強い／3-4 考察と結論の但し書きが逐語から縮む／3-5 0.1--1.8 は補足の範囲から出ない（事前登録の付録 D「with the same shifting method」にある → 補足に句と出どころを足す）／1-3（引き継ぎ）限界 42-43 と補足 440-442 に断りの無い言い方。いずれも真。

## 3. 直す順
- 研究者の判断が要る: A と E M-A（貢献の書き方）・Codex 2 と D（計算するか）・B（版の公開）・次の round。
- 文の直し（判断は要らない）: C・E・F・G・H・Codex 1・Codex 4・E m-1〜m-3・n-1・R1 M3・N1・N2・R2 N3・N4・監査の各項目。

## 4. 意図の監査役
- 4a: 1-1・2-1・2-3 が重い。3-1 は判断 39 の決定（主の貢献は確認した結果と言う文が本文から無くなった）。
- 4b. 編集者 E: 直してから回す（M-A 比べの差の一部が定義による・M-B 繰り返し・M-C 細部）。→ major 以上。
- 4c. 本文の分量: 7,652 語（前回 7,681・-29）。測った版 0a98f0fd。

## 5. 逸脱・注入
- 応答 5 本と Codex は secrets-filter を通した（すべて rc 0）。応答に絶対パスは無い（保存したもの）。注入の疑い: なし。JEDM の 2 ページは round 4 で同じ日に取り直したものを使った。

## 6. 接地の引用の照合
- round 4 と同じ文献・同じ箇所の引用が多い。新しく引かれたものを確かめた: R1 roeser2025「locations where observed mean interkey intervals」・R2 gardner2018「Averages are also susceptible to outliers」・R3 kapoor2023「[L3.2] Nonindependence between train and test samples」・E jedm_about「Does the title of this paper clearly and sufficiently reflect its contents?」は、空白を詰めて 4 件とも本文に逐語で在った。捏造は見つからなかった。

## 7. 研究者に問うこと
- 貢献の書き方・計算・版の公開・次の round。
