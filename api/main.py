import logging
import uvicorn
from fastapi.responses import JSONResponse
from fastapi import FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
import routes.login_route as login
import routes.member_route as member 
import routes.event_route as event
import routes.subscription_routes as subscription
from fastapi.staticfiles import StaticFiles


app = FastAPI()

version_router = APIRouter()

version_router.include_router(login.router, tags=["login"])
version_router.include_router(member.router, tags=["member"])
version_router.include_router(event.router, tags=["event"])
version_router.include_router(subscription.router, tags=["subscription"])
app.include_router(version_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
@app.get("/")
async def ping():
    return JSONResponse(content={"status": "success", "message": "Pong!"}, status_code=200)


app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)




