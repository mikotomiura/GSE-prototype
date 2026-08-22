# design — `IME_ACTIVE` を cloak 経路で駆動し直す

## 0. ⚠️★★★ 引き継ぎに無かった論点を 1 つ足した — **辺の向き**

引き継ぎ §2 と `findings §15.5` は「`CLOAKED`/`UNCLOAKED` で駆動する」とだけ書いており、
⚠️ **`CLOAKED` と `UNCLOAKED` の *どちらが「候補ウィンドウが見えている」なのか* を
一度も確かめていない。**

★ これは飾りの論点ではない:

| 仮定 | ★ `ime_dwell` が測るもの |
|---|---|
| `CLOAKED` = 候補表示 (★ 旧 v0.1.27 コードの仮定) | ★ 候補ウィンドウの滞在時間 |
| `UNCLOAKED` = 候補表示 (★ DWM の素直な意味論) | ⚠️★★★ **変換と変換の *あいだ*** (候補が隠れている時間) |

⚠️ **件数はどちらでも同じに見える** (cloak = uncloak = n)。★ 順序か実状態を見ないと決まらない。
→ ★ 実測 D (順序 + 窓 ID + DWM 実状態) / 実測 E (静止時の状態) を
`examples/ime_winevent_probe.rs` に足して裁く。

## 1. 全体構成

```
  ┌── WinEvent hook #2 (0x8017..=0x8018)  ★ 新規・既存の IME 用 (0x8027-29) とは別に張る
  │
  ▼
cloak_event_callback
  └─ try_send(CloakEvent { hwnd: isize, cloaked: bool })   ← ★ Atomic + try_send のみ (Win-1)
        │  ⚠️ HWND は Send でないので isize で渡す
        ▼
  cloak resolver スレッド (ime_windows.rs)
        ├─ GetClassNameW(hwnd) → ★ 完全一致 "IME" だけ通す
        ├─ DwmGetWindowAttribute(DWMWA_CLOAKED) で **OS に現在状態を聞き直す**
        │    (⚠️ 辺の名前を信じない。配送は非同期なので実状態が唯一の真実)
        ├─ CloakFold (純粋な状態機械) に食わせる
        └─ IME_ACTIVE / IME_COMPOSITION_START_MS / IME_SHADOW_* を更新
             ⚠️ hwnd は解決に使うだけで **保存も送出もしない**
```

### 1.1 ⚠️ なぜ「範囲を広げる」のではなく **2 本目を張る** か

★ `SetWinEventHook` の `eventMin`/`eventMax` は**単一の連続区間**しか取れない。
`CLOAKED`(0x8017)/`UNCLOAKED`(0x8018) は既存範囲 `0x8027..=0x8029` と連続していない。

⚠️ 広げて `0x8017..=0x8029` にすると、間の **`EVENT_OBJECT_TEXTSELECTIONCHANGED`(0x8020) など
高頻度イベントが全部届く**。★ 2 本目を張れば **2 個のイベント ID だけ**で済む。
→ ★ **2 本目を張る。** 負荷を実測して決めるまでもなく、購読量が桁で違う。

### 1.2 ⚠️★★★ 既存 `EVENT_OBJECT_IME_*` 経路との競合をどう防ぐか

★ 既存経路 (0x8027-29) は**コールバック内で直接** `IME_COMPOSITION_START_MS` などを書く。
⚠️ cloak 経路も同じ atomics を書くので、**両方飛ぶ端末では 2 人の書き手ができる**
(★ この repo が過去に踏んだ事故の型そのもの)。

→ ★ **`LEGACY_IME_EVENT_SEEN` フラグで優先順位を固定する**:
**文書化された経路 (0x8027-29) が 1 度でも飛んだ端末では、cloak 経路は手を出さない。**

★ 実測ではこの Windows 11 で 0x8027-29 は 60 秒 × 8 回すべて 0 件なので、
実際には cloak 経路が駆動する。⚠️ しかし他の IME / 他の OS ビルドで飛ぶ場合に
**壊れる方向ではなく、正しい方 (文書化された経路) が勝つ**。

## 2. クラス絞り — **完全一致 `"IME"` を採る**

| クラス | ★ 実測 (findings §16) | 判定 |
|---|---|---|
| **`IME`** | cloak 18 / 遠い 0 / dwell 中央 701ms | ★ **採用** |
| `Xaml_WindowedPopupClass` | cloak 9 / 遠い 0 | ⚠️ 不採用 — **汎用**(ツールチップ/メニュー/フライアウト) |
| `ApplicationFrameWindow` | cloak 9 / 遠い 0 | ⚠️ 不採用 — **汎用**(全 UWP のホスト) |

