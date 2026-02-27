from fastapi import FastAPI
from app.database import engine, Base

from app.models import client, otp
from app.routers import auth_router

from app.models import client_basic_details
from app.routers import client_router
from app.routers import poc_router
from app.routers import client_tentative_counts_router
from app.routers import client_integrations_router
from app.routers import client_crm_info_router
from app.routers import crm_migration_documents_router
from app.routers import client_module_router
from app.routers import client_pipeline_router


app = FastAPI(title="CRM Onboarding System") 

# Auth Router
app.include_router(auth_router.router)

# Client Bacis Details Router 
app.include_router(client_router.router)

# POC Details Router
app.include_router(poc_router.router)

# Tentative counts
app.include_router(client_tentative_counts_router.router)

# Client Integration
app.include_router(client_integrations_router.router)

# Client Old CRM Info
app.include_router(client_crm_info_router.router)

# Client Old CRM data migration
from app.routers import crm_migration_documents_router

# Modules and Subscription
app.include_router(client_module_router.router)

# Tags and stages pipeline
app.include_router(client_pipeline_router.router)


@app.get("/")
def root():
    return {"message": "CRM Backend Running"}
