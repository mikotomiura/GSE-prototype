# typescript-standards: Tauri IPC パターン集

## 1. 500ms ポーリングパターン（認知状態取得）

```typescript
useEffect(() => {
  if (!isRunning) return;

  const poll = async () => {
    try {
      const state = await invoke<CognitiveState>("get_cognitive_state");
      setCogState(state);
    } catch (e) {
      // IPC 失敗 → 安全なデフォルトに戻す
      setCogState({ p_flow: 1.0, p_incubation: 0.0, p_stuck: 0.0, label: "Flow" });
    }
  };

  const id = setInterval(poll, 500);
  return () => clearInterval(id);
}, [isRunning]);
```

---

## 2. Tauri イベント listen パターン（Wall 解除通知）

```typescript
useEffect(() => {
  const unlisten = listen<void>("wall-unlocked", () => {
    setWallActive(false);
  });

  return () => {
    unlisten.then(f => f());  // クリーンアップ
  };
}, []);
```

---

## 3. Wall Server 起動・停止パターン

```typescript
interface WallServerInfo {
  url: string;
  qr_svg: string;
  token: string;
}

const startWall = async () => {
  try {
    const info = await invoke<WallServerInfo>("start_wall_server");
    setWallInfo(info);
    setWallActive(true);
  } catch (e) {
    console.error("wall server failed to start:", e);
    // Wall なしで継続（graceful degradation）
  }
};

const stopWall = async () => {
  try {
    await invoke<void>("stop_wall_server");
  } finally {
    setWallActive(false);
    setWallInfo(null);
  }
};
```

---

## 4. Stuck 累積時間追跡パターン

Wall トリガー (p_stuck > 0.70 が 30 秒以上) の累積計測は Frontend の責務。
ただし閾値の 0.70 や 30 秒はバックエンドの設計値を参照するだけで、
Frontend で変更しない。

```typescript
const stuckAccumMsRef = useRef<number>(0);
const lastPollTimeRef = useRef<number>(Date.now());

// ポーリング内で累積
const now = Date.now();
const delta = now - lastPollTimeRef.current;
lastPollTimeRef.current = now;

if (state.p_stuck > 0.70) {
  stuckAccumMsRef.current += delta;
  if (stuckAccumMsRef.current >= 30_000 && !wallActive) {
    startWall();
  }
} else {
  stuckAccumMsRef.current = 0;  // リセット
}
```
