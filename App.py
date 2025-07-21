from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os

from pipeline import process_bill_image_and_categorize

app = FastAPI(
    title="Bill Processing API",
    description="Upload a bill image to extract and categorize expenses",
    version="1.0.0"
)

@app.post("/process-bill")
async def process_bill(file: UploadFile = File(...)):
    """
    Accepts a bill image file (from JS or other client),
    runs the model pipeline, and returns JSON response.
    """
    # Save uploaded file to a temporary file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run the model pipeline
    try:
        result = process_bill_image_and_categorize(temp_path)
    except Exception as e:
        os.remove(temp_path)
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Clean up the temp file
    os.remove(temp_path)

    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
