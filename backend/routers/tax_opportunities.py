from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import TaxOpportunity, InformalBusiness, User
from schemas import (
    TaxOpportunityCreate,
    TaxOpportunity as TaxOpportunitySchema,
    TaxEstimateResponse
)
from auth import get_current_user
from security import limiter, sanitize_input

router = APIRouter()

@router.post("/", response_model=TaxOpportunitySchema)
@limiter.limit("30/minute")
async def create_tax_opportunity(
    request: Request,
    opportunity: TaxOpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tax opportunity record"""
    # Sanitize inputs
    region = sanitize_input(opportunity.region)
    sector = sanitize_input(opportunity.sector)
    
    # Calculate impact percentage
    impact_percentage = ((opportunity.projected_collection - opportunity.current_collection) / 
                        opportunity.current_collection * 100) if opportunity.current_collection > 0 else 0
    
    db_opportunity = TaxOpportunity(
        region=region,
        sector=sector,
        estimated_revenue=opportunity.estimated_revenue,
        potential_tax=opportunity.potential_tax,
        business_count=opportunity.business_count,
        confidence_level=0.75  # Default confidence level
    )
    
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    
    return db_opportunity


@router.get("/", response_model=List[TaxOpportunitySchema])
@limiter.limit("100/minute")
async def get_tax_opportunities(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    region: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    min_potential: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of tax opportunities with optional filters"""
    query = db.query(TaxOpportunity)
    
    # Apply filters
    if region:
        region = sanitize_input(region)
        query = query.filter(TaxOpportunity.region.ilike(f"%{region}%"))
    
    if sector:
        sector = sanitize_input(sector)
        query = query.filter(TaxOpportunity.sector.ilike(f"%{sector}%"))
    
    if min_potential is not None:
        query = query.filter(TaxOpportunity.potential_tax >= min_potential)
    
    opportunities = query.offset(skip).limit(limit).all()
    return opportunities


@router.get("/estimate/{region}", response_model=TaxEstimateResponse)
@limiter.limit("50/minute")
async def estimate_tax_potential(
    request: Request,
    region: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estimate tax potential for a specific region"""
    region = sanitize_input(region)
    
    # Get all businesses in the region
    businesses = db.query(InformalBusiness).filter(
        InformalBusiness.region.ilike(f"%{region}%")
    ).all()
    
    if not businesses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No businesses found in region: {region}"
        )
    
    # Calculate totals
    total_potential_tax = sum(b.tax_potential or 0 for b in businesses)
    business_count = len(businesses)
    
    # Calculate confidence score based on data completeness
    complete_records = sum(1 for b in businesses if b.estimated_revenue and b.tax_potential)
    confidence_score = (complete_records / business_count) * 0.9 if business_count > 0 else 0
    
    # Breakdown by sector (business type)
    breakdown_by_sector = {}
    for business in businesses:
        sector = business.business_type
        if sector not in breakdown_by_sector:
            breakdown_by_sector[sector] = {
                "business_count": 0,
                "total_revenue": 0,
                "total_tax_potential": 0
            }
        
        breakdown_by_sector[sector]["business_count"] += 1
        breakdown_by_sector[sector]["total_revenue"] += business.estimated_revenue or 0
        breakdown_by_sector[sector]["total_tax_potential"] += business.tax_potential or 0
    
    return TaxEstimateResponse(
        region=region,
        total_potential_tax=total_potential_tax,
        business_count=business_count,
        confidence_score=confidence_score,
        breakdown_by_sector=breakdown_by_sector
    )


@router.get("/analytics/summary")
@limiter.limit("30/minute")
async def get_tax_analytics_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary analytics for tax opportunities"""
    # Total opportunities
    total_opportunities = db.query(TaxOpportunity).count()
    
    # Total potential tax
    total_potential = db.query(func.sum(TaxOpportunity.potential_tax)).scalar() or 0
    
    # Average confidence level
    avg_confidence = db.query(func.avg(TaxOpportunity.confidence_level)).scalar() or 0
    
    # Top regions by potential
    top_regions = db.query(
        TaxOpportunity.region,
        func.sum(TaxOpportunity.potential_tax).label('total_potential')
    ).group_by(TaxOpportunity.region).order_by(
        func.sum(TaxOpportunity.potential_tax).desc()
    ).limit(10).all()
    
    # Top sectors by potential
    top_sectors = db.query(
        TaxOpportunity.sector,
        func.sum(TaxOpportunity.potential_tax).label('total_potential')
    ).group_by(TaxOpportunity.sector).order_by(
        func.sum(TaxOpportunity.potential_tax).desc()
    ).limit(10).all()
    
    return {
        "summary": {
            "total_opportunities": total_opportunities,
            "total_potential_tax": total_potential,
            "average_confidence": round(avg_confidence, 2)
        },
        "top_regions": [
            {"region": region, "potential_tax": float(potential)}
            for region, potential in top_regions
        ],
        "top_sectors": [
            {"sector": sector, "potential_tax": float(potential)}
            for sector, potential in top_sectors
        ]
    }


@router.get("/{opportunity_id}", response_model=TaxOpportunitySchema)
@limiter.limit("100/minute")
async def get_tax_opportunity(
    request: Request,
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific tax opportunity by ID"""
    opportunity = db.query(TaxOpportunity).filter(TaxOpportunity.id == opportunity_id).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax opportunity not found"
        )
    
    return opportunity


@router.put("/{opportunity_id}", response_model=TaxOpportunitySchema)
@limiter.limit("20/minute")
async def update_tax_opportunity(
    request: Request,
    opportunity_id: int,
    opportunity_update: TaxOpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a tax opportunity record"""
    db_opportunity = db.query(TaxOpportunity).filter(TaxOpportunity.id == opportunity_id).first()
    
    if not db_opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax opportunity not found"
        )
    
    # Update fields
    db_opportunity.region = sanitize_input(opportunity_update.region)
    db_opportunity.sector = sanitize_input(opportunity_update.sector)
    db_opportunity.estimated_revenue = opportunity_update.estimated_revenue
    db_opportunity.potential_tax = opportunity_update.potential_tax
    db_opportunity.business_count = opportunity_update.business_count
    
    db.commit()
    db.refresh(db_opportunity)
    
    return db_opportunity


@router.delete("/{opportunity_id}")
@limiter.limit("10/minute")
async def delete_tax_opportunity(
    request: Request,
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a tax opportunity record"""
    db_opportunity = db.query(TaxOpportunity).filter(TaxOpportunity.id == opportunity_id).first()
    
    if not db_opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax opportunity not found"
        )
    
    db.delete(db_opportunity)
    db.commit()
    
    return {"message": "Tax opportunity deleted successfully"}

