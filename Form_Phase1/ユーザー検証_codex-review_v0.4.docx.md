**GSE ユーザー検証設計レビュー v0.4**

既存「ユーザー検証\_codex-review」の統合改訂版 / 2026-06-22

# **0\. 改訂方針**

本稿は、既存の「ユーザー検証\_codex-review」に含まれていた v0.3 評価、JITAI 的な介入設計、blind 較正 UI、MRT 的評価、IME 注意点を維持しつつ、GSE のユーザー検証を X 側と Y 側に分けて再設計するものである。

ここでいう X は「MhD/介入推論の有効性」、Y は「GSE というシステム自体の価値、AI 依存低下、自力解決、自己効力感、Physical Anchor/散歩の受容」を指す。なお、MhD 内部の X/Y 軸、すなわち Cognitive Friction / Productive Engagement とは用語上区別する。

既存文書で有効だった部分は残し、誤解を招く部分は削除・置換した。特に「認知状態を読めた」という強い表現、「Ctrl/Cmd+V 回数 \= AI 依存度」という単純化、「diff 量 / 総打鍵数 \= 自力解決率」という単純化、「一般性自己効力感だけで心理的成長を測る」という設計は、下記の形に改める。

# **1\. 最終判断**

現状の v0.3 検証設計は、GSE の「認知状態推定の核」を研磨する第一関門として採用してよい。モデル出力から独立したランダム時点プローブ、申告前 30 秒だけを見る時間隔離、GT ではなく criterion label と呼ぶ方針、C-index、前向き holdout、MNAR 範囲報告は、HCI/ESM/JITAI 研究の方向と合っている \[1\]\[2\]\[4\]。

ただし、v0.3 は「認知状態を確実に読めた」ことを証明する最終手法ではない。より正確には、「本文を保存しない privacy-preserving な行動 proxy が、主観的な摩擦・前進感と個人内でどれだけ順序一致するか」を検証する測定法・モデル破綻検出フェーズである。

また、X 側の推論妥当性と、Y 側のプロダクト価値は混同してはならない。X が成立しても UX が悪ければ GSE は使われない。逆に Y が改善しても、それが MhD 推論の効果ではなく、単なるタイマー、Monk Mode、または参加者の意識変化による可能性が残る。そのため、検証は X1: 推論妥当性、X2: 介入判断妥当性、Y: システム価値の三層に分解する。

# **2\. 既存内容から残すもの・削除するもの・追加するもの**

| 扱い | 対象 | 理由 |
| :---- | :---- | :---- |
| 残す | ランダムプローブ、申告前 30 秒の時間隔離、blind/minimal dashboard、C-index、前向き holdout、MNAR 範囲報告。 | ESM/EMA と JITAI の検証文法に近く、少人数スモークでも破綻検出に使えるため \[1\]\[4\]。 |
| 残す | Need と Opportunity の分離、dismiss / recent dismiss / cooldown / daily cap / Monk Mode のログ化。 | 介入は「必要そうか」だけでなく「今受け取れるか」に依存するため \[2\]。 |
| 削除・置換 | 「認知状態を読めた」「Ground Truth を得た」という表現。 | 主観申告も機能ラベルも criterion label であり、脳内状態そのものではないため。 |
| 削除・置換 | Ctrl/Cmd+V 回数のみで AI 依存度を評価する設計。 | 貼り付けには AI 出力以外の引用、URL、メモ移動が混入するため。 |
| 削除・置換 | diff 量 / 総打鍵数のみで自力解決率を評価する設計。 | Backspace や写経で総打鍵数が膨らむため、自力生成と成果物品質を分ける必要がある。 |
| 追加 | AB/BA クロスオーバー、介入候補時点の micro-randomized trial 的評価、長期継続指標。 | 介入タイミングと cutoff は予測問題ではなく因果・処方問題であるため \[3\]\[4\]。 |
| 追加 | Google Form / Dropbox 利用時のデータ分離、疑似匿名化、暗号化、本文・クリップボード本文・ウィンドウタイトル非保存。 | キーストロークログは本文なしでも個人識別性を持ちうるため \[7\]\[16\]\[17\]。 |

# **3\. X 側: MhD 推論と介入判断の検証**

## **3.1 X1: 推論妥当性**

