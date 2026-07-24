# 文献カード: エージェント型コーディングの過信を content-free 行動テレメトリで検出できるか (RQ-2 専用ラウンド)

トピック: agentic-coding-overreliance-detection / 日付: 2026-07-24
動機: 前カード（`20260724-friction-retention-and-overreliance-evidence.md`）が3ラウンド連続で
「**RQ-2（agentic coding の過信を行動イベントのみで検出できるか＝設計書 Adapter B / Epic 4）は
検証を通過した一次証拠がゼロ＝判定不能**」と名指しした。本カードはその**穴を埋める専用 deep-research
ラウンド**（第4ラウンド・5 angle・20 ソース取得・84 claim 抽出→25 検証→24 confirmed / 1 refuted）。
用途は **Epic 4 の go/no-go gate**。RQ-2 は2問に分解:
- **(a)** AI ペアプロで自動化過信 / 盲目的 accept は実在し測定可能な行動署名を持つか
- **(b)** content-free 代理指標（accept 率・review dwell・test-before-accept・revert 率）が
  欠陥/脆弱性導入 or 測定された overreliance と実証的に相関するか

> **検証状態**: 各カードに 3 票パネル投票（`3-0` / `2-1`）を明記。GSE に有利な主張も不利な主張も
> 同じフィルタで否決（対称。§否決リスト参照）。**エビデンス温度を厳守し過大主張しない**
> （`research-positioning.md §8`・自己申告逆風）。

> **gate 判定（要点先出し）**:
> - **RQ-2(a) = 現象は確定（high）**。過信・過剰 accept は実在し、客観的に悪い成果（セキュリティ低下）を生む。
> - **RQ-2(b) = PLAUSIBLE BUT UNPROVEN（「直接証拠なし」に接する）**。**コーディング領域で content-free
>   代理指標と害/overreliance を同一セッションで同時測定した研究はコーパス中ゼロ**。リンクは
>   (i)代理を測るが accept 行為 or 自己申告生産性しか予測しない研究、(ii)害を測るがコード内容/Git
>   メタデータで測る研究、(iii)非コーディング領域で overreliance の行動検出を示す研究——の
>   継ぎ接ぎでしか成立しない。**Epic 4 を現状の前提のまま建てる根拠としては不十分＝「先に de-risk」が妥当**。

---

## パート A: RQ-2(a) — 過信は実在し害を生む（確定領域）

### カード1: Perry et al. (2023) — AI 支援は主観的安心と客観的セキュリティ低下を同時に生む **[検証済 3-0 / 2-1 / 3-0]** [V45]

arXiv: 2211.03622 (ACM CCS 2023, N=47, codex-davinci-002, Python/JS/C・5セキュリティ課題)

1. **どんなもの?**: AI アシスタント有無で書いたコードのセキュリティと、本人のセキュリティ確信度を比較した統制実験。
2. **先行研究と比べてどこがすごい?**: 過信を「主観と客観の乖離」として RCT で捉えた RQ-2(a) の礎石。
3. **技術・手法の肝**: **AI 支援群は 5 課題中 4 課題で有意にセキュリティが低いコードを書いた**（客観・χ²有意）
   のに、**自分のコードは安全だと信じやすかった**。**非安全な解を出した被験者ほど AI への信頼が高い**
   （Q3 平均 4.0 対 1.5）＝過信が悪い成果に直結。
4. **どう有効と検証?**: 統制実験（客観セキュリティ = 静的判定）+ 事後アンケート。
5. **議論はあるか?**: セキュリティ低下は客観・有意だが、**過信/信頼部分は自己申告**で信頼-非安全の逆相関は
   記述的（有意検定なし・小サブグループ n≈33）。**2022 年モデル（codex-davinci-002）で 2026 の
   エージェント型ツールへの外挿は未検証**。本研究自体は content-free 行動検出を検証していない。
6. **次に読むべき**: カード7（Perry の観察的二次分析）。
- **GSE への含意**: **Epic 4 が狙う現象（過信）の存在と害は確立**。ただし「検出できる」の証拠ではない
   ——「守るべき困難が存在する」に留め、検出可能性の接地には使わない。
- **やり残し**: 2026 世代エージェントで効果量が安定/拡大/縮小のいずれか。

