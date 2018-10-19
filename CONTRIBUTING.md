# Contributing

<!-- toc -->

- [Environment Setup](#environment-setup)
  * [Requirements](#requirements)
  * [Code and Dependencies](#code-and-dependencies)
  * [Application Settings](#application-settings)
  * [Recommended Setup](#recommended-setup)
- [Local Server](#local-server)
- [Tests](#tests)
- [Git Workflow](#git-workflow)
  * [Updating the Codebase](#updating-the-codebase)
    + [Dependency Changes](#dependency-changes)
    + [Migration Changes](#migration-changes)
  * [Pull Requests](#pull-requests)
    + [Updating a Feature Branch](#updating-a-feature-branch)

<!-- tocstop -->

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

### Application Settings

For a local developer environment, you should create a `.env` file in the root of your project to enable debug mode.

```dotenv
DJANGO_DEBUG=True
```

This file will be read and used to set environment variables when executing commands within the context of `pipenv`.

### Recommended Setup

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

## Local Server

To run a server on your local machine, you must create the appropriate database tables and then you can run the development server.

```bash
pipenv run timetracker/manage.py migrate
pipenv run timetracker/manage.py runserver
```

## Tests

Tests are run using [pytest](https://docs.pytest.org/en/latest/). These tests are run automatically on every push by our CI server. To run them locally, use the command:

```bash
pipenv run pytest timetracker/
```

## Git Workflow

Work should be done on short lived "feature branches". These branches should branch off of the most recent version of `master`, and then be merged back in to `master`, usually as a single commit.

### Updating the Codebase

There are frequent updates to the repository, so you should be updating your local copy often. To do so, simply run `git pull`.

#### Dependency Changes

If you get an error related to a module not being found, you may have to install additional dependencies. Simply run the install command again:

```bash
pipenv install --dev
```

#### Migration Changes

If the changes you pull in have additional database migrations, you will have to migrate your local database again.

```bash
pipenv run timetracker/manage.py migrate
```

*Note: Occasionally backwards incompatible changes to the migrations will happen. In this case, you will have to delete the `timetracker/db.sqlite3` file and run the migrations again. This should be a rare occurrence.*

### Pull Requests

Once you have the basic concept of your change made, you should push your branch to GitHub and open a pull request. This will run our automated testing suite, provide information on test coverage, and more importantly, allow for others to provide feedback on your work. All changes must have at least one approving review before being merged.

#### Updating a Feature Branch

Since there are multiple people working on the project, chances are your feature branch will fall behind the most recent master version. To fix this, you can update your local copy of the master branch and then rebase your feature branch on top of it.

```bash
git checkout master
git pull
git checkout <your-feature-branch>
git rebase master
```

If you rebase a feature branch you have already pushed, you will have to force push it the next time you want to push.

```bash
git push --force
```
