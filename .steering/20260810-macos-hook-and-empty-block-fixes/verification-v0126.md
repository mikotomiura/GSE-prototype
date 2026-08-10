# v0.1.26 の macOS 実機確認 (2026-08-10)

**使ったもの**: `dist/_common/G1_実施用_macOS.zip` (v0.1.26 の dmg から組んだ**配布物そのもの**) を
展開した `gse-next.app`。参加者 ID は **`P999`**、実施週 = 第1週 (blind 較正)。ブロック 2 本。

---

## ★★ 修正【4】— Input Monitoring の要求。**実機で赤→緑を確認**

⚠️★ 新しいパスに置くと Input Monitoring だけ denied に戻り、Accessibility は
署名で引き継がれる。→ **壊れていた条件 (`IM denied && AX granted`) をそのまま再現できた。**

```
07:08:09  Input Monitoring permission not granted. Opening System Settings ...   ← ★ v0.1.25 では出なかった
07:08:09  Polling for Input Monitoring permission...
07:08:09  Input Monitoring denied but Accessibility granted. Trying Default tap (Accessibility) first
          (Input Monitoring has still been requested above).
```

v0.1.25 は同じ状態で `Using Default tap (Accessibility) directly — skipping ListenOnly` だけを出し、
★ **システム設定を開かないまま黙って失敗し続けた**。→ `decisions.md` D-5 の「実機未実施」が埋まった。

### 成功時のログも実態を出すようになった

```
CGEventTap installed (macOS keyboard hook active) tap_mode=Input Monitoring input_monitoring=true accessibility=true
```

⚠️★ **測定器の罠を 1 つ踏みかけた**: 端末から**直接**実行すると `input_monitoring=true` と出るが、
これは **VS Code の権限を継承しているだけ**である。`open` 経由 (= 被験者と同じ経路) では denied だった。
★ **直接起動での権限判定は当てにならない。**

---

## レシート UI — 5 項目

| | 期待 | 結果 |
|---|---|---|
| 【1】 | ブロック終了後に確認カード | ✅ 出た (1 本目・2 本目とも) |
| 【2】 | `記録を送信しています…` | ⚠️ **観測できず** (下記) |
| 【3】 | `✅ この回の記録を送信しました（HH:MM・N 件）` | ✅ 出た (`16:28・1 件` / `16:35・1 件`) |
| 【4】 | 文字が読めるか | ✅ 読める。★ 背景と同色の文字は無い |
| 【5】 | `✅ 送信を待っている記録はありません。` | ✅ 出た (★ `counted` 条件の確認・下記) |

### 【3】は実体と一致する

```
16:34:55.432  block auto-ended
16:34:55.478  packaged 1 / awaiting_approval 1     ← 46 ms
16:35:01      .ok  (承認)
16:35:06      .sent (送信成功)   ← ★ レシートの「16:35」と一致
```

★ 2 本目のレシートは **1 本目の `16:28` ではなく `16:35`** を指した。
断定文も `unsent === 0 && last_error === null` の分岐 (「送信は完了しています」) で出ている。

### ★ 【5】は **新しく足した `counted` 条件**の確認でもある

`counted: false` に倒れると、⚠️ **fail-open を直したつもりが fail-closed** になり、
安全装置のカードが二度と出なくなる。→ 未送信 0 件・起動直後の状態で **出ることを実機で確認**した。

---

## ⚠️ 確認できなかったもの (★ 隠さず書く)

### 【2】送信中カード / 【7】梱包中の表示 — **窓が小さすぎて撮れない**

この機械では `block auto-ended` → `packaged` が **46〜64 ms** で終わる。
画面のポーリングは 3 秒間隔なので、★ **そもそも画面が送信中状態を観測しない**。
→ 「出なかった」のではなく **「出る時間が無かった」**。⚠️ 遅い端末・複数件まとめ送信では出る。

### 【6】前の回のレシートが残らないこと — **構造的には保証されているが、実機では再現できていない**

⚠️★ 旧実装でこの窓が開くのも同じ 46 ms + ポーリング間隔なので、
**v0.1.25 でも写る確率は低い**。したがって「写らなかった」ことは修正の証拠にならない。

★ 効いている根拠は次の 2 つであって、写真ではない:
- ブロック終了時に `reset_sent_receipt()` を呼ぶ (= `last_sent_ms` が構造的に null になる)
- 番兵を `emit("g1-block-ended")` の **前**で立てる (= スタート画面が出た瞬間から `sending: true`)

⚠️ **「実機で旧バグを再現して消えるところまで見た」とは書かない。**

---

## 後片づけの対象 (★ 増えた)

```
Drive (未処理):
  P999_block03_gse_20260810_071400.age   60,183 B  id 1xLOn2OA6H28BI0xn_8a9mmzgN3_tL_cY
  P999_block04_gse_20260810_072954.age   59,924 B  id 1nRAIhhm0nLYiBC9qLcwTqDae_hYYYl0Q
Drive (処理済み):
  (macos_test)P999_block01 / block02
ローカル (この Mac): ~/Documents/GSE-submissions/ の P999_block01..04 と manifest.jsonl の 4 行
手元: ~/Desktop/G1_確認用_v0126/  (★ 入力監視の権限がこのパスに紐づいている)
```

★ `P999` は存在しない番号なので実データを汚さない。⚠️ Drive に残ると素性が分からなくなるので、
`(macos_test)` を前置するか削除すること (Drive MCP はリネーム/削除ができない → 人が UI から)。
