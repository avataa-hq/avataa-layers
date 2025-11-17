# Layers

## Environment variables

```toml
DB_HOST=<pgbouncer/postgres_host>
DB_NAME=<pgbouncer/postgres_layers_db_name>
DB_PASS=<pgbouncer/postgres_layers_password>
DB_PORT=<pgbouncer/postgres_port>
DB_TYPE=postgresql
DB_USER=<pgbouncer/postgres_layers_user>
DEBUG=<True/False>
DOCS_CUSTOM_ENABLED=<True/False>
DOCS_REDOC_JS_URL=<redoc_js_url>
DOCS_SWAGGER_CSS_URL=<swagger_css_url>
DOCS_SWAGGER_JS_URL=<swagger_js_url>
KEYCLOAK_HOST=<keycloak_host>
KEYCLOAK_PORT=<keycloak_port>
KEYCLOAK_PROTOCOL=<keycloak_protocol>
KEYCLOAK_REALM=avataa
KEYCLOAK_REDIRECT_HOST=<keycloak_external_host>
KEYCLOAK_REDIRECT_PORT=<keycloak_external_port>
KEYCLOAK_REDIRECT_PROTOCOL=<keycloak_external_protocol>
MINIO_BUCKET=<minio_layers_bucket>
MINIO_PASSWORD=<minio_layers_password>
MINIO_SECURE=<True/False>
MINIO_URL=<minio_api_host>
MINIO_USER=<minio_layers_user>
SECURITY_TYPE=<security_type>
```

### Compose

- `REGISTRY_URL` - Docker regitry URL, e.g. `harbor.domain.com`
- `PLATFORM_PROJECT_NAME` - Docker regitry project Docker image can be downloaded from, e.g. `avataa`


Export Compliance

This Software, including any source code, technology, and technical data, is distributed under the Apache License, Version 2.0.

Users of this Software are solely responsible for compliance with all applicable national and international laws, regulations, and restrictions pertaining to export, re-export, or import. This includes, but is not limited to, the U.S. Export Administration Regulations (EAR) and restrictions concerning embargoed countries and restricted party lists.

By downloading, accessing, or using this Software, you affirm that:

1.  You are not located in a country that is subject to a U.S. government embargo or has been designated by the U.S. government as a "terrorist supporting" country.
2.  You are not listed on any U.S. government list of prohibited or restricted parties (e.g., the Specially Designated Nationals List or the Denied Persons List).
