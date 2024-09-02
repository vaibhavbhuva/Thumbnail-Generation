from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.graph import app_graph

from .routers import router as v1_router

load_dotenv()

app = FastAPI(
    title= "KB Image Generation API"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(v1_router)

@app.get("/")
def read_root():
    return {"This is": "Image Generation Application"}

# @app.post("/summarize/resource/{resource_id}", response_model=dict)
# async def summarize_resource(resource_id: str):

#     state = {
#         "contents": [],
#         "summaries": [],
#         "collapsed_summaries": [],
#         "final_summary": "",
#         "image_prompt": "",
#         "image_url": ""
#     }
    
#     try:
#         result = await app_graph.invoke(state)
#         return {
#             "final_summary": result["final_summary"],
#             "image_prompt": result["image_prompt"],
#             "image_url": result["image_url"]
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))