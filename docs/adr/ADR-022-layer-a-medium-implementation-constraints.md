# ADR-022: 層 A の媒体実装制約を一次で確定し、A-7 を落として表示面を OS ごとに分ける（iOS = ロック画面ウィジェット / Android = ライブ壁紙）

- **ステータス**: ★★★ **Accepted**（2026-09-02・研究者判断）
- **日付**: 2026-09-02（★ 追記 2026-09-03: D9 / Android 側）
- **関連**: **ADR-021**（★ 本 ADR が **D1 の但し書き / D3 / D4 / D10** を追補する）/
  **ADR-017**（D2 の契約・**D4 の制約 1 と S1–S6**・D5 / D6）/ **ADR-018 D2 / D3** /
  **ADR-015**（Wall Server の削除理由）
- **作業記録**: `.steering/20260902-expression-layer-os-constraints/`
- **一次証拠**: ⚠️★★★ **本 ADR の一次は査読論文ではなく OS ベンダの公式ドキュメントである。**
  → ★ **`docs/references.md` には登録しない**（★ 先例: `docs/agent-shared.md` の
  Windows TSF / UIPI の逐語は `.steering/.../survey-input-channels.md §7` を指している）。
  ★ **逐語・URL・OS バージョンの全件は
  `.steering/20260902-expression-layer-os-constraints/survey-os-constraints.md` にある。**
  ★ 取得日は全て **2026-09-02**。⚠️ Apple / Google の当該ページは**版番号を持たない living document**。

---

## Context

### 1. ★ 何を裁くか

**ADR-021 D1 は、ロック画面を第一媒体に決めた際に 1 つ先送りした。** 逐語:

> 「**OS 制約でアニメーションを載せられない場合がある → 実装時に再検査**」

★ これは小さな但し書きに見えるが、**そうではない**。

- ADR-021 **D10 の A-6** は ⚠️★★★ **「色を主符号にしない」**と決めた（[P85]: 周辺視の色の見落とし 6% → 25%・
  ⚠️ **実証群に色覚多様性の被験者がゼロ** [P252]）。
- ★ その**唯一の代替として A-7**（振幅 ~1°・1–3 Hz の **anchored oscillation**）を置いた。
- ★ **ADR-021 D4** は、`invitation` を `level` から分離する符号としても **A-7 を採った**。

→ ★★★ **A-7 が実装不能なら、層 A の符号体系と `invitation` の契約が同時に崩れる。**
★ **だから「実装時に再検査」ではなく、いま閉じる。**

### 2. ⚠️ 調べ方（★ 再現できる形で書く）

⚠️★★★ **本領域は AI 生成 SEO ページが統計を捏造していることが前セッションで判明している**
（★ ADR-021 の研究衛生上の警告）。→ ★ **一次のみを根拠にした。**

| 規律 | 実施 |
|---|---|
| ✅ 一次 | Apple 公式ドキュメント / HIG / Apple Platform Security / WWDC 公式トランスクリプト / 公式ユーザガイド / Android 公式 / AOSP / Firebase 公式 / RFC / NIST SP |
| ❌ 使わない | ブログ / まとめ / StackOverflow / **abstract だけ** / AI 生成 SEO ページ |
| ★ 必須 | **英語原文の逐語 ＋ URL ＋ OS バージョン** |
| ★★★ 必須 | ⚠️ **「一次で確認できなかった」を明記する**（★ 推測で埋めない） |

⚠️★★★ **取得手法の実測**: `developer.apple.com` の HTML は **JS SPA で本文が空になる**。
→ ★ **DocC JSON API**（`https://developer.apple.com/tutorials/data/documentation/<path>.json`）
を直接叩くと取れる（★ 試した 17 URL すべて HTTP 200）。
★ **availability の OS バージョンは要約を通さず `metadata.platforms` から機械的に読み出した。**

---

### 3. ⚠️★★★ 調査して初めて分かった最大の事実 —— **2 つの OS は正反対である**

★ 調査前の暗黙の前提は「**ロック画面という 1 つの面に、1 つの表現を載せる**」だった。
⚠️★★★ **一次を当たると、その前提が成り立たない。**

| | **iOS** | **Android** |
|---|---|---|
| ロック画面**ウィジェット** | ✅ **使える** | ❌ **実質使えない**（★ glanceable hub は既定 OFF・別シーン・CDD は "MAY"） |
| **ライブ壁紙** | ❌ **存在しない** | ✅ **使える**（★ AOSP がキーガード窓に `FLAG_SHOW_WALLPAPER` を立てる） |
| **持続アニメーション** | ❌ **不可**（★ 最大 2 秒・連続更新非対応） | ✅ **可**（★ 任意 Canvas/GL・レートはアプリ制御） |
| **AOD への描画** | ❌ 不可 | ❌ 不可（★ `AMBIENT_WALLPAPER` は `signature|preinstalled`） |
| **色** | ❌ **OS が強制的に desaturate** | ✅ **自由** |
| **常時通知なしの常駐** | ★ push 前提 | ✅ `BIND_FOREGROUND_SERVICE_WHILE_AWAKE` |

→ ★★★ **「1 つの面」ではなく「OS ごとに別の面」であり、しかも能力が真逆である。**
★ **本 ADR の決定の多くは、この非対称から導かれる。**

---

## Decision

### D1. ⚠️★★★ **A-7（1–3 Hz の持続振動）を第 1 版の符号として採らない**

★ **理由は 3 本あり、3 本目が決定的である。**

#### 理由 1: iOS では成立しない（★ 一次 4 本が独立に同じ結論を指す）

| # | 逐語（英語原文） | 何を塞ぐか |
|---|---|---|
| **1** | ⚠️★★★ *"**On devices that include an Always-On display, the system doesn't perform animations to preserve battery life in Always On.**"* | ★★★ **AOD ではアニメーションが 1 フレームも出ない** |
| **2** | *"The Always-On display shows the time, widgets, and Live Activities at a glance, and **when not in use, the display efficiently adjusts down to 1Hz**."* | ★ **1 Hz では 1.5 Hz を再現できない** |
| **3** | *"**Animations in widgets and Live Activities have a maximum duration of two seconds.**"* ＋ *"**`Transaction` isn't available to widgets and Live Activities**"* | ★ **持続の土台が無い** |
| **4** | *"your widget extension is **not continually active, even if the widget is onscreen**"* ／ *"timeline entries that are **at least about 5 minutes apart**"* ／ HIG *"**Widgets don't show real-time information.**"* | ★ **ウィジェット経路が塞がる** |

