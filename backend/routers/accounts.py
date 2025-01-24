from fastapi import APIRouter

accounts_router = APIRouter(prefix="/accounts", tags=["accounts"])

@accounts_router.get("/")
def get_accounts():
    pass

@accounts_router.get("/{account_id}")
def get_account(account_id: int):
    pass