X1 は、MhD が出す Cognitive Friction / Productive Engagement、または stuck\_likelihood / friction\_score / engagement\_score が、ユーザーの主観的な Q1 摩擦・Q2 前進とどれだけ対応するかを検証する層である。ここでは「Flow / Incubation / Stuck を当てる」よりも、連続スコアの順序一致を見る。少人数では混同行列よりも、個人内 C-index、Spearman 相関、セッション中央値の安定性を見る方が妥当である。

較正中は、Current State や Flow/Incubation/Stuck % を被験者に見せてはいけない。モデルの推定を表示すると、被験者の申告がシステム推定に引きずられ、criterion label が汚染される。Dashboard は session time、hook 状態、Monk Mode、終了ボタン程度に絞る。

X1 の成功表現は、「認知状態を読めた」ではなく、「privacy-preserving な行動 proxy が、主観的摩擦・主観的前進と個人内で順序一致した」とする。

## **3.2 X2: 介入判断妥当性**

X2 は、MhD の推論結果に基づく nudge / wall / zen / defer / none の判断が、実際にユーザーの復帰や自力試行に効くかを検証する層である。X1 と X2 を混ぜると、「推論は合っているが介入が邪魔」「推論は粗いがタイマー的介入が効く」というケースを分離できなくなる。

介入候補時点では、すべて介入するのではなく、一定割合で nudge と defer をランダム化する。例えば、介入候補が発生した瞬間に 70% は nudge、30% は defer とし、介入後 2 分 / 5 分の手動入力復帰、paste 回避、dismiss、helpfulness を比較する。これは JITAI の構成要素がどの状況で効くかを見る micro-randomized trial 的な設計である \[4\]。

強い Wall は、初期検証では原則 opt-in または Monk Mode 内に限定する。Stuck 誤検知が実際の Stuck を誘発するリスクがあるため、false positive の UX コストを通常の分類誤差より重く扱う。

# **4\. Y 側: システム価値の指標設計**

## **4.1 AI 依存度**

Ctrl/Cmd+V 回数はログとして残すが、主指標にはしない。AI 依存度は「貼り付け回数」ではなく、「詰まった直後に外部生成物へ逃げたか」「最終成果物に占める外部貼り付け量がどれだけか」「貼り付けなしに自力復帰できたか」で測る。

| 指標 | 定義 | 扱い |
| :---- | :---- | :---- |
| paste\_count\_per\_hour | 1 時間あたりの貼り付け回数。 | 補助 |
| external\_paste\_count | GSE Editor 外からの貼り付け回数。 | 主要 |
| paste\_chars\_per\_1000\_final\_chars | 最終成果物 1000 字あたりの外部貼り付け文字量。 | 主要 |
| large\_paste\_rate | 50 字以上または 100 字以上の貼り付け割合。 | 主要 |
| paste\_after\_stuck\_rate | Stuck 候補後 5 分以内に外部貼り付けが起きた割合。 | 最重要 |
| self\_recovery\_without\_paste | Stuck 候補後 5 分以内に、外部貼り付けなしで手動入力に復帰した割合。 | 最重要 |

Mehta et al. の keystroke-based LLM 支援検出は、テキスト内容ではなく「どう書いたか」を利用する点で GSE と整合する。ただし、同研究は構造化された実験環境での結果であり、日本語 IME・自由執筆・GSE 介入環境に直接一般化しない。そのため、Mehta 系メトリクスは主指標ではなく、AI 支援混入の補助指標として扱う \[6\]。

## **4.2 自力解決率**

diff 量と総打鍵数の比率だけでは、自力解決を測れない。総打鍵数は Backspace、削除、迷い、写経で増えるため、「自分で考えて前進したか」を直接表すとは限らない。主指標は manual\_contribution\_ratio と productive\_manual\_recovery\_rate に置き換える。

manual\_contribution\_ratio \= manual\_insert\_chars / (manual\_insert\_chars \+ external\_paste\_chars)

productive\_manual\_recovery\_rate \= Stuck 候補後 5 分以内に、external paste なしで、net\_diff が正方向に進んだ割合

ただし、自力率だけを上げると、AI を使わずに低品質な成果物を作っただけという解釈が残る。そのため、成果物品質を第三者ブラインド評価で測る。評価者には条件 A/B、GSE 使用有無、AI 使用量を見せず、論理性、独自性、完成度、読みやすさを 5 段階で評価してもらう。

## **4.3 自己効力感**

