# 要件 — macOS フック権限 / 空ブロック提出 / 残レビュー

## 背景

`.steering/20260810-macos-visual-check-and-distribution/` の macOS 実機確認で、
**確認そのものの副産物として 2 つの欠陥が実測で出た**。加えて、提出レシート UI に
`code-reviewer` / `security-checker` / `/cross-review` が 2 セッション連続で未実施のままである。

## ゴール

| | 内容 |
|---|---|
| 【1】 | ブロックを一度も開始していないセッションを提出しない |
| 【2】 | macOS でフック生存検知を動かす (`liveness.rs:141` が `None` を返す) |
| 【3】 | レシート UI に code-reviewer / security-checker / cross-review を通す |
| 【4】 | Input Monitoring が拒否されているとき、**必ず要求する** (いまは黙って諦める経路がある) |

## 受け入れ条件

### 【1】空ブロックの提出

- [ ] `meta` + `ime_state` だけの NDJSON が `.age` に包まれない
- [ ] ★ ブロックを実際に回したセッションは従来どおり包まれる (回帰なし)
- [ ] `packaging.rs` に「`ime_state` だけのセッションを包まない」テストがある
- [ ] ⚠️ HMM に触れないので `HMM_VERSION` bump とゴールデン再生成は不要 (要確認)

### 【4】Input Monitoring の要求

- [ ] `!im_granted && ax_trusted` でも `CGRequestListenEventAccess()` を呼ぶ
      (= システム設定が開き、被験者に何をすべきか伝わる)
- [ ] ★ 成功時のログが **実際に効いている権限**を出す (latch した推測ではなく)
- [ ] `using_accessibility_fallback` 診断値が実態と一致する
- [ ] ★ 再現手順で赤 → 緑を実機で確認する

## ⚠️ 実測にもとづく事実 (推測でない)

2026-08-10 の `~/Documents/GSE-sessions/gse-app.log` より:

```
04:09:39  Input Monitoring permission not granted. Opening System Settings...   ← 出た
04:09:45  Accessibility permission not granted. Native prompt dialog shown.     ← ここで AX が付いた
04:10:51  Input Monitoring denied but Accessibility granted. … skipping ListenOnly.  ← ★ 以後、
04:12:34  Input Monitoring denied but Accessibility granted. … skipping ListenOnly.  ★ 二度と要求しない
04:13:04  CGEventTap installed via Accessibility                                 ← ⚠️ 嘘 (IM 付与の直後)
04:13:18  CGEventTap installed via Input Monitoring
```

→ ★ **アプリ自身の Accessibility フォールバックが、以後の起動で
Input Monitoring を要求しなくさせている。** 被験者から見ると
「何も出ないまま打鍵が記録されないアプリ」になる。
★ 実際にこのセッションでは、研究者 (私) が手でシステム設定を開いて回復させた。

## 制約

- ⚠️ v0.1.25 は**すでに配布済み**。直したものを配るには再ビルド → 再検証 → 再配布が要る
- ⚠️ `analysis/` に OS API を持ち込まない。macOS 依存は `input/` に閉じる
