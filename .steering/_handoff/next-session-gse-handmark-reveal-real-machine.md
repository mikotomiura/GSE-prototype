# 引き継ぎ —— 手跡の「ほかの窓をどける」の実機の確かめと、3 名の配る前の残り

> 作成: 2026-11-23（Mac のセッション）。このメモは入口で、一次ではない。一次は `.steering/20261123-handmark-reveal-count/`（requirement・design・decisions の判断 1〜6）・ADR-051 補訂（2026-11-23）・同意文書 `.steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md` の「配る前の条件」の表。

## 入口の文

Mac（12-09 4:00 以降）:
```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-handmark-reveal-real-machine.md を読んで、§1（Mac の実機）から進めて。
```

G-GEAR（Windows）:
```
GSE-prototype/.steering/_handoff/next-session-gse-handmark-reveal-real-machine.md を読んで、§2（Windows の実機）だけを行い、結果を収集して報告して。修正はしない。
```

## 0. ここまで（2026-11-23）

- 枝 `feature/handmark-reveal-count`（worktree `/Users/johnd/GSE-prototype-handmark-reveal`）。コードとテストまで。push と PR は `/finish-task` で研究者に確かめる。
- レビュー: 作業中の code-reviewer・security-checker（判断 6）と /cross-review（Claude ∥ Codex・判断 7）。HIGH は直した。残る穴は判断 6・7 の「採らなかったもの」。
- 入れたもの: トレイの「ほかの窓をどける」／「窓を戻す」（手跡の窓を出している間だけ）、`handmark_day.reveal_count`（その日にどけた回数・押した時刻は残さない）、区間の削除での回数の差の引き算、両 OS のどける・戻す、自動で戻す 4 つの契機（窓を閉じる・日の変わり目・終了・駆動スレッドが抜けたとき）。
- 手元で確かめたこと: macOS の lib のテスト 1400 件と全体、clippy、変異 13 個がすべて赤、schema の作り直し。Windows のファイルは、切り出した最小の crate を `cargo clippy --target x86_64-pc-windows-msvc` で型検査した（誤りを入れて赤になる陽性対照つき）。本体の Windows の CI は、GitHub Actions の 11 月の分数が尽きているので 12-01 以降に走る。
- 実機では一度も動かしていない（判断 5）。

## 注意（本人の段 1）

- 12-08 までは、この版を段 1 のモード（`GSE_S1_MODE=1` か配布の印）でこの Mac で動かさない。理由は 2 つある。
  1. どけると本人の gse-next の窓（背景の層・帯）も隠れ、後期の表示と表示の時間の記録を乱す。
  2. 状態ファイル `~/.gse/handmark_day_state.json` は版をまたいで 1 つで、`DayRecord` は `deny_unknown_fields`。この版が `reveal_count` を書くと、本人の gse-next（v0.1.42）がそれを壊れた状態ファイルとして扱う。
- 12-09 以降に確かめるときも、本人の段 1 の記録を止めるか、3 名の版に入れ替えるかを先に研究者に聞く（`next-session-gse-stage1-self-late-check-and-run2.md` §3 の最後の項目と同じ問い）。

## 1. Mac の実機（12-09 4:00 以降）

画面の確かめは memory `macos-app-visual-check-workflow` の作法で行う。トレイの後足しの項目は AX から押せない（memory `tauri-tray-inserted-items-invisible-to-ax`）ので、押すのは研究者に頼み、私はログと記録を見る。同じ名前のプロセスが並んでいる間は AX で押さない（memory `jxa-same-name-process-ax-crosstalk`）。