一般性自己効力感尺度は副指標として残す。ただし、短期の GSE 介入で変化を見るには広すぎる可能性が高い。主観主指標には、GSE 用の task-specific self-efficacy を追加する。一般性自己効力感は人生全般への対処可能感に近く、短期の執筆・AI 依存介入の検出感度が低くなる可能性がある \[10\]。

追加項目例: 「AI に頼らず、自分の言葉で論点を前に進められると思う」「詰まったとき、すぐ AI に聞かずに別角度から考え直せると思う」「書いては消す状態になっても、自分で原因を切り分けられると思う」「GSE の介入は、自分で考える感覚を取り戻す助けになった」。

## **4.4 UX・継続利用・介入害**

Y 側では、AI 依存低下だけでなく、UX の悪化を同時に見る。AI 依存が下がっても、ストレス、作業中断、離脱、緊急解除が増えるなら、GSE はプロダクトとして失敗である。

| 指標 | 意味 |
| :---- | :---- |
| dismiss\_rate | 介入表示後に閉じられた割合。Need 誤りと Opportunity 誤りを分ける。 |
| early\_unlock\_rate | Wall / Physical Anchor の早期解除率。強介入の害の proxy。 |
| interventions\_per\_hour | 1 時間あたり介入数。通知疲れの proxy。 |
| helpfulness / annoyance | 介入直後またはセッション後の主観評価。 |
| NASA-TLX short | 精神的要求、努力、フラストレーションを簡易測定する \[11\]。 |
| next-week willingness | 翌週も使いたいか。継続価値の最小指標。 |

## **4.5 Physical Anchor / 散歩の受容**

Physical Anchor は、効果と受容を分けて検証する。歩行や自然環境には創造性・注意回復・反芻低下に関する理論的根拠があるが、GSE からの半強制的な離席や散歩が受け入れられるかは別問題である \[8\]\[9\]\[12\]。

| 層 | 指標・運用 |
| :---- | :---- |
| 受容 | opt-in 率、拒否理由、緊急解除率、夜間・天候・体調による opt-out。 |
| 実行 | Indoor 離席完了率、Outdoor 歩行完了率、戻るまでの時間。 |
| 効果 | 復帰後 5 分 / 10 分の manual\_input、stuck 再発率、主観的リセット感。 |
| 安全 | 22:00〜6:00 は Outdoor 条件を無効化し、Indoor 条件に縮退する。未成年参加者を含む場合は保護者同意と安全な実施条件を別途設ける。 |

# **5\. 推奨実験設計**

## **5.1 Phase 0: 破綻検出スモーク**

n=3〜5、各 3〜5 セッション。介入はオフ、または Lv1 のみ。目的は、ログが取れるか、IME で壊れないか、ラベル UI の負担が過大でないか、Dropbox 提出・Google Form 回答の導線が機能するかを確認することである。

日本語 IME は検証上の主要リスクである。非アルファベット圏の IME 入力では、従来型 keylogger が画面上の変換・確定を取りこぼしうるため、本文を保存しない範囲で composition active、IME confirmation、candidate retry、確定間隔をログ化する \[5\]。

## **5.2 Phase 1: X1 較正・妥当性検証**

n=5〜10、2 週間。blind/minimal dashboard にし、MhD の状態表示は見せない。ランダムプローブまたはセッション直後の手がかり再生で Q1 摩擦・Q2 前進を取得する。主分析は、被験者内 C-index、Spearman 相関、セッション中央値 C-index とする。

Go 条件は、PreReg-1/2 を通過し、C-index が事前定義された Go または少なくとも Kill でないこととする。Fail の場合は、モデル高度化ではなく、特徴量定義・IMEログ・ラベルUI・対象タスクの見直しを優先する。

## **5.3 Phase 2: Y 価値検証 AB/BA クロスオーバー**

単純な導入前後比較は避ける。タスク慣れ、締切、参加者の意識変化が混入するためである。推奨は、同一参加者内で A: ログのみ / 介入なし、B: GSE 介入あり / Monk Mode 任意を比較する AB/BA クロスオーバーである。半数を A→B、半数を B→A に割り付ける。

| 条件・指標 | 内容 |
| :---- | :---- |
| A 条件 | ログのみ。MhD 推定は記録するが介入しない。 |
| B 条件 | Lv1/Lv2 介入あり。Lv3/Lv4 は Monk Mode opt-in のみ。 |
| 主指標 | paste\_after\_stuck\_rate、self\_recovery\_without\_paste、manual\_contribution\_ratio、blind\_quality\_score。 |
| 副指標 | 一般性自己効力感、task-specific self-efficacy、NASA-TLX short、helpfulness、annoyance、next-week willingness。 |

