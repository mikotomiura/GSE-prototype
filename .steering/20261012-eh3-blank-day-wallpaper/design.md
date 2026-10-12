# 設計

- `restore` の始めで、つながっている対象のモニタごとに読み戻し（`Backend::get`）を取り、元のパスと同じモニタ（`showing_original`）を決める。
- そのモニタには `set` しない。戻った扱い（`restored` に入れる）にし、`ok` は元のファイルの SHA-256 が控えと同じかで決める（今までの `read_back && unchanged` と同じ基準）。
- 書くモニタが 1 台も無ければ `set_position` もしない。
- 判定は書いた記録（`last_set`）ではなく読み戻しで行う。異常終了で記録を失っても、肖像が残るモニタは元と違うパスなので書き戻す。
- 本人が替えたモニタは、これまでどおり `detect_user_change` が先に除く（元のパスに本人が戻した場合も、この層が書いた後なら本人の差し替えとして除かれる）。

## テスト

- `showing_the_original_while_it_is_already_shown_writes_nothing`: 2 台・起動の後に本人が位置を替えた・元を見せる → `set` 0 回・位置は本人の値のまま・終わりも `set` 0 回で状態ファイルを消す。
- `only_monitors_still_showing_the_portrait_are_written_back`: 2 台に肖像 → 1 回目の戻しで 1 台だけ失敗 → 2 回目は 1 台だけ書く。
