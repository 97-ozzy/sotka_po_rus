from .base import router as base_router
from .practice import router as practice_router
from .submit_word import router as submit_word_router
from .premium import router as premium_router
from .leaderboard import router as leaderboard_router
from .info_support import router as support_router
from .stats import router as stats
from .admin_commands import router as admin_commands
from .referral_system import router as referral_system

all_handlers = [
    base_router,
    practice_router,
    admin_commands,
    submit_word_router,
    premium_router,
    referral_system,
    leaderboard_router,
    support_router,
    stats
]

def register_all_handlers(dp):

    for router in all_handlers:
        dp.include_router(router)

