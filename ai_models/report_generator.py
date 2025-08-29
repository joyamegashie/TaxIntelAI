import openai
import os
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    GPT-powered document and report generation for tax intelligence
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Use environment variable or provided API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("No OpenAI API key provided. Report generation will use templates only.")
        
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 2000
    
    def generate_tax_opportunity_report(self, data: Dict) -> str:
        """
        Generate a comprehensive tax opportunity report
        """
        if not self.api_key:
            return self._generate_template_report(data)
        
        try:
            prompt = self._create_tax_opportunity_prompt(data)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a tax policy expert and data analyst specializing in informal economy taxation in African countries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate GPT report: {e}")
            return self._generate_template_report(data)
    
    def _create_tax_opportunity_prompt(self, data: Dict) -> str:
        """
        Create a detailed prompt for tax opportunity report generation
        """
        prompt = f"""
        Generate a comprehensive tax opportunity analysis report based on the following data:

        REGIONAL DATA:
        - Region: {data.get('region', 'Unknown')}
        - Total Businesses Identified: {data.get('business_count', 0)}
        - Estimated Total Revenue: ${data.get('total_revenue', 0):,.2f}
        - Current Tax Collection: ${data.get('current_collection', 0):,.2f}
        - Potential Tax Revenue: ${data.get('potential_tax', 0):,.2f}
        - Tax Gap: ${data.get('tax_gap', 0):,.2f}
        - Collection Efficiency: {data.get('collection_efficiency', 0)*100:.1f}%
        - Compliance Rate: {data.get('compliance_rate', 0)*100:.1f}%

        SECTOR BREAKDOWN:
        {self._format_sector_data(data.get('sectors', []))}

        BUSINESS TYPES IDENTIFIED:
        {self._format_business_types(data.get('business_types', []))}

        Please provide:
        1. Executive Summary (2-3 paragraphs)
        2. Key Findings and Insights
        3. Revenue Opportunity Analysis
        4. Sector-Specific Recommendations
        5. Implementation Priorities
        6. Risk Assessment
        7. Expected Timeline and Milestones

        Format the report professionally with clear headings and actionable recommendations.
        Focus on practical implementation strategies for African tax authorities.
        """
        
        return prompt
    
    def _format_sector_data(self, sectors: List[Dict]) -> str:
        """Format sector data for the prompt"""
        if not sectors:
            return "No sector data available"
        
        formatted = []
        for sector in sectors:
            formatted.append(f"- {sector.get('name', 'Unknown')}: {sector.get('business_count', 0)} businesses, ${sector.get('potential_tax', 0):,.2f} potential tax")
        
        return "\n".join(formatted)
    
    def _format_business_types(self, business_types: List[Dict]) -> str:
        """Format business types for the prompt"""
        if not business_types:
            return "No business type data available"
        
        formatted = []
        for btype in business_types:
            formatted.append(f"- {btype.get('type', 'Unknown')}: {btype.get('count', 0)} businesses")
        
        return "\n".join(formatted)
    
    def generate_policy_impact_report(self, baseline: Dict, projected: Dict, policy_details: Dict) -> str:
        """
        Generate a policy impact assessment report
        """
        if not self.api_key:
            return self._generate_template_policy_report(baseline, projected, policy_details)
        
        try:
            prompt = f"""
            Generate a detailed policy impact assessment report for the following tax policy simulation:

            POLICY DETAILS:
            - Policy Name: {policy_details.get('name', 'Tax Policy Reform')}
            - Policy Type: {policy_details.get('type', 'Unknown')}
            - Target Region: {policy_details.get('region', 'Unknown')}
            - Implementation Timeline: {policy_details.get('timeline', '12 months')}

            BASELINE SCENARIO:
            - Current Tax Collection: ${baseline.get('current_collection', 0):,.2f}
            - Compliance Rate: {baseline.get('compliance_rate', 0)*100:.1f}%
            - Collection Efficiency: {baseline.get('collection_efficiency', 0)*100:.1f}%

            PROJECTED SCENARIO:
            - Projected Tax Collection: ${projected.get('projected_collection', 0):,.2f}
            - Improved Compliance Rate: {projected.get('compliance_rate', 0)*100:.1f}%
            - Improved Collection Efficiency: {projected.get('collection_efficiency', 0)*100:.1f}%
            - Additional Revenue: ${projected.get('additional_revenue', 0):,.2f}
            - Percentage Increase: {projected.get('percentage_increase', 0):.1f}%

            Please provide:
            1. Executive Summary
            2. Policy Overview and Objectives
            3. Impact Analysis (Revenue, Compliance, Efficiency)
            4. Implementation Strategy
            5. Resource Requirements
            6. Risk Assessment and Mitigation
            7. Success Metrics and KPIs
            8. Recommendations for Optimization

            Format as a professional policy brief suitable for government decision-makers.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior tax policy advisor with expertise in African tax systems and informal economy formalization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate policy impact report: {e}")
            return self._generate_template_policy_report(baseline, projected, policy_details)
    
    def generate_business_intelligence_summary(self, business_data: List[Dict]) -> str:
        """
        Generate a business intelligence summary from detected businesses
        """
        if not self.api_key:
            return self._generate_template_business_summary(business_data)
        
        # Aggregate data for analysis
        total_businesses = len(business_data)
        total_revenue = sum(b.get('estimated_revenue', 0) for b in business_data)
        total_tax_potential = sum(b.get('tax_potential', 0) for b in business_data)
        avg_confidence = sum(b.get('confidence_score', 0) for b in business_data) / total_businesses if total_businesses > 0 else 0
        
        # Group by business type
        business_types = {}
        for business in business_data:
            btype = business.get('business_type', 'Unknown')
            if btype not in business_types:
                business_types[btype] = {'count': 0, 'revenue': 0}
            business_types[btype]['count'] += 1
            business_types[btype]['revenue'] += business.get('estimated_revenue', 0)
        
        # Group by region
        regions = {}
        for business in business_data:
            region = business.get('region', 'Unknown')
            if region not in regions:
                regions[region] = {'count': 0, 'revenue': 0}
            regions[region]['count'] += 1
            regions[region]['revenue'] += business.get('estimated_revenue', 0)
        
        try:
            prompt = f"""
            Analyze the following informal business intelligence data and provide strategic insights:

            OVERALL STATISTICS:
            - Total Businesses Detected: {total_businesses}
            - Total Estimated Revenue: ${total_revenue:,.2f}
            - Total Tax Potential: ${total_tax_potential:,.2f}
            - Average AI Confidence: {avg_confidence*100:.1f}%

            BUSINESS TYPE DISTRIBUTION:
            {self._format_business_type_analysis(business_types)}

            REGIONAL DISTRIBUTION:
            {self._format_regional_analysis(regions)}

            Please provide:
            1. Key Business Intelligence Insights
            2. Market Opportunity Analysis
            3. Sector-Specific Patterns and Trends
            4. Geographic Distribution Analysis
            5. Tax Collection Priorities
            6. Formalization Strategy Recommendations
            7. Data Quality Assessment

            Focus on actionable insights for tax authorities and policy makers.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business intelligence analyst specializing in informal economy analysis and tax policy in developing countries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate business intelligence summary: {e}")
            return self._generate_template_business_summary(business_data)
    
    def _format_business_type_analysis(self, business_types: Dict) -> str:
        """Format business type data for analysis"""
        formatted = []
        for btype, data in business_types.items():
            formatted.append(f"- {btype}: {data['count']} businesses, ${data['revenue']:,.2f} total revenue")
        return "\n".join(formatted)
    
    def _format_regional_analysis(self, regions: Dict) -> str:
        """Format regional data for analysis"""
        formatted = []
        for region, data in regions.items():
            formatted.append(f"- {region}: {data['count']} businesses, ${data['revenue']:,.2f} total revenue")
        return "\n".join(formatted)
    
    def _generate_template_report(self, data: Dict) -> str:
        """
        Generate a template-based report when GPT is not available
        """
        report = f"""
# TAX OPPORTUNITY ANALYSIS REPORT

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Region:** {data.get('region', 'Unknown')}

## EXECUTIVE SUMMARY

This report analyzes tax opportunities in {data.get('region', 'the specified region')} based on AI-powered informal business detection and revenue estimation.

### Key Metrics
- **Total Businesses Identified:** {data.get('business_count', 0):,}
- **Estimated Total Revenue:** ${data.get('total_revenue', 0):,.2f}
- **Potential Tax Revenue:** ${data.get('potential_tax', 0):,.2f}
- **Current Tax Collection:** ${data.get('current_collection', 0):,.2f}
- **Tax Gap:** ${data.get('tax_gap', 0):,.2f}

## KEY FINDINGS

1. **Revenue Opportunity:** The analysis identifies significant untapped tax revenue potential of ${data.get('tax_gap', 0):,.2f}.

2. **Collection Efficiency:** Current collection efficiency stands at {data.get('collection_efficiency', 0)*100:.1f}%, indicating room for improvement.

3. **Compliance Rate:** The estimated compliance rate is {data.get('compliance_rate', 0)*100:.1f}%, suggesting need for enhanced taxpayer engagement.

## RECOMMENDATIONS

### Immediate Actions (0-6 months)
- Implement targeted outreach programs for identified businesses
- Establish mobile tax collection points in high-density areas
- Launch taxpayer education campaigns

### Medium-term Initiatives (6-18 months)
- Deploy digital tax registration platforms
- Introduce simplified tax regimes for small businesses
- Enhance tax administration capacity

### Long-term Strategy (18+ months)
- Integrate AI-powered tax intelligence into regular operations
- Develop comprehensive informal sector formalization program
- Establish performance monitoring and evaluation systems

## IMPLEMENTATION PRIORITIES

1. **High Priority:** Focus on businesses with highest tax potential
2. **Medium Priority:** Target sectors with good compliance potential
3. **Low Priority:** Monitor emerging business areas for future opportunities

---
*This report was generated using TaxIntel AI platform.*
        """
        
        return report
    
    def _generate_template_policy_report(self, baseline: Dict, projected: Dict, policy_details: Dict) -> str:
        """Generate template policy impact report"""
        additional_revenue = projected.get('additional_revenue', 0)
        percentage_increase = projected.get('percentage_increase', 0)
        
        report = f"""
# POLICY IMPACT ASSESSMENT REPORT

**Policy:** {policy_details.get('name', 'Tax Policy Reform')}
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## EXECUTIVE SUMMARY

This assessment evaluates the projected impact of implementing {policy_details.get('name', 'the proposed tax policy')} in {policy_details.get('region', 'the target region')}.

### Impact Overview
- **Additional Revenue:** ${additional_revenue:,.2f}
- **Percentage Increase:** {percentage_increase:.1f}%
- **Implementation Timeline:** {policy_details.get('timeline', '12 months')}

## BASELINE VS. PROJECTED SCENARIO

### Current State
- Tax Collection: ${baseline.get('current_collection', 0):,.2f}
- Compliance Rate: {baseline.get('compliance_rate', 0)*100:.1f}%
- Collection Efficiency: {baseline.get('collection_efficiency', 0)*100:.1f}%

### Projected Outcomes
- Tax Collection: ${projected.get('projected_collection', 0):,.2f}
- Compliance Rate: {projected.get('compliance_rate', 0)*100:.1f}%
- Collection Efficiency: {projected.get('collection_efficiency', 0)*100:.1f}%

## IMPLEMENTATION STRATEGY

### Phase 1: Preparation (Months 1-3)
- Policy framework development
- Stakeholder consultation
- Resource allocation

### Phase 2: Pilot Implementation (Months 4-6)
- Limited rollout in selected areas
- System testing and refinement
- Staff training and capacity building

### Phase 3: Full Deployment (Months 7-12)
- Region-wide implementation
- Monitoring and evaluation
- Continuous improvement

## RISK ASSESSMENT

### High Risks
- Resistance from informal sector participants
- Insufficient administrative capacity

### Medium Risks
- Technology adoption challenges
- Resource constraints

### Mitigation Strategies
- Comprehensive stakeholder engagement
- Phased implementation approach
- Continuous monitoring and support

---
*This assessment was generated using TaxIntel AI platform.*
        """
        
        return report
    
    def _generate_template_business_summary(self, business_data: List[Dict]) -> str:
        """Generate template business intelligence summary"""
        total_businesses = len(business_data)
        total_revenue = sum(b.get('estimated_revenue', 0) for b in business_data)
        total_tax_potential = sum(b.get('tax_potential', 0) for b in business_data)
        
        report = f"""
# BUSINESS INTELLIGENCE SUMMARY

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Period:** Current snapshot

## OVERVIEW

This summary provides insights from AI-powered analysis of {total_businesses} informal businesses.

### Key Statistics
- **Total Businesses Analyzed:** {total_businesses:,}
- **Total Estimated Revenue:** ${total_revenue:,.2f}
- **Total Tax Potential:** ${total_tax_potential:,.2f}
- **Average Revenue per Business:** ${total_revenue/total_businesses if total_businesses > 0 else 0:,.2f}

## KEY INSIGHTS

### Business Distribution
The analysis reveals diverse business types across multiple sectors, indicating a vibrant informal economy with significant formalization potential.

### Revenue Patterns
Estimated revenue patterns suggest substantial economic activity that could contribute meaningfully to tax revenues through appropriate formalization strategies.

### Geographic Spread
Businesses are distributed across various regions, requiring tailored approaches for different geographic contexts.

## STRATEGIC RECOMMENDATIONS

### Immediate Focus Areas
1. **High-Revenue Businesses:** Prioritize engagement with businesses showing highest revenue potential
2. **Cluster Approach:** Target business clusters for efficient resource utilization
3. **Sector-Specific Strategies:** Develop tailored approaches for different business types

### Implementation Approach
1. **Data-Driven Targeting:** Use AI insights to prioritize outreach efforts
2. **Graduated Formalization:** Implement step-by-step formalization process
3. **Continuous Monitoring:** Regular assessment of progress and impact

---
*This summary was generated using TaxIntel AI platform.*
        """
        
        return report

