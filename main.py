from fastapi import FastAPI, Query
from seo_audit import audit_url

app = FastAPI(title="SEO Audit Tool API")

@app.get("/")
def home():
    return {"message": "SEO Audit API is running"}

@app.get("/api/v1/audit")
def run_audit(url: str = Query(..., description="Target website URL")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return audit_url(url)