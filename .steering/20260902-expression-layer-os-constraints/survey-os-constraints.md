# サーヴェイ記録 — ロック画面の OS 制約・セキュリティ機構

> 2026-09-02 / タスク: `.steering/20260902-expression-layer-os-constraints/`
> ⚠️ **証拠規律**: 一次のみ（Apple / Google / AOSP / Firebase 公式ドキュメント・RFC・NIST）。
> ⚠️★★★ **ブログ・まとめ・AI 生成 SEO ページは 1 件も根拠に使っていない。**
> ★ 取得日は全て **2026-09-02**。⚠️ Apple / Google の当該ページは**版番号を持たない living document** であり、
> 「2026-09-02 時点の内容」としか言えない。

## ★ 取得手法（★ 再検証のために記録する）

⚠️★★★ **`developer.apple.com` の HTML は JS SPA で、通常の HTTP 取得では本文が空になる。**
→ ★ **DocC JSON API を直接叩くと取れる**（★ 前回 17 URL すべて HTTP 200 で実測）:

```
https://developer.apple.com/tutorials/data/documentation/<path>.json
https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json
```

`primaryContentSections` / `abstract` / `metadata.platforms`（`introducedAt` / `deprecatedAt`）を走査する。
★ **availability の OS バージョンは要約モデルを通さず機械的に読み出した。**

---

## 系統 A — iOS ロック画面ウィジェット（WidgetKit）

### ⚠️★★★ A-7（振幅 ~1°・1–3 Hz のその場振動）の判定

★ **「公式に支持された方法は一次に存在しない」。** ⚠️ **ただし「技術的に不可能」と断定する一次も無い。**

| # | 逐語（英語原文） | URL |
|---|---|---|
| **1** | ⚠️★★★ *"**Animations in widgets and Live Activities have a maximum duration of two seconds.**"* | `developer.apple.com/documentation/widgetkit/animating-data-updates-in-widgets-and-live-activities` |
| **2** | ⚠️★★★ *"**On devices that include an Always-On display, the system doesn't perform animations to preserve battery life in Always On.** Check the isLuminanceReduced environment value before animating content changes."* | 同上 |
| **3** | ★ *"WidgetKit renders the views on your behalf in a separate process. As a result, your widget extension is **not continually active, even if the widget is onscreen**."* | `.../keeping-a-widget-up-to-date` |
| **4** | ★ *"**the system can't run your code or update data bindings at the time it renders your widget**"* ／ *"**the system archives a view representation** and only renders the views using these representations"* | 同上 |
| **5** | ★ HIG: *"widgets periodically refresh their information but **don't support continuous, real-time updates**"* ／ *"**Widgets don't show real-time information.**"* | HIG `widgets` |
| **6** | ★ アニメーションは**エントリ間のトランジション**として定義される: *"**every time the content of the widget changes, the system is going to animate the transition between the entries**"* ／ *"SwiftUI determines what is the same and what is different **between the entries**"* | WWDC23 10028 |
| **7** | ★ 継続更新が**逐語で保証されている唯一の経路**: *"**some SwiftUI views let you display content that continues updating while your widget is visible**"* → ★ **`Text` の日時スタイル（`.timer` / `.relative`）のみ** | `.../displaying-dynamic-dates` |

⚠️★★★ **`.repeatForever` がロック画面ウィジェットで持続振動を生むかは、Apple が許可とも禁止とも書いていない**（一次で確認できず）。
→ ★ **現時点で言えるのは「公式に支持されていない」まで。** ★ **実機実測が要る論点である。**

⚠️★★★ **Always-On の一文（#2）は、実機実測を待たずに効く。** ★ AOD 端末の被験者では**アニメーションが 1 フレームも出ない**。

### ★ 更新頻度（★ 公式に数字がある）

| 逐語 | 値 |
|---|---|
| *"a daily budget **typically includes from 40 to 70 refreshes**"* ／ *"roughly translates to widget reloads **every 15 to 60 minutes**"* | ★ **1 日 40–70 回** |
| *"**WidgetKit imposes a minimum amount of time before it reloads a widget.** Your timeline provider should create timeline entries that are **at least about 5 minutes apart**."* | ★ **最小 5 分** |
| *"Your app can **tell WidgetKit to request a new timeline**"* ／ WWDC23: *"**Typically, updates to widgets are done on a best effort basis**"* | ⚠️ `reloadTimelines` は**要求**であって実行ではない |
| *"**Like timeline updates, the system budgets WidgetKit push notifications and delivers them opportunistically**"* | ⚠️ push も同じ檻の中 |
| ⚠️ 即時保証がある唯一の経路（App Intent 起点 *"always guaranteed to occur"*）は **ロック中は使えない**: *"On a locked device, buttons and toggles are inactive"* | — |

