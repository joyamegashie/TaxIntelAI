from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Informal Business schemas
class InformalBusinessBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    business_type: str
    estimated_revenue: Optional[float] = None
    region: str


class InformalBusinessCreate(InformalBusinessBase):
    pass


class InformalBusiness(InformalBusinessBase):
    id: int
    tax_potential: Optional[float] = None
    detected_at: datetime
    confidence_score: Optional[float] = None
    
    class Config:
        from_attributes = True


# Tax Opportunity schemas
class TaxOpportunityBase(BaseModel):
    region: str
    sector: str
    estimated_revenue: float
    potential_tax: float
    business_count: int


class TaxOpportunityCreate(TaxOpportunityBase):
    pass


class TaxOpportunity(TaxOpportunityBase):
    id: int
    confidence_level: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Policy Simulation schemas
class PolicySimulationBase(BaseModel):
    simulation_name: str
    region: str
    policy_type: str
    current_collection: float
    projected_collection: float


class PolicySimulationCreate(PolicySimulationBase):
    simulation_data: Optional[dict] = None


class PolicySimulation(PolicySimulationBase):
    id: int
    impact_percentage: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# GeoFiscal Data schemas
class GeoFiscalDataBase(BaseModel):
    region: str
    latitude: float
    longitude: float
    economic_activity_score: float
    business_density: float
    tax_collection_rate: float
    informal_economy_percentage: float


class GeoFiscalDataCreate(GeoFiscalDataBase):
    pass


class GeoFiscalData(GeoFiscalDataBase):
    id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True


# API Response schemas
class BusinessClusterResponse(BaseModel):
    businesses: List[InformalBusiness]
    total_count: int
    region_summary: dict


class TaxEstimateResponse(BaseModel):
    region: str
    total_potential_tax: float
    business_count: int
    confidence_score: float
    breakdown_by_sector: dict


class GeoFiscalHeatmapResponse(BaseModel):
    regions: List[GeoFiscalData]
    summary_stats: dict


class PolicyImpactResponse(BaseModel):
    simulation_id: int
    current_collection: float
    projected_collection: float
    impact_percentage: float
    recommendations: List[str]

