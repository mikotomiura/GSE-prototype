# 設計（確定版 — v1 ＋ v2 のハイブリッド・/reimagine 1 回目）

★ **2026-09-28: `/reimagine` の結果、ハイブリッドを採用した**（decisions.md 判断 14）。
土台 = 初版 v1（`design-v1.md`・判断 10 の訂正入り）、取り込み = 再生成案 v2（`design-v2.md`）の 8 点。
★ v2 由来の箇所には **〔v2〕** と付けた。比較は `design-comparison.md`。

⚠️ 本書は評価プロトコルの**設計**である。確定版を
`experiments/<date>-ime-observation-accuracy/preregistration.md` として**実測前に凍結**する
（★ 凍結は §1.1a の較正パイロットの結果を根拠として書いてから。★ OS ごとに段階凍結する —— §6）。

## 0. 論文の主張（外枠）

**題**（★ 判断 15 で T1 に決定・E2 の結果次第で見直す）: *Observing Japanese IME conversion without recording text:
Observability limits, a cross-platform logger, and a synthetic-input validation*（BRM）

★ 〔v2〕 **評価は 3 層**に分ける（⚠️ L1 だけでは BRM の読者に答えていない —— 事象レベルで一致していても、
誤りが特定の条件に偏れば**書字研究者が計算する集計量**は系統的にずれる）:

| 層 | 問い | 節 |
|---|---|---|
| **L1 事象の一致** | 1 回の変換ごとに、検出・時間・放棄・ナビが IME 自身の状態と一致するか | §1.2–1.3 |
| ★ **L2 測度の一致** | 書字研究者が実際に計算する集計量（テキストごとの平均変換時間・変換の数・放棄率・変換中の時間割合）が一致するか | §1.3a |
| **L3 漏洩** | ログから本文・本文の同定がどこまでできるか | §2 |

| # | 主張 | 根拠（現存 / これから作る） |
|---|---|---|
| C1 | Windows では他プロセスの TSF composition を**権限によらず**観測できず、macOS には公開 API が無い。したがって content-free な IME 観測は窓イベントか打鍵推論のどちらかに限られる | 現存: `survey-input-channels.md` §7.1–7.6（⚠️ 論文用に一次の MS / Apple 文書へ引き直し、`[Pn]` で接地する） |
| C2 | 本文を取らずに「1 変換 = 1 行」（`dwell_ms` / `nav` / `abandon`）を両 OS で記録できる。ただし OS ごとに**由来と母数が違う**（Windows = 候補窓が出た変換・窓イベント由来、macOS = かな入力の一区切りすべて・打鍵推論） | 現存: `ime_compose.rs` 冒頭の表・`schema_dto.rs` `ImeShadow` |
| C3 | その記録は IME 自身の状態と◯◯の精度で一致し（L1）、書字研究者が使う集計量も◯◯の範囲で一致する（L2）（シナリオ別・速さ別・OS 別・IME 別） | **これから**: 評価 E1 |
| C4 | 記録から本文をどこまで復元できるか（開集合の復元と閉集合の同定） | **これから**: 評価 E2 |
| C5 | 常駐コストは実用範囲 | ★ **これから**: 評価 E3（公開する観測部だけを両 OS で再計測・判断 12）。⚠️ 既存値は GSE アプリ全体の値で、0.98% は**無効**（§3） |

⚠️ **書かないこと**: 「世界初」「先行が存在しない」（`docs/glossary.md` の禁止用語）。差分は
「[P270] は IME を迂回（テキスト水準ロガー）、[V5] は本文の読み取りに依存」という**設計上の排他性**で書く（`research-positioning.md:816-821`）。

## 1. 評価 E1 — 精度（主評価）

### 1.1 系の構成

```
[シナリオ実行器] --合成キー/マウス--> [OS の IME] --> [参照入力欄 (自作アプリ・前面)]
                                      |                  └─ 正解ログ: 自プロセス内の composition イベント
                                      └─(同時に)--> [GSE の IME 観測部] --> ImeShadow 行
```