→ ★★★ **GSE の 1Hz ゲート・秒オーダーの判定はロック画面ウィジェットへ写せない。** ★ 担えるのは**分オーダーの遅い表示**まで。
⚠️ かつ **「何分以内なら必ず届く」という保証値は一次に無い** → ★ **遅延を設計前提として数値化できない。**

### ⚠️★★★ 色は OS が強制的に落とす（★ A-6 が「選択」でなく「強制」になる）

| 逐語 | 含意 |
|---|---|
| *"it **renders widgets on the Lock Screen on iPhone using the vibrant mode**"* ／ *"**The system desaturates the widget, making a monochrome version**"* | ★ **色相は符号に使えない** |
| 公式対応表: `accessoryCircular` **fullColor = No** / `accessoryInline` **No** / `accessoryRectangular` = Yes | ★ 円形・インラインは**そもそも色を持てない** |
| *"**The brightness of pixels determines how vibrant they appear on the Lock Screen. Brighter gray values provide more contrast, and darker values provide less contrast.**"* ／ *"**use opaque grayscale values, rather than opacities of white**"* | ★ **残る符号は明度だけ** |
| ⚠️ *"**people can also color the Lock Screen to a colored tint**"* ⇔ HIG *"**monochromatic appearance without a tint color**"* | ⚠️★★★ **一次の中で食い違っている**。★ いずれにせよアプリ側が色相を決める余地は無い |
| ⚠️ *"**Devices with the Always-On display render widgets on the Lock Screen with reduced luminance.**"* | ⚠️★★★ **明度が唯一の符号なのに、AOD がその明度を削る** → ★ **AOD の有無が被験者間の交絡になる** |

★ 併せて Apple 自身の一般則: *"**Convey meaning without relying on specific colors to represent information.** … **Use text and iconography in addition to color to express meaning.**"* → ★ **ADR-021 A-6 と方向が一致する。**

### ★ その他

- **形状 3 種**: *"as inline text that appears above the clock, and as **circular and rectangular shapes** that appear below the clock"*。
  公式寸法（430×932pt 端末）: Circular **76×76pt** / Rectangular **172×76pt** / Inline **257×26pt**。
  ⚠️ *"**The sizes of widgets may vary across devices.**"*
- **配置は本人の手動操作**: *"**Touch and hold the Lock Screen**, then tap … **Tap your existing widgets or tap Add Widgets.**"*
  ★ WidgetKit のシンボル索引を機械走査した範囲で**配置 API は存在しない**（あるのは読み取り `getCurrentConfigurations` と更新 `reloadTimelines` のみ）。
- ⚠️ HIG が代替を名指ししている: *"**Offer Live Activities to show real-time updates.**"* ⚠️ ただし *"for a **limited amount of time**"* という用途制約つき。
- ⚠️★★★ **振動に関する Apple の唯一の逐語ガイダンスは visionOS 節にある** ——
  *"**Avoid showing objects that oscillate in a sustained way.** … avoid … around **0.2 Hz** …"*。
  ★ 同ページ冒頭が *"**No additional considerations for iOS**, iPadOS, macOS, or tvOS."* と書いているので、
  ⚠️ **この 0.2 Hz を iOS の根拠に引いてはならない。**
- ★ Reduce Motion: *"**When this setting is active, ensure your app or game responds by reducing automatic and repetitive animations**"*
  → ⚠️ **A-7 を採るなら Reduce Motion 時の代替符号が要る**（★ 新しい設計要件）。

---

## 系統 B — 背景実行と受信経路（★ ADR-017 D4 制約 1 との両立）

### ★★★ 結論: **制約 1〜4 と両立する経路は存在する。⚠️ ただし全て APNs / FCM を経由する。**

⚠️★★★ **「外部サーバを経由しない」×「PC に常設リスナを置かない」×「背景で受信する」の 3 条件同時充足は、iOS には存在しない。**

| 経路 | OS | 制約1 (PC 常設リスナ不要) | 外部サーバ | 背景受信 | 判定 |
|---|---|---|---|---|---|
| **A. ActivityKit push** | iOS 16.1+ | ✅ PC は APNs への outbound HTTPS | ❌ APNs | ✅ | ★ **本命** |
| **B. WidgetKit push** | iOS | ✅ | ❌ APNs | ✅（opportunistic） | ★ 補助 |
| C. silent push | iOS | ✅ | ❌ APNs | △ 保証なし | ⚠️ 毎時 2–3 通まで |
| **D. Local Push Connectivity** (`NEAppPushProvider`) | iOS 14+ | ❌ **PC が常設サーバになる** | ✅ 不要 | ✅ | ⚠️★★★ **制約 1 違反** |
| E. アプリ内 LAN ソケット | iOS | ✅ | ✅ 不要 | ❌ **前景のみ** | ❌ |
| F. MultipeerConnectivity | iOS（iOS 27 で deprecated） | ✅ | ✅ 不要 | ❌ | ❌ |
| G. PushKit VoIP | iOS | ✅ | ❌ APNs | ✅ | ❌ **CallKit 必須** |
| **H. FCM high-priority** | Android | ✅ | ❌ FCM | ✅ | ⚠️★★★ **規約と矛盾**（下記） |
| I. Foreground Service + スマホ待ち受け | Android 8+ | ✅ | ✅ 不要 | ✅ | ⚠️ **常時通知が出る** |

