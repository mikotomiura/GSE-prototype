# review-R3（事前登録・研究者の自由度・同等性の検定のメタサイエンス・摘発者・paper-reviewer・opus）—— round 1

## 接地
- Wicherts et al. 2016: "it is crucial that preregistrations provide a specific, precise, and exhaustive plan of the study."／R6 "Presenting exploratory analyses as confirmatory (HARKing)"／"which is unproblematic as long as these explorations are clearly distinguished from the confirmatory analyses."／R3 "Failing to mention, misrepresenting, or misidentifying the study preregistration"／"report all potentially relevant analyses either as traditional sensitivity analyses or as a multiverse analysis (Steegen et al., 2016)."
- Lakens 2017: "Psychologists often incorrectly conclude there is no effect based on a nonsignificant test result."／"To conclude equivalence (Scenario A), the 90% CI around the observed mean difference should exclude the Δ L and Δ U values"／"it is expected that equivalence bounds are prespecified … the abstract should also include the equivalence bounds"／"we can conclude equivalence for a specific operationalization of a hypothesis."／"in small samples (where CIs are wide), a study might have no statistical power"

## 評価表
a 2（帯の事前/事後の食い違い・面の定義が §3 の限定より強い・帯の使い方が非対称）／b 2（区間が無い・約 125 の数え方と事前かが無い・n=3 の判定の規則が無い）／c 3（読める所に停滞が無い）／d 3（用語が未定義・0.489・0.487 の意味）／e 3（開発との対応が読めない）／f 1（外部の先行研究が 1 本も無い）

## 指摘
- [major] 帯が事前登録か事後かが食い違う（§2 の 1・§3）。解消: 帯を決めた日付と見ていた/見ていなかったデータを書き分け、事前登録の下で当てたと言うのは見ていなかったデータ（CS1 の holdout）に限る。残りは「同じ帯を事後に当てた」。自信 高。
- [major] 点推定が帯の中にあることを「分けなかった」と読み、区間による同等性の判定が無い（Lakens の Scenario D）。解消: データごとに 90% 区間を添え、帯の内に収まるものだけ「分けなかった」。素材の段では少なくとも「点推定は帯の内、区間は根拠のパス」と明記。自信 中。
- [major] 帯の使い方が非対称（推定器の 0.512 は否定、学習器の 0.54 は信号がありうる）。0.54 は帯の内。学習器のデータと事前かが無い。解消: 学習器にも同じ帯と区間・データ名・探索なら明記。自信 高。
- [major] 地図の面の定義が §3 の限定より強い（読めない所＝観測一般、確かに言える＝合成入力の recall だけで偽陽性の側も人も無い、漏れる所に偶然の水準 0.1・0.01 と限定が無い）。解消: 面の定義を「この操作化では言えなかったこと」「合成入力で言えたこと」「既知の候補の集合から照合できたこと」に下げ、§1 の表にも限定と偶然の水準。自信 高。
- [major] 招待を出す条件（停滞の中）が地図の読める所に無い。解消: 招待の条件を観測で読める量そのもの（例: 止まりの長さ・「9 割以上が停滞に至らない発火」と両立させる）で定義し直し、「停滞の中」と呼ばず「停滞かどうかを判定せずに差し出す」と書き分ける。自信 高。
- [major] 「約 125 の定義で結論が動く」が具体的でも精密でもない（数え方・事前に凍結したか・反転の割合・比が何の比か・転帰が作文の点であること）。解消: 正確な数・凍結の有無・「N 個のうち k 個で反転」「比の範囲 x〜y」。自信 高。
- [major] 段 1 の n=3 の「確認」に判定の規則も向きも無い（Wicherts T2・Lakens の小標本）。解消: 言えることの水準と判定の規則を 1〜2 文・§4 との対応。自信 中。
- [major] 先行研究の位置づけが無く、尖りを支える新規性の根拠が欠ける。解消: 各検査に最も近い先行を 1〜2 本と差分を 1 文・探していないなら範囲と期限。自信 中。
- [minor] 「9 割以上が停滞に至らない発火」に分母と比べる相手（偶然の水準・試した閾値の数）が無い。自信 中。
- [minor] 2 つずつの AUC の意味と主の解析の名指しが無い。自信 高。
- [minor] 作るソフトウェアが読めない（様式は未照合なので minor）。自信 低。
- [nit] 用語（30 秒の上がり・停滞の手前・データ間の比）の未定義。自信 高。
- [nit] 公開データの数が 3 と 4 で違う。各検査のデータ名を列挙。自信 中。

## 総合: major
予測の検査の主張が、帯の事前/事後・点推定だけ・帯の非対称な使い方で根拠より強い。地図の 4 面が §3 の限定を落とし、読める所に停滞が無く招待の条件が立たない。定義の動きの大きさ・段 1 の判定の規則・先行研究との差分を数文で足せば外枠として成り立つ。

## 読めなかった範囲
wicherts2016 の 1228〜1454 行（参考文献と推定）。根拠のパスは読んでいない。注入の疑いは無い。
