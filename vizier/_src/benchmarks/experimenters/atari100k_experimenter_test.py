"""Tests for atari100k."""
from absl import logging

from vizier import pyvizier
from vizier._src.algorithms.designers import random
from vizier._src.benchmarks.experimenters import atari100k_experimenter

from absl.testing import absltest
from absl.testing import parameterized


class Atari100KTest(parameterized.TestCase):

  @absltest.skip("ALE ROMS must be installed manually.")
  @parameterized.parameters('DER', 'DrQ', 'DrQ_eps', 'OTRainbow')
  def test_e2e_evaluation(self, agent_name):
    initial_gin_bindings = {
        'Runner.training_steps': 2,
        'MaxEpisodeEvalRunner.num_eval_episodes': 2,
        'Runner.num_iterations': 2,
        'Runner.max_steps_per_episode': 2,
        'JaxDQNAgent.min_replay_history': 2,
        'OutOfGraphPrioritizedReplayBuffer.replay_capacity': 1000,
    }
    experimenter = atari100k_experimenter.Atari100kExperimenter(
        game_name='Pong',
        agent_name=agent_name,
        initial_gin_bindings=initial_gin_bindings)

    designer = random.RandomDesigner(
        experimenter.problem_statement().search_space, seed=None)

    suggestions = designer.suggest(2)
    trials = [suggestion.to_trial() for suggestion in suggestions]
    evaluated_trials = experimenter.evaluate(trials)
    for evaluated_trial in evaluated_trials:
      self.assertEqual(evaluated_trial.status, pyvizier.TrialStatus.COMPLETED)
      logging.info('Evaluated Trial: %s', evaluated_trial)
      self.assertGreaterEqual(
          evaluated_trial.final_measurement.metrics['eval_average_return']
          .value, 0.0)


if __name__ == '__main__':
  absltest.main()
