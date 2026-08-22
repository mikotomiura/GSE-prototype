# requirement — `IME_ACTIVE` を cloak 経路で復旧する (A)

- 日付: 2026-08-23
- ブランチ: `chore/ime-active-enumwindows-probe` の上に積む
- 引き継ぎ: `.steering/_handoff/next-session-prompt-ime-active-cloak-rewiring.md`
- 前提記録: `.steering/20260822-ime-active-rewiring/findings-enumwindows-probe.md` §14-16

## 背景

2026-08-22 の実測 (60 秒 × 8 回) で以下が確定している。**議論し直さない。**

1. Windows 11 の IME 候補 UI は `ShowWindow` ではなく **DWM の cloak/uncloak** で表示制御される。
2. 正しい `EVENT_OBJECT_IME_*` (0x8027-29) は **1 件も飛ばない**。`EnumWindows` / UIA / 0x8030 も 0。
3. → PR #109 (定数を 0x8017/0x8018 から正しい値へ修正) は **働いていた信号を消した**。
4. ただし旧実装も正しくない —— **クラス絞りが無く、無関係な窓の cloak も同じ `IME_ACTIVE` に流れていた**。
5. 無操作 24 秒で cloak は 0 件 (false positive 無し)。`IME` : 候補UI : ホストフレーム = 2 : 1 : 1。

## ゴール

`IME_ACTIVE` を `EVENT_OBJECT_CLOAKED`/`UNCLOAKED` ＋ **ウィンドウクラス絞り** で駆動し直し、
`ime_shadow` を「IME 候補ウィンドウ滞在」の正しい量として復活させる。

⚠️ **収集開始前にしかできない** (`preregistration.md §3.6` により収集開始後は記録仕様を変えられない)。

## 受け入れ条件 (すべて exit code / 実測ログで確認する)

- [ ] `cargo fmt --all -- --check` = 0
- [ ] `cargo test --workspace` = 0
- [ ] `cargo clippy --all-targets` = 0 (変更ファイルの警告 0 件)
- [ ] 既存ゴールデンが **byte-equal** (`gse-replay -- tests/fixtures/minimal.ndjson --snapshot ...`)
- [ ] `emit_schema` が `schema/current.json` と byte-equal
- [ ] `python scripts/check_schema_parity.py --dataset C:/gse-dataset` = 0
- [ ] **実起動ログで `ime_shadow` 行が実際に出る** (「実装した」ではなく「出た」)
- [ ] **無操作 60 秒で `ime_shadow` が 1 行も出ない** (false positive の回帰確認)
- [ ] `capabilities` の扱いを記録 (1 台でしか確認していないので `config_gated` 据え置きが安全)
- [ ] **pause 区間の割合**を実測して記録 (§3.2)
- [ ] `decisions.md` に (i) クラス絞り (ii) 2 周期の畳み込み (iii) A-2 の判断 を記録
- [ ] `code-reviewer` + `security-checker` を並列起動 → HIGH 対応
- [ ] `/cross-review` (パス限定。`findings-*.md` は外部へ渡さない)

## スコープ外 (混ぜない)

- v0.1.28 のリリース (Mac 側担当)
- ADR-014 の研究者判断 6 件
- `ime_dwell_med` の再解釈 (findings §13-15 に記録済み)
- **推論への配線 (段 3)** —— ADR-011 D4 により G1 判定後
- **A-2 (macOS `kCGWindowList` ポーリング) の実装** —— Mac セッション必須。本セッションは判断のみ

## 運用メモ

- /reimagine 適用: **No**
- 理由: 引き継ぎ §2 が設計を既に確定させており (cloak 駆動 + クラス絞り + resolver スレッド)、
  残る選択肢はクラス絞りと畳み込みの 2 点のみ。どちらも**実測で裁く**性質のもので、
  案を再生成しても実測なしには決まらない。→ 実測を優先する。