- **参照入力欄（正解の源）**
  - macOS: `NSTextInputClient` を実装した最小の Cocoa アプリ。**プロトコルへの呼び出しをすべて**（`setMarkedText` の長さと `selectedRange`・`insertText`・`unmarkText`・`firstRect`）時刻つきで記録する。
    - ⚠️★ **2026-09-28 訂正**: 初版は `unmarkText` を「取消」としていたが**誤り**。Apple の一次文書は逐語 "The text view should accept the marked text as if it had been inserted normally."（`unmarkText()`）＝ ★ **確定側**である。
    - ⚠️ **取消は「marked text が空になり、非空の `insertText` が続かない」**と見込むが、⚠️ **Apple の文書に根拠が無い**。★ **呼び出しの順序も文書に書かれていない**（`NSTextInputClient` / `NSTextInputContext` の一次文書を 2026-09-28 に確認）。→ ★ 1.1a の較正パイロットで確定する。
    - ⚠️ プロトコルに**候補窓の表示を知らせるメソッドは無い**（`firstRect` は候補窓の位置決めに呼ばれうるが、表示の通知ではない）。→ ★ macOS 定義（かな入力の一区切りすべて）は候補窓を要らないので影響は無いが、⚠️ **macOS で「Windows 定義の正解」は作れない**。
  - Windows: ★ **2 経路を較正パイロットで試して選ぶ**（2026-09-28 変更）。
    - (a) **IMM 互換**: 自窓で `WM_IME_STARTCOMPOSITION` / `WM_IME_COMPOSITION`（`GCS_RESULTSTR`）/ `WM_IME_ENDCOMPOSITION` と `WM_IME_NOTIFY`（`IMN_OPENCANDIDATE` / `IMN_CLOSECANDIDATE`）。⚠️ MS の一次文書（*IME and TSF Accessibility in Windows XP*, 2002・アーカイブ）は逐語 "all non-TSF-enabled applications, except 16-bit and console window applications, are empowered by the TSF-based text services through a compatibility layer" と書くが、⚠️ **どのメッセージが届くかは書いていない**。
    - (b) **TSF 直受け**: 参照入力欄を TSF 対応アプリにし、`ITfContextOwnerCompositionSink`（`OnStartComposition` / `OnUpdateComposition` / `OnEndComposition`。逐語 "implemented by an application to receive composition-related notifications"）＋ 候補一覧は `ITfUIElementSink` で受ける。★ MS-IME は TSF の IME なので、**翻訳層を挟まない**。
    - ★ どちらも**自分のプロセス内の観測**なので `docs/agent-shared.md` 制約 7 に触れない（判断 2）。
  - ★ 〔v2〕 **正解ログは content-free にする**: 記録するのは**イベント種別・長さ・時刻だけ**（確定文字列は記録しない）。★ 照合には長さで足りる。→ 公開しても、コーパスの著作権や漏洩の議論が要らない。
- ★ 〔v2〕 **oracle（シナリオ実行器の意図の記録）を同時に取る**: 「候補 2 つ目で確定」「ESC で取消」「矢印 3 回」のような意図を試行ごとに書き出す。
  - ★ **正解の検証だけに使う**。⚠️ 観測部の評価には使わない（macOS の観測部は打鍵推論なので、打鍵由来の oracle で評価すると**循環する** —— 判断 2 の背景と同じ）。
  - ★ **oracle ↔ 正解の不一致 = 「IME がシナリオの意図どおりに動かなかった」試行**。⚠️ 捨てずに**件数と型を報告する**。★ 観測部の評価（正解 ↔ 観測）には**含める**（除外すると IME が素直に動いた易しい試行だけが残る）。
- **シナリオ実行器**: macOS = `CGEventPost`（memory `macos-app-visual-check-workflow`: 合成キーは IME を実際に駆動する）、Windows = `SendInput`（scan code）。
- **時計**: 正解ログと ImeShadow は別プロセスなので、両者に**同じ時計**を使うか、開始時に同期マーカー（特定キー列）を打って対応づける。
  ⚠️ **GSE の `t` と macOS の `dwell_ms` は壁時計（`SystemTime`）由来で単調ではない**（`ime_compose.rs` 冒頭）。→ ★ 参照入力欄は**壁時計と単調時計の両方**を記録し、run 中に時計が跳んだ区間は除外として数える（NTP の同期も run 中は止める）。

### 1.1a 較正パイロット（★ 2026-09-28 追加・判断 11）

