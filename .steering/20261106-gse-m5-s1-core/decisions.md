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

## 判断 9: `day_question` に現地の分を書かず、時間帯の中かの真偽 `in_eod_window` だけを書く

- 判断日時: 2026-11-06
- 背景: security-checker の MEDIUM。`shown_local_minute`（現地の分）と `shown_ts`（UTC）を同じ行に書くと、時差が分の精度で正確に出る。計画の判断 4 は「日付と UTC の時刻から時差をおおよそ逆算できる点は残る」と書いていたが、効き方は「おおよそ」ではなかった。今の O1 の記録はファイル名も UTC（`logger.rs:3240-3265`）なので、時差を出す初めての欄になる。
- 選択肢: A 時間帯の中かの真偽に落とす／B そのまま残し判断 4 の文を直す／C 30 分単位に丸める（多くの時差は 1 時間か 30 分の倍数なので隠す効きが小さい）
- 採用: A（研究者・推奨どおり）
- 理由: 判断 4 の目的（出た問いが時間帯の中だったかを記録で確かめる）は保ち、時差は出さない。
- トレードオフ: 他の参加者の記録で「現地の何時に出たか」の分布（S1-F5）を記録だけからは描けない。本人の試しでは研究者が自分の時差を知っているので UTC から戻せる。`target_day` と `t` からおおよその時差が出る点（日の切れ目の近くだけ）は残る。
- 影響範囲: `logger.rs`（`DayQuestionRow`）・`schema_dto.rs`・`schema/current.json`・調停器の `Action::ShowDayQuestion { in_window }`。計画の判断 4 の文は書き換えず、ここで上書きする。

## 判断 10: 作業中の点検（code-reviewer・security-checker）への対応

- 判断日時: 2026-11-06
- 対応したもの（一次で確かめてから直し、HIGH と MEDIUM のうち調停器の 3 点は直した処理を壊すと名指しの検査が赤になることを確かめた）:

| 出所 | 重さ | 指摘 | 対応 |
|---|---|---|---|
| code-reviewer | HIGH | 溜まった候補の離席を今の時刻で判定し、同じ tick の押下を先に入れていた（スリープ明けに何時間も前の候補が発火しうる） | 離席を候補の時刻 `c` 以前の最後の押下から判定。この tick の押下は ① の後で反映。検査 `stale_candidate_after_sleep_does_not_fire` |
| code-reviewer | MEDIUM | 拾い直しの印がカードが開いていても立つ | 尋ねたときか対象が無いと決まったときだけ立て、開いていれば持ち越す。検査 `pickup_deferred_while_card_open` |
| code-reviewer | MEDIUM | 日の問いの途切れに一時停止とスリープの時間が入る | 再開と復帰で起点を置き直す。検査 `eod_idle_excludes_pause_and_sleep` |
| code-reviewer | MEDIUM | `s1_and_eh3_both_dropped` が空回り（EH3 を落とす行を消しても緑） | 純粋な関数 `s1::resolve_with_eh3` に切り出して 4 通りを検査。`lib.rs` はその戻り値を `eh3::resolve` に渡す |
| code-reviewer | MEDIUM | 送出元が無いのにログが「問いを出す」と言う | ログの文を「モードだけを記録・駆動役は未実装」に改めた。2 本目で文を戻す（引き継ぎに書く） |
| code-reviewer | MEDIUM | 層化と無作為の検査の日の問いの側が空回り | 模擬の現地の時刻を進め（16:40 から・日の切れ目をまたぐ）、日の問いが出たことを assert |
| code-reviewer | LOW | `hourly_max_total` の切り捨て | `div_ceil` |
| code-reviewer | LOW | 再開の予約を `take()` が先に消す | カードが開いていれば残す |
| code-reviewer | LOW | 溜まった候補に今の区画を当てる | 候補ごとの時刻で区画を引く（`local_at`・検査 `local_at_steps_back_across_the_cutoff`） |
| code-reviewer | LOW | スリープの復帰でウォームアップをやり直さない | やり直す |
| code-reviewer | LOW | 同意の印を直書き | 一時ファイル → 置き換え |
| code-reviewer | LOW | 答えていない行に回答を書ける | 整形で `null` に揃える |
| security-checker | MEDIUM | 現地の分で時差が出る | 判断 9 |
| security-checker | LOW | 2 つ目の時刻が 0 の行が epoch から消える | 点に倒す |

- 見送ったもの: code-reviewer LOW「日をまたいだ再開で予約を消す処理の検査は、消しても緑」。日の比較と新しい日に押下が無いことで二重に守られており、消去の処理は保険。security-checker LOW 2 件（同意の時点で出す枠の行の `t`・同意の取り消しの関数）は送出元と画面を作る 2 本目で決める（引き継ぎに書く）。

## 判断 11: /cross-review 1 巡目（Claude code-reviewer ∥ Codex）への対応

- 判断日時: 2026-11-06
- Codex に送った範囲: `ae8775e0..HEAD -- src-tauri/src`（研究者の判断で、生成物の `schema/current.json` と `.steering` の文書は外した・差分が手動の承認の閾値 2000 行を超えたため）。記録の本文は含まない。使用量 63345 / 1 回はメインの台帳へ写した。
- HIGH は両者とも無し。対応したもの（すべて一次で確かめ、調停器の 4 点は直した処理を壊すと名指しの検査が赤になることを確かめた）:

| 分類 | 指摘 | 対応 |
|---|---|---|
| 両者一致 | 再開の tick にカードが開いていると予約が次の再開まで消化されない | `resume_pending` で同じ日のうちに持ち越す。検査 `resume_with_card_open_asks_after_close` |
| 両者一致 | `local_at` が分の境界の 1 分以内を取り違える | 分の中の秒をミリ秒で引く。検査に境界の 1 秒前後 |
| Codex のみ | 無作為に伏せられた日の問いのカードを日の切れ目で閉じられない | `DayQuestion::showing` で自分が出したカードを覚え、切れ目で閉じる。伏せている間はもう 1 枚出さない。検査 `hidden_day_card_closes_at_day_end` |
| Codex のみ | `superseded` の網羅の検査が手書き | `match` で列を作り、値を足すとコンパイルできなくする |
| Claude のみ | 拾い直しの持ち越しが日の切れ目で消えない | 切れ目で消す。検査 `pickup_pending_not_carried_across_day` |
| Claude のみ | 層化の途切れに一時停止とスリープの時間が入る | 再開と復帰で層化の前の押下を忘れる。検査 `strata_ignore_gap_spanning_pause_or_sleep`（対照つき） |
| Claude のみ（LOW） | ログの文字列の行継続の欠け・衝突のログの文・スリープ明けの検査の言い切り・`resolve_with_eh3` の 5 通り目 | 直した |

- 2 本目の駆動役への注: 無作為が出たとき日の問いのカードは駆動役が伏せて保ち、無作為に答えた後で出し直す（調停器は出し直しの指示を出さない。`showing` が残っているので、駆動役は出し直すべきカードを調停器の状態とそろえられる）。引き継ぎ §2 に足す。
