from robyn import Robyn, logger, Response, Request
from .frontend import frontend
app = Robyn(__file__)
app.include_router(frontend)
logger = logger(app)

def sync_decorator_view():
    def get():
        return "Hello, world!"

    def post(request: Request):
        body = request.body
        return {"status_code": 200, "description": body}

app.add_view("/sync/view/decorator", sync_decorator_view)
@app.view("/sync/view/decorator")
def sync_decorator_view():
    def get():
        return "Hello, world!"

    def post(request: Request):
        body = request.body
        return {"status_code": 200, "description": body}


@app.before_request()
async def log_request(request: Request):
    logger.info(f"Received request: %s", request)

@app.after_request()
async def log_response(response: Response):
    logger.info(f"Sending response: %s", response)

@app.get("/")
def index():
    return "Hello SGG!"


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=8080)
