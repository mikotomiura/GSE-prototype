# decisions

## D1: 層 2（再有効化）と層 3（作り直し）の**両方**を入れる

- **決定**: runloop timer で `CGEventTapIsEnabled` を見て再有効化し、それでも Down が続くなら
  `CFRunLoopStop` で既存の再作成経路を起こす。
- **理由**: ★ 2 つの機序（「tap が disable された」／「runloop が楽をしている」）は
  **別の手段でしか救えない**。⚠️ 2026-09-04 の実測ではどちらだったか**記録が無い**ので、
  片方だけ入れると外す可能性がある。
- **却下案**:
  - ⚠️ 再有効化だけ → **runloop 自体が楽をしていると timer も発火しない**ので手が無い。
  - ⚠️ 作り直しだけ → 毎回 2 秒の空白が出る（★ 軽い手段で済むなら済ませたい）。

## D2: 診断は `tracing` に出す（⚠️ NDJSON スキーマは変えない）

- **決定**: `tap_enabled` / `watchdog_recoveries` を Down のログ行にのみ載せる。
- **理由**: ★ `schema_dto.rs` を触ると `emit_schema` / `schema/current.json` / gse-dataset の
  parity まで波及する。⚠️ 診断 1 個に払う代償として大きい。
  ★ 研究者の機械では `gse-app.log` で「次の 1 回」が決着する。
- **却下案**: NDJSON の `hook_health` に列を足す → ⚠️ 被験者データにも残るが、
  ★ 必要になったら別 PR で足せる（⚠️ 今入れると本 PR の検証範囲が広がりすぎる）。

## D3: `request_reinstall()` は「出せなかった」を `false` で返し続ける

- **決定**: フック未起動 / run loop 未取得なら `false`。⚠️ `true` と偽らない。
- **理由**: ★ ログの `rehook_requested` は**研究者が機序を判断する唯一の手掛かり**である。
  ⚠️ 「呼んだ」を「効いた」と読ませると、2026-09-04 と同じ調査の空回りが起きる
  （memory `silent-success-is-not-visible`）。
- **却下案**: 呼べたら常に `true` → ⚠️ 何も起きていないのに緑に見える。

## D4: 上限 3 回で諦める

- **決定**: `MAX_REHOOK_ATTEMPTS_PER_EPISODE = 3`。
- **理由**: ⚠️ 上限が無いと 1Hz で `CFRunLoopStop` を叩き続ける。★ 1 回だと
  **今回のバグ（出せていないのに済みにする）を再現する**。
- ⚠️ **3 に出典は無い**（★ 恣意的である）。→ ★ 明記して、測った後に動かさない。
