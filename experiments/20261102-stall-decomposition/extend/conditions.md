# 打鍵の外の信号を持つ公開データへの当てはめの条件（計算の前にコミットする・2026-11-02）

上の `../conditions.md`（`28a91da0`）と `../checks/conditions.md`（`f189859a`）の続き。研究者の決定は `.steering/20261102-gse-stall-decomposition/decisions.md` 判断 11・12・16・17。材料の調べは `docs/literature/20261102-public-data-beyond-keystrokes.md` のカード 1・2（main）。
コミットの前に codex-consult で条件の文を見てもらい、指摘 7 点を取り込んだ（decisions.md 判断 18）。
記述だけで、判定の閾値を置かない。ゲートに載せない。型を選ばない・主要アウトカムを決めない。統制課題の結果は、ふつうのデスクワークへそのまま持ち込まない（ADR-032 D5）。データの間で類の割合を比べない（類の中身がデータで違う）。

## E0 この条件を書く前に見たもの（開示）

- DUX: 2 本の CSV の全行を読み、列の名前・出来事の型ごとの行数・session の数と session ごとの長さ（分）と押下の数・キーの名前の一覧（`LETTER_E` などの名前とその数）を数えた。停滞・休止・型の値は見ていない。
- SWELL-KW: 76 本のファイルの名前の一覧と、1 本（人 1 人の条件 1 つ）の要素の名前・出来事の型ごとの数・名前つきキー（`Backspace`・`Alt + Tab` など）の数・時刻の形を見た。文字の値・ウィンドウの題名・URL は出していない。停滞・休止・型の値は見ていない。
- BB-MAS は使わない（引き継ぎ §3 の順 3・後回し）。

## E1 データ（repo の外 `~/gse-public-data/`）

### DUX [V352]

- Zenodo 7778612 の `v0.csv`（SHA-256 `8909dc6286cbfba32f615688d11e73c8873b97b0f7efad8d3cdf56e5096c63bf`）と `v1.csv`（`5879bea5977903a772393bee2d85e8879df871912d8105ff786823529e87a22b`）。配布元の MD5 と一致を確かめた。置き場は `~/gse-public-data/dux/raw/`。CC BY 4.0。
- 区切りはタブ。v0 は session 10 本・v1 は 36 本で、session の番号は v0 と v1 で重なる。観測の単位（書き手）は（版, session）の組とする（46 本）。同じ人が v0 と v1 の両方にいるかは確かめられない（限界に書く）。
- 1 session は約 9〜33 分・押下は約 700〜1,750 回（E0 で見た）。

### SWELL-KW [V351]

- DANS（doi:10.17026/dans-x55-69zp）の `0 - Raw data/A - anonimized Computer interaction - raw data uLog/` にある XML 76 本。配布元の checksum と 76 本すべて一致を確かめた。置き場は `~/gse-public-data/swell/raw/`。CC BY-NC-SA 4.0（非商用）。来歴には各ファイルの SHA-256 の一覧の SHA-256 を書く。
- 名前は `a_pp<人>_c<条件>_uLog_<日時>.xml`。人は 25 名（pp1〜pp25）、条件は c1〜c3（ふつう・割り込み・時間の圧力）。人 2 の c1 だけ 2 本ある。同じフォルダの文書（`Written Documents…`）と、まとめの zip は取らない。

## E2 取っておく書き手（判断 12・俯瞰と同じ規則）

- 変換・replay の前に決める。SEED は `../SEED`（20261102）。
- DUX: （版, session）の組を `("v0", 番号)`・`("v1", 番号)` の文字列 `v0:<番号>`・`v1:<番号>` にして辞書順に並べ、`random.Random(SEED + 2).sample(一覧, round(0.3 × 46))` = 14 本を取っておく。
- SWELL-KW: 人の番号 1〜25 から `random.Random(SEED + 3).sample(range(1, 26), round(0.3 × 25))` = 8 名（Python の `round(7.5)` は 8）を取っておく。その人の 3 条件をすべて取っておく。
- 一覧は repo の外（`~/gse-public-data/extend/holdout.json`）。標準出力には人数と一覧の SHA-256 だけを出す。来歴に Python の版を書く。外れた書き手（観測 10 分未満など）があっても、取っておいた書き手から補わない。
- 変換は、取っておく書き手の行を識別子（DUX は `session` 列と版・SWELL-KW はファイル名の人の番号）で振り分けるところまでしか処理しない（時刻・型・キーを読まない）。解析の側で、読み込んだ書き手に一覧の書き手が入っていないことを確かめ、入っていたら止める。
- DUX は E0 で全行の構造を見ており、同じ人が v0 と v1 にいるかも分からないので、取っておくものは「見ていない書き手」ではなく「停滞の解析に使っていない session」と呼ぶ。
- 集計は DUX 32 本・SWELL-KW 17 名（51 ファイル前後）で記述する。

