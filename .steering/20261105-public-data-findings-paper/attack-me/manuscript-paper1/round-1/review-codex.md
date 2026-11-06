# review-codex（manuscript round 1・run-codex-consult.sh・rc=0・既知の未決 16 件を添えた）

評価（5＝良好。提示原稿と規程抜粋に基づく）

| 項目 | 点 | 所見 |
|---|---:|---|
| a 主張と根拠 | 3 | 統計量の限定は明確だが、トリガーへの結論が広い。 |
| b 方法 | 2 | マッチング単位と観測端の処理に確認が必要。 |
| c 持ち帰れるもの | 3 | 評価手順は有用。ただし再利用に必要な仕様が残る。 |
| d 簡潔さ・構成 | 3 | 状態ラベルは明快。同等性・留保の反復は圧縮可能。 |
| e 規程適合 | 4 | 提示情報では要旨長・付録位置・申告位置は適合。 |
| f 先行研究 | 3 | 比較軸は豊富だが、探索手順は追試できない。 |

以下は既知の未決とは別の指摘です。

1. **[major] マッチングの説明と定義が一致しない**  
   **位置・引用：** `sections/limitations.tex`：“Matching was on writer, block, stratum and newline”; `sections/design.tex`：“collected across the writer's assignments”。  
   **問題：** S2のセルにもblockがなく、選んだ対照と全stallの直積を取る。block内マッチングを実施したとは読めず、ペア数の重みも抽出時の対応とは異なる。  
   **解消条件：** 実装上の候補集合・抽出単位・集計単位を一致させて記述。代替として、抽出した対応ペアだけの統計量と比較し、精度と対象集団の重みの交換条件を示す。  
   **自信：高。**

2. **[major] 観測端によるラベル選択が未規定**  
   **位置・引用：** `appendix/supplement.tex`：“trims rows without input before gaps of 60~s or more”。  
   **問題：** 次の文字入力がない課題末尾、30分境界、削除された空白区間で、pauseの終了・onset・θの蓄積をどう扱うか不明。長い停滞ほど除外される可能性があり、対象は単なる「30秒以上」と一致しない。  
   **解消条件：** 境界例の時系列と除外件数を提示。30秒の観測で確定できる事例と右打切りを区別し、除外依存性を点検する。  
   **自信：中〜高。**

3. **[major] 単一時点の順位評価からトリガー全般へ拡張**  
   **位置・引用：** `sections/conclusion.tex`：“These signals gave no basis for a seconds-scale trigger before stalls in character production.”  
   **問題：** 検定対象はuでの差分。事前の一過性ピーク、連続超過、pause開始後の更新は別の規則である。S8の一様シフトによる換算も、同じAUCを持つ別の分布の閾値性能を保証しない。  
   **解消条件：** 結論を検定したスコアに限定。追加案は時間依存の評価と固定アラーム予算下の感度・先行時間。換算値にはシフト機構への依存を明示する。  
   **自信：高。**

4. **[major] 学習器の再標本化仕様が不足**  
   **位置・引用：** `appendix/supplement.tex`：“the interval resamples writers and refits (200 resamples; no failures)”。  
   **問題：** 復元抽出で同じwriterの複製が異なるfoldに入れば漏洩する。防止策とfold再構成が不明で、200回の端点を四桁表示して0.55との交差を論じる安定性も未提示。  
   **解消条件：** 元writer IDによる分割維持を明記し、端点のMonte Carlo安定性を示す。  
   **自信：高〔仕様不足〕、中〔実害〕。**

5. **[minor] 新規性探索の監査可能性**  
   **位置・引用：** `appendix/supplement.tex`：“claims were checked by three independent votes”。  
   **問題：** 投票主体・独立性・検索式が不明。  
   **解消条件：** 索引名、検索日、検索式、選定基準、判定主体を記載する。  
   **自信：高。**

総合推奨：**major**。  
主要統計量の対象と観測端の仕様を確定する必要がある。  
トリガーへの結論を限定し、再標本化の追試可能性を整えれば、評価可能な負の結果として明確になる。
