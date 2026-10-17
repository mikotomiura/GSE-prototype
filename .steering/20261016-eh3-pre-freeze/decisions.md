# 重要な設計判断

前提: worktree `/Users/johnd/GSE-prototype-eh3-pre-freeze`（`chore/eh3-pre-freeze`・`origin/main` `5d7c53be` から）。
引き継ぎは `docs/tangibility-design` ブランチにあり main には無い（2026-10-16 に確かめた）。

## 判断 1: タスクの立て方と順序

- **判断日時**: 2026-10-16（研究者・AskUserQuestion・推奨どおり）
- **採用**: タスク名 `eh3-pre-freeze`。F-1 と分け方の検査を 1 つのタスクにする。順序は「F-1 の画を先に作り、見比べの数日のうちに検査を実装」。
- **理由**: 検査は `analysis/portrait/` にテストを足し `PortraitRunner` を小さく直すだけで、`grammar`・`drift` の既定に触れない。画を作って壁紙に置いた後なら衝突しない。F-1 の結論が既定を変えるときは、検査の後に 1 行直せば済む。
- **却下案**: 引き継ぎどおり厳密に F-1 → 検査（数日待つだけになる）／検査を先に（見比べの開始が遅れる）／2 つのタスクに分ける。

## 判断 2: F-1 の画の作り方・置き方・日数・順序・記録

- **判断日時**: 2026-10-16（研究者・AskUserQuestion 2 回・すべて推奨どおり）

| # | 問い | 決定 |
|---|---|---|
| 1 | 画の作り方 | **Rust の生成器 ＋ 合成の列**。既存の `render_portrait_samples` を広げる。引き継ぎの既定だった `render_e18.py`（EH1 の Python・移植前）は、配る生成器とずれる恐れがあるので使わない。判断 3（tangibility）の「合成の列だけ」は守る |
| 2 | 時計の更新の再現 | 再現しない。日中は育った画、その日の作業の終わりに seed に替える（EH3 の `a_first=seed` と同じ順。seed は翌朝の最初の打鍵まで見える画）。置き替えは研究者が手で 1 日 2 回 |
| 3 | 日数 | 1 候補 2 日・計 8 日。日ごとに合成の列の seed を変え、同じ画を 2 日見ない |
| 4 | 順序 | 固定の順を乱数で決める。`random.Random(20261016).shuffle` で `raw-none` → `lattice-diffuse` → `lattice-none` → `raw-diffuse`（各 2 日） |
| 5 | 記録 | このタスクの `f1-viewing-notes.md` に研究者が書く（日ごとに候補・「予想しない形が返るか」・「良し悪しに見えないか」）。系には記録しない。選んだ結果は本ファイルに |

- **基準**（tangibility 判断 3）: 「予想しない形が返るか」と「良し悪しに見えないか」。EH2 と同じ扱いで参加者なし。
- **画面**: この Mac は 2560×1664（16:10）、画布は 320×180（16:9）。

## 判断 3: 分け方の検査の形

- **判断日時**: 2026-10-16（研究者・AskUserQuestion・推奨どおり）
- **背景**: 生成器の入力 `Second` には推定の欄が無いが、`PortraitRunner`（`lib.rs:842`）は `FeatSnapshot` をまるごと受け取る（`p_stuck`・`p_flow`・`raw_x` などを含む）。画は `emit` が大域の `send_wall` を直接呼んで出している。
- **採用**:
  - 振る舞いの検査: `PortraitRunner` の画を出す処理を戻り値にし（送るのは呼び出し側・振る舞いは変えない）、同じ f1..f6・打鍵・時計で推定の値だけを変えても、出す画と時刻が変わらないことを単体テストで確かめる。配布物のコードに触れるので凍結の前に入れる。
  - 参照の検査: Rust の単体テスト。`analysis/portrait/` のソースを `include_str!` で読み、推定・招待の参照が無いことを確かめる。ディレクトリの中の `.rs` を数えて検査の対象と合わなければ赤にする（ファイルを足したときの漏れを防ぐ）。
- **却下案**: `PortraitLayer` だけに当てる（入力に推定の欄が無いので形だけになり、呼び出し側の漏れを拾えない）／`PortraitRunner` を別モジュールへ移す（`lib.rs` の差分が大きい）／`scripts/` の静的検査（CI に 1 段足す必要がある）。

## 判断 4: 試しの画を見て、見比べを文法 2 つ・1 日 4 時間に組み直す

