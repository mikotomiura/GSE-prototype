# 設計（v1・決めること 1〜6 を確かめた後）—— 手跡を main に入れる計画

> この文書は計画で、コードは変えない。決めること 1〜6 は研究者が 1 問ずつ選び、`decisions.md` に書いた。次に `/reimagine` で別の案を作り、比べる（主に判断 6）。

## 0. 材料の棚卸し（2026-11-08・読み取り専用のサブエージェント 2 本の報告をメインが一部一次で確かめた）

### 0.1 試作の実装（枝 `spike/handmark-stage`・351f94e5・merge-base 5d7c53be・main は 308 コミット先）

| 部品 | ファイル | 役割 | OS |
|---|---|---|---|
| 風 | `handmark_wind.rs` | 打鍵の時刻のリングバッファから、250ms ごとに風を計算して背景と帯へ配る。純計算 | 非依存 |
| 背景の層 | `handmark_stage_spike.rs`・`HandmarkStage.tsx`・`handmarkStageTrace.ts` | 壁紙の上・アイコンの下の透明窓に、霧・草・粒・波紋を描く | macOS のみ |
| 下の縁の帯 | `handmark_edge_strip.rs`・`HandmarkEdgeStrip.tsx` | 14pt の NSPanel。Dock の上端に沿う。全画面では画面の下端。覆われたら描画を止める | macOS のみ |
| ポインタ・ホイール | `handmark_stage_pointer.rs`・`input/handmark_pointer{,_macos}.rs`・`input/handmark_wheel_macos.rs` | カーソル 1 点を 16ms ごとに読む（権限不要）。左クリック。ホイールは専用の CGEventTap | macOS のみ |
| 背景を見る | `handmark_reveal.rs` | トレイから他のアプリを隠し、戻す | macOS のみ |
| 小面（閉じた） | `handmark_spike.rs`・`HandmarkSurface.tsx` | 右下の波紋。計測 CSV。判断 7 で閉じた | macOS のみ |
| 語の検査 | `handmark_stage_guard.rs` | 禁じる語の検査（陽性対照つき）。テストだけのモジュール | macOS のテスト |
| トレイ | `tray.rs` +119 行 | 閉じる・見る／戻す・入力ごとの入れ切り | macOS のみ |

- 打鍵は押下の時刻だけを渡し、一時停止中は渡さない（一次: 試作の lib.rs の差分 46〜48 行）。キーの種類と文字は渡さない。
- この経路から NDJSON には何も書かない。例外は計測の環境変数と、「背景を見る」の tracing の行の 2 つ。
- 試作の入口はすべて環境変数（`GSE_HANDMARK_STAGE_SPIKE` ほか 8 本）。本番には入口が無い。
- Windows 向けの実装は無い（一次: `input/` の handmark の 3 ファイルのうち 2 つが `_macos`）。
- CPU（1 コアに対する割合）: 背景は低電力モードで約 8〜9%、低電力を切ると約 15〜16%。帯は打たない間が約 2.2%、打つ間が約 7.2%（1 回ずつの比べ）。
- rebase の衝突の見込み: `lib.rs`（main 側 +1413 行）と `tray.rs`（main 側 +51 行・招待の項目の差し込みと `request_quit`）が高い。
- 注: 報告の「guard のテスト 23 件」は、一次で数えると `#[test]` が 13 件だった。判断には効かない。

### 0.2 設計の記録（枝 `docs/tangibility-design`）