### ⚠️★★★ iOS で LAN 直受信ができない理由（★ 一次）

- ★ 背景実行モードは**列挙されている**: `audio` / `location` / `voip` / `external-accessory` / `bluetooth-central` / `bluetooth-peripheral` / `screen-capture` / `fetch` / `remote-notification` / `processing` / `workout-processing` / `nearby-interaction` / `push-to-talk`。
  → ★★★ **「LAN ソケットを保持する」モードが無い。**
- *"**Typically, an app is in a suspended state when it's in the background.**"*
- *"**Apps don't normally receive any extra execution time after they enter the background.**"*
- 背景移行時の猶予は *"**That method has five seconds**"*。
- ⚠️★★★ *"**If an iOS app is in the background and performs a local network operation while its Local Network privilege is undetermined, the system denies that operation without presenting the local network alert.**"*
- ★ **唯一の LAN 直受信・背景常駐 API** である Local Push Connectivity は、定義上 *"maintain a persistent network connection to **your server**"* → ⚠️ **PC が常設サーバになるので制約 1 違反**。かつ Apple の entitlement 承認が要る。

### ⚠️ APNs の配送品質（★ 設計に直撃する）

| 逐語 | 含意 |
|---|---|
| *"As a best-effort service, **APNs may reorder notifications you send to the same device token**."* | ⚠️ 順序保証なし |
| *"**APNs stores only one notification per bundle ID.** … In most cases, the latest notification is stored. However, **this behavior isn't always guaranteed**"* | ⚠️ 中間状態は落ちる |
| *"tries to deliver it **at least once**"* | ⚠️★★★ **重複配送があり得る** |
| *"**Your notifications may also get throttled, saved in storage, and in some cases, not delivered.**"* | ⚠️ 配送保証なし |
| silent push: *"**don't try to send more than two or three per hour**"* | ⚠️ 毎時 2–3 通 |

★ **Live Activity の運用上限**: *"**A Live Activity can be active for up to eight hours**"* ／ *"remains on the Lock Screen for a maximum of **12 hours**"*
→ ⚠️★★★ **1 日の作業を 1 本の Live Activity で覆えない。**

### ⚠️★★★ Android 側の致命傷（★ 本プロジェクト固有）

| 逐語 | 含意 |
|---|---|
| *"**Foreground services show a status bar notification**, to make users aware that your app is performing a task"* | ⚠️ **通知＝介入なので致命的** |
| ⚠️ *"users still see notices related to foreground services in the **Task Manager**, regardless of whether the notification permission is granted."* | ⚠️ 権限拒否でも消えない |
| ⚠️★★★ *"In fact, **the only intended use for high priority FCM messages is to push a notification to the user**, so this situation must not occur."* | ⚠️★★★ **GSE の要件と正面から矛盾** |
| ⚠️★★★ *"**If FCM detects a pattern in which messages don't result in user-facing notifications, your messages may be deprioritized.**"* | ⚠️ 降格される |
| ⚠️ 降格されると *"**your app cannot start a foreground service**"* | ⚠️ 連鎖して壊れる |
| *"`dataSync` … **a total of 6 hours in a 24-hour period**"* | ⚠️ 時間上限 |
| ⚠️ Doze: *"**Suspends network access.**"* ★ FGS が例外かは**一次で確認できず** | ⚠️ 未確認 |
| ⚠️ *"**Every manufacturer can set their own criteria**"* ／ *"**device-specific power optimizations**"* | ⚠️ メーカー差は Google 自身が認めている |

### ⚠️★★★ 何が外部へ漏れるか（★ 隠さない）

- ★ ActivityKit push の `ContentState` は **`ActivityAttributes` に一致する平文 JSON でなければ system が解釈できない** → ★★★ **E2E 暗号化できない。** `level` / `invitation` / `seq` の値そのものが APNs を通る。
- ⚠️★★★ 加えて **イベントの発生時刻列（＝被験者の作業状態が遷移したタイミング）** が不可避に Apple 側のメタデータになる。
- ⚠️ **Apple が APNs ペイロードを読めるか / 読めないかは一次で確認できなかった。**
  ★ *"No confidential or proprietary information is transmitted through APNs."* は **MDM 配備ガイドの文脈**であり、
  サードパーティ push が E2E 暗号化されるという主張ではない。→ ★★★ **「Apple から見えない」と書いてはならない。**
