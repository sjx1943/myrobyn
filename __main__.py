from http.client import HTTPException

import frontend
from robyn import Robyn, WebSocket
from robyn.robyn import Request, Response, jsonify
from robyn.scaffold.mongo.app import db
from sqlalchemy.orm import Session
import crud
from models import SessionLocal
from robyn.authentication import AuthenticationHandler, BearerGetter, Identity
import os
import pathlib
from robyn.templating import JinjaTemplate

app = Robyn(__file__)

current_file_path = pathlib.Path(__file__).parent.resolve()
jinja_template = JinjaTemplate(os.path.join(current_file_path, "templates"))

@app.get("/frontend")
async def get_frontend(request):
    context = {"framework": "Robyn", "templating_engine": "Jinja2"}
    return jinja_template.render_template("index.html", **context)

app.include_router(frontend)


websocket = WebSocket(app, "/notifications")

@websocket.on("connect")
async def notify_connect():
    return "Connected to notifications"

@websocket.on("message")
async def notify_message(message):
    return f"Received: {message}"

@websocket.on("close")
async def notify_close():
    return "Disconnected from notifications"

class BasicAuthHandler(AuthenticationHandler):
    def authenticate(self, request: Request):
        token = self.token_getter.get_token(request)

        try:
            payload = crud.decode_access_token(token)
            username = payload["sub"]
        except Exception:
            return

        with SessionLocal() as db:
            user = crud.get_user_by_username(db, username=username)

        return Identity(claims={"user": f"{ user }"})


app.configure_authentication(BasicAuthHandler(token_getter=BearerGetter()))


@app.get("/users/me", auth_required=True)
async def get_current_user(request):
    user = request.identity.claims["user"]
    return user


@app.post("/users/register")
async def register_user(request):
    user = request.json()
    with SessionLocal() as db:
        created_user = crud.create_user(db, user)
    return created_user

@app.post("/users/login")
async def login_user(request):
    user = request.json()
    with SessionLocal() as db:
        token = crud.authenticate_user(db, **user)

    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")


    return jsonify({"access_token": token})



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

@app.get("/crimes/search")
async def search_crimes(request):
    crime_type = request.query_params.get("crime_type")
    date = request.query_params.get("date")
    location = request.query_params.get("location")
    status = request.query_params.get("status")

    crimes = crud.search_crimes(db, crime_type=crime_type, date=date, location=location, status=status)
    return crimes