# Example usage and testing
if __name__ == "__main__":
    # Initialize report generator
    generator = ReportGenerator()
    
    # Test data for tax opportunity report
    test_data = {
        'region': 'Nairobi Central',
        'business_count': 150,
        'total_revenue': 2500000,
        'current_collection': 180000,
        'potential_tax': 400000,
        'tax_gap': 220000,
        'collection_efficiency': 0.45,
        'compliance_rate': 0.6,
        'sectors': [
            {'name': 'Retail', 'business_count': 60, 'potential_tax': 160000},
            {'name': 'Services', 'business_count': 45, 'potential_tax': 135000},
            {'name': 'Food & Beverage', 'business_count': 45, 'potential_tax': 105000}
        ],
        'business_types': [
            {'type': 'Market Vendor', 'count': 50},
            {'type': 'Small Retail', 'count': 40},
            {'type': 'Service Provider', 'count': 35},
            {'type': 'Roadside Shop', 'count': 25}
        ]
    }
    
    # Generate tax opportunity report
    print("Generating Tax Opportunity Report...")
    tax_report = generator.generate_tax_opportunity_report(test_data)
    print(tax_report)
    
    print("\n" + "="*80 + "\n")
    
    # Test policy impact report
    baseline = {
        'current_collection': 180000,
        'compliance_rate': 0.6,
        'collection_efficiency': 0.45
    }
    
    projected = {
        'projected_collection': 280000,
        'compliance_rate': 0.75,
        'collection_efficiency': 0.6,
        'additional_revenue': 100000,
        'percentage_increase': 55.6
    }
    
    policy_details = {
        'name': 'Digital Tax Registration Initiative',
        'type': 'Digitalization',
        'region': 'Nairobi Central',
        'timeline': '12 months'
    }
    
    print("Generating Policy Impact Report...")
    policy_report = generator.generate_policy_impact_report(baseline, projected, policy_details)
    print(policy_report)

