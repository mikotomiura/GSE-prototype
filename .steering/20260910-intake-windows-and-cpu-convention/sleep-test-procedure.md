# ⚠️★★★ スリープ跨ぎ検証 —— **私からは実行できなかった**（★ 手順を渡す）

## ★ 何が起きたか（2026-09-10 02:58 JST）

`pmset sleepnow` が **`Unable to sleep system: error 0xe00002e2`（rc=71）** で拒否された。
⚠️ **測定器の欠陥ではなく、環境が寝られない状態だった。**

★ `pmset -g assertions` の実測:

| ★ 主体 | ★ アサーション |
|---|---|
| ⚠️★★★ **`caffeinate -i -t 300`（親 = `claude`）** | `PreventUserIdleSystemSleep` |
| ⚠️ Safari の **WebKit Media Playback** ×3 | `PreventUserIdleSystemSleep` / `PreventUserIdleDisplaySleep` |
| ★ `coreaudiod`（音声出力中） | `PreventUserIdleSystemSleep` |
| ★ `powerd`「Prevent sleep while display is on」 | 同上 |
| ★ `UserIsActive` | **1**（＝ 操作中と判定されている） |

→ ⚠️★★★ **Claude Code が動いている間、この Mac はアイドルスリープしない。**
★ これは今後の自動スリープ検証すべてに効く（★ 私が回すこの手の実験は**構造的に成立しない**）。

## ★ 実行手順（⚠️ 研究者が叩く）

★ GSE は **起動したまま**（pid は `pre-sleep-snapshot.txt` にある）。

```bash
# ⚠️ ① 先に Safari のメディア再生を止める（★ 止めないと寝ない）
# ★ ② Claude Code を止めるか、寝かせる直前に叩く
pmset sleepnow
#   ★ 効かなければ「蓋を閉じる」でもよい（★ どちらでも検証としては成立する）
```

★ **5 分ほど寝かせてから起こし**、以下を 1 回叩く:

```bash
bash .steering/20260910-intake-windows-and-cpu-convention/post-wake-check.sh
```

## ★ 見るもの（⚠️ 6 項目すべて。1 つでも欠けたら「確かめた」と書かない）

1. ★ プロセスが生きているか
2. ★ 復帰直後のログ（⚠️ `starved_ms` / `tap_enabled` / `delivering events again` / `rehook`）
3. ★ `pmset -g log` で **本当に寝たか**（★ 一次資料）
4. ★ NDJSON の穴が**スリープ時間とほぼ一致**するか（⚠️ 型と時刻だけ・中身は読まない）
5. ★ `.o1_clock_hwm` が巻き戻っていないか（⚠️ 巻き戻ると sweep が止まる・`o1.rs:546`）
6. ⚠️ **打鍵が拾えるか** —— ★ これは**人が何か打ってから**でないと判定できない

## ⚠️★★★ 陰性対照は **すでに崩れている**

★ 今回、**スリープさせていない**のに、GSE 起動の **65 秒後** に飢餓が出た:

```
2026-09-09T17:48:03Z  CGEventTap installed  tap_mode=Input Monitoring
                      input_monitoring=true accessibility=true
2026-09-09T17:49:08Z  ERROR keyboard hook may be dead: the system saw input but
                      the hook was not called   starved_ms=30074
```

→ ⚠️★★★ **復帰直後に飢餓を見ても、スリープが原因とは言えない。**
★ 引き継ぎ §3-3 の警告どおりであり、⚠️ **Windows でも通常稼働中に同型が出ている**。

★ 一方で **NDJSON 自体は健全**だった（★ `feat` 530 行・1 Hz・**最大の穴 1 秒**・30 秒超の穴 **0 個**・
壊れ行 **0**）。→ ⚠️ **「飢餓のログが出た」＝「記録が落ちた」ではない**（★ 2026-09-05 の訂正と同型）。