- **判断日時**: 2026-10-16（研究者・AskUserQuestion・推奨どおり）
- **背景**（day 1 の試し・4 候補 × 2・3・4 時間・配る物と同じ `PortraitLayer` の経路）:
  - 5 分ごとの予定のうち画が替わるのは 2 時間で 5 回、4 時間で 10 回（約 2 割）。残りは打鍵の最中（直前 5 秒）か 60 秒以上の不在で飛ぶ。Windows の実機（`.steering/20261011-portrait-eh3-after-impl/decisions.md` 判断 3: 更新 2・飛ばし 8）と近い割合。
  - drift `diffuse` は更新ごとに 1 回の軽いぼかし（`DIFFUSE_SIGMA` 0.6 px・`DIFFUSE_MIX` 0.1）。この回数では `none` との差は画素の値で最大 4/255 で、目では見分けられない。前に研究者に見せた見本（`render_portrait_samples`）は予定をすべて更新に回していたので、実物より drift が効き、画も大きく見えていた。
  - `raw` は 2 時間で左上の角に寄り、4 時間までほぼ変わらない（覆う割合 0.17）。`lattice` は中心の塊が少しずつ広がる（0.07 → 0.10）。
- **採用**: 見比べは `raw` / `lattice`（drift `none`）を 4 日ずつ・計 8 日。順は判断 2 #4 の乱数の順を文法に読み替えた raw → lattice → lattice → raw（各 2 日・ABBA）。1 日の合成の長さは 4 時間。drift は「配る物の経路では見えない」を材料に、見比べの後に別に決める。
- **却下案**: 4 候補を 2 日ずつのまま（drift の対は同じ画を見るだけになる）／合成の打鍵を更新が多い形に変える（形を決める根拠が無く、実機の割合からも離れる）。
- **影響範囲**: `render_f1_viewing_days` の順と既定の長さ。`f1-viewing-notes.md` の表。drift の扱いは F-1 の結論に含めて研究者が決める。
- **研究者に伝える材料**: 更新が約 2 割しか起きないことは F-2（予定の値）と肖像の育ち方の両方に効く。凍結の前に見直すかは研究者が決める（このタスクでは変えない）。

## 判断 5: 分け方の検査の細部（判断 3 の実装で決めたこと）

- **判断日時**: 2026-10-17（実装の中で決めた。研究者に未確認の細部なので、完了の報告で伝える）
- **採用**:
  1. **出口を「戻り値」ではなく「差し替えられる受け口」にした。** `PortraitRunner` に `wall: Box<dyn FnMut(WallCmd)>`（本番は `send_wall`）を持たせ、`Show`・`Finish`・`Ack` をそこへ渡す。戻り値にして呼び出し側で送ると、終了の前の経路（`tick` の中で `end()` の `Show` を出してから `Ack` を送る）の順序を呼び出し側で組み直す必要があり、凍結の前に配布物の順序を変える危険のほうが大きい。受け口なら順序はそのままで、検査は届いた指示をすべて（`Finish`・`Ack` を含めて）見られる。判断 3 の「送るのは呼び出し側」の意図（検査が出力を観測できる・振る舞いは変えない）は満たす。
  2. **セッションの種**（`rand::random`）も差し替えられるようにした（`seed: fn() -> u64`）。比べる 2 回で同じ種にしないと、推定と関係なく画が違う。
  3. **`tick` の一時停止を引数にした。** 中で `crate::recording::is_paused()` を読むと、`recording.rs` のテストが大域の旗を並行して切り替えるので、検査が揺れる。呼び出し側が `crate::recording::is_paused()` を渡す（振る舞いは同じ）。
  4. **参照の検査の範囲に `wallpaper*.rs` を含めた。** 引き継ぎ §3 が「肖像」を `analysis/portrait/`・`wallpaper*.rs` と定めているため。`crate::` の参照は許可リスト（`crate::eh3`・`crate::analysis::portrait`・`crate::wallpaper`・`crate::submission::home_dir`）で見る。
  5. **生成器の内部の関数 `level` を `normalized_mean` に改名した**（変数 `levels` → `means`）。禁止の語 `level`（ADR-017 の表現チャネルの段）と同じ名で、識別子の検査が誤って赤になるため。振る舞いは変えない（既存の生成器のテストと replay が緑）。
  6. **置き場所は `lib.rs` のテストのモジュール `portrait_separation_tests`。** `PortraitRunner` が `lib.rs` の非公開の型であることと、検査のコードが検査の対象のディレクトリに入らない（禁止の語を書いても自分を赤にしない）ため。
- **陽性対照**（2026-10-17・コミットしない。控えから戻し `cmp` で一致を確かめた）:

