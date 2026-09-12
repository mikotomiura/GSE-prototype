# `IME_ACTIVE` の Ordering を共通-2 の対に閉じる

## 背景

★ mac セッション (PR #190) が `IME_OPEN` の Ordering を閉じる過程で、
⚠️ **`IME_ACTIVE` が 7 箇所 `Relaxed` のまま**であることを実測し、起票した
(`20260911-outcome-arbitration-and-o1-preflight/blockers.md` 起票 10 /
 `20260912-mac-clippy-green-and-ci-gate/decisions.md` §8.4)。

⚠️★★★ **mac では直せない。** ★ 残っている経路は
`hook_windows.rs` / `ime_windows.rs` / `lib.rs` の Windows 側で、
**mac からは 1 行もコンパイルできない**ため「Windows 実機/CI と対で別 PR」と明示されている。

★ 規則の SSOT は `hook-constraints` Skill **共通-2**:

> `IME_OPEN` / `IME_ACTIVE`: Analysis スレッドとの可視性保証が必要
> → store は **Release**、load は **Acquire**

⚠️★★★ **`LAST_KEY_MS` のような「近似値で十分」な変数とは別扱い**であることが、
同じ表の中に明記されている (★ あちらは `Relaxed` で正しい)。

## ゴール

`IME_ACTIVE` の store / load を **Release / Acquire の対**に閉じ、
⚠️ **片側だけ直して「直したつもりで何も保証していない」状態を作らない**
(★ これは mac が 判断 5b で一度踏んで撤回した罠である ——
 **store だけ Release にしても読み手が `Relaxed` なら happens-before は成立しない**)。

## スコープ

### 含むもの
- ★ 実測した **7 箇所**:

| # | 箇所 | 現状 | 備考 |
|---|---|---|---|
| 1 | `input/hook.rs:32` (`is_ime_active()`) | `load(Relaxed)` | ★ OS 非依存のアクセサ |
| 2 | `input/hook_windows.rs:212` | `store(true, Relaxed)` | |
| 3 | `input/hook_windows.rs:253` | `store(false, Relaxed)` | |
| 4 | `input/hook_windows.rs:603` | `load(Relaxed)` | ⚠️★★★ **フックコールバック内** |
| 5 | `input/ime_windows.rs:124` | `store(false, Relaxed)` | |
| 6 | `input/ime_windows.rs:574` | `load(Relaxed)` | |
| 7 | `lib.rs:3583` | `store(false, Relaxed)` | |

- ★ **再発を機械で止める回帰テスト** (⚠️ mac は実測しただけで、規則を守る仕掛けは無い)

### 含まないもの
- ⚠️ `LAST_KEY_MS` / `CONSECUTIVE_TAP_FAILURES` 等、**共通-2 が `Relaxed` で正しいと明記**しているもの
- ⚠️ 起票 10① (`macos_vk_to_vk` の素通しアーム) —— ★ mac が 判断 6 で
  「VK 分布が変わりうるので混ぜない」と裁定済み (研究者裁定 S-1)
- ⚠️ 研究者判断 R-2 / R-3 / R-4 / R-5 (★ 引き継ぎに残したまま)

## 受け入れ条件

- [ ] `IME_ACTIVE` を含む行に `Ordering::Relaxed` が **0 件** (コメント行を除く)
- [ ] `IME_OPEN` も同様に 0 件 (★ mac の PR #190 の成果を固定する)
- [ ] 新しい回帰テストが**変異させると赤になる**ことを実測する
      (⚠️ 「足したら緑だった」は検査が効いている証拠にならない)
- [ ] `cargo clippy --all-targets --features package -- -D warnings` が exit 0 (★ CI と同条件)
- [ ] `cargo test --workspace` が **654 → 655 passed / 0 failed**
- [ ] ゴールデン 6 fixture が全一致 / `emit_schema` が byte-equal
- [ ] `cargo fmt --check`

## 関連ドキュメント

- `.claude/skills/hook-constraints/SKILL.md` 共通-1 (コールバック内の禁止操作) / **共通-2**
- `.steering/20260912-mac-clippy-green-and-ci-gate/decisions.md` 判断 5 / **5b** / §8.4
- `.steering/20260911-outcome-arbitration-and-o1-preflight/blockers.md` 起票 10

## 運用メモ
- /reimagine 適用: **No**
- 理由: ★ 規則 (共通-2) に照らして**正誤が決まる**ので設計上の争点が無い
  (⚠️ mac が裁定 S-1 で採ったのと同じ理由)。
