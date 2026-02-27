import uuid
import json
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import logging
from sqlalchemy.orm import Session
from models.analysis_request import AnalysisRequest
from models.database import AnalysisHistory, get_db
from services.static_analyzer import run_static_analysis
from services.groq_service import analyze_with_groq
from services.aggregation_engine import aggregate_issues
from services.confidence_engine import compute_confidence
from middleware.auth_middleware import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def analyze(
    request: AnalysisRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # 1. Run static analysis
        static_issues = run_static_analysis(request.language, request.code)

        # 2. Get AI analysis from Groq
        groq_result = analyze_with_groq(
            language=request.language,
            mode=request.mode,
            instruction=request.instruction,
            code=request.code,
            static_issues=static_issues,
        )

        # 3. Aggregate static + AI issues
        aggregated = aggregate_issues(static_issues, groq_result["ai_issues"])

        # 4. Compute confidence score
        confidence = compute_confidence(aggregated)

        # 5. Store analysis result
        history = AnalysisHistory(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            project_id=getattr(request, "project_id", None),
            code_input=request.code,
            ai_output=json.dumps({
                "ai_suggestions": groq_result["ai_issues"],
                "optimized_code": groq_result["optimized_code"],
                "explanation": groq_result.get("explanation", ""),
            }),
        )
        db.add(history)
        db.commit()

        return {
            "static_issues": static_issues,
            "ai_suggestions": groq_result["ai_issues"],
            "aggregated_issues": aggregated,
            "optimized_code": groq_result["optimized_code"],
            "explanation": groq_result.get("explanation", ""),
            "confidence_score": confidence,
        }
    except Exception as e:
        logger.error(f"Analysis endpoint error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={
            "static_issues": [],
            "ai_suggestions": [],
            "aggregated_issues": [],
            "optimized_code": request.code,
            "explanation": f"Server error: {str(e)}",
            "confidence_score": 0,
        })
