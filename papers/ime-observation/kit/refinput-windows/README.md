# refinput-windows — 参照入力欄 Windows (a) IMM 互換（(b) TSF 直受けは末尾の節）

自分の窓で受けた IME のメッセージ（`WM_IME_STARTCOMPOSITION` / `WM_IME_COMPOSITION` / `WM_IME_ENDCOMPOSITION` /
`WM_IME_NOTIFY`）を、**種別・フラグ・長さ・時刻だけ**の content-free な `gt/1`（`src: "win_imm"`）で記録する
Rust の小さなアプリ。ログ形式の契約は [`../formats/FORMATS.md`](../formats/FORMATS.md)。

- ⚠️★★★ **文字列を一切取得しない**（下の「文字列を取得しないこと」）。
- ⚠️ **解釈しない**: 届いたメッセージを届いた順に書く。どのメッセージが届くか（非 TSF の互換層で何が来るか）は
  Microsoft の一次文書（*IME and TSF Accessibility in Windows XP*）に書かれていないので、実 IME を使った
  較正パイロット（M5）で確かめる。この部品は「届いたら書く」だけで、意味づけ（変換セッションの組み立て）は後段
  （issue 010）が担う。
- 自分のプロセス内の観測なので、グローバルフック・DLL 注入・他プロセスの TSF 観測は使わない
  （`docs/agent-shared.md` 制約 7 に触れない）。

## 構成

| ファイル | 役割 |
|---|---|
| `src/core.rs` | **OS 非依存の核**。`Ev`（事象）→ `gt/1` の 1 行（`line`）・ヘッダ（`header`）・読み戻しの検査（`check_line`）・単位換算（`units_from_bytes` / `ticks_to_ns`）。`cargo test` は Mac でも走る。 |
| `src/bin/refinput_imm.rs` | Windows のみ。窓を 1 つ作り、メッセージを記録して `DefWindowProcW` に渡す。Windows 以外では何もせず exit 2。 |

依存は **`windows = "0.58"`（`cfg(windows)` のみ・`src-tauri` と同じ版）だけ**。JSON は整数と列挙の名前しか出さないので
手書きで、serde は使わない。

## ビルド・起動・selftest

```bash
cd papers/ime-observation/kit/refinput-windows
cargo test                                        # 核の単体テスト（OS 非依存）
cargo build --release --bin refinput_imm
target/release/refinput_imm.exe --selftest --out /tmp/gt.jsonl   # 窓を作らず、核を通して書き・読み戻して検査
python3 ../formats/validate_logs.py --kind gt /tmp/gt.jsonl      # 形の検査（exit 0 なら形は契約どおり）
target/release/refinput_imm.exe --out gt_win_imm.jsonl           # 窓を開いて記録する（窓を閉じると終わる）
```

- `--out <path>`: 出力先。⚠️ 記録の実行では**既にあるファイルを上書きしない**（あれば exit 1。生ログを潰さないため）。
  `--selftest` は指定先を作り直す（`--out` が無ければ一時ファイルに書いて消す）。
- `--selftest`: 窓を作らない。核を通した代表的な列（フォーカス・`VK_PROCESSKEY`・開始・候補窓の開閉・更新・確定・終了）を
  決め打ちの時刻で書き、読み戻して、書いたとおりであること（BOM・CRLF・欠けが無い）と、全行が content-free な `gt/1`
  の形であること（`check_line`）を確かめる。⚠️ 通っても「実 IME でメッセージが届く」ことは示さない。
- **コンソールには何も出さない**。結果は終了コードで知らせる:
  `0` 正常 / `1` 実行時の失敗（窓・書き込み・出力先が既にある・selftest の不一致）/ `2` 使い方の誤り・Windows 以外。
- 出力は UTF-8・BOM なし・LF・1 行 1 オブジェクト・区切りに空白なし。1 行ごとに OS へ書くので、プロセスが落ちても
  そこまでは残る。

## 記録するメッセージ

`DefWindowProcW` に**渡したうえで**記録する（IME の既定の表示を壊さない）。時刻は届いた時点の
`t_wall_ms`（Unix ms・壁時計）と `t_mono_ns`（`QueryPerformanceCounter` を ns に換算・起動からの単調時計。
⚠️ 壁時計は NTP などで跳びうるので、両方を記録する）。

