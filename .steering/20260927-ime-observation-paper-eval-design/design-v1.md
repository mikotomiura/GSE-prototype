# 設計（初版 v1 — /reimagine 前）

★ **2026-09-28: 一次確認による訂正 4 点を入れて研究者が承認した**（decisions.md 判断 10）。
訂正 = `unmarkText` は確定側（§1.1）／Windows の正解は 2 経路を試す（§1.1）／`nav` の正解の作り方（§1.3）／
CPU 0.98% は無効・E3 は観測部だけ再計測（§3）。★ 加えて較正パイロット（§1.1a・判断 11）と BRM の規程（§4・§5）を足した。

⚠️ 本書は評価プロトコルの**下書き**である。承認後に `/reimagine` を回し、確定版を
`experiments/<date>-ime-observation-accuracy/preregistration.md` として**実測前に凍結**する。

## 0. 論文の主張（外枠）

**仮題**: *Observing Japanese IME conversion without recording text: an observability analysis,
a cross-platform logger, and a synthetic-input validation*（BRM）

| # | 主張 | 根拠（現存 / これから作る） |
|---|---|---|
| C1 | Windows では他プロセスの TSF composition を**権限によらず**観測できず、macOS には公開 API が無い。したがって content-free な IME 観測は窓イベントか打鍵推論のどちらかに限られる | 現存: `survey-input-channels.md` §7.1–7.6（⚠️ 論文用に一次の MS / Apple 文書へ引き直し、`[Pn]` で接地する） |
| C2 | 本文を取らずに「1 変換 = 1 行」（`dwell_ms` / `nav` / `abandon`）を両 OS で記録できる。ただし OS ごとに**由来と母数が違う**（Windows = 候補窓が出た変換・窓イベント由来、macOS = かな入力の一区切りすべて・打鍵推論） | 現存: `ime_compose.rs` 冒頭の表・`schema_dto.rs` `ImeShadow` |
| C3 | その記録は IME 自身の状態と◯◯の精度で一致する（シナリオ別・OS 別・IME 別） | **これから**: 評価 E1 |
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
  - ⚠️ 正解ログの中身（確定文字列）は**評価マシンの中だけ**で使い、突き合わせ後に破棄するか、公開する場合は合成コーパスなので問題ない（後述 1.3）。★ 突き合わせには**長さとイベント種別だけ**で足りるので、正解ログ自体を content-free にしてもよい（/reimagine で決める）。
- **シナリオ実行器**: macOS = `CGEventPost`（memory `macos-app-visual-check-workflow`: 合成キーは IME を実際に駆動する）、Windows = `SendInput`（scan code）。
- **時計**: 正解ログと ImeShadow は別プロセスなので、両者に**同じ時計**を使うか、開始時に同期マーカー（特定キー列）を打って対応づける。
  ⚠️ **GSE の `t` と macOS の `dwell_ms` は壁時計（`SystemTime`）由来で単調ではない**（`ime_compose.rs` 冒頭）。→ ★ 参照入力欄は**壁時計と単調時計の両方**を記録し、run 中に時計が跳んだ区間は除外として数える（NTP の同期も run 中は止める）。

### 1.1a 較正パイロット（★ 2026-09-28 追加・判断 11）

- **目的**: 正解の定義（開始・確定・取消・候補窓）を**実機の呼び出し列**で決める。★ Apple も MS も呼び出し順を文書にしていないため。
- **やること**: 参照入力欄**だけ**を動かし、S1〜S15 を各数回流して呼び出し列を記録する。Windows は (a) / (b) の両経路を記録する。
- ⚠️★★★ **やらないこと**: GSE の IME 観測部を**走らせない**。ImeShadow と**一切突き合わせない**（＝ 精度の実測ではない。`handoff §4`「プロトコル凍結前に実測を始めない」に抵触しない）。
- **出力**: シナリオ × OS × IME ごとの呼び出し列の型と、それから導いた正解の定義。★ preregistration に「正解の定義の根拠」として載せ、パイロットの生ログも公開物に含める。

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
- 各セル × シナリオで **n = 200 セッション**を目安（再現率 0.95 付近で Wilson CI の半幅 ≈ ±3pt）。⚠️ 確定値は /reimagine 後に凍結する。
- **入力文**: 青空文庫（著作権切れ）の文から、シナリオが要求する長さの句を seed 固定で抽出する。
- **打鍵タイミング**: キー間隔を公開された打鍵研究の分布から seed 固定でサンプルする（⚠️ 出典は `[Pn]` で接地する）。**タイミングは精度に効きうる**ので、固定間隔との 2 条件で感度を見る。