⚠️ **さらに HIG が正面から抑制している**（★ 技術可否とは別の軸）:
*"**unnecessary changes during Always On can be especially distracting on iPhone**, because people often put
their device face up on a surface, **making motion on the screen visible even when they're not looking directly at it.**"*

★ **継続更新が逐語で保証されている唯一の経路は `Text` の日時スタイル**（*"**some SwiftUI views let you
display content that continues updating while your widget is visible**"*）——
⚠️ **数字が進むだけで、振動には使えない。★ かつ ADR-021 D3 の「数値を出さない」に正面から抵触する。**

#### 理由 2: ⚠️★★★ Android では**成立する。ただし「画面が点いている間だけ」である**

★ **ライブ壁紙経由なら載る**（★ 一次）:

| 逐語 | 含意 |
|---|---|
| SystemUI `applyKeyguardFlags()`: *"**Show the wallpaper if we're on keyguard/AOD** and the wallpaper is not occluded by a solid backdrop."* → `FLAG_SHOW_WALLPAPER` を立てる | ★ **ロック画面表示中も壁紙が描かれる** |
| `WallpaperService`: *"As some wallpapers use visibility as a signal to start animations, this makes sure `Engine#onVisibilityChanged` is invoked **only when the display is both on and visible (with brightness on)**."* | ★ **画面 ON のときだけ visible** |
| *"Called to inform you of the wallpaper becoming visible or hidden. **It is very important that a wallpaper only use CPU while it is visible.**"* | ★ 消灯中は描かない |
| `ApplicationInfo.FLAG_STOPPED`: *"could also include user actions like adding it as an app widget, **selecting it as a live wallpaper**, selecting it as a keyboard"* | ★ **OS が想定した常駐の作り方**（★ 裏技ではない） |

⚠️★★★ **しかし AOD には載らない**:
`<attr name="supportsAmbientMode">` は *"**This feature requires the android.permission.AMBIENT_WALLPAPER
permission. @hide @SystemApi**"*（★ 当該権限は `signature|preinstalled`）。
★ さらに **targetSdk 35+ で毎フレーム描画のロック自体が撤去された** —— 逐語
*"This change disables the `DRAW_WAKE_LOCK`, an internal wakelock acquired per-frame duration display DOZE.
**It was added to allow animation during AOD.** … it will be removed."*

→ ★ **Android で言えるのは「本人が画面を点けてロック画面を見ている間は動く」までであり、「常時」ではない。**

#### 理由 3: ★★★ **非対称そのものが、採らない理由である**

⚠️★★★ **A-7 を採ると、iOS の被験者には振動が出ず、Android の被験者には出る。**

- ★ **ADR-021 D3 は「系が固定する」ものに「写像の極性」と「形状クラス」を挙げた。**
  → ★ **同じ `invitation` が端末によって別の符号になるのは、この既決に反する。**
- ⚠️★★★ **評価が壊れる** —— ★ `expression-channel.md` §7-1 は「**行動側の対照（ON/OFF の無作為化 ＋
  作業ログの客観指標）が要る**」としている。★ **符号が OS で違うと、OS が表現と交絡する。**
  ⚠️ **被験者間で「何を見たか」が違うのに、まとめて 1 つの結論を出すことになる。**
- ★ **A-6 の代替を探した動機は「色に依存しない共通の符号」だった。**
  → ⚠️ **OS 依存の符号では、その動機自体を満たさない。**

★ **したがって、共通解は「静的な符号」しかない。**

#### ★ 代わりに何を置くか

★ **`invitation` の符号を静的なものへ差し替える。** ★ 第 1 候補は **「面の縁が開く / 閉じる」**（★ 開口＝招待）:

1. ★ **色に依存しない**（A-6 を守る）。
2. ★ **`level` の目盛り（図の占有率と凝集度）と空間的に分離している**
   → ADR-021 D4 の「1 目盛りの読みを汚さない」を保てる。
3. ⚠️★★★ **「変化なし」を空白で表さない**（ADR-021 D2 **C4**）——
   ★ **閉じた縁を常に描く**ので、招待が無い状態も**明示的に描かれる**。
4. ★ **両 OS で同一に実装できる。**

⚠️ **受容性は未検証である。** → ★ `experiments/20260902-expression-layerA-visual/` の試視ハーネスは
**A-7（振動）と静的代替の両方**を実装しており、**どちらに転んでもデータが取れる**。

#### ⚠️★★★ 断定しない部分を明示する

- ⚠️ **`.repeatForever` が iOS のロック画面ウィジェットで持続振動を生むかは、Apple が許可とも禁止とも
  書いていない**（★ 一次で確認できなかった）。→ ★ **「公式に支持されていない」までが言えること。**
  ★ ただし **AOD の一文は実機実測を待たずに効く**ので、判定は変わらない見込み。
- ⚠️ **`TimelineView` がウィジェットで動作するかも一次に記述が無い。**
  ★ WidgetKit の対応ビュー一覧に無いが、**その一覧は `Gauge` / `ProgressView` も欠くので不完全**であり、
  ⚠️ **不在は証拠にならない。**
- ⚠️★★★ **Android の AOD 中に 3rd-party の `Engine` へ渡る `onVisibilityChanged` の実値は
  end-to-end で確認できていない。** ★ 窓フラグは立つが、`COMMAND_FREEZE` 経路は
  *"the wallpaper host receives `onVisibilityChanged(false)` callback"* と述べており、逆を示唆する。
  → ★ **実機で `onVisibilityChanged` をログして確定させる**（→ M-7）。

### D2. ⚠️★★★ **「1°」を絶対値として使わない。面の大きさに対する比で定義し直す**

★ **`references.md` の [P85] には既に留保が書いてある** —— 逐語:
「⚠️★★★ **偏心 7°–52° の周辺視条件の結果であり、ロック画面は中心視なので
「色は periphery で弱い」という最大の優位が層 A では効かない。**」

★ **本 ADR はこれを一段進める: 数値そのものも移植できない。★ しかも OS で意味が違う。**

| OS / 面 | 面の大きさ | ★ 1° 全振幅が占める割合 |
|---|---|---|
| **iOS `accessoryCircular`** | **76×76 pt** = 11.8 mm = **2.26°** | ⚠️★★★ **幅の 44%** |
| **iOS `accessoryRectangular`** | **172×76 pt** = 26.8×11.8 mm = 5.12°×2.26° | 幅の **20%** |
| **Android ライブ壁紙** | ★ **画面全体** | ★ **数 %**（★ 400 ppi 機で 1° ≒ 82 px） |

⚠️ **視距離 300 mm と 163 pt/inch は一次で確認していない仮定である**
（★ 試視ハーネスで可変にし、感度を見られるようにした）。
⚠️ 公式の但し書き: *"**The sizes of widgets may vary across devices. Your widget content should be
flexible and avoid using fixed values.**"*

→ ★★★ **同じ「1°」が、iOS では「面の半分を動かす」で、Android では「わずかに揺れる」になる。**
★ **絶対値としての 1° は、層 A では意味を持たない。**

⚠️ **代償**: ★ 比で定義し直すと **[P85] の検出可能性の保証が外れる**（★ 文献の外に出る）。
→ ★ **受け入れ試験を自前で回すしかない**（★ ADR-021 D10 の留保と同じ構造）。

### D3. ⚠️★★★ **A-6「色を主符号にしない」を維持する。★ 根拠が「文献」から「OS の非対称」へ広がった**

| OS | 逐語 | 含意 |
|---|---|---|
| **iOS** | *"it **renders widgets on the Lock Screen on iPhone using the vibrant mode**"* ／ *"**The system desaturates the widget, making a monochrome version**"* ／ 公式対応表: `accessoryCircular` **fullColor = No** | ★ **色相は使えない**（★ 強制） |
| **iOS** | *"**The brightness of pixels determines how vibrant they appear on the Lock Screen.**"* ／ *"**use opaque grayscale values, rather than opacities of white**"* | ★ **残るのは明度だけ**（⚠️ 透明度で階調を作ってはいけない） |
| **Android** | ★ ライブ壁紙は任意 Canvas/GL —— **制約なし** | ✅ **色は自由** |

→ ★★★ **色を使うと、iOS の被験者では消え、Android の被験者では残る。★ D1 理由 3 と同じ構造の交絡になる。**
★ **したがって A-6 は維持する。** ⚠️ **根拠は文献（[P85] / [P252]）だけでなく、OS の非対称でもある。**

★ 併せて Apple 自身の一般則も同じ方向: *"**Convey meaning without relying on specific colors to represent
information.** … **Use text and iconography in addition to color to express meaning.**"*

#### ⚠️★★★ 本決定が ADR-021 D3 を 1 項目だけ取り下げる

★ ADR-021 D3 は「本人が選ぶ（choose-from-N）」に **「配色テーマ」**を含めていた
（根拠は [P101] 逐語 *"offer the individual a choice of metaphors"* ＋ 減衰対策 [V124]）。
→ ⚠️★★★ **iOS ロック画面では色相が system に落とされるので成立しない。**

★ **残す**: モチーフ / 表示の有無。
⚠️ **層 A から外す**: **配色テーマ** —— ★ **層 B（専用アプリ）では成立するので、そちらへ移す。**

⚠️ **さらに悪い交絡がある**: *"**Devices with the Always-On display render widgets on the Lock Screen
with reduced luminance.**"* → ★★★ **明度が唯一の符号なのに、AOD がその明度を削る。**
★ **AOD 対応端末かどうかを端末条件として記録・統制する。**

⚠️ **一次の中の食い違いを隠さない**: 現行ドキュメントは *"**people can also color the Lock Screen to a
colored tint**"* と書くが、HIG は *"**monochromatic appearance without a tint color**"* と書く。
→ ★ **いずれにせよアプリ側が色相を決める余地は無い**が、⚠️ **被験者ごとに見え方が変わり得る。**

### D4. ★★★ **表示面は OS ごとに違う。iOS = ロック画面ウィジェット / Android = ライブ壁紙**

⚠️★★★ **これは妥協ではなく、一次から強制される。★ 各 OS で「もう一方の面」が存在しないか使えない。**

#### iOS: ロック画面ウィジェット（★ Live Activities は採らない）

⚠️ **HIG は逆を名指ししている** —— *"**Offer Live Activities to show real-time updates.** … **Widgets don't
show real-time information.**"* ★ **しかし一次を並べると、GSE では逆になる。**

| | ロック画面ウィジェット | Live Activities |
|---|---|---|
| 無音で更新できるか | ★ **できる**（★ 通知機構を通らない） | ★ できる（`alertConfiguration` の既定が `nil`） |
| ⚠️ **遠隔で開始・再開できるか** | ★ **常設**（★ 「開始」の概念が無い） | ⚠️★★★ **alert が "requirement"** |
| ⚠️ **寿命** | ★ **無期限** | ⚠️★★★ *"active for up to **eight hours**"* ／ ロック画面上 **12 時間** |
| 更新頻度 | ⚠️ 最小 5 分・1 日 **40–70 回**・opportunistic | ★ budget 制 |
| 配置 | ⚠️ **本人の手動操作が必要** | ★ アプリから開始 |

★★★ **決め手は「8 時間上限 ＋ push-to-start の alert 必須」の組み合わせである。**

★ push-to-start の逐語: *"it comes with the following **requirements**: … **Include an `alert` in the JSON
payload.**"* ／ alert の効果: *"Live Activity alerts **light up the screen and by default play the notification
sound**"*。⚠️ `AlertConfiguration.AlertSound` の構成メンバは **`named(_:)` と `default` の 2 つのみ**（★ 無音が無い）。

→ ⚠️★★★ **Live Activities で 1 日を覆うには 8 時間ごとに再開が要り、遠隔での再開は alert を強制される。
＝ 技術的理由だけで、1 日 2–3 回「画面を点灯させ通知音を鳴らす提示」が発生する。**
★ それは **ADR-017 D5 / ADR-021 D5 の「注意を強く奪う提示は介入である」に該当し、
Need / Opportunity の判定を通っていない介入**になる。→ ★★★ **設計の根幹に反するので採らない。**

★ 対してウィジェットは **無期限・無音**であり、**`level` は 1 日に数回しか変わらない**ので
「最小 5 分・1 日 40–70 回」の予算は足りる。

#### Android: ライブ壁紙（★ ウィジェットは採らない）

⚠️★★★ **Android のロック画面ウィジェットは、API が生きていても依存できる面ではない。**

| 逐語 / 実測 | 含意 |
|---|---|
| `WIDGET_CATEGORY_KEYGUARD` は **API 17・非 deprecated**（★ API 36 で `WIDGET_CATEGORY_NOT_KEYGUARD` が新設） | ★ **API は生きている** |
| ⚠️ `<bool name="config_glanceableHubEnabled">**false**</bool>` ／ *"enabled **via resource overlay only on products we want the hub to be present on**"* | ⚠️★★★ **AOSP 既定 OFF** |
| ⚠️ *"The communal scene shows the glanceable hub **when device is locked and docked**."* | ⚠️ **Lockscreen とは別シーン＝遷移が要る。常時可視でない** |
| ⚠️ CDD: *"**MAY support** application widgets on the lock screen."* | ⚠️ **保証されていない** |
| ⚠️ *"**Updates requested with `updatePeriodMillis` will not be delivered more than once every 30 minutes.**"*（★ AOSP `MIN_UPDATE_PERIOD = 30 * 60 * 1000`） | ⚠️ 自動更新は 30 分が下限（★ 明示 `updateAppWidget()` は非スロットル） |

→ ★ **ライブ壁紙を採る。**

⚠️★★★ **代償（★ Android 側は代償が重い）**:

| # | 何 | 一次 |
|---|---|---|
| **1** | ⚠️★★★ **3rd-party は「ロック画面専用の壁紙」を設定できない** | `setWallpaperComponentWithFlags(name, which)` は `@SystemApi`+`@hide`、`SET_WALLPAPER_COMPONENT` = `signature\|privileged` → ★ **セットアップで本人に「ロック画面にも適用」を選ばせる運用が必須** |
| **2** | ⚠️★★★ **本人がロック画面専用の壁紙を別に設定していると、見えない** | *"When called with which=`FLAG_LOCK`, clear the lockscreen wallpaper. **The home screen wallpaper will become visible on the lock screen.**"*（★ 裏返すと、lock 壁紙がある間は home の LWP は出ない） |
| **3** | ⚠️★★★ **CDD 保証ではない** | ★ ロック画面に壁紙を出すのは **AOSP SystemUI の実装**であって CDD の MUST ではない → ⚠️ **OEM 差分の実機確認が要る** |
| **4** | ⚠️ 不透明バックドロップ（メディア再生中のアルバムアート等）が乗ると隠れる | *"the wallpaper is not occluded by a **solid backdrop**"* |
| **5** | ★ **初回ロック解除前（BFU）は `directBootAware` の宣言が要る** | *"This happens for **wallpapers that are not direct-boot aware**; they can only be rendered after the user unlocks the device for the first time after a reboot. **In the meantime, the default wallpaper is shown instead.**"* |

⚠️★★★ **併せて記録する: Android では AppWidget が BFU で例外なく閉じている。**
`AppWidgetServiceImpl.java` L1017-1020 が逐語 *"User " + userId + " **must be unlocked for widgets to be
available**"* を投げ、★ **全 7109 行に対する `grep -c directBootAware` = 0**（★ 実測）。
→ ★ **仮に Android でウィジェットを採っていたら、再起動直後は必ず消えていた。**

### D5. ⚠️★★★ **搬送路も OS で違う。iOS は外部を経由せざるを得ない**

#### iOS: ★ **APNs 経由しかない**

⚠️★★★ **「外部サーバを経由しない × PC に常設リスナを置かない × 背景で受信する」の
3 条件同時充足は、iOS には存在しない。**

- ★ 背景実行モードは**列挙されている**（`audio` / `location` / `voip` / `external-accessory` /
  `bluetooth-central` / `bluetooth-peripheral` / `screen-capture` / `fetch` / `remote-notification` /
  `processing` / `workout-processing` / `nearby-interaction` / `push-to-talk`）
  → ★★★ **「LAN ソケットを保持する」モードが無い。**
- *"**Typically, an app is in a suspended state when it's in the background.**"*
- ⚠️★★★ *"**If an iOS app is in the background and performs a local network operation while its Local
  Network privilege is undetermined, the system denies that operation without presenting the local network alert.**"*
- ★ 唯一の LAN 直受信・背景常駐 API である **Local Push Connectivity** は、定義上
  *"maintain a persistent network connection to **your server**"* → ⚠️ **PC が常設サーバになるので制約 1 違反。**

★ **採る経路**: **PC → APNs（WidgetKit push）→ ウィジェットのリロード**。
★ PC は `api.push.apple.com` への **outbound HTTPS クライアント**であり、**リスナを開かない**
→ ★ **制約 1 の趣旨（「LAN に開かない」）には合致する。**

#### Android: ★ **ライブ壁紙が「常時通知なしの常駐」を与える**

⚠️ **Android の最大の問題は「Foreground Service の常時通知が介入に当たる」ことだった。★ それが解ける。**

| 逐語 | 含意 |
|---|---|
| ★ システムは壁紙を `BIND_AUTO_CREATE \| BIND_SHOWING_UI \| **BIND_FOREGROUND_SERVICE_WHILE_AWAKE** \| BIND_INCLUDE_CAPABILITIES` でバインドする。*"Like `BIND_FOREGROUND_SERVICE`, but **only applies while the device is awake**."* | ★★★ **常時通知を出さずに、覚醒中は FGS 相当の優先度が得られる** |
| ⚠️ Doze: *"**Suspends network access.**"* | ⚠️ **画面 OFF 中はネットワークが止まる** |

→ ★ **素直な設計は「イベントを PC 側でバッファし、`onVisibilityChanged(true)` を契機に取りに行く」**。
★ **曝露予算を「画面が点いている数秒」に賭ける方針と一致する。**

⚠️★★★ **ただし W-1 に宿題が 2 つ残る**:

1. ⚠️ **「取りに行く」＝ 端末が PC へ接続する ＝ PC 側にリスナが要る。**
   ★ ADR-017 D4 **制約 2 は「on-demand 起動 ＋ 停止時のティアダウン」を明示的に許している**ので、
   **GSE 稼働中だけ開いて停止時に閉じる**なら制約 1 に反しない。⚠️ **W-1 が明示的に裁くこと。**
2. ⚠️★★★ **pull 型の搬送が ADR-017 D3「PC → スマホの一方向」に当たるかどうか。**
   ★ **運ばれる中身は PC → スマホの一方向のまま**だが、★ 接続の向きは逆である。
   → ⚠️ **「inbound を作らない」の意味を W-1 で定義し直す必要がある。**

⚠️★★★ **`CompanionDeviceManager` は搬送路にならない**（★ 独立証拠 5 件）:
`WifiDeviceFilter` は `ScanResult`（＝**アクセスポイント**）にしかマッチしない ／
*"For Bluetooth classic devices this is triggered when the device connects/disconnects. **WiFi devices are
not supported.**"* ／ `android.companion` 全ソースの `mdns|nsd|dnssd|bonjour|zeroconf` grep = **0 件** ／
`setSelfManaged()` は `signature|privileged` ／ `notifyDeviceAppeared()` は `@SystemApi @hide`。

#### ⚠️★★★ 契約に書く「漏れるもの」（★ iOS 側・隠さない）

| # | 何 | なぜ |
|---|---|---|
| **1** | ⚠️ **`level` / `invitation` / `seq` の値そのものが APNs を通りうる** | ★ push を system が解釈するので **E2E 暗号化できない**。★ **ただし WidgetKit push は本文を持たない**（`{"aps":{"content-changed": true}}` のみ）ので、**値を載せずに済む余地がある**（→ W-1） |
| **2** | ⚠️★★★ **イベントの発生時刻列**（＝**本人の作業状態が遷移したタイミング**） | ★ **不可避に Apple 側のメタデータになる。避けられない** |
| **3** | ⚠️ **Apple がペイロードを読めるかは一次で確認できなかった** | ★★★ **「Apple から見えない」と書いてはならない。** ⚠️ *"No confidential or proprietary information is transmitted through APNs."* は **MDM 配備ガイドの文脈** |
| **4** | ⚠️ **PC 側に APNs provider 資格情報（`.p8` 鍵）を置く**ことになる | ★ 被験者の PC 上に配布する秘密が増える |

→ ★★★ **content-free の原則は「文字列を送らない」までは守れるが、iOS では「タイミングを漏らさない」は守れない。**
⚠️★★★ **Android ではこれが起きない**（★ 外部を経由しないため）。→ ★ **同意文書で OS 別に書く。**

### D6. ★ **S3（リプレイ対策）の既決を維持する。★ 1 点だけ追補する**

★ ADR-017 D4 **S3** は `epoch` ＋ 単調 `seq` ＋ 巻き戻り破棄を置き、
⚠️「**それだけで十分と決めつけない**」と留保していた。→ ★ **OS 側に既存機構は無かった。**

| # | 逐語 / 実測 | 出典 |
|---|---|---|
| 1 | ⚠️★★★ **APNs / FCM の一次文書に "replay" は 0 件**（★ 全文 grep で実測） | 実測 |
| 2 | *"As a best-effort service, **APNs may reorder** notifications…"* ／ *"tries to deliver it **at least once**"*（★ **重複あり**） | APNs |
| 3 | *"**FCM doesn't guarantee the order of delivery.**"* | FCM |
| 4 | ★ TLS 1.3 は**セッション内のみ**: *"The second class of attack **cannot be prevented at the TLS layer and MUST be dealt with by any application.**"* | RFC 8446 §8 |
| 5 | ★★★ **NIST が GSE の設計を逐語で推奨している**: *"certain identifying information can be incorporated into the AAD. Examples … include a **sequential message number or a time stamp**. … **detection of replayed messages, out-of-sequence messages, or missing messages**."* | NIST SP 800-38D App. D |

⚠️ **紛らわしいので明記する**: **Android KeyStore の "rollback resistance" / RPMB は無関係**である。
★ 守っているのは *削除した鍵の復元* と *ストレージの巻き戻し* であって、**ネットワーク上のメッセージ再送ではない**。
★ かつ `setRollbackResistant` は **公開 Android API に存在しない**（★ 実測）。

★ **追補（1 点だけ）**: **`epoch` / `seq` を平文フィールドではなく AEAD の AAD（または署名対象）に含める。**

### D7. ★ **オフスイッチ要件は満たせる。ただし「本アプリだけを止める経路」を第一に設計する**

★ `expression-channel.md` §7-3 は「**オフスイッチ要件は交渉不可**」としている。→ ★ **両 OS で満たせる。**

| OS | ★ 本アプリだけを止める（★ 第一の経路） | ⚠️ 日常機能も一緒に落ちる経路 |
|---|---|---|
| **iOS** | ★ ロック画面の編集でウィジェットを外す ／ ★ **アプリ内の停止 UI**（★ HIG が要求: *"make it easy for people to turn them off in your app"*） | ⚠️ `Settings > Face ID & Passcode` の **"Allow Access When Locked"** ／ ⚠️ `Display & Brightness > Always On Display` |
| **Android** | ★ **壁紙を付け替える**（`ACTION_SET_WALLPAPER` / `ACTION_LIVE_WALLPAPER_CHOOSER` / `clear(int)` = *"reverting to the system default"*） ／ ★ アプリ内の停止 UI | ⚠️ force stop / アンインストール |

⚠️★★★ **iOS の「日常機能も落ちる」側の逐語**: *"**If you turn off Lock Screen access to a feature, you
prevent someone who has your iPhone from viewing any personal information that it might contain** …
However, **you also lose quick access to the information yourself**."*
→ ★★★ **同意文書と `participant-setup-guide.md` では「本アプリだけを止める経路」を第一に書く。**

★ **BFU の扱い**:

- **iOS**: *"the developer can **add the Data Protection capability to a widget extension**. Until a user
  unlocks their device …, **WidgetKit displays placeholders instead of the widget content**."*
  ⚠️ **オプトインしない場合の挙動は一次に記述が無い。**
- **Android**: ★ `android:directBootAware="true"` を宣言すればライブ壁紙はバインドされる。
  ⚠️ 宣言しなければ **既定壁紙にフォールバックする**（★ ログ逐語 *"Wallpaper isn't direct boot aware;
  using fallback until unlocked"*）。

★ **Stolen Device Protection (iOS 17.3+) は該当しない**（★ 保護対象の列挙に入っていない・実測）。

### D8. ⚠️★★★ **研究衛生: 前セッション由来の所見 1 件を撤回する**

★ 本セッションの調査中、**前回の中断時に「`CompanionDeviceManager` に
システムが出す mDNS picker（`FLAG_SHOW_PICKER`）がある」という所見**が出ていた。
→ ⚠️★★★ **これは誤りである。撤回する。**

**実測**:

- `android.companion` 全ソースの `picker` grep = **0 件**
- 公開 SDK の `FLAG_` 定数は **`FLAG_CALL_METADATA = 1` のみ**

★ **CDM に picker 相当の UI は確かに存在する**（逐語 *"choose the device to associate the application
with"*）が、⚠️ **それは `IntentSender` 経由の関連付け確認 UI であって、`FLAG_SHOW_PICKER` という
定数でも mDNS 探索でもない。**

→ ★★★ **教訓: 中断したエージェントの「発見しかけ」を、確定した所見として持ち越してはならない。**
★ 本 ADR では、**中断報告に出た所見を引き直した**（★ 別のエージェントが自分の完全コピーで再確認した）。

⚠️ **併せて記録する**: 同じ再確認で AOSP の行番号 2 件も訂正された
（`AppWidgetServiceImpl.java` L1013-1024 → **L1017-1020** ／ WMS のコメントは **L712-717**）。
★ **逐語・結論は不変。**

⚠️ **もう 1 件**: ★ `CompanionDeviceManager` の **関連付け解除 UI は AOSP Settings に存在しない** ——
`BluetoothDetailsCompanionAppsController.isAvailable()` が
*"// Do not show this preference for now."* で `false` を返す状態が **main / 16 / 15 / 14 / 13 の全ブランチで同一**。
★ ガイドも逐語 *"**The companion app is responsible for clearing its own associations**"*。
→ ★ **CDM を将来使うなら、解除 UI は自前実装が要る**（★ 同意文書の撤回手段と直結する）。

### D9. ★★★ **曝露予算（層 A の 2 秒）を維持する。★ [P264] の分母を一次で確認し、顔認証時代の再検算も行った**

⚠️ **懸念の出発点**: 曝露予算の根拠 4 本のうち **3 本が 2014–2017 年の Android のみ**である
（[P153] / [P240] / [P263]）。★ **顔認証（自動解錠）時代には、ロック画面に滞在する時間そのものが
消えている可能性がある** —— ★ そうなら**層 A は媒体として成立しない**。

#### ★ 確認 1: [P264] の分母は「ロック画面での接触だけ」で正しかった（★ 一次で確認）

⚠️★★★ **分母が違えば予算計算が変わるので、本文を開いて確認した。**

| 逐語（本文） | 何が分かるか |
|---|---|
| *"Overall, this resulted in a dataset of **n=894 unique smartphone use sessions, of which 221 (24.7%) constituted locked phone use**."* | ★ **分母は 221 件＝ロック状態のまま完結した接触**。★ **全接触の混合ではない** |
| *"**Lock screen checks ranged between 1s and 22s and lasted 4.2s on average (median 3s, standard deviation 4.1s).**"* | ★ **4.2 秒 / 中央値 3 秒は「ロック画面での接触」の値** |
| *"We find that about a quarter of smartphone interactions represent using the phone for a very brief amount of time (**3-4s on average**) in a locked state."* | ★ Discussion でも一致 |

★ **さらに好都合な点**: [P264] は端末の screen-on/off ログではなく、
**一人称視点カメラ（Subcam・200 時間超）の行動コーディング**から算出している（★ 二重コーディング一致率 94% /
Krippendorff's α = 0.91）。→ ★ **「実際に見ている時間」に近く、本プロジェクトの構成概念に合致する。**

★ **標本**: n=41・**iOS 78%** / Android Samsung 15% / その他 7%・21–29 歳・UK 2018–2019 収集。
→ ★★★ **顔認証が普及した後の iOS 主体の標本で、4.2 秒が観測されている。★ 崩れていない。**

#### ★ 確認 2: 2024 年の一次を 1 本追加した [P268]

★ **Abdrabou et al., CHI EA '24**（N=21・24 時間 in-the-wild・前面カメラ ＋ 較正不要の視線推定）。

| 逐語 | 何を支持するか |
|---|---|
| *"On average, participants took **6.33s for patterns, 5.94s for passwords, 4.51s for PINs, and 4.15s for fingerprints**."* | ★ **2024 年でも解錠まわりは瞬間的ではない** |
| ⚠️★★★ *"attentive techniques having more gaze on the screen (**M = 83.33**; SD = 18.94) than inattentive (**M = 23.53**; SD = 23.87)"*（`U=45, P=.011`） | ⚠️★★★ **指紋解錠では実質 1 秒未満しか画面を見ていない**（★ 4.15s × 23.53%） |
| ⚠️★★★ *"Using the smartphone's front camera for gaze estimation, our study **couldn't analyse gaze behaviour during FaceID unlock**."* | ⚠️★★★ **Face ID については測れていない** |

⚠️★★★ **この一次は不利な側も持っている。隠さない。**

★ **ただし構成概念が違う** —— [P268] が測っているのは **「解錠動作中の視線」**であって
**「ロック画面での滞在時間」ではない**。→ ⚠️ **[P264] と足し合わせてはならない。**
★ **層 A の予算が乗っているのは「解錠に進まない接触」**（★ [P264] の 24.7%・[P240] の 42.6%・[P263] の 54%）
**であり、[P268] が測ったのは「解錠に進む接触」**である。→ ★ **別の母集団。**

#### ★ 決定