## **5.4 Phase 3: X2 介入効果 MRT 的評価**

介入候補時点で、一定割合を nudge、一定割合を defer に割り付ける。比較する近接アウトカムは、介入後 2 分 / 5 分の手動入力復帰、external paste 回避、dismiss、helpfulness、frustration とする。これにより、「どの状況で介入が効くか」「どの cutoff で介入すべきか」を観察研究より直接的に検証できる \[3\]\[4\]。

# **6\. Google Form / Dropbox 運用**

Google Form は、同意取得、スクリーニング、事前・事後アンケート、自己効力感尺度、セッション後 UX 評価に使う。ログファイルそのものは Form に直接載せず、participant\_id とアンケート回答だけを扱う。Google Workspace はセキュリティ・プライバシー・管理者制御を重視しているが、研究設計上は「個人情報とログを分離する」ことを前提にする \[15\]。

Dropbox は、ログ提出用の File Request として使う。File Request は Dropbox アカウントがない参加者でも提出できるが、リンクを知っている者が提出可能になるため、リクエストごとに期限・パスワード・提出者 ID 命名規則を設定する \[16\]。

Dropbox 側で保存時・転送時の暗号化は提供されるが、標準設定では研究者が完全に鍵を管理するゼロ知識保管とは異なる。機微性のあるログは、アップロード前にローカルで ZIP 暗号化し、本文・クリップボード本文・ウィンドウタイトルを含めない \[17\]。

データ分離の原則: Google Form の氏名・メール・同意情報と、Dropbox のログファイルは participant\_id でのみ結合する。対応表は別ファイルで保管し、共有フォルダには置かない。公開データセットにする場合は、さらに participant\_id を再発番する。

# **7\. 最小ログスキーマ案**

| 項目 | 説明 |
| :---- | :---- |
| session\_id | セッション単位の UUID。 |
| participant\_id | 同意情報とは別管理する疑似 ID。 |
| condition | A: log-only / B: intervention / MRT: nudge or defer。 |
| task\_kind | argumentative\_writing / report / proposal / creative / exploratory\_vibe\_coding など。 |
| timestamp\_ms | イベント時刻。 |
| event\_type | key / paste / delete / pause / intervention\_candidate / nudge / defer / dismiss / unlock。 |
| manual\_insert\_chars | 手動入力文字数。本文は保存しない。 |
| external\_paste\_chars | 外部貼り付け文字数。本文は保存しない。 |
| source\_role | text\_editor / browser / ai\_chat / document / unknown。ウィンドウタイトルは保存しない。 |
| q1\_friction, q2\_progress | 事後またはランダムプローブによる criterion label。 |
| dismiss\_reason | 詰まってない / 今はもがきたい / 閉じる / 無言。 |

# **8\. Go / No-Go 基準案**

| 判定 | 条件 |
| :---- | :---- |
| X1 Go | blind 条件で、C-index が事前定義基準を満たす。少なくとも Kill 判定ではない。 |
| X1 No-Go | Q1/Q2 との対応が不安定。IME・タスク種別・ラベル UI のどれが原因かを切り分ける。 |
| Y Go | B 条件で paste\_after\_stuck\_rate が下がり、self\_recovery\_without\_paste が上がる。同時に blind\_quality\_score と NASA-TLX が悪化しない。 |
| Y No-Go | AI 依存は下がるが品質・ストレス・継続意欲が悪化する。介入強度を縮退する。 |
| Physical Anchor Go | opt-in 率、完了率、復帰後入力、主観的リセット感が一定以上で、緊急解除・安全上の拒否が少ない。 |
| Physical Anchor No-Go | 早期解除や拒否理由が多い。Outdoor をストレッチ扱いに戻し、Indoor のみで再評価する。 |

# **9\. 実装 TODO**

* 較正中 Dashboard から Current State / Flow / Incubation / Stuck % を消す。  
* Nudge / Wall に dismiss 理由 UI を追加し、「詰まってない」「今はもがきたい」「閉じる」「無言」を分けてログ化する。  
* paste ログを count だけでなく、source\_role、external\_paste\_chars、large\_paste\_rate、paste\_after\_stuck\_rate として保存する。ただし本文は保存しない。  
* manual\_contribution\_ratio と productive\_manual\_recovery\_rate を gse-replay \--metrics に追加する。  
* AB/BA 条件、MRT の nudge/defer 割付、condition を session metadata に追加する。  
* Google Form の回答 ID と Dropbox のログ ID を participant\_id で結合し、氏名・メールとログを同じ場所に置かない。  
* 参考文献コード \[1\] 形式を本文末尾に付け、末尾の参考文献リストに URL を集約する。