- ⚠️ Google が FCM ペイロードを読めるか / 保持期間も**一次で確認できなかった**（installation ID は 180 日と明記あり）。
- ⚠️ PC から直接 APNs / FCM に POST するには **PC 側に provider 資格情報（APNs `.p8` / FCM service account 鍵）を置く**ことになる。
  → ★ 被験者の PC 上に配布する秘密が増える。★ 避けるならリレーサーバが要り、**外部依存が 1 段増える**。

---

## 系統 C — リプレイ・順序（S3）

### ★★★ 結論: **OS/プラットフォームはアプリ層のリプレイ防護を一切提供しない。** ★ `epoch` + 単調 `seq` + 巻き戻し破棄は**回避不能で、かつ標準が指示している正解**。

| # | 逐語 | 出典 |
|---|---|---|
| 1 | ⚠️★★★ APNs / FCM の一次文書に **"replay" は 0 件**（両者とも grep ヒット 0） | 実測 |
| 2 | *"**FCM doesn't guarantee the order of delivery.**"* | firebase.google.com/docs/cloud-messaging/customize-messages/collapsible-message-types |
| 3 | *"it doesn't mean that the message was already delivered … it means that it was **accepted for delivery**"* | `.../setting-message-lifespan` |
| 4 | ⚠️ *"For Android, there is a limit of **100 messages** that can be stored without collapsing. **If the limit is reached, all stored messages are discarded.**"* | `.../collapsible-message-types` |
| 5 | ★ TLS 1.3: *"Protection against replay for **ordinary TLS 1.3 1-RTT data is provided** via the server's Random value"* | RFC 8446 §2.3 |
| 6 | ★★★ TLS 1.3: *"The second class of attack **cannot be prevented at the TLS layer and MUST be dealt with by any application.**"* | RFC 8446 §8 |
| 7 | ★★★ NIST: *"GCM, like many other authentication mechanisms, **does not inherently prevent** an adversary from … '**replaying**' it"* | NIST SP 800-38D App. D |
| 8 | ★★★ NIST が **GSE の設計そのものを逐語で推奨**: *"certain identifying information can be incorporated into the AAD. Examples … include a **sequential message number or a time stamp**. Upon successful verification of authenticity, this information may provide a means for the **detection of replayed messages, out-of-sequence messages, or missing messages**."* | 同上 |
| 9 | ★ HOTP: *"If the value received … matches … **the server increments the counter value by one**."*（★ `seq` と同型） | RFC 4226 §7.2 |
| 10 | ★ TOTP: *"The verifier **MUST NOT accept the second attempt** of the OTP after the successful validation"* | RFC 6238 §5.2 |

⚠️ **`apns-collapse-id` / `apns-id` はリプレイ検出用ではない** —— `apns-id` の逐語用途は *エラー報告時の突合* のみ。
⚠️ **Android KeyStore の "rollback resistance" / RPMB は無関係** —— 守っているのは*削除した鍵の復元*と*ストレージの巻き戻し*であって、
ネットワーク上のメッセージ再送ではない。★ かつ `setRollbackResistant` は**公開 Android API に存在しない**（実測）。

→ ★★★ **唯一の追加提案**: NIST App. D に従い、`epoch` / `seq` を**平文フィールドではなく AEAD の AAD（または署名対象）に含める**。
★ 改竄と再送の判定が 1 つの検証に畳める。

---

## 系統 D — ペアリング（S1）の iOS 側

### ★ 結論: **OS がペアリング相当の同意を強制する経路は限られる。**

| 技術 | OS が明示操作を**強制**するか | 逐語 |
|---|---|---|
| **MultipeerConnectivity** | ⚠️ **強制しない** | *"Apps running on the nearby devices **can choose** whether to accept or reject the invitation, and **can ask** their users for permission."* ／ `invitationHandler` は *"a block that **your code must call**"* → ★ **無音の auto-accept が可能** |
| **DeviceCheck / App Attest** | ⚠️ **一次にユーザー操作の記述が無い**（無音） | ★ 相手は *"**your own server**"* 限定 → ⚠️ **PC アプリを iPhone アプリに対して認証する用途の記述は存在しない** |
| **ASWebAuthenticationSession** | ✅ **強制する** | *"**the operating system shows a modal view telling them which domain the app is authenticating with and asking whether to proceed**"* |
| **NearbyInteraction** | ✅ 強制する（⚠️ ただし*位置共有の可否*であって相手選択ではない） | *"the framework presents a prompt that displays the textual value of `NSNearbyInteractionUsageDescription`"* ／ ⚠️ **UWB 必須** ＋ transport は自前 |
| **Keychain 共有** | ⚠️ **強制しない**（明示的に不要と書かれている） | *"**This kind of sharing doesn't require interaction with or permission from the user, but limits sharing to apps that are delivered by a single development team.**"* |
| **AccessorySetupKit** (iOS 18+) | ✅ **強制する**（★ OS が picker を出し人が選ぶ＝ S1 に最も忠実） | *"**for the operating system to present a picker**"* ／ ⚠️ **Bluetooth / Wi-Fi アクセサリ限定** |

