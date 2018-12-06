# Timetracker Web

[![Travis (.com)](https://img.shields.io/travis/com/comp523-jarvis/timetracker-web.svg)](https://travis-ci.com/comp523-jarvis/timetracker-web)
[![Codecov](https://img.shields.io/codecov/c/github/comp523-jarvis/timetracker-web.svg)](https://codecov.io/gh/comp523-jarvis/timetracker-web)

Web app and API for Ulimi time tracker.

**Important Links**
Deployed App
  https://ulimiapps.com
  
Documentation
  https://timetracker-web.readthedocs.io/en/latest/

<!-- toc -->

- [Deployment](#deployment)
  * [Environment Variables](#environment-variables)
    + [`DJANGO_ALLOWED_HOSTS`](#django_allowed_hosts)
    + [`DJANGO_DB_HOST`](#django_db_host)
    + [`DJANGO_DB_NAME`](#django_db_name)
    + [`DJANGO_DB_PASSWORD`](#django_db_password)
    + [`DJANGO_DB_PORT`](#django_db_port)
    + [`DJANGO_DB_USER`](#django_db_user)
    + [`DJANGO_DEBUG`](#django_debug)
    + [`DJANGO_MEDIA_ROOT`](#django_media_root)
    + [`DJANGO_SECRET_KEY`](#django_secret_key)
    + [`DJANGO_STATIC_ROOT`](#django_static_root)
- [Development](#development)

<!-- tocstop -->

## Deployment

See [the deployment repository](https://github.com/comp523-jarvis/timetracker-web-deployment) for an example of how to deploy the application.

### Environment Variables

The following environment variables can be used to modify the application's behavior.

*Note: To use Postgres for the database, all of `DJANGO_DB_NAME`, `DJANGO_DB_PASSWORD`, and `DJANGO_DB_USER` must be set.*

#### `DJANGO_ALLOWED_HOSTS`

Default: `''`

This is a comma separated list of hostnames that are permitted to access the site. This must be set if `DJANGO_DEBUG` is `false`. See [the documentation](https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-ALLOWED_HOSTS) for information on what values are permitted and how they affect the application's behavior.

#### `DJANGO_DB_HOST`

Default: `localhost`

The hostname of the Postgres database to run the application on.

#### `DJANGO_DB_NAME`

Default: `''`

The name of the database to store the application's data in.

#### `DJANGO_DB_PASSWORD`

Default: `''`

The password of the user that the application uses to connect to Postgres.

#### `DJANGO_DB_PORT`

Default: `5432`

The port to connect to the Postgres database on.

#### `DJANGO_DB_USER`

Default: `''`

The name of the user that the application uses to connect to Postgres.

#### `DJANGO_DEBUG`

Default: `false`

Set to `true` (case insensitive) to enable Django's debug mode. See [the documentation](https://docs.djangoproject.com/en/2.1/ref/settings/#debug) for specifics.

#### `DJANGO_MEDIA_ROOT`

Default: `''`

The directory on the filesystem where the application will store user-uploaded files. This directory must be writeable by the user running the application.

#### `DJANGO_SECRET_KEY`

Default: `''`

Set the key Django uses for certain security operations. This must be set if `DJANGO_DEBUG` is `false`. See [the documentation](https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SECRET_KEY) for details on the operations that the secret key is used for. 

#### `DJANGO_SES_ENABLED`

Default: `false`

Set to `true` (case insensitive) to enable sending emails through AWS SES. If this is enabled, the server process needs to have access to AWS credentials allowing SES access. The easiest ways to accomplish this are running the server on an EC2 instance with a role that allows access or by providing `AWS_ACCESS_KEY_ID` and `AWS_SECRET_KEY` environment variables to the server process.

#### `DJANGO_STATIC_ROOT`

Default: `''`

The directory on the filesystem where the application will store static files. This directory must be writeable by the user running the application.

## Development

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for developer documentation.
