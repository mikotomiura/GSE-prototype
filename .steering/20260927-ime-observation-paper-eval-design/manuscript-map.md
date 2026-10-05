# 原稿の内部対応表（公開しない）

> 公開物 `papers/ime-observation/manuscript/outline.md` の内部の対応。公開物には判断の番号・`.steering/` のパス・GSE の語・`[Pn]`/`[Vn]` を書かない（`papers/README.md`・判断 36・76）ので、それらはここに持つ。
> 作成: 2026-10-04（G-GEAR・枝 `docs/ime-manuscript-outline`・引き継ぎ `next-session-ime-paper-writing.md` §2 の 1）。

## 1. 外枠の各部 ↔ 判断

| 外枠の部分 | 判断（一次） | メモ |
|---|---|---|
| 題（Working title） | 判断 15（T1）→ ★ 判断 149 で "Logging …" に固定（T4 の分岐は取り下げ） | 2026-10-05: `README.md`・`CITATION.cff`・`.zenodo.json`・`main.tex` の題も揃えた（判断 150 の実装）。凍結のタグは変えていない |
| 要旨の規則 | 判断 149-5 → ★ 判断 150-2 で事前登録 §6.1 に合わせて直した | 主の範囲 ＋ 外した割合（範囲・carry-over）＋ `all_trials`・層は 30 試行以上・Windows は別の構成概念・CPU は系ごと |
| attack-me（外枠） | round 1（判断 149）・round 2（判断 150） | round 3 は回さない。原稿の attack-me（stage `manuscript`）に round 1・2 の引き継ぎを渡す |
| Journal requirements | 判断 1・design.md §5 の 12（2026-09-28 の確認）・判断 145（10-04 の費用の確認） | ★ 2026-10-04 23:39 に `curl -sL`（cookie つき）で原文を取得して逐語で照合した（判断 147 の追記）。投稿は **ScholarOne**。Open Practices は References の直前（外枠の初稿の順を直した）。分量の上限・LaTeX の雛形は規定なし。投稿の直前にもう一度読む |
| Scope of the claims | 判断 6（精度評価が主・漏れても報告）・事前登録 §6.1（区間の幅で書く・評価語を使わない）・§6.8・§7・design.md §0 の「書かないこと」・`docs/research-positioning.md` の差分（設計上の排他性） | |
| Contributions 1〜4 | 判断 6 の (3)(1)(2)(4) | ★ **メインの選択（研究者が覆せる）**: ロガーを独立の貢献にせず、貢献 2「ロガーとその検証（主）」にまとめた。判断 6 の 4 つ ＋ 判断 146 の 1 つ ＝ 5 つに合わせるため。design.md §0 の C2（ロガー）は貢献 2 の前半に入る |
| Contribution 5（データセット） | 判断 146 | 「人の書字のデータ」「自然な入力のベンチマーク」と書かない（外枠の文で否定形で明記） |
| §5 Validation method | 事前登録 §2〜§6・§10・逸脱 D1〜D5 | 手法の節は凍結物から書く（引き継ぎ §2 の 3） |
| §10 The dataset | 判断 146 の (a)〜(c)・増える仕事 1〜3 | Gebru ら（未登録） |
| §11 Recommendations | design.md §5 の 10・事前登録 §6.8 | 結果より先に書かない（外枠に明記） |
| §12 Limitations | 事前登録 §7・§10.11・design.md §3（バッテリー） | |
| Open Practices Statement | `experiment/notes.md`（OSF 9nh7r・4jwzn） | GitHub ＋ Zenodo の DOI は M12 |
| Declarations | design.md §5 の 12（見出しの一覧） | Ethics は「人を対象としない」（判断 1） |
| 「Every number … copied … by a script」 | 引き継ぎ §3（JSON から写す・手で丸めない）・reproducibility-discipline | ★ 表を JSON から生成する道具（`manuscript/` に置く）は結果の節の前に作る |

## 2. 主張 ↔ 内部の根拠

