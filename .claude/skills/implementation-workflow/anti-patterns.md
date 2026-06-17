# Implementation Workflow — アンチパターン集

実装タスクでよくある「骨格を省略・ショートカット」した失敗のカタログ。

---

## AP-1: 設計承認を取らずに実装に入る

**何が起きたか**:
Step C をスキップして「明らかなことだから」と判断し実装を開始。
コードを半分書いたところでアーキテクチャの方向性が違うことが判明し、全書き直し。

**なぜ起きるか**:
- requirement.md を「読んだ気になる」（実際には流し読み）
- 「design.md を書くのは時間の無駄」という誘惑

**防ぐには**:
`design.md` の「変更対象ファイル」欄を埋めた時点でユーザーに見せる。
承認の返事が来るまで Step D に進まない（待つ）。

---

## AP-2: `git add .` でコミットする

**何が起きたか**:
`git add .` でステージしたところ、`tests/fixtures/` に置いていたデバッグ用 NDJSON
（実セッションデータ）が一緒にコミットされ、プライベートデータが公開リポジトリに流出しそうになった。

**なぜ起きるか**:
- 変更ファイル数が多くなると個別指定が面倒
- `data-privacy` Skill と `git-workflow` Skill を別々に見ていないと見落とす

**防ぐには**:
`git status` で変更ファイルを確認してから `git add [具体的なパス]` で個別追加。
`tests/fixtures/` / `tests/sessions/` は `.gitignore` 対象かを必ず確認。

---

## AP-3: `cargo test` を省略して「動いているから大丈夫」と判断する

**何が起きたか**:
手動実行で確認済みのつもりで `cargo test` をスキップ。
後続の PR で別 contributor が `gse-replay --snapshot` を実行したところ、
`FeatSnapshot` の byte-equal が崩れており、HMM 挙動の回帰が判明。

**なぜ起きるか**:
- Step F を「やっているつもり」になる（実行した ≠ パスした）
- リプレイテストを単体テストと別物と思っていない

**防ぐには**:
Step F は順番通りに: 単体テスト → gse-replay → schema check（該当時）。
`test-runner` サブエージェントに実行させて「PASS/FAIL を明示」させる。

---

## AP-4: code-reviewer のみ起動し security-checker を省略する

**何が起きたか**:
`logger.rs` を変更した際に code-reviewer だけ起動。
security-checker を省略したため、新しいログフィールドに実セッションパスが混入していたことを見落とした。
（`data-privacy` Skill 参照: キーストローク内容は外部送信禁止）

**なぜ起きるか**:
「セキュリティ的な変更ではないから security-checker は不要」という誤判断。
`logger.rs` は常に security-checker の必須対象なのに見落とす。

**防ぐには**:
Step G で「code-reviewer と security-checker を**並列で**」と書いてある。
`logger.rs` / `hook.rs` / `wall_server.rs` の変更時は security-checker の起動を義務化。

---

## AP-5: file-finder + impact-analyzer のどちらか一方しか使わない

**何が起きたか**:
`analysis/engine.rs` を修正する際に file-finder で類似実装を見つけたが、
impact-analyzer を省略した。結果として `lib.rs` の `start_analysis_loop()` が
呼び出し元であることに気づかず、引数シグネチャを変更してビルドが壊れた。

**なぜ起きるか**:
「このファイルを変えるだけ」と思い込むと影響範囲調査を省略する。

**防ぐには**:
Step B は「並列で両方を起動する」と明記。どちらか一方は不完全。
特に `analysis/` の変更は `lib.rs` → Tauri コマンド への依存がある（architecture-rules 参照）。

---

## AP-6: implementation-workflow Skill を「知っている」ので参照をスキップする

**何が起きたか**:
「前回と同じ手順だから覚えている」という理由で SKILL.md を Read しなかった。
前回と違い今回は `/fix-bug`（TDD 順序必須）だったが、Step E の前にテストを書かずに
実装を先に書いてしまい、後から追加したテストが実装にフィットしすぎて意味のないものになった。

**なぜ起きるか**:
- CLAUDE.md 行動規範「3. Skill 参照: 実装前に必ず参照する」を省略したくなる誘惑
- 「どうせ同じ内容だから」という錯覚（コマンドごとのオーバーライドを忘れる）

**防ぐには**:
毎回 SKILL.md を Read する。コマンドによるオーバーライド表（`/fix-bug` の TDD 挿入等）を確認する。

---

## AP-7: コンテキスト超過を無視して実装を続ける

**何が起きたか**:
`/context` が 70% を超えた状態で実装を続けた結果、後半のコードに
前半の設計判断が正確に反映されず、設計と実装に乖離が生じた。

**なぜ起きるか**:
「中断すると流れが切れる」という心理的抵抗。

**防ぐには**:
Step E の規約: `/context` が 50% を超えたら `/smart-compact`。
50% は余裕を持った閾値（GSE は 1M context モデル）。
50% 超えても数 MB の設計文書・コードを正確に保持できないリスクがある。
