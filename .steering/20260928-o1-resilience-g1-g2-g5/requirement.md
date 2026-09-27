# o1-resilience-g1-g2-g5

## 背景

O1（普段の作業の長期記録）の配布タグ `v0.1.37` には、耐障害性の穴が 3 つ残っている
（調査: `.steering/20260927-g1-o1-release-and-o1-resilience/decisions.md` の「T2 の調査」節）。

- **G-1**: 自動起動が無い。再起動後にアプリを開き忘れると、その日から何も記録されない。
  いまは受領台帳の「5 日途絶」で後から気づけるだけ。
- **G-2**: 送信（reconcile）は起動時と日次ローテート時にしか走らない。回線断で失敗した `.age` は次のきっかけまで残る。
- **G-5**: 32 MB を超える `.age` は受け口が `too large`（HTTP 200 + `ok:false`）で拒否する。
  クライアントはそれを知らないまま、起動とローテートのたびに同じファイルを再送し続ける。研究者にも被験者にも伝わらない。

研究者の指示（2026-09-28）:「O1 に関しての保留である G-1〜G-5 などは具体的に修正しましょう」。
`v0.1.37` はまだ誰にも配っていない（2026-09-28・研究者回答）。

## ゴール

G-1 / G-2 / G-5 を O1 モードに限って実装し、O1 用の新タグ `v0.1.38` で配布物を作り直す。

## スコープ

### 含むもの
- G-5: O1 の `.age` が 32 MB を超えたら送信をやめて隔離フォルダへ移し、applog に記録する。送信前の検査と、受け口の `too large` 応答の両方で行う。データは消さない。
- G-2: O1 モードで 6 時間ごとに収束器を回す。新しい `ReconcileReason::O1Periodic` を足し、フロントの数値契約（`App.tsx`）も合わせる。
- G-1: `tauri-plugin-autostart` を使い、O1 モードの初回起動で 1 回だけ自動起動を登録する。以後は登録し直さない。
  - 実装より先に Mac の小実験で確かめる: LaunchAgent で起動したときに入力監視（TCC）の許可が保たれるか／NDJSON が `gse_o1_*` で出るか／`o1_mode` が meta に立つか。
  - LaunchAgent が駄目なら、ログイン項目（AppleScript）方式を同じ実験で測る。それも駄目なら Mac は見送り、Windows だけ入れる。
- 同意文書・README に入れる文面案（自動起動の告知と解除手順）。**研究者が承認してから**タグを打つ。
- 版上げ → タグ `v0.1.38`（push は研究者承認後）→ Release の中身を確かめる → `make-common-app-zip.sh --mode o1` → `docs/o1-distribution-tag.md` に追記 → Drive の差し替えは研究者が行い、こちらはバイト数を照合する。

### 含まないもの
- G1 の配布物（`v0.1.36` で凍結・ADR-034 D3）。G1 の挙動を変えない。
- GAS の `doPost` の変更（受け口は変えない方針）。
- 同意文書の「未了」項目（6 択 ESM 追補を採るかどうか）。
- G-3（スリープをまたいだ確認）は研究者の手順として渡すだけ。G-4（`extract.py`）は変えない。
- 送信見送りになった `.age` を分割して送ること。

## 受け入れ条件

- [ ] G-5: 32 MB を超える `.age` は uploader が呼ばれずに隔離フォルダへ移ることをテストで示す（ぴったり 32 MB は送る）。受け口の `too large` 応答でも隔離されることをテストで示す。隔離したものは以後の再送対象に入らない。どちらも変異検査で赤を確認する。
- [ ] G-2: O1 のときだけ 6 時間周期の reconcile が起動することをテストで示す（判定関数）。`ReconcileReason::O1Periodic` がフロントの数値契約と一致する。
- [ ] G-1: 初回だけ登録し、2 回目は登録しないこと、O1 以外では登録しないことを判定関数のテストで示す。Mac 実機の小実験の結果を記録する。
- [ ] `cargo test --workspace --features package`・fmt・clippy `-D warnings`・tsc が緑。CI（Windows / macOS）が緑。
- [ ] `/finish-task` のレビュー（code-reviewer・security-checker・`/cross-review`）を通す。
- [ ] 文面案を研究者が承認する → タグ `v0.1.38` → Release と zip を確かめ、`docs/o1-distribution-tag.md` に記録する。

## 関連ドキュメント

- `.steering/_handoff/next-session-o1-resilience-g1-g2-g5.md`
- `.steering/20260927-g1-o1-release-and-o1-resilience/decisions.md`
- `docs/o1-distribution-tag.md`
- `docs/glossary.md`（O1 自動起動 / O1 定期再送 / 送信見送り（32 MB 超））

## 運用メモ
- /reimagine 適用: No
- 理由: 方式は grill で研究者が選んだ（プラグイン・初回のみ ON／6 時間・新しい Reason／隔離）。代案の比較は decisions.md に残してある。Mac の小実験で方式を切り替える分岐も決めてある。
