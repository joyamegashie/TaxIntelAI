import numpy as np
import requests
import json
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SatelliteAnalyzer:
    """
    Satellite imagery analysis for informal business detection
    Integrates with Sentinel-2 and other satellite data sources
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://services.sentinel-hub.com/api/v1"
        self.session = requests.Session()

        # Set up session headers
        if self.api_key:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

    def get_satellite_data(
        self,
        latitude: float,
        longitude: float,
        bbox_size: float = 0.01,
        date_range: int = 30,
    ) -> Dict:
        """
        Retrieve satellite imagery data for a given location
        """
        try:
            # Calculate bounding box
            bbox = [
                longitude - bbox_size / 2,  # min_lon
                latitude - bbox_size / 2,  # min_lat
                longitude + bbox_size / 2,  # max_lon
                latitude + bbox_size / 2,  # max_lat
            ]

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)

            # For demonstration, we'll simulate satellite data
            # In production, this would make actual API calls to Sentinel Hub or similar services
            simulated_data = self._simulate_satellite_data(
                latitude, longitude, bbox_size
            )

            return {
                "location": {"latitude": latitude, "longitude": longitude},
                "bbox": bbox,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "data": simulated_data,
                "source": "simulated",  # In production: 'sentinel-2', 'landsat', etc.
            }

        except Exception as e:
            logger.error(f"Failed to retrieve satellite data: {e}")
            return self._get_fallback_data(latitude, longitude)

    def _simulate_satellite_data(
        self, latitude: float, longitude: float, bbox_size: float
    ) -> Dict:
        """
        Simulate satellite imagery analysis results
        In production, this would process actual satellite imagery
        """
        # Simulate different indices and features that would be extracted from satellite imagery
        np.random.seed(int((latitude + longitude) * 1000) % 2**32)

        # Normalized Difference Vegetation Index (NDVI)
        # Lower values might indicate built-up areas
        ndvi = np.random.uniform(-0.2, 0.8)

        # Normalized Difference Built-up Index (NDBI)
        # Higher values indicate built-up areas
        ndbi = np.random.uniform(-0.5, 0.5)

        # Urban Index
        urban_index = np.random.uniform(0, 1)

        # Building density (estimated from image analysis)
        building_density = np.random.uniform(0, 1)

        # Road network density
        road_density = np.random.uniform(0, 1)

        # Market/commercial area indicators
        commercial_activity = np.random.uniform(0, 1)

        # Temporal changes (indicating economic activity)
        temporal_change = np.random.uniform(0, 0.3)

        # Night-time lights intensity (economic activity indicator)
        nighttime_lights = np.random.uniform(0, 1)

        # Population density estimate
        population_estimate = np.random.uniform(100, 5000)

        return {
            "spectral_indices": {
                "ndvi": ndvi,
                "ndbi": ndbi,
                "urban_index": urban_index,
            },
            "infrastructure": {
                "building_density": building_density,
                "road_density": road_density,
                "commercial_activity": commercial_activity,
            },
            "activity_indicators": {
                "temporal_change": temporal_change,
                "nighttime_lights": nighttime_lights,
                "population_estimate": population_estimate,
            },
            "quality_metrics": {
                "cloud_coverage": np.random.uniform(0, 0.3),
                "image_resolution": "10m",
                "acquisition_date": datetime.now().isoformat(),
            },
        }

    def _get_fallback_data(self, latitude: float, longitude: float) -> Dict:
        """
        Provide fallback data when satellite API is unavailable
        """
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "bbox": [
                longitude - 0.005,
                latitude - 0.005,
                longitude + 0.005,
                latitude + 0.005,
            ],
            "date_range": {
                "start": (datetime.now() - timedelta(days=30)).isoformat(),
                "end": datetime.now().isoformat(),
            },
            "data": {
                "spectral_indices": {"ndvi": 0.3, "ndbi": 0.1, "urban_index": 0.5},
                "infrastructure": {
                    "building_density": 0.4,
                    "road_density": 0.3,
                    "commercial_activity": 0.4,
                },
                "activity_indicators": {
                    "temporal_change": 0.1,
                    "nighttime_lights": 0.4,
                    "population_estimate": 1000,
                },
                "quality_metrics": {
                    "cloud_coverage": 0.1,
                    "image_resolution": "10m",
                    "acquisition_date": datetime.now().isoformat(),
                },
            },
            "source": "fallback",
        }

    def analyze_business_potential(self, satellite_data: Dict) -> Dict:
        """
        Analyze satellite data to determine business potential
        """
        data = satellite_data["data"]

        # Extract features
        ndvi = data["spectral_indices"]["ndvi"]
        ndbi = data["spectral_indices"]["ndbi"]
        urban_index = data["spectral_indices"]["urban_index"]
        building_density = data["infrastructure"]["building_density"]
        road_density = data["infrastructure"]["road_density"]
        commercial_activity = data["infrastructure"]["commercial_activity"]
        nighttime_lights = data["activity_indicators"]["nighttime_lights"]
        population_estimate = data["activity_indicators"]["population_estimate"]

        # Calculate business potential score
        # Lower NDVI + Higher NDBI + Higher urban index = more built-up area
        built_up_score = (1 - ndvi) * 0.3 + ndbi * 0.3 + urban_index * 0.4
        built_up_score = np.clip(built_up_score, 0, 1)

        # Infrastructure accessibility score
        infrastructure_score = road_density * 0.6 + building_density * 0.4

        # Economic activity score
        economic_score = (
            nighttime_lights * 0.5
            + commercial_activity * 0.3
            + min(population_estimate / 2000, 1) * 0.2
        )

        # Overall business potential
        business_potential = (
            built_up_score * 0.4 + infrastructure_score * 0.3 + economic_score * 0.3
        )
        business_potential = np.clip(business_potential, 0, 1)

        # Determine business types likely to be present
        likely_business_types = self._predict_business_types(data)

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(data)

        return {
            "business_potential_score": business_potential,
            "confidence": confidence,
            "component_scores": {
                "built_up_area": built_up_score,
                "infrastructure": infrastructure_score,
                "economic_activity": economic_score,
            },
            "likely_business_types": likely_business_types,
            "recommendations": self._generate_recommendations(business_potential, data),
        }

    def _predict_business_types(self, data: Dict) -> List[Dict]:
        """
        Predict likely business types based on satellite data characteristics
        """
        business_types = []

        road_density = data["infrastructure"]["road_density"]
        commercial_activity = data["infrastructure"]["commercial_activity"]
        building_density = data["infrastructure"]["building_density"]
        population_estimate = data["activity_indicators"]["population_estimate"]

        # Market vendors (high commercial activity, high population)
        if commercial_activity > 0.6 and population_estimate > 1500:
            business_types.append(
                {
                    "type": "Market Vendor",
                    "probability": min(
                        0.9,
                        commercial_activity * 0.7 + (population_estimate / 3000) * 0.3,
                    ),
                    "characteristics": "High foot traffic, commercial zones",
                }
            )

        # Roadside businesses (high road density)
        if road_density > 0.5:
            business_types.append(
                {
                    "type": "Roadside Shop",
                    "probability": min(
                        0.8, road_density * 0.8 + commercial_activity * 0.2
                    ),
                    "characteristics": "Good road access, visible location",
                }
            )

        # Small retail (moderate building density)
        if building_density > 0.4:
            business_types.append(
                {
                    "type": "Small Retail",
                    "probability": min(
                        0.7, building_density * 0.6 + commercial_activity * 0.4
                    ),
                    "characteristics": "Established structures, local commerce",
                }
            )

        # Service providers (balanced indicators)
        if all(x > 0.3 for x in [road_density, commercial_activity, building_density]):
            business_types.append(
                {
                    "type": "Service Provider",
                    "probability": min(
                        0.6, (road_density + commercial_activity + building_density) / 3
                    ),
                    "characteristics": "Mixed commercial and residential area",
                }
            )

        # Sort by probability
        business_types.sort(key=lambda x: x["probability"], reverse=True)

        return business_types[:3]  # Return top 3 most likely types

    def _calculate_confidence(self, data: Dict) -> float:
        """
        Calculate confidence score based on data quality
        """
        cloud_coverage = data["quality_metrics"]["cloud_coverage"]

        # Base confidence
        confidence = 0.8

        # Reduce confidence for high cloud coverage
        confidence -= cloud_coverage * 0.3

        # Adjust based on image resolution (simulated)
        resolution = data["quality_metrics"]["image_resolution"]
        if resolution == "10m":
            confidence += 0.1
        elif resolution == "30m":
            confidence -= 0.1

        return np.clip(confidence, 0.3, 0.95)

    def _generate_recommendations(
        self, business_potential: float, data: Dict
    ) -> List[str]:
        """
        Generate recommendations based on analysis
        """
        recommendations = []

        if business_potential > 0.7:
            recommendations.append(
                "High business potential - prioritize for tax registration outreach"
            )
            recommendations.append("Consider establishing mobile tax collection points")
        elif business_potential > 0.4:
            recommendations.append(
                "Moderate business potential - conduct ground verification"
            )
            recommendations.append("Implement business formalization incentives")
        else:
            recommendations.append(
                "Low business potential - monitor for future development"
            )

        # Infrastructure-specific recommendations
        road_density = data["infrastructure"]["road_density"]
        if road_density < 0.3:
            recommendations.append(
                "Poor road access - consider mobile service delivery"
            )

        # Population-specific recommendations
        population = data["activity_indicators"]["population_estimate"]
        if population > 2000:
            recommendations.append(
                "High population density - establish permanent tax office"
            )

        return recommendations

    def batch_analyze_locations(
        self, locations: List[Tuple[float, float]]
    ) -> List[Dict]:
        """
        Analyze multiple locations in batch
        """
        results = []

        for i, (lat, lng) in enumerate(locations):
            logger.info(
                f"Analyzing location {i+1}/{len(locations)}: ({lat:.4f}, {lng:.4f})"
            )

            try:
                # Get satellite data
                satellite_data = self.get_satellite_data(lat, lng)

                # Analyze business potential
                analysis = self.analyze_business_potential(satellite_data)

                # Combine results
                result = {
                    "location": {"latitude": lat, "longitude": lng},
                    "satellite_data": satellite_data,
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat(),
                }

                results.append(result)

                # Add small delay to avoid overwhelming APIs
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Failed to analyze location ({lat}, {lng}): {e}")
                # Add error result
                results.append(
                    {
                        "location": {"latitude": lat, "longitude": lng},
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return results

    def generate_heatmap_data(
        self,
        center_lat: float,
        center_lng: float,
        grid_size: int = 10,
        bbox_size: float = 0.1,
    ) -> Dict:
        """
        Generate heatmap data for business potential visualization
        """
        # Create grid of points
        lat_step = bbox_size / grid_size
        lng_step = bbox_size / grid_size

        grid_points = []
        for i in range(grid_size):
            for j in range(grid_size):
                lat = center_lat - bbox_size / 2 + i * lat_step
                lng = center_lng - bbox_size / 2 + j * lng_step
                grid_points.append((lat, lng))

        # Analyze all grid points
        logger.info(f"Generating heatmap data for {len(grid_points)} grid points...")
        results = self.batch_analyze_locations(grid_points)

        # Extract heatmap values
        heatmap_data = []
        for result in results:
            if "analysis" in result:
                heatmap_data.append(
                    {
                        "latitude": result["location"]["latitude"],
                        "longitude": result["location"]["longitude"],
                        "business_potential": result["analysis"][
                            "business_potential_score"
                        ],
                        "confidence": result["analysis"]["confidence"],
                    }
                )

        return {
            "center": {"latitude": center_lat, "longitude": center_lng},
            "bbox_size": bbox_size,
            "grid_size": grid_size,
            "data_points": heatmap_data,
            "summary": {
                "total_points": len(heatmap_data),
                "avg_potential": np.mean(
                    [d["business_potential"] for d in heatmap_data]
                ),
                "max_potential": max([d["business_potential"] for d in heatmap_data]),
                "high_potential_areas": len(
                    [d for d in heatmap_data if d["business_potential"] > 0.7]
                ),
            },
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = SatelliteAnalyzer()

    # Test single location analysis
    test_lat, test_lng = -1.2921, 36.8219  # Nairobi CBD

    print(f"Analyzing location: ({test_lat}, {test_lng})")
    satellite_data = analyzer.get_satellite_data(test_lat, test_lng)
    analysis = analyzer.analyze_business_potential(satellite_data)

    print(f"\nBusiness Potential Score: {analysis['business_potential_score']:.3f}")
    print(f"Confidence: {analysis['confidence']:.3f}")

    print("\nComponent Scores:")
    for component, score in analysis["component_scores"].items():
        print(f"  {component}: {score:.3f}")

    print("\nLikely Business Types:")
    for business_type in analysis["likely_business_types"]:
        print(f"  {business_type['type']}: {business_type['probability']:.3f}")
        print(f"    {business_type['characteristics']}")

    print("\nRecommendations:")
    for rec in analysis["recommendations"]:
        print(f"  - {rec}")

    print("\n" + "=" * 60)

    # Test batch analysis
    test_locations = [
        (-1.2921, 36.8219),  # Nairobi CBD
        (-1.3031, 36.8073),  # Kibera
        (-1.2634, 36.8059),  # Westlands
    ]

    print(f"\nBatch analyzing {len(test_locations)} locations...")
    batch_results = analyzer.batch_analyze_locations(test_locations)

    for i, result in enumerate(batch_results):
        if "analysis" in result:
            loc = result["location"]
            analysis = result["analysis"]
            print(f"Location {i+1}: ({loc['latitude']:.4f}, {loc['longitude']:.4f})")
            print(f"  Business Potential: {analysis['business_potential_score']:.3f}")
            print(
                f"  Top Business Type: {analysis['likely_business_types'][0]['type'] if analysis['likely_business_types'] else 'None'}"
            )

    print("\n" + "=" * 60)

    # Test heatmap generation (small grid for demo)
    print("\nGenerating heatmap data...")
    heatmap = analyzer.generate_heatmap_data(-1.29, 36.82, grid_size=3, bbox_size=0.02)

    print(f"Heatmap Summary:")
    print(f"  Total Points: {heatmap['summary']['total_points']}")
    print(f"  Average Potential: {heatmap['summary']['avg_potential']:.3f}")
    print(f"  Max Potential: {heatmap['summary']['max_potential']:.3f}")
    print(f"  High Potential Areas: {heatmap['summary']['high_potential_areas']}")
