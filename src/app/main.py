from fastapi import FastAPI, HTTPException, Response
from app.schemas import EntryCreate, EntryUpdate

app = FastAPI(title = "DevDiary")

entries = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/entries",status_code = 201)
def create_entry(entry: EntryCreate):
    new_entry = {
        "id": len(entries) +1,
        "title": entry.title,
        "content": entry.content
    }

    entries.append(new_entry)
    return new_entry


@app.get("/entries")
def get_entries():
    return entries


@app.get("/entries/{entry_id}")
def get_entry(entry_id: int):

    print("Requested ID:", entry_id)
    print("Current entries:", entries)

    for entry in entries:
        if entry["id"] == entry_id:
            return entry
        
    raise HTTPException(
        status_code = 404,
        detail = f"Entry with id {entry_id} not found"
    )

@app.patch("/entries/{entry_id}")
def update_entry(entry_id: int, entry_update: EntryUpdate):
        for entry in entries: 
            
            if entry["id"] == entry_id:
    
                if entry_update.title is not None: 
                    entry["title"] = entry_update.title

                if entry_update.content is not None: 
                     entry["content"] = entry_update.content

                return entry
        
        raise HTTPException(
            status_code=404,
            detail=f"Entry with id {entry_id} not found"
        )

@app.delete("/entries/{entry_id}", status_code =204)
def delete_entry(entry_id: int):
    
    for index, entry in enumerate(entries):
        if entry["id"] ==  entry_id:
            deleted_entry = entries.pop(index)

            return {
                "message": "Entry deleted successfully",
                "entry": deleted_entry
            }
    
    raise HTTPException(
        status_code=404,
        detail=f"Entry with id {entry_id} not found"
    )

