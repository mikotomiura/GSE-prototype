# タスクリスト

## 準備
- [x] ハンドオフ `.steering/_handoff/next-session-prompt-o1-macos-distribution.md` を読む
- [x] ⚠️ **メモを一次資料にせず**、2 つのゲートを macOS 実機で実際に走らせた
- [x] ★ メモとの食い違い（16/1 → 15/2、14/14 → 16/1）の**真因を実測で特定**した
- [x] ★ ブランチ差ではなく**環境差**であることを main でも測って確認した
- [x] `verify-before-claiming` Skill を読む

## 実装
- [x] ★ 同型の欠陥を**リポジトリ全体で走査**（17 箇所・6 ファイル）
- [x] `scripts/sync-session.sh` — ⚠️★ **O1 ガードの `exit 4` を復活**（本番コードの欠陥）
- [x] `scripts/sync_session_o1_guard_test.sh` — 7 箇所（★ テストが途中で死んでいた）
- [x] `scripts/check-o1-release-readiness.sh` — 2 箇所
- [x] `experiments/.../make-common-app-zip.sh` — 4 箇所
- [x] `experiments/.../prepare-subjects.sh` — 2 箇所（⚠️ 機械置換がコメントの意味を壊したので書き直した）
- [x] `experiments/.../run.sh` — 1 箇所
- [x] ★ `bom_crlf_ok` の BOM 検査を **BSD/GNU 両対応**にする（`od` の区切り幅に依存しない）
- [x] ⚠️★★ **陽性対照 `ctl3` が 1 バイトも壊せていなかった**のを直す（★ BOM 修正で露出した）
- [x] ★ 対照そのものの検査（`cmp` で「元と同一なら赤」）を足す
- [x] **新規** `scripts/check-shell-portability.sh`（★ 陽性/陰性対照つき）
- [x] ★ `check-o1-release-readiness.sh` から移植性ゲートを呼ぶ

## テスト（★ すべて macOS 実機で実測）
- [x] `sync_session_o1_guard_test.sh` が**最後まで走る** → **通過 10 / 失敗 0**
- [x] O1 セッション → **`exit 4`**（★ 壊れていた括弧内の理由まで出た）
- [x] 通常セッション → **`exit 2`**（★ 4 以外＝ガードを通り抜けた証拠）
- [x] `make-common-app-zip.sh --selftest` → **17/17**
- [x] `check-shell-portability.sh` → **5/0**
- [x] ⚠️★ ゲートの **3 状態**確認（正常=緑 / 違反を仕込む=赤 / 復元=緑・`cmp` で完全復元を確認）
- [x] `check-o1-release-readiness.sh` → **通過 17 / 未達 1**（★ 残るは「送信 timeout 未実測」のみ）
- [ ] ⚠️★★ **`sync-session.ps1` は未実行**（★ PowerShell がこの Mac に無い。Windows で 1 回走らせること）
- [ ] ⚠️ **Windows CI で赤が出ないこと**の確認（★ push 後）

## 検算ラン（§1-C・⚠️ ダミー設定・送信ゼロ）
- [x] `--mode o1 --tag v0.1.29 --config <ダミー>` を実行
- [x] ① dmg マウント＋署名 `valid on disk` / `satisfies its Designated Requirement`
- [x] ② 展開後も署名が生きている
- [x] ③ zip 展開後も**実行ビットが残る**
- [x] ④ `o1.mode` あり / **`g1.mode` 無し**（★ 排他）
- [x] ⑤ `初回セットアップ_mac.sh` の自己検査（★ スクリプトが 2 回実施）
- [x] ⑥ README が共通 4 語 ＋ O1 固有 5 語を保持（★ ドラフト表記も残存）
- [x] ⑦ Windows zip の中身（マーカー / `GSE_起動.bat` / README / `pubkey.txt` / `gse-submit.exe`）
- [x] ⑧ `__MACOSX` / `.DS_Store` の混入なし
- [x] ★ **`--mode o1` が G1 の zip を作り直していない**ことをタイムスタンプで確認
- [x] ⚠️ 送信先が **DRYRUN のダミー**であることを中身で確認（★ 配ってはいけない物証）
- [ ] ⚠️★★★ **ダミー入り zip の削除**（★ `rm` が環境ゲートで拒否された → 研究者に依頼）

## レビュー（★ 研究者の指示で実施・2026-08-29）
- [x] Codex（`/cross-review` 相当・`run-codex-review.sh main...HEAD`）→ 5 指摘
- [x] `code-reviewer` → HIGH 2 / MEDIUM 4 / LOW 4
- [x] `security-checker` → HIGH 3 / MEDIUM 3 / LOW 3

