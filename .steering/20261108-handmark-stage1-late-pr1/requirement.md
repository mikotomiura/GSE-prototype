# handmark-stage1-late-pr1 —— 段 1 の後期を始められる最小の切れ端（ADR-051 D7 の PR 1）

## 背景

ADR-051（2026-11-08 Accepted）は、段 1 の後期に手跡を日ごとの無作為で出す形を決めた。D7 の PR 1 は、後期を始めるのに要る最小の切れ端（割付の表・日ごとの行・入口の門・状態の純関数・背景の層・切る／戻す・記録の検査）である。引き継ぎは `.steering/_handoff/next-session-gse-handmark-mac.md`（`docs/handmark-to-main-plan` 枝）の節 A。

## ゴール

段 1 のモードで、割付の表と SHA-256 がそろったときだけ、macOS で打鍵だけを入力にした手跡の背景の層が日ごとの割付どおりに出て、日ごとの行（`handmark_day`）が記録される。それ以外では窓も tap も作らない。

## スコープ

研究者の選択で 2 本に割る（判断 1）。

### 1a（OS 非依存・先に出す）
- 割付の表（`handmark_assignment.json`）と `.sha256` の読み込み・検め。表を作る bin `gse-handmark-table`
- 日ごとの行 `handmark_day` の型・`schema_dto.rs`・`emit_schema`・`capabilities.rs`（段 1 のときだけ `config_gated`）・`redaction.rs`（切った／戻した時刻だけ消す）
- 日の状態ファイル `~/.gse/handmark_day_state.json`（表示の量の累計・切った状態）と、切ったときの印 `handmark_off_<日>`
- 入口の門（段 1 のモード ∧ 表 ∧ SHA-256 一致・起動・日付の変わり目・60 秒ごとに検め直す）
- 状態の純関数（打鍵の時刻の列・ポインタの口（空）・種・時刻 → 状態・固定の時間刻み）と性質のテスト（同じ入力で同じ状態・種を変えれば変わる）
- 記録の検査（手跡が動いても `handmark_day` 以外の行が増えない・語の検査と陽性対照）

### 1b（macOS・1a の後）
- 背景の層の窓と描画（`HandmarkStage.tsx` の写し）・`lib.rs` の受信ループからの押下の時刻・トレイの切る／戻す・配線
- 画面を見て確かめる

### 含まないもの
帯（PR 2）・カーソルとクリック（PR 3）・ホイール（PR 5）・「背景を見る」（PR 6）・日の問いの項目（PR 7）・小面と計測の仕掛け。

## 受け入れ条件（1a）

- [ ] 表が無い・壊れている・SHA-256 が合わない・段 1 のモードでない、のどれでも門が閉じ、理由が `handmark_day` に書かれる
- [ ] 門を開いた後に表を消すと、次の検め直しで閉じる（テスト）
- [ ] 同じ入力から状態がバイト単位で同じ・種を変えると変わる（性質のテスト）
- [ ] 同じ日の再起動で表示の量が 0 に戻らない・最後の行を採れば二重に数えない（テスト）
- [ ] 切る操作の書き残しに失敗 → 強制終了 → 同じ日に起動し直しても出さない（障害を注入するテスト）
- [ ] 手跡が動いても `handmark_day` 以外の行が 1 行も増えない（テスト）
- [ ] schema の parity（gse-dataset）を通す
- [ ] code-reviewer・security-checker・/cross-review（Codex を加える）

## 関連ドキュメント

- docs/adr/ADR-051-handmark-in-stage1-late-period.md（D2・D4・D5・D7）・ADR-050・ADR-048
- 試作: worktree `/Users/johnd/GSE-prototype-handmark-stage`（枝 `spike/handmark-stage`・読むだけ）

## 運用メモ
- /reimagine 適用: No
- 理由: 形は ADR-051 で決まり、残りの分岐は研究者が 6 問で選んだ（判断 1）