| # | 壊し方 | 結果 |
|---|---|---|
| 0 | 画の回数の下限を 100000 に | 赤（「画が 5 回しか出ていない」）。合成の 2 時間で画は 5 回 |
| 1 | `analysis/portrait/mod.rs` に `use crate::analysis::invitation;` | 参照の検査が赤（`["invitation", "crate::analysis::invitation"]`） |
| 2 | `PortraitRunner::feat` に `p_stuck > 0.5` で材料を捨てる分岐 | 振る舞いの検査が赤（停滞が低いままの列で 1 番目の指示が変わる） |
| 3 | `PortraitRunner::feat` で `p_stuck > 0.5` のとき材料を止める（`material_blocked_until_ms`） | 振る舞いの検査が赤 |
| 4 | `analysis/portrait/extra.rs` を足す | ファイルの照合が赤 |

- **限界**: 参照の検査はコメント行と `#[cfg(test)]` より後を見ない。行の途中のコメントや文字列の中の語は数える（赤に倒れる側）。振る舞いの検査は合成の 2 時間・1 つの割り当て（`raw`・`none`・`a_first=seed`）だけで、`a_first=none`・`lattice`・日付の区切り・スリープの経路は通していない。

## 判断 6: code-reviewer ∥ security-checker の指摘を直す（9c47e03c に対して）

- **判断日時**: 2026-10-17
- **security-checker**: CRITICAL・HIGH・MEDIUM なし。LOW 1 件（`with_outputs` が本番のコードにも入る・将来固定の種を渡しうる）→ doc コメントに「本番は `new` だけ」と書いた。
- **code-reviewer HIGH（一次で確かめた・正しい）**: 参照の検査は最初の `#[cfg(test)]` で切っていたが、`generator.rs:161` は impl の中のテスト用の関数（`with_walk_start`）で、161〜288 行（描画の本体）を見ていなかった。`wallpaper.rs:522` も同じ型。したがって判断 5 #5 の改名の理由（`level` が誤って赤になる）は、9c47e03c の検査では観測されていなかった。
  - 直し: 切る位置を「字下げの無い `#[cfg(test)]` の次の行が `mod`（`pub` / `pub(crate)` を許す）」に限った。直した後、改名を戻すと `level` で赤になる（改名の理由がいまは成り立つ）。最初の直しでは `wallpaper.rs` のテストのモジュールが `pub(crate) mod tests` で始まるのを見落とし、赤に倒れて気づいた。
  - 再発防止の対照をコミットするテスト `the_reference_check_catches_each_kind_of_leak` に置いた（impl の中の `#[cfg(test)]` の後ろの `p_stuck` を拾う・テストのモジュールの中は拾わない、など）。
- **MEDIUM 1**（振る舞いの検査は `FeatSnapshot` の引数しか変えないので、`PortraitRunner` が大域の推定・招待の状態を読む経路は緑のまま通る）: 正しい。陽性対照で確かめた（`tick` に `INVITATION_PRESENT` を読む分岐を足しても振る舞いの検査は緑）。→ `lib.rs` の `struct PortraitRunner` から `impl PortraitRunner` の終わりまでを切り出して参照の検査にかけた（`FeatSnapshot`・`loop_step` は `feat` の引数の型として許す・`crate::` は許可リスト）。同じ陽性対照で赤（`["INVITATION_PRESENT"]`）。
- **MEDIUM 2**（`super::super` のような相対の参照が素通り）: `analysis/portrait/` の子は `super::` を 1 段だけ、それ以外（`mod.rs`・`wallpaper*.rs`・殻）は `super::` を許さない。
- **MEDIUM 3**（`crate::eh3` を前方一致で許すと `Trigger` などの招待の経路を通す）: 許可を型・関数の名前に絞った（`Assignment`・`Condition`・`Drift`・`Grammar`、殻は加えて `DayTracker`・`local_day`）。`{...}` でまとめた import はほどいて照合する（入れ子はほどかず赤に倒れる）。
- **陽性対照**（追加・2026-10-17・控えから戻し `cmp` で一致を確かめた）: 改名を戻す → 赤（`["level", "level"]`）／`PortraitRunner::tick` に `INVITATION_PRESENT` → 赤／`generator.rs` の `draw` に `p_stuck` → 赤。
- **見送った LOW**: 終了の経路（`PORTRAIT_END_REQUESTED` → `end` → `Ack` の順）を通すテスト（大域の旗と `PORTRAIT_END_DONE` を伴い、並行するテストと干渉する。順序は差分で変えていない）／f3・f4・f6 と打鍵への感度の対照（f1 で比べ方が鈍くないことは確かめた）／`use crate as c;` の別名は拾えない。判断 5 の「限界」に加える。

## 判断 7: /cross-review（a515ac47..ca9d7865）の指摘を直す

