from gymnasium.envs.registration import register
from envs import StkEnv

register(
    id="STKEnv-v0",
    entry_point = StkEnv
)