| 外枠の ID | 内部の根拠 | 状態 |
|---|---|---|
| OB1〜OB3・OB5 | ★ 2026-10-05 に MS / Apple の一次文書を取り直した（`docs/references.md` の [V207]〜[V235]・WebKit のソース [V206]）。原稿は `sections/observability.tex`（§3・Table 2）。旧出どころ `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §3.2・§7.1〜7.5 は当たりを付けるためだけに使った | ★★★ **判断 151**: 調査メモ §7.5 の「135 個でゼロ」は C の定数だけで、AppKit の定数に変換中の範囲の属性と開始・終了の通知があった（WebKit が実際に出す）→ OB3 を狭め、OB5（アプリしだいの経路は両 OS にある）を足した。⚠️ 定数の数（C 101/9/25・AppKit 132/19/43）は 2026-10-05 の文書の値 → 計測の版の SDK のヘッダで確かめる（Mac・外枠の Open items）。⚠️ Windows の cloak の観察は機械とビルドが記録されていない（2026-08-22〜23・`.steering/20260822-ime-active-rewiring/`・`20260823-ime-active-cloak-rewiring/`）→ 原稿は「ビルドは記録していない」と書いた。macOS のウィンドウ一覧の「変換が始まってから候補窓」は観察の記録が見つからず、文書で言える形に直した |
| OB4 | 事前登録 §1.1・§10.3・§10.11（Two constructs） | |
| LG1 | `kit/formats/FORMATS.md`（`obs/1`）・`validate_logs.py`・`notes.md` の Step 0 | ★ 10-04 にソースで確かめた: macOS も押下と解放の両方で key 行を書く（`driver_macos.rs` の `handle_key`・`queue_row` は repeat と観測しないキーだけを落とす）。★ 10-05（判断 151）: macOS の観測するキーは `driver_macos/keymap.rs` の `is_observed_key`（英字・数字・主キー群の記号・Return・Tab・Space・Backspace・Forward Delete・Escape・矢印・F1〜F12）で、事前登録 §1.1 の書き方より狭い。Windows は `driver_windows/keyboard.rs` の `is_observed_key`（＋ `key_gate.rs`）。ヘッダの `manifest_sha256` は共通部分の manifest だけ（`main.rs` 56 行）。原稿は `sections/logger.tex`（§4・Table 3・Table 4） |
| LG2 | `kit/logger/src/`・`spec_predict.py` の selftest・★ Windows の安全弁は `main.rs` 273 行（実装）・777 行（テスト） | 判断 150 で LG2b に名指した。★ 10-05: Windows の監視ループは 2 つの経路に補助の信号 2 つ（`driver_windows/candidate.rs`：フォーカスした要素のクラス名・トップレベルの窓の走査）を論理和で足して「候補窓が開いているか」を判断し、安全弁の計時と閉じの見落としに使う（`main.rs` の `run_cycle`）。事前登録 §10.3 は 2 経路だけを書く → 原稿は注で補った |
| AG1〜AG8 | 事前登録の問い 1〜3・`notes.md` の結果ファイルの表 | ★ 判断 150 で番号を振り直した（旧 AG9 → AG7・旧 AG10 → AG8・round 1 の AG7/AG8 は RF1・KT1 に寄せた）。マーカーの時刻（`clock_sync.py` の出力）は外枠の「Claims and evidence」の冒頭で「タグから run ごとに作り結果と一緒に置く」と決めた |
| AG7 | `data.md`・`data.windows.md` の run checks | ★ Windows の試行 1 は外から止められた（低メモリでコーディング支援のセッションがシェルを終えた）・管理者権限の開始は数えない（研究者の判断）→ 原稿の試行の表にそのまま載せる。★ 起動ごとに寄託したか・理由も載せる（判断 150・Y28）。⚠️ 試行 2 の間に Surface で何が動いていたかは未確認（Surface で調べる・判断 150-6） |
| KT1 | 凍結の `delivery.py` 62〜76 行（対のつくり方・要約） | 判断 150 で外枠と `method.tex` に定義を写した |
| RC1〜RC3 | 事前登録 §6.8・§10.7 | |
| RT1 | 事前登録 §6.10・§10.9 | |
| DS1 | 事前登録 §3.1（**基準を満たすパイロットの生ログは本計測のデータと預ける** ＝ 凍結物が既に約束している・判断 110）・`pilot-macos.md` / `pilot-windows.md` の Raw logs | ★ 判断 146 の増える仕事 4「較正パイロットの生ログを含めるか」は、**預けることは凍結物で決まっている**。残るのは「データセットの一部として数えるか」だけ → 研究者に確認（§4） |
| DS2 | `data.md` の Deposit procedure | |
| DS3 | 判断 146 の (a)〜(c) | |

## 3. 引用 ↔ 内部の書誌（公開物は著者と年で引く・判断 76）

| 外枠の箇所 | 文献 | 内部の ID | 状態 |
|---|---|---|---|
| §2 Inputlog | Leijten & Van Waes (2013) | [V31] | 登録済み |
| §2 「a recent comparison lists as not supporting non-alphabetic writing」・hybrid logger | Crotti et al. (2026) Hylog | [V5] | 登録済み（⚠️ 逐語は対句で引く: "Translog II … is the only tool that supports non-alphabetic writing"・Table III） |
| §2 ScriptLog | 未定（Strömqvist ら / Wengelin ら） | — | ⚠️ 未登録 |
| §2 Translog-II | Carl (2012)・Zou & Carl (2026) | [P359]（Zou & Carl）／Carl (2012) は未登録 | 一部未登録 |
| §2 HMM の書字過程 | Uto et al. (2020) | [P270] | 登録済み |
| §2 中国語の書字の博士論文 | Lu (2020) | [P272] | 登録済み |
| §2 英日翻訳の過程コーパス | Carl, Aizawa & Yamada (2016)・生ログ [P360] | [P273]・[P360] | 登録済み |
| §2 本文を持たない打鍵データの公開 | Tappy / IKDD / Q-type | [P274]（ほか 2 系統の ID は §2 を書くときに確かめる） | 一部確認待ち |
| §2 打鍵の時刻から本文を推す攻撃 | Song, Wagner & Tian (2001) など | — | ⚠️ 未登録 |
| §3 MS の TSF・WinEvent・UIA・フック・DWM の文書 | Microsoft Learn ほか | — | ⚠️ 未登録 |
| §3 Apple の NSTextInputClient・Accessibility・IMK・CGWindowList・TIS | Apple Developer | — | ⚠️ 未登録 |
| §5 打鍵の速さ | Dhakal et al. (2018) | [P269] | 登録済み |
| §5 / §6 統計 | Wilson / Efron / Cameron ら / Bland & Altman / Cohen / Shrout & Fleiss / McGraw & Wong / Witten & Bell | [V179] [V188] [V181] [V184] [V185] [V186] [V187] [V189] | 登録済み（判断 98 の 7） |
| §5 読みの付与 | Takaoka et al. (2018) Sudachi | [V190] | ★ 登録済み（2026-10-05・判断 148）・`references.bib` の `takaoka2018`・`method.tex` が引く |
| §5 / §10 コーパスの出所 | 青空文庫 | [V191] | ★ 登録済み（同上）・`references.bib` の `aozora` |
| §2 計時の道具の検証（attack-me round 1 の X8） | Plant (2016)・Pinet et al. (2017)・Bridges et al. (2020) | — | ⚠️ 未登録（attack-me の接地で OpenAlex を確認済み・論文で引くときに登録） |
| §2・§12 打鍵の記録の漏れと書き手の特定（X13） | Monaco (2018) | — | ⚠️ 未登録（同上） |
| §10 データの説明書 | Gebru et al. (2021) Datasheets for Datasets | — | ⚠️ 未登録 |

★ 未登録のものは、その節を書くときに一次（Crossref・出版社・公式文書）で書誌を確かめて `docs/references.md` に append する（citation-ssot ルール 5: 未確認は provisional）。

## 4. 研究者に確かめたこと（外枠の段階）

→ ★ 2026-10-04 に 3 問とも推奨どおり（判断 147）: データセットは専用の短い節（§10）／パイロットの生ログは別の区分で数える／原稿は LaTeX（Springer の雛形）。⚠️ この機械（G-GEAR）には LaTeX も pandoc も無い（`command -v` で確認）。
