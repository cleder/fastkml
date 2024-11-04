"""
Configure the tests.

Register the hypothesis 'exhaustive' profile to run 10 thousand examples.
Run this profile with ``pytest --hypothesis-profile=exhaustive``
"""

from hypothesis import HealthCheck
from hypothesis import settings

settings.register_profile(
    "exhaustive",
    max_examples=10_000,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile(
    "coverage",
    max_examples=10,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile("ci", suppress_health_check=[HealthCheck.too_slow])
