# verdict — attack-me・stage `prereg`・対象物 Windows の追補・round 1（2026-10-03・Surface・メイン）

対象物: `papers/ime-observation/experiment/preregistration.md` §10 と、タグ `ime-observation-prereg-macos` から `53eec8f2` までの公開物とコードの変更。投稿先 BRM。

## 1. 編集者の判定: **major revision（直して再査読）**

- 有効な査読: **3 / 3**（R1・R2・R3 とも接地に入り査読まで進んだ。4 本とも保存の検査を通った: `secrets-filter.sh` 0・応答に絶対パス 0。4 本とも「一覧の外は開いていない・Grep は一覧のファイルを 1 つずつ」と申告）。推奨は **R1 major・R2 major・R3 major**。fatal 0。
- 接地の引用: 3 人から計 12 文を `tmp/sources/` の本文で照合（空白と行末のハイフンを正規化）→ **12 / 12 在る・捏造 0**。
- 注入の疑い: 4 本とも なし。
- 理由（3 行）:
  1. **Windows の観測器の指定が §10 に無く、書いた説明（「composition events を読む」）は実装と違う**（3 / 3 と監査役が別の角度で）。観測器のセッションは IME の窓が見えている区間で、経路が 2 つあり、20 秒の打ち切りは cloak の経路にしか無い。
  2. **D3 の根拠がそれに依る**: 「20 秒の打ち切りは両 OS で同じ」は成り立たず、範囲を正解（比べる片側）の長さで決めることの偏りも書いていない（3 / 3）。
  3. 公開の安全と固定の残り: TSF の参照では人の打鍵が停止規則に掛からない帰結（3 / 3・R2 major）、問 4 の判定規則の "both cells"（R2 major）、Windows の解析に並べる run と 2 つのタグ（R3・監査役）、手順書とセルのパスの不一致（3 / 3 と監査役）。

## 2. 一致した指摘（分母 = 有効な査読 3。監査役は別枠）

| 群 | 指摘 | R1 | R2 | R3 | 監査 | 裏取り |
|---|---|---|---|---|---|---|
| A | Windows の観測器の指定が無く、「composition events」は誤り | major | major | major | — | **真**: `ime_winevent.rs`:1-4・12（`EVENT_OBJECT_IME_SHOW`/`HIDE`・「A display event opens a conversion session and a dismissal closes it」）・`cloak.rs`:4-8。§10.6・D3・`gt_scope.py` の docstring が誤り（メインの誤記） |
| B | 20 秒の打ち切りが経路で違い、起点も違う → D3 の「same on both systems」は成り立たない | major | (major の中) | (major の中) | — | **真**: `MAX_SESSION_MS` を使うのは cloak の経路だけ（`ime_cloak.rs`:295・`cloak.rs`:643）。WinEvent の経路（`ime_winevent.rs`:82-91）は打ち切りなし。`MONITOR_SAFETY_VALVE_MS` は定数の検査（`ime_cloak.rs`:190）にしか使われない。MS-IME でどちらが動くかは、封印した行を読まない限り分からない（ロガーの stderr には経路の記録が無いことを確かめた） |
| C | D3 は範囲を正解（比べる片側）の長さで決める。独立な定義（計画・oracle）を主か副に・境界の帯を報告 | major | minor | minor | — | **真**: §6.4「decided from the oracle and the plan alone」と食い違う。パイロットで計画の長さと正解の長さは 10/10 × 2 run（同じ計画・seed 8）で一致 |
| D | TSF の参照に人が打つと、どの停止規則にも掛からない（帰結が書かれていない・補う検査が無い） | minor | **major** | — | — | **真**: TSF の参照は IME が消費したキーを受け取らない（パイロット 3〜16 / 1,174〜3,900）。焦点も失われないので理由 4 も働かない。§3.4 は喪失の外の観測の余分な行で中止にしない |
| E | `cell.windows.json` のパスが手順書の基準（公開物の根）と合わない | minor | minor | — | 3-2 | **真**: 書き出しはパスを書き換えない（`export.internal.py` を確かめた）。メインの誤り |
| F | `python3` と `python` の不一致 | nit | nit | nit | 3-1 | **真**。⚠️ `run.sh`:37-38 は Store のスタブの `python3` を選ぶ（この機械） |
| G | §10.1 の変更の一覧がタグの差と一致しない（`notes.md`・selftest）／過去形 | minor・nit | nit | nit・nit | 2-5 | **真** |
| H | `pipeline.py` の古い docstring（49-50・781-782 行）と `PRIMARY_NOTE` が D3 と矛盾 | minor | — | — | 3-3 | **真** |
| I | 「39 of 39 in each of three runs」は IMM を含む（`win_tsf` の根拠は 2 run） | nit | nit | nit | — | **真** |
| J | 所要時間の比は直す前の手順から（直した後は 15.2 s） | minor | — | minor | 2-2 | **真**: 直した後の短い run は 15.2 / 13.02 = 1.17（ブロックあたりの起動の負担が大きい）→ 約 12〜13 時間と幅で書く |
| K | README.windows.md の「four runs」と pilot-windows.md の「pilot runs」が合わない | nit | — | — | 3-4 | **真**（4 本 = `pilot-*`・`verify-*` が以前の版。`short-*` は使っていない） |

