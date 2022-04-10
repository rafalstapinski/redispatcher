import tomli

import redispatcher


def assert_versions_equal():

    with open("pyproject.toml", "rb") as pyproject:
        toml = tomli.load(pyproject)

    assert (
        redispatcher.__version__ == toml["tool"]["poetry"]["version"]
    ), "pyproject.toml and redispatcher.__version__ mismatch"


if __name__ == "__main__":
    assert_versions_equal()
