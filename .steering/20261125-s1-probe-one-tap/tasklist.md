# tasklist

## 準備
- [x] 引き継ぎ・ADR-055・事前登録の草案・コードを読む
- [x] file-finder ＋ impact-analyzer（並列）
- [x] design.md・/reimagine（判断 6）

## 記録（backend）
- [x] logger: `ActivityCategory::asks_scales()`、段 1 用の書き手 `realtime_label_s1_answered(q1: Option, q2: Option)`、debug_assert の緩和、往復のテスト
- [x] s1_driver: `ProbeCard.partial`・段（step）の決定・`S1CardView::Probe` に step と keys、答えの適用（食い違う step を拒む）、閉じる全経路で partial があれば answered の行（取り消しは書かない）、単体テスト
- [x] lib.rs: `answer_s1_probe` コマンド（invoke_handler 登録）、skip のコマンドの partial の扱い、`record_probe_response` の扱い、生成コードの門のテスト（8408 行）
- [x] replay.rs・calibration_eval.rs: q の無い answered を破損と扱わず別に数え、回答数は q のそろった answered に限る。テスト
- [x] schema_dto.rs の doc → `emit_schema` で current.json を作り直す・gse-dataset の写しの照合

## キー（backend）
- [x] view から「あるべきキーの組」を決める純関数と差分の計算（単体テスト: 全経路で空になる）
- [x] `run_s1_effects` で差分を登録・解除（ロックの外・メインスレッド）、失敗で keys: None
- [x] 共通ハンドラに 修飾キー＋Digit0〜7 の分岐 → `answer_s1_probe` と同じ処理
- [x] `capabilities/default.json` の register/unregister を外す（backend の登録が動くことを確かめる）

## 画面
- [x] `probeTypes.ts` の型（step・keys）
- [x] `S1ProbeCard.tsx`: 段ごとの大きなボタン・キーの表示・「回答する」を無くす・閉じる（⌥0）
- [x] `S1ConsentPanel.tsx`: 優先の規則とキーの説明

## 文書
- [x] ADR-057（ADR-031 D3・ADR-055 の答え方と Q1・Q2 を聞く条件・キーの登録と O1 の理由・限界）と README
- [x] 事前登録の草案（S1-A3・S1-A4・S1-B3・前進）
- [x] 同意文書（承認待ちの版）§3 とフォームのビルダー・テスト
- [x] data-privacy ルール 7・glossary・functional-design

## 検証
- [x] cargo test --workspace・clippy・tsc・npm run build
- [x] gse-replay --snapshot（minimal）回帰
- [x] macOS 実機: カードを出してキーで答える・記号が入らない・フォーカスが動かない・tap が答えのキーを見るか・画面を目で見る
- [x] code-reviewer ＋ security-checker（並列）・指摘対応（判断 8・9）
- [x] /finish-task（/cross-review 必須・判断 10）・コミット・push・PR（研究者の確認済み。CI の枠が無いので [skip ci] で merge・研究者の提案）