- **目的**: 正解の定義（開始・確定・取消・候補窓）を**実機の呼び出し列**で決める。★ Apple も MS も呼び出し順を文書にしていないため。★ 〔v2〕 あわせて**計器そのもの**（正解・入力・時計）が正しいことを確かめる。
- **やること**:
  1. 参照入力欄**だけ**を動かし、S1〜S15 を各数回流して呼び出し列を記録する。Windows は (a) / (b) の両経路を記録し、★ **両者が同じ区間を返すか**も見る（食い違えばそれ自体を報告する）。
  2. 〔v2〕 **oracle ↔ 正解の一致率**を測る（低ければシナリオ・タイミングを直す）。
  3. 〔v2〕 **合成入力が観測部のフックにも届くか**を、観測部の**生の打鍵行だけ**で確かめる（★ ImeShadow 行は見ない）。★ 2026-09-28 に `src-tauri/src/input/` を grep し、合成入力（`LLKHF_INJECTED` 等）を捨てるコードが**無い**ことは確認済み —— ⚠️ ただし「届く」ことは未実測。
  4. 〔v2〕 **時計の対応**: 同期マーカーをブロックごとに打ち、正解側と観測側の時刻差の**分布とドリフト**を測る。
- ⚠️★★★ **やらないこと**: ImeShadow 行を**見ない・突き合わせない**（＝ 精度の実測ではない。`handoff §4`「プロトコル凍結前に実測を始めない」に抵触しない）。
- **出力**: シナリオ × OS × IME ごとの呼び出し列の型と、それから導いた正解の定義・oracle 一致率・時計誤差。★ preregistration に「正解の定義の根拠」として載せ、パイロットの生ログも公開物に含める。

### 1.1b 〔v2〕 IME の状態を固定する（試行の独立性）

⚠️ **IME は学習する。** 前の試行で選んだ候補が次の試行で先頭に来ると、同じシナリオでも Space の回数・候補の位置が変わり、**試行が独立でなくなる**。

- ★ 学習・予測変換・ユーザー辞書・ライブ変換（macOS）の設定を**要因または固定値として記録**し、★ **ブロックの先頭で辞書・学習状態をリセット**する。⚠️ リセットできない IME は「学習の影響を受けうる」と限界に書く（★ リセット手段の有無は較正パイロットで確かめる）。
- ★ OS / IME の版を記録し、計測中は自動更新と時刻同期を止める。

### 1.2 単位と照合

- **単位** = 正解側の 1 変換セッション（開始 = 最初の marked text / STARTCOMPOSITION、終了 = 確定または取消）。
- ⚠️ **母数が OS で違う**ので、正解側も OS ごとに GSE の定義に合わせて 2 通り作る:
  - Windows 定義: 候補窓が出た（`IMN_OPENCANDIDATE` を含む）セッションだけ
  - macOS 定義: かな入力の一区切りすべて
  - ★ 加えて**両 OS 共通の正解（全 composition）**に対する値も出し、「定義の違いで何が落ちるか」を示す。
- **照合**: 時間区間の重なり（IoU ≥ 0.5）で 1 対 1 に対応づける。1 対多は**分割**、多対 1 は**併合**として別に数える（macOS のマウス確定は併合になると分かっている — `schema_dto.rs` の注記）。

### 1.3 指標

| 指標 | 定義 | 区間推定 |
|---|---|---|
| 検出の適合率 / 再現率 / F1 | 上の照合で | セル別に Wilson 95% CI |
| 分割率 / 併合率 | 照合できなかった理由の内訳 | 同上 |
| `dwell_ms` の誤差 | 照合できた対の差。中央絶対誤差 ＋ Bland–Altman（偏り・一致限界） | ブートストラップ（seed 固定） |
| `abandon` の一致 | 正解 = 確定なしで marked text が消えた。混同行列 ＋ κ | Wilson |
| `nav` の一致 | 完全一致率 ＋ 差の分布。★ 正解 = **正解側のセッション区間**（Windows は候補窓が開いていた区間）の中で**シナリオ実行器が送った矢印キーの数**（`ImeShadow.nav` の定義は「変換中の矢印キー押下回数」・`schema_dto.rs`）。★ 区間を IME 自身の状態から取るので循環しない | Wilson |
| 20 秒打ち切り | 20 秒超のセッションで行が出ないことの確認（仕様どおりか） | 件数 |
| 〔v2〕 oracle ↔ 正解の不一致 | IME が意図どおりに動かなかった試行の件数と型（★ 評価からは除外しない） | Wilson |

