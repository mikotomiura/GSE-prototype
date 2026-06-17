use serde::Serialize;

const NUDGE_NEED_THRESHOLD: f64 = 0.60;
const WALL_NEED_THRESHOLD: f64 = 0.70;
const WALL_SLACK_THRESHOLD: f64 = 0.50;
const NUDGE_OPPORTUNITY_THRESHOLD: f64 = 0.35;
const WALL_OPPORTUNITY_THRESHOLD: f64 = 0.45;
const WALL_ACCUMULATION_MS: u64 = 30_000;
const NUDGE_COOLDOWN_MS: u64 = 10 * 60 * 1000;
const WALL_COOLDOWN_MS: u64 = 60 * 60 * 1000;
const RECENT_DISMISS_MS: u64 = 20 * 60 * 1000;
const SHORT_PAUSE_MIN_MS: u64 = 2_000;
const SHORT_PAUSE_MAX_MS: u64 = 8_000;
const MEDIUM_PAUSE_MAX_MS: u64 = 30_000;
const AWAY_IDLE_MS: u64 = 180_000;
const NUDGE_DAILY_CAP: u32 = 6;
const WALL_DAILY_CAP: u32 = 1;
const DAY_MS: u64 = 24 * 60 * 60 * 1000;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum InterventionAction {
    None,
    Nudge,
    Wall,
    Defer,
}

impl InterventionAction {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::Nudge => "nudge",
            Self::Wall => "wall",
            Self::Defer => "defer",
        }
    }

    pub fn parse(value: &str) -> Option<Self> {
        match value {
            "none" => Some(Self::None),
            "nudge" => Some(Self::Nudge),
            "wall" => Some(Self::Wall),
            "defer" => Some(Self::Defer),
            _ => None,
        }
    }
}

/// Opportunity 層の加点理由を機械可読化した enum。
///
/// production の `calculate_opportunity` が返す reason 文字列の**単一真実源**。
/// `as_str()` は現行文字列を byte 一致で再生する (既存 NDJSON ログ・IPC・テストの
/// `reason` 文字列を不変に保つため)。`InterventionDecision` には `#[serde(skip)]`
/// で載せるので NDJSON schema にも IPC JSON にも出ず in-memory のみ。評価層
/// (`intervention_eval`) が reason 別の HIR/Precision 層別化に使う。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum OpportunityReason {
    LowOpportunity,
    ShortPause,
    MediumPause,
    LongPause,
    ActiveTyping,
    PostBurstPause,
    CorrectionAfterPause,
    ActiveCorrectionLoop,
}

impl OpportunityReason {
    /// production の reason 文字列を byte 一致で再生する (単一真実源)。
    pub fn as_str(self) -> &'static str {
        match self {
            Self::LowOpportunity => "low_opportunity",
            Self::ShortPause => "short_pause",
            Self::MediumPause => "medium_pause",
            Self::LongPause => "long_pause",
            Self::ActiveTyping => "active_typing",
            Self::PostBurstPause => "post_burst_pause",
            Self::CorrectionAfterPause => "correction_after_pause",
            Self::ActiveCorrectionLoop => "active_correction_loop",
        }
    }

    /// 評価層が reason 別層別化を固定順 (決定的 JSON 出力) で反復するための全 variant。
    pub const ALL: [OpportunityReason; 8] = [
        Self::LowOpportunity,
        Self::ShortPause,
        Self::MediumPause,
        Self::LongPause,
        Self::ActiveTyping,
        Self::PostBurstPause,
        Self::CorrectionAfterPause,
        Self::ActiveCorrectionLoop,
    ];
}

/// sweep / オフライン評価のために注入可能にした float 閾値群。
///
/// `Default` は現行のモジュール const と**完全同値**であり、production
/// (`InterventionPolicyState::new`) は既定値で動くため挙動は不変。評価層のみ
/// sweep 値で `new_with_thresholds` を呼ぶ。duration / cap / pause band 系 const は
/// 本タスクの sweep 対象外なので据え置く。
#[derive(Debug, Clone, Copy)]
pub struct InterventionThresholds {
    pub nudge_need: f64,
    pub wall_need: f64,
    pub wall_slack: f64,
    pub nudge_opportunity: f64,
    pub wall_opportunity: f64,
}

