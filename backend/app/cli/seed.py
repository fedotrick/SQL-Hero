import asyncio
import sys
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.cli.seed_data import ACHIEVEMENTS_DATA, LESSONS_DATA, MODULES_DATA
from app.core.config import get_settings
from app.models.database import Achievement, Lesson, Module


async def seed_modules(session: AsyncSession) -> dict[int, Module]:
    print("Seeding modules...")
    module_map: dict[int, Module] = {}
    
    for module_data in MODULES_DATA:
        result = await session.execute(
            select(Module).where(Module.order == module_data["order"])
        )
        existing_module = result.scalar_one_or_none()
        
        if existing_module:
            print(f"  Module '{module_data['title']}' already exists (order {module_data['order']}), skipping...")
            module_map[module_data["order"]] = existing_module
        else:
            module = Module(**module_data)
            session.add(module)
            await session.flush()
            module_map[module_data["order"]] = module
            print(f"  Created module '{module_data['title']}' (order {module_data['order']})")
    
    await session.commit()
    print(f"Modules seeding completed: {len(module_map)} modules")
    return module_map


async def seed_lessons(session: AsyncSession, module_map: dict[int, Module]) -> None:
    print("Seeding lessons...")
    total_lessons = 0
    
    for module_lessons_data in LESSONS_DATA:
        module_order = module_lessons_data["module_order"]
        module = module_map.get(module_order)
        
        if not module:
            print(f"  Warning: Module with order {module_order} not found, skipping lessons...")
            continue
        
        for lesson_data in module_lessons_data["lessons"]:
            result = await session.execute(
                select(Lesson).where(
                    Lesson.module_id == module.id,
                    Lesson.order == lesson_data["order"]
                )
            )
            existing_lesson = result.scalar_one_or_none()
            
            if existing_lesson:
                print(f"  Lesson '{lesson_data['title']}' (module {module_order}, order {lesson_data['order']}) already exists, skipping...")
            else:
                lesson = Lesson(
                    module_id=module.id,
                    **lesson_data
                )
                session.add(lesson)
                total_lessons += 1
                print(f"  Created lesson '{lesson_data['title']}' (module {module_order}, order {lesson_data['order']})")
    
    await session.commit()
    print(f"Lessons seeding completed: {total_lessons} new lessons created")


async def seed_achievements(session: AsyncSession) -> None:
    print("Seeding achievements...")
    total_achievements = 0
    
    for achievement_data in ACHIEVEMENTS_DATA:
        result = await session.execute(
            select(Achievement).where(Achievement.code == achievement_data["code"])
        )
        existing_achievement = result.scalar_one_or_none()
        
        if existing_achievement:
            print(f"  Achievement '{achievement_data['title']}' (code: {achievement_data['code']}) already exists, skipping...")
        else:
            achievement = Achievement(**achievement_data)
            session.add(achievement)
            total_achievements += 1
            print(f"  Created achievement '{achievement_data['title']}' (code: {achievement_data['code']})")
    
    await session.commit()
    print(f"Achievements seeding completed: {total_achievements} new achievements created")


async def verify_seed_data(session: AsyncSession) -> dict[str, Any]:
    print("\nVerifying seed data...")
    
    modules_result = await session.execute(select(Module))
    modules = modules_result.scalars().all()
    
    lessons_result = await session.execute(select(Lesson))
    lessons = lessons_result.scalars().all()
    
    achievements_result = await session.execute(select(Achievement))
    achievements = achievements_result.scalars().all()
    
    lessons_per_module: dict[int, int] = {}
    for lesson in lessons:
        lessons_per_module[lesson.module_id] = lessons_per_module.get(lesson.module_id, 0) + 1
    
    stats = {
        "total_modules": len(modules),
        "total_lessons": len(lessons),
        "total_achievements": len(achievements),
        "lessons_per_module": lessons_per_module,
    }
    
    print(f"  Total modules: {stats['total_modules']}")
    print(f"  Total lessons: {stats['total_lessons']}")
    print(f"  Total achievements: {stats['total_achievements']}")
    print(f"  Lessons per module: {stats['lessons_per_module']}")
    
    return stats


async def run_seed() -> dict[str, Any]:
    settings = get_settings()
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("Starting database seeding...")
            print("=" * 60)
            
            module_map = await seed_modules(session)
            
            print()
            await seed_lessons(session, module_map)
            
            print()
            await seed_achievements(session)
            
            print("=" * 60)
            stats = await verify_seed_data(session)
            
            print("\n✅ Database seeding completed successfully!")
            return stats
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


def main() -> None:
    try:
        stats = asyncio.run(run_seed())
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nSeeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