⚠️★★★ **異なる開発者の Mac アプリと iOS アプリが keychain item を共有することはできない**（逐語で "single development team"）。

### ★ Local Network privacy（S5 に効く）

| 逐語 | 含意 |
|---|---|
| *"The first time a program accesses the local network, **the system displays an alert** asking the user to approve that access."* ／ *"**future accesses don't prompt**"* | ⚠️ 一度きり。**相手を特定しない** |
| ★ **inbound の accept は local network 権限を要求しない**: TCP *"Listening for and accepting incoming TCP connections"* → **no** ／ UDP *"Receiving an incoming UDP unicast"* → **no**（★ outbound は yes） | ★ 重要 |
| *"**All Bonjour operations require local network access.**"* | — |
| *"If your program successfully made a TCP connection … and then the user changed the Local Network privilege to deny …, **the connection closes**."* | ★ 失効経路になる |

⚠️ **MultipeerConnectivity は iOS 27 / Xcode 27 で deprecated**（★ iOS 26 時点では未 deprecated）:
*"**Xcode 27 deprecates the entire Multipeer Connectivity framework.**"* → ★ **新規採用は非推奨。**

---

## ⚠️ 一次で確認できなかったこと（★ 埋めない）

1. ⚠️★★★ **`.repeatForever` / `withAnimation` + `onAppear` がロック画面ウィジェットで持続振動を生むか** —— Apple は許可とも禁止とも書いていない。★ **実機実測が要る。**
2. ⚠️ **`TimelineView` がウィジェットで動作するか** —— 肯定・否定いずれの一次記述も無い。★ WidgetKit の対応ビュー一覧に無いが、**その一覧は `Gauge` / `ProgressView` も欠くので不完全**であり、**不在は証拠にならない**。
3. **ウィジェットのアニメーションが有効になる最小 iOS バージョン** —— *"In earlier OS versions, widgets don't animate"* の「earlier than what」が逐語で書かれていない。
4. **1 日あたりのハードな上限回数** —— *"typically includes from 40 to 70"* は**典型値**であって上限の明記ではない。
5. **ロック画面の点灯 / raise to wake でリロードが走るか** —— 一次に記述なし。
6. **アニメーションが vibrant / accessory ファミリで実際に実行されるか** —— 明示的な例外として書かれているのは **Always-On のみ**。
7. **Apple が APNs ペイロードを読めるか** / **Google が FCM ペイロードを読めるか・保持期間** —— どちらも一次に明示なし。
8. **Doze 中に Foreground Service がネットワークを維持できるか** —— Doze の doc は *"Suspends network access."* とだけ書き、**FGS が例外かを明記していない**。★ Android 経路 I の実用性はここに懸かる。**実機実測が要る。**
9. **Live Activity の push-to-start（`pushToStartToken`）** —— 8 時間上限を跨ぐ再開手段として重要だが逐語未取得。★ **再調査中。**
10. **FCM が重複配送するか**（at-least-once か at-most-once か）—— 一次に記述なし。★ **APNs は "at least once" と明言するので、両者の明示性は非対称。**
11. **実機実測は一切行っていない**（iOS / Android 実機が本環境に無い）。★ **すべて文書ベースである。**
12. **macOS / Windows のファイアウォールを on-demand に開閉する公式作法**（S5）—— ★ 未調査。W-1 の実装時課題として残す。

---

## 系統 E — Android（★ ロック画面の面 / secure lock screen / CompanionDeviceManager）

### ★★★ 結論: **ロック画面で常時アニメーションできる 3rd-party の面は「ライブ壁紙」一つだけ**

