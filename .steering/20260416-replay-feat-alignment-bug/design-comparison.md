# 設計案比較

## v1 の要旨

調査フレームワークとしての計画書。「コード読解 → 実データ計測 → 仮説検証 → 修正判断」の 4 Phase 構成。修正案は「Cheap/Hard」二層で A-D の 4 オプションを decisions.md で提示、A (logged feat 使用) を採択するまでがスコープ。fix 実装方針は「collect_logged_feats を追加」の一文に凝縮。バックフィルは言及のみ。

## v2 の要旨

**問題を「clock semantic mismatch」として再定義**。user_label と logged feat は同じ wall-clock 軸、regen feat は virtual clock 軸。metrics が regen feat を使う構造自体が semantic bug と位置づけ、「logged feat を唯一の真値」と設計原則に昇格。テストは**unit / integration / 実データ回帰の 3 層**、バックフィル計画 (Mac/Windows の既存 metrics JSON 再生成 + baseline_metrics.md の before/after 併記) を**設計の主要セクションに格上げ**。

## 主要な差異

| 観点 | v1 | v2 |
|---|---|---|
| アプローチ | 調査手順書。bug 原因を IME pause auto-reset の再現差と説明 | 設計原則として「clock semantic の分離」を core rationale に据え、IME pause は一例として扱う |
| 技術選定 | `collect_logged_feats` 新規追加 (v2 と同じ) | 同じ。ただし LoggedFeatDto を `#[serde(rename = "t")]` で明示的に型定義 |
| 変更規模 | replay.rs + metrics.rs tests | replay.rs + 新規 integration test file + 新規実データ fixture + baseline_metrics.md + dataset repo metrics JSON |
| テスト戦略 | 1 層 (統合テスト 1 件) | 3 層 (unit / integration / 実データ回帰)、実データ fixture をコミットして CI で捕捉 |
| バックフィル | decisions.md D3 で言及のみ | design.md の主要セクション。Mac/Windows 両方の metrics JSON 再生成、before/after の履歴保全、ロールバック計画を明記 |
| リスク管理 | 「git revert で戻せる」 | fixture の機密性・fix 後の数値悪化・dataset 履歴損失をそれぞれ緩和策とセットで記載 |
| Phase 2a 判定への橋渡し | 「数値で再評価」とだけ | fix 後 Mac n=2 + Windows n=1 での再計算と retrospective 閾値 (Stuck precision ≥ 0.6) 達成検証を受け入れ条件に |
| コメント修正 | 触れない | `bin/replay.rs:79-81` の「feat 読み飛ばし専用」設計意図を fix 後の実態に合わせて更新 |

## 推奨案

**v2 を推奨**。

理由:
1. **本件の再発防止力が段違い**: 層3 (実データ回帰) fixture を tests に組み込むことで、将来 metrics パスを再度 regen に戻す変更が入った際に CI で必ず落ちる。v1 は 1 層統合テストのみで、エッジケースを逃す
2. **バックフィルを設計の一級要素に格上げ**している点は Phase 2a 判定のゴール (requirement.md #4) と直結する。v1 はここが decisions.md の副次項目で、実装完了と「Go/No-Go 判定可能」の間にギャップがある
3. **clock semantic mismatch としての再定義**は、IME pause 以外の同種の将来バグ (例: macOS の異なる IME 経路、engine.set_paused の他の呼び出し経路) にも同じ原則で対処可能。v1 の IME-auto-reset 説明は現象ベースで再現範囲が狭い
4. コスト差: v2 は fixture 準備と baseline_metrics 更新で +30-60 分増だが、これは Phase 2a 判定までに**どのみち必要な作業**

ハイブリッド案は妥当性薄い (v1 の骨子は v2 に包含される)。v2 丸ごと採用が合理的。
