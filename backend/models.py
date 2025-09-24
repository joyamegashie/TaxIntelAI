from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InformalBusiness(Base):
    __tablename__ = "informal_businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    business_type = Column(String)
    estimated_revenue = Column(Float)
    tax_potential = Column(Float)
    region = Column(String)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    confidence_score = Column(Float)


class TaxOpportunity(Base):
    __tablename__ = "tax_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)
    sector = Column(String)
    estimated_revenue = Column(Float)
    potential_tax = Column(Float)
    business_count = Column(Integer)
    confidence_level = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PolicySimulation(Base):
    __tablename__ = "policy_simulations"

    id = Column(Integer, primary_key=True, index=True)
    simulation_name = Column(String)
    region = Column(String)
    policy_type = Column(String)
    current_collection = Column(Float)
    projected_collection = Column(Float)
    impact_percentage = Column(Float)
    simulation_data = Column(Text)  # JSON data
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GeoFiscalData(Base):
    __tablename__ = "geofiscal_data"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    economic_activity_score = Column(Float)
    business_density = Column(Float)
    tax_collection_rate = Column(Float)
    informal_economy_percentage = Column(Float)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
