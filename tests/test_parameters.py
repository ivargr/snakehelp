from snakehelp import parameters


@parameters
class MyParameters:
    seed: int
    name: str
    ending: str


def test_parameters_decorator():
    assert MyParameters.parameters == ["seed", "name", "ending"]