| メッセージ | `ev` | 付随フィールド |
|---|---|---|
| `WM_IME_STARTCOMPOSITION` | `start_comp` | なし |
| `WM_IME_COMPOSITION` | `comp` | `flags`（`lParam` の GCS_* のビット）, `comp_len`, `result_len` |
| `WM_IME_ENDCOMPOSITION` | `end_comp` | なし |
| `WM_IME_NOTIFY` | `notify` | `imn`（`wParam` の IMN_* の値） |
| `WM_KEYDOWN` | `key_down` | `vk`（仮想キーコード） |
| `WM_SETFOCUS` / `WM_KILLFOCUS` | `focus_in` / `focus_out` | なし |

- `vk`: IME が処理中のキーは `VK_PROCESSKEY`（`0xE5` = 229）になる。**そのまま記録する**（意味はパイロットで確かめる）。
  ⚠️ IME が処理しないキーの `vk` は**打鍵したキーの種類そのもの**なので、この窓には**合成入力（公有の刺激）だけ**を送る。
  被験者の自然な入力を受けさせない（content-free は「文字列を取らない」までで、キーの種類は取る）。
- `WM_IME_COMPOSITION` の `wParam`（直近の 1 文字を運ぶ）は**読まない**。読むのは `lParam` のフラグだけ。
- `comp_len` / `result_len`: **UTF-16 のコード単位数**。`lParam` に `GCS_COMPSTR` / `GCS_RESULTSTR` のビットが立っている
  ときだけ `ImmGetCompositionStringW` で得る。立っていなければ 0（ビットが立っていたかは `flags` で分かる）。
  ⚠️ IMM のエラー（負の戻り値）も 0 として記録する（区別しない）。
- ⚠️ 上の表にないメッセージ（`WM_SYSKEYDOWN`・マウスなど）は記録しない。

`core.rs` の `Ev` には TSF 直受け用のバリアント（`TsfStart` / `TsfUpdate` / `TsfEnd` / `UiBegin` /
`UiUpdate` / `UiEnd`）も入っている。この bin（IMM 版）は使わない。TSF 版は下の「(b) TSF 直受け」。

## 文字列を取得しないこと（content-free）

- `ImmGetCompositionStringW` は**バッファ `NULL`・長さ 0** で呼ぶ（`ImmGetCompositionStringW(himc, kind, None, 0)`）。
  この形では文字列そのものは取得されず、**バイト数だけ**が返る（`bytes / 2` = コード単位数）。呼び出しはこの 1 箇所だけ。
- `Ev` のどのバリアントも `String` / `&str` / `char` を持たない。文字列は型の上で運べない。
- 文字を運ぶメッセージ（`WM_IME_CHAR` / `WM_CHAR`）は**記録しない**（扱わず、既定の処理に任せる）。
  ⚠️ ただしメッセージループは `TranslateMessage` を呼ぶ（IME はこれ経由でキーを受ける）。記録しないだけである。
- ⚠️ **形の保証と意味の保証は別**（FORMATS.md「保証の範囲」）。`validate_logs.py` は行の形（列挙・整数・未知のキーなし）を
  確かめるが、整数の欄に本文を符号化して詰めていないことは検査できない。それを担うのはこの部品の設計（種別・フラグ・長さ・
  時刻しか書かない）である。

## 制約・未確認

- ⚠️ **実 IME での動作は未確認**（M5 の較正パイロットで確かめる）。どの `WM_IME_*` / `IMN_*` が、どの順で、
  どのフラグで届くかは、この部品では**解釈も補完もしない**。
- 窓は既定の入力コンテキストのまま（`ImmAssociateContext` などで IME を制御しない）。
- ライセンス: コードは Apache-2.0。

---

# (b) TSF 直受け — `refinput_tsf`