impl Default for InterventionThresholds {
    fn default() -> Self {
        Self {
            nudge_need: NUDGE_NEED_THRESHOLD,
            wall_need: WALL_NEED_THRESHOLD,
            wall_slack: WALL_SLACK_THRESHOLD,
            nudge_opportunity: NUDGE_OPPORTUNITY_THRESHOLD,
            wall_opportunity: WALL_OPPORTUNITY_THRESHOLD,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct InterventionDecision {
    pub action: InterventionAction,
    pub need_score: f64,
    pub opportunity_score: f64,
    pub p_stuck: f64,
    pub idle_ms: u64,
    pub wall_accum_ms: u64,
    pub reason: String,
    pub suppressed_by: Vec<String>,
    /// Opportunity 層の加点理由 (機械可読)。`#[serde(skip)]` で NDJSON schema /
    /// IPC JSON には出さず in-memory のみ。評価層の reason 別層別化に使う。
    /// production 出力は従来どおり `reason: String` を使う。
    #[serde(skip)]
    pub opportunity_reason: OpportunityReason,
}

impl InterventionDecision {
    pub fn safe_default() -> Self {
        Self {
            action: InterventionAction::None,
            need_score: 0.0,
            opportunity_score: 0.0,
            p_stuck: 0.0,
            idle_ms: 0,
            wall_accum_ms: 0,
            reason: "safe_default".to_string(),
            suppressed_by: Vec::new(),
            opportunity_reason: OpportunityReason::LowOpportunity,
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct InterventionInput {
    pub now_ms: u64,
    pub p_stuck: f64,
    pub f3_correction_rate: f64,
    pub f4_burst_length: f64,
    pub f6_pause_after_del_rate: f64,
    pub idle_ms: u64,
    pub monk_mode: bool,
    pub wall_active: bool,
}

#[derive(Debug, Clone)]
pub struct DecisionResult {
    pub decision: InterventionDecision,
    pub should_log: bool,
}

#[derive(Debug)]
pub struct InterventionPolicyState {
    day_index: u64,
    nudge_count_today: u32,
    wall_count_today: u32,
    last_tick_ms: Option<u64>,
    last_nudge_at_ms: Option<u64>,
    last_wall_at_ms: Option<u64>,
    last_dismiss_at_ms: Option<u64>,
    last_dismiss_action: Option<InterventionAction>,
    current_action: InterventionAction,
    wall_accum_ms: u64,
    last_decision: InterventionDecision,
    last_log_key: Option<String>,
    last_log_at_ms: Option<u64>,
    /// 注入された閾値。production は既定値 (= 現行 const)。評価層のみ sweep 値。
    thresholds: InterventionThresholds,
}

impl InterventionPolicyState {
    /// production 既定。閾値は現行 const と同値の `InterventionThresholds::default()`。
    pub fn new(now_ms: u64) -> Self {
        Self::new_with_thresholds(now_ms, InterventionThresholds::default())
    }

    /// 評価 / sweep 用。既定以外の閾値を注入する。production からは呼ばない。
    pub fn new_with_thresholds(now_ms: u64, thresholds: InterventionThresholds) -> Self {
        Self {
            day_index: day_index(now_ms),
            nudge_count_today: 0,
            wall_count_today: 0,
            last_tick_ms: None,
            last_nudge_at_ms: None,
            last_wall_at_ms: None,
            last_dismiss_at_ms: None,
            last_dismiss_action: None,
            current_action: InterventionAction::None,
            wall_accum_ms: 0,
            last_decision: InterventionDecision::safe_default(),
            last_log_key: None,
            last_log_at_ms: None,
            thresholds,
        }
    }

    pub fn last_decision(&self) -> InterventionDecision {
        self.last_decision.clone()
    }

    pub fn record_dismiss(&mut self, action: InterventionAction, now_ms: u64) {
        if matches!(action, InterventionAction::Nudge | InterventionAction::Wall) {
            self.last_dismiss_at_ms = Some(now_ms);
            self.last_dismiss_action = Some(action);
            if self.current_action == action {
                self.current_action = InterventionAction::None;
            }
        }
    }

    pub fn decide(&mut self, input: InterventionInput) -> DecisionResult {
        self.reset_daily_if_needed(input.now_ms);

        if input.wall_active {
            self.wall_accum_ms = 0;
            self.current_action = InterventionAction::Wall;
            let decision = InterventionDecision {
                action: InterventionAction::Wall,
                need_score: clean_score(input.p_stuck),
                opportunity_score: 1.0,
                p_stuck: clean_score(input.p_stuck),
                idle_ms: input.idle_ms,
                wall_accum_ms: 0,
                reason: "wall_active".to_string(),
                suppressed_by: Vec::new(),
                opportunity_reason: OpportunityReason::LowOpportunity,
            };
            let should_log = self.should_log(input.now_ms, &decision);
            self.last_decision = decision.clone();
            return DecisionResult {
                decision,
                should_log,
            };
        }

        self.update_wall_accumulation(&input);

        let p_stuck = clean_score(input.p_stuck);
        let need_score = p_stuck;
        let (opportunity_score, opportunity_reason) = calculate_opportunity(&input);

        let mut suppressed_by = Vec::new();
        let mut candidate = if input.idle_ms >= AWAY_IDLE_MS {
            suppressed_by.push("away_idle".to_string());
            InterventionAction::None
        } else if need_score < self.thresholds.nudge_need {
            InterventionAction::None
        } else if need_score >= self.thresholds.wall_need
            && self.wall_accum_ms >= WALL_ACCUMULATION_MS
        {
            if opportunity_score >= self.thresholds.wall_opportunity {
                InterventionAction::Wall
            } else {
                InterventionAction::Defer
            }
        } else if opportunity_score >= self.thresholds.nudge_opportunity {
            InterventionAction::Nudge
        } else {
            InterventionAction::Defer
        };

        if candidate == InterventionAction::Wall {
            self.apply_wall_suppressions(input.now_ms, input.monk_mode, &mut suppressed_by);
            if !suppressed_by.is_empty() {
                candidate = InterventionAction::Defer;
            }
        } else if candidate == InterventionAction::Nudge {
            self.apply_nudge_suppressions(input.now_ms, &mut suppressed_by);
            if !suppressed_by.is_empty() {
                candidate = InterventionAction::Defer;
            }
        }

        let reason = reason_for(
            candidate,
            need_score,
            opportunity_score,
            opportunity_reason,
            &self.thresholds,
        );
        self.record_activation(candidate, input.now_ms);

        let decision = InterventionDecision {
            action: candidate,
            need_score,
            opportunity_score,
            p_stuck,
            idle_ms: input.idle_ms,
            wall_accum_ms: self.wall_accum_ms,
            reason,
            suppressed_by,
            opportunity_reason,
        };
        let should_log = self.should_log(input.now_ms, &decision);
        self.current_action = candidate;
        self.last_decision = decision.clone();

        DecisionResult {
            decision,
            should_log,
        }
    }

    fn reset_daily_if_needed(&mut self, now_ms: u64) {
        let current_day = day_index(now_ms);
        if current_day != self.day_index {
            self.day_index = current_day;
            self.nudge_count_today = 0;
            self.wall_count_today = 0;
        }
    }

    fn update_wall_accumulation(&mut self, input: &InterventionInput) {
        let elapsed_ms = self
            .last_tick_ms
            .map(|last| input.now_ms.saturating_sub(last))
            .unwrap_or(0);
        self.last_tick_ms = Some(input.now_ms);

        if input.monk_mode {
            self.wall_accum_ms = 0;
            return;
        }

        let p_stuck = clean_score(input.p_stuck);
        if p_stuck >= self.thresholds.wall_need {
            self.wall_accum_ms = self.wall_accum_ms.saturating_add(elapsed_ms);
        } else if p_stuck < self.thresholds.wall_slack {
            self.wall_accum_ms = self
                .wall_accum_ms
                .saturating_sub(elapsed_ms.saturating_mul(2));
        }
    }

    fn apply_nudge_suppressions(&self, now_ms: u64, suppressed_by: &mut Vec<String>) {
        if self.current_action != InterventionAction::Nudge {
            if self.nudge_count_today >= NUDGE_DAILY_CAP {
                suppressed_by.push("daily_cap".to_string());
            }
            if recently(now_ms, self.last_nudge_at_ms, NUDGE_COOLDOWN_MS) {
                suppressed_by.push("cooldown".to_string());
            }
        }
        if self.recently_dismissed(now_ms, InterventionAction::Nudge) {
            suppressed_by.push("recent_dismiss".to_string());
        }
    }

    fn apply_wall_suppressions(
        &self,
        now_ms: u64,
        monk_mode: bool,
        suppressed_by: &mut Vec<String>,
    ) {
        if monk_mode {
            suppressed_by.push("monk_mode".to_string());
        }
        if self.current_action != InterventionAction::Wall {
            if self.wall_count_today >= WALL_DAILY_CAP {
                suppressed_by.push("daily_cap".to_string());
            }
            if recently(now_ms, self.last_wall_at_ms, WALL_COOLDOWN_MS) {
                suppressed_by.push("cooldown".to_string());
            }
        }
        if self.recently_dismissed(now_ms, InterventionAction::Wall) {
            suppressed_by.push("recent_dismiss".to_string());
        }
    }

    fn recently_dismissed(&self, now_ms: u64, action: InterventionAction) -> bool {
        self.last_dismiss_action
            .map(|dismissed| dismissed == action)
            .unwrap_or(false)
            && recently(now_ms, self.last_dismiss_at_ms, RECENT_DISMISS_MS)
    }

    fn record_activation(&mut self, action: InterventionAction, now_ms: u64) {
        if action == self.current_action {
            return;
        }
        match action {
            InterventionAction::Nudge => {
                self.nudge_count_today = self.nudge_count_today.saturating_add(1);
                self.last_nudge_at_ms = Some(now_ms);
            }
            InterventionAction::Wall => {
                self.wall_count_today = self.wall_count_today.saturating_add(1);
                self.last_wall_at_ms = Some(now_ms);
                self.wall_accum_ms = 0;
            }
            InterventionAction::None | InterventionAction::Defer => {}
        }
    }

    fn should_log(&mut self, now_ms: u64, decision: &InterventionDecision) -> bool {
        let interesting = decision.action != InterventionAction::None
            || !decision.suppressed_by.is_empty()
            || decision.need_score >= self.thresholds.nudge_need;
        if !interesting {
            return false;
        }

        let key = format!(
            "{}|{}|{}",
            decision.action.as_str(),
            decision.reason,
            decision.suppressed_by.join(",")
        );
        let changed = self.last_log_key.as_deref() != Some(key.as_str());
        let due = self
            .last_log_at_ms
            .map(|last| now_ms.saturating_sub(last) >= 5_000)
            .unwrap_or(true);

        if changed || due {
            self.last_log_key = Some(key);
            self.last_log_at_ms = Some(now_ms);
            true
        } else {
            false
        }
    }
}

fn calculate_opportunity(input: &InterventionInput) -> (f64, OpportunityReason) {
    let mut score: f64 = 0.0;
    let mut reason = OpportunityReason::LowOpportunity;

    if (SHORT_PAUSE_MIN_MS..=SHORT_PAUSE_MAX_MS).contains(&input.idle_ms) {
        score += 0.45;
        reason = OpportunityReason::ShortPause;
    } else if input.idle_ms > SHORT_PAUSE_MAX_MS && input.idle_ms <= MEDIUM_PAUSE_MAX_MS {
        score += 0.35;
        reason = OpportunityReason::MediumPause;
    } else if input.idle_ms < SHORT_PAUSE_MIN_MS {
        score -= 0.20;
        reason = OpportunityReason::ActiveTyping;
    } else if input.idle_ms < AWAY_IDLE_MS {
        score += 0.15;
        reason = OpportunityReason::LongPause;
    }

    if (SHORT_PAUSE_MIN_MS..=SHORT_PAUSE_MAX_MS).contains(&input.idle_ms)
        && input.f4_burst_length >= 4.0
        && input.f3_correction_rate < 0.20
        && input.f6_pause_after_del_rate < 0.30
    {
        score += 0.25;
        reason = OpportunityReason::PostBurstPause;
    }

    let correction_context =
        input.f3_correction_rate >= 0.20 || input.f6_pause_after_del_rate >= 0.30;
    if correction_context
        && input.idle_ms >= SHORT_PAUSE_MIN_MS
        && input.idle_ms <= MEDIUM_PAUSE_MAX_MS
    {
        score += 0.15;
        reason = OpportunityReason::CorrectionAfterPause;
    } else if correction_context && input.idle_ms < SHORT_PAUSE_MIN_MS {
        score -= 0.20;
        reason = OpportunityReason::ActiveCorrectionLoop;
    }

    (score.clamp(0.0, 1.0), reason)
}

fn reason_for(
    action: InterventionAction,
    need_score: f64,
    opportunity_score: f64,
    opportunity_reason: OpportunityReason,
    thresholds: &InterventionThresholds,
) -> String {
    match action {
        InterventionAction::None if need_score < thresholds.nudge_need => {
            "below_need_threshold".to_string()
        }
        InterventionAction::None => "suppressed_or_away".to_string(),
        InterventionAction::Nudge => opportunity_reason.as_str().to_string(),
        InterventionAction::Wall => "sustained_stuck".to_string(),
        InterventionAction::Defer if opportunity_score < thresholds.nudge_opportunity => {
            "high_need_but_low_opportunity".to_string()
        }
        InterventionAction::Defer => "suppressed".to_string(),
    }
}

fn clean_score(value: f64) -> f64 {
    if value.is_finite() {
        value.clamp(0.0, 1.0)
    } else {
        0.0
    }
}

fn recently(now_ms: u64, at_ms: Option<u64>, window_ms: u64) -> bool {
    at_ms
        .map(|at| now_ms.saturating_sub(at) < window_ms)
        .unwrap_or(false)
}

fn day_index(now_ms: u64) -> u64 {
    now_ms / DAY_MS
}

#[cfg(test)]
mod tests {
    use super::*;

    fn input(now_ms: u64, p_stuck: f64, idle_ms: u64) -> InterventionInput {
        InterventionInput {
            now_ms,
            p_stuck,
            f3_correction_rate: 0.05,
            f4_burst_length: 5.0,
            f6_pause_after_del_rate: 0.0,
            idle_ms,
            monk_mode: false,
            wall_active: false,
        }
    }

    /// 既定閾値が現行 const と byte 一致であること (production 不変の機械的保証)。
    /// 誰かが `Default` を const から切り離して別値をハードコードしたら落ちる。
    #[test]
    fn default_thresholds_equal_production_consts() {
        let t = InterventionThresholds::default();
        assert_eq!(t.nudge_need, NUDGE_NEED_THRESHOLD);
        assert_eq!(t.wall_need, WALL_NEED_THRESHOLD);
        assert_eq!(t.wall_slack, WALL_SLACK_THRESHOLD);
        assert_eq!(t.nudge_opportunity, NUDGE_OPPORTUNITY_THRESHOLD);
        assert_eq!(t.wall_opportunity, WALL_OPPORTUNITY_THRESHOLD);
    }

    /// OpportunityReason::as_str が production の reason 文字列を再生すること。
    #[test]
    fn opportunity_reason_as_str_matches_legacy_strings() {
        use OpportunityReason::*;
        assert_eq!(LowOpportunity.as_str(), "low_opportunity");
        assert_eq!(ShortPause.as_str(), "short_pause");
        assert_eq!(MediumPause.as_str(), "medium_pause");
        assert_eq!(LongPause.as_str(), "long_pause");
        assert_eq!(ActiveTyping.as_str(), "active_typing");
        assert_eq!(PostBurstPause.as_str(), "post_burst_pause");
        assert_eq!(CorrectionAfterPause.as_str(), "correction_after_pause");
        assert_eq!(ActiveCorrectionLoop.as_str(), "active_correction_loop");
    }

    #[test]
    fn nudge_after_short_post_burst_pause() {
        let mut policy = InterventionPolicyState::new(0);
        let result = policy.decide(input(10_000, 0.66, 3_000));
        assert_eq!(result.decision.action, InterventionAction::Nudge);
        assert!(result.decision.opportunity_score >= NUDGE_OPPORTUNITY_THRESHOLD);
        assert_eq!(result.decision.reason, "post_burst_pause");
    }

    #[test]
    fn active_typing_defers_even_with_high_need() {
        let mut policy = InterventionPolicyState::new(0);
        let result = policy.decide(input(10_000, 0.72, 500));
        assert_eq!(result.decision.action, InterventionAction::Defer);
        assert_eq!(result.decision.reason, "high_need_but_low_opportunity");
    }

    #[test]
    fn wall_after_sustained_stuck_and_opportunity() {
        let mut policy = InterventionPolicyState::new(0);
        policy.decide(input(0, 0.75, 3_000));
        let result = policy.decide(input(WALL_ACCUMULATION_MS + 1, 0.75, 3_000));
        assert_eq!(result.decision.action, InterventionAction::Wall);
        assert_eq!(result.decision.reason, "sustained_stuck");
    }

    #[test]
    fn monk_mode_suppresses_wall() {
        let mut policy = InterventionPolicyState::new(0);
        policy.decide(input(0, 0.75, 3_000));
        let mut next = input(WALL_ACCUMULATION_MS + 1, 0.75, 3_000);
        next.monk_mode = true;
        let result = policy.decide(next);
        assert_ne!(result.decision.action, InterventionAction::Wall);
        assert_eq!(result.decision.wall_accum_ms, 0);
    }

    #[test]
    fn nudge_daily_cap_suppresses_new_activations() {
        let mut policy = InterventionPolicyState::new(0);
        for i in 0..NUDGE_DAILY_CAP {
            let t = i as u64 * (NUDGE_COOLDOWN_MS + 1);
            let result = policy.decide(input(t, 0.66, 3_000));
            assert_eq!(result.decision.action, InterventionAction::Nudge);
            policy.decide(input(t + 1, 0.10, 0));
        }

        let t = NUDGE_DAILY_CAP as u64 * (NUDGE_COOLDOWN_MS + 1);
        let result = policy.decide(input(t, 0.66, 3_000));
        assert_eq!(result.decision.action, InterventionAction::Defer);
        assert!(result
            .decision
            .suppressed_by
            .contains(&"daily_cap".to_string()));
    }
}
