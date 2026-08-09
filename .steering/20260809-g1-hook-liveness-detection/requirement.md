# g1-hook-liveness-detection — キーボードフックの silent death を検知する

## 背景

⚠️★★ 2026-08-09 の Windows 実機 G1 検証で、**5 分間 0 打のブロックが「正常」として自動提出された**
（`experiments/20260801-controlled-friction-task/windows-verification.md §5-7`）。

一次資料で確定していること（★ 推測ではない）:

| 確かめたこと | 実測 |
|---|---|
| block01 の打鍵 | `key` **1 件のみ**（`enter`・計測開始 +10.1 s）→ 以後 **290 秒ゼロ**。`feat` は最後まで 1 Hz |
| 同じ端末・同じ日・同じバイナリの block02 | `key` **2,063**（＝フック自体は動く。★ 陽性対照） |
| 研究者の証言 | 打鍵先は block01 / block02 とも **同じ HTML**（昇格窓ではない） |
| 再インストール経路 | `Keyboard hook message loop exited` **0 件**（★ 陽性対照 `Keyboard hook installed` は 3 件） |
| コールバックの詰まり | `InputEvent dropped` **0 件**。`hook_callback` は **`try_send` のみ**でブロックしない |
| `gse_next_lib` の WARN/ERROR | **6 行だけ**＝既知の 2 種 ×3。★ **異常を示す行はゼロ** |

**構造的な原因**: `hook_windows.rs:215-226` のメッセージループは **`WM_QUIT` でしか抜けない**。
OS が低レベルフックを黙って外しても、ループは回り続け、★ **`HOOK_ACTIVE` は `true` のまま**である
（`HOOK_ACTIVE` は「設置に成功した」しか意味しない＝ `hook_windows.rs:207`）。
→ トレイは終始「● 計測中」、ログにも警告なし、**その場で気づく手段が無い**。

⚠️ ★ **フックが死んだ根本原因（`LowLevelHooksTimeout` 等）はまだ切り分けていない。**
★ しかし **「検知できない」ことは原因と独立に確定している**ので、先に検知を入れる。

## ゴール

★ **「打鍵が記録できていない」ことを、その場で・機械的に分かるようにする。**

1. アプリ自身が気づく（ログに `ERROR`）
2. 研究者／被験者が気づける（トレイが `⚠ 計測できていません`）
3. ★★ **提出物 (`.age`) だけを見て、後から機械判定できる**（新しい行型を刻む）
4. 可能なら自動で復旧する（unhook → re-hook）

## スコープ

### 含むもの

- ★ **OS の「最後の入力時刻」を、自前のフックとは独立に取得する**
  （Windows: `GetLastInputInfo()`。⚠️ ★ **キーの内容も種別も読まない** = `data-privacy` 適合）
- ★ 判定は **OS 非依存の純関数**に切り出し、単体テストで固定する
- **二段の閾値**（grill 決定 D-1）: ログ `ERROR` は短い窓 / トレイ表示は長い窓
- **新しい NDJSON 行型**（grill 決定 D-2）で提出物に痕跡を刻む
  （`schema_dto.rs` → `emit_schema` 再生成 → `check_schema_parity.py`）
- **自動復旧**（grill 決定 D-3）: 既存の「ループ先頭に戻って再設置」経路をバックオフ付きで使う
- トレイの既存 `HookDown` 状態への配線（★ 文言は既にある。**増やさない**）

### 含まないもの

- ⚠️ ★ **フックが死んだ原因の特定**（別タスク。再現実験が要る）
- ⚠️ ★ **macOS 側の実装**（★ macOS には `CONSECUTIVE_TAP_FAILURES` の別経路が既にある。
  純関数は共用できる形にするが、`CGEventSourceSecondsSinceLastEventType` の配線は次タスク）
- ⚠️★★ **被験者向けの新しい文言・通知・介入**（盲検と介入規制を壊す。`protocol.md`）
- ⚠️★★ **ブロックの自動やり直し**（`protocol.md:1082`「打鍵数が閾値を下回ったブロックを
  その場でやり直さない」＝ 結果を見た後の介入になる）。★ **検知と記録が上限**である
- HMM の挙動変更（→ `HMM_VERSION` の bump は**しない**）

## 受け入れ条件

- [ ] ★ 判定の純関数に単体テストがあり、**わざと壊して赤を実測**してある
      （正常 / フック死 / マウスのみ / セッション非活性 の 4 状態）
- [ ] ★ 「システムに入力があるのに自前の `key` が来ない」状態で `tracing::error!` が出る
- [ ] ★ 同じ状態が続くとトレイが `⚠ GSE — 計測できていません（研究者に連絡してください）` になる
- [ ] ★★ 新しい行型が NDJSON に出て、`emit_schema` の出力が `schema/current.json` と byte-equal
- [ ] ★ `validate_blocks.py` / `analyze.py` が新しい行型で**壊れない**
      （★ `FORBIDDEN_LINE_TYPES` は probe 3 種のみ＝ 許可リスト方式ではないことを確認済み）
- [ ] ★ ゴールデン回帰 15 snapshots が **byte-equal のまま**（＝ `feat` 列を変えていない）
- [ ] `cargo test --workspace` / `cargo fmt --check` / clippy / `tsc --noEmit` が緑
- [ ] ⚠️ ★ **Windows 実機での確認は「未実施」と書く**（macOS では最終的な発火を再現できない）

## 関連ドキュメント

- `experiments/20260801-controlled-friction-task/windows-verification.md` §5-7 / §5-8（一次記録）
- `.steering/20260808-g1-tray-status-and-quit/`（トレイ 3 状態の実装と、そこで残った穴）
- `src-tauri/src/input/hook_windows.rs:207` / `:215-226` / `:381`（原因の所在）
- `src-tauri/src/tray.rs:29-52`（`measure_state()` は `HOOK_ACTIVE` を見る）
- `docs/development-guidelines.md` §3（Replay-as-Truth）/ `hook-constraints` Skill / `data-privacy` Skill

## 運用メモ

- **/reimagine 適用: No**
- 理由: ★ grill（3 分岐 × 各 2-3 案）で代替案を並べて選択済みであり、機構そのものは
  「フックと独立した入力時刻の情報源」= `GetLastInputInfo()` が事実上一択のため。
  ⚠️ ただし **原因特定タスク**（別タスク）は「再現が難しいバグ」に当たるので、
  そちらを起票するときは `/reimagine` を検討する。
