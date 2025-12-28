from martech_sdk.configs.mixins import ConfigMixins

class LMNAccount(ConfigMixins):
    ACCOUNT_TYPE = "lmn"
    PINTEREST_ID = "549764189253"

class EnterpriseAccount(ConfigMixins):
    ACCOUNT_TYPE = "enterprise"
    PINTEREST_ID = "549755856460"