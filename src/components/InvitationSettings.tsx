import React, { useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import InvitationGlyph, { INVITATION_GLYPH } from "./InvitationGlyph";

// EH3 の招待の「説明と設定」の窓（招待の図像を押す・トレイから開く）。
//
// 守ること:
// - 本人の量（何回出た・残り・累計・何日続いた）を置かない（ADR-035 D6・ADR-025 D1）。
//   置いてよいのは系の設定値の選択肢だけ。
// - N 択だけ（自由な値の入力を置かない・ADR-035 D3）。初回に設定を強いない（D2）。
// - 規則と目的は書くが、個々の提示の理由には触れない（U-2 の候補・F-3 で研究者が文面を確かめる）。
// - 統制的な語（〜してください・〜すべき・休憩しましょう など）を使わない（I-4・R-I15）。
// ⚠️ この画面の操作は記録しない（NDJSON・applog とも）。設定は端末の中の `~/.gse/eh3_invitation.json` だけ。
// ⚠️ 文面は F-3 で研究者が確かめるまでの案である。

type TimeWindow = "core" | "extended" | "wide";
type DailyCap = "one" | "two" | "four";

interface InvitationSettingsValue {
    enabled: boolean;
    window: TimeWindow;
    cap: DailyCap;
}

const WINDOW_OPTIONS: { value: TimeWindow; label: string }[] = [
    { value: "core", label: "9 時から 18 時" },
    { value: "extended", label: "8 時から 20 時" },
    { value: "wide", label: "6 時から 22 時" },
];

const CAP_OPTIONS: { value: DailyCap; label: string }[] = [
    { value: "one", label: "1 日 1 回まで" },
    { value: "two", label: "1 日 2 回まで" },
    { value: "four", label: "1 日 4 回まで" },
];

const InvitationSettings: React.FC = () => {
    const [value, setValue] = useState<InvitationSettingsValue | null>(null);
    const [status, setStatus] = useState<string>("");
    // 保存中は替えさせない（続けて替えると、古い値を含む設定で上書きして「出さない」が戻りうる）
    const [saving, setSaving] = useState(false);
    // 同じ描画の中で続けて押されても 2 回送らないための錠（state はその描画の古い値を読む）
    const savingRef = useRef(false);

    useEffect(() => {
        invoke<InvitationSettingsValue>("get_invitation_settings")
            .then(setValue)
            .catch(() => setStatus("設定を読めませんでした。"));
    }, []);

    // 保存できたときだけ画面の値を替える（失敗したのに選んだ値が出たままにならないように）。
    const save = (next: InvitationSettingsValue) => {
        if (savingRef.current) return;
        savingRef.current = true;
        setSaving(true);
        invoke("set_invitation_settings", { settings: next })
            .then(() => {
                setValue(next);
                setStatus("保存しました。");
            })
            .catch(() => setStatus("保存できませんでした。"))
            .finally(() => {
                savingRef.current = false;
                setSaving(false);
            });
    };

    return (
        <main className="invitation-settings">
            <h1>
                <InvitationGlyph variant={INVITATION_GLYPH} />
                この印について
            </h1>
            <p>
                作業の途中で、画面の右上にこの印が出ることがあります。席を立って体を動かす、外の空気を吸いに出る、
                といったことをしてもよい、というお誘いです。応じても応じなくてもかまいません。印はおよそ 1 分で消えます。
            </p>
            <p>
                印が出るのは、打鍵の様子から、作業が進みにくくなっているかもしれない時間がしばらく続いたときです。
                これは推定なので、外れることがあります。同じひと続きの時間の中では 1 回までで、消えてから 30 分はあけます。
                出る時間帯と 1 日の回数は、下で選んだ範囲の中だけです。夜 22 時から朝 6 時までは出ません。
                1 回ごとの印について、その理由は表示しません。
            </p>
            <p>
                印を押したかどうかは記録しません。印が出た時刻は記録します（同意書の記録の項目のとおりです）。
                ここで選んだ設定の内容は、このパソコンの中にだけ保存し、記録には含めません。
            </p>

            {value && (
                <form onSubmit={(e) => e.preventDefault()}>
                    <fieldset disabled={saving}>
                        <legend>印を</legend>
                        <label>
                            <input
                                type="radio"
                                name="enabled"
                                checked={value.enabled}
                                onChange={() => save({ ...value, enabled: true })}
                            />
                            出す
                        </label>
                        <label>
                            <input
                                type="radio"
                                name="enabled"
                                checked={!value.enabled}
                                onChange={() => save({ ...value, enabled: false })}
                            />
                            出さない
                        </label>
                    </fieldset>
                    <fieldset disabled={saving}>
                        <legend>出る時間帯</legend>
                        {WINDOW_OPTIONS.map((o) => (
                            <label key={o.value}>
                                <input
                                    type="radio"
                                    name="window"
                                    checked={value.window === o.value}
                                    onChange={() => save({ ...value, window: o.value })}
                                />
                                {o.label}
                            </label>
                        ))}
                    </fieldset>
                    <fieldset disabled={saving}>
                        <legend>1 日の回数</legend>
                        {CAP_OPTIONS.map((o) => (
                            <label key={o.value}>
                                <input
                                    type="radio"
                                    name="cap"
                                    checked={value.cap === o.value}
                                    onChange={() => save({ ...value, cap: o.value })}
                                />
                                {o.label}
                            </label>
                        ))}
                    </fieldset>
                </form>
            )}
            <p className="invitation-settings-status" role="status">
                {status}
            </p>
        </main>
    );
};

export default InvitationSettings;