IMM 互換層を**経ずに**、自分のスレッドの TSF の composition の開始・更新・終了と、候補窓などの UI 要素の表示を
`gt/1`（`src: "win_tsf"`）で記録する。MS-IME は TSF の IME なので翻訳層を挟まない（design.md §1.1 (b)）。
形式・content-free の規則は (a) と同じ（契約は [`../formats/FORMATS.md`](../formats/FORMATS.md)）。

**TSF の道: 道 1**

- ⚠️ **design.md の書き方（道 2）とは違う道を採った。** design.md §1.1 (b) は「参照入力欄が
  `ITfContextOwnerCompositionSink` を受ける」と書く。しかしこのシンクを受けるのは**コンテキストの所有者**
  （`ITextStoreACP` を実装したアプリ）で、自前のテキストストアが要る（道 2・大きい）。
  道 1 は **TSF 対応のコントロール（RichEdit `MSFTEDIT_CLASS`）を載せ**、その TSF の文書を**自スレッドの
  `ITfThreadMgr` から見る**。所有者にはならない（`ITfContextOwnerCompositionSink` は実装しない）。
- **理由**: 小さい（テキストストアを自前で持たない）。TSF では text service の composition はアプリのコンテキストの中に
  作られるので、コンテキストの `ITfContextComposition::EnumCompositions` でそれを列挙できる**はず**（⚠️ MS-IME について
  一次資料で確かめたわけではない設計上の仮説。M5 で確かめる）。
- ⚠️ **道 1 が `OnStartComposition` / `OnUpdateComposition` / `OnEndComposition` と同じ粒度で通知を捉えるかは未確認**
  （M5 で実 IME で確かめる）。道 1 の通知は「編集が終わった」（`OnEndEdit`）で、それを見て開始・更新・終了を**導く**。
  違いが出たら preregistration の「正解の経路」の記述に効くので、M5 で実測して直す。

## 何を受けて何を書くか

| 受ける（自スレッドの TSF） | `ev` | 付随フィールド |
|---|---|---|
| `ITfTextEditSink::OnEndEdit`（フォーカス中のコンテキスト）で composition が**新しく現れた** | `tsf_start` の直後に `tsf_update` | `len` |
| 同・composition がある間の編集 | `tsf_update` | `len`（範囲 `cch` の合計。UTF-16 のコード単位数） |
| 同・composition が**無くなった** | `tsf_end` | `result_len`（下記・省略あり） |
| `ITfUIElementSink::BeginUIElement` / `UpdateUIElement` / `EndUIElement` | `ui_begin` / `ui_update` / `ui_end` | `ui_kind` |
| `ITfThreadMgrEventSink::OnSetFocus`（フォーカス中のドキュメントが有る / 無い） | `focus_in` / `focus_out` | なし |
| メッセージループで見た `WM_KEYDOWN` | `key_down` | `vk`（(a) と同じ。合成入力だけを送ること） |

- `ui_kind`: 要素が `ITfCandidateListUIElement` を問い合わせて得られれば `candidate`、`ITfReadingInformationUIElement` なら
  `reading`、それ以外は `other`。`ui_update` / `ui_end` は `ui_begin` で決めた種類を使う（終わった要素を問い合わせられるとは
  限らないため。`ui_begin` を見ていない ID は、`ui_update` では問い合わせ、`ui_end` では `other`）。
- **`tsf_update` は編集のたびに書く**（長さが同じでも。解釈は後段・issue 010）。
- **`tsf_end` の `result_len`** = composition の文字が文書に**残った**長さ
  （終了後の文書末 − 直前まで composition を除いた文書の長さ）。確定なら composition の長さ、取消なら 0。
  ⚠️ issue 010 の `after_result` は `result_len > 0` で確定と取消を分けるので、**省略すると取消に数えられる**。
  文書末の位置が得られなかったときだけ省略する。⚠️ 確定のとき IME が最後に文字を置き換える場合は、最後に観測した長さと
  ずれうる（文書末の差から求めるので、残った長さは正しい）。**実 IME での確認は M5**。
- フォーカスが動いたとき、開いていた composition は**終わりを書かずに忘れる**（終わったか分からないものを終わったと書かない。
  後段は閉じないセッションとして扱う）。