### カード2: 害の実測研究はコード内容/Git で測る——行動テレメトリではない **[検証済 3-0 / 3-0]** [V46]

arXiv: 2310.02059 (GitHub 実プロジェクトの AI snippet 脆弱性) / 2603.28592 (302.6k AI-authored commits・6,299 repo・5アシスタント)

1. **どんなもの?**: 受容された AI コードが実際に抱える欠陥/CWE を静的解析 + Git メタデータで定量化。
2. **先行研究と比べてどこがすごい?**: 「AI コードは欠陥を運ぶ」を大規模実データで示した。
3. **技術・手法の肝**: Copilot 生成 snippet の**約 35.8% がセキュリティ弱点**を含む。別研究で
   **全アシスタントで 15%超の commit が静的解析 issue を1件以上導入**。technical-debt 研究は
   「検証なき盲目的 accept」を **ESLint/Pylint/Semgrep + Git メタで測り、定性記述に留める**。
4. **どう有効と検証?**: 静的解析 + リポジトリマイニング。
5. **議論はあるか?**: **これらは accept 率・dwell・test-before-accept・revert 率を一切測っていない**
   ——害側と行動代理側が同一研究で交わっていない、が RQ-2(b) の核心的空白。
6. **次に読むべき**: カード3（accept 行為だけ測る研究群）。
- **GSE への含意**: **害は実在するが、それを content-free 行動から予測できるという証拠にはならない**。
- **やり残し**: 同一セッションで行動代理×客観的害を co-measure した研究（＝gate が要する証拠）。

---

## パート B: RQ-2(b) — 代理指標は「accept 行為」までしか予測しない（未接続領域）

### カード3: content-free テレメトリは accept 行為を高精度予測——だが害へのリンクはゼロ **[検証済 3-0 (4件)]** [V47]

DOI: 10.1145/3808125 (PACMSE/FSE 2026, 66,329 産業インタラクション) / arXiv: 2601.21379 (CSAP)

1. **どんなもの?**: コード内容を見ずに、履歴 accept 率・生成間隔・タイミング等の content-free 特徴で
   suggestion の accept/reject を予測するモデル。
2. **先行研究と比べてどこがすごい?**: content-free での accept 予測の実現可能性を産業規模で実証。
3. **技術・手法の肝**: accept された suggestion は履歴 accept 数/率が有意に高く生成間隔が長い。
   **12 特徴中 content 由来は 1 つのみ**、意味的類似度は限定的有意＝**content-free 予測が ~0.97
   accuracy で成立**（別研究 CSAP は表示前予測 0.973/0.922）。
4. **どう有効と検証?**: 大規模ログの分類モデル。
5. **議論はあるか?**: **論文の目的は割込み suggestion のフィルタで、accept と欠陥/脆弱/過信の接続主張はゼロ**。
   特徴も RQ-2 の害代理（dwell・test-before-accept・revert）ではない。**部分的循環**（過去 accept から
   未来 accept を予測）。
6. **次に読むべき**: カード4（同型の pre-filter 研究）。
- **GSE への含意（gate 中核）**: **「accept 行為の content-free 検出」は実現可能**。しかし**それは
   overreliance の検出ではない**——高 accept 率は品質信号でないと著者自身が別研究で警告（カード5）。
- **やり残し**: accept 予測を欠陥/overreliance アウトカムに接続する研究。

### カード4: pre-invocation テレメトリだけで accept をほぼ倍化——実運用実装可能性 **[検証済 3-0]** [V48]

arXiv: 2511.18849 (4ヶ月 VS Code 本番デプロイ)

1. **どんなもの?**: タイピング速度・ファイルナビ・編集活動のみ（呼出前・content-free）で低価値 LLM 呼出を抑制する pre-filter。
2. **先行研究と比べてどこがすごい?**: content-free 信号の**運用有用性**を本番で示した。
3. **技術・手法の肝**: pre-filter で **accept 率 18.4%→34.2%**、低価値呼出 35% 抑制。
4. **どう有効と検証?**: 本番 A/B 相当のデプロイ計測。
5. **議論はあるか?**: **測っているのは accept 率の最適化であり害ではない**。RQ-2(b) の outcome 側は不在。
6. **次に読むべき**: カード5（accept 率↔成果の唯一の相関研究）。
- **GSE への含意**: GSE が passive に集められる種類の content-free 信号（ナビ/編集活動）で accept を
   予測できる＝**測定基盤の実現可能性は追い風**。ただし検出対象が「害」でない点は変わらない。
