# 実機 smoke runbook — idle オーバーレイ退避

> **【優先度】観測 OS は Windows (プライマリターゲット・被験者環境)。Windows 実機 smoke を最優先で
> 実施する (decisions.md D8)。macOS は副次確認。** 同じチェック項目を両 OS で行うが、本バグの
> 受け入れ判定は **Windows 11 機**で green を必須とする。

- **Windows (最優先)**: 本番相当ビルド (CI バイナリ or `cargo build` Windows) で起動。デバッグ
  プローブを使う場合は `VITE_GSE_DEBUG=1` + `GSE_DEBUG=1` の二重 gate。Windows では透明窓の
  クリック透過が効かない (Tauri #11461) ため、**幾何退避が効いて初めて idle 全域透過になる**点に注意。
- **macOS (副次)**: `~/.cargo/bin/cargo build --target aarch64-apple-darwin`。同 gate。

## 主眼チェック (本タスクの受け入れ条件)
1. **idle 全域クリック透過**: ブラウザ等を前面に置き、GSE を idle にする。画面のどこを
   クリックしても背後アプリが反応する。→ 透明窓が残ってクリックを奪わないこと。
2. **idle 不可視**: idle 時にオーバーレイが視覚的に見えない (透明窓の残像なし)。

## 非回帰チェック (D7-D13 死守)
3. **Probe 表示**: probe 発火 (`debug_force_probe`) → カードが**見えて**カード内クリックで回答でき、
   **カード外は背後アプリへ透過**する (右上 box・非ブロック設計)。
4. **Probe 応答後 → idle**: 回答後、画面全域で背後アプリがクリックできる (主眼1の再確認)。
5. **Wall**: Wall 発動 → **全画面ブロック** (QR/ボタンのみ操作可)。解除 → idle で背後クリック可へ復帰。
6. **タイピングフォーカス**: 前面エディタで打鍵中に probe/idle 遷移してもフォーカスを奪われない
   (D12 resign_key 非回帰)。
7. **macOS 非回帰 (副次)**: macOS 機で probe/Wall/idle が従来どおり (退避は両 OS 共通実装で
   macOS の NSPanel/ignoresMouseEvents 経路を壊さない)。
   ※本タスクの主問題は Windows のため、項目 1-6 は **Windows 機での green が受け入れ必須**。

## 退避→show 復帰の重点チェック (code-reviewer HIGH / D5 検証)
8. **退避後の初回 probe がオンスクリーン**: アプリ起動直後 (idle=画面外退避済み) の状態から
   最初の probe を発火 → カードが**画面右上にオンスクリーン表示**される (画面外に留まらない)。
9. **退避後の初回 Wall が全画面**: idle から直接 Wall を発動 → **全画面ブロック**になる
   (1x1 offscreen のまま残らない)。
10. **idle⇄probe 高速トグル**: probe 発火→即応答→再発火を素早く数回繰り返し、カードが毎回
    オンスクリーンに出る (D7: 退避と show の race が IPC FIFO で正しく解決されることの実機確認)。

## 軽量回帰番兵 (任意・DevTools)
- idle 中に DevTools console で:
  `(await import('@tauri-apps/api/window')).getCurrentWindow().outerPosition()`
  を実行し、x <= -10000 (画面外退避済み) を確認する。
  → これが主因 (幾何退避) を直接検証する番兵 (decisions.md D4)。

## 期待結果
- **Windows 機**で 1/2/4 が green = 本バグ (idle 残存クリック阻害) 解消 (受け入れ必須)。
- 3/5/6 が green = 非ブロック設計・Wall・フォーカス非回帰維持。
- macOS 機で 1-10 が green = macOS 非回帰 (副次)。

注: steering ディレクトリ名 `20260629-macos-overlay-idle-clickthrough` は当初 macOS 想定で命名された
名残。実際の観測 OS は Windows (decisions.md D8)。リネームは Refs/commit/memory 整合のため見送る。
