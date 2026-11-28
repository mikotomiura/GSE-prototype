# タスクリスト

- [x] v0.1.42 から枝 `fix/s1-self-canvas-hotfix` を切り、e656ca62 を載せて食い違いを直す（f1cf1364）
- [x] test:handmark 50 件・tsc・guard 36 件が緑、陽性対照（`window.localStorage` を足す）で guard が赤
- [x] 版を 0.1.45 に上げる（87449613）
- [x] push・タグ v0.1.45・CI の build と release（run 46128959669。1 回目は build-macos が成果物の upload で `CreateArtifact: ETIMEDOUT`、失敗した job の再実行で緑）
- [x] Release を prerelease にし、v0.1.44 を latest に戻す
- [x] dmg（`gse-next_0.1.45_aarch64.dmg`・SHA-256 4ed566aeb63fc2b48cc2b97e8d930f8a13087b426849783288e690d1e2902c9b）: 版 0.1.45・`s1-self-trial-1` 1 件・`s1-n3-1` 0 件・codesign の確認が通る
- [x] 門（`--audience self --os-only macos`・hotfix の worktree から実行）: 通過 24 / 未達 2。未達はどちらもタグの節（判断 2）
- [x] 研究者がトレイから終了 → v0.1.42 の app を退避 → 入れ替え → `s1-release-tag.txt` を v0.1.45 に。残す 6 ファイル（表・.sha256・s1.mode・o1.mode・o1.autostart・seed）の SHA-256 は前後で同じ。入れ替えは 2026-11-28T21:31:55+0900
- [x] 再起動の後のログ: 1 回目の起動は入力監視の許可待ち（HookDown）。研究者が許可して起動し直し、2026-11-28T12:37:03Z に Measuring・段 1 と手跡の driver が起動。1 回目の記録は次の起動の orphan sweep で閉じた
- [ ] 帯が全幅に描かれることを画面で見る（次に手跡が出る日。2026-11-28 は 4:00 から表示時間 0 で、入れ替えの前から出ていない）
- [x] 記録を main に入れる（.steering の docs だけ・この枝は main に入れない）
