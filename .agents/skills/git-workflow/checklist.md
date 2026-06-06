# git-workflow: マージ前チェックリスト

## ビルド確認

- [ ] `cargo build` が成功する
- [ ] `cargo clippy -- -D warnings` が通る（警告ゼロ）
- [ ] `npm run build` が成功する（Vite ビルド）

## コード品質

- [ ] フックコールバック内にブロッキング処理がない
- [ ] `unsafe` ブロックに安全性コメントがある
- [ ] `windows` crate のみ使用（`winapi` 不使用）
- [ ] `println!` / `eprintln!` がない（`tracing` を使う）
- [ ] TypeScript に `any` 型がない

## コミットメッセージ

- [ ] `[type]([scope]): [説明]` フォーマットになっている
- [ ] 重要機能変更には `(vX.XX)` が付いている
- [ ] .steering/ 記録があれば `Refs:` を記載した

## .steering/ 記録

- [ ] `requirement.md` が書かれている
- [ ] `design.md` が書かれている
- [ ] `tasklist.md` のすべてのタスクが完了している
- [ ] 重要な設計判断は `decisions.md` に残した

## セキュリティ

- [ ] VK コードのみ記録（Unicode テキスト内容を記録していない）
- [ ] 新しい外部 HTTP 通信を追加していないか（追加する場合はセキュリティ Skill を確認）
