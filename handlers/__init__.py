from .base import router as base_router
from .practice import router as practice_router
from .menu import router as menu_router
from .moderation import router as moderation_router
from .premium import router as premium_router
from .leaderboard import router as leaderboard_router

all_handlers = [
    base_router,
    practice_router,
    menu_router,
    moderation_router,
    premium_router,
    leaderboard_router
]

def register_all_handlers(dp):
    for router in all_handlers:
        dp.include_router(router)