| 面 | 3rd party API | アニメ | 逐語 / 実測 |
|---|---|---|---|
| **ライブ壁紙 (`WallpaperService`)** | ✅ 公開 | ✅ **任意 Canvas/GL・レートはアプリ制御** | *"Called to inform you of the wallpaper becoming visible or hidden. **It is very important that a wallpaper only use CPU while it is visible.**"*（`WallpaperService.java` L774-780） |
| └ ロック画面で見えるか | ✅ **AOSP は見せる** | ✅ | SystemUI `applyKeyguardFlags()`: *"**Show the wallpaper if we're on keyguard/AOD** and the wallpaper is not occluded by a solid backdrop."* → `FLAG_SHOW_WALLPAPER`（`NotificationShadeWindowControllerImpl.java` L361-372） |
| └ 画面 ON との連動 | — | — | *"As some wallpapers use visibility as a signal to start animations, this makes sure `Engine#onVisibilityChanged` is invoked **only when the display is both on and visible (with brightness on)**."*（L262-270） |
| └ ⚠️ `FLAG_LOCK` で lock 専用に設定 | ❌ **3rd-party 不可** | — | `setWallpaperComponentWithFlags(name, which)` は `@SystemApi`+`@hide`、`SET_WALLPAPER_COMPONENT` = `signature\|privileged` |
| └ ⚠️ lock 壁紙が別設定だと隠れる | — | — | *"When called with which=`FLAG_LOCK`, clear the lockscreen wallpaper. **The home screen wallpaper will become visible on the lock screen.**"* |
| └ 3rd-party の設定経路 | ✅ **本人の確認必須** | — | *"Directly launch live wallpaper preview, **allowing the user to immediately confirm** to switch"*（`ACTION_CHANGE_LIVE_WALLPAPER`・API 16） |
| **AOD / Ambient** | ❌ **公開 API は存在しない** | — | `<attr name="supportsAmbientMode">`: *"**This feature requires the android.permission.AMBIENT_WALLPAPER permission. @hide @SystemApi**"*（★ 当該権限は `signature\|preinstalled`）。`isInAmbientMode()` / `onAmbientModeChanged()` も `@SystemApi @hide` |
| └ さらに targetSdk 35+ で封鎖 | — | ❌ | *"This change disables the `DRAW_WAKE_LOCK`, an internal wakelock acquired per-frame duration display DOZE. **It was added to allow animation during AOD.** … it will be removed."*（`@EnabledSince(VANILLA_ICE_CREAM)`） |
| **ロック画面ウィジェット (glanceable hub)** | △ **実質不可** | △ | `WIDGET_CATEGORY_KEYGUARD` は **API 17・非 deprecated**（★ API 36 で `WIDGET_CATEGORY_NOT_KEYGUARD` 新設）だが、⚠️ `<bool name="config_glanceableHubEnabled">**false**</bool>`／*"The communal scene shows the glanceable hub **when device is locked and docked**."*／CDD *"**MAY support** application widgets on the lock screen."* |
| └ `updatePeriodMillis` 最小値 | — | — | *"**Updates requested with `updatePeriodMillis` will not be delivered more than once every 30 minutes.**"*（★ AOSP `MIN_UPDATE_PERIOD = 30 * 60 * 1000`）。★ **明示 `updateAppWidget()` は非スロットル** |
| └ `RemoteViews` の許可リスト | ✅ 限定的 | △ | 逐語 *"**Descendants of these classes are not supported.**"*。★ `ViewFlipper`（`android:flipInterval`）/ `ProgressBar`（`indeterminateDuration`）/ `AnalogClock` で 1–3 Hz は技術的に出せる。⚠️ **面そのものが依存できない** |
| **オーバーレイ窓** | ❌ **ロック画面の下に敷かれる** | — | 層番号: `TYPE_WALLPAPER` = **1** / `TYPE_APPLICATION_OVERLAY` = **11** / `TYPE_NOTIFICATION_SHADE` = **17** |
| **Smartspace** | ❌ | — | `@SystemApi` |
| **DreamService** | ✅ 公開・任意描画 | ✅ | ⚠️ *"launched when a charging device is **idle, or docked in a desk dock**"* ＝ 用途が違う |

### ⚠️★★★ (a)/(b)/(c) で `Engine` は visible になるか（★ 曝露予算の中心）

| 局面 | 判定 | 確度 |
|---|---|---|
| **(a) 画面 ON・ロック画面を見ている数秒** | ✅ **visible = true。描画される** | ★ **高**（AOSP 実装コードで直接確認） |
| **(b) AOD 中** | ❌ **3rd-party はアニメーションできない** | ★ 高（★ ただし `onVisibilityChanged` の実値は **end-to-end 未確認** → **M-7**） |
| **(c) 画面消灯中** | ❌ 描画されない | ★ 中〜高 |

→ ★★★ **曝露予算を (a) に賭ける設計は正しい。** ★ (a) は AOSP 実装コードで裏が取れている。
⚠️ **フレームレート上限は見つからなかった**（★ 「無い」ことを網羅確認したわけではない）。

### ★ secure lock screen（Android）

