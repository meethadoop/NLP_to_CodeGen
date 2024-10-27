from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

from nlsql.main import NLSQL
from nlsql.config import Config, load_config
from nlsql.utils.logger import get_logger

logger = get_logger(__name__)

class QueryRequest(BaseModel):
    query: str
    use_cache: bool = True
    export_format: Optional[str] = None

class TemplateRequest(BaseModel):
    template_name: str
    parameters: Dict[str, str]
    export_format: Optional[str] = None

class TemplateDefinition(BaseModel):
    name: str
    description: str
    template: str
    parameters: List[str]

app = FastAPI(
    title="NLSQL API",
    description="Natural Language to SQL Query Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global NLSQL instance
nlsql_instance = None

async def get_nlsql():
    global nlsql_instance
    if nlsql_instance is None:
        config = load_config()
        nlsql_instance = NLSQL(config)
    return nlsql_instance

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/templates")
async def list_templates(nlsql: NLSQL = Depends(get_nlsql)):
    """List all available query templates"""
    try:
        templates = nlsql.template_manager.list_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/templates")
async def add_template(
    template: TemplateDefinition,
    nlsql: NLSQL = Depends(get_nlsql)
):
    """Add a new query template"""
    try:
        nlsql.add_query_template(
            template.name,
            template.description,
            template.template,
            template.parameters
        )
        return {"message": f"Template '{template.name}' added successfully"}
    except Exception as e:
        logger.error(f"Error adding template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query")
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    nlsql: NLSQL = Depends(get_nlsql)
):
    """Process a natural language query"""
    try:
        result = await nlsql.process_query(request.query, use_cache=request.use_cache)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query/template")
async def process_template(
    request: TemplateRequest,
    background_tasks: BackgroundTasks,
    nlsql: NLSQL = Depends(get_nlsql)
):
    """Process a query using a template"""
    try:
        result = await nlsql.process_template(
            request.template_name,
            request.parameters
        )
        return JSONResponse(content=result)
    except ValueError as e:
        logger.error(f"Template error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Template processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/statistics")
async def get_statistics(nlsql: NLSQL = Depends(get_nlsql)):
    """Get query execution statistics"""
    try:
        return nlsql.get_query_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
