from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum
from kuber_data_sync.model.time import DateTime
from datetime import datetime

from typing import Union, Optional

##################### ENUMS ####################

class AdvertiserStatus(Enum):
    ACTIVE = 'ACTIVE'

class CustomizeSpecifyRate(Enum):
    ALL = "ALL"
    CHANNEL = "CHANNEL"
    RATE = "RATE"

class Type(Enum):
    HOUSE_ADVERTISER = "HOUSE_ADVERTISER"
    HOUSE_AGENCY = "HOUSE_AGENCY"
    ADVERTISER = "ADVERTISER"
    AGENCY = "AGENCY"
    AD_NETWORK = "AD_NETWORK"
    PARTNER = "PARTNER"
    CHILD_PUBLISHER = "CHILD_PUBLISHER"
    VIEWABILITY_PROVIDER = "VIEWABILITY_PROVIDER"
    UNKNOWN = "UNKNOWN"

class CreditStatus(Enum):
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    CREDIT_STOP = 'CREDIT_STOP'
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"

class DelegationType(Enum):
    UNKNOWN = "UNKNOWN"
    MANAGE_ACCOUNT = "MANAGE_ACCOUNT"
    MANAGE_INVENTORY = "MANAGE_INVENTORY"

class DelegationStatus(Enum):
    UNKNOWN = "UNKNOWN"
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class AccountStatus(Enum):
    UNKNOWN = "UNKNOWN"
    INVITED = "INVITED"
    DECLINED = "DECLINED"
    PENDING_GOOGLE_APPROVAL = "PENDING_GOOGLE_APPROVAL"
    APPROVED = "APPROVED"
    CLOSED_POLICY_VIOLATION = "CLOSED_POLICY_VIOLATION"
    CLOSED_INVALID_ACTIVITY = "CLOSED_INVALID_ACTIVITY"
    CLOSED_BY_PUBLISHER = "CLOSED_BY_PUBLISHER"
    DISAPPROVED_INELIGIBLE = "DISAPPROVED_INELIGIBLE"
    DISAPPROVED_DUPLICATE_ACCOUNT = "DISAPPROVED_DUPLICATE_ACCOUNT"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"
    DEACTIVATED_BY_AD_MANAGER = "DEACTIVATED_BY_AD_MANAGER"

class OnboardingTask(Enum):
    UNKNOWN = "UNKNOWN"
    BILLING_PROFILE_CREATION = "BILLING_PROFILE_CREATION"
    PHONE_PIN_VERIFICATION = "PHONE_PIN_VERIFICATION"
    AD_MANAGER_ACCOUNT_SETUP = "AD_MANAGER_ACCOUNT_SETUP"

##################### MODELS ###################

class ChildPublisher(BaseModel):
    approvedDelegationType: DelegationType
    proposedDelegationType: DelegationType
    status: DelegationStatus
    accountStatus: AccountStatus
    childNetworkCode: str
    sellerId: str
    proposedRevenueShareMillipercent: str
    onboardingTasks: OnboardingTask

class AppliedLabels(BaseModel):
    labelId: str
    isNegated: bool

    model_config = ConfigDict(
        coerce_numbers_to_str=True
    )

class ViewabilityProvider(BaseModel):
    vendorKey: str
    verificationScriptUrl: str
    verificationParameters: str
    verificationRejectionTrackerUrl: str

class Advertiser(BaseModel):

    externalId: str = Field(alias='id', serialization_alias="externalId")
    name: Optional[str] = None
    # type: Type
    email: Optional[str] = Field(default="")
    advertiserStatus: CreditStatus = Field(alias="creditStatus", serialization_alias="advertiserStatus")
    # appliedLabels: list[AppliedLabels]
    # childPublisher: Union[ChildPublisher, None]
    # appliedTeamIds: list[str]
    # thirdPartyCompanyId: Union[str, None]
    lastModifiedDateTime: datetime

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True
    )

    @field_validator("lastModifiedDateTime", mode='before')
    def zeep_2_dt_obj(cls, value, values):
        return DateTime(**value).date_time_object
    
    
    def model_post_init(self, __context):
        # Force email to always be "N/A"
        self.email = ""