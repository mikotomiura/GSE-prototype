# `_handoff/` の索引 — ⚠️★★★ **まずここを読む**

> ⚠️ このディレクトリには **86 本以上**の引き継ぎメモがある（2026-08-31 時点）。
> ★ ファイル名も更新日時も**どれが現行かを決めない**（★ 古いメモを後から追記して
> mtime が新しくなることがある）。
> → ⚠️ **本ファイルが「いま有効なのはどれか」の単一の真実源である。**

---

## ★ いま有効なメモ

| トラック | ファイル | 状態 |
|---|---|---|
| ⚠️★★★ **転帰定義の一本化（★ 次の主タスク）** | `next-session-outcome-arbitration-adr029.md` | ✅ **現行・最優先**（2026-09-11・**未着手**）。★ `20260911-outcome-arbitration-and-o1-preflight` の **issue 007**。⚠️★★★ **ADR-009（4 択・stall onset 起点・paste は競合イベント）と ADR-024（2 値・away-gap 起点・**paste 自体が主イベント**）で主従が反転**しており、⚠️ **両者の関係はどの文書にも書かれていない**。→ ★ **新規 ADR-029** で「上書きか / 並存か / 第三の統合か」を理由付きで確定する。⚠️★★★ **モデルは Opus**・**`/reimagine` を設計段階で必ず起動**（`requirement.md` の運用メモで Yes 決定済み）。⚠️ **ADR-009 を Accepted にしない**（G1 が `n = 0/3`）／**ADR 本文を書き換えない**。★ **O1 はまだ開始していない**ので、ラベル定義を今のうちに確定する（★ 後から選ぶと**事後選択**になる）。⚠️ issue 007 の **AC 8 のパスが誤っている**（正: `20260911-outcome-arbitration-and-o1-preflight/_codex-review-007.md`）。★ **この issue の裁定で issue 009（修飾キー同時押下フラグ）の要否が決まる** |
| ⚠️ **申し送り F-1〜F-5**（★ **F-4 だけが残っている**） | `next-session-followups-f1-f5.md` | ⚠️ **一部消化済み**（2026-09-12）。★ **F-1 + F-2 は PR #197 で決着** —— `.github/workflows/supply-chain.yml` が toolchain / Rust 依存 630 crate / npm の 3 層を**週次**で検査する（⚠️ **門ではなく信号**: `main` に branch protection が無い）。★ **F-5 は PR #196 で決着**（`ci.yml` top-level に `permissions: contents: read`）。★ **F-3 は裁定 = 足さない**（⚠️ lint 結果は互いに上位集合でないので片側追加では非対称が消えない）。⚠️★★★ **残るのは F-4 のみ**（★ **mac 先行が必須** → 下の行）。⚠️ 新規申し送り **F-8**（Actions の版が可動タグ）／**F-9**（workflow の構文検査が無い）。★ 旧文（着手前の状況）は以下: ★ **F-1**（toolchain 由来 advisory の検知手段）が最優先 —— ⚠️ **security-checker と Codex が *独立に* 指摘**。★ `cargo audit` は `Cargo.lock` しか見ず **toolchain 同梱の cargo / rustc / std は射程外**で、⚠️ RustSec DB に `std` の advisory は **1 件も無い**（rust-lang/rust の repo advisory のみ）。★ 頻度は約 7 年で 6 件だが、⚠️★★★ **唯一の critical（CVE-2024-24576 / `std::process::Command`）が GSE の製品コード 20 箇所のクラスに当たる**。★ 他: **F-2** cargo-audit/dependabot（⚠️ npm audit は既に 7 件・全て devDeps）／**F-3** `stop-check.sh` に `--features package`（★ Windows 実測 10s→14s）／**F-4** default features の clippy を CI へ（⚠️★★★ **mac 先行が必須** → 下の行）／**F-5** `permissions: contents: read`（⚠️ **4 job に無い**・既存の穴・最も安い） |
| ⚠️★★★ **mac: default features の clippy を緑にする（★ F-4 の前提）** | `next-session-mac-default-clippy.md` | ✅ **現行**（2026-09-12・**未着手**・**mac 実機**）。⚠️★★★ **CI の clippy は `--features package` 付きの 1 箇所だけ**で、**default features のみの clippy は CI に存在しない**。★ **Windows は exit 0**（実測）だが ⚠️ **mac は未検証**（★ mac セッションが測ったのは `--features package` 付きの形）。⚠️ ローカル `stop-check.sh` は default features で回る**が WARN を出すだけでブロックしない** → ★ **mac 側で警告が出ていても誰も気づかない構造**。→ ⚠️★★★ **緑を確かめずに CI へ足すと main が即赤になり全作業が止まる**（★ R-1 で学んだ順序: ① mac で緑 → ② CI に足す）。⚠️ **本メモは CI には足さない**（★ そこで止める）。完了報告に「mac の default features clippy は exit 0」と明記すること |
| ~~R-2〜R-5 の裁定~~ | `next-session-r2-r5-decisions.md` | ✅ **完了**（2026-09-12・**PR #193 / #194 / #195** がすべて main へ）。★ **R-2** = toolchain を **1.98.1** に固定（⚠️ 初稿の 1.94.1 は本機の値で、CI は 1.98.1 だった＝巻き戻しだった）／★ **R-3** = ⚠️ **`1.87` は誤り**で **1.88** へ訂正（依存 `time` 系が要求）／★ **R-4** = 無音 skip を `panic!` へ ＋ CI に env 前提の検査 step。⚠️★★★ **CI 実測で元の問いに答えが出た** —— **Windows: `USERPROFILE`=set / macOS: ⚠️ `USERPROFILE`=unset・`HOME`=set**（★ mac 側の保護は `HOME` だけに依存していた）／★ **R-5** = ✅ **閉じた**（ラッパー 3 回連続成功・台帳が自動計上）。⚠️ 申し送り **F-1〜F-5** は下の 2 行へ。★ **F-6（予算上限 300,000 据え置き）は裁定済み** |
| ⚠️★★★ **mac 側 clippy と CI 検査ゲート** | `next-session-mac-clippy-and-ci-gate.md` | ✅ **完了**（2026-09-12・mac 実機 → **PR #190** → ★ **main へマージ済み**（`5900ab4`）。⚠️ 旧記述「main へのマージは未実施」は失効）。★ 結果: mac 側 clippy **7 件 → exit 0** ／ 起票 10② を閉じた（⚠️ **store だけでは happens-before が成立しないので load 4 箇所も Acquire へ**） ／ **R-1 達成 = CI の check 両 OS ＋ frontend-check が pass**（★ clippy step は Win 42 秒 / mac 49 秒・`timeout-minutes: 30` に 24 分以上の余裕）。⚠️★★★ **R-4 は「観察できない」ことが判明**（★ テストが skip を沈黙で表現するため、CI ログで通過と skip が区別できない → 先にテストを loud にする作業が要る）。⚠️ **R-2 / R-3 / R-5 は未決**。⚠️ **新起票: `IME_ACTIVE` の Ordering が 7 箇所 Relaxed**（★ `hook_windows.rs:603` = フックコールバック内を含むので Windows 実機と対で別 PR）。⚠️ **ディスクだけ余裕が無い**（★ run 後の空き 16 GiB に対し threshold 15 GiB・`target` は 3.0 GiB → 次の run で cargo-sweep が走る見込み）。★ 詳細は当該メモ §8。 ⚠️ 以下は**着手前の記述**（履歴）: ★ Windows 側は clippy **51 件**（lib/bin 33 ＋ `#[cfg(test)]` 18）を潰して `--all-targets` 込みで **exit 0** にした（⚠️ 当初 29 件と見えたのは **lib が落ちて bin が解析されていなかった**ため。★ 受け入れ条件は件数ではなく exit 0 に置くこと）。⚠️★★★ **mac 固有ファイル**（`hook_macos.rs` / `ime_macos.rs` / `observe_macos.rs` / `sensors_macos.rs`）は **Windows で 1 行もコンパイルされない**ので、★ **mac 側の件数は原理的に本機から測れない**。⚠️ `ime_macos.rs` の `#[allow(clippy::new_without_default)]` は **Windows で未検証**。★ 本タスクの主目的は **R-1（CI に clippy step を足す）を足せる状態にすること**（⚠️ mac が赤のまま足すと **main の CI が即赤になり全作業が止まる**）。⚠️ 研究者判断 **R-1〜R-5 は全て未決**（CI clippy / toolchain 固定 / MSRV 1.87 / CI の `USERPROFILE`・`HOME` / `run-codex-review.sh` の Windows 対応）。★ 一次資料は `.steering/20260912-post-mac-sync-cleanup/decisions.md` 判断 8/9/12/13/14 ★★★ **2026-09-12 追記 (§7)**: mac 側で**着手前の実測**を済ませてある —— ⚠️ `-D warnings` は **exit=101**（★ 内訳 **7 件**: `hook_macos.rs` ×3 / `ime_macos.rs` ×1 / `lib.rs` ×3。⚠️ **`lib.rs` の 2 件は `#[cfg(target_os = "macos")]` 内で Windows からは原理的に見えなかった**）。⚠️ **「7 件」を受け入れ条件にしない**（lib が緑になるまで bin が見えない）—— 基準は **`exit 0`**。★ **研究者判断**: スコープは **clippy ＋ `blockers.md` 起票 10②（`IME_OPEN.store` を Relaxed→Release・⚠️ `ime_windows.rs:289` が対なので両方・**別コミット**）**、⚠️ **起票 10① は入れない**（VK 分布が動き `HMM_VERSION` 判断が要る → 起票 6 と一緒に idea 議論へ）。**R-1 = 緑にしてから同じ PR で CI に追加**。⚠️ 実行は**次セッション**（`/start-task` から）。 |
| ~~macOS 実機での IME 確定/放棄の検証~~ | `next-session-mac-ime-shadow-verification.md` | ✅ **完了**（2026-09-12）。★ **AC 6 合格**（確定 3 → `abandon:false` / 放棄 3 → `abandon:true`・`dwell_ms` も妥当）。⚠️★★★ **ただし「合格」だけでは終わっていない**: ★ **起票 6 の懸念は当たった** —— **ライブ変換（macOS の既定 = ON）では ESC 1 回が「読みに戻す」**であり放棄ではないので、⚠️ **`abandon` が系統的に過大**（確定 1 回が `放棄1＋確定1` に分裂）。★★★ さらに **新規 起票 9** —— ⚠️ **macOS の かな キーを Windows の「半角/全角」定数に流用してトグル扱いしており、偶数回押すと `IME_OPEN` が実体と反転したまま残り、日本語変換が丸ごと `ime_shadow` から欠測する**（★ 実測: 🌸 を確定したのに 0 件）。⚠️ 由来は `5e3c85c` で PR #182 の変更ではないが、**#182 が入ったことで害が重くなった**。★★★ **起票 9 は 2026-09-12 に修正済み**（`0x68` の写像を `VK_KANJI` → `VK_DBE_HIRAGANA` に直し、遷移表を **`input/ime_mode.rs`（OS 非依存）へ 1 本化**して複製を両 OS から削除。★ 変異テストで赤を確認済み・657 passed / ゴールデン 15 一致 / schema drift なし）。⚠️★★★ **起票 6 は意図的に直していない**（★ 判断 12）—— **設計上の争点があり、ライブ変換 ON を直すと OFF 側で放棄が過小になる**うえ、`esc_count` 化は schema 追加（ADR-005）で **特徴量設計が動くなら手戻り**になる。→ ★ **idea 議論の入力として残す**。★ O1 の再配布は **idea 議論 → Mh-D 全体の修正 → 再配布** の順（⚠️ O1 未開始なので配布前の締切は無い）。⚠️ **残件 = 既配布ぶん（v0.1.34 / v0.1.35）の事後補正は未検証**。→ ★ 一次資料は `design-008-macos-ime-shadow.md` **§11** / `blockers.md` **起票 4 / 6 / 7 / 9** |
| **`.idea` → SSOT の取り込みと昇格（★ 進行中）** | `next-session-idea-to-ssot-intake.md` | ⚠️ **一部消化済み**（2026-09-11）。★ **T1 = 不要**（mac 側が取り込み完了）／**T2 の issue 008 = 完了**（★ PR #182・CI 全緑）。⚠️ **残 = issue 007（→ 上の行）／issue 009（007 の裁定待ち）／T3 / T4（issue 未分解）**。⚠️★★★ **本文の `v0.1.34` は失効**（★ 2026-09-11 に **`v0.1.35`** がリリース済み）。⚠️★★★ **本文の「配布後は原理的に復元不能」も失効** —— ★ `key` 行の `category` は `escape` と `enter` を**別カテゴリ**として残すので、確定/放棄は**事後に再構成できる**（`20260911-outcome-arbitration-and-o1-preflight/decisions.md` 判断 7）。★ 以下は当時の記述: ★ 下の `intake-windows-and-continue.md` **§2（ブランチ取り込み）を issue 単位に分解したもの**。⚠️★★★ **研究者が案 C（系統ごとに PR）を採択済み**。⚠️★★★ **タスクは 4 本に分割されている**（1 セッション 1 タスク）: **T1** `20260911-intake-arbitration-branch`（取り込み・**issue 001–006 分解済み・次はこれ**）／ **T2** `20260911-outcome-arbitration-and-o1-preflight`（転帰定義の一本化 ＋ O1 配布前実装・**issue 007–009 分解済み**）／ **T3** `20260911-mhd-inference-ssot`（MhD 推論アーキ・⚠️ **ADR-008 D8 と WP5 I2 が正面衝突**・**調査済み/issue 未分解**）／ **T4** `20260911-practice-portrait-ssot`（Practice Portrait・**調査済み/issue 未分解**）。★ T2–T4 は T1 完了待ち（取り込み後の docs に既に書かれている可能性があり重複判定ができないため）。★ T3/T4 は各ディレクトリの `_survey-*.md` が一次資料。⚠️★★★ **ADR-023〜028 は既に書かれている**（未マージブランチにある）—— ★ `.idea/20260907` の `W-2` は **ADR-027 が**、`.idea/20260908` の `W-3` は **ADR-028 が既に閉じた**。★ Wave 0 = 取り込み 6 件（**Loop Engineering 適合**・AC は exit code で回収可）／ Wave 1 = 転帰定義の一本化（★ **最優先**・`/reimagine` 必須）＋ O1 配布前に手遅れになる実装 2 件。⚠️★★★ **O1 はまだ開始していない**ので、`macOS の IME 確定/放棄判別`（P1）と `修飾キー同時押下フラグ`（P3）が**今なら間に合う**（★ 配布後は原理的に復元不能） |
| ⚠️★★★ **G-GEAR の成果を取り込み mac で続ける** | `next-session-prompt-intake-windows-and-continue.md` | ⚠️ **§2 を上の新メモへ委譲した**（2026-09-11）。★ **§1 は 2026-09-10 に決着済み**（Windows 実機の busy-loop 実測で `1 コア = 100%` 基準に確定・×16 は誤り）。★ **§3 / §4 / §5 はまだ有効**（★ mac の**スリープ跨ぎ 30 分**が最優先）。★ 以下は当時の記述: ✅ **現行**（2026-09-10・**未着手**）。★ **`next-session-prompt-post-windows.md` の後継**（⚠️ 向こうは G-GEAR が実測結果で更新済みなので**両方読む**）。⚠️★★★ §1 = **Windows の「CPU FAIL 相当」が本当か**を Windows 実験で決着させる（★ `\Process(x)\% Processor Time` が**合計基準なら ×16 は誤り**で FAIL は偽の警報。⚠️ **配布可否に直結**）。★ §2 = G-GEAR ブランチ `feat/resumption-outcome-arbitration` の取り込み（⚠️ **88 コミット / 199 ファイル / +28,054 行**・ADR-023〜028 ＋ metrics.rs +909 行を含む → ★ **単純マージにしない**）。★ §3 = Windows が残した宿題 3 件。★ §4 = mac の残り（**スリープ跨ぎ 30 分**が最優先）。★ §5 = 決着済み一覧（⚠️ 蒸し返さない） |
| ★ **Windows の受け入れ検査（★ G-GEAR が実測結果で更新済み）** | `next-session-prompt-post-windows.md` | ⚠️ **一部消化済み**（★ §1 = Windows 実測**完了**・§3 の研究者判断 5 件**全て決着**）。★ **§2-1 のスリープ跨ぎ検証**と §5 の積み残しは**まだ有効**なので、上の新メモと**併せて読む**。★ 以下は当時の記述: ★ §1 = Windows から返る結果の**受け入れ検査**（⚠️ 8 列か / 7・8 列目が空か / CPU% を mac と直接比べていないか）と `notes.md` の締め。★ §2 = mac 側の小さな残り（**起動の山を 1 秒間隔で 5 分**／未マージ 2 ブランチ／廃棄可 2 ブランチ）。⚠️ §3 = 研究者判断 **5 件**（Drive の zip 差し替え／`TIMEOUTTEST_*` の削除／`MAX_BYTES` 48→32 MB／**G1 の計器の版**／**G1 の配布関門 3 件**）。⚠️★★★ **starvation の追加対処はしない** —— ★ 診断 `tap_enabled` を入れたので**次の Down のログで機序が決着する**まで待つ |
| ~~稼働コストの再測（macOS）~~ | `next-session-prompt-o1-runtime-cost-round2.md` | ✅ **完了**（2026-09-05・PR #158）。★ 8 時間 **1 本**を完走（806 サンプル ＋ 起動前の基線 3 行）。⚠️ **起動の山は 35 s 間隔では拾えないと判明**（★ 孤児回収は 1.5 秒）→ 1 秒間隔の別 run が残り。⚠️ **集計器の欠陥を 3 件**見つけて直した。★ 以下は当時の記述: ★ 8 時間 **1 本**だけ（⚠️ 対照は 2026-09-04 に廃止）。① **エネルギー影響**（`top -stats power`・新規追加・⚠️ GSE 稼働下は未検証）② **起動時のコスト**（★ 前回は稼働 4h15m 後から測ったので未測定）③ **PR #151 の 2 回目の実機検証**（★ 孤児が 1 本残っている）。⚠️ CPU / メモリ / NDJSON は**測り直さない**（★ 前回で有効） |
| ★★★ **設計スライドの作り直し（技術・アーキ・研究手段）** | `next-session-design-slides.md` | ✅ **現行**（2026-09-04・**未着手**）。★ 研究者指定＝全体アーキ／ワークフローと各層の処理・計算過程／モデルの更新・昇格の実施手段／各モデルの選定理由とアーキ解説／各アーキのつながり。⚠️ **証明などの綿密な内容は技術設計書へ委託**。★ **図を積極的に使い、必要な箇所は具体的に描く**。★ デザイン基盤＝ 研究者指定の `deck_temp1.pptx`（★ 10.0×5.62 inch・レイアウト互換は 2026-09-04 に実測済み）。⚠️★★★ **着手前に `md2pptx.py` の穴 4 件を塞ぐ**（テンプレート未対応／スライドサイズの上書き／見本 6 枚が残る／**画像を置けない**） |
| ~~Windows 実機（G-GEAR 専用）~~ | `next-session-prompt-windows-runtime-cost-and-orphan-verify.md` | ✅ **完了**（2026-09-09/10）。★ 8 時間実測・孤児回収・overlay の idle 確認まで実施（`.steering/20260904-windows-orphan-verify/`）。⚠️★★★ **CPU% の OS 間定義差を見落とし、後から訂正**した（★ 換算すると FAIL 相当という主張 —— ⚠️ **その換算自体が正しいかは未決**。上の新メモ §1）。★ 以下は当時の記述: ⚠️★★★ **走らせる前に 1 分スモークで 8 列を確かめること**（★ サンプラが 6 列しか出さない欠陥を 2026-09-05 に直した・**Windows 実機では未実行**）。⚠️ 対照は廃止／サンプラを先に起こす／**CPU% を mac と直接比べない**。★ 以下は当時の記述: ★ ① 孤児回収 (PR #151) の実機検証（⚠️ **OS 再起動で `session_end` が書かれるかは未知**）／② 稼働コスト 8h × 2（⚠️ **Windows 側スクリプトは一度も実行されていない**）／③ overlay のクリック奪取。⚠️ **Mac では代替できない仕事だけ** |
| ~~O1 配布前の残り（Mac 側）~~ | `next-session-prompt-o1-preflight-4.md` | ✅ **完了**（2026-09-05）。★ **② 送信 timeout を実測**（PR #159・180 → **300 秒**）／**③ 稼働コストも実測**（PR #158）。⚠️★★★ ゲートは **20 件 / 0 件 = 配布してよい状態**になり、**v0.1.32** を切って O1 配布 zip を作り直した（★ G1 は sha256 不変で温存）。★ 以下は当時の記述: ★ ④ 孤児回収は **PR #151 でマージ済み**／① は研究者判断 C で `docs/o1-roster-operations.md` へ／⑤ は**誤りだったので訂正済み**。★ **残 = ② 送信 timeout の実測（リリース判定の唯一の赤）／③ 稼働コストの実測** |
| **G1 / O1 の収集前の所見** | `g1-o1-precollection-findings.md` | ✅ **現行**（2026-09-01）。★ 調査 2 本の所見。⚠️ **配る O1 バイナリが古い**／被験者の画面に生の `**`／O1 同意文書の版が固定されていない |
| **G1 / O1 の実物配備** | `next-session-prompt-g1-o1-gas-deployment.md` | ✅ **現行**（2026-09-01）。★ PR #140 を実 Apps Script へ配備し、収集前の穴を埋める。⚠️ **ブラウザ作業あり**（`browser-verification` 必須） |
| **O1 リリース / 配布** | `next-session-prompt-o1-v0-1-31-and-open-fronts.md` | ⚠️ **一部消化済み**（2026-08-31）。★ §1（PR を畳む）・§2（fork 遮断）・§3（ディスクガード指摘 4 件）・§7（G1/O1 進捗調査）は **PR #139 で完了**。★ **残っているのは §4 (v0.1.31) / §5 (README 承認) / §6 (送信 timeout) / §8 (積み残し)** —— それらは上の新メモにも引き写してある |
| **未踏 2027 / 研究の主張** | `next-session-research-positioning-fix.md` | ✅ **現行**（2026-09-01）。★ `docs/research-positioning.md` の ADR-018 / ADR-015 未追随 4 件と de Jong 2020 のカード化 |
| ★★★ **層 A の試視（PS-Q5 を閉じる）** | `next-session-layerA-shishi.md` | ✅ **現行・最優先**（2026-09-03）。★ **試視ハーネスは完成済み**（`experiments/20260902-expression-layerA-visual/`・機械検査 Python 30 / ページ内 12・全緑）。⚠️★★★ **回すのは研究者本人**（★ N=1）。⚠️ **実施前に `layerA.config.json` を開いてはならない**（★ 写像が書いてある）。★ **判定**: 未教示 = 他者が読める上限 / 教示後 = 本人。⚠️ **`aperture`（静的符号）を先に回す**（★ ADR-022 D1 が A-7 を落としたため）。★ 併せて **M-11（`participant-setup-guide.md` / `data-privacy` への周知）＝ 実参加者投入前のブロッカー** |
| 表現層の具体設計（OS 制約 → 試視） | `next-session-expression-layer-concrete.md` | ✅ **完了**（2026-09-03・`149f147`）。★ **第 1 目標＝ OS 制約の調査を閉じ ADR-022 を起票**（★ D1–D9）。⚠️★★★ **A-7（1–3 Hz の持続振動）は第 1 版の符号から外した** —— iOS では成立せず、Android はライブ壁紙で成立するが**画面点灯中のみ**で、★ **符号が OS で違うと OS が表現と交絡する**ため。★ **表示面は OS ごとに別**（iOS = ロック画面ウィジェット / Android = ライブ壁紙）。⚠️ **第 2 目標＝ PS-Q5 の試視は、ハーネスを作ったが *まだ回していない*** → ★ **下の行へ** |
| 表現チャネルのその他の繰り越し | `next-session-expression-channel-followups.md` | ✅ **現行**（2026-09-02）。★ 逐語照合の続き（**V106 → P229 → P224 → V104 → P236**）／⚠️ **`.pptx` / `.docx` の実地確認（2 回繰り越し中）**／一次未到達 6 件の入手／Stage 4 の逆側／ADR-019 D6 の実装 |
| 表現チャネル（`.idea` §7 の未決事項 8 件） | `next-session-expression-channel-open-items.md` | ✅ **完了**（2026-09-02・`d68d302`）。★ **8 件すべて裁定し ADR-021 を起票**。★ 繰り越し 2 / 4 / 5 も閉じた。⚠️ **残りは上の 2 行へ** |
| GSE 設計の深掘り（表現 → 身体回帰 → Mh-D 再定義） | `next-session-gse-design-deepening.md` | ✅ **完了**（2026-09-02・`d68d302` でコミット済み）。★ B / C を閉じ、**ADR-019 / ADR-020** を起票、`references.md` に **43 件** append、未踏提出資料 3 本を更新。⚠️ **A は積み残し**（→ 上の行） |
| スマホ表現チャネル | `next-session-prompt-smartphone-expression-channel.md` | ⚠️ 別トラック（Windows 側） |
| 表現チャネル SSOT の積み残し | `next-session-prompt-expression-channel-followups.md` | ⚠️ 別トラック |

★ **セッション引き継ぎではない運用メモ**（★ 上の表の対象外）:
`mac-runner-disk-cleanup-prompt.md` —— self-hosted mac ランナーのディスク枯渇時に
Mac 側セッションへ貼る手順。⚠️ **2026-08-31 に一度実行済み**（★ 恒久対策は PR #139 の
ディスクガードと週次掃除）。

⚠️ ★ **上の表に無いものは、すべて「過去の記録」として扱う。**
★ 読んでよいが、⚠️ **そこに書かれた状態を現在の事実として使わない**。

---

## ⚠️★★★ 明示的に無効化したメモ

| ファイル | なぜ危険か |
|---|---|
| `next-session-prompt-o1-v0-1-31-and-timeout.md` | ⚠️ 「PR #132 で 0600 欠陥が直った」前提。★ **その修正は不完全で PR #136 で塞ぎ直した**。さらに未対応 HIGH 2 件が抜けている |
| `next-session-prompt-o1-release-and-rebuild.md` | ⚠️ 判定条件・操作順に**誤りが 4 件**（★ 後継メモの §0-1 に一覧がある） |
| `next-session-prompt-o1-macos-distribution.md` | ⚠️ 「最新タグ `v0.1.29` を使え」— ★ **`v0.1.29` は O1 を含まない**。この記述が実際に事故を起こした |
| `next-session-prompt-mitou-2027-rewrite.md` | ⚠️ **PR #135 で完了済み。**★ 前提（参考文献を提案書に置く / 段階呼称 Lv1〜Lv4 / 完了条件は「時間・往復」）が**すべて現行と食い違う**（ADR-018 で完了条件を外した） |

★ これらは**ファイル冒頭に上書き表示を入れてある**（★ 入っていないものを見つけたら足すこと）。

---

## ⚠️ 引き継ぎメモの扱い（★ 直近 2 セッションの教訓）

★ 引き継ぎメモは **三次資料**である（`verify-before-claiming` ルール 1）。
⚠️ **根拠にしてはならない。** 当たりを付けるためだけに使う。

★ 実際に、直近 2 セッションで**メモの記述を 5 か所訂正**した:

| # | メモの記述 | ⚠️ 実体 |
|---|---|---|
| 1 | 「`Cargo.lock` に該当バージョンが 2 箇所」 | ★ 2 件目は無関係な第三者クレート `schannel` |
| 2 | 「`Probe scheduler thread started` が出ていないこと」 | ⚠️ **O1 でも必ず出る**（判定条件そのものが誤り） |
| 3 | 「制約は 2 つ」 | ⚠️ **3 つ**（Apps Script の実行時間上限 360 秒） |
| 4 | 「削除は**一時停止 → 削除**の順」 | ⚠️★★★ **O1 では逆**。★ そのまま渡して 2 回失敗させた |
| 5 | 「E-1 の不具合が踏めるのはここ」 | ★ 既に修正済みで再発していなかった |

→ ⚠️ **メモに書いてあることは、手を動かす前に一次資料（コード / 実行結果）で裏を取る。**

---

## ★ 新しいメモを作るときの規約

1. ★ **このファイルの表を必ず更新する**（⚠️ 更新しないなら作らない）
2. ★ 置き換えた旧メモの**冒頭に上書き表示を入れる**（⚠️ 消さない —— 経緯が失われる）
3. ⚠️ **数字と状態には「いつ測ったか」を書く**（★ 「通過 18 / 未達 1」だけでは後で嘘になる）
4. ★ 「済んでいること」と「未実施」を分けて書く。⚠️ **未実施は未実施と書く**
