# 重要な設計判断

設計の判断の本体は計画の `.steering/20261105-gse-m5-probe-wiring-plan/decisions.md`（判断 0〜10）。ここには分割と実装で新しく決めたことだけを書く。

## 判断 1: M5 を 3 本の PR に分け、本タスクは B1〜B3

- 判断日時: 2026-11-06
- 背景: 計画の tasklist の B1〜B7 は 1 タスクの想定だったが、20 ファイル近くに及び、画面と実機での確かめを含む。
- 選択肢: A 3 本（B1〜B3／B4・B5／B6・B7）／B 1 本／C 2 本（B1〜B3／B4〜B7）
- 採用: A（研究者・推奨どおり）
- 理由: 区切りごとにレビューでき、実機での確かめは 2 本目に集まる。hosted の Windows の CI の分数も分けて使える。
- トレードオフ: 1 本目と 2 本目の間は、行種と調停器はあるが送出元が無い状態で main に置かれる。
- 影響範囲: 本タスクのスコープ（requirement.md）。
- 見直し: 2 本目の設計で調停器の入出力の形が足りないと分かったとき。

## 判断 2: 送出元が無い間、新しい行種と `activity_label` は `emitterless` に置く

- 判断日時: 2026-11-06
- 背景: 計画の B3 は「`activity_label` を `emitterless` から外し、4 行種を `config_gated`」だった。分割により、送出元（`lib.rs` で行を書く経路）は 2 本目に移る。
- 採用: 1 本目では `probe_frame`・`probe_suppressed`・`day_question` を `activity_label` と同じく `emitterless` に足す。`config_gated` への移しと `activity_label_has_no_emitter_until_it_is_wired` の削除は、送出元を作る 2 本目で行う。
- 理由: ADR-013 D2（宣言の根拠は writer ではなく送出元があるか）。宣言すると、記録できない行を「測ったが 0 行」と読ませる過大申告になる。既存の検査が送出元を作った時点で赤になり、移しを強制する。
- 研究者には聞いていない: 既存の規則で答えが決まっているため。
- 影響範囲: `capabilities.rs` の検査。2 本目の tasklist に移しを書く。

## 判断 3: 登録の画面の同意の項目は 2 本目へ

- 判断日時: 2026-11-06
- 背景: 計画の B1 に「登録の画面の同意の項目（判断 5）」があるが、tsx の変更で画面の確かめを要する。
- 採用: 1 本目は `submission::s1_probe_consent_acknowledged`・`write_s1_probe_consent` の関数と検査まで。画面とコマンド `acknowledge_s1_probe_consent` は 2 本目。
- 理由: 1 本目を cargo test で閉じる（判断 1）。

## 判断 4〜7: 計画の設計から変えた 4 点（2026-11-06・研究者が承認）

詳細は design.md「計画から変えた点」。

| # | 変えた形 | 理由（一次） |
|---|---|---|
| 4 | 調停器は時差ではなく現地の日 `local_day` と現地の分 `local_minute` を受け取る | `analysis/` が最上位の `eh3` に依存しない（architecture-rules ルール 1）。変換は `eh3.rs:353/359` |
| 5 | 候補の間隔の乱数と `probe_id` の乱数を分ける | 同じ列から引くと発火の有無で後の候補が動く |
| 6 | `SkipReasonKind` にも `superseded`。UI の `record_realtime_skip` は拒む | `replay.rs:3896-3899` が未知の値の行を数えて捨てる（impact-analyzer の指摘を一次で確認） |
| 7 | EH3 の `set_mode`（`lib.rs:4169`）の前に段 1 を判定する | `OnceLock` は後から落とせない |

## 判断 8: `day_question` と `probe_suppressed` は 2 つの時刻を両端とする区間で消す

- 判断日時: 2026-11-06
- 背景: 計画の design.md §4 は新しい行種を `"t"` の点で消すとしていた。`day_question` は `t`（閉じた時刻）のほかに `shown_ts`、`probe_suppressed` は `t`（判定した時刻）のほかに `candidate_ts` を持つ。
- 採用: `redaction::line_interval` で `day_question` は `shown_ts`〜`t`、`probe_suppressed` は `candidate_ts`〜`t` の区間にする（`activity_label` の `recall_window` と同じ作り）。検査 `new_s1_rows_are_deleted_by_t`。
- 理由: 点で消すと、削除した区間の中の時刻（表示した時刻・候補の時刻）が残った行の別の欄に残りうる。消す側に倒す（`data-privacy` ルール 6-iii）。
- 研究者には聞いていない: 削除の約束（その時間帯が消える）を強める向きで、約束の文言とも合う。
- 影響範囲: `redaction.rs`。3 本目の replay で、削除の後に欠けた候補を「欠け」と数える照合に効く。
