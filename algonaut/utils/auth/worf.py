import requests
from .user import User, OrganizationRoles
from .organization import Organization
from .access_token import AccessToken
import flask
import logging

logger = logging.getLogger(__name__)

from . import AuthClient as BaseAuthClient, get_access_token

from typing import Callable, Optional, Dict, Any


def binary_id(uuid: str) -> bytes:
    return bytearray.fromhex(uuid.replace("-", ""))


class AuthClient(BaseAuthClient):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.base_url = config["url"]
        self.version = config["version"]

    def _request(
        self, method: Callable, access_token: str, url: str, **kwargs
    ) -> requests.Response:
        if not "headers" in kwargs:
            kwargs["headers"] = {}
        headers = kwargs["headers"]
        headers["Authorization"] = f"bearer {access_token}"
        full_url = f"{self.base_url}/{self.version}/{url}"
        return method(url=full_url, **kwargs)

    def _get(self, access_token: str, url: str, **kwargs) -> requests.Response:
        return self._request(requests.get, access_token, url, **kwargs)

    def get_user(self, request: flask.Request) -> Optional[User]:
        token = get_access_token(request)
        if not token:
            return None
        try:
            response = self._get(token, "user")
        except requests.ConnectionError:
            logger.error("Cannot connect to authentication backend...")
            return None
        if response.status_code != 200:
            return None
        data = response.json()
        access_token = AccessToken(token=data["access_token"])
        # Each user has a "personal" organization that is linked to his/her user ID.
        org_name = data["user"]["display_name"]
        if not org_name:
            org_name = data["user"]["email"].split("@")[0]
        org_name = org_name.lower()
        personal_organization = Organization(
            name=org_name,
            source="worf_user",
            default=True,
            id=binary_id(data["user"]["id"]),  # we create a binary ID
        )
        org_roles = [
            OrganizationRoles(organization=personal_organization, roles=["superuser"])
        ]
        if data.get("organization"):
            # If the user is associated with a real organization, we also add it.
            organization = Organization(
                name=data["organization"]["name"],
                description=data["organization"].get("description", ""),
                source="worf",
                id=binary_id(data["organization"]["id"]),  # we create a binary ID
            )
            roles = []
            for role in data["organization"]["roles"]:
                if role["confirmed"]:
                    roles.append(role["role"])
            org_roles.append(OrganizationRoles(organization=organization, roles=roles))

        return User(access_token=access_token, organization_roles=org_roles)
