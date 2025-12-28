import json
from enum import Enum
from google.cloud import bigquery
from martech_sdk.utils.nucleus import Nucleus
from martech_sdk.utils import logging
from martech_sdk.configs.mixins import ConfigMixins

############################################# Enums #############################################

class Project:
    MARTECH = 'martech'
    LMN = 'lmn'

class Env:
    DEV = 'dev'
    STAGE = 'stage'
    PROD = 'prod'

class ConfigSource:
    GCS = "gcs"
    LOCAL = "local"
    NUCLEUS = "nucleus"

############################################# Env Details #############################################

ENV_CONFIG_DETAILS = {
    "bucket_name":{
        "dev" :"clwcirsmnp-medianetwork-dev",
        "stage" :"clwcirsmnp-medianetwork-stg",
        "prod" :"clwcirsmnp-medianetwork-prd"
    }
}

############################################# Env Config Entities #############################################

class Subnet(ConfigMixins):
    PROJECT_ID = None
    NETWORK = None

class ServiceAccounts(ConfigMixins):
    MARTECH = None
    LMN = None

class Buckets(ConfigMixins):
    TMP = None
    SOURCE = None
    BRONZE = None

class Certificate(ConfigMixins):
    PATH = None
    FILE_PATH = None

class SecretManagerConfig(ConfigMixins):
    DEFAULT_PROJECT_ID = None
    DEFAULT_SECRET_ID = 'sec-vault'
    DEFAULT_VERSION_ID = 'latest'
    DEFAULT_TTL = '1h'

class VaultConfig(ConfigMixins):
    SERVER = None
    MARTECH_PATH_NAME = "martechmodernization"
    TOKEN_URL = None

class AdapterUIConfig(ConfigMixins):
    SERVER = None
    GCS_CERTS_FILE_PATH = None
    LOCAL_CERTS_FILE_PATH = None
    ANALYTICS_MEASUREMENT_API_ENDPOINT = "marketing-dashboard-api/adapters/write-analytics-measurement"


class PinterestConfig(ConfigMixins):
    SERVER_URL = None
    SCOPE = "ads:read,boards:read,pins:read"
    TOKEN_ENDPOINT = "v5/oauth/token"
    CAMPAIGN_METADATA_ENDPOINT = "v5/ad_accounts/<account_id>/campaigns"
    CAMPAIGN_METRICS_ENDPOINT = "v5/ad_accounts/<account_id>/campaigns/<campaign_id>/reports"
    CAMPAIGN_METRICS_REPORT_ENDPOINT = "v5/ad_accounts/<account_id>/reports"

class MetaConfig(ConfigMixins):
    VAULT_SECRET_PATH = 'martech/onprem/turbo_titans/common/meta'

class VendorConfig(ConfigMixins):
    PINTEREST = PinterestConfig
    META = MetaConfig

