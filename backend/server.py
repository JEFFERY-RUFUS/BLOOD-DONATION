from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import random
import base64
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class PlantProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    plant_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_watered: Optional[datetime] = None
    soil_moisture: Optional[float] = None
    health_status: str = "healthy"

class PlantProfileCreate(BaseModel):
    name: str
    plant_type: str

class DiseaseDetection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plant_id: str
    image_data: str
    disease_name: str
    confidence: float
    severity: str
    treatment: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DiseaseDetectionResponse(BaseModel):
    disease_name: str
    confidence: float
    severity: str
    treatment: str
    description: str
    recommendations: List[str]

class SensorData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plant_id: str
    soil_moisture: float
    temperature: float
    humidity: float
    light_level: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plant_id: str
    alert_type: str
    message: str
    severity: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False

# Mock disease detection data
MOCK_DISEASES = [
    {
        "name": "Tomato Late Blight",
        "severity": "High",
        "treatment": "Remove affected leaves immediately. Apply copper-based fungicide every 7-10 days. Ensure good air circulation.",
        "description": "A serious fungal disease that causes dark, water-soaked spots on leaves and stems. Can spread rapidly in humid conditions.",
        "recommendations": [
            "Improve air circulation around plants",
            "Water at soil level to avoid wetting leaves",
            "Apply preventive fungicide sprays",
            "Remove and destroy infected plant material"
        ]
    },
    {
        "name": "Powdery Mildew",
        "severity": "Medium",
        "treatment": "Spray with baking soda solution (1 tsp per quart of water). Improve air circulation and reduce humidity.",
        "description": "White, powdery fungal growth on leaf surfaces. Common in humid conditions with poor air circulation.",
        "recommendations": [
            "Increase spacing between plants",
            "Water in the morning to allow leaves to dry",
            "Apply neem oil or horticultural oil",
            "Remove severely affected leaves"
        ]
    },
    {
        "name": "Bacterial Leaf Spot",
        "severity": "Medium",
        "treatment": "Remove affected leaves and apply copper-based bactericide. Avoid overhead watering.",
        "description": "Small, dark spots with yellow halos on leaves. Caused by bacterial infection, often spread by water splash.",
        "recommendations": [
            "Use drip irrigation instead of overhead watering",
            "Apply copper-based treatments",
            "Remove infected plant debris",
            "Improve garden sanitation"
        ]
    },
    {
        "name": "Healthy Plant",
        "severity": "None",
        "treatment": "Continue current care routine. Monitor regularly for any changes.",
        "description": "Your plant appears healthy with no signs of disease. Keep up the good work!",
        "recommendations": [
            "Maintain consistent watering schedule",
            "Ensure adequate sunlight exposure",
            "Monitor for early signs of stress",
            "Continue regular fertilization"
        ]
    }
]

# Plant Care Routes
@api_router.get("/")
async def root():
    return {"message": "AI Plant Care System API"}

@api_router.post("/plants", response_model=PlantProfile)
async def create_plant(plant: PlantProfileCreate):
    plant_dict = plant.dict()
    plant_obj = PlantProfile(**plant_dict)
    await db.plants.insert_one(plant_obj.dict())
    return plant_obj

@api_router.get("/plants", response_model=List[PlantProfile])
async def get_plants():
    plants = await db.plants.find().to_list(1000)
    return [PlantProfile(**plant) for plant in plants]

@api_router.get("/plants/{plant_id}", response_model=PlantProfile)
async def get_plant(plant_id: str):
    plant = await db.plants.find_one({"id": plant_id})
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return PlantProfile(**plant)

