from fastapi import APIRouter, HTTPException, status
from app.db.health import check_database

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        status: "healthy" or "unhealthy"
        database: true if DB is connected
    """
    db_ok = await check_database()
    
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": db_ok,
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes/Docker.
    
    Returns 200 only if all dependencies are ready.
    """
    db_ok = await check_database()
    
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not ready",
        )
    
    return {"ready": True}