import React, { useEffect, useState, useMemo, useRef } from 'react';
import { getCurrentWindow } from "@tauri-apps/api/window";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

interface OverlayProps {
    stuckProb: number;
    isWallActive: boolean;
}

interface WallServerInfo {
    url: string;
    qr_svg: string;
}

const Overlay: React.FC<OverlayProps> = ({ stuckProb, isWallActive }) => {
    const [nudgeOpacity, setNudgeOpacity] = useState(0);
    const [wallServerInfo, setWallServerInfo] = useState<WallServerInfo | null>(null);
    const [showTypingWarning, setShowTypingWarning] = useState(false);
    const [phoneConnected, setPhoneConnected] = useState(false);
    const currentWindow = useMemo(() => getCurrentWindow(), []);

    // Wall発動中のキーボード打鍵検知に使うref群
    const wallStartTimeRef = useRef<number>(0);
    const lastWarnedKeyAtRef = useRef<number>(0);
    const warningTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // スマートフォン接続イベントの購読
    useEffect(() => {
        const unlisten = listen("wall-phone-connected", () => {
            setPhoneConnected(true);
        });
        return () => {
            unlisten.then((f) => f());
        };
    }, []);

    // マウント直後に即座にクリック透過を有効化 (初期状態保証)
    // React の useEffect は最初のレンダー後に実行されるため、起動時に
    // オーバーレイが一瞬クリックをブロックしてウィンドウをドラッグ不能にする問題を防ぐ。
    useEffect(() => {
        currentWindow.setIgnoreCursorEvents(true).catch(() => {});
    // currentWindow は useMemo で安定しているが lint 警告を避けるため含める
    }, [currentWindow]); // eslint-disable-line react-hooks/exhaustive-deps

    // isWallActive に応じてクリック透過をトグル
    // Lv1 (nudge): クリック透過 → ユーザーは下のウィンドウを操作可能
    // Lv2 (wall):  クリックブロック → QRコードをスキャンするまで操作不可
    useEffect(() => {
        currentWindow.setIgnoreCursorEvents(!isWallActive);
    }, [isWallActive, currentWindow]);

    // Wall発動/解除に連動してWall Serverを起動/停止する
    useEffect(() => {
        if (isWallActive) {
            invoke<WallServerInfo>("start_wall_server")
                .then(info => setWallServerInfo(info))
                .catch(e => console.error("Failed to start wall server:", e));
        } else {
            invoke("stop_wall_server").catch(console.error);
            setWallServerInfo(null);
        }
    }, [isWallActive]);

    // Wall発動時刻を記録し、Wall解除時にリセット
    useEffect(() => {
        if (isWallActive) {
            wallStartTimeRef.current = Date.now();
            lastWarnedKeyAtRef.current = 0;
            setShowTypingWarning(false);
        }
    }, [isWallActive]);

    // Wall発動中のキーボード打鍵検知: 打鍵を検知したら警告バナーを2.5秒表示
    // lastKeyAt = Date.now() - idle が wallStartTime より後なら Wall後の打鍵
    // 同一バーストへの重複警告を防ぐため1秒のデバウンスを設ける
    useEffect(() => {
        if (!isWallActive) {
            setShowTypingWarning(false);
            return;
        }
        const interval = setInterval(async () => {
            try {
                // get_last_keypress_timestamp() は Rust の LAST_KEY_MS をエポックmsで直接返す。
                // Date.now() - idle_ms の逆算より精度が高い (advice.md §D)
                const lastKeyAt = await invoke<number>("get_last_keypress_timestamp");
                if (
                    lastKeyAt > wallStartTimeRef.current &&
                    lastKeyAt > lastWarnedKeyAtRef.current + 1000
                ) {
                    lastWarnedKeyAtRef.current = lastKeyAt;
                    setShowTypingWarning(true);
                    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
                    warningTimerRef.current = setTimeout(() => setShowTypingWarning(false), 2500);
                }
            } catch (_) {}
        }, 300);
        return () => {
            clearInterval(interval);
            if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
        };
    }, [isWallActive]);

    useEffect(() => {
        // Nudge Logic: visual feedback starts at 0.6 stuck probability
        if (stuckProb > 0.6 && !isWallActive) {
            // Map 0.6-0.9 to 0.0-1.0 opacity
            const opacity = Math.min(1, (stuckProb - 0.6) / 0.3);
            setNudgeOpacity(opacity);
        } else {
            setNudgeOpacity(0);
        }
    }, [stuckProb, isWallActive]);

    // Layer 4: macOS で overlay の透過が失敗した場合のフォールバック。
    // nudge も wall も不要な間は hide() してメインウィンドウを隠さない。
    // nudge/wall が必要になったら show() で再表示する。
    // macOS で透過が正常動作している場合は無駄な呼び出しだが副作用はない。
    useEffect(() => {
        const shouldBeVisible = nudgeOpacity > 0 || isWallActive;
        if (shouldBeVisible) {
            currentWindow.show().catch(() => {});
        } else {
            currentWindow.hide().catch(() => {});
        }
    }, [nudgeOpacity, isWallActive, currentWindow]);

    return (
        <div className="overlay-root">
            {/* Nudge Layer (Red Vignette) */}
            <div
                className="nudge-layer"
                style={{ opacity: nudgeOpacity }}
            ></div>

            {/* The Wall (Blocking Layer) */}
            {isWallActive && (
                <div className="wall-layer">
                    <h1>Time to Move!</h1>
                    <p>Scan the QR code with your phone to unlock</p>

                    {wallServerInfo ? (
                        <div className="qr-container">
                            <img src={wallServerInfo.qr_svg} alt="QR Code" className="qr-code" />
                            <p className="qr-hint">
                                Open camera app and point at QR code
                            </p>
                            {wallServerInfo.url && (
                                <p className="qr-url">{wallServerInfo.url}</p>
                            )}
                        </div>
                    ) : (
                        <p className="qr-loading">Starting unlock server...</p>
                    )}

                    <p className="wall-network-hint">
                        PCとスマホが同じWi-Fiに接続されていることを確認してください
                    </p>
                    {/* スマートフォン接続バッジ */}
                    {phoneConnected && (
                        <div className="phone-connected-badge">
                            Phone connected — Zen Timer running
                        </div>
                    )}
                    {/* Wall発動中の打鍵警告バナー */}
                    {showTypingWarning && (
                        <div className="wall-typing-warning">
                            ⚠ キーボードは使えません！
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Overlay;
