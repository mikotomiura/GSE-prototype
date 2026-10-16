# 引き継ぎ: 手跡の背景の層の試作の後（Mac）

作成 2026-10-17（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号を多用しない。研究者に決めてほしいことは、報告の文章に並べず AskUserQuestion で、推奨と理由を添えて聞く。PR は出さず push で止める。

## 0. 新しいセッションで最初に打ち込む文

どちらかを選ぶ。

```
.steering/_handoff/next-session-handmark-stage-followups.md を読んで、§3 の A（直した版の試視）から始めて。
```

```
.steering/_handoff/next-session-handmark-stage-followups.md を読んで、§3 の B（手跡の理論の語）へ進んで。
```

このメモは枝 `spike/handmark-stage`（worktree `/Users/johnd/GSE-prototype-handmark-stage`）にある。コミットの前に `git branch --show-current` を確かめる。

## 1. 何が決まったか（`.steering/20261016-handmark-stage-spike/decisions.md`）

- 判断 1: 右下の小面は候補台の乙（40 px・墨の輪＋白い縁・窓 52 px）。候補台 https://claude.ai/artifact/6MgWQuDKsintuj2DCZhJpS
- 判断 2: 試視で白い下地の輪が見えにくかったので、墨の線 4 px・広がりの前半は濃いまま（候補台の「乙改」）。
- 判断 3: 試視で「チョイチョイ打つと動きが止まっては動く」ので、背景の流れに慣性を持たせた。
- 判断 4・5: 完了時のレビュー（code-reviewer・security-checker・Codex 2 巡）の指摘の扱い。

## 2. いまの事実（`results.md`）

- 背景の窓は `kCGDesktopWindowLevel`（壁紙の上・アイコンとウィジェットの下）に公開の API だけで置けた。壁紙の画像は読み書きしていない。
- メニューバーが出ている限り、覆われても描画は止まらない。全画面のアプリの間だけ止まり、戻ると再開する。
- 取り込み: 保護なしの背景は Chrome の画面共有と標準のスクリーンショットに写り、保護ありは写らなかった（陽性対照つき）。標準のスクリーンショットで保護ありの小面が写らなかったのは、前の試作（写った）と食い違う。理由は未確認。
- 負荷: 背景の分で 1 コアの約 8〜9 % 増（電池・低電力モード・各 1 回）。描画は 1 秒に 30 回で頭打ち（低電力モードの見込み・未確認）。
- Spaces: 移った先でも背景と小面は画面上にあった。描画の継続は記録していない。
- 起動: `GSE_HANDMARK_SPIKE=1`（小面）・`GSE_HANDMARK_STAGE_SPIKE=1`（背景）・`GSE_HANDMARK_STAGE_SPIKE_PROTECT=1`（背景の保護）・`GSE_HANDMARK_SPIKE_MEASURE=1`（計測）。研究者の試視の手順は `manual-check.md`。
- Claude ができること（2026-10-17 に確かめた）: 合成の Cmd+Shift+3 で撮れる／Chrome の `getDisplayMedia`（別プロフィール・`--lang=en-US`）で画面全体を取れる／AX で「開始する」を押せる。Mission Control の中身は AX に出ないので、デスクトップを足すのは研究者。撮った画像は研究者の画面が写るので、必要な所だけ切り出してすぐゴミ箱へ。

## 3. 次の候補

> 2026-10-17 追記: A は済んだ（`results.md` §9.1・研究者の言葉: 線はより潜在的になり、自分との同期・共存の感覚が少し芽生えた。右下も存在として少し改善された。暗い壁紙は未確認）。B もすでに 2026-10-16 に済んでいた（枝 `docs/tangibility-design` の `.steering/20261016-handmark-theory-term/`・理論の文書 §1.4・/cross-review 2 巡・判断 4）。このメモを書いた時点でそれを見落としていた。残りは下の「残り」だけ。

- A. 直した版（輪 4 px・流れの慣性）を研究者の画面で見る。あわせて暗い壁紙（任意）。見る前に Claude が起動して「開始する」を押せる。
- B. 手跡の理論の語（枝 `docs/tangibility-design` の `.steering/_handoff/next-session-handmark-theory-term.md`）。
- 残り（急がない）: 低電力モードを切ったとき・電源につないだときの負荷、標準のスクリーンショットの食い違いの切り分け、Zoom の自動（研究者の判断で見送り中）、複数ディスプレイ。

## 4. 守ること

- `src-tauri/src/analysis/portrait/`・EH3 の壁紙のファイル（`wallpaper*.rs`・`eh3.rs`）・G-GEAR の `experiments/` に触れない。背景と小面は `engine`・`invitation`・`p_stuck` に依存しない。
- 打鍵の内容（キーの種類）を材料にしない。計測は合成の打鍵で。研究者の打鍵を記録に使わない（試視の起動は `env -u GSE_HANDMARK_SPIKE_MEASURE`）。
- 計測の CSV は OS の一時ディレクトリの `gse-handmark-spike/` に残るので、測った後は消す。
- 本線にマージしない。背景を参加者に出すのは EH3 の後。写し方（D）は仮。
