from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import get_db
from models import InformalBusiness, User
from schemas import (
    InformalBusinessCreate, 
    InformalBusiness as InformalBusinessSchema,
    BusinessClusterResponse
)
from auth import get_current_user
from security import limiter, sanitize_input, validate_coordinates

router = APIRouter()

@router.post("/", response_model=InformalBusinessSchema)
@limiter.limit("50/minute")
async def create_business(
    request: Request,
    business: InformalBusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new informal business record"""
    # Validate coordinates
    if not validate_coordinates(business.latitude, business.longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Sanitize inputs
    name = sanitize_input(business.name)
    business_type = sanitize_input(business.business_type)
    region = sanitize_input(business.region)
    
    # Calculate tax potential (simplified calculation)
    tax_potential = (business.estimated_revenue or 0) * 0.15  # 15% tax rate
    
    db_business = InformalBusiness(
        name=name,
        latitude=business.latitude,
        longitude=business.longitude,
        business_type=business_type,
        estimated_revenue=business.estimated_revenue,
        tax_potential=tax_potential,
        region=region,
        confidence_score=0.8  # Default confidence score
    )
    
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    
    return db_business


@router.get("/", response_model=List[InformalBusinessSchema])
@limiter.limit("100/minute")
async def get_businesses(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    region: Optional[str] = Query(None),
    business_type: Optional[str] = Query(None),
    min_revenue: Optional[float] = Query(None, ge=0),
    max_revenue: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of informal businesses with optional filters"""
    query = db.query(InformalBusiness)
    
    # Apply filters
    if region:
        region = sanitize_input(region)
        query = query.filter(InformalBusiness.region.ilike(f"%{region}%"))
    
    if business_type:
        business_type = sanitize_input(business_type)
        query = query.filter(InformalBusiness.business_type.ilike(f"%{business_type}%"))
    
    if min_revenue is not None:
        query = query.filter(InformalBusiness.estimated_revenue >= min_revenue)
    
    if max_revenue is not None:
        query = query.filter(InformalBusiness.estimated_revenue <= max_revenue)
    
    businesses = query.offset(skip).limit(limit).all()
    return businesses


@router.get("/{business_id}", response_model=InformalBusinessSchema)
@limiter.limit("100/minute")
async def get_business(
    request: Request,
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific informal business by ID"""
    business = db.query(InformalBusiness).filter(InformalBusiness.id == business_id).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    return business


@router.get("/clusters/detect", response_model=BusinessClusterResponse)
@limiter.limit("20/minute")
async def detect_business_clusters(
    request: Request,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5.0, ge=0.1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect clusters of informal businesses within a radius"""
    # Simple distance calculation (for production, use PostGIS or similar)
    # This is a simplified implementation
    lat_range = radius_km / 111.0  # Approximate km per degree latitude
    lon_range = radius_km / (111.0 * abs(latitude))  # Adjust for longitude
    
    businesses = db.query(InformalBusiness).filter(
        and_(
            InformalBusiness.latitude.between(latitude - lat_range, latitude + lat_range),
            InformalBusiness.longitude.between(longitude - lon_range, longitude + lon_range)
        )
    ).all()
    
    # Calculate summary statistics
    total_revenue = sum(b.estimated_revenue or 0 for b in businesses)
    total_tax_potential = sum(b.tax_potential or 0 for b in businesses)
    
    # Group by business type
    business_types = {}
    for business in businesses:
        btype = business.business_type
        if btype not in business_types:
            business_types[btype] = {"count": 0, "revenue": 0}
        business_types[btype]["count"] += 1
        business_types[btype]["revenue"] += business.estimated_revenue or 0
    
    region_summary = {
        "total_businesses": len(businesses),
        "total_estimated_revenue": total_revenue,
        "total_tax_potential": total_tax_potential,
        "business_types": business_types,
        "center_coordinates": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km
    }
    
    return BusinessClusterResponse(
        businesses=businesses,
        total_count=len(businesses),
        region_summary=region_summary
    )


@router.put("/{business_id}", response_model=InformalBusinessSchema)
@limiter.limit("30/minute")
async def update_business(
    request: Request,
    business_id: int,
    business_update: InformalBusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an informal business record"""
    db_business = db.query(InformalBusiness).filter(InformalBusiness.id == business_id).first()
    
    if not db_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Validate coordinates
    if not validate_coordinates(business_update.latitude, business_update.longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Update fields
    db_business.name = sanitize_input(business_update.name)
    db_business.latitude = business_update.latitude
    db_business.longitude = business_update.longitude
    db_business.business_type = sanitize_input(business_update.business_type)
    db_business.estimated_revenue = business_update.estimated_revenue
    db_business.region = sanitize_input(business_update.region)
    db_business.tax_potential = (business_update.estimated_revenue or 0) * 0.15
    
    db.commit()
    db.refresh(db_business)
    
    return db_business


@router.delete("/{business_id}")
@limiter.limit("20/minute")
async def delete_business(
    request: Request,
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an informal business record"""
    db_business = db.query(InformalBusiness).filter(InformalBusiness.id == business_id).first()
    
    if not db_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    db.delete(db_business)
    db.commit()
    
    return {"message": "Business deleted successfully"}