★ **層 A の設計上限 2 秒（ADR-021 D10 A-1）を維持する。**

⚠️★★★ **ただし限界を 2 つ明記する**:

1. ⚠️★★★ **Face ID 下での曝露時間を測った査読研究は存在しない。**
   ★ 2024 年の研究ですら測れていないと自ら書いている。→ ★ **iOS の主要生体認証について秒単位のデータが無い。**
2. ⚠️ **生体認証を使う接触では、画面を実際に見ている時間がより短い可能性がある**（[P268]）。
   ⚠️ **N=21・CHI EA（LBW 水準）・Android のみ・較正なし前面カメラ**なので、
   ★ **この数値だけで設計上限を動かす根拠にはならない。**

★ **これは「2 秒で足りる」の追認ではなく、「2 秒より短い可能性を否定できていない」という記録である。**
→ ★ **ADR-021 D10 A-1 が「[P264] の実測（中央値 3 秒）より厳しい側へ倒した設計判断」だったことが、
ここで効いてくる。★ 2 秒は既に安全側である。**

#### ⚠️ 引用してはいけないもの（★ 実測で判明）

⚠️★★★ **[P153] の「準備時間 22.7 秒」「未解錠時の平均 71.5 秒」を使ってはならない。**
★ これらは **[P264] の Related Work による [P153] の要約**であって、**[P153] 本文を直接確認していない**。
→ ★ **`citation-ssot` の「二次引用を根拠にしない」に該当する。** ★ 使うなら [P153] 本文で逐語確認すること。

---

## Alternatives

| 却下案 | 却下理由 |
|---|---|
| ★ **A-7 を維持し、Android だけで出す** | ⚠️★★★ **OS が表現と交絡する**（D1 理由 3）。★ 被験者間で「何を見たか」が違うのに 1 つの結論を出すことになる |
| ★ **A-7 を維持し、実機で `.repeatForever` を試してから決める** | ⚠️★★★ **iOS の AOD の一文が実機実測を待たずに効く**。★ かつ**非対称の問題は実測では解けない** |
| ★ **色を主符号にする**（A-6 を取り下げる） | ⚠️★★★ **iOS では OS が強制的に desaturate するので、そもそも選べない**（D3）。★ かつ [P252] の実証群に色覚多様性の被験者がゼロ |
| ★ **iOS で Live Activities を採る** | ⚠️★★★ **8 時間上限 ＋ push-to-start の alert 必須**により、**技術的理由だけで 1 日 2–3 回の介入が発生する**（D4） |
| ★ **Android でロック画面ウィジェットを採る** | ⚠️★★★ **glanceable hub は AOSP 既定 OFF・「locked and docked」の別シーン・CDD は "MAY"**。★ かつ **BFU で例外なく閉じる**（`grep -c directBootAware` = 0） |
| ★ **専用アプリを第一媒体にする** | ⚠️ **ADR-021 D1 が却下済み** —— open rate 中央値 **4.0%** [P266]・アプリ単独条件 **2.5 件/日** [P148] |
| ★ **Local Push Connectivity で LAN 直受信する（iOS）** | ⚠️★★★ **定義上 PC が常設サーバになり ADR-017 D4 制約 1 に違反する**。★ かつ Apple の entitlement 承認が要る |
| ★ **`CompanionDeviceManager` を搬送路にする（Android）** | ⚠️★★★ **Wi-Fi 上の PC を狙えない**（★ 独立証拠 5 件・D5） |
| ★ **Android で Foreground Service を使う** | ⚠️★★★ **常時通知が出る**（*"Foreground services **show a status bar notification**"*）＝ 本設計では介入に当たる。★ かつ **CDM の権限が免除するのは「BG からの FGS *起動* 制限」であって「通知要件」ではない**（★ 実測: `ActiveServices.java` の通知ロジックに companion 条件は 1 つも無い） |
| ★ **`Text` の日時スタイルで動きを作る（iOS）** | ⚠️ **数字が進むだけ**。★ **ADR-021 D3 の「数値・順位・達成度を出さない」に正面から抵触する** |
| ★ **OS ベンダ文書を `docs/references.md` に登録する** | ★ **先例に反する** —— `agent-shared.md` の Windows TSF / UIPI の逐語は `.steering/` の survey を指している。⚠️ かつ **版番号を持たない living document** なので `[Pn]` の恒久 ID になじまない |

---

## Consequences

### 良くなること

- ★★★ **ADR-021 D1 の但し書きが閉じた。** ★ 「実装時に再検査」が**いま**片付いた。
- ★★★ **実装不能な案を選ぶ危険が消えた** —— ★ これが本セッションを OS 調査から始めた理由である。
- ★★★ **「1 つの面に 1 つの表現」という暗黙の前提が誤りだと分かった**（★ Context 3）。
  → ★ **設計を非対称の上に立て直せる。**
- ★★★ **Android で「常時通知なしの常駐」が成立することが分かった**（★ ライブ壁紙のバインド）。
  → ★ **「通知は介入だから使えない」という詰みが Android では解けた。**
- ★ **A-6 が「文献に基づく設計判断」から「OS の非対称からも要求される制約」へ強くなった**（D3）。
- ★ **S3 の留保（「十分と決めつけない」）に答えが出た** —— ★ **標準が同じ設計を指示していた**（D6）。
- ★ **オフスイッチ要件が両 OS で満たせることを一次で確認した**（D7）。
- ★ **誤った所見を 1 件撤回できた**（D8）。

### 代償（★ 隠さない）

- ⚠️★★★ **A-6 の代替を失った。** ★ 残る符号は **形状・配置・明度** のみ。
  → ★ **層 A の弁別が成立するかは、いよいよ自前の試視でしか分からない。**
- ⚠️★★★ **[P85] の 1° という「文献に支えられた具体値」を失った**（D2）。★ 比で定義し直すと**文献の外に出る**。
- ⚠️★★★ **ADR-021 D3 から「配色テーマを本人が選ぶ」が層 A では落ちた。**
  → ★ **本人の自由度がさらに小さくなった**（★ ADR-021 が既に「音」と「表示場所」を落としている）。
