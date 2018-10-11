# Timetracker Web

[![Travis (.com)](https://img.shields.io/travis/com/comp523-jarvis/timetracker-web.svg)](https://travis-ci.com/comp523-jarvis/timetracker-web)

Web app and API for Ulimi time tracker

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

#### `DJANGO_STATIC_ROOT`

Default: `''`

The directory on the filesystem where the application will store static files. This directory must be writeable by the user running the application.

## Development

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for developer documentation.
