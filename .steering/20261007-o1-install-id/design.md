# 設計
- 保存先: `~/.gse/o1_install_id`（`o1_participant_id` と同じ流儀）。ログインユーザー × 端末ごとに 1 つ。フォルダ移動に追従しない。
- 生成: `rand` で 8 バイト → 16 桁小文字 hex。ハードウェア・MAC・ホスト名・ユーザー名は使わない（ADR-013 D6）。
- 純関数: `o1::is_valid_install_id` / `o1::generate_install_id`、IO は `submission.rs`（`read_or_create_o1_install_id`）。
- キャッシュ: `o1::set_install_id` / `o1::install_id()`（OnceLock・`set_mode` と同形）。lib.rs の `set_mode` 直後に O1 のときだけ確定。
- meta: `o1_mode_fragment` を純関数 `o1_meta_fragment(mode, install_id)` に分け、O1 のとき `,"o1_mode":"..","o1_install_id":".."`。
- schema_dto: `o1_install_id: Option<String>`（skip_serializing_if）。`emit_schema` で current.json 更新。
- 限界: 同じ `~/.gse` を別端末へコピーすれば同じ ID になる／ユーザーを変えると別 ID／~/.gse を消すと別 ID（導入単位）。
