from kuber_data_sync.service.ad_unit import AdUnit
from kuber_data_sync.service.creative import Creative
from kuber_data_sync.service.advertiser import Advertiser
from kuber_data_sync.service.audience_segment import AudienceSegment
from kuber_data_sync.service.creative_template import CreativeTemplate
from kuber_data_sync.service.lineitem_creative_association import LineItemCreativeAssociation
from kuber_data_sync.service.trafficker import Trafficker
from kuber_data_sync.service.label import Label
from kuber_data_sync.service.placement import Placement
from kuber_data_sync.service.order import Order
from kuber_data_sync.service.custom_targeting_key import CustomTargetingKey
from kuber_data_sync.service.custom_targeting_value import CustomTargetingValue
from kuber_data_sync.service.lineitem import LineItem
from kuber_data_sync.service.geo_target import GeoTarget
from kuber_data_sync.service.bandwidth_group import BandwidthGroup
from kuber_data_sync.service.package import Package

__all__ = [
    "AdUnit",
    "Creative",
    "Advertiser",
    "AudienceSegment",
    "CreativeTemplate",
    "LineItemCreativeAssociation",
    "Trafficker",
    "Label",
    "Placement",
    "Order",
    "CustomTargetingKey",
    "CustomTargetingValue",
    "LineItem",
    "GeoTarget",
    "BandwidthGroup",
    "Package"
]

ENTITY_CLASS_MAP = {cls.__name__: cls for cls in [eval(name) for name in __all__]}
