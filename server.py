from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from checker import Checker
from fastapi import FastAPI
from config import Configuration
from distutils.util import strtobool
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

def create_dict(errors):
    dict = errors.__dict__.copy()
    dict['time'] = errors.time.strftime('%x %X')
    dict['report'] = errors.get_string_report()
    return dict

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)

@app.get("/get-errors")
def get_errors():
    errors = checker.check_errors()
    return create_dict(errors)

@app.get("/last-errors")
def get_last_errors():
    errors = checker.last_errors
    return create_dict(errors)

@app.get("/")
async def main():
    return RedirectResponse(url='/index.html')

app.mount("/", StaticFiles(directory="front"), name="static")

if __name__ == "__main__":
    checker = Checker()
    config = Configuration()
    automatic_check = strtobool(config['AutomaticCheck'])
    if automatic_check:
        checker.run_in_background()
    uvicorn.run(app, host=config['Host'], port=int(config['Port']))