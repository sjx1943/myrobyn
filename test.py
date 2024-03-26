from robyn import Robyn

from robyn import Request
app = Robyn(__file__)
@app.get("/")
async def h(request: Request) -> str:
    return "Hello, sgg"

app.start(port=8080, host="0.0.0.0") # host is optional, defaults to 127.0.0.1