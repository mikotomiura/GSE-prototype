## 設計案比較（/reimagine 1 回目）

### v1 の要旨
途中の答えを backend の `ProbeCard.partial` が持ち、Q1・Q2 まで済むか、カードがどの経路で閉じたときに、今と同じ 2 行（`realtime_label`・`activity_label`）を書く。`realtime_label` の q1・q2 は答えた分だけ入り、残りは null。ショートカットは backend が、カードの開閉の全経路が通る `run_s1_effects` で view から差分を取って登録・解除し、既存の共通ハンドラに数字の分岐を足す。

### v2 の要旨
押すたびに 1 行を書いて終わる。Q3 で今の 2 行（段 1 の `realtime_label` は q が常に null）、Q1・Q2 は新しい行種 `s1_scale_label` を 1 押しに 1 行。driver は「答えた」の印だけを持ち、印のあるカードが閉じても skipped を書かない。ショートカットは frontend のカードの部品が JS の API で登録・解除し、callback はクリックと同じ関数を呼ぶ。

### 主要な差異

| 観点 | v1 | v2 |
|---|---|---|
| 途中の答え | backend が持ち、閉じるときに書く | 持たない。押すたびに書く |
| 記録の形 | 行種は増やさない。`realtime_label` の q を answered でも null 可に | 行種 `s1_scale_label` を足す。段 1 の `realtime_label` の q は常に null |
| Q1・Q2 の読み方 | 今どおり `realtime_label` の q1・q2 | `probe_id` で 2 行を突き合わせる |
| キーの登録 | backend（`run_s1_effects`・ロックの外で） | frontend の部品の mount/unmount（JS の API） |
| 依存 | 増えない | npm に `@tauri-apps/plugin-global-shortcut` |
| 変更が及ぶ文書・schema | schema の doc・gse-dataset の写し（形は同じ） | 新しい行種の schema・capabilities・削除保証の行種の一覧・同意文書の「記録するもの」の表・gse-dataset |
| 閉じる経路の扱い | 全経路で partial を書く（経路ごとのテストが要る） | 全経路で「印があれば skipped を書かない」（同じく経路ごとのテスト） |
| 途中でアプリが落ちたとき | 押した分が失われる | 押した分は残る |
| リスク | 閉じる経路の書き漏れ。ロックとメインスレッドの取り合い | 行種の追加の波及。webview が登録の権限を実際に使い始める。解析の突き合わせ |

### 推奨案

ハイブリッド（v1 を土台に、v2 から 1 点を取る） —— 理由:

- 記録は v1。Q1・Q2 は事前登録の草案（S1-A3 の詰まりの定義の候補）と replay・calibration_eval がすでに `realtime_label` の q で読む。行種を足すと同意文書の表・削除保証・capabilities・gse-dataset に波及し、得るもの（落ちたときに押した分が残る）はカードが出ている数十秒のあいだの落ちに限られる。
- キーは v1（backend が持つ）。カードの真実は backend にあり、閉じる経路も backend が決めるので、登録の真実も同じ側に置く方が食い違わない。npm の依存も増えない。
- v2 から取る 1 点: overlay の webview に与えている `global-shortcut:allow-register` / `allow-unregister`（`capabilities/default.json`）は、frontend から 1 度も使われていない（`src/` に用例が無い）。登録を backend に置くなら、この権限を外して、webview が任意の組を登録できる面を閉じる。backend の `app.global_shortcut()` は capabilities の対象外なので、外しても backend の登録は動く（実装で確かめる）。
