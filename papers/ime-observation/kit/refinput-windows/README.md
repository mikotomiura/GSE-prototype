# refinput-windows — 参照入力欄 Windows (a) IMM 互換

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

`core.rs` の `Ev` には issue 009（TSF 直受け）用のバリアント（`TsfStart` / `TsfUpdate` / `TsfEnd` / `UiBegin` /
`UiUpdate` / `UiEnd`）も入っている。この bin は使わない。

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
