import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import PolicySimulation, TaxOpportunity, InformalBusiness, User
from schemas import (
    PolicySimulationCreate,
    PolicySimulation as PolicySimulationSchema,
    PolicyImpactResponse
)
from auth import get_current_user
from security import limiter, sanitize_input

router = APIRouter()

@router.post("/simulate", response_model=PolicyImpactResponse)
@limiter.limit("20/minute")
async def create_policy_simulation(
    request: Request,
    simulation: PolicySimulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create and run a new policy simulation"""
    # Sanitize inputs
    simulation_name = sanitize_input(simulation.simulation_name)
    region = sanitize_input(simulation.region)
    policy_type = sanitize_input(simulation.policy_type)
    
    # Calculate impact percentage
    if simulation.current_collection > 0:
        impact_percentage = ((simulation.projected_collection - simulation.current_collection) / 
                           simulation.current_collection) * 100
    else:
        impact_percentage = 100.0  # If starting from zero
    
    # Generate recommendations based on policy type and impact
    recommendations = generate_policy_recommendations(
        policy_type, impact_percentage, simulation.current_collection, simulation.projected_collection
    )
    
    # Store simulation data
    simulation_data = {
        "policy_parameters": simulation.simulation_data or {},
        "assumptions": {
            "compliance_rate": 0.7,
            "implementation_timeline": "12 months",
            "administrative_cost_percentage": 0.05
        },
        "risk_factors": [
            "Economic downturn could reduce projected revenue",
            "Resistance from informal sector participants",
            "Administrative capacity constraints"
        ]
    }
    
    db_simulation = PolicySimulation(
        simulation_name=simulation_name,
        region=region,
        policy_type=policy_type,
        current_collection=simulation.current_collection,
        projected_collection=simulation.projected_collection,
        impact_percentage=impact_percentage,
        simulation_data=json.dumps(simulation_data)
    )
    
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    
    return PolicyImpactResponse(
        simulation_id=db_simulation.id,
        current_collection=simulation.current_collection,
        projected_collection=simulation.projected_collection,
        impact_percentage=impact_percentage,
        recommendations=recommendations
    )


@router.get("/", response_model=List[PolicySimulationSchema])
@limiter.limit("100/minute")
async def get_policy_simulations(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    region: Optional[str] = Query(None),
    policy_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of policy simulations with optional filters"""
    query = db.query(PolicySimulation)
    
    # Apply filters
    if region:
        region = sanitize_input(region)
        query = query.filter(PolicySimulation.region.ilike(f"%{region}%"))
    
    if policy_type:
        policy_type = sanitize_input(policy_type)
        query = query.filter(PolicySimulation.policy_type.ilike(f"%{policy_type}%"))
    
    simulations = query.offset(skip).limit(limit).all()
    return simulations


@router.get("/compare")
@limiter.limit("30/minute")
async def compare_policy_scenarios(
    request: Request,
    simulation_ids: str = Query(..., description="Comma-separated list of simulation IDs"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare multiple policy simulation scenarios"""
    try:
        sim_ids = [int(id.strip()) for id in simulation_ids.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid simulation IDs format"
        )
    
    if len(sim_ids) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 simulations allowed for comparison"
        )
    
    simulations = db.query(PolicySimulation).filter(PolicySimulation.id.in_(sim_ids)).all()
    
    if len(simulations) != len(sim_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more simulations not found"
        )
    
    # Prepare comparison data
    comparison_data = []
    for sim in simulations:
        comparison_data.append({
            "simulation_id": sim.id,
            "simulation_name": sim.simulation_name,
            "region": sim.region,
            "policy_type": sim.policy_type,
            "current_collection": sim.current_collection,
            "projected_collection": sim.projected_collection,
            "impact_percentage": sim.impact_percentage,
            "net_increase": sim.projected_collection - sim.current_collection,
            "created_at": sim.created_at.isoformat()
        })
    
    # Calculate summary insights
    best_impact = max(comparison_data, key=lambda x: x["impact_percentage"])
    highest_revenue = max(comparison_data, key=lambda x: x["net_increase"])
    
    return {
        "simulations": comparison_data,
        "summary": {
            "total_simulations": len(comparison_data),
            "best_impact_percentage": {
                "simulation_id": best_impact["simulation_id"],
                "simulation_name": best_impact["simulation_name"],
                "impact_percentage": best_impact["impact_percentage"]
            },
            "highest_revenue_increase": {
                "simulation_id": highest_revenue["simulation_id"],
                "simulation_name": highest_revenue["simulation_name"],
                "net_increase": highest_revenue["net_increase"]
            },
            "average_impact": round(sum(s["impact_percentage"] for s in comparison_data) / len(comparison_data), 2)
        }
    }


@router.get("/templates")
@limiter.limit("50/minute")
async def get_policy_templates(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get predefined policy simulation templates"""
    templates = {
        "digital_tax_registration": {
            "name": "Digital Tax Registration Initiative",
            "description": "Implement digital platforms for informal business registration",
            "policy_type": "digitalization",
            "expected_impact_range": "15-30%",
            "implementation_cost": "Medium",
            "timeline": "6-12 months",
            "parameters": {
                "registration_incentives": True,
                "mobile_platform": True,
                "simplified_procedures": True,
                "grace_period_months": 6
            }
        },
        "simplified_tax_regime": {
            "name": "Simplified Tax Regime for SMEs",
            "description": "Introduce simplified tax calculation and payment methods",
            "policy_type": "simplification",
            "expected_impact_range": "20-40%",
            "implementation_cost": "Low",
            "timeline": "3-6 months",
            "parameters": {
                "flat_rate_percentage": 3,
                "turnover_threshold": 100000,
                "quarterly_payments": True,
                "online_filing": True
            }
        },
        "tax_amnesty_program": {
            "name": "Tax Amnesty and Formalization Program",
            "description": "Offer amnesty for past tax liabilities with formalization incentives",
            "policy_type": "amnesty",
            "expected_impact_range": "25-50%",
            "implementation_cost": "Low",
            "timeline": "12-18 months",
            "parameters": {
                "amnesty_period_months": 12,
                "penalty_waiver_percentage": 100,
                "future_compliance_requirements": True,
                "business_support_services": True
            }
        },
        "mobile_tax_collection": {
            "name": "Mobile Money Tax Collection",
            "description": "Integrate tax payments with mobile money platforms",
            "policy_type": "mobile_integration",
            "expected_impact_range": "30-60%",
            "implementation_cost": "Medium",
            "timeline": "9-15 months",
            "parameters": {
                "mobile_money_integration": True,
                "automatic_deduction": False,
                "payment_reminders": True,
                "transaction_fee_subsidy": True
            }
        },
        "property_tax_modernization": {
            "name": "Property Tax Modernization",
            "description": "Use satellite imagery and AI for property tax assessment",
            "policy_type": "modernization",
            "expected_impact_range": "40-80%",
            "implementation_cost": "High",
            "timeline": "18-24 months",
            "parameters": {
                "satellite_assessment": True,
                "ai_valuation": True,
                "online_appeals_process": True,
                "phased_implementation": True
            }
        }
    }
    
    return {"templates": templates}


@router.post("/generate-report/{simulation_id}")
@limiter.limit("10/minute")
async def generate_policy_report(
    request: Request,
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a comprehensive policy impact report"""
    simulation = db.query(PolicySimulation).filter(PolicySimulation.id == simulation_id).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy simulation not found"
        )
    
    # Get related data for the region
    region_businesses = db.query(InformalBusiness).filter(
        InformalBusiness.region.ilike(f"%{simulation.region}%")
    ).count()
    
    region_tax_opportunities = db.query(TaxOpportunity).filter(
        TaxOpportunity.region.ilike(f"%{simulation.region}%")
    ).count()
    
    # Parse simulation data
    try:
        simulation_data = json.loads(simulation.simulation_data) if simulation.simulation_data else {}
    except json.JSONDecodeError:
        simulation_data = {}
    
    # Generate comprehensive report
    report = {
        "executive_summary": {
            "simulation_name": simulation.simulation_name,
            "region": simulation.region,
            "policy_type": simulation.policy_type,
            "current_collection": simulation.current_collection,
            "projected_collection": simulation.projected_collection,
            "revenue_increase": simulation.projected_collection - simulation.current_collection,
            "impact_percentage": simulation.impact_percentage,
            "confidence_level": "Medium"
        },
        "regional_context": {
            "informal_businesses_identified": region_businesses,
            "tax_opportunities_mapped": region_tax_opportunities,
            "economic_profile": f"Region with {region_businesses} identified informal businesses"
        },
        "implementation_plan": {
            "phases": [
                {
                    "phase": 1,
                    "duration": "Months 1-3",
                    "activities": ["Policy design", "Stakeholder consultation", "Legal framework"],
                    "milestones": ["Policy document approved", "Legal amendments passed"]
                },
                {
                    "phase": 2,
                    "duration": "Months 4-6",
                    "activities": ["System development", "Staff training", "Pilot implementation"],
                    "milestones": ["Systems operational", "Staff certified", "Pilot completed"]
                },
                {
                    "phase": 3,
                    "duration": "Months 7-12",
                    "activities": ["Full rollout", "Monitoring", "Adjustments"],
                    "milestones": ["Full implementation", "First review completed"]
                }
            ]
        },
        "risk_assessment": {
            "high_risks": [
                "Political resistance to change",
                "Insufficient administrative capacity"
            ],
            "medium_risks": [
                "Technology adoption challenges",
                "Taxpayer compliance issues"
            ],
            "low_risks": [
                "Minor system integration issues"
            ],
            "mitigation_strategies": [
                "Comprehensive stakeholder engagement",
                "Phased implementation approach",
                "Continuous monitoring and adjustment"
            ]
        },
        "success_metrics": {
            "primary_kpis": [
                "Tax revenue increase",
                "Number of new registrations",
                "Compliance rate improvement"
            ],
            "secondary_kpis": [
                "Administrative efficiency gains",
                "Taxpayer satisfaction scores",
                "Cost-benefit ratio"
            ]
        },
        "recommendations": generate_policy_recommendations(
            simulation.policy_type, 
            simulation.impact_percentage,
            simulation.current_collection,
            simulation.projected_collection
        )
    }
    
    return report


@router.get("/{simulation_id}", response_model=PolicySimulationSchema)
@limiter.limit("100/minute")
async def get_policy_simulation(
    request: Request,
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific policy simulation by ID"""
    simulation = db.query(PolicySimulation).filter(PolicySimulation.id == simulation_id).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy simulation not found"
        )
    
    return simulation


def generate_policy_recommendations(
    policy_type: str, 
    impact_percentage: float, 
    current_collection: float, 
    projected_collection: float
) -> List[str]:
    """Generate policy recommendations based on simulation results"""
    recommendations = []
    
    # Base recommendations
    if impact_percentage > 50:
        recommendations.append("High impact potential - prioritize for immediate implementation")
    elif impact_percentage > 25:
        recommendations.append("Moderate impact - consider phased implementation")
    else:
        recommendations.append("Low impact - review policy parameters or consider alternatives")
    
    # Policy-specific recommendations
    if policy_type.lower() in ["digitalization", "digital"]:
        recommendations.extend([
            "Ensure robust digital infrastructure and internet connectivity",
            "Provide comprehensive digital literacy training for taxpayers",
            "Implement strong cybersecurity measures"
        ])
    elif policy_type.lower() in ["simplification", "simplified"]:
        recommendations.extend([
            "Conduct extensive taxpayer education campaigns",
            "Establish clear guidelines and procedures",
            "Provide multilingual support materials"
        ])
    elif policy_type.lower() == "amnesty":
        recommendations.extend([
            "Set clear eligibility criteria and deadlines",
            "Combine with business formalization support services",
            "Ensure strong enforcement post-amnesty period"
        ])
    elif policy_type.lower() in ["mobile", "mobile_integration"]:
        recommendations.extend([
            "Partner with established mobile money providers",
            "Ensure transaction security and data protection",
            "Provide incentives for mobile payment adoption"
        ])
    
    # Revenue-based recommendations
    revenue_increase = projected_collection - current_collection
    if revenue_increase > 1000000:  # Large revenue increase
        recommendations.append("Allocate additional resources for implementation given high revenue potential")
    
    return recommendations

