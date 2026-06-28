"""
Configure the tests.

Register the hypothesis 'exhaustive' profile to run 10 thousand examples.
Run this profile with ``pytest --hypothesis-profile=exhaustive``
"""

from hypothesis import HealthCheck
from hypothesis import settings

# suppress differing_executors: _Tests mixin methods are intentionally shared
# between TestLxml and TestPyUppsala — hypothesis sees them as the same function
# running in different class contexts, which is expected and correct.
settings.register_profile(
    "default",
    suppress_health_check=[HealthCheck.differing_executors],
)
settings.load_profile("default")

settings.register_profile(
    "exhaustive",
    max_examples=10_000,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.differing_executors],
)
settings.register_profile(
    "coverage",
    max_examples=10,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.differing_executors],
)
settings.register_profile(
    "ci",
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.differing_executors],
)
