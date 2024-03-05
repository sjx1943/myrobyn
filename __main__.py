
from robyn import Robyn
from robyn.robyn import Request, Response
from sqlalchemy.orm import Session
import crud
from models import SessionLocal

app = Robyn(__file__)

@app.post("/crimes")
async def add_crime(request):
    with SessionLocal() as db:
        crime = request.json()
        insertion = crud.create_crime(db, crime)

    if insertion is None:
        raise Exception("Crime not added")

    return {
        "description": "Crime added successfully",
        "status_code": 200,
    }

@app.get("/crimes")
async def get_crimes(request):
    with SessionLocal() as db:
        skip = request.query_params.get("skip", 0)
        limit = request.query_params.get("limit", 100)
        crimes = crud.get_crimes(db, skip=skip, limit=limit)

    return crimes

@app.get("/crimes/:crime_id", auth_required=True)
async def get_crime(request):
    crime_id = int(request.path_params.get("crime_id"))
    with SessionLocal() as db:
        crime = crud.get_crime(db, crime_id=crime_id)

    if crime is None:
        raise Exception("Crime not found")

    return crime

@app.put("/crimes/:crime_id")
async def update_crime(request):
    crime = request.json()
    crime_id = int(request.path_params.get("crime_id"))
    with SessionLocal() as db:
        updated_crime = crud.update_crime(db, crime_id=crime_id, crime=crime)
    if updated_crime is None:
        raise Exception("Crime not found")
    return updated_crime

@app.delete("/crimes/{crime_id}")
async def delete_crime(request):
    crime_id = int(request.path_params.get("crime_id"))
    with SessionLocal() as db:
        success = crud.delete_crime(db, crime_id=crime_id)
    if not success:
        raise Exception("Crime not found")
    return {"message": "Crime deleted successfully"}


