# physical-anchor: Flutter 統合スケッチ

## アーキテクチャ概要

```
Tauri App (Windows)
    │
    │ Wall Server 拡張 (tiny_http)
    │ GET /anchor → Flutter WebView に HTML 配信
    │ POST /anchor/progress ← 進捗受信
    │ POST /anchor/complete ← 完了受信
    │
スマートフォン (iOS / Android)
    ├── 方式 A: ブラウザで /anchor を開く（QR コード経由）
    └── 方式 B: Flutter アプリを事前インストール
```

**推奨: 方式 A（ブラウザ）で MVP を構築。方式 B は Lv4 屋外対応時に追加。**

---

## Flutter 実装スケッチ（Lv3: 室内歩行）

```dart
import 'package:pedometer/pedometer.dart';

class PhysicalAnchorLv3 extends StatefulWidget {
  final String serverUrl;  // Wall Server の URL
  final int targetSteps;   // 目標歩数（Tauri から受け取る）

  const PhysicalAnchorLv3({
    required this.serverUrl,
    this.targetSteps = 100,
  });
}

class _PhysicalAnchorLv3State extends State<PhysicalAnchorLv3> {
  late StreamSubscription<StepCount> _stepSub;
  int _steps = 0;
  final _startTime = DateTime.now();

  @override
  void initState() {
    super.initState();
    _stepSub = Pedometer.stepCountStream.listen(_onStep);
  }

  void _onStep(StepCount event) {
    setState(() => _steps++);

    final elapsed = DateTime.now().difference(_startTime);
    final speedMs = _steps * 0.75 / max(elapsed.inSeconds, 1);

    // 進捗を Wall Server に報告
    http.post(Uri.parse('${widget.serverUrl}/anchor/progress'), body: jsonEncode({
      'steps': _steps,
      'distance_m': _steps * 0.75,
      'speed_ms': speedMs,
      'elapsed_s': elapsed.inSeconds,
    }));

    // 完了判定は Rust 側が行うが、UI フィードバック用にローカルでも確認
    if (_steps >= widget.targetSteps) {
      _onComplete();
    }
  }

  void _onComplete() {
    http.post(Uri.parse('${widget.serverUrl}/anchor/complete'));
    // 完了画面を表示
  }
}
```

---

## Lv4 屋外散歩（geolocator 追加）

```dart
import 'package:geolocator/geolocator.dart';

// Lv4 では GPS 距離も計測
StreamSubscription<Position>? _posSub;
double _totalDistance = 0.0;
Position? _lastPosition;

void _startGps() {
  _posSub = Geolocator.getPositionStream(
    locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
  ).listen((pos) {
    if (_lastPosition != null) {
      _totalDistance += Geolocator.distanceBetween(
        _lastPosition!.latitude, _lastPosition!.longitude,
        pos.latitude, pos.longitude,
      );
    }
    _lastPosition = pos;
    _reportProgress();
  });
}
```

---

## Wall Server 拡張エンドポイント（Rust 側）

```rust
// wall_server.rs に追加するハンドラ

fn handle_anchor_progress(request: &Request, progress_tx: &Sender<AnchorProgress>) {
    // ボディを JSON パース
    let mut body = String::new();
    request.as_reader().read_to_string(&mut body).ok();
    if let Ok(progress) = serde_json::from_str::<AnchorProgress>(&body) {
        tracing::info!(
            steps = progress.steps,
            distance_m = progress.distance_m,
            speed_ms = progress.speed_ms,
            "anchor progress received"
        );
        progress_tx.try_send(progress).ok();
    }
}
```