★ 〔v2〕 **区間推定の単位**: 同じブロックの試行は IME の状態を共有するので独立でない。→ 連続量の区間は**ブロック単位のクラスタ・ブートストラップ**（seed 固定）。
★ 〔v2〕 **推定で書く**（仮説検定をしない）。BRM の統計ガイドライン逐語 "In many scientific investigations the goal of an experiment is to measure the magnitude of an effect with some degree of precision"。
★ **事前に決める除外規則**: 時計の跳び・IME の異常終了・ホストのクラッシュ。★ 除外件数は全部報告し、逸脱は `deviations.md` に記録する。

### 1.3a 〔v2〕 L2 —— 測度の一致（★ 主評価の一つ）

- ★ 試行を「テキスト」（1 文 = 複数の変換）に束ね、書字研究者が使う集計量を**正解・観測の両方から**計算する:
  テキストごとの **平均変換時間 / 変換の数 / 放棄率 / 変換中の時間割合**。
- ★ 指標: **Bland–Altman（偏りと一致限界）＋ ICC(2,1)（絶対一致）**。
- ★ 速さ・シナリオの混合を変えた 2〜3 の「合成テキスト母集団」で、**集計量の偏りが混合比で動くか**を見る。

### 1.4 シナリオ目録（S）

| ID | 内容 | 想定される挙動 |
|---|---|---|
| S1 | ローマ字 → Space 1 回 → Enter | 基本 |
| S2 | Space 複数回で候補を巡回 → Enter | |
| S3 | Space を押さずに Enter で確定 | Windows では行が出ない（定義上）、macOS は出る |
| S4 | 候補表示中に ESC で取消 | abandon |
| S5 | 候補を出さずに ESC で取消 | macOS のみ abandon |
| S6 | Backspace で全消去 | |
| S7 | 矢印で文節を移動して確定 | nav |
| S8 | 候補を数字キーで確定 | macOS は併合になる見込み |
| S9 | 候補をマウスで確定 | macOS は併合になる見込み。⚠️ 候補窓の座標を得る手段が要る —— 再現できなければ「評価できなかった」と報告する |
| S10 | 予測候補を Tab / 矢印で選択 | |
| S11 | macOS ライブ変換 ON で Space なしに変換 | |
| S12 | かな入力モード | ⚠️ macOS は IME_OPEN の反転欠陥が既知（`hook_macos.rs:369,1329`）→ 既知の失敗として測る |
| S13 | 20 秒を超えるセッション | 打ち切り |
| S14 | 変換中に IME を OFF にする | |
| S15 | 変換中に別アプリへフォーカスを移す | |

### 1.5 行列と標本数

- OS × IME × 設定: macOS 標準（ライブ変換 ON / OFF）・Windows MS-IME（必須）、Google 日本語入力（両 OS・任意）。
- ★ 〔v2〕 **打鍵の速さを 3 水準の要因**にする（遅い・中・速い）。★ 各水準のキー間隔は公開の打鍵研究から根拠づける（⚠️ 出典は `[Pn]` で接地する）。→ ★ **速さ別の精度曲線**を出す。
  ★ 加えて **候補を選ぶまでの間**（思考の間）を 0.2 s〜20 s の範囲で振り、`dwell_ms` の誤差と 20 秒打ち切りの境界を見る。
- ★ 〔v2〕 **標本数** = **n = 75 / セル × シナリオ × 速さ**（再現率 0.95 付近で Wilson 95% 半幅 ≈ ±5pt。セル × シナリオでは 225 で、初版の 200 とほぼ同じ）。
  ★ 所要時間の見積もり: 1 試行 ≈ 8 s として 1 セル = 15 × 3 × 75 = 3,375 試行 ≈ **7.5 時間**（1 晩 1 セル）。⚠️ 確定値は較正パイロットの 1 試行の実測時間で見直してから凍結する。
- ⚠️ 〔v2〕 **合成入力には「自然な混合比」が無い** → 全シナリオを足した 1 つの精度はシナリオの配分でいくらでも動く。★ **主推定値はシナリオ別**に出し、まとめるときは**重み（既定 = 均等）を明示**して「自然な打鍵での精度ではない」と書く。
- **入力文**: 青空文庫（著作権切れ）の文から、シナリオが要求する長さの句を seed 固定で抽出する。

### 1.6 〔v2・任意〕 実アプリへの転移確認

