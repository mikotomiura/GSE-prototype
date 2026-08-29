# replay.rs の既存 flaky test を直す（✅ **2026-08-29 完了**）

> ⚠️★★★ **起票日**: 2026-08-25（★ `.steering/20260825-o1-researcher-decisions/` の **判断 O1-7 / D-7** で
> 「別タスクとして起票する」と研究者が決定）。⚠️ **本ディレクトリは起票であって、着手記録ではない。**

## 背景

★ 発見は **2026-08-24 の mac セッション**（`.steering/20260824-o1-macos-instrument/decisions.md` **判断 5**）。
⚠️ **発見したセッションの diff とは無関係**であり、原因は既に main にある別コミットである。

- **真因**: `9eb1384c`（PR #113・Windows 側 O1 実装）が、新テスト関数
  `o1_observation_lines_are_skipped_by_run_replay` を **既存の `#[test]` 属性と関数定義の *間* に挿入**した。
- **結果 1**: 旧 `#[test]` が**新関数へ再結合**され、⚠️ **同じ関数に `#[test]` が 2 回**付いた
  （`duplicated attribute` 警告）。→ ★ 2 インスタンスが**同一の一時ファイルパス**
  （`std::process::id()` ベース・同一プロセスなので同じパス）へ並列に書き込み・削除し、⚠️ **まれに失敗する**。
- **結果 2**: ⚠️★★★ `hook_health_line_is_skipped_by_run_replay` が **自分の `#[test]` を失い、
  テストとして実行されなくなった**（`dead_code` 警告）。→ ★ **静かに無効化された回帰保護が 1 本ある。**

## ゴール

- [x] 重複した `#[test]` を解消した
- [x] `hook_health_line_is_skipped_by_run_replay` に **`#[test]` を付け直した**
- [x] `cargo test --workspace` を **5 回**回して緑（★ flaky 再現せず）
- [x] `duplicated attribute` / 当該 `dead_code` の警告が消えたことを確認

## ⚠️ 起票時の想定より 1 つ多かった（★ 実物を読んで判明・2026-08-29）

★ 起票は「`#[test]` を 1 行消して 1 行足す」としていたが、⚠️ **`hook_health` の doc コメント 7 行も
一緒に取り残されていた**（`:2369-2375`）。PR #113 は
**doc コメント + `#[test]` と関数定義の間**に新しい doc + `#[test]` + 関数を挿入していたため、
★ hook_health を説明する 7 行が **o1 の関数に付いていた**。

→ ⚠️ 属性だけ直すと**説明文がずれたまま**になるので、**doc 7 行 + `#[test]` をまとめて
`fn hook_health_line_is_skipped_by_run_replay` の直前へ戻した**。

## ★ 実測（★ 直る前 / 直った後）

| | main（修正前） | 修正後 |
|---|---|---|
| `o1_observation_lines_are_skipped_by_run_replay` | ⚠️ **2 回**表示（＝二重登録） | ✅ 1 回 |
| `hook_health_line_is_skipped_by_run_replay` | ⚠️ **実行されない**（`function ... is never used`） | ✅ **実行される** |
| `cargo test --workspace` × 5 | — | ✅ 5/5 緑 |
| ゴールデン replay | — | ✅ `OK: 15 snapshots match` |

⚠️★ **CI が実際に赤くなって見つかった**（PR #124 の mac check・2026-08-29）。
★ Windows は同じコミットで pass しており、⚠️ **race なので OS ではなくタイミングで割れる**。

## スコープ

### 含むもの
- 上記 2 行の属性の付け替えと、その検証

### 含まないもの
- ⚠️ **テストの中身を変えること**（★ CLAUDE.md 禁止事項「既存のテストを無断で削除しない」）
- ⚠️ 一時ファイルパスの設計変更（★ 二重登録が消えれば衝突も消える。⚠️ 消えなければ別途起票する）

## 受け入れ条件

- [ ] `--workspace` を **3 回連続**で緑（★ 発見時の実測は `--workspace` 全体で **1/2 の確率で失敗**）
- [ ] ゴールデン byte-equal（`replay_snapshot_goldens_byte_equal`）が緑のまま
- [ ] ⚠️ `HMM_VERSION` を動かしていないこと

## 関連

- `.steering/20260824-o1-macos-instrument/decisions.md` **判断 5**（一次記録・修正内容の特定）
- `.steering/20260825-o1-researcher-decisions/decisions.md` **判断 O1-7**（起票の決定）
