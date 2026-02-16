/// Hidden Markov Model for cognitive state estimation
///
/// This module implements a 3-state HMM to probabilistically estimate the user's
/// cognitive state (FLOW, INCUBATION, STUCK) based on typing patterns.
///
/// The model uses:
/// - **States**: 0=FLOW, 1=INCUBATION, 2=STUCK
/// - **Observations**: flight_time_ms (time between consecutive key presses)
/// - **Transition probabilities**: How likely to move between states
/// - **Emission probabilities**: How likely each observation given a state
///
/// The Forward Algorithm is used to:
/// 1. Calculate observation probability for each state (emission probability)
/// 2. Apply state transition probabilities
/// 3. Normalize to get updated state probabilities
/// 4. Return the most likely current state

use crate::inference::rules::FlowState;

/// Threshold below which observation probability is clamped (prevents log(0))
const MIN_OBSERVATION_PROB: f64 = 1e-10;

/// Represents a Hidden Markov Model with 3 states
///
/// # States
/// - Index 0: FLOW (flowing state, fast typing)
/// - Index 1: INCUBATION (thinking state, moderate delays)
/// - Index 2: STUCK (stuck state, long delays or corrections)
#[derive(Clone, Debug)]
pub struct HMM {
    /// Transition probability matrix [from_state][to_state]
    /// Row i represents probabilities of transitioning FROM state i
    /// Each row sums to 1.0
    transition: [[f64; 3]; 3],

    /// Current state probability distribution
    /// state_probs[i] = P(state_i | observations_so_far)
    /// Always sums to 1.0
    state_probs: [f64; 3],
}

impl HMM {
    /// Creates a new HMM with predefined transition probabilities
    ///
    /// # Transition Matrix Interpretation
    /// - From FLOW (idx 0): [0.85 stay in FLOW, 0.10 → INCUBATION, 0.05 → STUCK]
    /// - From INCUBATION (idx 1): [0.40 → FLOW, 0.45 stay in INCUBATION, 0.15 → STUCK]
    /// - From STUCK (idx 2): [0.30 → FLOW, 0.20 → INCUBATION, 0.50 stay in STUCK]
    ///
    /// # Initial State
    /// The model starts in FLOW state with probability 1.0
    ///
    /// # Returns
    /// A new HMM instance ready to process observations
    pub fn new() -> Self {
        HMM {
            transition: [
                // From FLOW (idx 0): likely to stay in FLOW, small chance to lose focus
                [0.85, 0.10, 0.05],
                // From INCUBATION (idx 1): balanced between states
                [0.40, 0.45, 0.15],
                // From STUCK (idx 2): initially hard to recover, likely to stay stuck
                [0.30, 0.20, 0.50],
            ],
            // Start in FLOW state
            state_probs: [1.0, 0.0, 0.0],
        }
    }

    /// Returns the current state probabilities
    ///
    /// # Returns
    /// A tuple of (flow_prob, incubation_prob, stuck_prob)
    /// Always sums to 1.0
    pub fn state_probs(&self) -> (f64, f64, f64) {
        (self.state_probs[0], self.state_probs[1], self.state_probs[2])
    }

    /// Returns the most likely current cognitive state
    ///
    /// # Returns
    /// The FlowState with highest probability
    pub fn most_likely_state(&self) -> FlowState {
        let max_idx = self.state_probs
            .iter()
            .enumerate()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
            .map(|(idx, _)| idx)
            .unwrap_or(0);

        match max_idx {
            0 => FlowState::Flow,
            1 => FlowState::Incubation,
            _ => FlowState::Stuck,
        }
    }

    /// Resets the HMM to initial state (FLOW with 100% probability)
    pub fn reset(&mut self) {
        self.state_probs = [1.0, 0.0, 0.0];
    }

    /// Updates the HMM with a new observation (flight time in milliseconds)
    ///
    /// Uses the Forward Algorithm:
    /// 1. Calculate observation probabilities P(observation | state) using Gaussian
    /// 2. Multiply current state probabilities by transition matrix
    /// 3. Multiply by observation probabilities
    /// 4. Normalize to sum to 1.0
    ///
    /// # Arguments
    /// * `flight_time` - Flight time in milliseconds (time between key presses)
    /// * `backspace_count` - Number of backspaces in the recent window (may include hesitation effect)
    ///
    /// # Returns
    /// The most likely cognitive state after incorporating the new observation
    pub fn update(&mut self, flight_time: f64, backspace_count: u32) -> FlowState {
        // Calculate observation probabilities for each state using both flight time
        // and backspace frequency (naive-bayes style multiplication)
        let obs_probs = self.calculate_observation_probs(flight_time, backspace_count);

        // Forward algorithm: multiply by transition matrix and observation probs
        let mut new_state_probs = [0.0; 3];

        for to_state in 0..3 {
            let mut prob = 0.0;
            // Sum over all previous states
            for from_state in 0..3 {
                prob += self.state_probs[from_state]
                    * self.transition[from_state][to_state]
                    * obs_probs[to_state];
            }
            new_state_probs[to_state] = prob;
        }

        // Normalize so probabilities sum to 1.0
        let total: f64 = new_state_probs.iter().sum();
        if total > 0.0 {
            for prob in &mut new_state_probs {
                *prob /= total;
            }
        } else {
            // Fallback: equal probabilities
            new_state_probs = [1.0 / 3.0; 3];
        }

        self.state_probs = new_state_probs;
        self.most_likely_state()
    }