- ★ 正解が取れるのは自作の参照入力欄だけだが、実際の書字は他のアプリで起きる。⚠️ Windows の観測部は IME の候補窓のイベントに依るので、ホストで挙動が変わりうる。
- ★ 実アプリ（macOS = テキストエディット、Windows = メモ帳）で「中」の速さだけ・n = 30 / シナリオを流し、**oracle で数えられる量だけ**（変換の数・放棄の数）と `dwell_ms` の**分布**を参照入力欄の結果と比べる。
- ⚠️ **任意**（縮退順の先頭・§6）。やらなければ「参照入力欄は 1 アプリ」を限界に書く。

## 2. 評価 E2 — 本文をどこまで復元できるか

- **攻撃者が見るもの**: 公開・提出される形の NDJSON（`Key` 行の `category` と時刻、`ImeShadow` 行）。⚠️ 生 `vk` は含まない（ADR-014 判断 6 以降の形式）。★ `KeyCategory` は 14 種で、英字キーは 1 つの `Alphabetic` に畳まれる（`anonymize.rs`）。
- ★ 〔v2〕 **攻撃者の知識を段で定義する**: K0 = ログだけ / K1 = K0 ＋ 文のジャンル（どのコーパスか）/ K2 = K0 ＋ 候補文の集合（閉集合）。
- **A1 開集合の復元（K0 / K1）**: 日本語の言語モデルを持つ攻撃者が、カテゴリ列と時刻から本文を推定する。指標 = 文字誤り率。**ベースライン** = 言語モデルの事前分布だけ（ログを見ない）。「ログを見ることでどれだけ良くなるか」を報告する。
- **A2 閉集合の同定（K2）**: 候補文 K 個のどれを打ったかを当てる（K = 10 / 100 / 1000）。指標 = 正解率 vs 偶然 1/K。
  ★ 〔v2〕 **シミュレーション攻撃**で行う: 攻撃者は各候補文を**同じシナリオ生成器に通して予想ログを作り**、観測ログと最も近い候補を選ぶ（★ ローマ字の長さ・Space・句読点・Enter の位置が決定的に出るので、現実的な最強の閉集合攻撃）。
  ⚠️ **同定はかなりできる見込み**なので、**結果が悪くてもそのまま報告する**（decisions.md 判断 6）。
- ★ 〔v2〕 **特徴の除去実験**: 時刻を消す / `Alphabetic` の連続長を消す（窓ごとの件数だけにする）/ 1 秒ビンに粗くする —— のそれぞれで同定率がどれだけ下がるかを測る。→ ★ **「どこまで粗くすれば漏れが減るか」という公開粒度の推奨**を論文に書ける。
- **データ**: E1 と同じ合成入力を流用（青空文庫の文）。人のデータは使わない。
  〔v2・任意〕 **現代文のコーパス**を E2 だけで足す（⚠️ 青空文庫だけだと、現代文で学習した攻撃者の言語モデルと文体がずれて**漏洩を過小評価する**）。★ ライセンスが再配布を許すものを選ぶ。間に合わなければ限界に書く（縮退順・§6）。
- ⚠️ 攻撃の強さの上限は主張しない（「この攻撃では」と限定して書く）。

## 3. 評価 E3 — 実行コスト

★ **2026-09-28 改訂（判断 12）**: **公開する IME 観測部だけ**を単体の常駐プロセスとして、両 OS で**測り直す**。

- ⚠️★★★ **`_summary.txt` の CPU 平均 0.98% は無効な値だった**（2026-09-28 に一次で確認）。
  2026-09-04 の 1 回目の run で、⚠️ 旧計器 `top -l 2` が CPU% を**約 0.48 倍に過小報告**していた
  （`experiments/20260903-o1-runtime-cost/notes.md:616-653, 855-904`）。**論文に引かない。**
- ★ 直した計器（macOS = `ps -o cputime` の増分 / 実時間）での値は **GSE アプリ全体**の値であり、観測部だけの値ではない。★ 論文では**参考として併記するだけ**にする（版と条件を明記する）:

  | OS | 版 | 条件 | CPU 平均 | 出典 |
  |---|---|---|---|---|
  | macOS | v0.1.34 | 8h・作業中（`key` 10,533 件） | 2.19 % | `notes.md:868-892` |
  | macOS | v0.1.34 | 60 分・ほぼ無操作 | 1.62 % | `notes.md:967-1000` |
  | Windows | v0.1.33 | 8h | 2.06 % | `notes.md:887-892` |

  ⚠️ `notes.md:1000` 逐語「**GSE の CPU は N % と単一の数字で言わない**」—— 活動量で動く。→ ★ 観測部の再計測でも**作業中 / 無操作の 2 条件**を採る。