- **やり残し**: 同信号が blind vs verified accept を弁別できるか。

### カード5: Ziegler et al. (2024) — accept 率が最良予測子、ただし相手は自己申告生産性 ρ=0.24・revert 近縁指標は劣後 **[検証済 3-0 / 3-0 / 2-1]** [V49]

arXiv: 2205.06537 (CACM 67(3), 2024・GitHub 著者)

1. **どんなもの?**: Copilot テレメトリ各種と SPACE ベース自己申告生産性の相関を大規模に測った。
2. **先行研究と比べてどこがすごい?**: content-free テレメトリが「何と」相関するかを初めて数値化。
3. **技術・手法の肝**: **accept 率（accepted_per_shown）が知覚生産性の単独最良予測子だが ρ=0.24
   （弱・P<1e-4）**。**accept 後 30/120/300/600 秒でコードが変化しない persistence 指標
   （＝revert/rework の逆・RQ-2 の revert 代理に最も近い）は accept 率より一様に劣後**。
4. **どう有効と検証?**: 大規模相関分析。
5. **議論はあるか?**: **outcome が SPACE 自己申告＝プロジェクトが不信を置く指標そのもの**。ρ=0.24 は弱い。
   **著者が「意図せず 80% accept する壊れた Tab キーは便益なく高テレメトリを生む」と明記**し過剰 accept
   検出を自ら牽制。GitHub 著者 COI だが**主張は楽観に反する向き**なので採用。相関≠因果を著者明記。
6. **次に読むべき**: カード6（accept≠盲目 accept の直接観察）。
- **GSE への含意（gate に不利）**: **revert 近縁の persistence が accept 率より弱い**＝素朴な
   「revert 率で盲目 accept を測る」設計に逆風。accept 率の唯一の検証済相関は自己申告（不信対象）で ρ=0.24。
- **やり残し**: persistence/revert を客観的害に接続した研究。

### カード6: Tang et al. (2023) — accept と delete は content-free に弁別可、だが accept≠盲目（accept-then-verify）**[検証済 2-1 / 3-0]** [V50]

PLATEAU'23 (toby.li/files/plateau23-tang-copilot.pdf, N=9 質的ラボ)

1. **どんなもの?**: Copilot 使用中の IDE イベント列（accept/Undo/Redo）を content-free に記録・分析。
2. **先行研究と比べてどこがすごい?**: accept-and-keep と generate-then-delete の弁別可能性を IDE イベントのみで示した。
3. **技術・手法の肝**: trigram の **61.6% が連続 generate-accept、38.4% が直後の backspace 削除を含む**。
   accept(n=302)・Undo/Redo(n=96) を純 IDE イベントで記録。**だが被験者は accept 後に検証していた**。
4. **どう有効と検証?**: 小規模質的ラボ観察。
5. **議論はあるか?**: **N=9・欠陥/overreliance へのリンクなし**。**「accept 行為単独は盲目 accept の
   汚い代理」**——高 accept 率は真の検証と両立しうる。
6. **次に読むべき**: カード7（検証行動と安全性の唯一のヒント）。
- **GSE への含意**: **accept/revert を content-free に取れることは確認**。しかし**「いつ accept したか」
   だけでは blind か verified か分からない**——test-before/after-accept や dwell で弁別できるかが未解決の要。
- **やり残し**: accept-then-verify と blind-accept を content-free に分離する実証。

### カード7: Perry 二次分析 — 検証コスト行動と安全性の弱い連関（部分 content-coupled）**[検証済 3-0 / 3-0]** [V51]

arXiv: 2211.03622（観察的/二次分析）

1. **どんなもの?**: engagement 行動（プロンプト再構成・パラメータ調整・AI への不信）と脆弱性の関連の観察。
2. **先行研究と比べてどこがすごい?**: 行動→セキュリティ連関の最も直接的なヒント。
3. **技術・手法の肝**: **engagement 行動が多いほど脆弱性が少なく**、AI 出力と最終提出の低編集距離
   （"Model Close"）は安全解に達しにくい（**安全解の 87% は有意な編集を要した**）。