    /// Calculates observation probability for each state given the flight time
    ///
    /// Uses Gaussian distribution with state-specific mean and standard deviation:
    /// - FLOW: μ=50ms, σ=30ms (fast typing)
    /// - INCUBATION: μ=250ms, σ=100ms (thinking)
    /// - STUCK: μ=1000ms, σ=500ms (long pauses)
    ///
    /// # Arguments
    /// * `observation` - Flight time in milliseconds
    ///
    /// # Returns
    /// Array of observation probabilities [P(obs|FLOW), P(obs|INCUBATION), P(obs|STUCK)]
    fn calculate_observation_probs(&self, flight_time: f64, backspace_count: u32) -> [f64; 3] {
        // Flight time parameters per state: (mean, std_dev)
        let ft_params = [
            (50.0, 30.0),      // FLOW
            (250.0, 100.0),    // INCUBATION
            (1000.0, 500.0),   // STUCK
        ];

        // Backspace frequency modeled as a continuous proxy (use gaussian on count)
        // Means and std devs chosen so that STUCK favors higher backspace counts
        let bs_params = [
            (0.3, 0.7),   // FLOW: very few deletes
            (1.0, 1.0),   // INCUBATION: occasional deletes
            (3.5, 1.5),   // STUCK: frequent deletes/edits
        ];

        let mut probs = [0.0; 3];
        for idx in 0..3 {
            let (ft_mean, ft_std) = ft_params[idx];
            let (bs_mean, bs_std) = bs_params[idx];

            let p_ft = Self::gaussian_pdf(flight_time, ft_mean, ft_std).max(MIN_OBSERVATION_PROB);
            let p_bs = Self::gaussian_pdf(backspace_count as f64, bs_mean, bs_std).max(MIN_OBSERVATION_PROB);

            // Naive Bayes style: multiply independent observation likelihoods
            probs[idx] = p_ft * p_bs;
        }

        probs
    }

    /// Calculates the probability density function (PDF) of a normal distribution
    ///
    /// Formula: P(x|μ,σ) = (1 / (σ√(2π))) * e^(-(x-μ)² / (2σ²))
    ///
    /// # Arguments
    /// * `x` - Observation value
    /// * `mean` - Mean of the distribution
    /// * `std_dev` - Standard deviation of the distribution
    ///
    /// # Returns
    /// The probability density at x
    fn gaussian_pdf(x: f64, mean: f64, std_dev: f64) -> f64 {
        let coefficient = 1.0 / (std_dev * (2.0 * std::f64::consts::PI).sqrt());
        let exponent = -((x - mean).powi(2)) / (2.0 * std_dev.powi(2));
        coefficient * exponent.exp()
    }
}

impl Default for HMM {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hmm_initialization() {
        let hmm = HMM::new();
        let (flow, incubation, stuck) = hmm.state_probs();
        assert_eq!(flow, 1.0);
        assert_eq!(incubation, 0.0);
        assert_eq!(stuck, 0.0);
        assert_eq!(hmm.most_likely_state(), FlowState::Flow);
    }

    #[test]
    fn test_observation_prob_calculation() {
        let hmm = HMM::new();
        let probs = hmm.calculate_observation_probs(50.0, 0); // Fast typing
        // FLOW should have highest probability for fast typing
        assert!(probs[0] > probs[1]); // FLOW > INCUBATION
        assert!(probs[0] > probs[2]); // FLOW > STUCK
    }

    #[test]
    fn test_update_with_fast_typing() {
        let mut hmm = HMM::new();
        // Simulate fast typing (40ms - typical FLOW state)
        let state = hmm.update(40.0, 0);
        assert_eq!(state, FlowState::Flow);
        let (flow, _, _) = hmm.state_probs();
        assert!(flow > 0.5);
    }

    #[test]
    fn test_update_with_long_pause() {
        let mut hmm = HMM::new();
        // Simulate long pause (2000ms - typical STUCK state)
        let state = hmm.update(2000.0, 0);
        assert_eq!(state, FlowState::Stuck);
        let (_, _, stuck) = hmm.state_probs();
        assert!(stuck > 0.5);
    }

    #[test]
    fn test_probability_normalization() {
        let mut hmm = HMM::new();
        hmm.update(150.0, 0);
        let (flow, incubation, stuck) = hmm.state_probs();
        let sum = flow + incubation + stuck;
        assert!((sum - 1.0).abs() < 1e-9); // Safely close to 1.0
    }

    #[test]
    fn test_gaussian_pdf() {
        // PDF at mean should be maximum
        let at_mean = HMM::gaussian_pdf(50.0, 50.0, 30.0);
        let away_from_mean = HMM::gaussian_pdf(100.0, 50.0, 30.0);
        assert!(at_mean > away_from_mean);
    }
}
