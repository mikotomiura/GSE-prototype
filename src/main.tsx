import React from "react";
import ReactDOM from "react-dom/client";
import { getCurrentWindow } from "@tauri-apps/api/window";
import App from "./App";

// Layer 2: React マウント前にウィンドウ別の背景制御。
// overlay ウィンドウでは index.html のインライン背景 (#0f172a) を透過に切り替える。
// main ウィンドウでは #0f172a のままにし、CSS/React 依存なしで黒画面を防止する。
// getCurrentWindow() は __TAURI_INTERNALS__ を参照する同期 API なので安全。
if (getCurrentWindow().label === "overlay") {
  document.body.style.backgroundColor = "transparent";
}

// Layer 2: ErrorBoundary — React レンダーエラーを可視化。
// エラーが黒画面として無音で隠れることを防ぐ。
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { error: Error | null }
> {
  state = { error: null as Error | null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return React.createElement(
        "div",
        {
          style: {
            padding: "2rem",
            color: "#f8fafc",
            backgroundColor: "#0f172a",
            minHeight: "100vh",
            fontFamily: "system-ui, sans-serif",
          },
        },
        React.createElement("h1", { key: "h" }, "GSE: Render Error"),
        React.createElement(
          "pre",
          { key: "e", style: { whiteSpace: "pre-wrap", opacity: 0.7 } },
          this.state.error.message + "\n" + this.state.error.stack
        )
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
