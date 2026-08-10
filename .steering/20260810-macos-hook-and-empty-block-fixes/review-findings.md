# 【3】レシート UI のレビュー結果 (2026-08-10)

対象: コミット `b4c9e5f` (`feat(frontend): 提出の成功を肯定形で出し、6 秒の無表示を埋める`)。
⚠️ ★ **このコードは v0.1.25 として既に被験者へ配布済み**である。

`code-reviewer` と `security-checker` を並列で実行した。
⚠️ `/cross-review` (Codex) は**未実施**。

## 総括

| 深刻度 | 件数 | 要旨 |
|---|---|---|
| HIGH | 2 | 送信が失敗している最中／梱包前の窓に、**肯定形のレシートが出る** |
| MEDIUM | 5 | 参加者 ID 変更で嘘をつく / 絶対パス (実名) の露出 / 梱包中の無表示 / 分単位の「数秒」/ 数え損ねを ✅ と出す |
| LOW | 6 | Atomic の ordering、時計、文言の細部 |

★ backend 側の「押した ≠ 送れた」(D-1) は **3 段で守られており破れていない**
(`upload() == Ok` かつ `.sent` 書き込み成功のときだけ `sent += 1`、
GAS の HTTP 200 ではなく本文 `"ok":true` を要求)。
⚠️ 壊れているのは **フロント側の表示条件が時間軸を持っていない**ことである。

---

## HIGH-1: 送信が失敗している最中に「送信は完了しています」が出る

`src/App.tsx:738-763`

**壊れる条件** (実運用で起きる):
ブロック 1 が送信成功 (`last_sent_ms` が立つ) → ブロック 2 で「送信する」→
Wi-Fi 断 / GAS 停止で upload 失敗。このとき `.ok` は付いているので
`awaiting_approval == 0`、スレッド終了で `sending == false`、
`last_sent_ms` は **ブロック 1 のまま非 null** → 表示条件 3 つを全部通過する。

→ 画面に **赤いエラーカード ＋ 未送信カード ＋ 緑の「✅ この回の記録を送信しました」** が並ぶ。

⚠️ `awaiting_approval > 0` のゲートはこの経路を塞げない (承認済みで未達は 0 に落ちる)。

**修正方針**: 断定文と「この回」を条件付きにする。
`unsent === 0 && last_error === null` のときだけ
「送信は完了しています。次のブロックに進んでください。」を出す。

## HIGH-2: ブロック終了直後の数秒、前の回のレシートが残る

`src-tauri/src/lib.rs` の `emit("g1-block-ended")` と `spawn_reconcile` の間。

**壊れる条件**: `sending: true` が立つのは ack 待ちの**後**なので、その間フロントは
`awaiting_approval=0 / unsent=0 / sending=false / last_sent_ms=前の回` を読む。
→ ★ **2 ブロック目以降、毎回**最大 3 秒 (ack タイムアウト時 8 秒) 緑のレシートが残る。
1 ブロック目は代わりに「✅ 送信を待っている記録はありません」が出る (梱包前なので**事実に反する**)。

**修正方針**: `InFlightGuard` を `emit("g1-block-ended")` **より前**で作って
`spawn_reconcile` に渡す。併せて G1 の `start_session` で `SUBMIT_LAST_SENT_MS/COUNT` を 0 に戻す。

## MEDIUM-1 (security): `last_error` に絶対パス = **OS ユーザー名**が載る

`lib.rs:967 resolve_submit_bin()` → `lib.rs:1248` (`redact_home_path` を通らない)
→ `App.tsx:813` が `<code>` で生表示。

⚠️★ 画面の文言は「**次の内容を研究者にお伝えください**」であり、
**被験者にスクリーンショット共有を促している**。Windows では
`C:\Users\<実名>\Downloads\...` になりうる。→ ★ **P012 と実名が同じ画像に並ぶ = 仮名化の解除。**

発火条件は現実的 (AV が `gse-submit.exe` を隔離 / 被験者が exe だけ別フォルダにコピー)。
同じ穴が手動提出側 (`lib.rs:976` → `Dashboard.tsx:114`) にもある。

**修正方針**: `resolve_submit_bin` のメッセージからパスを落とす、
または `*slot = Some(redact_home_path(&e))` にする。

## MEDIUM-2 (security): 参加者 ID を打ち直すと、緑カードが嘘をつく

`SUBMIT_LAST_SENT_MS/_COUNT` は **プロセス全体で 1 組**で ID を持たないが、
`unsent` / `awaiting_approval` は **現在の ID 限定**で数える (前方一致・大文字小文字を区別)。

→ 被験者が `P012` → `P013` (あるいは `p012`) と打ち直すと既存の `.age` が全部 orphan 化し、
`unsent = awaiting_approval = 0` になる。
- 直前に送信実績があれば → **偽レシート**が出続ける
- 実績が無ければ → 「✅ 送信を待っている記録はありません」(未送信の `.age` が実在するのに)

⚠️ ★ 未送信ブロックが恒久的に届かないまま、被験者にも研究者にも警告が出ない。
**このコミットが潰そうとした失敗様式そのもの** (無表示 → 肯定形の誤情報に格上げ)。

## MEDIUM 残り

- **梱包フェーズが完全に無表示** (`App.tsx:658` の `unsent > 0` ゲート。`.age` 生成前は 0)
- **「数秒かかります」が分単位になりうる** (timeout 180 秒/件。3 件で最悪 9 分。
  その間 `!sending` ゲートで**未送信カード = 唯一の安全装置が隠れる**)
- **数え損ねを ✅ と出す** (`lib.rs:1143-1152` はホーム/ID が解決できないと `(0,0)` を返す
  → 実際には `.age` があるのに「送信を待っている記録はありません」。★ fail-open への退行)

## LOW (抜粋)

- `SUBMIT_IN_FLIGHT` の `fetch_sub`/`load` が `Relaxed` で `last_sent_ms` の `Release` と
  同期しない (aarch64 = macOS ビルドでのみ 1 ポーリング分ずれうる)
- `now_ms` の `.unwrap_or(0)` が「まだ 1 件も送っていない」センチネルと衝突する
- 「この回の記録を送信しました（3 件）」— 「あとで」を勧めている以上 `count > 1` は普通に起きる
- `npm audit` high 3 件は **すべて devDependencies (vite)**。配布バイナリには載らない

## ★ 漏れないと確認できたもの (security)

- 打鍵・文章内容: レシートが読むのは **件数と epoch ms だけ**
- `.age` の平文フォールバックは**無い** (recipient 解決に失敗すれば `Err`)
- `g1-submit.json` の `secret` は URL・エラー文字列・`tracing` のいずれにも現れない
- 参加者 ID の検証は書き込み時と読み取り時の**両方**に掛かっており、`../` は入らない
- `last_error` は React のテキスト補間 (`dangerouslySetInnerHTML` 不使用 = XSS 無し)

---

## ⚠️ 本タスクでの扱い

★ **どれも本タスクでは直していない。** 配布済みバイナリに入っており、
直すには再ビルド → 再検証 → 再配布が要る。**研究者の判断が要る。**
