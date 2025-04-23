import cv2  
import numpy as np
from fastapi import FastAPI, UploadFile, File, Response
from fastapi.responses import JSONResponse
from processor import processor

engine = FastAPI(title="YOLO Engine")
core = processor()

@engine.post("/detect")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    input = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    frame = core.process_frame(input)
    _, img_frame = cv2.imencode('.jpg', frame)

    return Response(content=img_frame.tobytes(), media_type="image/jpeg")
 


@engine.get("/stats")
async def get_stats():
    stats = core.get_stats()
    live_ids = core.get_live_ids()
    
    return JSONResponse(content={
        "stats": stats,
        "live_ids": live_ids,
    })
 

