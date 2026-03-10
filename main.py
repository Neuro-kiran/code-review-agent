"""
Autonomous Code Review Agent
AI-powered pull request analyzer with bug detection, security scanning, and code improvement suggestions
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import json
import uuid
from datetime import datetime
import asyncio

from agents.code_analyzer import CodeAnalysisAgent
from agents.security_scanner import SecurityScanner
from agents.performance_analyzer import PerformanceAnalyzer
from utils.github_client import GitHubClient
from config.settings import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Code Review Agent",
    description="Autonomous AI-powered code review and analysis system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class CodeReviewRequest(BaseModel):
    repo_url: str
    pr_number: int
    analyze_security: bool = True
    analyze_performance: bool = True
    check_best_practices: bool = True

class ReviewComment(BaseModel):
    file: str
    line: int
    severity: str  # critical, high, medium, low
    category: str  # bug, security, performance, style, best_practice
    message: str
    suggested_fix: Optional[str]

class CodeReviewResponse(BaseModel):
    review_id: str
    repo: str
    pr_number: int
    status: str
    total_issues: int
    critical_issues: int
    comments: List[ReviewComment]
    summary: str
    processing_time: float
    timestamp: datetime

# Global instances
code_analyzer = CodeAnalysisAgent()
security_scanner = SecurityScanner()
performance_analyzer = PerformanceAnalyzer()
github_client = GitHubClient()
reviews = {}

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Code Review Agent...")
    await code_analyzer.initialize()
    await security_scanner.initialize()
    await performance_analyzer.initialize()
    logger.info("Code Review Agent initialized")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "code-review-agent",
        "version": "1.0.0"
    }

@app.post("/review-pr", response_model=CodeReviewResponse)
async def review_pull_request(
    request: CodeReviewRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze a GitHub pull request for bugs, security issues, and improvements
    """
    review_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        # Fetch PR details
        pr_data = await github_client.fetch_pr(request.repo_url, request.pr_number)
        
        # Extract changed files
        changed_files = await github_client.get_changed_files(
            request.repo_url, 
            request.pr_number
        )
        
        comments = []
        
        # Code analysis for bugs and issues
        logger.info(f"Analyzing code for PR #{request.pr_number}")
        code_issues = await code_analyzer.analyze_files(changed_files)
        comments.extend(code_issues)
        
        # Security scanning
        if request.analyze_security:
            logger.info(f"Scanning for security vulnerabilities in PR #{request.pr_number}")
            security_issues = await security_scanner.scan_files(changed_files)
            comments.extend(security_issues)
        
        # Performance analysis
        if request.analyze_performance:
            logger.info(f"Analyzing performance in PR #{request.pr_number}")
            perf_issues = await performance_analyzer.analyze_files(changed_files)
            comments.extend(perf_issues)
        
        # Count issues by severity
        critical_count = len([c for c in comments if c.severity == "critical"])
        
        # Generate summary
        summary = generate_review_summary(len(comments), critical_count)
        
        # Create review response
        processing_time = (datetime.now() - start_time).total_seconds()
        
        response = CodeReviewResponse(
            review_id=review_id,
            repo=request.repo_url,
            pr_number=request.pr_number,
            status="completed",
            total_issues=len(comments),
            critical_issues=critical_count,
            comments=comments,
            summary=summary,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
        # Store review
        reviews[review_id] = response
        
        # Post comments to GitHub in background
        if settings.POST_TO_GITHUB:
            background_tasks.add_task(
                post_review_to_github,
                request.repo_url,
                request.pr_number,
                comments
            )
        
        logger.info(f"Code review completed: {review_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in code review {review_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/review/{review_id}")
async def get_review(review_id: str):
    """Retrieve a previous review"""
    if review_id not in reviews:
        raise HTTPException(status_code=404, detail="Review not found")
    return reviews[review_id]

@app.post("/analyze-files")
async def analyze_uploaded_files(files: List[str]):
    """
    Analyze uploaded code files for issues
    """
    try:
        review_id = str(uuid.uuid4())
        
        # Analyze files
        comments = await code_analyzer.analyze_files(files)
        
        return {
            "review_id": review_id,
            "files_analyzed": len(files),
            "issues_found": len(comments),
            "comments": comments
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/review/{review_id}")
async def websocket_review(websocket: WebSocket, review_id: str):
    """
    WebSocket endpoint for real-time review updates
    """
    await websocket.accept()
    try:
        while True:
            if review_id in reviews:
                review = reviews[review_id]
                await websocket.send_json({
                    "review_id": review_id,
                    "status": review.status,
                    "total_issues": review.total_issues,
                    "critical_issues": review.critical_issues
                })
            else:
                await websocket.send_json({"error": "Review not found"})
            
            await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

def generate_review_summary(total_issues: int, critical_count: int) -> str:
    """Generate a summary of the code review"""
    if critical_count > 0:
        return f"Found {total_issues} issues ({critical_count} critical). Please address critical items before merging."
    elif total_issues > 0:
        return f"Found {total_issues} minor issues. Consider improvements for code quality."
    else:
        return "No issues found! Code looks good."

async def post_review_to_github(
    repo_url: str,
    pr_number: int,
    comments: List[ReviewComment]
):
    """Post review comments to GitHub PR"""
    try:
        logger.info(f"Posting {len(comments)} comments to GitHub PR")
        for comment in comments:
            await github_client.post_comment(
                repo_url,
                pr_number,
                comment.file,
                comment.line,
                comment.message
            )
        logger.info("Comments posted successfully")
    except Exception as e:
        logger.error(f"Error posting comments to GitHub: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL
    )