@api_router.delete("/plants/{plant_id}")
async def delete_plant(plant_id: str):
    result = await db.plants.delete_one({"id": plant_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"message": "Plant deleted successfully"}

# Disease Detection Routes
@api_router.post("/detect-disease/{plant_id}")
async def detect_disease(plant_id: str, file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and encode image
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Mock AI disease detection
        disease_info = random.choice(MOCK_DISEASES)
        confidence = random.uniform(0.75, 0.95) if disease_info["name"] != "Healthy Plant" else random.uniform(0.85, 0.98)
        
        # Create detection record
        detection = DiseaseDetection(
            plant_id=plant_id,
            image_data=image_base64,
            disease_name=disease_info["name"],
            confidence=confidence,
            severity=disease_info["severity"],
            treatment=disease_info["treatment"],
            description=disease_info["description"]
        )
        
        await db.detections.insert_one(detection.dict())
        
        # Create alert if disease detected
        if disease_info["name"] != "Healthy Plant":
            alert = Alert(
                plant_id=plant_id,
                alert_type="disease_detected",
                message=f"Disease detected: {disease_info['name']}",
                severity=disease_info["severity"].lower()
            )
            await db.alerts.insert_one(alert.dict())
        
        return DiseaseDetectionResponse(
            disease_name=disease_info["name"],
            confidence=round(confidence * 100, 1),
            severity=disease_info["severity"],
            treatment=disease_info["treatment"],
            description=disease_info["description"],
            recommendations=disease_info["recommendations"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@api_router.get("/plants/{plant_id}/detections")
async def get_plant_detections(plant_id: str):
    detections = await db.detections.find({"plant_id": plant_id}).sort("timestamp", -1).to_list(50)
    return [DiseaseDetection(**detection) for detection in detections]

# Sensor Data Routes
@api_router.post("/plants/{plant_id}/sensor-data")
async def add_sensor_data(plant_id: str, data: dict):
    # Generate realistic sensor data
    sensor_data = SensorData(
        plant_id=plant_id,
        soil_moisture=data.get("soil_moisture", random.uniform(30, 80)),
        temperature=data.get("temperature", random.uniform(18, 28)),
        humidity=data.get("humidity", random.uniform(40, 70)),
        light_level=data.get("light_level", random.uniform(200, 800))
    )
    
    await db.sensor_data.insert_one(sensor_data.dict())
    
    # Check for alerts
    if sensor_data.soil_moisture < 30:
        alert = Alert(
            plant_id=plant_id,
            alert_type="low_moisture",
            message="Soil moisture is low. Consider watering your plant.",
            severity="medium"
        )
        await db.alerts.insert_one(alert.dict())
    
    return sensor_data

@api_router.get("/plants/{plant_id}/sensor-data")
async def get_sensor_data(plant_id: str):
    data = await db.sensor_data.find({"plant_id": plant_id}).sort("timestamp", -1).to_list(100)
    return [SensorData(**item) for item in data]

# Alerts Routes
@api_router.get("/plants/{plant_id}/alerts")
async def get_plant_alerts(plant_id: str):
    alerts = await db.alerts.find({"plant_id": plant_id}).sort("timestamp", -1).to_list(50)
    return [Alert(**alert) for alert in alerts]

@api_router.get("/alerts")
async def get_all_alerts():
    alerts = await db.alerts.find().sort("timestamp", -1).to_list(100)
    return [Alert(**alert) for alert in alerts]

@api_router.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    result = await db.alerts.update_one(
        {"id": alert_id},
        {"$set": {"resolved": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved"}

# Dashboard Stats
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    total_plants = await db.plants.count_documents({})
    total_detections = await db.detections.count_documents({})
    active_alerts = await db.alerts.count_documents({"resolved": False})
    healthy_plants = await db.detections.count_documents({"disease_name": "Healthy Plant"})
    
    return {
        "total_plants": total_plants,
        "total_detections": total_detections,
        "active_alerts": active_alerts,
        "healthy_plants": healthy_plants,
        "health_percentage": round((healthy_plants / max(total_detections, 1)) * 100, 1)
    }

# Water scheduling
@api_router.post("/plants/{plant_id}/water")
async def water_plant(plant_id: str):
    result = await db.plants.update_one(
        {"id": plant_id},
        {"$set": {"last_watered": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"message": "Plant watered successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()