## E3 変換（本文を書き出さない）

出力の NDJSON は `meta`・`session_start`・`key` 行（時刻・`category`・`press`）だけ。キーの名前そのもの・文字・本文は書き出さない。打鍵の外の出来事は別の中間（時刻と種類の名前だけ）に置く。変換器は、本文に当たる値（DUX の `enteredText`・`selectedValue`・`target`、SWELL-KW の `KeyboardValue` の文字・`Control*`・`EventDescription`・`CustomEventProperties`）が出力に出ないことを、陽性対照（それらの値を入れた偽の入力）つきの自己検査で確かめる。

### DUX

- 読む列は `session`・`timestamp`（ms の整数）・`type`・`key`・`repeat`・`control`・`alt`・`meta` だけ。
- 処理の順: (1) 版と `session` で振り分ける (2) 時刻の昇順に並べる（同じ時刻はファイルの中の順を保つ） (3) `repeat` が `true` の `KeyPressed` を除く（E0 では 0 件） (4) 押下と離しを対にする (5) category を決める。
- 押下 = `KeyPressed`。離し = 同じ `key` の、押下と同じか後で、次の同じ `key` の押下より前の最初の `KeyReleased`。対にならなかった `KeyReleased` は捨てる。離しが無い押下は、押下 + 100 ms と「次の押下（キーを問わない・(3) の後）の 1 ms 前」の早いほうで合成し、押下より前にはしない（次の押下が同じ ms なら離しは押下と同じ時刻・CoAuthor の規則）。合成した数・捨てた離しの数を報告する。停滞の始まりは押下の時刻だけで決まるので、離しの扱いは型の割合に効かない見込みだが、自己検査で確かめる。
- キーの名前 → category（KLiCKe・CoAuthor と同じ category の名前・件数を見た後だが、値は見ていない）:
  - `LETTER_*` → alphabetic、`DIGIT_*`・`NUMPAD_*` → numeric、`SPACE` → space、`ENTER` → enter、`TAB` → tab、`BACK_SPACE` → backspace、`DELETE` → delete
  - `PERIOD`・`COMMA` → sentence_punctuation、`SEMICOLON`・`QUOTE`・`SLASH`・`BACK_SLASH`・`OPEN_BRACKET`・`CLOSE_BRACKET`・`EQUALS`・`MINUS`・`DEAD_GRAVE` ほか `DEAD_*` → punctuation
  - `SHIFT`・`CONTROL`・`ALT`・`ALT_GRAPH`・`META`・`CAPS_LOCK` → modifier、`LEFT`・`RIGHT`・`UP`・`DOWN`・`HOME`・`END`・`PAGE_UP`・`PAGE_DOWN` → navigation、`ESCAPE` → escape、`F1`〜`F24` → function
  - `ANONYMIZED`（個人情報の欄の文字を伏せたもの）→ alphabetic。`UNDEFINED` とそれ以外 → other。`ANONYMIZED` と other の数を報告する。
  - 修飾つきの押下: `control`・`alt`・`meta` のどれかが `true` の押下で、キーが修飾キーでないもの（`Ctrl + C` の `LETTER_C` など）は、上の表によらず other（文字の入力にも削除にも数えない）。ただしキーが `BACK_SPACE`・`DELETE` なら backspace・delete のまま。`shift` だけのものは上の表のまま。修飾つきで other にした数を報告する。
- 感度（DUX だけ・記述）: `TAB` はフォームの欄の移動なので、`TAB` を navigation（文字の入力に入れない）にした変換でも replay から回し直し、X1 の類の割合と停滞の数を並べる。category の対応は型だけでなく、正味の産出・θ・停滞の集合そのものを変える。
- 打鍵の外: クリック = `MouseButtonDown` と `Scroll` の時刻（O1 の `buttons > 0` か `wheel > 0` に当たる。押した時刻を取り、完了の通知の `MouseClick`・`MouseDoubleClick`・`MouseButtonUp` は使わない）。ポインタの移動 = `MouseMovement` の時刻（沈黙の中の割合の記述だけ）。フォーカスの遷移は無い（類 1 なし）。`ValueSelection`・`TextInput` は読まない。
- 1 session = 1 本の NDJSON。開始 = session の最初の押下。