- ⚠️★★★ **iOS では状態遷移の時刻列が Apple 側のメタデータになる**（D5）。★ **避けられない。**
- ⚠️★★★ **実装が OS で 2 本になった。** ★ ウィジェット（iOS）とライブ壁紙（Android）は**別物**であり、
  **共通化できるのは「何を描くか」だけ**である。→ ★ **工数が増える。**
- ⚠️ **セットアップ手順が増えた** —— iOS は「ウィジェットを置く」、Android は「ロック画面にも適用する」。
  ★ どちらも**配置 API が無い**ので本人の操作が要る。
- ⚠️ **iOS は表示の遅延を数値化できない**（★ "opportunistic" の保証値が一次に無い）。
- ⚠️ **Android はロック画面に壁紙が出ることが CDD 保証ではない**（★ OEM 差分の実機確認が要る）。
- ⚠️ **AOD 対応端末かどうかが被験者間の交絡になる**（★ iOS は明度が削られ、両 OS ともアニメーションが出ない）。
- ★ **`EXPR_VERSION` は動かない**（★ 表現層の内部仕様を変更していない）。
- ★ **コード変更ゼロ**（★ `src-tauri/**` / `src/**` の差分なし。★ 表現チャネルは未実装）。

### ⚠️ 本 ADR で閉じていないもの（★ 何が埋まれば閉じるか）

| # | 未決 | ★ 埋める手段 |
|---|---|---|
| **PS-Q5** | **THAT / WHAT / HOW のどの段で止めるか** | ★ **試視の実施**（★ ハーネスは `experiments/20260902-expression-layerA-visual/` にあり機械検査は全緑。⚠️ **まだ回していない**） |
| **E-7** | 層 0 と `stable` を本人が弁別できるか | ★ 同上（★ 混同行列と遷移対 `layer0 ↔ stable`） |
| ★ **M-1** | ⚠️ `.repeatForever` が iOS 実機で動くか | ★ **実機実測**（⚠️ 一次に記述なし）。★ 動いても AOD では出ない |
| ★ **M-2** | ⚠️ alert なし更新で Dynamic Island が一瞬 expanded になるか | ★ **実機実測**（⚠️ **一次内で衝突**）。★ D4 が Live Activities を採らないので判定には効かない |
| ★ **M-3** | **静的な代替符号（縁の開口）の受容性** | ★ 試視（★ ハーネスが両符号を持つ） |
| ~~M-5~~ | ~~曝露量の外的妥当性~~ | ✅ **D9 で閉じた**（★ [P264] の分母を一次で確認・[P268] を追加）。⚠️ **ただし Face ID 下の実測は存在しない**（→ M-9） |
| ★ **M-9** | ⚠️★★★ **Face ID 下でのロック画面滞在・視線の秒単位データ** | ⚠️ **査読研究が存在しない**（★ 2024 年の [P268] ですら測れていないと自ら書いている）→ ★ **自前で測るか、限界として明記し続けるかの二択** |
| ★ **M-6** | ⚠️ macOS / Windows のファイアウォール on-demand 開閉（**S5**） | ★ 未調査 → ★ **W-1 の実装時課題へ送る** |
| ★ **M-7** | ⚠️★★★ **Android の AOD 中に `onVisibilityChanged` が何を返すか** | ★ **実機で `onVisibilityChanged` をログする**（⚠️ AOSP コードだけでは詰め切れない） |
| ★ **M-8** | ⚠️ **OEM 差分**（★ ロック画面に壁紙が出るか・省電力の独自制限） | ★ **実機確認**（⚠️ Google 公式は *"Every manufacturer can set their own criteria"* としか書かない） |
| **W-1** | wire protocol の具体 | ★ 実装着手時の別 ADR（★ **D5 / D6 が前提を足し、宿題を 2 つ足した**） |

⚠️★★★ **A-7 は恒久否決ではない。** ★ 再開条件は **「両 OS で同じ符号として出せるようになる」**こと。
⚠️ **片方の OS だけで出せても採らない**（★ D1 理由 3）。

### ⚠️★★★ 研究衛生上の記録

★ 本 ADR の調査で **罠を 3 つ確認した**:

1. ⚠️ **`developer.apple.com` は JS SPA で本文が取れず、通常の取得では「ページが空」に見える。**
   ★ そこで諦めるか二次資料に流れると、**この領域全体を二次で書くことになる。**
   → ★ **DocC JSON API という一次への経路を survey に記録した。**
2. ⚠️★★★ **中断したエージェントの「発見しかけ」を確定所見として持ち越すと、誤りが混入する**（D8）。
3. ⚠️ **一次の中でも整合しないことがある。** ★ 本調査で **3 件**記録した:
   tint の可否（現行ドキュメント ⇔ HIG）／ Dynamic Island が alert なしで expanded になるか
   （ActivityKit 記事 ⇔ HIG）／ アニメ修飾子を system が無視する条件
   （WidgetKit 記事は **iOS 16 以前に限定**、ActivityKit 記事は**限定なし**）。

---

## Migration

1. ✅ `.steering/20260902-expression-layer-os-constraints/survey-os-constraints.md` に**逐語・URL・OS バージョンの全件**を記録
2. ✅ `experiments/20260902-expression-layerA-visual/` に試視ハーネスを作成（★ 機械検査 Python 30 / ページ内 12・全緑）
3. ⬜ `docs/architecture/expression-channel.md` を追随（**§3.5.1**（表示面が OS で違う）/ **§3.5.2**（A-6 / A-7）/ **§4.1**（配色テーマを層 B へ移す）/ **§7.5**（A12 / A13）/ **§8**（M-1〜M-8））
4. ⬜ `docs/adr/README.md` に本 ADR を追加し、**ADR-021 の行に改訂注記**を入れる
5. ⬜ `docs/participant-setup-guide.md` — ★ **OS 別の配置手順が増える**（⚠️ **被験者向け文書は契約**）
6. ⬜ `data-privacy` Skill — ★ **「iOS では状態遷移の時刻列が外部を通る」を追記**（★ D5）
7. ⚠️ **`docs/references.md` には登録しない**（★ OS ベンダ文書のため。★ 先例に従う）
8. ⚠️ **ADR-021 / ADR-017 の本文は書き換えない**（★ 本リポジトリの規約）。★ 本 ADR の追補で受ける。
