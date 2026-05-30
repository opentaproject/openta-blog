# `.envrc` Setup

This file explains the environment variables used by the Sidecar deployment. Values marked `CHANGEME` should be replaced before running or deploying the app.

```sh
export SCRAM_PASSWORD=SCRAMX
export PGUSER=postgres  # CHANGEME
export PGPASSWORD=postgres # CHANGEME
export POSTGRES_DEFAULT_DB=sidecar0 # CHANGEME
export OPENAI_API_KEY=  # Set if using OPENAI
export SUPERUSER_PASSWORD=XXXXX # CHANGEME
export SUPERUSER=super
export SECRET_KEY=XXXX # CHANGEME
export LTI_KEY=lti-key # CHANGEME
export LTI_SECRET= # CHANGEME
export DISABLE_LTI_VALIDATION=False
export PGDATABASE=default
export HOSTNAME=CHANGEME
```

## Variables

`SCRAM_PASSWORD`

Password used when configuring SCRAM authentication for PostgreSQL-related services.

`PGUSER`

PostgreSQL username used by the application and setup scripts. Change this from the default `postgres` for real deployments.

`PGPASSWORD`

Password for `PGUSER`. Change this from the default `postgres`.

`POSTGRES_DEFAULT_DB`

Initial/default PostgreSQL database name used during database setup.

`OPENAI_API_KEY`

OpenAI API key. Set this only if the deployment uses OpenAI features.

`SUPERUSER_PASSWORD`

Password for the Django superuser created by setup scripts. Change this before deployment.

`SUPERUSER`

Username for the Django superuser. The name of the superuser is hardcoded to `super`

`SECRET_KEY`

Django `SECRET_KEY`. This must be a unique, private value for each deployment.

`LTI_KEY`

Canvas LTI consumer key. The default is `lti-key`; change it if you configure Canvas with a different key.

`LTI_SECRET`

Canvas LTI shared secret. Set this to the same secret configured in Canvas.

`DISABLE_LTI_VALIDATION`

Set to `True` to bypass LTI consumer key and signature validation. The default is `False`, which requires valid Canvas LTI credentials.

`PGDATABASE`

Database name used by Django/PostgreSQL clients. This should always be `default`; the application settings now hardcode this expectation.

`HOSTNAME`

Public hostname for the Sidecar deployment, for example:

```sh
export HOSTNAME=sidecar.example.com
```
