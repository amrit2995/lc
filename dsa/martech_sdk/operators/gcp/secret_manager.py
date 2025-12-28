from google.cloud import secretmanager
from martech_sdk.configs.env import EnvConfig
from martech_sdk.utils import logging
import json

class SecretData:
    def __init__(self, role_id, secret_id):
        role_id = role_id
        secret_id = secret_id

    def __call__(self, key=None):
        if hasattr(self, key):
            return getattr(self, key)
        return {'role_id': self.role_id, 'secret_id': self.secret_id}
    
    def __repr__(self):
        return f"SecretData(role_id={self.role_id}, secret_id={self.secret_id})"

class SecretManagerOperator:
    
    def __init__(self) -> None:
        self._client: secretmanager.SecretManagerServiceClient | None = None

    def get_client(self):
        if not self._client:
            self._client = secretmanager.SecretManagerServiceClient()
        return self._client

    @property
    def client(self):
        return self.get_client()

    def create(self, project_id, secret_id, ttl: str = EnvConfig.SECRETS.DEFAULT_TTL):
        logging.info("Creating secret.")
        parent = self.client.project_path(project_id)

        secret = self.client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}, "ttl": ttl},
            }
        )

        logging.info(f"Created secret: {secret.name}")

    def add_secret_versions(
        self, 
        project_id: str = EnvConfig.SECRETS.DEFAULT_PROJECT_ID, 
        secret_id: str = EnvConfig.SECRETS.DEFAULT_SECRET_ID,
        payload: str | None = None
    ):
        logging.info("Adding secret version.")
        parent = self.client.secret_path(project_id, secret_id)

        secret_version = self.client.add_secret_version(
            request={
                "parent": parent,
                "payload": {
                    "data": payload.encode('UTF-8') if payload else None,
                },
            }
        )

        logging.info(f"Added secret version: {secret_version.name}")

    def list_secret_versions(
        self,
        project_id: str = EnvConfig.SECRETS.DEFAULT_PROJECT_ID,
        secret_id: str = EnvConfig.SECRETS.DEFAULT_SECRET_ID
    ):
        logging.info("Listing secret versions.")
        parent = self.client.secret_path(project_id, secret_id)
        secret_versions = self.client.list_secret_versions(parent=parent)
        logging.info(f"Listed secret versions: {secret_versions}")
        return secret_versions

    def get(
        self,
        project_id: str = EnvConfig.SECRETS.DEFAULT_PROJECT_ID, 
        secret_id: str = EnvConfig.SECRETS.DEFAULT_SECRET_ID,
        version_id: str = EnvConfig.SECRETS.DEFAULT_VERSION_ID
    ):
        logging.info("Fetching secrets from secret manager.")
        logging.info(f"Project ID: {project_id}")
        logging.info(f"Secret ID: {secret_id}")
        logging.info(f"Version ID: {version_id}")
        name = self.client.secret_version_path(project_id, secret_id, version_id)
        logging.info(f"Secret Name: {name}")
        response = self.client.access_secret_version(name=name)
        logging.info(f"Secret Response:- {response}")
        secret_data = response.payload.data.decode('UTF-8')

        parsed_data = json.loads(secret_data)
        role_id = parsed_data.get("role_id")
        secret_id = parsed_data.get("secret_id")
        secret_data = SecretData(role_id=role_id, secret_id=secret_id)
        logging.info("Secrets Fetched from secret manager.")

        return secret_data()