- 要件の核（理論 §1.4）: 本人には自分の手のものと分かり、本人にも他人にも状態としては読めない。両方を測って確かめる。
- 自然世界の制約: 育たない・溜まらない。天気や季節で状態を表さない。打鍵は風のような行為の性質だけを動かし、打鍵が無くても漂う基層を持つ（why-interesting 判断 6）。
- 背景の写像は 1 秒に丸める（res=sec）。res=sub は机上の検査で打鍵の有無を写し、赤が多かった（expression 判断 3）。間隔比の案 D は未検査。
- 推定（`level`・`p_stuck`）を材料にも契機にもしない（expression 判断 2）。
- 帯（edge-strip 判断 3〜7）: 本体の非アクティブな NSPanel。中身は揺れる線 1 本・薄い霧・少しの粒。描画は入力があれば 30 回／秒、無ければ 10 回／秒。いつも出す。
- 「背景を見る」でどけた回数は記録する、と研究者が選んだ（window-boundary 判断 5）。ただし schema・同意・ADR は手当てしていない。
- ADR-040（手跡の入力を記録しない・Proposed）。D1 でポインタ・クリック・ホイールを背景の層の表現に使ってよいとし、D2〜D4 で記録にも推定にも入れず溜めないとする。Accepted の条件が 2 つ残る（一次: ADR-040 の 219 行目）。(a) Windows で位置とクリックを読めるかを確かめる。(b) macOS でホイールの tap が打鍵の tap の失効を増やさず、入れ切りを繰り返しても残らないことを確かめる。打鍵の tap の失効は 5 回の起動（約 23 時間）で 11 回あり、原因は切り分けていない。
- 漏れの確かめ方の既存の案: 自己認識（自分の形と他人の形の強制選択・取り違えも数える）と状態の漏れを、同じ刺激で対に測る。判定は信頼区間による 3 値。「偶然を上回らない」を「無い」の証明にしない。机上の検査では、基準の特徴で当てられる分を引いた残りを漏れと数える（why-interesting 判断 3）。
- 出典の食い違い: ADR-048 は「handmark-why-interesting 判断 14・15」を引くが、その文書の判断は 12 まで。同期と速さを区別する対照は expression-design の判断 14・15 にある。main に入れる ADR で正しく引き直す。

### 0.3 main 側（origin/main b9010318）

- ADR-048 D3 の日の終わりの問いは、すでに実装されている（`analysis/probe_arbiter.rs:592` の `DayQuestion`）。契機は夕方の途切れが主で、一時停止と終了が補助、翌日の拾い直しが 1 回。記録は `logger.rs:874` の `DayQuestionRow`。項目は動機づけの 1 つだけで、文の版を `items_version` で持つ。
- 事前登録 `docs/preregistration-stage1.md` の節 F（S1-F1〜F4）には、割付の方法・前期のずらし方・持ち越し・ラベルプールが「値は未定」として並んでいる。このタスクで決めた値は、事前登録の改訂のタスクへ渡す。
- main の ADR-040 は `ADR-040-nudge-not-in-core.md` で、番号がぶつかる。main の ADR は 049 まである。

## 1. 決めたこと（2026-11-08・研究者が 1 問ずつ選んだ。詳細と却下案は decisions.md）

| 判断 | 決めたこと |
|---|---|
| P | 後期の手跡は、まず macOS だけ。Windows は後で作ってから入れる。Windows 向けの引き継ぎを書く |
| 1 | 試作のほぼ全部を入れる: 風・背景・帯・カーソル・クリック・ホイール・「背景を見る」・トレイ。小面と計測の仕掛けは入れない |
| 1b | 参加者は手跡を切れる。切った・戻した時刻を記録し、翌日は割付に戻る。主の解析は ITT |
| 2 | 漏れは、記録から描き直して予測器 A（速さ・リズム・止まり＋pointer_bin）と B（A＋見た目）を比べる。AUC の差・日のブロックのブートストラップ 95%・1 日ずつ抜く交差検証・3 値・δ = 0.05。確認の段の前に本人の後期の日で回す |
| 3 | 割付の表は研究者が配布前に作り、SHA-256 を先に残す。初日は必ず表示、以後は 2 日ずつのブロック。日の区切りは `eh3::local_day`。日ごとに 1 行の行種 |
| 4 | ADR-050（入力を記録しない・枝の 040 を振り直し・macOS の射程で Proposed）と ADR-051（後期の形）の 2 本 |
| 5 | 既存の `day_question` に、手跡ありの日だけ同期・共存の項目を足す。契機と回数は変えない |
| 6 | 書き直し・PR 6 本: 文書 → OS 非依存 → macOS の背景・帯・トレイ → 条件 (b) の実測 → ホイールと「背景を見る」→ 机上の道具 →（文献の後）日の問いの項目 |

## 2. このタスクで変えるファイル（文書だけ）

- `.steering/20261108-handmark-to-main-plan/`（本書・`decisions.md`・`tasklist.md`）
- `docs/adr/ADR-05x-*.md` と `docs/adr/README.md`（決めること 4 の結果しだい）
- `docs/architecture/gse-design-map.md` §3.1 の R10
- `.steering/_handoff/`（実装の PR ごとの引き継ぎと、Windows 版の引き継ぎ `next-session-gse-handmark-windows.md`）

## 3. 確かめ方

- 文書だけなので `cargo test` は回さない。ADR の README の一覧と、地図の R10 の参照先が実在するかを grep で確かめる。
- code-reviewer と /cross-review（Codex を加える）。Codex に O1・段 1 の記録の本文を送らない。

## 4. 戻し方

- 文書だけなので、PR を revert すれば戻る。
