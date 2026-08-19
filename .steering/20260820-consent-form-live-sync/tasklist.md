# タスクリスト — 電子同意フォームの反映と突合

## 実施 (2026-08-20)

- [x] 公開 viewform を読み、**古いことを実測で確定**（新文言 0 件 / 対照は検出）
- [x] デプロイ済み `コード.gs` を退避し repo 正本と diff → **意図した 2 ハンクのみ**
- [x] repo 正本を貼り付け → 保存 → ★ **リロード後に読み戻して byte-equal を確認**
- [x] `checkConsentFormParity()` 実行 → `❌ 説明文がコードと一致しない`（既存回答 6 件）
- [x] `migrateConsentForm()` 実行 → `挿入 0 件（説明文の更新のみ）` → `✅ 一致`
- [x] ★ **公開 viewform を再確認** — 新文言 4 種が出て旧文言が消えた（対照つき）
- [x] クリップボードを退避時の状態（空）へ復元

## 受け入れ条件の判定

| # | 条件 | 判定 |
|---|---|---|
| 1 | プロジェクトのコードが repo 正本と byte-equal | ✅ 195,348 B / 3,490 行で一致 |
| 2 | `checkConsentFormParity()` が ✅ | ✅ 「同意項目 8 件・既存回答 6 件」 |
| 3 | 公開 viewform に新文言・旧文言の消失 | ✅ 6 項目すべて実測 |
| 4 | 既存回答が失われない | ✅ 6 件のまま。挿入 0 件・`clearForm` 不使用 |

## 提出経路の検証 (2026-08-20・研究者がテスト提出を実施)

- [x] ★ **提出経路は生きている** — `onG1ConsentSubmit` がトリガー経由で 8.439 秒・完了
      （採番 → 課題ページフォルダ探索 → 受付メール 1 通 → 冪等マーカー記録まで完走）

⚠️ **副作用**: 詳細は `decisions.md` の「P015」節。

## ⚠️ やっていないこと（★ 混ぜない）
- [ ] **案内メールの実文面は未確認** — 2 つ目の diff ハンク（`■ 記録するもの / しないもの`）は
      デプロイ済みだが、⚠️ **実際にメールを送って確かめてはいない**
- [ ] G1-M / G1-S は触っていない（正本に差分が無いため）

## 収集開始の前提条件（`preregistration.md` 第 17 版）

| # | 前提 | 状態 |
|---|---|---|
| 1 | ADR-013 の実装 | ✅ v0.1.27 で実装・実機の `meta` 行で確認 |
| 2 | G-1 の修正 | ✅ v0.1.27・実機で二度押しを実測 |
| 3 | **同意文書と実フォームの突合** | ✅ **本タスクで完了** |
| 4 | ゴールデン 6 本 / schema parity / 両 OS の対のテスト | ✅ **2026-08-20 に実施**（下記） |

## 前提条件 4 の実測 (2026-08-20)

⚠️★ `cargo` は broken symlink だった（`~/.cargo/bin/cargo` → `rustup` が消えている）。
★ ツールチェーン本体を直接呼んで実行した:
`export PATH="$HOME/.rustup/toolchains/stable-aarch64-apple-darwin/bin:$PATH"`

| # | 条件 | 実測 |
|---|---|---|
| D-a | `cargo test --workspace` | ✅ exit 0（439 passed / 0 failed） |
| D-b | `capabilities_covers_every_line_type` | ✅ ok |
| D-c | OS 依存の宣言テスト | ✅ `ime_shadow_is_declared_only_where_its_emitter_is_compiled` |
| D-d | `starve_window_omits_empty_windows` / `dropped_delta_is_written_alongside_cumulative_dropped` / `hook_health_semantics_unchanged` | ✅ 3 件とも ok |
| D-e | `every_capability_has_a_reachable_emitter` | ✅ ok |
| D-f | `emit_schema` byte-equal ＋ `check_schema_parity.py --dataset` | ✅ ⚠️ **dataset 側を同期して**から exit 0 |
| D-g | ゴールデン 6 本 byte-equal | ✅ `replay_snapshot_goldens_byte_equal`（6 本を列挙・空出力も弾く） |
| D-h | `HMM_VERSION` 据え置き | ✅ `0.4.0` |

### ⚠️ D-f は最初 **赤**だった

`check_schema_parity.py --dataset ~/gse-dataset` が exit 1、
`Missing variants in B: starve_window`。★ `~/gse-dataset` の `schema/current.json` が
`CapabilitiesDto` / `HeadIdDto` / `starve_window` を欠く**真部分集合**だった
（引き継ぎ補足の「Windows 機で未コミット」分が push されていなかった）。
→ repo 側から同期し、gse-dataset に `4d4efdc` としてコミットした（+154 行・削除 0）。

### ⚠️ Done 表の**テスト名が実体と食い違っていた**

`requirement.md`（`20260819-g1-reboot-and-instrument-fix`）の Done 表が挙げる
`ime_shadow_in_capabilities_on_windows` / `ime_shadow_absent_from_capabilities_on_macos` /
`dropped_delta_is_per_line_difference` は、**ソースに存在しない**。
実体は `ime_shadow_is_declared_only_where_its_emitter_is_compiled` /
`dropped_delta_is_written_alongside_cumulative_dropped` である。

★ 中身は Done 表の意図より**強い**: 前者は `assert_eq!(declared_here, cfg!(target_os = "windows"))`
で **cfg ゲートせず両 OS で走り**、OS ごとに期待値を変える（「対のテスト」を 1 本で満たす）。
⚠️ ただし **名前で追えない Done 基準**は主張と実体のずれそのものなので記録に残す。

### ⚠️ 未確認

- ★ **Windows 側は未実行**。手元の macOS 検査は `hook_windows.rs` を 1 行もコンパイルしない
  ので、D-c の「**両 OS の CI で**緑」は **CI の結果を見るまで未確認**である。
- `cargo` の broken symlink は直していない（`rustup` の再インストールが要る）。