| 項目 | 逐語 / 実測 |
|---|---|
| 通知の既定 | *"**The default level, `VISIBILITY_PRIVATE`**, … The notification's icon and tickerText … are shown in all situations, but the contents are only available if the device is unlocked"* |
| チャネル単位はアプリから設定不可 | `setLockscreenVisibility()`: *"**Only modifiable by the system and notification ranker.**"* |
| `isUserUnlocked()` | *"**On devices with direct boot, a user is unlocked only after they've entered their credentials** … **When a user is locked, only device-protected data storage is available.**"* |
| ★ **BFU でライブ壁紙は動く**（`directBootAware` 必須） | *"This happens for **wallpapers that are not direct-boot aware**; they can only be rendered after the user unlocks the device for the first time after a reboot. **In the meantime, the default wallpaper is shown instead.**"* ／ ログ *"Wallpaper isn't direct boot aware; using fallback until unlocked"* |
| ⚠️★★★ **BFU で AppWidget は不可（例外なし）** | `AppWidgetServiceImpl.java` **L1017-1020**: `throw new IllegalStateException("User " + userId + " **must be unlocked for widgets to be available**")` ／ ★ **全 7109 行に対する `grep -c directBootAware` = 0**（★ 実測） |
| ★ **stopped 状態からの正規の離脱事由** | `ApplicationInfo.FLAG_STOPPED`: *"could also include user actions like adding it as an app widget, **selecting it as a live wallpaper**, selecting it as a keyboard"* → ★ **裏技ではなく OS が想定した常駐の作り方** |
| ★ 本人が止める経路 | `ACTION_SET_WALLPAPER`（API 1）／ `ACTION_LIVE_WALLPAPER_CHOOSER`（API 7）／ `clear(int)` = *"reverting to the system default"*（API 24） |
| ⚠️ 常駐と統制のトレードオフ | *"The following types of apps are exempt from entering the restricted bucket … **Apps with active widgets**"* |

### ⚠️★★★ `CompanionDeviceManager` は搬送路にならない（★ 独立証拠 5 件）

| # | 実測 |
|---|---|
| ① | `public final class WifiDeviceFilter implements DeviceFilter<**ScanResult**>` —— ★ `android.net.wifi.ScanResult` は**アクセスポイント**。`matches()` は namePattern と BSSID のみ |
| ② | *"For Bluetooth classic devices this is triggered when the device connects/disconnects. **WiFi devices are not supported.**"*（`startObservingDevicePresence`） |
| ③ | `android.companion` 全ソース ＋ `services/companion` を `mdns\|nsd\|dns_sd\|dnssd\|bonjour\|zeroconf` で grep → ★ **0 件** |
| ④ | ⚠️★★★ `android.companion` 全ソースを `picker` で grep → ★ **0 件**。公開 SDK の `FLAG_` 定数は `FLAG_CALL_METADATA = 1` のみ → ★ **前セッションの「`FLAG_SHOW_PICKER` 発見」は誤り。撤回する**（→ ADR-022 D8） |
| ⑤ | `setSelfManaged()` は `signature\|privileged`、`REQUEST_COMPANION_PROFILE_COMPUTER` も `signature\|privileged`（*"**Not for use by third-party applications.**"*）、`notifyDeviceAppeared()` は `@SystemApi @hide` |

★ **CDM の picker 相当 UI は存在する** —— *"**choose the device to associate the application with** … **confirm the association**"*。
⚠️ **ただしそれは `IntentSender` 経由の関連付け確認 UI であって、mDNS 探索ではない。**

⚠️★★★ **FGS の「通知要件」は免除されない**（★ 混同しやすい）:
★ `REQUEST_COMPANION_RUN_IN_BACKGROUND`（protection level **normal**）が免除するのは
**「BG からの FGS *起動* 制限」**であって、**「常時通知を出す要件」ではない**。
★ 実測: `ActiveServices.java` の通知ロジックに **companion 条件は 1 つも無い**。
★ `startForeground()` 逐語: *"supplying **the ongoing notification to be shown to the user** while in this state"* ／
*"notification Notification: … **This value cannot be null.**"*

⚠️ **関連付け解除 UI は AOSP Settings に存在しない**:
`BluetoothDetailsCompanionAppsController.isAvailable()` が *"// Do not show this preference for now."* で
`false` を返す状態が **main / 16 / 15 / 14 / 13 の全ブランチで同一**。
★ ガイド逐語: *"**The companion app is responsible for clearing its own associations**"*。
→ ★ **将来 CDM を使うなら解除 UI は自前実装が要る**（★ 同意文書の撤回手段と直結）。

★ **アンインストール / データ消去**: `onPackageRemoved` / `onPackageDataCleared` の両方が全 association を `disassociate()`。

### ⚠️ 系統 E で一次に届かなかったもの（11 項目・★ 主要なもの）

1. **Pixel など実機で glanceable hub が有効か**（★ AOSP 既定 false・有効化は端末 overlay）
2. **Android 15/16 のロック画面ウィジェット公式発表ページ** —— ★ `/develop/ui/views/appwidgets/lockscreen` 等は **404**
3. **`WallpaperService` リファレンスの Direct Boot 記述** —— ★ ページ内 0 hits（根拠は AOSP のコメント／ログ文字列のみ）
4. ⚠️★★★ **CDD にロック画面へ壁紙を出す要件は無い** → ★ **「ロック画面に壁紙が見える」は AOSP 実装の事実であって CDD 保証ではない**（★ OEM が変え得る）
5. **OEM 固有挙動**（Samsung / Xiaomi の省電力）—— ★ Google 公式は *"Every manufacturer can set their own criteria"* のみ
6. **Doze 中の bound `CompanionDeviceService` のネットワーク保証**
7. ⚠️★ **AOD 中に 3rd-party `Engine` へ渡る `onVisibilityChanged` の実値**（→ **M-7**）
8. ⚠️★ **ロック画面／壁紙固有のフレームレート上限の有無**

