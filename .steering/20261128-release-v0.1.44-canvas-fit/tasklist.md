# tasklist

- [x] 版を 0.1.44 に上げる（package.json・tauri.conf.json・Cargo.toml・Cargo.lock）・`cargo metadata --locked`
- [x] コミット → push → PR → CI 緑 → マージ（PR #444・7618ce11）
- [x] マージのコミットで版を検算してタグ `v0.1.44` を push
- [x] CI の build-macos と release の成功を確かめ、配布物をスクラッチパッドへ落とす（run 46103002385）
- [x] 門を通す（--audience self --os-only macos・26 通過 / 0 未達）
- [-] gse-next を止め、gse-next.app だけを替え、s1-release-tag.txt を書き換える → 取りやめ（decisions.md 判断 1）
- [-] 起動し直して Measuring・input_monitoring=true・手跡の日の行を確かめる → v0.1.45 で行った
- [-] 帯が全幅に描かれることを画面で見る → v0.1.45 で行う
