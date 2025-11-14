from fastapi import FastAPI, Header, Body, Query
import uvicorn

app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

@app.get("/print/{name}")
def read_name(name: str = 'Amrit'):
    return {"Hello": name}

@app.get("/print/{name}/{age}")
def read_name_age(name: str, age: int):
    return {"Hello": name, "Age": age}

@app.get("/print/{name}/{age}/{city}")
def read_name_age_city(name: str, age: int, city: str):
    return {"Hello": name, "Age": age, "City": city}

@app.get("/header")
def use_header(name: str = Header("Amrit")):
    return f"Hello? {name}"

@app.get("/query_param")
def use_query_param(name: str = Query("Amrit")):
    return f"Hello? {name}"

@app.get("/body")
def use_body(name: str = Body("Amrit")):
    return f"Hello? {name}"

@app.post("/user_agent")
def user_agent(user_agent: str = Header("Amrit")):
    return user_agent

@app.post("/body")
def display_body(body: dict = Body(...)):
    return body

# if __name__ == "__main__":
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8000,
#         reload=True
#     )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
