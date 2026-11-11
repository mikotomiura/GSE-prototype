# verdict —— attack-me round 6（stage outline・外枠 commit 90250abc）

## 1. 判定: major revision（Step 4 の 4b による。R1〜R3 はそろって minor）

- 有効な査読: R1・R2・R3・E の 4 本。接地の逐語は round 1〜5 と同じ本文から引いている（R1 は Pohle の別の箇所 "AIC and BIC tend to favor models with too many states" と Monaco "the smoothed POHMM estimates approach that of the unsmoothed" を新しく引いた）。メインは R1〜R3 の引用を各 1 件以上 Grep で確かめた（下の §6）。捏造なし。
- 各役の判定: R1 minor・R2 minor・R3 minor・E「直してから回す（文の単位で直る・2 か所）」・Codex major（別枠）。
- 判定の推移: round 1〜6 すべて major。R1〜R3 は round 6 で初めて 3 人そろって minor。major は E の判定（4b の規則）による。E の 2 か所は文の直しで済む（推奨の範囲を当てた手順と分ける・構造による縮みと手順による縮みを冒頭で読めるようにする）。指摘の多くは round 5 の直しで入れた文（Take-home の「could not have detected … of that size」・推奨の「smoothing … all chosen on other people」）から出ている。
- 費用: Opus 5 本（各 6.9 万〜11.0 万 tokens）・Codex 約 31,000 tokens（この日の累計 228,932 / 2,400,000）。
- 4c 分量: 外枠 3,688 語・75 行（round 5 は 3,530 語）。本文なし。予算の合計 6,800 語。

## 2. 一致した指摘（分母は有効な査読 4 本）

| # | 指摘 | 挙げた役 | 裏取り |
|---|---|---|---|
| W1 | 推奨（Take-home・5 節の「structure, shrinkage and smoothing are all chosen on other people」・入れ子）は本研究で当てていない手順。C1 の当てた手順（平滑を固定・入れ子なし）と分けて書いていない | R2（major）・R3（M2）・E（N1）（3/4）・監査役 3-D・1-A | 真。7・49・65 行。5 節は入れ子にだけ "which we did not do" がある |
| W2 | 「could not have detected per-person differences of that size」（Take-home）と 4.4「both directions are smaller than the protocol could detect」は、返った量を埋めた差の下限と比べる（尺度の混同が形を変えて残った）。合成の条件・k の限定も無い | R1（minor 2・nit）・R3（M1・m4）（2/4）・監査役 2-A・2-B・Codex 2 | 真。7・48 行 |
| W3 | 主の行で選ばれた tau が本文に無い。縮みの族の極限が共通でなく最頻値なので、残りと最頻値 − 共通が同じ大きさなのは族の形から予想される可能性 | R1（major）・R2（2/4） | 真。tau は S8 だけ。族の形はコードで確かめた（round 4）。最頻値の試験の summary によると、主の行（最頻値を候補に入れない 2 段）で選ばれた τ は P15 の k = 1〜12 で全員 10^6、k = 15 で 16 人が 3 × 10^5（tables の「領域」で確かめる） |
| W4 | C1 の「below 1e-2」が k = 15 の場合だけ（k = 5 は 3e-2・k = 1 は測っていない）。5 節の 36 nats も k = 15 だけ | R2・R3（n1）（2/4）・監査役 2-C | 真 |
| W5 | 補足の README が再現の一致を主張し、外枠の Open items（主張しない）と食い違う | R2・R3（m1）（2/4） | 真（README 75–78 行） |
| W6 | 本人の連鎖が強い相手であることが重なった窓に由来するかを、重ならない窓での hmm3 − 連鎖の向きで示していない（以前の外枠にあった文が落ちた） | R1・R2（2/4）・監査役 1-B | 真。round 4 の書き直しで Supporting evidence から「with non-overlapping windows (direction only) it beats the chain in CoAuthor (S13)」が落ちた（私の削り過ぎ） |
| W7 | +∞ の書き手を含めた中央値の母数が書かれていない・有限の書き手だけの数は負に偏って見える | R1・R3（n2）（2/4） | 真。中央値は 17 人（+∞ を含む）で取った（最頻値の試験の summary の n = 17・n_pos_inf = 2）。外枠に母数が無い |
| W8 | 但し書きの繰り返しと 4.3 の細部 | E（N4・N5）・R2（d）（2/4） | 真 |

## 3. 1 人だけの指摘（裏取り）