4. **どう有効と検証?**: n=47 の観察分析。
5. **議論はあるか?**: **信号が部分的に content-coupled**（再構成=プロンプト内容参照・編集距離=コード比較）。
   関係は**非対称**（安全解は編集を要するが、非安全解の編集距離は広くばらつく＝低編集距離→非安全は決定的でない）。
   効果量/有意検定なし・記述的。
6. **次に読むべき**: カード8（非コーディング領域の直接検出証拠）。
- **GSE への含意**: 行動→安全の連関は「実現可能性の示唆」までで**証明ではない**。純 content-free 化も未達。
- **やり残し**: content-free な検証行動代理と安全性の因果。

---

## パート C: 転移証拠——overreliance は行動検出できる（ただし非コーディング / 非純 content-free）

### カード8: 非コーディング領域では overreliance が行動署名を残す **[検証済 3-0 (4件)]** [V52]

DOI: 10.1145/3772318.3790332 (CHI 2026, misinformation, N=77) / arXiv: 2602.11567 / Swaroop et al. 2025 (Harvard, N=147, probe)

1. **どんなもの?**: 会話 LLM の誤情報課題とエイリアン医療判断課題で、overreliance を行動から推定できるか検証。
2. **先行研究と比べてどこがすごい?**: overreliance が**行動署名を残す**ことの最強の直接証拠（ただし転移証拠）。
3. **技術・手法の肝**: 誤情報課題（N=77）で**マウス/キーボードのナビ行動が低/高 overreliance を弁別**。
   判断課題（Swaroop, N=147）で**わざと誤った "probe" 推奨への accept/reject が overreliance quality を
   2 probe で ~92% 予測**（応答時間・性格を凌駕）。
4. **どう有効と検証?**: 観察 + probe 挿入実験。
5. **議論はあるか?（gate に重要な3制約）**: (1)**領域不一致**——誤情報検出・論理パズルでエージェント型
   コーディングでない。(2)**純 content-free でない**——CHI のマーカー（段落丸ごと copy-paste・誤情報の
   accept）は内容参照を要する。(3)**受動でない**——92% は**能動的な誤り注入**と construct 内自己相関
   （過去の過剰 accept が未来を予測）で、欠陥へのリンクではない。
6. **次に読むべき**: カード9（分野レビューの方法論的空白宣言）。
- **GSE への含意**: 「overreliance は行動検出できる」の一般命題は medium 支持。**コーディング領域への
   直接適用は low**。GSE が passive content-free で同じ弁別力を得られるかは未証明。
- **やり残し**: probe/ナビ署名がエージェント型コーディングに純 content-free で転移するか。

### カード9: 分野レビュー自身が「妥当な overreliance 測定法の不在」を認める **[検証済 3-0 / 3-0]** [V53]

arXiv: 2509.08010 (Ibrahim et al. 2025, overreliance 測定レビュー) / 2605.23130 (SOUPS 2026, セキュリティ意識・質的 N=15)

1. **どんなもの?**: overreliance 測定法の系統レビューと、AI 支援コーディングのセキュリティ意識の質的観察。
2. **先行研究と比べてどこがすごい?**: 「RQ-2(b) の空白は我々のサンプルの偏りでなく分野公認の open gap」を裏づけ。
3. **技術・手法の肝**: レビューは「**実証的証拠の欠如は妥当・適切な overreliance 測定法の不在を反映する**」
   と明記し測定方向を**提案するに留まる**。SOUPS 研究は質的（面接+観察 N=15）でテレメトリも欠陥相関もなし。
   関連観察: 実 IDE セッションで **"Validation" 意図はメッセージの 3.99% のみ**（低検証の行動署名の示唆）。
