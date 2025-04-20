from .base import router as base_router
from .practice import router as practice_router
from .menu import router as menu_router
from .moderation import router as moderation_router
from .submit_word import router as submit_word
from .premium import router as premium_router
from .leaderboard import router as leaderboard_router
from .add_new_words import router as add_new_words

all_handlers = [
    base_router,
    practice_router,
    menu_router,
    submit_word,
    moderation_router,
    premium_router,
    leaderboard_router,
    add_new_words
]

def register_all_handlers(dp):

    for router in all_handlers:
        dp.include_router(router)

