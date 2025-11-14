from fastapi import FastAPI
from models import Tag, TagIn, TagOut
from fastapi.exceptions import HTTPException
from datetime import datetime
from service import Service

app = FastAPI()

items = []

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items")
def create_item(item: TagIn) -> TagIn:
    item: Tag = Tag(
        tag=item.tag,
        created=datetime.now()
    )
    Service.create(item)
    return item

@app.get("/items")
def get_items():
    return Service.get_items()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)