---

## 系統 G — 曝露量の外的妥当性（★ 顔認証時代）

### ★★★ 結論: **(A) 崩れていない。** ⚠️ ただし限界を 2 つ明記する。

#### ★ [P264] の分母を一次で確認した（★ 想定どおりだった）

| 逐語（本文） | 何が分かるか |
|---|---|
| *"Overall, this resulted in a dataset of **n=894 unique smartphone use sessions, of which 221 (24.7%) constituted locked phone use**."* | ★ **分母は 221 件＝ロック状態のまま完結した接触** |
| *"**Lock screen checks ranged between 1s and 22s and lasted 4.2s on average (median 3s, standard deviation 4.1s).**"* | ★ **4.2 秒 / 中央値 3 秒はロック画面での接触の値** |
| *"We find that about a quarter of smartphone interactions represent using the phone for a very brief amount of time (**3-4s on average**) in a locked state."* | ★ Discussion でも一致 |

★ **測定は端末ログではなく一人称カメラ（Subcam・200 時間超）の行動コーディング**
（★ 二重コーディング一致率 **94%** / Krippendorff's α = **0.91**）。
→ ★ **「実際に見ている時間」に近く、本プロジェクトの構成概念に合致する。**
★ 標本 n=41・**iOS 78%**・UK 2018–2019 収集 → ★ **顔認証普及後の iOS 主体の標本である。**

#### ★ 2024 年の一次を 1 本追加した（→ `[P268]`）

★ **Abdrabou et al., CHI EA '24**, doi:10.1145/3613905.3651094（★ 著者版 OA: `eprints.gla.ac.uk/323192`）
N=21・24 時間 in-the-wild・前面カメラ ＋ Seeso.io（較正不要）・**Android 専用**。

| 逐語 | 含意 |
|---|---|
| *"On average, participants took **6.33s for patterns, 5.94s for passwords, 4.51s for PINs, and 4.15s for fingerprints**. Participants unlocked their phones an average number of **37.71 times** (max=58, min=8)."* | ★ 2024 年でも解錠まわりは瞬間的でない |
| ⚠️★★★ *"attentive techniques having more gaze on the screen (**M = 83.33**; SD = 18.94) than inattentive (**M = 23.53**; SD = 23.87)"*（`U=45, P=.011`） | ⚠️★★★ **指紋解錠では実質 1 秒未満しか画面を見ていない** |
| ⚠️★★★ *"Using the smartphone's front camera for gaze estimation, our study **couldn't analyse gaze behaviour during FaceID unlock**."* | ⚠️★★★ **Face ID は測れていない** |

⚠️★★★ **構成概念が違うので [P264] と足し合わせてはならない** ——
★ [P268] が測ったのは **「解錠動作中の視線」**、[P264] は **「ロック画面での滞在時間」**。
★ 層 A の予算が乗っているのは **「解錠に進まない接触」**（★ [P264] の 24.7% / [P240] の 42.6% / [P263] の 54%）
であり、[P268] が測ったのは **「解錠に進む接触」**である。→ ★ **別の母集団。**

#### ⚠️★★★ 引用してはいけないもの（★ 実測で判明）

⚠️ **[P153] の「準備時間 22.7 秒」「未解錠時の平均 71.5 秒」を使ってはならない。**
★ これらは **[P264] の Related Work による [P153] の要約**であって、**[P153] 本文を直接確認していない**。
→ ★ **`citation-ssot` の「二次引用を根拠にしない」に該当する。**

#### ⚠️ 探したが見つからなかったもの（★ 検索式を明記）

⚠️ **本セッションは WebSearch の予算を使い切ったため、Crossref / OpenAlex / Semantic Scholar の API 直叩きのみ**
（★ 各 2 クエリ程度の軽い探索であり、**網羅的な「存在しない」の証明ではない**）。

1. **Face ID / 生体認証時代（2018 年以降）のロック画面滞在時間の実測（iOS 中心）**
   —— 検索式 `Face ID unlock duration field study smartphone`（OpenAlex・from 2018-01-01）→ **該当なし**
2. **「ロック画面止まりの接触割合」の 2018 年以降の再測**
   —— 検索式 `smartphone screen checks not unlocked percentage field study`（Crossref・from 2018-01-01）→ **該当なし**
3. **通知がロック画面での視線を横取りする問題の秒単位実測** —— ★ **未着手**（時間予算）