## 2. 評価 E2 — 本文をどこまで復元できるか

- **攻撃者が見るもの**: 公開・提出される形の NDJSON（`Key` 行の `category` と時刻、`ImeShadow` 行）。⚠️ 生 `vk` は含まない（ADR-014 判断 6 以降の形式）。
- **A1 開集合の復元**: 日本語の言語モデルを持つ攻撃者が、カテゴリ列と時刻から本文を推定する。指標 = 文字誤り率。**ベースライン** = 言語モデルの事前分布だけ（ログを見ない）。「ログを見ることでどれだけ良くなるか」を報告する。
- **A2 閉集合の同定**: 候補文 K 個のどれを打ったかを当てる（K = 10 / 100 / 1000）。指標 = 正解率 vs 偶然 1/K。⚠️ 文字数・空白・句読点の位置・変換回数から**同定はある程度できる見込み**なので、**結果が悪くてもそのまま報告する**（decisions.md 判断 6）。
- **データ**: E1 と同じ合成入力を流用（青空文庫の文）。人のデータは使わない。
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
| `ime_compose.rs` / `ime_cloak.rs`（OS 非依存の状態機械）＋ OS ごとの最小ドライバ | GSE 本体（HMM・介入・logger 全体・提出系） |
| 参照入力欄（両 OS）・シナリオ実行器 | Phase1 / G1 / O1 のデータ |
| 解析スクリプト・評価データ（合成）・seed / lockfile | |

⚠️ ライセンスは未決（研究者判断）。
★ **置き場所は DOI の付く信頼できるリポジトリ**（Zenodo / OSF）にする（2026-09-28 に BRM の規程を一次で確認）:
- BRM は逐語 "the journal follows the Open Science Initiative's Level 2 Transparency and Openness Guidelines. This means that all relevant information must be placed in a trusted repository. This applies to stimuli and methods being validated, new analyses being reported, and new equipment being described."
- ★ Type 4 のデータ方針: 逐語 "materials described in the manuscript, including all relevant raw data, will be freely available to any researcher wishing to use them for non-commercial purposes" → ⚠️ **ライセンスは少なくとも非商用の自由利用を許すもの**でなければならない。
- ★ データ引用は DOI を参考文献に載せる（逐語 "Data citations should include a persistent identifier (such as a DOI)"）。

## 5. 論文の節構成（BRM）

1. Introduction — 打鍵ログ研究と CJK の IME という空白、本文を取らない要請
2. Background & related work — IME の変換過程 / Inputlog・ScriptLog / [P270] / [V5]
3. Observability analysis（C1）
4. The logger（C2）— `KeyCategory`、`ImeShadow`、OS の非対称をどう記録で宣言するか（`capabilities`）
5. Study 1: Accuracy（E1）
6. Study 2: Text recoverability（E2）
7. Study 3: Runtime cost（E3）
8. Limitations — 合成入力のみ・参照入力欄は 1 アプリ・マウス確定・かな入力の欠陥・IME の版依存
9. Availability & Compliance with ethical standards（人を対象としない）
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

⚠️ 律速は Windows の実測。遅れた場合の縮退: Google 日本語入力を落とす → S9（マウス確定）を「評価できなかった」とする。

## 7. テスト戦略（評価系そのものの検査）

- 照合器は**既知の答えを持つ合成の正解 / 観測の対**で単体テストする（完全一致 / 分割 / 併合 / 取り逃し / 偽検出の 5 型）。
- ⚠️ 陽性対照: 観測ログをわざと 1 行消す・ずらす変異で、指標が期待どおり悪化することを確かめる（memory `measurement-instrument-false-positives`）。
- 解析は seed 固定で 2 回走らせてバイト一致を確かめる（`docs/experiment-tracking.md`）。