### SWELL-KW

- 読む要素は `Event` の `EventType`・`EventAction`・`TimeStamp`・`KeyboardValue` だけ。時刻は `TimeStamp`（UTC の ISO 8601・100 ns の桁）を ms の整数に切り捨てる。同じ ms の出来事はファイルの中の順を保つ。
- 押下 = `EventType` が `Keyboard` の出来事（`character`・`special key`・`key combination`）。uLog は 1 打鍵に 1 つの出来事で、押下か離しかの時刻かは確かめられない（限界）。キーを押し続けたときの自動の繰り返しを区別する欄も無い。離しは DUX の「離しが無い押下」と同じ規則で合成する。
- category:
  - `character`: `KeyboardValue` の 1 文字を CoAuthor の `char_category` で分ける。
  - `special key`: `Space` → space、`Return`・`Enter` → enter、`Tab` → tab、`Backspace` → backspace、`Delete` → delete、`Left arrow`・`Right arrow`・`Up arrow`・`Down arrow`・`Home`・`End`・`PageUp`・`PageDown` → navigation、`NumPad0`〜`NumPad9` → numeric、`Escape` → escape、`F1`〜`F24` → function、それ以外 → other。
  - `key combination`（`A + B` の形）: 修飾が `Shift` だけなら、最後の部分を `special key` の規則（1 文字なら `char_category`）で分ける。`Ctrl` か `Alt` を含み、最後の部分が `Backspace`・`Delete` なら backspace・delete。それ以外（`Alt + Tab`・`Ctrl + C` など）→ other。
- 打鍵の外: フォーカスの遷移 = `Other` の `Window Activated` の時刻（行き先と向きは読まない・O1 の `focus_transition` に当たる）。`Keyboard focus changed`（アプリの中の部品の移動）・`Application started/exited`・`Browser URL changed` は使わない。クリック = `Mouse` の `clicked`・`doubleclicked`・`dragged`・`wheel turned` の時刻。ポインタの移動の記録は無い（沈黙の中の移動の割合は出さない）。
- セッション = 1 ファイル（1 本の NDJSON・replay も θ の温まりもファイルごと）。人 2 の c1 の 2 本は 2 つのセッションとして扱い、開始・観測区間・X2 の「最初の押下から 60 秒」はそれぞれのファイルで決める。条件ごとの集計では 2 本を c1 に合わせる。
- 判断 17 の適用の順（取っておかない 17 名のファイルだけで判断する）:
  1. 押下の出来事が 1 つも無いか、時刻が秒より粗いファイルは外して理由を書く。全ファイルがそうなら SWELL-KW を外す。
  2. 残ったファイル全体で `Window Activated` が 1 つも無ければ、遷移の類を作らず「作れない」と書き、全ファイルを 3 類（操作・削除・沈黙）の操作の軸のデータとして残す（3 には進まない）。
  3. 1 つでもあれば、`Window Activated` が 0 のファイルは 4 類の主の集計から外し（O1 の C1 と同じ・「無かった」と「記録が止まっていた」を区別できない）、数と押下の数の和を報告する。併せて、外さない全ファイルで遷移の旗を落とした 3 類の割合も並べる（外したことで類の分布が選ばれていないかを見るため）。

## E4 停滞の始まり

- `gse-replay`（SHA-256 `26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3`・HMM_VERSION 0.5.0）を、CoAuthor の俯瞰（`build_coauthor.py`）と同じ 2 段（replay → `add_feat.py` → `--features`）で回す。p1-episode 1.2.0 の既定（overrides なし）。onset・観測区間（`provenance.observed_intervals`）はそのまま使う（併合しない）。
- 中間は repo の外（`~/gse-public-data/extend/dux_work/`・`swell_work/`）。中間の使い回しは入力と変換器と replay の SHA-256 で照合する。
- 観測が 10 分未満の書き手は外す（俯瞰と同じ）。書き手の観測は、DUX は session の、SWELL-KW は人の残ったファイルの観測区間の和。DUX は 1 session が短いので外れる数を報告する。

## E5 集計（型の定義は `../types_core.py` のまま）

型の軸・窓・優先順・長さの段は上の条件（C2・C3）と同じ。類は DUX が 3 つ（操作・削除・沈黙）、SWELL-KW が 4 つ（遷移・操作・削除・沈黙）。

