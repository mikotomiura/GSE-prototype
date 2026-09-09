# ⚠️★★★ Windows へ渡す 5 分の実験 —— `\Process(x)\% Processor Time` の規約を決める

## ★ 何を決めるのか

`experiments/20260903-o1-runtime-cost/scripts/sample-windows.sh` が記録した CPU% が
**どちらの基準か**を決める。⚠️ これで O1 の配布可否の解釈が 16 倍変わる。

| ★ 規約 | ★ 意味 |
|---|---|
| **1 コア = 100 %**（合計基準） | macOS `top` と同じ。⚠️ **×16 換算は誤り**。Windows 平均 2.06 % はそのまま 2.06 % |
| **全コア = 100 %**（正規化基準） | Task Manager と同じ。★ ×16 が正しく、⚠️ 平均 33 % で FAIL 相当 |

## ★ 手順（PowerShell・管理者不要）

```powershell
# ★ 0. 論理プロセッサ数を出す（★ 期待 16）
(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors

# ★ 1. 1 コアを 100% 占有するプロセスを 1 個だけ作る
$job = Start-Process powershell -PassThru -ArgumentList '-NoProfile','-Command','while($true){}'
Start-Sleep 8

# ★ 2. サンプラと同じ式で読む（⚠️ 式を変えないこと）
1..3 | ForEach-Object {
  (Get-Counter -Counter "\Process(powershell*)\% Processor Time").CounterSamples |
    Select-Object InstanceName, CookedValue | Format-Table -AutoSize
  Start-Sleep 2
}

# ★ 3. 後始末（⚠️ 必ず止める。放置すると 1 コアを焼き続ける）
Stop-Process -Id $job.Id
```

## ★ 読み方

⚠️ `powershell*` のインスタンスは**複数**出る（★ 実験を打っている窓自身も含む）。
★ 見るのは **busy-loop 側＝ CookedValue が最大のもの**。

| ★ 最大の CookedValue | ★ 結論 |
|---|---|
| **≒ 100**（90〜105） | ★ **合計基準**。⚠️ **×16 は誤り** → notes.md の「FAIL 相当」を撤回する |
| **≒ 6.25**（100 / 16） | ★ **正規化基準**。⚠️ ×16 が正しい → **配布可否を再判断** |
| ★ それ以外 | ⚠️ **どちらでもない** → 生の数字をそのまま貼って返す（★ 丸めない） |

## ⚠️ 陽性対照になっている理由

★ busy-loop は **確実に 1 コアぶん** を食う（⚠️ `while($true){}` は単一スレッド）。
→ ★ 読み値が「1 コアぶんをどう表現するか」を直接見ていることになる。

## ★ 返してほしいもの

1. ★ 手順 0 の数字
2. ★ 手順 2 の出力を**そのまま**（⚠️ 要約しない・小数を丸めない）
3. ⚠️ 途中で何かおかしかったら**それも**（★ 「うまくいった」だけだと検算できない）
