# Contributing

## Environment Setup

### Requirements

Before starting the development process, you must have the following tools installed on your system:

* [Git](https://git-scm.com/)
* [Python 3.6](https://www.python.org/downloads/)
* [Pipenv](https://pipenv.readthedocs.io/en/latest/)

*Note: If you are used to creating a virtual environment for python projects, that step can be skipped because it is handled by pipenv.*

### Code and Dependencies

The code is available in the GitHub repository [comp523-jarvis/timetracker-web](https://github.com/comp523-jarvis/timetracker-web). Our first step is to clone the repository and install the requirements.

```bash
git clone git@github.com:comp523-jarvis/timetracker-web
# Or, if you don't have an SSH key on GitHub
git clone https://github.com/comp523-jarvis/timetracker-web

# Next 'cd' into the project directory
cd timetracker-web

# Finally, install the requirements
pipenv install --dev
```

#### Recommended Setup

All code is linted, or checked for style, by [flake8](http://flake8.pycqa.org/en/latest/) on every push. To prevent yourself from pushing code with style violations, we recommend setting up the flake8 git hook.

```bash
pipenv run flake8 --install-hook git
git config flake8.lazy true
git config flake8.strict true
```

This creates a hook that will lint your changed code before each commit, and reject your commit if the check fails. If you're curious, the git configuration options do two things. The `flake8.lazy` flag means that only changed code is checked, and the `flake8.strict` flag means the commit is actually rejected rather than a warning being produced. If you want to run the linter outside of the commit process, use the command:

```bash
pipenv run flake8
```

## Tests

Tests are run using [pytest](https://docs.pytest.org/en/latest/). These tests are run automatically on every push by our CI server. To run them locally, use the command:

```bash
pipenv run pytest timetracker/
```