- X1 型の分布と事後の軸: 上の条件の C4 の P1〜P3 と 3 等分（記述）。4 つの信号の共起の表（優先順で潰す前の旗の有無）も出す。書き手ごとの中央値の単位は、DUX は session、SWELL-KW は人（3 条件の停滞を合わせる・条件で重みを付けない）。率の分母は観測区間との重なり。DUX は沈黙の中のポインタの移動の割合も出す。SWELL-KW は条件（c1〜c3）ごとの類の割合と停滞の 1 時間あたりも併記する。3 等分はセッション（ファイル）の中で取る。
- X2 止まる前の 30 秒の手の様子を、停滞にならなかった短い休止と比べる（主）・無作為な窓を併記: `../checks/conditions.md` の R1 と同じ（u・2〜30 秒の対照・同じ区切りの種類から最大 5 件・最初の押下から 60 秒未満を外す・[u − 30 秒, u] が u を含む観測区間に収まらないものを外す・対照は次の文字の入力が同じ観測区間の中にあり、どの停滞の [s − 30 秒, t0] にも入らないもの（θ が 30 秒より短いと 2〜30 秒の休止も停滞になりうるため）・選んだ対照は戻さない・候補が 0 の停滞は数えて外す・無作為な窓は停滞 1 件につき 10 個）。対照と無作為な窓は停滞と同じセッション（ファイル）から取る。再標本化（2,000 回・95% 区間）は書き手の単位（DUX は session・SWELL-KW は人）で、停滞とその対照を組にする。
- X3 前の型と長さ: R2 と同じ（θ の 4 層・前の窓と固定長の窓・沈黙 ÷ 操作の長さの中央値の比は両方 20 件以上の層だけ）。加えて、同じ集合（X2 に入った停滞）を 3 つの窓（[s − 30 秒, t0]・[t0 − 30 秒, t0]・[u − 30 秒, u]）で分けた型ごとの長さの中央値（`../checks/` の事後の集計を、この実験では計算の前に置く）。
- X4 優先順の感度: R3 と同じ 3 つの順。SWELL-KW は遷移を含む 3 つ、DUX は遷移の無い 2 つ（今の順・削除を操作より上）。
- 集計のコードは `../checks/analyze_checks.py` と `../public/analyze_public.py` の関数を使い回す。書き手・session・人の番号・ファイル名・日時は結果に出さない。

## E6 言える範囲（先に置く）

- どちらも統制課題で、ふつうのデスクワークではない。DUX は旅費精算の試験アプリで、否定的な感情の仕掛け（意図した不具合など）を入れてある。SWELL-KW は模擬の知識労働で、c2 は割り込みのメールで切り替えが設計上増え、c3 は時間の圧力がある。
- DUX の打鍵の多くはフォームの欄への入力で、`TAB` は欄の移動だが、category は他のデータと同じ tab（文字の入力の集合に入る）にした。正味の産出を少し高く数えうる（E3 の感度で並べる）。`NUMPAD_*`・`DEAD_*`・`ANONYMIZED` の対応と、SWELL-KW の `Ctrl + Backspace`（語の単位の削除を 1 回に数える）も、正味の産出の代理を他のデータと少しずつ変える。
- 「沈黙だけ」は、そのデータで採った信号が窓の中に無いことで、無活動ではない（DUX は欄の値の選択・SWELL-KW はポインタの移動とアプリの中の部品の移動を数えない）。
- クリックの旗は、DUX は押した時刻、SWELL-KW は uLog が出す通知の時刻で、窓の端の近くでは計器の違いで類が変わりうる。
- SWELL-KW の打鍵の時刻が押下か離しかは確かめられない。ポインタの移動は記録されない。
- DUX の 1 session は短く（約 9〜33 分）、θ の温まり（`warmup_count`）で停滞の始まりが少なくなる。
- 停滞の始まりは詰まりの判定ではない（ADR-030 の 9b）。型は止まりの手前と最中の手の様子の記述。自己申告での確かめは扱わない（判断 13）。
- 「遷移あり」の類は、SWELL-KW では `Window Activated` が「アプリの中の部品の移動」を含まない点で O1 の `focus_transition` に近いが、同じ計器ではない。
- 取っておいた書き手は開けない。開ける条件は、そのときに先に書く（判断 5）。
- 検定をしない。差は大きさの記述にとどまる。
- 記録・中間・本文を外部の LLM（Codex を含む）に送らない。repo に入れるのは集計だけ。
