"""
CLI command to refresh the leaderboard cache.
This can be used in cron jobs or scheduled tasks.
"""
import asyncio
import sys

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.services.leaderboard import refresh_leaderboard_cache


async def refresh_leaderboard() -> None:
    """Refresh the leaderboard cache from users' XP data."""
    async with AsyncSessionLocal() as db:
        try:
            print("Starting leaderboard cache refresh...")
            entries_updated = await refresh_leaderboard_cache(db)
            print(f"✓ Successfully refreshed leaderboard cache")
            print(f"  Updated {entries_updated} entries")
        except Exception as e:
            print(f"✗ Error refreshing leaderboard cache: {e}")
            sys.exit(1)


def main() -> None:
    """Main entry point for the CLI command."""
    asyncio.run(refresh_leaderboard())


if __name__ == "__main__":
    main()
