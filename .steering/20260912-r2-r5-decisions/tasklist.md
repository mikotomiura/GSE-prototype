# タスクリスト: R-2〜R-5

## Phase 0: grill (✅ 完了)

- [x] 一次資料 3 本を読む (handoff を一次資料にしない)
- [x] 実測 6 件で判断分岐を潰す (design.md の表)
- [x] 研究者裁定を 7 件記録 (decisions.md)

## Phase 1: PR-B — R-3 ＋ R-4 (`fix/msrv-proof-and-loud-redact-test`)

### R-3
- [x] `cd src-tauri && cargo +1.87 check --all-targets --features package` を実測
- [x] 結果を `Cargo.toml` の `rust-version` 注記へ反映 (⚠️ Windows cfg 集合のみの実証と明記)
- [x] ⚠️ exit != 0 なら真の下限へ `rust-version` を修正し根拠を記録

### R-4
- [x] `lib.rs:5260` の `else { return; }` → `else { panic!(..) }`
- [x] `ci.yml` `check` job に env 前提の検査 step (⚠️ 値は出さない・`if [ -n .. ]`。★ 判断 10 で `${VAR:+set}` は却下)
- [x] `cargo test --features package --workspace` が exit 0
- [x] 変異テスト: `return` に戻すと検査 step が意味を失うことを実証

### 共通
- [x] `cargo clippy --all-targets --features package -- -D warnings` が exit 0
- [x] ゴールデン `gse-replay --snapshot` が byte-equal
- [ ] code-reviewer + security-checker を**並列**起動
- [ ] `/cross-review` (⚠️ **ラッパーを先に試す** = R-5 の検証)
- [ ] PR 作成 → CI 緑 → main へマージ

## Phase 2: PR-A — R-2 (`chore/pin-rust-toolchain`)

- [ ] repo 直下に `rust-toolchain.toml` (channel 1.94.1 / components・⚠️ targets は書かない)
- [ ] `ci.yml` 3 箇所に注記 (⚠️ action は残す)
- [ ] `rustup show active-toolchain` が `overridden by` を返すことを確認
- [ ] ゴールデン byte-equal / clippy exit 0
- [ ] code-reviewer + security-checker を並列起動
- [ ] PR 作成 → ⚠️ **初回 CI で必ず見る**: ディスクガードの `free before:` / `wiped=` 行、
      clippy step の所要時間、toolchain DL の有無
- [ ] main へマージ → main run が success

## Phase 3: 後片付け

- [x] ⚠️ handoff `next-session-mac-clippy-and-ci-gate.md` §8.6 の失効行を訂正 (handoff §6)
- [ ] `.steering/_handoff/next-session-r2-r5-decisions.md` を「済」に更新 or 削除
- [ ] R-5 の結論を記録 (2 回連続成功なら閉じる)
- [ ] `/finish-task`