4. **どう有効と検証?**: 系統レビュー + 質的観察。
5. **議論はあるか?**: 提案止まりで検証済み測定法はなし。3.99% は示唆であり害への接続はない。
6. **次に読むべき**: 設計書 Adapter B（Epic 4）/ `research-positioning.md §8`。
- **GSE への含意（well-calibrated negative）**: **「現状の前提のまま Epic 4 を建てる証拠は不十分」が
   分野公認**。逆に言えば**「content-free 代理×客観的コーディング害を co-measure する de-risking pilot」を
   自作すれば、それ自体が分野の欠落を埋める貢献になりうる**。
- **やり残し**: まさにその co-measurement 研究（下記 open question 1）。

---

## パート D: gate 判定と否決リスト

### Epic 4 go/no-go への含意
- **建てるか（現状前提）**: **No / 先に de-risk**。load-bearing な RQ-2(b)（content-free 代理→害/overreliance）は
  コーディング領域で**直接証拠ゼロ**。revert 近縁指標は accept 率に劣後 [V49]、accept 率の唯一の検証済相関は
  自己申告 ρ=0.24 [V49]、92% probe 検出は能動注入×非コーディング [V52]。
- **測定基盤は追い風**: accept/reject/revert・ナビ/編集活動の content-free 収集は実現可能 [V47][V48][V50]。
  欠けているのは**「その信号が害を予測する」実証**であって信号取得能力ではない。
- **次の一手（推奨）**: 大規模実装前に、**content-free 代理指標と客観的コーディング害（導入欠陥/CWE）を
  同一セッションで co-measure する小規模 de-risking pilot**（分野の open gap そのもの）。self-report を
  基準に据えない（§8 逆風）。

### 否決リスト（対称フィルタ・引用禁止）
- **「AI 導入 issue の 22.7% が最新版まで残存＝過剰 accept の行動署名」= 0-3 否決**（arXiv 2603.28592）。
  残存率は review/revert 不足の直接証拠にならず、行動署名への飛躍が退けられた。GSE に有利な方向の主張だが否決。

## references.md 登録候補（本カードで登録・V 名前空間 append-only）

| [n] | 文献 | ID | 接地 |
|---|---|---|---|
| [V45] | Perry et al. (2023) CCS'23 | arXiv:2211.03622 | AI 支援は主観的安心↔客観的セキュリティ低下（過信の実在・RQ-2a 礎石） |
| [V46] | AI コード欠陥/脆弱の実測 | arXiv:2310.02059 / 2603.28592 | 害は静的解析+Git で測る＝行動テレメトリと未交差 |
| [V47] | acceptance-prediction (FSE/CSAP 2026) | 10.1145/3808125 / arXiv:2601.21379 | content-free で accept 行為を~0.97 予測・害リンクゼロ |
| [V48] | pre-invocation テレメトリ pre-filter | arXiv:2511.18849 | 呼出前 content-free 信号で accept ほぼ倍化（測定基盤実現可能性） |
| [V49] | Ziegler et al. (2024) CACM | arXiv:2205.06537 | accept 率↔自己申告生産性 ρ=0.24・revert 近縁 persistence は劣後 |
| [V50] | Tang et al. (2023) PLATEAU'23 | toby.li/plateau23-tang-copilot | accept/delete は content-free 弁別可・だが accept≠盲目(accept-then-verify) |
| [V51] | Perry 二次分析（engagement×安全） | arXiv:2211.03622 | 検証行動↔脆弱性の弱連関（部分 content-coupled・非対称） |
| [V52] | 非コーディング overreliance 検出 | 10.1145/3772318.3790332 / arXiv:2602.11567 / Swaroop 2025 | overreliance は行動検出可(92%/2probe)・領域不一致・非純 content-free・能動注入 |
| [V53] | overreliance 測定レビュー + SOUPS 2026 | arXiv:2509.08010 / 2605.23130 | 分野が妥当な測定法の不在を公認（well-calibrated negative） |

> **重複防止キー**: 上記 arXiv ID / DOI は既存 references.md に未登録を確認済み（citation-ssot dedup）。
> **番号は V 名前空間の末尾 [V44] に続けて append**（renumber 禁止・恒久 ID）。
> **前カードとの関係**: 前カードの [V37]Buçinca / [V38]Vasconcelos（overreliance の隣接理論）を
> 実証面から補完。前カードが「判定不能」とした RQ-2 を本ラウンドで「(a)確定 / (b)未証明」まで前進させた。