確かめること:
1. 手跡を出している日だけ、トレイに「ほかの窓をどける」が「やめる」の上に出る。出さない日・「やめる」の後は出ない。
2. 押すと、押した時に見えていたアプリだけが隠れ、背景の層と帯は見えたまま残る。前面のアプリも隠れる。Dock に出ないが窓を出しているアプリ（メニューバーの常駐アプリの設定窓など）も隠れる。項目は「窓を戻す」に変わる。
3. 「窓を戻す」で、覚えたアプリだけが戻る。もともと隠していたアプリは隠れたまま。前面だったアプリが前面に戻るか（macOS 14 以降の協調的な切り替えで戻らないことがある。戻らなければ記録する）。
4. 自分を前面に出したときに、GSE の他の窓（main 窓など）が前に出てこないか。
5. 全画面のアプリの中で押したとき（試作では未確かめ）。
6. どけたまま「やめる」・トレイの終了で、窓が戻る。終了のとき `gse-app.log` に `returning windows was queued to the main thread` が出たら、その後に実際に戻ったかを見る。
7. 記録: 次の 5 分ごとの行の `reveal_count` が押した回数（戻すのは数えない）。押した直後に `handmark_day` の行が出ない。一時停止中に押しても増えない。区間の削除で、区間の中の回数が後の行から引かれる。
8. `gse-app.log` に、アプリの名前・pid・窓の情報が出ていない。

## 2. Windows の実機（G-GEAR・収集だけ）

memory `windows-agent-collection-only` の作法: G-GEAR 側の Claude Code には収集だけを頼み、修正は Mac の文脈で行う。陽性対照（どけていない状態の同じ観測）を必ず採らせる。

確かめること:
1. トレイの項目の出方と並び（カーソル・クリック・ほかの窓をどける・やめる・終了）。
2. 押すと、見えていた他のアプリの窓が最小化され、背景の層・帯・デスクトップのアイコンは見えたまま。タスクバーは消えない。
3. 最大化していた窓が、戻すと最大化のまま戻る。重なりの順がおおむね元に近い（非同期なので保証はしない）。
4. 管理者として動く窓（管理者で開いたコマンドプロンプトなど）は最小化されずに残り、戻すときにも触られない。
5. どけている間に本人が自分で戻した窓・閉じた窓は、「窓を戻す」で触られない。
6. 別の仮想デスクトップの窓は触られない。
7. どけてすぐ（1〜2 秒以内に）「窓を戻す」を押したとき、応答の遅いアプリ（重い処理中のアプリ）があるときに、最小化されたまま残る窓が無いか（`ShowWindowAsync` が非同期なので、戻しが最小化より先に走りうる・判断 7）。残ったら、戻す側で「まだ最小化されていない窓を一覧に残して後で戻す」形を検討する（無条件に `SW_RESTORE` を送ると最大化が解けるので避ける）。
8. 記録は §1 の 7 と同じ。

## 3. 3 名の配る前の残り（このタスクの外）

同意文書の「配る前の条件」の表で残っているもの（2026-11-23 の時点）:
- 条件 4（どけた回数）: このタスクで入れた。実機の確かめ（§1・§2）の後に満たす。
- 条件 6: `src/components/S1ConsentPanel.tsx` の取り消しの文を §4-2 に合わせる（今の文は「記録そのものはこれまでどおり続きます」）。
- 条件 10: トレイの場所（macOS はメニューバー・Windows は通知領域）の書き方を両 OS の実機で確かめる。
- 条件 11: 終了後の説明の文。
- 条件 8・9: 事前登録の最長の期間と頻度の数値（事前登録のタスク `next-session-gse-stage1-prereg-values-and-stop-rule.md`）。
- 条件 13: 研究者が同意文書を読み直して印を入れ直し、ADR-055 を Accepted にする。
- このタスクのレビューから: 異常終了ではどけた窓が戻らない（本人が Dock・タスクバーから戻せる）。参加者向けの案内（`docs/participant-setup-guide.md` §7）に 1 行足すかを、配布のタスクで決める（判断 6 の採らなかったもの）。
- ほかに: 受領台帳（`Form_O1/GSE_O1_Ledger.gs`）の段 1 の扱い、管理シートの終了判定の列、同意フォームの Apps Script への配備と段 1 用の配布フォルダ、PR #425（配布の門の手跡の検査・12-01 以降に CI を走らせ直す）。

## 4. gse-dataset の schema の写し

`handmark_day` に `reveal_count` が増えたので、gse-dataset の `schema/current.json` を同じ形に更新する PR が要る（Q3 の 7 択のときの gse-dataset PR #10 と同じ）。`/finish-task` の schema parity の検査で食い違いが出たら、こちらを先に行う。ローカルの gse-dataset は `fetch` してから比べる（memory `schema-parity-stale-local-dataset`）。
