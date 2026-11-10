# 引き継ぎ —— 手跡を macOS で main に入れる（PR 0 の残り・PR 1・PR 2〜7）

> 作成: 2026-11-08（Mac のセッション・`.steering/20261108-handmark-to-main-plan/`）。研究者の選択で、Mac で進める 3 本の引き継ぎを 1 本の入口にまとめた（判断 10）。作業と PR は別々のまま。このメモは入口で、一次ではない。決定の一次は ADR-051 と ADR-050、計画の一次はそのタスクの `decisions.md`（判断 P・1・1b・2・3・5・6b）。Windows 版は別の引き継ぎ `next-session-gse-handmark-windows.md`。

## 入口の文

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-handmark-mac.md を読んで、手跡の <A: PR 1 / B: PR 0 の残り / C: PR n> を /start-task から始めて。
```

## 順番

1. **A. PR 1（後期を始められる最小の切れ端）** が先。後期を始めるのに要るのはこれだけ。
2. **B. PR 0 の残り（glossary・理論 §1.4・文献）** は PR 1 を待たない。PR 1 と並行でも前後でもよい。文書だけ。
3. **C. PR 2〜7** は PR 1 の後。2・3・6 は順を入れ替えてよい。4 は 3 の後、5 は 3 の後。

1 つのセッションでは 1 つの節だけを扱う。A と B を 1 本の PR に混ぜない（確かめ方が違う）。C は、始めるときに ADR-051 D7 と PR 1 の記録を読み直してから、その PR だけの引き継ぎを書き起こす。

## 前提（どの節にも共通）

- PR 0（ADR-050・ADR-051・README・地図 R10・この引き継ぎ）が main に入っていること。入っていなければ、PR #399（枝 `docs/handmark-to-main-plan`）の状態を研究者に聞く。
- 枝は `git fetch` してから origin/main で切り、worktree を作る（memory: parallel-sessions-share-checkout）。

## 守ること（どの節にも共通）

- UI を変える PR は、画面を見るまで完了にしない（memory: ui-changes-need-eyes）。
- 研究者本人の gse-next（`/Users/johnd/GSE-S1-self/S1_実施用_macOS/gse-next.app`）が動いている間は、同じ名前のプロセスに AX で押さない（memory: jxa-same-name-process-ax-crosstalk）。
- 本人の段 1 の記録（O1・段 1 の NDJSON）を開かない。Codex に送らない。
- 完了時は code-reviewer（コードの PR は security-checker も）と /cross-review（Codex を加える）。
- push・PR は研究者に確かめてから。docs だけの PR は `[skip ci]` にできる（memory: feedback-push-only-no-pr-during-runs）。
- この Mac の空きは 2026-11-08 に約 12 GiB で、self-hosted の macOS の検査が止まる 8 GiB に近い。CI を起こす前に空きを確かめる。

---

## A. PR 1: 段 1 の後期を始められる最小の切れ端（ADR-051 D7）

### 何を入れるか（ADR-051 D4・D5・D2 の一部）

1. **割付の表を読む処理**: 研究者が配布前に作る人ごとの表を読む。中身は、前期の長さ（後期の開始日）と後期の日ごとの「あり・なし」。表の SHA-256 を検める。
   - 置き場所と形式は、このタスクで決める。候補は `~/.gse/`、または配布物のフォルダの `s1.mode` の隣。
   - 研究者が表を作る小さな道具（種から表と SHA-256 を出す）も、このタスクか別の PR で用意する。
2. **日ごとの行種**: 割付の上の状態・割付の上の開始日・初めて表示した日・出ていた時間・見えていた時間・切った／戻した時刻・表の SHA-256・描画の種・出せなかった理由。
   - `schema_dto.rs` → `emit_schema` → `schema/current.json`。gse-dataset との parity（`/finish-task` Step 3）を通す。
   - `capabilities.rs` には、段 1 のときだけ `config_gated` として宣言する（既存の 4 行種と同じ作法）。
   - 区間の削除（`redaction.rs`）で、この行をどう扱うかを決める。
3. **入口の門**:
   - 段 1 のモード（`s1.rs` の判定: 配布形は印 `s1.mode`、開発・検証は `GSE_S1_MODE=1`）で、かつ表があり SHA-256 が合うときだけ動く。
   - それ以外では、窓も作らず tap も張らない。fail-closed で、出せない理由を日ごとの行に書く。
4. **状態の純関数（決定性）**:
   - ライブの契約と再生の契約に分ける（ADR-051 D5）。状態は `f(打鍵の時刻の列, ポインタの入力, 種, t)` で決め、固定の時間刻みで進める。再生ではポインタの口に `pointer_bin` からの近似を入れる。PR 1 の入力は打鍵だけで、ポインタの口は空でよい。
   - 描画の回数は状態に影響させない。
   - 同じ入力から同じ状態がバイト単位で出ることを、性質のテストで縛る。種を変えれば変わることも確かめる（陰性の対照）。
   - 試作の `handmark_wind.rs` を写して、この形に直す。
5. **背景の層（macOS・打鍵だけ）**:
   - 試作の `handmark_stage_spike.rs` と `HandmarkStage.tsx` の描画を写す。
   - 窓は、状態を描くだけにする。
   - `lib.rs` の受信ループに、押下の時刻を渡す 1 か所を足す。試作は `event.is_press && !recording::is_paused()` のときに渡していた。
6. **切る／戻す**: トレイの項目。その日のうちだけ続き、翌日は割付に戻る。時刻を日ごとの行に書く。
7. **記録の検査**:
   - 試作の `handmark_stage_guard.rs` の考え方（語の検査と陽性対照）を写す。
   - 手跡が動いても、日ごとの行以外の行が 1 行も増えないことをテストする。
   - ADR-050 D3 の表のうち、打鍵だけの PR 1 に当たる行を先に入れる。

大きすぎると分かったら、1a（OS 非依存: 1〜4・7）と 1b（5・6・配線）に割り、続けて出す（判断 6b）。

### 入れないもの（PR 1 では）

帯（PR 2）・カーソルとクリック（PR 3）・ホイール（PR 5）・「背景を見る」（PR 6）・日の問いの項目（PR 7）。小面と計測の仕掛けは、どの PR にも入れない。

### 試作の在り処

- worktree `/Users/johnd/GSE-prototype-handmark-stage`（枝 `spike/handmark-stage`・351f94e5）。読むだけで、rebase しない。
- 記録: `.steering/20261016-handmark-stage-spike/`・`20261021-handmark-stage-pointer/`・`20261030-handmark-edge-strip-impl/`（その枝の中）。
- 衝突の見込み: `lib.rs`（main 側 +1413 行）と `tray.rs`。main の `tray.rs` には、招待の項目の差し込み（`menu.insert(item, 2)`）と `request_quit` がある。配線は main に合わせて書き直す。

### 規約

`architecture-rules`・`rust-standards`・`typescript-standards`・`data-privacy`（新しい行種）。OS の API は `analysis/` に置かない。

### このタスクで決めること（研究者に 1 問ずつ）

1. 表の置き場所と形式。研究者が表を作る道具を、この PR に入れるか。
2. 日ごとの行の名前と、区間の削除での扱い。
3. 1a と 1b に割るか。
4. 日ごとの行を書き出す時点（起動・終了・日付の変わり目・一定の間隔）と、同じ日の行が複数あるときの合わせ方。落ちても失われないこと、二重に数えないことをテストで縛る（ADR-051 D4）。
5. 入口の門を検め直す契機（起動・日付の変わり目・一定の間隔）。表を消した後に窓と tap が壊れることをテストで縛る（ADR-051 D5）。
6. 同じ日に再起動したときの、切った状態の保ち方（ADR-051 D2）。切る操作のときにすぐ書き残し、起動では状態を戻してから窓と tap を作る。書き残せなければ出さない側に倒す。書き残しに失敗 → 強制終了 → 同じ日に起動し直しても出さないことを、障害を注入するテストで縛る（受け入れ条件）。

---

## B. PR 0 の残り: glossary「手跡」・理論 §1.4・文献 [P485]〜[P554] を main へ

ADR-048 Migration 2・ADR-051 Migration 1 の残り。コードは変えない。

### 何をするか

1. 枝 `docs/tangibility-design`（worktree `/Users/johnd/GSE-prototype-tangibility`）の `docs/glossary.md` の「手跡」の項を、main の `docs/glossary.md` に持ち込む。
   - ADR-048 D2 を反映する。許すのは行為の性質だけで、系の判断は許した以上に読めないこと。
   - ADR-050・ADR-051 を参照する。
2. 枝の `docs/theory/measurement-terminating-practice-portraiture.md` の §1.4 と、関わる節（測り方・反証・限界）を main の同じ文書に持ち込む。
   - main の版との差分を先に見る。枝は main より古い。
   - ADR-048 D2 を反映する。
3. 文献: 枝が足した [P485]〜[P554] のうち、持ち込む本文が引くものを main の `docs/references.md` に同じ番号で足す（`citation-ssot`）。
   - 2026-11-08 の時点で、main の P は [P484] で止まっている。V は、枝と main で同じ行だった（V290・V295・V298 で照合した）。
   - 足す前に、main で P485 以降が使われていないかを grep で確かめ直す。DOI の重なりも確かめる（名前空間を横断する重複の節）。
   - 使わない番号を飛ばすか、全部を足すかは研究者に聞く。番号は恒久 ID なので、飛ばしても後で足せる。
4. 枝の `docs/adr/ADR-040-handmark-input-not-recorded.md` の冒頭に「main で ADR-050 に振り直した」という注を足すかを、研究者に聞く。枝へのコミットになる。

### 規約

`citation-ssot`・`verify-before-claiming`（長い一次を 1 節だけ読んで代表させない）。`docs/glossary.md` の禁止用語（「不便益 HCI である」「段階的介入」など）に当たらないかを見る。

---

## C. PR 2〜7 と条件 (b) の実測（一覧）

PR 1 が入るまで、ここに書いた前提は動きうる。

| PR | 中身 | 前提 | 確かめ方 | 材料（試作の枝 `spike/handmark-stage`） |
|---|---|---|---|---|
| 2 帯 | 下の縁の帯（14pt・非アクティブの NSPanel・Dock の上端に沿う・全画面では画面の下端）と、見えていた時間の計り方（覆われ方の判定）。描画は入力があれば 30 回／秒、無ければ 10 回／秒で、完全に覆われたら止める | PR 1 | 画面を見る・CPU（1 コアの割合を累積の秒の差で測る。memory: macos-top-l2-undercounts-cpu） | `handmark_edge_strip.rs`・`HandmarkEdgeStrip.tsx`・`.steering/20261030-handmark-edge-strip-impl/`・tangibility 枝の `20261029-handmark-edge-strip-design/` 判断 3〜7 |
| 3 カーソルとクリック | 16ms ごとに一点を読む（権限なし）・左だけ・状態の関数への入力・`pointer_bin` からの近似の写像（漏れの確かめ用）。ADR-050 D2〜D4 の検査を、ポインタの行まで広げる | PR 1 | `cargo test`・`node --test`（`handmark-stage-trace.test.mjs` の 9 件を写す）・画面を見る | `handmark_stage_pointer.rs`・`input/handmark_pointer{,_macos}.rs`・`handmarkStageTrace.ts`・ADR-050 補訂 1 の項目 1・2・6・8 |
| 4 机上の道具 | 記録から描き直し、予測器 A（速さ・リズム・止まり＋`pointer_bin`）と B（A＋見た目）の AUC の差を出す。許す情報にポインタの量を含める・1 日ずつ抜く交差検証・日のブロックのブートストラップ両側 90%・3 値・δ = 0.05・天井（A の AUC の下限が 1−δ を超えれば「満たす（天井）」）・2 つの対象は両方満たすときだけ満たす・主は前期を含む全部の日、感度分析は実際に表示した「あり」の日で、感度分析が満たさなければ全体も満たさない・クラスが欠ければ判定不能・前期の日の種の手順・入れ子の引き直しを比べる（ADR-051 D3）。見た目の特徴は、画素からと状態からの両方を作って比べる（ADR-051 決めずに残すもの 2）。本人の前期の記録で、区間の幅を測る | PR 1・PR 3 | 合成の入力で既知の漏れを入れた陽性対照（人の記録を使わない） | 新規。`reproducibility-discipline`（`experiments/`・seed・HMM_VERSION）。計算が重ければ G-GEAR（11 月はふさがっている）か職場の PC |
| 5 条件 (b) の実測 → ホイール | ① 実測: PR 3 が入った main のビルドで、ホイールの tap を開発用の設定で入れた日と切った日を比べ、打鍵の tap の失効の数を見る。入れ切りと一時停止を繰り返して tap が残らないことも確かめる。② 通れば: ホイール専用の聞くだけの tap（入力監視の許可が要る）を入れ、ADR-050 を Accepted（macOS の射程）にする | PR 3 | 失効の数・tap の数 | `input/handmark_wheel_macos.rs`・ADR-050 補訂 1 の項目 3・4 |
| 6 「背景を見る」 | 他のアプリをどける・戻す（押したときに見えていたアプリだけを戻す）。全画面の中では、最大 1 秒待って前面に出られなければ隠さずやめる。終了のときに戻す。どけた回数の行と schema・同意の文の改訂。macOS 14 より前の `activate()` の分岐 | PR 1（帯の後が自然） | 画面を見る・同意の文の差分を研究者が読む | `handmark_reveal.rs`・tangibility 枝の `20261023-handmark-window-boundary/` 判断 5 と `20261029` 判断 6・7・論点 6・7 |
| 7 日の問いの項目 | 手跡ありの日だけ、`day_question` のカードに同期・共存の項目を足す（`items_version` を上げる）。契機と回数は変えない | 文献のラウンド（尺度の文）・PR 1 | `cargo test`（`probe_arbiter.rs` の既存のテストの形） | `analysis/probe_arbiter.rs` の `DayQuestion`・`logger.rs` の `DayQuestionRow`・`src/components/DayQuestionCard.tsx` |

- 後期の途中で PR が足されたら、その日からの刺激の違いが日ごとの行とビルドの版で分かるようにする（ADR-051 Consequences）。

### 条件 (b) の実測で守ること

- 本人の段 1 の Mac で、別のビルドを並べて走らせない。記録が混ざり、AX が取り違える（memory: jxa-same-name-process-ax-crosstalk）。
- 実測の時期と機械は、始める前に研究者に AskUserQuestion で確かめる。本人の段 1 の記録に影響しうる。実測の日の記録は探索として扱う。