1 人だけの指摘（裏取り）:

- R2 major: **問 4 の判定規則 "both cells" が 3 セルで決まっていない・Windows の問 4 の命令が無い** → **真**（§6.8 l.896-897・l.858 の `--config experiment/plan_config.macos.json`。`closed_set.py` は設定の SHA-256 を照合する）。
- R2 minor: IMM のパイロットの寄託の基準（k = 1）は登録の道具（`--check-deposit` は k = 0）で実装されていない → **真**。
- R2 minor: 凍結の機械の門が追補を区別しない（`sha256:` が同じ値なので、追補の凍結の前でも Windows の run を解析できる）→ **真**（D2 はすでにコードにある）。
- R2 minor: 利用者が自分の環境で読む指針（観測器は入力欄に依存しないが、正解の確定の時点は依存する・IMM と TSF の差）→ **真**（§10.10 に足せる）。
- R2 minor: Windows の観測器が key 行を書くキーの種類（修飾キーなど）が §10 に無い → **真**（`keyboard.rs`:47-52）。
- R3 minor: 逸脱が macOS を変えない根拠が再現できる形で無い（命令とハッシュ）→ **真**。
- R3 minor: §9 の SHA の表が Windows のタグで古くなる → **真**（§10.5 に Windows のタグの表を足せる）。
- R3 minor: Windows の解析に `data.md` のどの run を並べるか（2 つのタグ）→ **真**（`run.sh`:97・監査役 3-5 と同じ。macOS のタグの解析は Windows の run で止まる）。
- R3 minor: Windows の n と精度を層ごとに → **真**（表と命令を足せる）。
- R3 minor: 問 5 の Windows の CPU の量の定義と `cpu_all_zero` の扱い → **真**（`kit/e3/README.md`:38・65-68）。
- R3 minor: 参照の経路（TSF）を機械で検査していない → **真**（`src` が `win_tsf` でない run を解析しないと書く・または検査）。
- R3 nit: Windows のパイロットの封をした行を解析しないと §10.9 に明記していない → **真**。
- R1 minor: `pilot-windows.md` の数の整合 → **部分的に真**: 「1,174」は `short-tsf` の送った押下（39 試行・直す前の手順）で正しい（R1 は直した後の run だけを想定）。ただし「key-downs」は「試行の中で送った押下のうち参照に key-down として届いた数」（印を含まない・`delivery.py` の `reference.reach`）で、言い方が曖昧 → 直す。
- R1 minor: 主にする定義（`windows_def` か `all` か）が §10.6 と §5 で矛盾 → **真**。§5 の規則どおり `windows_def` を主にし、`all` から範囲を作ることを書く。
- R1 minor: TSF の参照の合成の境界の推定（`tsf.rs`:83-90・102-111）が報告されない → **真**（`result_len` の無い `tsf_end` の数を診断として登録できる）。
- R1 minor: 時計の外挿・§6.9 の 22 ms は macOS の値 → **真**。
- R1 minor: S14 の `VK_IME_ON/OFF` は人の「半角/全角」と別・S4 の取消が何回目か・手打ちとの比較が無い → **真**（限界と診断に足せる）。
- R1 minor（自信 低）: 観測器が Windows で行を 1 つも出さないとき → **真**（`pipeline.py`:33-36 は ime_shadow の行が 0 の run を拒む）。事前に扱いを決める。

監査役（別枠）: 1-1（§10.9 が IMM の k = 1 を隠す）真・1-2（問 3 の並べ替えの見方が Windows で null）真・1-3 真（軽い）・1-4 真（計測の時点で埋める）・2-1（`windows_def` ≈ `all` で C2 の母数の読み方が変わる）真・2-3（Romaji input の記録が判断に無い）真（レジストリに入力方式の上書きが無いことをこの round で確かめた）・2-4（§10.3 の状態の言い方が強い）真・3-6（`data.md` の手での照合が Windows の計画を指さない）真・3-7（開いたままのセッション）真。

## 3. 直す順

- major（設計の判断が要る → 研究者に問う）: B・C（長い試行の定義）／D（人の打鍵の盲点への検査）／R2 の問 4 の規則／R3・監査 3-5 の Windows の解析の入口と run の一覧
- major（判断は要らない）: A（§10 に「Windows の観測器」の小節・§10.6・D3・`gt_scope.py` の誤記）
- minor: E（パス）・F（Python の呼び名）・G・H・J・K・R1 の数の言い方・主にする定義・TSF の合成の境界の診断・時計・S14/S4 の限界・行 0 の扱い・R2 の利用者の指針とキーの種類・IMM の寄託・門の区別・R3 の再現できる根拠・§9 の表・層ごとの表・問 5・経路の検査・監査役 1-1・1-2・2-1・2-4・3-6・3-7
- nit: I・過去形・封をした行の明記

## 4. 逸脱・その他

- 失敗した役: なし。再起動なし。
- ⚠️ メインの誤り: 「composition events」（A）と `cell.windows.json` のパス（E）は、メインが一次（コード・書き出し）を確かめずに書いた。
