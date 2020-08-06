from typing import List, Optional
from pydantic import BaseModel, IPvAnyAddress, SecretStr


class PointBase(BaseModel):
    x: int
    y: int


class PointUpdate(PointBase):
    pass


class PointCreate(BaseModel):
    position: str


class Point(PointBase):
    id: int
    first: bool = False
    last: bool = False

    class Config:
        orm_mode = True


class CurveBase(BaseModel):
    name: str
    kind: str


class CurveCreate(CurveBase):
    offset: float = 0
    count: int = 2


class CurveUpdate(BaseModel):
    name: Optional[str]
    offset: Optional[float]


class Curve(CurveBase):
    id: int
    default: bool
    offset: float
    points: List[Point]

    class Config:
        orm_mode = True


class HeaderBase(BaseModel):
    name: str
    value: str


class HeaderCreate(HeaderBase):
    webhook_id: int


class HeaderUpdate(HeaderBase):
    pass


class Header(HeaderBase):
    id: int

    class Config:
        orm_mode = True


class WebhookBase(BaseModel):
    on: bool
    name: Optional[str]
    url: Optional[str]
    body: Optional[str]
    method: Optional[str]


class WebhookUpdate(WebhookBase):
    lights: Optional[List[int]]
    groups: Optional[List[int]]


class Webhook(WebhookBase):
    id: int
    header: Optional[List[Header]]
    lights: Optional[List['LightInfo']]
    groups: Optional[List['GroupInfo']]

    class Config:
        orm_mode = True


class StatusBase(BaseModel):
    status: bool


class StatusCreate(StatusBase):
    pass


class Status(StatusBase):
    id: int

    class Config:
        orm_mode = True


class SettingsBase(BaseModel):
    smart_off: bool


class SettingsUpdate(SettingsBase):
    pass


class Settings(SettingsBase):
    id: int

    class Config:
        orm_mode = True


class LightBase(BaseModel):
    id: int
    name: str
    type: str
    modelid: str
    manufacturername: str
    productname: str
    on: bool


class LightUpdate(BaseModel):
    on: Optional[bool]
    on_controlled: Optional[bool]
    on_threshold: Optional[float]
    ct_controlled: Optional[bool]
    bri_controlled: Optional[bool]
    bri_max: Optional[float]
    bri_curve_id: Optional[int]
    ct_curve_id: Optional[int]


class LightInfo(LightBase):
    class Config:
        orm_mode = True


class Light(LightBase):
    on_controlled: bool
    on_threshold: float
    bri_controlled: bool
    bri_max: float
    ct_controlled: bool
    bri_curve: Optional[Curve]
    ct_curve: Optional[Curve]

    class Config:
        orm_mode = True


class GroubBase(BaseModel):
    id: int
    name: str
    type: str


class GroupInfo(BaseModel):
    id: int
    name: str
    type: str
    lights: List[LightInfo]

    class Config:
        orm_mode = True


class Group(BaseModel):
    id: int
    name: str
    type: str
    lights: List[Light]

    class Config:
        orm_mode = True


class PositionBase(BaseModel):
    position: int
    visible: bool


class PositionUpdate(BaseModel):
    visible: bool


class PositionMove(BaseModel):
    move_from: int
    move_to: int


class Position(PositionBase):
    id: int
    light: Optional[LightInfo]
    group: Optional[GroupInfo]

    class Config:
        orm_mode = True


class BridgeBase(BaseModel):
    ipaddress: IPvAnyAddress


class BridgeCreate(BridgeBase):
    pass


class BridgeDiscovery(BaseModel):
    id: str
    internalipaddress: IPvAnyAddress
    macaddress: Optional[str]
    name: Optional[str]


class BridgeSync(BaseModel):
    lights: int
    groups: int


class Bridge(BridgeBase):
    id: str
    name: str
    username: SecretStr

    class Config:
        orm_mode = True


Webhook.update_forward_refs()
