from config.security_config import (
    KEYCLOAK_PUBLIC_KEY_URL,
    KEYCLOAK_AUTHORIZATION_URL,
    KEYCLOAK_TOKEN_URL,
    SECURITY_TYPE,
)
from services.security_service.implementation.keycloak import (
    Keycloak,
)
from services.security_service.security_data_models import (
    UserData,
    ClientRoles,
)
from services.security_service.security_interface import (
    SecurityInterface,
)


class DisabledSecurity(SecurityInterface):
    async def __call__(self, request) -> UserData:
        return UserData(
            id=None,
            audience=None,
            name="Anonymous",
            preferred_name="Anonymous",
            realm_access=ClientRoles(
                name="realm_access",
                roles=["__admin"],
            ),
            resource_access=None,
            groups=None,
        )


def get_disabled() -> SecurityInterface:
    return DisabledSecurity()


class SecurityFactory:
    @staticmethod
    def add_security():
        match SECURITY_TYPE:
            case "KEYCLOAK":
                keycloak_public_url = (
                    KEYCLOAK_PUBLIC_KEY_URL
                )
                token_url = KEYCLOAK_TOKEN_URL
                authorization_url = (
                    KEYCLOAK_AUTHORIZATION_URL
                )
                refresh_url = authorization_url
                scopes = {
                    "profile": "Read claims that represent basic profile information"
                }

                return Keycloak(
                    keycloak_public_url=keycloak_public_url,
                    token_url=token_url,
                    authorization_url=authorization_url,
                    refresh_url=refresh_url,
                    scopes=scopes,
                )

            case _:
                return get_disabled()


oauth2_scheme = SecurityFactory().add_security()
