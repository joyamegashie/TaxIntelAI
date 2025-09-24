import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
import joblib
import os
from typing import List, Dict, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessDetector:
    """
    AI model for detecting informal businesses from satellite imagery and geographic data
    """

    def __init__(self, model_path: Optional[str] = None):
        self.classifier = None
        self.revenue_estimator = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = model_path or "models/"

        # Ensure model directory exists
        os.makedirs(self.model_path, exist_ok=True)

        # Load pre-trained models if they exist
        self._load_models()

    def _load_models(self):
        """Load pre-trained models if they exist"""
        try:
            classifier_path = os.path.join(
                self.model_path, "business_classifier.joblib"
            )
            revenue_path = os.path.join(self.model_path, "revenue_estimator.joblib")
            scaler_path = os.path.join(self.model_path, "scaler.joblib")

            if all(
                os.path.exists(path)
                for path in [classifier_path, revenue_path, scaler_path]
            ):
                self.classifier = joblib.load(classifier_path)
                self.revenue_estimator = joblib.load(revenue_path)
                self.scaler = joblib.load(scaler_path)
                self.is_trained = True
                logger.info("Pre-trained models loaded successfully")
            else:
                logger.info("No pre-trained models found, will train new models")
        except Exception as e:
            logger.warning(f"Failed to load pre-trained models: {e}")

    def _save_models(self):
        """Save trained models to disk"""
        try:
            joblib.dump(
                self.classifier,
                os.path.join(self.model_path, "business_classifier.joblib"),
            )
            joblib.dump(
                self.revenue_estimator,
                os.path.join(self.model_path, "revenue_estimator.joblib"),
            )
            joblib.dump(self.scaler, os.path.join(self.model_path, "scaler.joblib"))
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Failed to save models: {e}")

    def generate_synthetic_data(
        self, n_samples: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate synthetic training data for demonstration purposes
        In production, this would be replaced with real satellite imagery features
        """
        np.random.seed(42)

        # Generate features that might be extracted from satellite imagery
        features = []
        labels = []
        revenues = []

        for _ in range(n_samples):
            # Simulate features extracted from satellite imagery
            building_density = np.random.uniform(0, 1)
            road_proximity = np.random.uniform(0, 1)
            vegetation_index = np.random.uniform(0, 1)
            population_density = np.random.uniform(0, 1)
            economic_activity = np.random.uniform(0, 1)
            market_proximity = np.random.uniform(0, 1)

            # Create feature vector
            feature_vector = [
                building_density,
                road_proximity,
                vegetation_index,
                population_density,
                economic_activity,
                market_proximity,
            ]

            # Generate label based on feature combination (simplified logic)
            business_probability = (
                building_density * 0.3
                + road_proximity * 0.2
                + population_density * 0.25
                + economic_activity * 0.15
                + market_proximity * 0.1
            )

            is_business = business_probability > 0.5

            # Generate revenue estimate for businesses
            if is_business:
                base_revenue = 20000 + (business_probability * 80000)
                revenue = base_revenue * (1 + np.random.normal(0, 0.3))
                revenue = max(5000, revenue)  # Minimum revenue
            else:
                revenue = 0

            features.append(feature_vector)
            labels.append(int(is_business))
            revenues.append(revenue)

        return np.array(features), np.array(labels), np.array(revenues)

    def train(
        self,
        features: Optional[np.ndarray] = None,
        labels: Optional[np.ndarray] = None,
        revenues: Optional[np.ndarray] = None,
    ):
        """
        Train the business detection and revenue estimation models
        """
        if features is None or labels is None or revenues is None:
            logger.info("Generating synthetic training data...")
            features, labels, revenues = self.generate_synthetic_data()

        # Split data
        X_train, X_test, y_train, y_test, rev_train, rev_test = train_test_split(
            features, labels, revenues, test_size=0.2, random_state=42
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train business classifier
        logger.info("Training business classifier...")
        self.classifier = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, class_weight="balanced"
        )
        self.classifier.fit(X_train_scaled, y_train)

        # Evaluate classifier
        y_pred = self.classifier.predict(X_test_scaled)
        logger.info("Classifier Performance:")
        logger.info(classification_report(y_test, y_pred))

        # Train revenue estimator (only on business samples)
        business_mask = y_train == 1
        if np.sum(business_mask) > 0:
            logger.info("Training revenue estimator...")
            self.revenue_estimator = GradientBoostingRegressor(
                n_estimators=100, max_depth=6, random_state=42
            )
            self.revenue_estimator.fit(
                X_train_scaled[business_mask], rev_train[business_mask]
            )

            # Evaluate revenue estimator
            business_test_mask = y_test == 1
            if np.sum(business_test_mask) > 0:
                rev_pred = self.revenue_estimator.predict(
                    X_test_scaled[business_test_mask]
                )
                mse = mean_squared_error(rev_test[business_test_mask], rev_pred)
                logger.info(f"Revenue Estimator MSE: {mse:.2f}")

        self.is_trained = True
        self._save_models()
        logger.info("Training completed successfully")

    def detect_businesses(
        self,
        coordinates: List[Tuple[float, float]],
        features: Optional[np.ndarray] = None,
    ) -> List[Dict]:
        """
        Detect businesses at given coordinates
        """
        if not self.is_trained:
            logger.warning("Model not trained, training with synthetic data...")
            self.train()

        results = []

        for i, (lat, lng) in enumerate(coordinates):
            if features is not None and i < len(features):
                feature_vector = features[i].reshape(1, -1)
            else:
                # Generate synthetic features for demonstration
                feature_vector = np.array(
                    [
                        [
                            np.random.uniform(0, 1),  # building_density
                            np.random.uniform(0, 1),  # road_proximity
                            np.random.uniform(0, 1),  # vegetation_index
                            np.random.uniform(0, 1),  # population_density
                            np.random.uniform(0, 1),  # economic_activity
                            np.random.uniform(0, 1),  # market_proximity
                        ]
                    ]
                )

            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)

            # Predict business probability
            business_prob = self.classifier.predict_proba(feature_vector_scaled)[0][1]
            is_business = business_prob > 0.5

            # Estimate revenue if it's a business
            estimated_revenue = 0
            if is_business and self.revenue_estimator:
                estimated_revenue = max(
                    0, self.revenue_estimator.predict(feature_vector_scaled)[0]
                )

            # Calculate tax potential (15% tax rate)
            tax_potential = estimated_revenue * 0.15

            result = {
                "latitude": lat,
                "longitude": lng,
                "is_business": is_business,
                "confidence_score": business_prob,
                "estimated_revenue": estimated_revenue,
                "tax_potential": tax_potential,
                "business_type": self._classify_business_type(feature_vector[0]),
                "region": self._get_region_from_coordinates(lat, lng),
            }

            results.append(result)

        return results

    def _classify_business_type(self, features: np.ndarray) -> str:
        """
        Classify business type based on features (simplified)
        """
        (
            building_density,
            road_proximity,
            vegetation_index,
            population_density,
            economic_activity,
            market_proximity,
        ) = features

        if market_proximity > 0.7:
            return "Market Vendor"
        elif road_proximity > 0.8:
            return "Roadside Shop"
        elif building_density > 0.6:
            return "Small Retail"
        elif economic_activity > 0.7:
            return "Service Provider"
        else:
            return "General Trade"

    def _get_region_from_coordinates(self, lat: float, lng: float) -> str:
        """
        Get region name from coordinates (simplified)
        """
        # This is a simplified mapping - in production, use proper geocoding
        if -1.5 <= lat <= -1.0 and 36.5 <= lng <= 37.0:
            return "Nairobi Central"
        elif -1.8 <= lat <= -1.5 and 36.5 <= lng <= 37.0:
            return "Nairobi South"
        elif -1.0 <= lat <= -0.5 and 36.5 <= lng <= 37.0:
            return "Nairobi North"
        else:
            return "Other Region"

    def cluster_businesses(
        self, business_data: List[Dict], eps: float = 0.01, min_samples: int = 3
    ) -> List[Dict]:
        """
        Cluster detected businesses to identify business districts
        """
        if not business_data:
            return []

        # Extract coordinates
        coordinates = np.array([[b["latitude"], b["longitude"]] for b in business_data])

        # Perform clustering
        clustering = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = clustering.fit_predict(coordinates)

        # Group businesses by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append({**business_data[i], "cluster_id": int(label)})

        # Calculate cluster statistics
        cluster_stats = []
        for cluster_id, businesses in clusters.items():
            if cluster_id == -1:  # Noise points
                continue

            total_revenue = sum(b["estimated_revenue"] for b in businesses)
            total_tax_potential = sum(b["tax_potential"] for b in businesses)
            avg_confidence = np.mean([b["confidence_score"] for b in businesses])

            # Calculate cluster center
            center_lat = np.mean([b["latitude"] for b in businesses])
            center_lng = np.mean([b["longitude"] for b in businesses])

            cluster_stats.append(
                {
                    "cluster_id": cluster_id,
                    "business_count": len(businesses),
                    "center_latitude": center_lat,
                    "center_longitude": center_lng,
                    "total_estimated_revenue": total_revenue,
                    "total_tax_potential": total_tax_potential,
                    "average_confidence": avg_confidence,
                    "businesses": businesses,
                }
            )

        return cluster_stats

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance from the trained classifier
        """
        if not self.is_trained or not self.classifier:
            return {}

        feature_names = [
            "building_density",
            "road_proximity",
            "vegetation_index",
            "population_density",
            "economic_activity",
            "market_proximity",
        ]

        importance = self.classifier.feature_importances_
        return dict(zip(feature_names, importance))


# Example usage and testing
if __name__ == "__main__":
    # Initialize detector
    detector = BusinessDetector()

    # Train the model
    detector.train()

    # Test detection on sample coordinates (Nairobi area)
    test_coordinates = [
        (-1.2921, 36.8219),  # Nairobi CBD
        (-1.3031, 36.8073),  # Kibera
        (-1.2634, 36.8059),  # Westlands
        (-1.3197, 36.8516),  # Eastlands
    ]

    # Detect businesses
    results = detector.detect_businesses(test_coordinates)

    # Print results
    for result in results:
        print(f"Location: ({result['latitude']:.4f}, {result['longitude']:.4f})")
        print(
            f"Business: {result['is_business']} (confidence: {result['confidence_score']:.2f})"
        )
        print(f"Type: {result['business_type']}")
        print(f"Revenue: ${result['estimated_revenue']:.2f}")
        print(f"Tax Potential: ${result['tax_potential']:.2f}")
        print(f"Region: {result['region']}")
        print("-" * 50)

    # Test clustering
    business_results = [r for r in results if r["is_business"]]
    if business_results:
        clusters = detector.cluster_businesses(business_results)
        print(f"\nFound {len(clusters)} business clusters")
        for cluster in clusters:
            print(
                f"Cluster {cluster['cluster_id']}: {cluster['business_count']} businesses"
            )
            print(f"Total tax potential: ${cluster['total_tax_potential']:.2f}")

    # Print feature importance
    importance = detector.get_feature_importance()
    print("\nFeature Importance:")
    for feature, imp in importance.items():
        print(f"{feature}: {imp:.3f}")