★ 決め手は「**名前が IME 固有か**」である。⚠️ 汎用クラスは今回の 60 秒でたまたま
候補 UI しか出さなかっただけで、**被験者が別のアプリを使えばツールチップ 1 個で誤検知する**。
★ `IME` の 2 周期問題は畳めば済むが、汎用クラスの誤検知は畳んでも消えない。

### 2.1 ⚠️★★★ 既存の `is_ime_candidate_class_name` とは **別関数**にする

★ 既存関数は完全一致 `"IME"` を**明示的に除外**しており、回帰テスト
`excludes_language_bar_and_imm32_system_window` がそれを固定している。

⚠️ **これは矛盾ではない。軸が違う**:

| 既存 (`is_ime_candidate_class_name`) | ★ 新規 (`is_ime_cloak_class`) |
|---|---|
| **可視性** (`IsWindowVisible`) で判定する | ★ **cloak 遷移**で判定する |
| ⚠️ `IME` 窓は**常時可視**なので、含めると永久に true | ★ `IME` 窓は**静止時に遷移しない** (60 秒無操作で 0 件・実測) |

→ ★ **別関数として実装し、両方の doc に「なぜ判定が逆なのか」を書く。**
⚠️ **既存の回帰テストは 1 行も触らない。**

## 3. 2 周期の畳み込み — **HWND 別 + ギャップ debounce の二段**

★ 実測は `IME` : 候補UI = 2 : 1 だが、⚠️ **その 2 周期が
(a) 同じ窓の連続 2 往復 なのか (b) 別々の窓の重なり なのかを見ていない。**
→ ★ 実測 D の `窓` 列 (不透明な連番) で判定する。

⚠️ **どちらでも壊れないように両方入れる**:

1. **HWND 別の集合** (`shown: BTreeSet<isize>`) — 集合が空でない間 `IME_ACTIVE = true`。
   → ★ (b) 重なりはこれで 1 区間に融合する (引き継ぎ §2.4 の「単一スロット」問題の解)。
2. **ギャップ debounce** (`FOLD_GAP_MS`) — 集合が空になっても即座に終わらせず、
   その時間内に再び埋まれば**同一セッションの続き**とみなす。
   → ★ (a) 連続 2 往復はこれで 1 行に畳まれる。

★ `FOLD_GAP_MS` の値は**実測 D のギャップ分布から決める** (⚠️ 勘で置かない)。

## 4. 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `src-tauri/Cargo.toml` | ★ `windows` に `Win32_Graphics_Dwm` feature を追加 |
| `src-tauri/src/input/hook.rs` | ★ `CLOAK_EVENT_TX` / `LEGACY_IME_EVENT_SEEN` を追加 |
| `src-tauri/src/input/hook_windows.rs` | ★ 2 本目の WinEvent hook + `cloak_event_callback` |
| `src-tauri/src/input/ime_windows.rs` | ★ `CloakFold` (純粋) + resolver スレッド |
| `src-tauri/src/lib.rs` | ★ resolver スレッドの起動 |
| `src-tauri/src/capabilities.rs` | ★ doc の実態を更新 (⚠️ `config_gated` は据え置き) |
| `src-tauri/examples/ime_winevent_probe.rs` | ★ 実測 D / E を追加 |

⚠️ **`schema_dto.rs` は触らない** —— ★ `ime_shadow` の**行の形は変えない**。
変えるのは「その行が出る条件」だけ。→ ゴールデン / schema / parity は不変のはず (要実測)。

## 5. テスト戦略

| 何 | どう |
|---|---|
| `is_ime_cloak_class` | ★ 単体 (`IME` は通す / `MSCTFIME UI` `IMEClass` `Xaml_...` は通さない) |
| `candidate_shown_from_cloak` | ★ 単体 (★ **実測で決めた向きを固定する回帰テスト**) |
| `CloakFold` | ★ 単体 — 重なり融合 / debounce 内の再入 / debounce 超えの分離 / dwell 計算 |
| 既存回帰 | ★ `excludes_language_bar_and_imm32_system_window` が**緑のまま**であること |
| ゴールデン | ★ `gse-replay ... --snapshot` が byte-equal |
| 実機 | ⚠️★★★ 実起動で `ime_shadow` が**出る** / 無操作 60 秒で**出ない** |


---

# ⚠️★★★ 実装後の訂正 — **設計時の前提が 3 つ崩れた** (2026-08-23)