- E N2 構造の縮みと手順の縮みを冒頭で（C1 に構造だけの行の値）。真。E N3 Take-home の第 2 文が定義前の語。真。E N6 関連研究を序論に持ち込まない。真。
- R1 擬似残差の定義（ランダム化か mid か・記号 25 の扱い）。真（外枠に無い・S13 にある）。R1 AR(1)-HMM を離散の Markov-switching の系譜に結ぶ・自由母数の数。真（引用は一次で確かめてから）。
- R2 適応の判断への橋（k ごとの読み）。真。R2 補足の節の統合（nit）。
- R3 m2「評価単位はどの適合にも選択にも入らない」は最終の手順の中だけ。真。R3 m3 Uto 2020 を 3.2 の根拠に使う。偽陽性に近い: 窓の幅（"frame width W = 30 s and step width H = 10 s"）は以前に本文で確かめて references.md の [P270] に逐語がある。未確認なのは評価の設計だけ。ただし書き方は「30 秒の枠・10 秒の歩み」に合わせる。R3 n3 パネルの名。真。
- 監査役 2-E CS1 の 1e-3 の検出は全員 τ = 10^6 の領域。真（S15 の但し書きに）。2-F「about 0.2」は k = 5 の値で範囲は +0.012〜+0.188。真。2-G 合成の順の文を理由として並べない。真。3-A〜3-C 意図の資料どうしの食い違い（context-B の持ち帰り 1・返る割合の置き場の記録）。真（論文の外）。3-E 後の確かめの数え方。真（S12 で数え方を明示）。3-F context-A の 14 行の古い予算。真（メインの作り直しの漏れ・逸脱）。

## 4. Codex（別枠・既知の未決 11 件を添えた）

判定 major。4 件: 最頻値の「同程度」に破綻した書き手（確率 0）を併記（W7 と重なる・真）。検出の実績を検出の限界に変えた言い方（W2・真）。主の差より計算のゆらぎ（EM の局所解・初期値）が大きいかもしれない（新・一部真: 本人の当てはめは τ ≥ 3 × 10^4 で開始点の 1 位と 2 位の差が 1.2e-8 以下〔tau-extend notes〕、全員の共通は 1 位と 2 位の差が 0.0117 以下で、w を除く共通は全員の共通の勝者から始める。共通の開始点の違いが残りに与える効きは測っていない）。前処理の情報の時点（新・偽陽性に近い: README によると特徴量は直近 30 秒の打鍵、平滑は指数、正規化と格子は固定の定数で、未来を使わない。外枠に 1 句足す）。

## 5. 直す順（案・どれも文の直しで、計算は足さない）

- 1. W1: C1 と Take-home で「当てた手順」（構造と縮みを他人で選ぶ・共通の平滑は固定・入れ子なし）と「勧める拡張」（平滑も他人で選ぶ・入れ子。本研究で当てていない）を分ける。Take-home の推奨は当てた手順と本人の連鎖に限り、拡張は 5 節に。
- 2. W2: 「could not have detected … of that size」と「smaller than the protocol could detect」をやめ、「この記録の長さの合成の書き手で、遷移に埋めた 1e-2 未満（k = 15）・3e-2 未満（k = 5）の差は検出されなかった（4 水準・各 2 種）」と事実だけを書き、向きは「読まない」とだけ書く。
- 3. W3: Table 2 と 4.3 に選ばれた τ（P15 は 10^6、k = 15 で 3 × 10^5）。最頻値の診断は本研究の事前分布の形（縮みの行き先が最頻値）に対するものと範囲を限る。E N2: C1 に構造だけの行の値を 1 句。
- 4. W4〜W8: k ごとの下限・README の文を下げる・重ならない窓の hmm3 − 連鎖の向きを Supporting evidence に戻す・中央値の母数（17 人・+∞ 2 人を含む）・但し書きを 6 節に寄せ細部を補足へ。
- 5. そのほか: Take-home の第 2 文を短く（E N3）・「about 0.2」を範囲に（監査役 2-F）・CS1 の 1e-3 の但し書き（2-E）・合成の順の文（2-G）・擬似残差の定義（R1）・Markov-switching の系譜（R1・引用は確かめてから）・最終の手順の中（R3 m2）・Uto の窓の書き方（R3 m3）・後の確かめの数え方（3-E）・前処理の因果（Codex）・共通の開始点の効きを限界と Open items（Codex）。
- 論文の外: context-B の持ち帰り 1・返る割合の置き場の記録・context-A の予算の行。

## 6. 逸脱・注入の疑い

- context-A の 14 行に古い「予算の合計は 7,000 語」が残っていた（13 行の 6,800 と食い違う）。メインの作り直しの漏れ。E・R3・監査役が気づき、対象物の欠陥には数えなかった。
- R1 は接地の grep を sources 全体に掛け、一覧の外の saeb.txt・varma.txt の断片が出た（使っていない）。
- 接地の照合（メイン）: R1 Pohle "AIC and BIC tend to favor models with too many states" と R2 Saeb "The definition of independence, however, depends on the use-case scenario." と R3 Varma "The parameter selection bias, on the other hand, is always negative." を Grep で確かめた（3 件とも本文にある）。
- 機械の検査は 6 本とも通った。注入の疑い: どの役からもなし。

## 7. 研究者に問うこと

1. 直す一覧（5）を承認するか（計算は足さない）。
2. 直した後: R1〜R3 はそろって minor で、E は文の 2 か所。round 7 を回すか、メインの確かめで閉じて本文へ進むか。