class EnvConfig(ConfigMixins):

    ENV = Env.DEV
    CONFIG_GSUTIL_PATH_TEMPLATE = 'gs://<bucket_name>/config/app-config-<env>.json'
    REGION = None
    SUBNET = Subnet
    NETWORK = None
    SERVICE_ACCOUNT = ServiceAccounts
    PROJECT_ID = None
    CERTS = Certificate
    BUCKET = Buckets
    SECRETS = SecretManagerConfig
    VAULT = VaultConfig
    ADAPTER_UI = AdapterUIConfig
    VENDOR = VendorConfig

    @classmethod
    def set_env(cls, env: str | Env):
        if isinstance(env, Enum):
            cls.ENV = env.value
        else:
            cls.ENV = env
        logging.info(f'Environment set to :- {cls.ENV}')

    @classmethod
    def download_file_from_gcs(cls, source, destination, bucket_name=''):

        if bucket_name:
            bucket = bigquery.Client().bucket(bucket_name)

        logging.info(f"Bucket: {bucket}")

        source = cls.get_relative_path(source)
        blob = bucket.blob(source)
        blob.download_to_filename(destination)
        logging.info(f"File {source} downloaded to {destination}.")
        return destination    

    @classmethod
    def download_config_file_from_gcs(cls):
        bucket_name = ENV_CONFIG_DETAILS['bucket_name'][cls.ENV]
        source = cls.CONFIG_GSUTIL_PATH_TEMPLATE.replace('<bucket_name>', bucket_name).replace('<env>', cls.ENV)
        destination = '/'.join(source.split()[3:])
        dest_path = cls.download_file_from_gcs(source, destination, bucket_name='')
        return json.load(open(dest_path))
    
    # @classmethod
    # def load_configs_from_local(cls):
    #     import importlib.resources as pkg_resources
    #     with pkg_resources.files('martech_sdk.configs.env_details').joinpath(f'app-config-{cls.ENV}.json').open('r') as f:
    #         return json.load(f)
        
    @classmethod
    def load_configs_from_nucleus(cls):
        logging.info("Load configs from Nucleus")
        NUCLEUS_HASH = '26010dc639d1942dbbd81da539389ccc'
        application_name = 'martech'
        scope = 'env-configs'
        env_data  = Nucleus.get(env=EnvConfig.ENV, applicationName=application_name, scope=scope, nucleusHash=NUCLEUS_HASH)['data']
        logging.info(f"env_data: {env_data}")
        return env_data
        
    

    @classmethod
    def parse_env_details(cls, env_details: dict):
        cls.REGION = env_details.get('dataproc', {}).get('region', None)

        # Load Subnet
        subnet_info = env_details.get('dataproc', {}).get('subnet', {})
        cls.SUBNET.PROJECT_ID = subnet_info.get('project_id', None)
        cls.SUBNET.NETWORK = subnet_info.get('network', None)
        logging.info(f"Subnet configs set: {cls.SUBNET.describe()}")

        # Load Service Account
        cls.SERVICE_ACCOUNT.MARTECH = env_details.get('service_accounts', {}).get(Project.MARTECH, None)
        logging.info(f"Service Account configs set: {cls.SERVICE_ACCOUNT.describe()}")

        # Load Project ID
        cls.PROJECT_ID = env_details.get('project_id', {}).get(Project.MARTECH, None)
        cls.SECRETS.DEFAULT_PROJECT_ID = cls.PROJECT_ID
        logging.info(f"Project ID configs set: {cls.PROJECT_ID}")
        logging.info(f"Project ID configs set: {cls.SECRETS.DEFAULT_PROJECT_ID}")

        # Load Certificates
        cert_info = env_details.get('certs', {})
        cls.CERTS.PATH = cert_info.get('certs_path', None)
        cls.CERTS.FILE_PATH = cert_info.get('certs_file_path', None)
        logging.info(f"Certificates configs set: {cls.CERTS.describe()}")

        # Load Buckets
        bucket_info = env_details.get('buckets', {}).get(Project.MARTECH, {})
        cls.BUCKET.TMP = bucket_info.get('tmp', None)
        cls.BUCKET.SOURCE = bucket_info.get('source_bucket', None)
        cls.BUCKET.BRONZE = bucket_info.get('bronze', None)
        logging.info(f"Buckets configs set: {cls.BUCKET.describe()}")

        # Load Vault
        vault_info = env_details.get('vault', {})
        cls.VAULT.SERVER = vault_info.get('server_url', None)
        logging.info(f"Vault configs set: {cls.VAULT.describe()}")

        # Load Adapter UI
        adapter_ui_info = env_details.get('adapter_ui', {})
        cls.ADAPTER_UI.SERVER = adapter_ui_info.get('server_url', None)
        cls.ADAPTER_UI.LOCAL_CERTS_FILE_PATH = adapter_ui_info.get('local_certs_file_path', None)
        cls.ADAPTER_UI.GCS_CERTS_FILE_PATH = adapter_ui_info.get('gcs_certs_file_path', None)
        logging.info(f"Adapter UI configs set: {cls.ADAPTER_UI.describe()}")

        # Load Vendor Configs
        # Load Pinterest configs
        vendor_info = env_details.get('vendor', {})
        logging.info(f"Vendor info: {vendor_info}")
        pinterest_info = vendor_info.get('pinterest', {})
        logging.info(f"pinterest_info: {pinterest_info}")
        cls.VENDOR.PINTEREST.SERVER_URL = pinterest_info.get('server_url')

        logging.info("Env configs loaded successfully")

    @classmethod
    def load_configs(cls, env: str | Env=Env.DEV, project: str | Project=Project.MARTECH, source: str=ConfigSource.GCS):
        
        logging.info("Loading Env Configs")
        env_details = None
        if isinstance(project, Enum):
            project = project.value

        cls.set_env(env)

        if source == ConfigSource.GCS:
            env_details = cls.download_config_file_from_gcs()
        # elif source == ConfigSource.LOCAL:
        #     env_details = cls.load_configs_from_local()
        elif source == ConfigSource.NUCLEUS:
            env_details = cls.load_configs_from_nucleus()
        else:
            raise ValueError("Invalid config source")

        cls.parse_env_details(env_details)
        logging.info('Env configs loaded successfully')

    @classmethod
    def add_attribute(cls,key, value):
        """
        create variable in uppercase to maintain uniformity.
        """
        setattr(cls, key, value)
        logging.info(f"{key} set to {eval(f'cls.{value}')}")