- ★ 計器は `experiments/20260903-o1-runtime-cost/` の**直した版**（校正つき）を流用する。⚠️ 短い窓でレート系を代表させない（`notes.md:906-907`）。
- ⚠️ **バッテリーは外す**。★ 指標としては 2026-09-04 に取り下げ済み、⚠️ Windows 機（G-GEAR）は**バッテリーが物理的に無い**、macOS の「エネルギー影響」は Apple 内部の無次元指標で換算できない（`notes.md:176-193, 446`）。→ 限界に書く。

## 4. 公開用の評価一式（別 repo）

| 含める | 含めない |
|---|---|
| `ime_compose.rs` / `ime_cloak.rs`（OS 非依存の状態機械）＋ OS ごとの最小ドライバ ＋ 単体ロガー | GSE 本体（HMM・介入・logger 全体・提出系） |
| 参照入力欄（両 OS）・シナリオ実行器 | Phase1 / G1 / O1 のデータ |
| 解析スクリプト・評価データ（合成・content-free）・★ 較正パイロットの生ログ・seed / lockfile | |

★ 〔v2〕 **観測部のコアは GSE の該当ファイルの「逐語コピー」にし、コピー元の GSE の commit とファイルの SHA-256 を manifest に記録する。** 公開 repo の CI が manifest と照合する。
→ ⚠️ GSE 本体の構造（workspace）は変えない（GSE 本体の OSS 公開は未踏採択後）。★ しかし「論文のツール ≠ GSE のツール」という乖離は検出できる。

★ **ライセンス**（2026-09-28 判断 15）: **コード = Apache-2.0 / データ・シナリオ・文書 = CC BY 4.0**。
★ **置き場所は DOI の付く信頼できるリポジトリ**（Zenodo / OSF）にする（2026-09-28 に BRM の規程を一次で確認）:
- BRM は逐語 "the journal follows the Open Science Initiative's Level 2 Transparency and Openness Guidelines. This means that all relevant information must be placed in a trusted repository. This applies to stimuli and methods being validated, new analyses being reported, and new equipment being described."
- ★ Type 4 のデータ方針: 逐語 "materials described in the manuscript, including all relevant raw data, will be freely available to any researcher wishing to use them for non-commercial purposes" → ⚠️ **ライセンスは少なくとも非商用の自由利用を許すもの**でなければならない。
- ★ データ引用は DOI を参考文献に載せる（逐語 "Data citations should include a persistent identifier (such as a DOI)"）。

## 5. 論文の節構成（BRM）

1. Introduction — 打鍵ログ研究と CJK の IME という空白、本文を取らない要請
2. Background & related work — IME の変換過程 / Inputlog・ScriptLog / [P270] / [V5]
3. Observability analysis（C1）
4. The logger（C2）— `KeyCategory`、`ImeShadow`、OS の非対称をどう記録で宣言するか（`capabilities`）
5. 〔v2〕 Validation framework — 正解（参照入力欄）・oracle・観測の三者照合、較正パイロット、IME の状態の固定
6. Study 1: Accuracy（E1）— L1 事象の一致 ＋ 速さ（＋ 任意: 実アプリへの転移）
7. 〔v2〕 Study 2: Measure-level agreement（E1 の L2）
8. Study 3: Text recoverability（E2）— 閉集合・開集合・特徴の除去
9. Study 4: Runtime cost（E3）
10. 〔v2〕 **Recommendations for researchers** — OS ごとに「信頼してよい測度 / 使ってはいけない比較」（例: `abandon` 率を OS 間で比べない）と、E2 の除去実験から導く公開粒度の推奨（★ BRM 逐語 "BRM readers want practical solutions."）
11. Limitations — 合成入力のみ・参照入力欄は 1 アプリ（転移確認をしなければ）・マウス確定・かな入力の欠陥・IME の版と学習・バッテリー未測定
12. Availability & Compliance with ethical standards（人を対象としない）
   ★ BRM の規程（2026-09-28 確認）: **Open Practices Statement を References の直前**に置く／
   **Declarations** 節（Funding / Competing interests / Ethics approval / Consent to participate /
   Consent for publication / Availability of data and materials / Code availability）を置き、
   逐語 "If any of the sections are not relevant to your manuscript, please include the heading and write 'Not applicable'"。
   要旨は **250 語以内**・APA 第 7 版。⚠️ 本文の分量上限は規程に書かれていない。