- 候補窓は**隠さない**: `BeginUIElement` で `*pbShow = TRUE` を返し、IME 自身の窓を出したままにする。

## 文字列を取得しないこと（TSF 版）

- 長さは `ITfRangeACP::GetExtent` の **`cch`（と文書末の位置）だけ**。範囲の本文を読む API
  （`ITfRange` の本文取得・`ITfContext` の書式付き本文取得など）は**呼ばない**（`tsf.rs` / `refinput_tsf.rs` に呼び出しが 0 件。
  `009-acceptance.sh` が検査する）。
- `OnEndEdit` が渡す読み取り専用の cookie（`ecReadOnly`）は、`ITfContext::GetEnd` で**文書末の位置を得る**ためだけに使う。
- `ITextStoreACP` は実装しない（道 1 なので本文をアプリ側から TSF に渡す実装が無い）。
- ⚠️ **他プロセス・他スレッドの TSF は見ない**: グローバルフック・`WinEvent`・DLL 注入は使わない。`ITfThreadMgr::Activate` は
  呼んだスレッドの TSF だけを起こす（`docs/agent-shared.md` 制約 7 に触れない）。

## 構成（TSF 版）・ビルド・selftest

| ファイル | 役割 |
|---|---|
| `src/tsf.rs` | Windows のみ。純粋な状態遷移（`CompTracker` / `UiKinds`・COM なしで単体テストできる）と、COM のシンク（`OnEndEdit` / `OnSetFocus` / `UIElement`）・登録（`Tsf::start` / `stop`）。 |
| `src/bin/refinput_tsf.rs` | Windows のみ。親窓と RichEdit を作り、TSF を起こしてメッセージを回す。`--selftest` は TSF を起こさない。 |

```bash
cd papers/ime-observation/kit/refinput-windows
cargo build --release --bins
target/release/refinput_tsf.exe --selftest --out /tmp/gt.jsonl   # TSF を起こさず、状態遷移と核を通して書き・読み戻して検査
python3 ../formats/validate_logs.py --kind gt /tmp/gt.jsonl
target/release/refinput_tsf.exe --out gt_win_tsf.jsonl           # 窓を開いて記録する（窓を閉じると終わる）
```

- 引数・終了コード・出力の書式は (a) と同じ（`0` 正常 / `1` 失敗 / `2` 使い方の誤り・Windows 以外。⚠️ 記録の実行は既にあるファイルを上書きしない）。
- `--selftest`: `CompTracker` に観測列（変換 1 回＝確定・取消 1 回・候補窓・読み窓・その他の窓）を流して事象を得て、
  核を通して書き、読み戻して検査する。⚠️ 通っても「実 IME で通知が届く」ことは示さない。
- 依存: `windows = "0.58"` に feature `implement` / `Win32_UI_TextServices` / `Win32_System_Com` / `Win32_UI_Controls_RichEdit` を足した。
  **`windows-core = "0.58"` を直接の依存に足した**: TSF のシンクを書く `#[implement]` の展開結果が `::windows_core::…` を
  名指しするため（`windows` の依存として Cargo.lock に元からある同じ 0.58 系で、新しい crate は増えない）。

## 制約・未確認（TSF 版）

- ⚠️ **実 IME での動作は未確認**（M5）。特に (1) RichEdit の TSF 文書に MS-IME の composition が現れて `OnEndEdit` が届くか、
  (2) `EnumCompositions` の範囲が `ITfRangeACP` で長さを返すか、(3) 候補窓の `BeginUIElement` が届くか、(4) `tsf_end` の `result_len` が
  確定・取消を区別できるか、は M5 で確かめる。届かない・区別できないなら Stop 条件（道 1 で足りない）として研究者へ返す。
- TSF の UI-less 指定（`ITfThreadMgrEx::ActivateEx` の `TF_TMAE_UIELEMENTENABLEDONLY`）は**使わない**: 使うと UI 要素に対応しない
  text service を止めてしまうため。通常の `Activate` で、UI 要素に対応する text service の通知だけを受ける。
- 合成入力を送るのは oracle の側の責務（この部品は受けて書くだけ）。窓にフォーカスが無いと `focus_in` が来ず、通知も届かない。