- **判断日時**: 2026-10-17（研究者の指示: cross-review と push まで行い、PR はタスクを閉じるときに出す・AskUserQuestion・推奨どおり）
- **結果**: 両者一致なし。Claude のみ 2 件（MEDIUM 1・LOW 1）、Codex のみ 3 件。差分は 583 行（警告の閾値 500 を超えたが手動承認の 2000 未満）。
- **採用して直したもの**:
  1. （Claude・MEDIUM・一次で確かめた）殻の切り出しが `"\n}\n"` を探していて、`*.rs` は `.gitattributes` で LF に固定していないため、Windows の checkout で CRLF になると見つからず panic する。→ 行で探す `runner_block` に替え、CRLF の合成のソースで切り出せることを対照に置いた。さらに `lib.rs`・肖像の側のソースを丸ごと CRLF にして 4 本が緑になることを手元で確かめた（戻して `cmp` で一致）。
  2. （Codex）`use super::{super::heads::writing};` が `super::super` の文字列の検査をすり抜ける。→ `analysis/portrait/` の子では `super::{` も外へ出る経路として拾う。対照を足した。
  3. （Claude・LOW）推定の欄 `obs`・`alpha` が語の一覧に無い。→ 殻の検査にだけ足した（肖像の側の `alpha` は `canvas.rs` の描画の引数なので禁じない）。陽性対照: 殻の `feat` が `f.obs` で材料を捨てる → 参照・振る舞いの両方が赤。
- **記録に回したもの**（判断 5 の「限界」に加える）:
  - （Codex）テストのモジュールより後ろに置いた配る項目は見ない。現状 5 ファイルとも、テストのモジュールがファイルの終わりまで続く。
  - （Codex）`run()` の中で、推定で `p.feat()`・`p.tick()` を呼ぶか自体を決める経路は、どちらの検査も守らない（振る舞いの検査の `drive` は `run()` の呼び出し順を手で写したもの）。
  - （Claude・LOW）一時停止の値を、`in_session` でない tick でも読むようになった。`is_paused` は Atomic の load だけで、振る舞いは変わらない（確認の記録）。

## 判断 8: 見比べの壁紙を自動で替え、気づきを Claude が毎晩 AskUserQuestion で聞く（判断 2 #2・#5 を改める）

- **判断日時**: 2026-10-17（研究者の依頼・AskUserQuestion 3 問）
- **採用**:
  - 期間は 2026-10-18（日）〜10-25（日） の 8 日。順と画は判断 4 のまま（raw 2 日 → lattice 4 日 → raw 2 日）。
  - 置き替えは手でなく launchd（`~/Library/LaunchAgents/com.johnd.gse-f1-viewing.plist`）。10:03 にその日の日中の画、21:57 にその日の seed。スクリプトは `~/Pictures/gse-f1-viewing/set-wallpaper.sh`（repo の外）で、呼ばれた時刻から置く 1 枚を決める（10:03 より前は前の日の seed）。眠っていて時刻を逃しても、起きたとき・ログインのときに正しい 1 枚になる。10-26 の 10:03 に始める前の壁紙（`original-wallpaper.txt`）に戻す。記録は `set-wallpaper.log`。
  - 質問は Claude が毎晩 22:0x に AskUserQuestion で聞く（このセッションの一回きりの予定・セッションを閉じると消えるので、そのときは研究者が新しいセッションで頼む）。形は中立の選択肢（はい・どちらともいえない・いいえ）で基準 2 つ、自由記述 1 問（Other）。具体的な読み（「縁に寄って見えた」など）を選択肢に書かない（気づきを誘導しないため）。答えは `f1-viewing-notes.md` の表に Claude が写し、自由記述は研究者の言葉のまま写す。
  - 10-26 の朝に「終えたあと」（文法の選択・理由・drift）を聞く。選択は研究者が決め、Claude は推奨を付けない。
- **改めたもの**: 判断 2 #2（置き替えは研究者が手で 1 日 2 回）→ 固定の時刻で自動。実物の EH3 は作業の終わりで seed になるので、21:57 はその近似。判断 2 #5（研究者のメモだけ）→ Claude が聞いて写す。系（GSE）には引き続き記録しない。答えは合成の画への感想で、打鍵の内容・NDJSON を含まない。
- **確かめたこと**: 時刻の境目（09:00・10:03・21:56・21:57・翌朝 08:00・10-26 09:59・10:03）を時刻の差し替え（`GSE_F1_NOW`）で通し、期待の 1 枚が選ばれた。開始前は何もしない。画が無いと exit 1。壁紙を置く処理（`NSWorkspace.setDesktopImageURL`）は、見比べの画を前もって見せないよう元の壁紙で試した。launchd の初回（ログ「開始前」・exit 0）。元の壁紙のフォルダー名の末尾に空白があり、macOS が返すパスは空白の無い古いもので見つからなかった → 実在のパスを `find` で取り直した。
- **限界**: 置くのはそのとき表示中の Space の画面だけ（`NSWorkspace` の仕様）。Space を複数使うと他の Space は替わらない。
