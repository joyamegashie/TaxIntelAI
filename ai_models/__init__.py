"""
TaxIntel AI - AI/ML Models Package

This package contains the core AI and machine learning models for the TaxIntel AI platform:

- business_detector.py: AI model for detecting informal businesses from satellite imagery
- tax_estimator.py: AI model for estimating tax potential and revenue opportunities  
- satellite_analyzer.py: Satellite imagery analysis and feature extraction
- report_generator.py: GPT-powered document and report generation

These models work together to provide comprehensive tax intelligence capabilities.
"""

from .business_detector import BusinessDetector
from .tax_estimator import TaxEstimator
from .satellite_analyzer import SatelliteAnalyzer

__all__ = ['BusinessDetector', 'TaxEstimator', 'SatelliteAnalyzer']