### ⚠️★★★ 3 者が一致した HIGH（★ 私も実測で再現した）
- [x] **走査 0 件で緑になる fail-open**（`git ls-files` の rc 未検査）
      → ⚠️ 非 git ディレクトリで **rc=0・5/5 緑**を実測。★ `exit 2` に分離し、
        **走査 0 本も赤**にし、**収集経路の対照**（既知ファイルが集まるか）を追加
- [x] 「違反あり」と「走査器が落ちた」が同じ `exit 1` に潰れていた → **1 と 2 に分離**

### ★ security-checker の HIGH
- [x] ⚠️★★ **`--selftest` が macOS で死んでいた**（`sed -i` の GNU 形式・17 箇所）
      → ★ 実測 **通過 18 / 失敗 17**。⚠️ そのなかに
        「**O1 ガードが空回りしていないことを示す唯一の変異試験**」が含まれていた
        ＝ **macOS では 1 度も実行されていなかった**。→ `sed_i` ヘルパで両対応にし、**37/0** へ
- [x] ✅ 文言が検査範囲より広く読める → 「★ この 1 型のみ」と件数を明示

### ★ code-reviewer の MEDIUM
- [x] ⚠️ **セクション 4 が構造上ぜったい赤にならない**（両分岐 `ok`）＋
      `${BASH}` は**上書きできない**（★ bash が起動時に自分のパスで上書きする）
      → `/bin/bash` と PATH 上の bash を**明示的に**走らせ、
        ⚠️ **3.x で再現しなければ赤**にする
- [x] `trap` が無く例外経路で一時ファイルが残る＋**理由の無い赤**になる → `trap` ＋ 途中終了の明示
- [x] ⚠️★ **shebang 分岐が 1 度も通っていなかった**（★ 収集 56 本は全部が拡張子由来）
      → インタプリタ **basename** 判定（`sh`/`bash`/`dash`/`ksh`/`zsh`/`ash`）にし、
        **対照を 1 本追加**（`#!/usr/bin/env sh` だけのファイル）
- [x] ⚠️★★ `docs/development-guidelines.md` の**反証された記述**を訂正
      （「bash 側は `bash -n` で十分堅牢」→ ★ **実測で `bash -n` は rc=0**）＋ 規約を明記

### ★ Codex の指摘
- [x] ⚠️★★ **CI に繋がっていない**（★ 当たり。実測で `ci.yml` も `run.sh` も呼んでいなかった）
      → `frontend-check` にステップ追加
- [x] `set -e` が後から足されると検査が黙って飛ぶ形 → `if` 条件部で受ける
- [x] 「shell portability」という名前より**検査範囲が狭い** → 冒頭に**見ていない型**を列挙
- [x] コメント・文字列も検出する → ★ **意図的**（`decisions.md` 判断 2）。却下
- [x] `sed` のリテラル CR が不安 → ★ **`cmp` の対照検査があるので silent pass しない**。却下

### ★ security-checker の MEDIUM / LOW
- [x] `grep -c` の `|| true` が **rc=2/127 まで飲んで fail-open** → 安全側（弾く）に倒す
- [x] 違反行の**全文出力**をやめる（★ 未追跡スクリプトの秘密が CI ログに出うる）
- [x] 走査結果に**追跡/未追跡の別**を出す
- [ ] ⚠️★★ **`sync-all.sh` がガードより前に O1 の生 NDJSON をコピーする**
      → ★ **起票（`decisions.md` 判断 6）**。⚠️ `.ps1` と対で直さないと片 OS だけ漏れる

## ドキュメント
- [x] `requirement.md` / `design.md` / `decisions.md`
- [ ] ★ 規約を `docs/development-guidelines.md` に載せるか（⚠️ 未判断・ゲートが機械で見張ってはいる）

## 完了処理
- [ ] git commit
- [ ] ⚠️ push は研究者が行う（★ 私からは環境ゲートで拒否される）

## ★ 次セッションへ（⚠️ 本セッションのスコープ外と確定したもの）
- [ ] ⚠️★★★ **本番 zip**（`Form_O1/o1_submit.json` を使う）
- [ ] ⚠️★★★ **macOS 実機の通し確認 §1-D 8 手順**（★ 研究者が操作）
- [ ] ⚠️★★★ **B-4「この時間帯の記録を消す」は全 OS でいまだ未実施**
- [ ] ⚠️★★★ **送信 timeout の実測**（★ ゲートに残る唯一の赤）
- [ ] ★ 配布フォルダ（短縮 URL 先）の中身と共有設定の確認
- [ ] ★ README の `【ドラフト・未承認】` 解除（⚠️ 実機で手順を踏んでから）
- [ ] ★ 「Apple Silicon のみ」を README に明記するか（⚠️ 研究者確認済: **Intel Mac の被験者はいない**）
