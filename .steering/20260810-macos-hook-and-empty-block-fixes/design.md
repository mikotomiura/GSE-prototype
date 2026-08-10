# 設計

## 【4】Input Monitoring を必ず要求する (`input/hook_macos.rs`)

### いまの形 (壊れている)

```rust
let mut use_accessibility = if !im_granted && ax_trusted {
    …  true            // ★ ここが CGRequestListenEventAccess() を**飛ばす**
} else {
    if !im_granted { CGRequestListenEventAccess(); }   // ← 要求はこちらにしか無い
    false
};
```

⚠️ ★ 「要求するか」と「どちらの tap を先に試すか」が **同じ分岐に同居している**のが原因。
Accessibility を先に試したいだけなのに、要求まで一緒に落ちている。

### 直す形

**2 つの判断を分ける。**

```rust
if !im_granted { CGRequestListenEventAccess(); }       // ① 要求は無条件 (Accessibility の有無と独立)
let mut use_accessibility = !im_granted && ax_trusted;  // ② 先に試す順序だけを決める
```

★ 振る舞いの差は「AX が付いている端末でもシステム設定が開く」だけ。
tap の作成順序・フォールバック・リトライ間隔は**一切変えない**。

### 成功時のログを実態に合わせる

`mode_label` は **試した tap の種類**であって、効いている権限ではない。
`use_accessibility` は一度 true になると、Input Monitoring が後から付与されて成功しても
true のままなので、⚠️ **成功ログが嘘になる** (2026-08-10 の 04:13:04 で実測)。

→ 成功した時点で `CGPreflightListenEventAccess()` / `AXIsProcessTrusted()` を読み直し、
**実際に付いている権限を出す**。`USING_ACCESSIBILITY_FALLBACK` も実態に合わせる
(この値は `lib.rs:740` で `using_accessibility_fallback` として研究者の診断に出る)。

⚠️ ログ文字列 `CGEventTap installed` を読む消費者はコード外に無いことを grep で確認済み。

## 【1】空ブロックを提出しない (`packaging.rs`)

### 原因

`has_any_data_row` が除外するのは `hook_health` だけで、
**IME モニタが起動直後に吐く `ime_state` がデータ行に数えられる**。
→ アプリを起動して閉じただけの 80 秒が「提出する価値があるセッション」になる。

### 案 A (最小): `ime_state` も除外する

`hook_health` と同じ扱いにする。★ 1 行で済む。
⚠️ ただし「診断行を足すたびにここを直す」構造が残る。

### 案 B (本質): ブロック開始の証拠を条件にする

`reconcile::is_closed_g1_session` の条件 4 (`g1_mode` がある) は **アプリ起動の証拠**でしかない。
`session_meta` 行 (= `開始する` が押されたときにだけ書かれる) の有無を条件に足す。

### ★ 採用: A + B の両方

- B が本命 (「ブロックが始まった」を直接見る)
- ⚠️ A も入れる。★ `has_any_data_row` は `find_latest_session_ndjson` からも呼ばれており
  (`packaging.rs:232`)、そちらは G1 とは別経路である。**片方だけ直すと穴が残る**
- ★ 除外リストの意図をコメントに固定する (「被験者の作業を表さない行」)

## 【2】macOS のフック生存検知 (`input/liveness.rs`)

`CGEventSourceSecondsSinceLastEventType` で「OS が最後にキーイベントを見た時刻」を取り、
`CALLBACK_COUNT` が動いていないのに OS 側は打鍵を見ている状態 = フックの silent death を検知する。
⚠️ Windows 実装と**判定規則を揃える** (`fix/hook-health-fail-rule` の AND 規則)。

## テスト戦略

| | 何で確かめるか |
|---|---|
| 【1】 | `packaging.rs` / `reconcile.rs` の単体テスト (`ime_state` だけのセッション / 実ブロック) |
| 【1】 | ★ 実際に作られた 261 B の NDJSON (`gse_20260810_041051.ndjson` と同じ形) を fixture にする |
| 【4】 | ★ **実機で再現 → 修正 → 再実機**。アプリを新しいパスに置くと IM だけ denied に戻るので再現できる |
| 【2】 | 実機で hook_health の値を見る |
| 共通 | `cargo test --workspace` / `gse-replay --snapshot` の回帰 |

⚠️ ★ 【4】は「ビルドが通った」を根拠にしない。**システム設定が開くところまで実機で見る**。
