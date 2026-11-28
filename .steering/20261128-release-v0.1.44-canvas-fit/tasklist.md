# tasklist

- [x] 版を 0.1.44 に上げる（package.json・tauri.conf.json・Cargo.toml・Cargo.lock）・`cargo metadata --locked`
- [ ] コミット → push → PR → CI 緑 → マージ
- [ ] マージのコミットで版を検算してタグ `v0.1.44` を push
- [ ] CI の build-macos と release の成功を確かめ、配布物をスクラッチパッドへ落とす
- [ ] 門を通す（--audience self --os-only macos）
- [ ] gse-next を止め、gse-next.app だけを替え、s1-release-tag.txt を書き換える（日時を記録）
- [ ] 起動し直して Measuring・input_monitoring=true・手跡の日の行を確かめる
- [ ] 帯が全幅に描かれることを画面で見る
