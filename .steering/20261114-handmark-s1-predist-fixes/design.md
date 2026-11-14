# 設計

## 1. 削除した区間の量を引く（判断 1）

純関数 `redaction::handmark_subtractions(rows, from, to, live) -> BTreeMap<day, Sub>`:

- 入力は、削除の対象のディレクトリの全ファイル（いま書いているファイルも読むだけ）の `handmark_day` の行のうち `visible_ms` が数のもの（累計の写し。出せなかった理由の行は `visible_ms` が null で累計を持たない）の `(day, t, shown_ms, visible_ms)` と、走行中の累計 `(day, shown_ms, visible_ms)`。
- 日 d ごとに、next = d の行で `t > to` の最初のもの（無く、走行中の累計が d なら走行中の累計）。next が無ければその日は引かない。
- prev = d の行で `t < from` の最後のもの（無ければ 0）。
- 引く量 = next − prev（shown・visible とも飽和の引き算）。0 なら引かない。
- 区間が d より前に終わっていても、d の最初の行（日付の変わり目か起動の行）は累計が小さいので、引き過ぎは 5 分ほどまで（判断 1 の端と同じ扱い）。

適用:
- `redact_file` は、区間の外に残る `handmark_day` の行で `t > to` かつ日が表にあるものから引く（visible ≤ shown を保つ）。
- 走行中の累計（駆動役・状態ファイル）は日が一致するときだけ引く。
- 順序（`delete_time_range`）: ローテート → 表を作る（ファイルと走行中の累計を読む）→ 状態と走行中の累計に適用 → ファイルに適用。

## 2. 一時停止（判断 2）

駆動役に `on_paused(paused, now)` を足す（`set_recording_paused` と駆動の刻みの両方から呼ぶ・同じ値なら何もしない）。

- 一時停止中は `add_shown`・`add_visible` をしない。
- 一時停止の始まりの時刻 p と、その時点の `off`・`cursor_off`・`click_off` を覚える。
- 再開（または一時停止のままの終了）のとき、状態の `[p, now]` の時刻の要素を消し、`off`・入力の切りが始まりと違えば `now` の時刻で 1 件足す。起点を消した・窓が開いていれば `now` で起点を取り直す。`now` は `recording_pause`（再開）か `meta` の終わりで既に記録に出る時刻なので新しく分かることはない。

## 3. 行種の削除の鍵

`redaction.rs` のテストで `schema/current.json` の `oneOf` から行種と必須の欄を読み、除外 4 行種（`meta`・`session_meta`・`invitation_condition`・`probe_frame`）以外は `line_timestamp` の鍵が必須の欄にあることと、その鍵だけを持つ行が区間で消えることを確かめる。schema の行種の集合が `KNOWN_LINE_TYPES` と一致することも確かめる。

## テスト戦略

- 純関数のテスト（前後の行・行が無い日・走行中の累計・2 日にまたがる区間・繰り返しの削除）と変異。
- 駆動役のテスト（一時停止中に量が増えない・時刻が残らない・再開で 1 件・終了で 1 件）。
