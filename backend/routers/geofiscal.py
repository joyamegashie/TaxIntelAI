from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from database import get_db
from models import GeoFiscalData, InformalBusiness, User
from schemas import (
    GeoFiscalDataCreate,
    GeoFiscalData as GeoFiscalDataSchema,
    GeoFiscalHeatmapResponse
)
from auth import get_current_user
from security import limiter, sanitize_input, validate_coordinates

router = APIRouter()

@router.post("/", response_model=GeoFiscalDataSchema)
@limiter.limit("30/minute")
async def create_geofiscal_data(
    request: Request,
    geofiscal_data: GeoFiscalDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new geofiscal intelligence data"""
    # Validate coordinates
    if not validate_coordinates(geofiscal_data.latitude, geofiscal_data.longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Sanitize inputs
    region = sanitize_input(geofiscal_data.region)
    
    db_geofiscal = GeoFiscalData(
        region=region,
        latitude=geofiscal_data.latitude,
        longitude=geofiscal_data.longitude,
        economic_activity_score=geofiscal_data.economic_activity_score,
        business_density=geofiscal_data.business_density,
        tax_collection_rate=geofiscal_data.tax_collection_rate,
        informal_economy_percentage=geofiscal_data.informal_economy_percentage
    )
    
    db.add(db_geofiscal)
    db.commit()
    db.refresh(db_geofiscal)
    
    return db_geofiscal


@router.get("/", response_model=List[GeoFiscalDataSchema])
@limiter.limit("100/minute")
async def get_geofiscal_data(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    region: Optional[str] = Query(None),
    min_activity_score: Optional[float] = Query(None, ge=0, le=1),
    max_activity_score: Optional[float] = Query(None, ge=0, le=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get geofiscal intelligence data with optional filters"""
    query = db.query(GeoFiscalData)
    
    # Apply filters
    if region:
        region = sanitize_input(region)
        query = query.filter(GeoFiscalData.region.ilike(f"%{region}%"))
    
    if min_activity_score is not None:
        query = query.filter(GeoFiscalData.economic_activity_score >= min_activity_score)
    
    if max_activity_score is not None:
        query = query.filter(GeoFiscalData.economic_activity_score <= max_activity_score)
    
    geofiscal_data = query.offset(skip).limit(limit).all()
    return geofiscal_data


@router.get("/heatmap", response_model=GeoFiscalHeatmapResponse)
@limiter.limit("50/minute")
async def get_geofiscal_heatmap(
    request: Request,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(50.0, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate geofiscal intelligence heatmap data for a region"""
    # Calculate coordinate bounds
    lat_range = radius_km / 111.0  # Approximate km per degree latitude
    lon_range = radius_km / (111.0 * abs(latitude))  # Adjust for longitude
    
    # Get geofiscal data within radius
    geofiscal_data = db.query(GeoFiscalData).filter(
        and_(
            GeoFiscalData.latitude.between(latitude - lat_range, latitude + lat_range),
            GeoFiscalData.longitude.between(longitude - lon_range, longitude + lon_range)
        )
    ).all()
    
    # Calculate summary statistics
    if geofiscal_data:
        avg_activity_score = sum(d.economic_activity_score for d in geofiscal_data) / len(geofiscal_data)
        avg_business_density = sum(d.business_density for d in geofiscal_data) / len(geofiscal_data)
        avg_tax_collection = sum(d.tax_collection_rate for d in geofiscal_data) / len(geofiscal_data)
        avg_informal_economy = sum(d.informal_economy_percentage for d in geofiscal_data) / len(geofiscal_data)
        
        # Find hotspots (top 20% by economic activity)
        sorted_data = sorted(geofiscal_data, key=lambda x: x.economic_activity_score, reverse=True)
        hotspot_count = max(1, len(sorted_data) // 5)
        hotspots = sorted_data[:hotspot_count]
    else:
        avg_activity_score = 0
        avg_business_density = 0
        avg_tax_collection = 0
        avg_informal_economy = 0
        hotspots = []
    
    summary_stats = {
        "total_regions": len(geofiscal_data),
        "average_economic_activity_score": round(avg_activity_score, 3),
        "average_business_density": round(avg_business_density, 3),
        "average_tax_collection_rate": round(avg_tax_collection, 3),
        "average_informal_economy_percentage": round(avg_informal_economy, 3),
        "economic_hotspots": len(hotspots),
        "search_center": {"latitude": latitude, "longitude": longitude},
        "search_radius_km": radius_km
    }
    
    return GeoFiscalHeatmapResponse(
        regions=geofiscal_data,
        summary_stats=summary_stats
    )


@router.get("/analytics/regional-comparison")
@limiter.limit("30/minute")
async def get_regional_comparison(
    request: Request,
    regions: str = Query(..., description="Comma-separated list of regions to compare"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare geofiscal metrics across multiple regions"""
    region_list = [sanitize_input(r.strip()) for r in regions.split(",")]
    
    if len(region_list) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 regions allowed for comparison"
        )
    
    comparison_data = {}
    
    for region in region_list:
        # Get data for this region
        region_data = db.query(GeoFiscalData).filter(
            GeoFiscalData.region.ilike(f"%{region}%")
        ).all()
        
        if region_data:
            # Calculate averages for this region
            avg_activity = sum(d.economic_activity_score for d in region_data) / len(region_data)
            avg_density = sum(d.business_density for d in region_data) / len(region_data)
            avg_collection = sum(d.tax_collection_rate for d in region_data) / len(region_data)
            avg_informal = sum(d.informal_economy_percentage for d in region_data) / len(region_data)
            
            comparison_data[region] = {
                "data_points": len(region_data),
                "economic_activity_score": round(avg_activity, 3),
                "business_density": round(avg_density, 3),
                "tax_collection_rate": round(avg_collection, 3),
                "informal_economy_percentage": round(avg_informal, 3),
                "tax_gap_estimate": round((1 - avg_collection) * avg_informal * 100, 2)
            }
        else:
            comparison_data[region] = {
                "data_points": 0,
                "economic_activity_score": 0,
                "business_density": 0,
                "tax_collection_rate": 0,
                "informal_economy_percentage": 0,
                "tax_gap_estimate": 0,
                "note": "No data available for this region"
            }
    
    return {
        "regions_compared": region_list,
        "comparison_data": comparison_data,
        "insights": {
            "highest_activity": max(comparison_data.keys(), 
                                  key=lambda x: comparison_data[x]["economic_activity_score"]),
            "highest_tax_gap": max(comparison_data.keys(), 
                                 key=lambda x: comparison_data[x]["tax_gap_estimate"]),
            "best_collection_rate": max(comparison_data.keys(), 
                                      key=lambda x: comparison_data[x]["tax_collection_rate"])
        }
    }


@router.get("/predict/tax-potential")
@limiter.limit("20/minute")
async def predict_tax_potential(
    request: Request,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    economic_activity_score: float = Query(..., ge=0, le=1),
    business_density: float = Query(..., ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Predict tax potential for a location based on economic indicators"""
    # Simple prediction model (in production, use ML models)
    base_tax_rate = 0.15  # 15% base tax rate
    
    # Adjust based on economic activity and business density
    activity_multiplier = 1 + (economic_activity_score - 0.5)  # Range: 0.5 to 1.5
    density_multiplier = min(2.0, 1 + (business_density / 100))  # Cap at 2x
    
    # Estimate potential annual tax collection per square km
    estimated_revenue_per_km2 = business_density * 50000 * economic_activity_score  # $50k avg per business
    potential_tax_per_km2 = estimated_revenue_per_km2 * base_tax_rate * activity_multiplier * density_multiplier
    
    # Get similar regions for comparison
    similar_regions = db.query(GeoFiscalData).filter(
        and_(
            GeoFiscalData.economic_activity_score.between(
                economic_activity_score - 0.1, economic_activity_score + 0.1
            ),
            GeoFiscalData.business_density.between(
                business_density - 20, business_density + 20
            )
        )
    ).limit(5).all()
    
    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "input_parameters": {
            "economic_activity_score": economic_activity_score,
            "business_density": business_density
        },
        "predictions": {
            "estimated_revenue_per_km2": round(estimated_revenue_per_km2, 2),
            "potential_tax_per_km2": round(potential_tax_per_km2, 2),
            "confidence_level": 0.7,  # Based on model accuracy
            "collection_efficiency_needed": round(base_tax_rate * 100, 1)
        },
        "similar_regions": [
            {
                "region": region.region,
                "activity_score": region.economic_activity_score,
                "business_density": region.business_density,
                "current_collection_rate": region.tax_collection_rate
            }
            for region in similar_regions
        ]
    }


@router.get("/{data_id}", response_model=GeoFiscalDataSchema)
@limiter.limit("100/minute")
async def get_geofiscal_data_by_id(
    request: Request,
    data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific geofiscal data by ID"""
    geofiscal_data = db.query(GeoFiscalData).filter(GeoFiscalData.id == data_id).first()
    
    if not geofiscal_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geofiscal data not found"
        )
    
    return geofiscal_data


@router.put("/{data_id}", response_model=GeoFiscalDataSchema)
@limiter.limit("20/minute")
async def update_geofiscal_data(
    request: Request,
    data_id: int,
    geofiscal_update: GeoFiscalDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update geofiscal intelligence data"""
    db_geofiscal = db.query(GeoFiscalData).filter(GeoFiscalData.id == data_id).first()
    
    if not db_geofiscal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geofiscal data not found"
        )
    
    # Validate coordinates
    if not validate_coordinates(geofiscal_update.latitude, geofiscal_update.longitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates"
        )
    
    # Update fields
    db_geofiscal.region = sanitize_input(geofiscal_update.region)
    db_geofiscal.latitude = geofiscal_update.latitude
    db_geofiscal.longitude = geofiscal_update.longitude
    db_geofiscal.economic_activity_score = geofiscal_update.economic_activity_score
    db_geofiscal.business_density = geofiscal_update.business_density
    db_geofiscal.tax_collection_rate = geofiscal_update.tax_collection_rate
    db_geofiscal.informal_economy_percentage = geofiscal_update.informal_economy_percentage
    
    db.commit()
    db.refresh(db_geofiscal)
    
    return db_geofiscal


@router.delete("/{data_id}")
@limiter.limit("10/minute")
async def delete_geofiscal_data(
    request: Request,
    data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete geofiscal intelligence data"""
    db_geofiscal = db.query(GeoFiscalData).filter(GeoFiscalData.id == data_id).first()
    
    if not db_geofiscal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geofiscal data not found"
        )
    
    db.delete(db_geofiscal)
    db.commit()
    
    return {"message": "Geofiscal data deleted successfully"}