★ 以下は**実装してから実測で分かったこと**である。⚠️ 上の設計文は当時の理解のまま残し、
ここに差分だけを書く (★ 上を書き換えると「最初から分かっていた」ように見えてしまう)。

## 訂正 1: §3「2 周期の畳み込み」の前提が誤りだった

| | ★ 設計時の理解 | ⚠️ 実測 |
|---|---|---|
| `IME` : 候補UI : ホストフレーム = 2:1:1 の正体 | 「1 変換につき `IME` が **2 周期**する」 | ★ **`IME` クラスの窓が 2 個あり、4 窓が同じミリ秒で同時に動く** |

→ ★ 畳むべきは **(a) 連続 2 往復**ではなく **(b) 窓の重なり**だった。
★ 幸い `CloakFold` は両方入れてあったので**実装は正しかった**が、
⚠️ **debounce の存在理由が変わった** (★ 今は「1 変換の途中の短い明滅」を吸収するため)。

★ `FOLD_GAP_MS` は実測から **150 ms** に確定 (`decisions.md` D-2)。

## 訂正 2: §0「辺の向き」— **実測 E だけでは決まらなかった**

★ 設計時は「静止時センサス (実測 E) で決まる」と考えたが、⚠️ **決まらなかった**。
★ センサスは `EnumWindows` なので**静止時に存在しない窓が見えず**、
⚠️ **変換に関与した当の窓 (`常駐=no`) を見ていなかった**。
→ ★ **実測 G (遷移した窓そのものを 250ms ごとに DWM へ問い合わせる)** を足して決着した。

★ 結論: **`UNCLOAKED` = 候補表示** (⚠️ 旧 v0.1.27 の仮定は逆)。実装は正しかった。

## 訂正 3: ⚠️★★★ **`ime_shadow` の意味が想定より広く、pause をやめた**

★ 設計時 (と引き継ぎ §3.2) は「この信号 = 候補ウィンドウ滞在 ≒ 打鍵時間の 15〜20%」
という前提で、**pause を設計どおり復活させる**つもりだった。

⚠️★★★ **実測でその前提が崩れた** —— この信号は **IME 変換セッション全体**
(ローマ字入力の開始〜確定) を覆い、**pause 率は 56〜60%** になる。

→ ★ **研究者判断で pause を外した** (`decisions.md` D-10)。
⚠️ これは**設計時に予定していたことと逆向き**の変更である。

### ⚠️ 波及した変更 (★ 設計時に無かったもの)

| # | 何 | なぜ |
|---|---|---|
| 1 | `analysis/loop_step.rs` からも `set_paused` を外す | ⚠️ 片方だけだと live と replay が食い違い **Replay-as-Truth が壊れる** |
| 2 | `HMM_VERSION` 0.4.0 → **0.5.0** | ★ 同じ入力から出る `FeatSnapshot` 列が変わるため |
| 3 | ゴールデン `phase1_ime_heavy` を再生成 (6 → 98) | ★ ⚠️ **他 5 本は byte-equal のまま** |
| 4 | `MAX_SESSION_MS` 6s → **20s** / valve 8s → **25s** | ⚠️ 6 秒が**実データを切っていた** (13 中 3 本) |
| 5 | `schema_dto.rs` の `ime_dwell` 定義を訂正 | ⚠️ 旧文「候補ウィンドウ表示〜非表示」は**実測で偽** |
| 6 | ⚠️ `gse-dataset/schema/current.json` も更新 | ★ doc は `emit_schema` 経由で schema に載るため |

⚠️★★★ **§4「変更対象ファイル」に `schema_dto.rs` は触らないと書いたが、触った。**
★ 理由は上記 5 —— **定義文が実測で偽だと分かったため**。
⚠️ ただし **行の形 (フィールド構成) は変えていない**ので、既存ゴールデンへの影響は無い。

## ★ §5「テスト戦略」への追加

★ 設計時に無かったテストを 2 本足した:

| テスト | 何を固定するか |
|---|---|
| `recorded_session_yields_one_row_per_conversion` | ★ **実測の 48 イベント列**を本番の `CloakFold` に流して 12 行になること |
| `too_large_a_debounce_merges_separate_conversions` | ⚠️ `FOLD_GAP_MS` を上げすぎると融合が始まる**境界**を可視化する |

★ さらに `const _: () = assert!(MAX_SESSION_MS + 1_000 <= MONITOR_SAFETY_VALVE_MS)` で、
⚠️ **fold が valve の内側で発火する不変条件をコンパイル時に固定**した
(★ 揃えると 1 変換で `ime_shadow` が 2 行出る)。