## 6. 日程（2026 年内の投稿に向けた逆算）

| 期間 | 内容 |
|---|---|
| 〜10 月中旬 | 参照入力欄（macOS）・シナリオ実行器・★ 較正パイロット（macOS）・照合解析、プロトコル凍結 |
| 〜11 月上旬 | macOS 実測、Windows の参照入力欄と★ 較正パイロット（(a) IMM / (b) TSF の 2 経路を試す） |
| 〜11 月下旬 | Windows 実測（研究者の Windows 機・収集のみ依頼）、E2、★ E3（観測部だけを両 OS で再計測・2 条件） |
| 12 月 | 執筆・評価一式の公開・BRM 投稿 |
| 〜2027-01-21 | （任意）CHI 2027 Posters |

★ **段階凍結**: 〜10 月中旬に macOS 版のプロトコルを凍結し、⚠️ Windows 版（正解の経路・定義）は **Windows 本計測の前に追補として凍結**する（★ Windows の較正パイロットが 11 月上旬のため）。追補も実測前であることを preregistration に記録する。

⚠️ 律速は Windows の実測。★ 遅れた場合の縮退順（判断 14）:
**実アプリへの転移確認（§1.6）→ Google 日本語入力 → 現代文コーパス（§2）→ S9（マウス確定）を「評価できなかった」とする → E2 の開集合の復元**。

## 7. テスト戦略（評価系そのものの検査）

- ★ 〔v2〕 **パラメータ回復テスト**（最重要）: 正解ログから**既知の誤りを注入した偽の観測ログ**（例: 取り逃し 5% / 分割 3% / 併合 3% / 時間の偏り +20 ms・ばらつき σ = 50 ms）を作り、解析が注入した値を**区間内で回復する**ことを確かめる。⚠️ 「実データで緑」だけでは、解析が誤りを見逃す形で壊れていても気づけない。
- 照合器は**既知の答えを持つ合成の正解 / 観測の対**で単体テストする（完全一致 / 分割 / 併合 / 取り逃し / 偽検出の 5 型）。
- ⚠️ 陽性対照: 観測ログをわざと 1 行消す・ずらす変異で、指標が期待どおり悪化することを確かめる（memory `measurement-instrument-false-positives`）。
- ★ 〔v2〕 陰性対照: 観測ログを時間方向に大きくずらす・シャッフルすると、一致が**偶然水準まで落ちる**こと。
- 解析は seed 固定で 2 回走らせてバイト一致を確かめる（`docs/experiment-tracking.md`）。

## 8. 後続 issue の案（★ 分解は次の作業）

★ Done は test 名 / exit code / 観測可能条件で書く。
1. 参照入力欄 macOS（全呼び出しを JSONL に記録）
2. 参照入力欄 Windows（(a) IMM 版 ＋ (b) TSF 版）
3. シナリオ実行器（両 OS・seed 固定・oracle 出力・速さ 3 水準）
4. 較正パイロット macOS → preregistration 凍結（macOS 版）
5. 照合器 ＋ L1/L2 解析（★ パラメータ回復テストが緑）
6. 単体ロガーの切り出し（★ manifest 照合が exit 0）
7. macOS 本計測
8. 較正パイロット Windows → preregistration 追補の凍結 → Windows 本計測
9. E2（閉集合のシミュレーション攻撃・開集合・除去実験）
10. E3（観測部だけ・2 条件）
11. 公開（Zenodo DOI）
12. 執筆（BRM）

## 設計判断の履歴

- 実行回数: /reimagine 1 回目（2026-09-28）
- 採用: **ハイブリッド**（v1 を土台に v2 の 8 点 ＋ 任意 2 点）
- 根拠: v1 は判断 1–13 と整合するが、⚠️ **凍結後には直せない妥当性の穴が 2 つ**あった（L2 が無い・IME の学習で試行が独立でない）。v2 の全部を入れると判断 7（2026 年内の投稿）に対して重いので、転移確認と現代文コーパスは任意（縮退順の先頭）にした。研究者が推奨どおりハイブリッドを選んだ（decisions.md 判断 14）。
