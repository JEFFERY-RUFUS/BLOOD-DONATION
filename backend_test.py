#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for AI Plant Care System
Tests all backend endpoints with proper data validation and error handling
"""

import requests
import json
import base64
import io
from PIL import Image
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://d5857de7-ad68-4c10-b47a-b69d277d3a86.preview.emergentagent.com/api"
TIMEOUT = 30

class PlantCareAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.test_plant_id = None
        self.test_alert_id = None
        self.results = {
            "plant_management": {"passed": 0, "failed": 0, "errors": []},
            "disease_detection": {"passed": 0, "failed": 0, "errors": []},
            "alert_system": {"passed": 0, "failed": 0, "errors": []},
            "dashboard_stats": {"passed": 0, "failed": 0, "errors": []},
            "sensor_data": {"passed": 0, "failed": 0, "errors": []}
        }

    def log_result(self, category, test_name, success, error_msg=None):
        """Log test results"""
        if success:
            self.results[category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.results[category]["failed"] += 1
            self.results[category]["errors"].append(f"{test_name}: {error_msg}")
            print(f"❌ {test_name}: {error_msg}")

    def create_test_image(self):
        """Create a test image for disease detection"""
        img = Image.new('RGB', (100, 100), color='green')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        return img_buffer

    def test_api_root(self):
        """Test API root endpoint"""
        print("\n🔍 Testing API Root Endpoint...")
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    print("✅ API Root endpoint working")
                    return True
                else:
                    print("❌ API Root endpoint - Invalid response format")
                    return False
            else:
                print(f"❌ API Root endpoint - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API Root endpoint - Error: {str(e)}")
            return False

    def test_plant_management(self):
        """Test Plant Profile Management API"""
        print("\n🌱 Testing Plant Profile Management API...")
        
        # Test 1: Create Plant
        try:
            plant_data = {
                "name": "Tomato Plant Alpha",
                "plant_type": "Tomato"
            }
            response = self.session.post(f"{BASE_URL}/plants", json=plant_data)
            
            if response.status_code == 200:
                plant = response.json()
                if "id" in plant and plant["name"] == plant_data["name"]:
                    self.test_plant_id = plant["id"]
                    self.log_result("plant_management", "Create Plant", True)
                else:
                    self.log_result("plant_management", "Create Plant", False, "Invalid response format")
            else:
                self.log_result("plant_management", "Create Plant", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("plant_management", "Create Plant", False, str(e))

        # Test 2: Get All Plants
        try:
            response = self.session.get(f"{BASE_URL}/plants")
            if response.status_code == 200:
                plants = response.json()
                if isinstance(plants, list):
                    self.log_result("plant_management", "Get All Plants", True)
                else:
                    self.log_result("plant_management", "Get All Plants", False, "Response not a list")
            else:
                self.log_result("plant_management", "Get All Plants", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("plant_management", "Get All Plants", False, str(e))

        # Test 3: Get Specific Plant
        if self.test_plant_id:
            try:
                response = self.session.get(f"{BASE_URL}/plants/{self.test_plant_id}")
                if response.status_code == 200:
                    plant = response.json()
                    if plant["id"] == self.test_plant_id:
                        self.log_result("plant_management", "Get Specific Plant", True)
                    else:
                        self.log_result("plant_management", "Get Specific Plant", False, "ID mismatch")
                else:
                    self.log_result("plant_management", "Get Specific Plant", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("plant_management", "Get Specific Plant", False, str(e))

        # Test 4: Water Plant
        if self.test_plant_id:
            try:
                response = self.session.post(f"{BASE_URL}/plants/{self.test_plant_id}/water")
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result:
                        self.log_result("plant_management", "Water Plant", True)
                    else:
                        self.log_result("plant_management", "Water Plant", False, "Invalid response format")
                else:
                    self.log_result("plant_management", "Water Plant", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("plant_management", "Water Plant", False, str(e))

    def test_disease_detection(self):
        """Test Disease Detection API with Mock AI"""
        print("\n🔬 Testing Disease Detection API...")
        
        if not self.test_plant_id:
            self.log_result("disease_detection", "Disease Detection", False, "No test plant available")
            return

        # Test 1: Upload Image for Disease Detection
        try:
            test_image = self.create_test_image()
            files = {'file': ('test_plant.jpg', test_image, 'image/jpeg')}
            
            response = self.session.post(f"{BASE_URL}/detect-disease/{self.test_plant_id}", files=files)
            
            if response.status_code == 200:
                result = response.json()
                required_fields = ["disease_name", "confidence", "severity", "treatment", "description", "recommendations"]
                if all(field in result for field in required_fields):
                    self.log_result("disease_detection", "Image Upload & Detection", True)
                else:
                    self.log_result("disease_detection", "Image Upload & Detection", False, "Missing required fields")
            else:
                self.log_result("disease_detection", "Image Upload & Detection", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("disease_detection", "Image Upload & Detection", False, str(e))

        # Test 2: Get Plant Detection History
        try:
            response = self.session.get(f"{BASE_URL}/plants/{self.test_plant_id}/detections")
            if response.status_code == 200:
                detections = response.json()
                if isinstance(detections, list):
                    self.log_result("disease_detection", "Get Detection History", True)
                else:
                    self.log_result("disease_detection", "Get Detection History", False, "Response not a list")
            else:
                self.log_result("disease_detection", "Get Detection History", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("disease_detection", "Get Detection History", False, str(e))

        # Test 3: Invalid File Upload
        try:
            files = {'file': ('test.txt', io.StringIO('not an image'), 'text/plain')}
            response = self.session.post(f"{BASE_URL}/detect-disease/{self.test_plant_id}", files=files)
            
            if response.status_code == 400:
                self.log_result("disease_detection", "Invalid File Rejection", True)
            else:
                self.log_result("disease_detection", "Invalid File Rejection", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("disease_detection", "Invalid File Rejection", False, str(e))

    def test_sensor_data(self):
        """Test Sensor Data API"""
        print("\n📊 Testing Sensor Data API...")
        
        if not self.test_plant_id:
            self.log_result("sensor_data", "Sensor Data", False, "No test plant available")
            return

        # Test 1: Add Sensor Data
        try:
            sensor_data = {
                "soil_moisture": 45.5,
                "temperature": 22.3,
                "humidity": 65.2,
                "light_level": 450.0
            }
            response = self.session.post(f"{BASE_URL}/plants/{self.test_plant_id}/sensor-data", json=sensor_data)
            
            if response.status_code == 200:
                result = response.json()
                required_fields = ["id", "plant_id", "soil_moisture", "temperature", "humidity", "light_level", "timestamp"]
                if all(field in result for field in required_fields):
                    self.log_result("sensor_data", "Add Sensor Data", True)
                else:
                    self.log_result("sensor_data", "Add Sensor Data", False, "Missing required fields")
            else:
                self.log_result("sensor_data", "Add Sensor Data", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("sensor_data", "Add Sensor Data", False, str(e))

        # Test 2: Get Sensor Data
        try:
            response = self.session.get(f"{BASE_URL}/plants/{self.test_plant_id}/sensor-data")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("sensor_data", "Get Sensor Data", True)
                else:
                    self.log_result("sensor_data", "Get Sensor Data", False, "Response not a list")
            else:
                self.log_result("sensor_data", "Get Sensor Data", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("sensor_data", "Get Sensor Data", False, str(e))

        # Test 3: Low Moisture Alert Generation
        try:
            low_moisture_data = {
                "soil_moisture": 25.0,  # Below 30 threshold
                "temperature": 22.0,
                "humidity": 60.0,
                "light_level": 400.0
            }
            response = self.session.post(f"{BASE_URL}/plants/{self.test_plant_id}/sensor-data", json=low_moisture_data)
            
            if response.status_code == 200:
                # Check if alert was created
                time.sleep(1)  # Brief delay for alert creation
                alerts_response = self.session.get(f"{BASE_URL}/plants/{self.test_plant_id}/alerts")
                if alerts_response.status_code == 200:
                    alerts = alerts_response.json()
                    low_moisture_alerts = [a for a in alerts if a.get("alert_type") == "low_moisture"]
                    if low_moisture_alerts:
                        self.log_result("sensor_data", "Low Moisture Alert Generation", True)
                    else:
                        self.log_result("sensor_data", "Low Moisture Alert Generation", False, "No low moisture alert created")
                else:
                    self.log_result("sensor_data", "Low Moisture Alert Generation", False, "Could not fetch alerts")
            else:
                self.log_result("sensor_data", "Low Moisture Alert Generation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("sensor_data", "Low Moisture Alert Generation", False, str(e))

    def test_alert_system(self):
        """Test Alert System API"""
        print("\n🚨 Testing Alert System API...")
        
        if not self.test_plant_id:
            self.log_result("alert_system", "Alert System", False, "No test plant available")
            return

        # Test 1: Get Plant Alerts
        try:
            response = self.session.get(f"{BASE_URL}/plants/{self.test_plant_id}/alerts")
            if response.status_code == 200:
                alerts = response.json()
                if isinstance(alerts, list):
                    self.log_result("alert_system", "Get Plant Alerts", True)
                    if alerts:
                        self.test_alert_id = alerts[0]["id"]
                else:
                    self.log_result("alert_system", "Get Plant Alerts", False, "Response not a list")
            else:
                self.log_result("alert_system", "Get Plant Alerts", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("alert_system", "Get Plant Alerts", False, str(e))

        # Test 2: Get All Alerts
        try:
            response = self.session.get(f"{BASE_URL}/alerts")
            if response.status_code == 200:
                alerts = response.json()
                if isinstance(alerts, list):
                    self.log_result("alert_system", "Get All Alerts", True)
                else:
                    self.log_result("alert_system", "Get All Alerts", False, "Response not a list")
            else:
                self.log_result("alert_system", "Get All Alerts", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("alert_system", "Get All Alerts", False, str(e))

        # Test 3: Resolve Alert
        if self.test_alert_id:
            try:
                response = self.session.patch(f"{BASE_URL}/alerts/{self.test_alert_id}/resolve")
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result:
                        self.log_result("alert_system", "Resolve Alert", True)
                    else:
                        self.log_result("alert_system", "Resolve Alert", False, "Invalid response format")
                else:
                    self.log_result("alert_system", "Resolve Alert", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("alert_system", "Resolve Alert", False, str(e))

    def test_dashboard_stats(self):
        """Test Dashboard Statistics API"""
        print("\n📈 Testing Dashboard Statistics API...")
        
        try:
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_plants", "total_detections", "active_alerts", "healthy_plants", "health_percentage"]
                if all(field in stats for field in required_fields):
                    # Validate data types
                    if (isinstance(stats["total_plants"], int) and 
                        isinstance(stats["total_detections"], int) and
                        isinstance(stats["active_alerts"], int) and
                        isinstance(stats["healthy_plants"], int) and
                        isinstance(stats["health_percentage"], (int, float))):
                        self.log_result("dashboard_stats", "Get Dashboard Stats", True)
                    else:
                        self.log_result("dashboard_stats", "Get Dashboard Stats", False, "Invalid data types")
                else:
                    self.log_result("dashboard_stats", "Get Dashboard Stats", False, "Missing required fields")
            else:
                self.log_result("dashboard_stats", "Get Dashboard Stats", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("dashboard_stats", "Get Dashboard Stats", False, str(e))

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        if self.test_plant_id:
            try:
                response = self.session.delete(f"{BASE_URL}/plants/{self.test_plant_id}")
                if response.status_code == 200:
                    print("✅ Test plant deleted successfully")
                else:
                    print(f"⚠️ Could not delete test plant: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error deleting test plant: {str(e)}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🧪 BACKEND API TEST SUMMARY")
        print("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.replace('_', ' ').title()}: {passed} passed, {failed} failed {status}")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  - {error}")
        
        print("-" * 60)
        print(f"TOTAL: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 ALL BACKEND TESTS PASSED!")
        else:
            print(f"⚠️ {total_failed} TESTS FAILED - NEEDS ATTENTION")
        
        return total_failed == 0

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Backend API Tests...")
        print(f"Testing against: {BASE_URL}")
        
        # Test API connectivity first
        if not self.test_api_root():
            print("❌ Cannot connect to API. Aborting tests.")
            return False
        
        # Run all test suites
        self.test_plant_management()
        self.test_disease_detection()
        self.test_sensor_data()
        self.test_alert_system()
        self.test_dashboard_stats()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        return self.print_summary()

if __name__ == "__main__":
    tester = PlantCareAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)