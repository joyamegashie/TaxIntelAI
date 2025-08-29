import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxEstimator:
    """
    AI model for estimating tax potential and revenue opportunities
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.revenue_model = None
        self.compliance_model = None
        self.collection_efficiency_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        self.model_path = model_path or "models/"
        
        # Ensure model directory exists
        os.makedirs(self.model_path, exist_ok=True)
        
        # Load pre-trained models if they exist
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models if they exist"""
        try:
            revenue_path = os.path.join(self.model_path, "revenue_model.joblib")
            compliance_path = os.path.join(self.model_path, "compliance_model.joblib")
            efficiency_path = os.path.join(self.model_path, "collection_efficiency_model.joblib")
            scaler_path = os.path.join(self.model_path, "tax_scaler.joblib")
            encoders_path = os.path.join(self.model_path, "label_encoders.joblib")
            
            if all(os.path.exists(path) for path in [revenue_path, compliance_path, efficiency_path, scaler_path]):
                self.revenue_model = joblib.load(revenue_path)
                self.compliance_model = joblib.load(compliance_path)
                self.collection_efficiency_model = joblib.load(efficiency_path)
                self.scaler = joblib.load(scaler_path)
                if os.path.exists(encoders_path):
                    self.label_encoders = joblib.load(encoders_path)
                self.is_trained = True
                logger.info("Pre-trained tax estimation models loaded successfully")
            else:
                logger.info("No pre-trained tax models found, will train new models")
        except Exception as e:
            logger.warning(f"Failed to load pre-trained tax models: {e}")
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            joblib.dump(self.revenue_model, os.path.join(self.model_path, "revenue_model.joblib"))
            joblib.dump(self.compliance_model, os.path.join(self.model_path, "compliance_model.joblib"))
            joblib.dump(self.collection_efficiency_model, os.path.join(self.model_path, "collection_efficiency_model.joblib"))
            joblib.dump(self.scaler, os.path.join(self.model_path, "tax_scaler.joblib"))
            joblib.dump(self.label_encoders, os.path.join(self.model_path, "label_encoders.joblib"))
            logger.info("Tax estimation models saved successfully")
        except Exception as e:
            logger.error(f"Failed to save tax models: {e}")
    
    def generate_synthetic_data(self, n_samples: int = 2000) -> pd.DataFrame:
        """
        Generate synthetic training data for tax estimation
        """
        np.random.seed(42)
        
        data = []
        
        regions = ['Nairobi Central', 'Nairobi South', 'Nairobi North', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
        sectors = ['Retail', 'Services', 'Manufacturing', 'Agriculture', 'Transport', 'Food & Beverage', 'Technology']
        
        for _ in range(n_samples):
            # Basic features
            region = np.random.choice(regions)
            sector = np.random.choice(sectors)
            business_count = np.random.randint(10, 500)
            population_density = np.random.uniform(100, 5000)  # people per km²
            economic_activity_score = np.random.uniform(0.1, 1.0)
            infrastructure_score = np.random.uniform(0.2, 1.0)
            education_level = np.random.uniform(0.3, 0.9)
            
            # Regional multipliers
            region_multipliers = {
                'Nairobi Central': 1.5,
                'Nairobi South': 1.2,
                'Nairobi North': 1.3,
                'Mombasa': 1.1,
                'Kisumu': 0.9,
                'Nakuru': 0.8,
                'Eldoret': 0.7
            }
            
            # Sector multipliers
            sector_multipliers = {
                'Retail': 1.0,
                'Services': 1.2,
                'Manufacturing': 1.4,
                'Agriculture': 0.6,
                'Transport': 0.9,
                'Food & Beverage': 0.8,
                'Technology': 1.6
            }
            
            # Calculate base revenue
            base_revenue_per_business = 30000 * region_multipliers[region] * sector_multipliers[sector]
            base_revenue_per_business *= (0.5 + economic_activity_score * 0.5)
            base_revenue_per_business *= (0.7 + infrastructure_score * 0.3)
            
            # Add noise
            base_revenue_per_business *= (1 + np.random.normal(0, 0.3))
            base_revenue_per_business = max(5000, base_revenue_per_business)
            
            total_estimated_revenue = base_revenue_per_business * business_count
            
            # Calculate compliance rate
            base_compliance = 0.3  # Base 30% compliance
            compliance_rate = base_compliance + (infrastructure_score * 0.2) + (education_level * 0.15)
            compliance_rate += np.random.normal(0, 0.1)
            compliance_rate = np.clip(compliance_rate, 0.1, 0.9)
            
            # Calculate collection efficiency
            base_efficiency = 0.6  # Base 60% collection efficiency
            collection_efficiency = base_efficiency + (infrastructure_score * 0.2) + (economic_activity_score * 0.1)
            collection_efficiency += np.random.normal(0, 0.1)
            collection_efficiency = np.clip(collection_efficiency, 0.3, 0.95)
            
            # Tax rates by sector
            tax_rates = {
                'Retail': 0.16,
                'Services': 0.18,
                'Manufacturing': 0.20,
                'Agriculture': 0.10,
                'Transport': 0.15,
                'Food & Beverage': 0.14,
                'Technology': 0.25
            }
            
            tax_rate = tax_rates[sector]
            
            # Calculate potential and actual tax
            potential_tax = total_estimated_revenue * tax_rate
            actual_tax_collected = potential_tax * compliance_rate * collection_efficiency
            
            data.append({
                'region': region,
                'sector': sector,
                'business_count': business_count,
                'population_density': population_density,
                'economic_activity_score': economic_activity_score,
                'infrastructure_score': infrastructure_score,
                'education_level': education_level,
                'estimated_revenue': total_estimated_revenue,
                'compliance_rate': compliance_rate,
                'collection_efficiency': collection_efficiency,
                'tax_rate': tax_rate,
                'potential_tax': potential_tax,
                'actual_tax_collected': actual_tax_collected
            })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        Prepare features for training
        """
        # Encode categorical variables
        categorical_cols = ['region', 'sector']
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col])
        
        # Select features
        feature_cols = [
            'region_encoded', 'sector_encoded', 'business_count', 'population_density',
            'economic_activity_score', 'infrastructure_score', 'education_level'
        ]
        
        X = df[feature_cols].values
        
        # Prepare targets
        targets = {
            'revenue': df['estimated_revenue'].values,
            'compliance': df['compliance_rate'].values,
            'efficiency': df['collection_efficiency'].values
        }
        
        return X, targets
    
    def train(self, data: Optional[pd.DataFrame] = None):
        """
        Train the tax estimation models
        """
        if data is None:
            logger.info("Generating synthetic training data...")
            data = self.generate_synthetic_data()
        
        # Prepare features and targets
        X, targets = self.prepare_features(data)
        
        # Split data
        X_train, X_test, y_revenue_train, y_revenue_test = train_test_split(
            X, targets['revenue'], test_size=0.2, random_state=42
        )
        _, _, y_compliance_train, y_compliance_test = train_test_split(
            X, targets['compliance'], test_size=0.2, random_state=42
        )
        _, _, y_efficiency_train, y_efficiency_test = train_test_split(
            X, targets['efficiency'], test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train revenue estimation model
        logger.info("Training revenue estimation model...")
        self.revenue_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.revenue_model.fit(X_train_scaled, y_revenue_train)
        
        # Evaluate revenue model
        y_revenue_pred = self.revenue_model.predict(X_test_scaled)
        revenue_r2 = r2_score(y_revenue_test, y_revenue_pred)
        revenue_mae = mean_absolute_error(y_revenue_test, y_revenue_pred)
        logger.info(f"Revenue Model - R²: {revenue_r2:.3f}, MAE: {revenue_mae:.2f}")
        
        # Train compliance rate model
        logger.info("Training compliance rate model...")
        self.compliance_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        self.compliance_model.fit(X_train_scaled, y_compliance_train)
        
        # Evaluate compliance model
        y_compliance_pred = self.compliance_model.predict(X_test_scaled)
        compliance_r2 = r2_score(y_compliance_test, y_compliance_pred)
        compliance_mae = mean_absolute_error(y_compliance_test, y_compliance_pred)
        logger.info(f"Compliance Model - R²: {compliance_r2:.3f}, MAE: {compliance_mae:.3f}")
        
        # Train collection efficiency model
        logger.info("Training collection efficiency model...")
        self.collection_efficiency_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        self.collection_efficiency_model.fit(X_train_scaled, y_efficiency_train)
        
        # Evaluate efficiency model
        y_efficiency_pred = self.collection_efficiency_model.predict(X_test_scaled)
        efficiency_r2 = r2_score(y_efficiency_test, y_efficiency_pred)
        efficiency_mae = mean_absolute_error(y_efficiency_test, y_efficiency_pred)
        logger.info(f"Collection Efficiency Model - R²: {efficiency_r2:.3f}, MAE: {efficiency_mae:.3f}")
        
        self.is_trained = True
        self._save_models()
        logger.info("Tax estimation training completed successfully")
    
    def estimate_tax_potential(self, region: str, sector: str, business_count: int,
                             population_density: float, economic_activity_score: float,
                             infrastructure_score: float, education_level: float) -> Dict:
        """
        Estimate tax potential for a given region and sector
        """
        if not self.is_trained:
            logger.warning("Models not trained, training with synthetic data...")
            self.train()
        
        # Prepare input data
        input_data = pd.DataFrame([{
            'region': region,
            'sector': sector,
            'business_count': business_count,
            'population_density': population_density,
            'economic_activity_score': economic_activity_score,
            'infrastructure_score': infrastructure_score,
            'education_level': education_level
        }])
        
        # Encode categorical variables
        for col in ['region', 'sector']:
            if col in self.label_encoders:
                try:
                    input_data[f'{col}_encoded'] = self.label_encoders[col].transform(input_data[col])
                except ValueError:
                    # Handle unseen categories
                    logger.warning(f"Unseen category '{input_data[col].iloc[0]}' for {col}, using default encoding")
                    input_data[f'{col}_encoded'] = 0
            else:
                input_data[f'{col}_encoded'] = 0
        
        # Prepare features
        feature_cols = [
            'region_encoded', 'sector_encoded', 'business_count', 'population_density',
            'economic_activity_score', 'infrastructure_score', 'education_level'
        ]
        X = input_data[feature_cols].values
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        estimated_revenue = self.revenue_model.predict(X_scaled)[0]
        compliance_rate = self.compliance_model.predict(X_scaled)[0]
        collection_efficiency = self.collection_efficiency_model.predict(X_scaled)[0]
        
        # Ensure reasonable bounds
        compliance_rate = np.clip(compliance_rate, 0.1, 0.9)
        collection_efficiency = np.clip(collection_efficiency, 0.3, 0.95)
        
        # Calculate tax estimates
        tax_rates = {
            'Retail': 0.16, 'Services': 0.18, 'Manufacturing': 0.20,
            'Agriculture': 0.10, 'Transport': 0.15, 'Food & Beverage': 0.14,
            'Technology': 0.25
        }
        tax_rate = tax_rates.get(sector, 0.16)
        
        potential_tax = estimated_revenue * tax_rate
        expected_tax_collected = potential_tax * compliance_rate * collection_efficiency
        tax_gap = potential_tax - expected_tax_collected
        
        return {
            'region': region,
            'sector': sector,
            'business_count': business_count,
            'estimated_revenue': estimated_revenue,
            'tax_rate': tax_rate,
            'potential_tax': potential_tax,
            'compliance_rate': compliance_rate,
            'collection_efficiency': collection_efficiency,
            'expected_tax_collected': expected_tax_collected,
            'tax_gap': tax_gap,
            'confidence_score': min(0.9, (compliance_rate + collection_efficiency) / 2)
        }
    
    def analyze_regional_opportunities(self, regions: List[str], 
                                     sectors: List[str] = None) -> List[Dict]:
        """
        Analyze tax opportunities across multiple regions
        """
        if sectors is None:
            sectors = ['Retail', 'Services', 'Manufacturing', 'Agriculture', 'Transport']
        
        opportunities = []
        
        for region in regions:
            for sector in sectors:
                # Generate realistic parameters for the region/sector combination
                business_count = np.random.randint(20, 200)
                population_density = np.random.uniform(500, 3000)
                economic_activity_score = np.random.uniform(0.3, 0.9)
                infrastructure_score = np.random.uniform(0.4, 0.8)
                education_level = np.random.uniform(0.4, 0.8)
                
                estimate = self.estimate_tax_potential(
                    region, sector, business_count, population_density,
                    economic_activity_score, infrastructure_score, education_level
                )
                
                opportunities.append(estimate)
        
        # Sort by tax gap (highest opportunity first)
        opportunities.sort(key=lambda x: x['tax_gap'], reverse=True)
        
        return opportunities
    
    def simulate_policy_impact(self, baseline_estimate: Dict, 
                             policy_changes: Dict) -> Dict:
        """
        Simulate the impact of policy changes on tax collection
        """
        # Create a copy of baseline
        new_estimate = baseline_estimate.copy()
        
        # Apply policy changes
        if 'compliance_improvement' in policy_changes:
            new_estimate['compliance_rate'] = min(0.9, 
                baseline_estimate['compliance_rate'] * (1 + policy_changes['compliance_improvement']))
        
        if 'efficiency_improvement' in policy_changes:
            new_estimate['collection_efficiency'] = min(0.95,
                baseline_estimate['collection_efficiency'] * (1 + policy_changes['efficiency_improvement']))
        
        if 'tax_rate_change' in policy_changes:
            new_estimate['tax_rate'] = baseline_estimate['tax_rate'] * (1 + policy_changes['tax_rate_change'])
        
        # Recalculate tax estimates
        new_estimate['potential_tax'] = new_estimate['estimated_revenue'] * new_estimate['tax_rate']
        new_estimate['expected_tax_collected'] = (new_estimate['potential_tax'] * 
                                                new_estimate['compliance_rate'] * 
                                                new_estimate['collection_efficiency'])
        new_estimate['tax_gap'] = new_estimate['potential_tax'] - new_estimate['expected_tax_collected']
        
        # Calculate impact
        impact = {
            'baseline_collection': baseline_estimate['expected_tax_collected'],
            'projected_collection': new_estimate['expected_tax_collected'],
            'additional_revenue': new_estimate['expected_tax_collected'] - baseline_estimate['expected_tax_collected'],
            'percentage_increase': ((new_estimate['expected_tax_collected'] / baseline_estimate['expected_tax_collected']) - 1) * 100,
            'new_estimate': new_estimate,
            'policy_changes': policy_changes
        }
        
        return impact

# Example usage and testing
if __name__ == "__main__":
    # Initialize estimator
    estimator = TaxEstimator()
    
    # Train the models
    estimator.train()
    
    # Test single estimation
    result = estimator.estimate_tax_potential(
        region="Nairobi Central",
        sector="Retail",
        business_count=150,
        population_density=2500,
        economic_activity_score=0.8,
        infrastructure_score=0.7,
        education_level=0.6
    )
    
    print("Tax Estimation Result:")
    for key, value in result.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "="*50)
    
    # Test regional analysis
    regions = ["Nairobi Central", "Mombasa", "Kisumu"]
    opportunities = estimator.analyze_regional_opportunities(regions)
    
    print(f"\nTop 5 Tax Opportunities:")
    for i, opp in enumerate(opportunities[:5]):
        print(f"{i+1}. {opp['region']} - {opp['sector']}")
        print(f"   Tax Gap: ${opp['tax_gap']:.2f}")
        print(f"   Potential: ${opp['potential_tax']:.2f}")
        print(f"   Expected: ${opp['expected_tax_collected']:.2f}")
    
    print("\n" + "="*50)
    
    # Test policy simulation
    policy_changes = {
        'compliance_improvement': 0.2,  # 20% improvement
        'efficiency_improvement': 0.15   # 15% improvement
    }
    
    impact = estimator.simulate_policy_impact(result, policy_changes)
    print(f"\nPolicy Impact Simulation:")
    print(f"Baseline Collection: ${impact['baseline_collection']:.2f}")
    print(f"Projected Collection: ${impact['projected_collection']:.2f}")
    print(f"Additional Revenue: ${impact['additional_revenue']:.2f}")
    print(f"Percentage Increase: {impact['percentage_increase']:.1f}%")