# **参考文献**

\[1\] Pejovic, V., Lathia, N., Mascolo, C., & Musolesi, M. (2015). Mobile-Based Experience Sampling for Behaviour Research. arXiv:1508.03725. https://arxiv.org/abs/1508.03725

\[2\] Sahu, N. K., Sneh, A., Gupta, S., & Lone, H. R. (2025). Real-World Receptivity to Adaptive Mental Health Interventions: Findings from an In-the-Wild Study. arXiv:2508.02817. https://arxiv.org/abs/2508.02817

\[3\] Dziak, J. J., & Nahum-Shani, I. (2025). Constructing Evidence-Based Tailoring Variables for Adaptive Interventions. arXiv:2506.03054. https://arxiv.org/abs/2506.03054

\[4\] Qian, T., Walton, A. E., Collins, L. M., Klasnja, P., Lanza, S. T., Nahum-Shani, I., Rabbi, M., Russell, M. A., Walton, M. A., Yoo, H., & Murphy, S. A. (2021). The Micro-Randomized Trial for Developing Digital Interventions: Experimental Design and Data Analysis Considerations. arXiv:2107.03544. https://arxiv.org/abs/2107.03544

\[5\] Crotti, R., Denaro, G., Du, Z., & Muñoz Martín, R. (2026). Hylog: A Hybrid Approach to Logging Text Production in Non-alphabetic Scripts. arXiv:2601.17753. https://arxiv.org/abs/2601.17753

\[6\] Mehta, A., Kumar, R., Singla, A., Bisht, K., Singla, Y. K., & Shah, R. R. (2025). Detecting LLM-Assisted Academic Dishonesty using Keystroke Dynamics. arXiv:2511.12468. https://arxiv.org/abs/2511.12468

\[7\] Condrey, D. (2026). Detecting Cognitive Signatures in Typing Behavior for Non-Intrusive Authorship Verification. arXiv:2603.00177. https://arxiv.org/abs/2603.00177

\[8\] Oppezzo, M., & Schwartz, D. L. (2014). Give your ideas some legs: The positive effect of walking on creative thinking. Journal of Experimental Psychology: Learning, Memory, and Cognition, 40(4), 1142-1152. https://doi.org/10.1037/a0036577

\[9\] Bratman, G. N., Hamilton, J. P., Hahn, K. S., Daily, G. C., & Gross, J. J. (2015). Nature experience reduces rumination and subgenual prefrontal cortex activation. PNAS, 112(28), 8567-8572. https://doi.org/10.1073/pnas.1510459112

\[10\] Schwarzer, R., & Jerusalem, M. (1995). Generalized Self-Efficacy Scale. In J. Weinman, S. Wright, & M. Johnston (Eds.), Measures in Health Psychology: A User’s Portfolio. http://userpage.fu-berlin.de/\~health/selfscal.htm

\[11\] Hart, S. G., & Staveland, L. E. (1988). Development of NASA-TLX. NASA Task Load Index. https://humansystems.arc.nasa.gov/groups/TLX/

\[12\] Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. Journal of Environmental Psychology, 15(3), 169-182. https://doi.org/10.1016/0272-4944(95)90001-2

\[13\] Park, J. H. (2024). Discriminant Power of Smartphone-Derived Keystroke Dynamics for Mild Cognitive Impairment. Journal of Medical Internet Research, 26:e59247. https://doi.org/10.2196/59247

\[14\] Anderson, C., Heissler, C., Ohly, S., & David, K. (2018). Assessment of Social Roles for Interruption Management: A New Concept in the Field of Interruptibility. arXiv:1805.07793. https://arxiv.org/abs/1805.07793

\[15\] Google Workspace Help. How Google protects your organization’s security and privacy. https://support.google.com/a/answer/60762?hl=en

\[16\] Dropbox Help. How to create and manage Dropbox file requests. https://help.dropbox.com/share/create-file-request

\[17\] Dropbox Help. Dropbox account safety: how Dropbox keeps your files secure. https://help.dropbox.com/security/how-security-works