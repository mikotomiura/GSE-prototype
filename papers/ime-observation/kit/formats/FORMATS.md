# ログ形式の契約（`gt/1` / `obs/1` / `plan/1` / `oracle/1` / `corpus/1`）

キットの部品はすべてこの契約の上で動く。形式を足す・変えるときは、生産側と検査側を同時に直す。

## 共通

- JSON Lines・UTF-8・1 行 1 オブジェクト。**1 行目はヘッダ**。行末は LF（CRLF は許す）。
- 時刻は整数（`t_wall_ms` = Unix ms・`t_mono_ns` = 単調時計 ns）。
- **区切りに空白を入れない**（`{"a":1,"b":2}` の形）。Python は
  `json.dumps(obj, ensure_ascii=False, separators=(",", ":"))`。
  後続の検査は `"kind":"sent"` のような空白なしの文字列で行を探すので、空白を入れると検査が
  素通り・誤って赤になる。`validate_logs.py` は `gt` / `obs` の行に、文字列の外の空白（`": "` / `", "` を含む）が
  あれば拒否する。
- **エスケープを使わない**。`validate_logs.py` は `gt` / `obs` の行に `\` があれば拒否する（許される文字列値は
  どれも `\` を含まないので、正しい出力は必ず通る）。`"gt\/1"` や、`\u` と 16 進 4 桁で 1 文字を綴った列挙値は
デコードすると列挙に合うが、
  生の文字列で行を探す検査が素通りする。Swift の `JSONEncoder` は既定で `/` を `\/` と書くので、
  `outputFormatting` に `.withoutEscapingSlashes` を付ける。Python は上の `json.dumps` のままでよい。
- **BOM を付けない**（UTF-8 の BOM は JSON として読めず拒否される。.NET の `Encoding.UTF8`・PowerShell 5 の
  `utf8` は既定で BOM を付けるので注意）。
- 整数は JSON の整数だけ（小数・指数表記・`NaN`・`Infinity` は拒否）。範囲は、`obs` は GSE の型に合わせて
  `t` / `dwell_ms` が 0〜2^64−1・`nav` が 0〜2^32−1、`gt` の付随フィールドと時刻は −2^63〜2^64−1。
  範囲を置くのは、1 つの欄に詰められる量を 8 バイトまでに抑えるため（⚠️ 範囲の中の値の意味は検査しない ——
  下の「保証の範囲」）。
- 同じキーを 1 行に 2 回書かない（検査器ごとに採る値が違い、本文を隠せるため）。

## `gt/1` — 参照入力欄が出す正解の生ログ

- ヘッダ: `{"kind":"header","format":"gt/1","src":<"mac_nstic"|"win_imm"|"win_tsf">,"app_version":<str>,"os":<"macos"|"windows">}`
- イベント: `{"kind":"ev","t_wall_ms":int,"t_mono_ns":int,"ev":<enum>, ...}`
- `ev` と付随フィールド（**付随フィールドは整数か真偽値だけ**。`cmd` / `ui_kind` のみ列挙型の文字列。
  現行の表のフィールドはすべて整数で、真偽値の位置は無い）:

| src | ev | 付随フィールド |
|---|---|---|
| 共通 | `key_down` | `vk`（OS のキーコード） |
| 共通 | `focus_in` / `focus_out` | なし |
| `mac_nstic` | `set_marked` | `len`, `sel_loc`, `sel_len`, `rep_loc`?, `rep_len`? |
| `mac_nstic` | `insert_text` | `len`, `rep_loc`?, `rep_len`? |
| `mac_nstic` | `unmark` / `first_rect` | なし |
| `mac_nstic` | `do_command` | `cmd` ∈ {`insertNewline:`, `cancelOperation:`, `deleteBackward:`, `deleteForward:`, `moveLeft:`, `moveRight:`, `moveUp:`, `moveDown:`, `insertTab:`, `insertBacktab:`, `noop:`, `other`} |
| `win_imm` | `start_comp` / `end_comp` | なし |
| `win_imm` | `comp` | `flags`（GCS_* のビット）, `comp_len`, `result_len` |
| `win_imm` | `notify` | `imn`（IMN_* の値） |
| `win_tsf` | `tsf_start` / `tsf_end` | `tsf_end` のみ `result_len`? |
| `win_tsf` | `tsf_update` | `len` |
| `win_tsf` | `ui_begin` / `ui_update` / `ui_end` | `ui_kind` ∈ {`candidate`, `reading`, `other`} |

長さはすべて **UTF-16 のコード単位数**。`?` は省略可。「共通」の `ev` はどの `src` でも出せる。
上の表にない `ev` は、その `src` では出ない `ev` として拒否する。

**content-free の規則**: 文字列を値に持てるのは `kind` / `format` / `src` / `app_version` / `os` / `ev` / `cmd` / `ui_kind`
だけ。`app_version` は正規表現 `^[0-9A-Za-z.+-]{1,32}$`、他は上の列挙のどれか。**未知のキーは拒否**、
整数の位置に文字列・配列・オブジェクトが来たら拒否（真偽値・`null` も整数ではないので拒否する）。

## `obs/1` — 単体ロガーの出力

GSE の NDJSON 行と**同じ名前・同じ形**（GSE 側の一次は `schema_dto.rs` の `LogEntryDto` と
`capabilities.rs` の `capabilities_json()`）。

- ヘッダ: `{"type":"meta","format":"obs/1","os":<"macos"|"windows">,"logger_version":<str>,"manifest_sha256":<64 hex>,"capabilities":<object>}`
  - `logger_version` は `app_version` と同じ規則（`^[0-9A-Za-z.+-]{1,32}$`）。`manifest_sha256` は 16 進 64 桁。
  - `capabilities` は GSE の `meta.capabilities` と**同じ形** =
    `{"unconditional":[<名前>…],"threshold_gated":[<名前>…],"config_gated":[<名前>…]}`。
    **3 つのキーはすべて必須**で、値は**文字列の配列**（空でよい）。名前は行の種類の名前で、
    **`key` / `ime_shadow` の列挙**（単体ロガーが出す行の種類はこの 2 つだけ）。3 つの配列を通して
    **各名前は高々 1 回**（重複は拒否・合計 2 個まで）。⚠️ 名前を正規表現で開いておくと、ローマ字の単語列を
    何個でも入れられる（本文の抜け道になる）ので閉じた列挙にしている。
- `{"type":"key","t":int,"category":<14 種>,"press":bool}` — `category` は `alphabetic` / `numeric` /
  `punctuation` / `sentence_punctuation` / `tab` / `backspace` / `delete` / `space` / `enter` /
  `navigation` / `modifier` / `function` / `escape` / `other`
- `{"type":"ime_shadow","t":int,"dwell_ms":int,"nav":int,"abandon":bool}`
- 上以外の `type`（2 行目以降の `meta` を含む）・未知のキー・列挙外の文字列は拒否。

## `plan/1` — 生成器の出力

- ヘッダ: `{"kind":"header","format":"plan/1","os":…,"seed":int,"generator_version":str,"config_sha256":<64 hex>}`
- ブロック: `{"kind":"block","block_id":int,"speed":"slow"|"mid"|"fast","reset_ime":bool,"marker":[<keyname>…],"marker_gap_ms":int}`
- 試行: `{"kind":"trial","trial_id":str,"block_id":int,"scenario":"S1"…"S15","speed":"slow"|"mid"|"fast","gap_before_ms":int,"think_ms":int,"phrase_id":str,"reading_len":int,"steps":[{"key":<keyname>,"at_ms":int,"down":bool}…],"intent":{…}}`
- `gap_before_ms` = 前の試行の終わりからこの試行の先頭までの待ち、`marker_gap_ms` = マーカーのキーの間隔。
  実行器はこの 2 つの値だけで待つ（自分で決めない）。
- **ブロックは速さで揃える**（1 ブロック = 1 つの速さ。ブロック行の `speed` と、その中の試行の `speed` は一致する）。
- `intent` のキーは `commit`（`enter` / `digit` / `mouse` / `none`）・`cand_index`・`nav_count`・`abandon`・
  `predictive`・`ime_toggle_mid`・`focus_switch_mid`・`expect_session`。
- 計画は刺激（公有の文の読み）なので content-free の対象ではない。

## `oracle/1` — 実行器の出力

- ヘッダ: `{"kind":"header","format":"oracle/1","plan_sha256":…,"os":…,"emitter_version":…,"backend":<"dryrun"|"macos"|"windows">}`
- `{"kind":"sent","trial_id":…,"step":int,"key":<keyname>,"down":bool,"t_wall_ms":int,"t_mono_ns":int}`
- `trial_begin` / `trial_end` / `block_begin` / `block_end`（`trial_id` または `block_id` ＋ 2 つの時刻）
- `{"kind":"marker","block_id":int,"seq":int,…時刻}`
- `{"kind":"reset","block_id":int,"exit_code":int,…時刻}`

## `corpus/1` — 句と読み

- ヘッダ: `{"kind":"header","format":"corpus/1","source":"aozora","tokenizer":str,"dict":str}`
- `{"kind":"phrase","phrase_id":str,"work_id":str,"text":str,"reading":str,"reading_len":int}`
- `reading` は**ひらがなだけ**（`^[ぁ-ゖー]+$`）。

## `keyname` の列挙

`a`–`z`, `0`–`9`, `space`, `enter`, `esc`, `backspace`, `tab`, `left`, `right`, `up`, `down`, `minus`, `comma`,
`period`, `ime_on`, `ime_off`, `f13`–`f19`, `shift`, `mouse_click`, `focus_away`, `focus_back`
（最後の 2 つは実キーではなく、実行器のバックエンドが OS の手段で前面のアプリを切り替える擬似キー・S15 用）。

## 検査

- `kit/formats/validate_logs.py --kind gt|obs FILE...` — 違反を行番号つきで出して exit 1、違反なしなら exit 0
  （exit 2 は検査できなかった。★ 0 以外はすべて不合格。違反があれば、開けないファイルが混ざっていても exit 1）。
  **違反の説明に値は出さない**（本文が混じっていても出力から漏れない）。キー名も、この文書に載っている名前の
  ときだけ出す。
- **保証の範囲**: 検査器が機械で保証するのは行の**形**である —— 文字列の値は列挙か正規表現に収まり、未知の
  キー・エスケープ・重複キーは無く、整数の位置には範囲内の整数しか無い。⚠️ **値の意味は保証しない**:
  整数の欄（`vk`・長さ・時刻）・版の文字列（`app_version` / `logger_version`）・`manifest_sha256` に符号化して
  詰めた本文は検出できない。content-free は**生産側の設計**（種別・長さ・時刻しか書かない）が担い、検査器は
  その形を確かめる。
- 機械検査するのは `gt` と `obs` だけ（content-free が要るもの）。`plan` / `oracle` / `corpus` の検査は、
  生産側の部品が自分の selftest で持つ。
