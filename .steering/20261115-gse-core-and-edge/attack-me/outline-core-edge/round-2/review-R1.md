# review-R1（round 2・paper-reviewer・opus）
接地: Chukharev-Hudilainen "only consider IKIs above a specific threshold (typically 1--2 seconds) as pauses"・"(somewhat arbitrary) cut-off value"・"the value of tpause considerably varies across participants"・"(3) What is the writer doing during the pause?"。Hanisch ら "implies a weak adversary and must be improved"・"Identity Disclosure"・"such as gender, age, or mental state"・"can freely select an inference technique"・"privacy-functionality (or privacy-utility) tradeoff"。
carryover: 1 一部（経過時間は停滞の定義を引き継ぐ・N1）／2 解消／3 解消（§1 の尖りが広い・N4）／4 一部（道具が本人・属性を測らない・N3、GSE 自身への含意が無い・N2）／5 解消（§5 と食い違う・N5）／6 解消／7 一部（停滞の秒と規則が無い・N6）／8 一部（休止の閾値の伝統・Steegen の番号・N7）／9 解消／10 ほぼ解消（N9）。
評価: a3 b3 c2 d4 e3 f3。
- [major] N2 漏れる所の結果が GSE 自身の記録と「地図に従う系」に返っていない（§4 に何を記録しないか・粒度・公開の範囲が無い）。解消: §4 に漏れる所が GSE の記録に課すもの（未決なら未決）を 1 項目。自信 高。
- [major] N1 招待の時点が「停滞の始まり」に依存し、定義しだいの所を引き継ぐ。退けた「止まりの長さ」案との区別も読めない。解消: 時点を決める量を名指しし、定義を変えたとき何を失うかを 1 文、または「比べるのは招待の有無で定義の正しさではない」と限定。自信 中。
- [major] N3 「他の記録や経路にも当てられる公開の道具」の入力と出力が無く、漏れの検査は内容の照合 1 種で本人の同定・属性の開示を測らない。他の経路に当てると測っていない脅威が地図から黙って落ちる。解消: 入力と出力・「内容の照合だけ」を道具の説明に・漏れる面に「検査していない脅威」の欄。自信 高。
- [minor] N4 尖りの結論が §3 の限定より広い。前提の側を測ったものに合わせて限定。自信 中。
- [minor] N5 §5「同等性の帯で確かめた（Lakens）」が §3 の事後の確認と食い違う。帯の内側の読み方（偶然と同等か小さいが在るか）が定まらない。自信 高。
- [minor] N6 停滞の操作的な定義が無い（秒・規則・人ごとの閾値か）。自信 高。
- [minor] N8 照合の正答率が候補の長さで決まりうる（長さだけの照合を基準に）。自信 中。
- [minor] N7 定義の行に休止の閾値の伝統が無い・Steegen に番号が無い。自信 中。
- [nit] N9 「5 分の 1」の母数・18＋18 と 2 つの信号の名指し・CoAuthor の人数。自信 中。
- [nit] N10 「言える範囲が測れた所の中で続ける」が「読める所は今は無い」と噛み合わない。条件の形に。自信 中。
総合: major（数文を足す範囲で直せる。N2・N3 は設計の判断が要る）。
読めなかった範囲: 接地は一部の行と grep・§7 のパス。注入の疑いは無い。
