"""
FastAPI server for Traffic Advisory Chatbot
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn
from typing import Literal
from datetime import datetime


from chatbot.traffic_advisor import TrafficAdvisoryChatbot, ChatbotResponse
from chatbot.response_formatter import ResponseFormatter

# Initialize FastAPI app
app = FastAPI(
    title="Adaptive Traffic Signal Advisory System",
    description="AI-powered traffic signal timing recommendations for traffic police",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = TrafficAdvisoryChatbot(area_type="urban")

# Pydantic models
class VehicleCounts(BaseModel):
    car: int = 0
    motorcycle: int = 0
    auto: int = 0
    bus: int = 0
    truck: int = 0
    bicycle: int = 0

class ApproachData(BaseModel):
    approach_id: Literal["N", "S", "E", "W"]
    vehicle_counts: VehicleCounts
    queue_length: float = Field(..., ge=0)
    lanes: int = Field(..., ge=1, le=4)
    congestion_level: Literal[
        "free",
        "stable",
        "congested",
        "severely_congested"
    ]
    pedestrian_count: int = Field(..., ge=0)
    current_green_time: float = Field(..., gt=0)
    link_length: Optional[float] = None


class TrafficRequest(BaseModel):
    approaches: List[ApproachData]
    current_cycle_time: float = 120
    emergency_vehicle_present: bool = False
    time_of_day: Optional[str] = None
    format: Literal["text", "json", "html"] = "text"

@app.get("/")
async def root():
    """Root endpoint with system info"""
    return {
        "system": "Adaptive Traffic Signal Advisory System",
        "version": "1.0.0",
        "description": "AI assistant for traffic signal timing recommendations",
        "endpoints": {
            "GET /": "This information",
            "POST /advise": "Get signal timing recommendations",
            "GET /health": "System health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "traffic_advisory_chatbot",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/advise")
async def get_signal_advice(request: TrafficRequest):
    """
    Get signal timing recommendations based on traffic metrics
    
    Example request:
    ```json
    {
        "approaches": [
            {
                "approach_id": "N",
                "vehicle_counts": {"car": 10, "motorcycle": 5},
                "queue_length": 75.5,
                "lanes": 2,
                "congestion_level": "congested",
                "pedestrian_count": 8,
                "current_green_time": 30,
                "link_length": 100
            },
            {
                "approach_id": "S",
                "vehicle_counts": {"car": 5, "bus": 2},
                "queue_length": 40.0,
                "lanes": 1,
                "congestion_level": "stable",
                "pedestrian_count": 3,
                "current_green_time": 25,
                "link_length": 80
            }
        ],
        "current_cycle_time": 120,
        "emergency_vehicle_present": false,
        "time_of_day": "peak"
    }
    ```
    """
    try:
        # Convert to dict for processing
        request_dict = request.model_dump()
        
        # Process with chatbot
        response = chatbot.process_request(request_dict)
        
        # Format response based on requested format
        if request.format == "json":
            return ResponseFormatter.to_json(response)
        elif request.format == "html":
            return ResponseFormatter.to_html(response)
        else:  # default to text
            return ResponseFormatter.to_plain_text(response)
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/quick_advice")
async def quick_advice(
    north_cars: int = Query(0, ge=0),
    south_cars: int = Query(0, ge=0),
    east_cars: int = Query(0, ge=0),
    west_cars: int = Query(0, ge=0),
   congestion: Literal[
    "free",
    "stable",
    "congested",
    "severely_congested"
] = Query("stable")

):
    """Quick advice endpoint for simple queries"""
    try:
        # Create simple request
        request_data = {
            "approaches": [],
            "current_cycle_time": 120,
            "emergency_vehicle_present": False
        }
        
        # Add approaches with data
        approaches = [
            ("N", north_cars),
            ("S", south_cars),
            ("E", east_cars),
            ("W", west_cars)
        ]
        
        for approach_id, car_count in approaches:
            if car_count > 0:
                request_data["approaches"].append({
                    "approach_id": approach_id,
                    "vehicle_counts": {"car": car_count},
                    "queue_length": car_count * 7.5,  # Estimate
                    "lanes": 1,
                    "congestion_level": congestion,
                    "pedestrian_count": 2,
                    "current_green_time": 30
                })
        
        if not request_data["approaches"]:
            return {"error": "No traffic data provided"}
        
        # Get advice
        response = chatbot.process_request(request_data)
        return ResponseFormatter.to_plain_text(response)
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )