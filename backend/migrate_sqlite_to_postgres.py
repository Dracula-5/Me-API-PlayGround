import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models import Base, Profile, Skill, Project, Work


def normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url


def make_engine(url: str):
    url = normalize_db_url(url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)


def print_usage() -> None:
    print("Usage:")
    print("  set TARGET_DATABASE_URL=<postgres_url>")
    print("  python backend/migrate_sqlite_to_postgres.py --reset")
    print("")
    print("Optional:")
    print("  set SQLITE_URL=sqlite:///./meapi.db")


def reset_target(session) -> None:
    session.query(Work).delete()
    session.query(Project).delete()
    session.query(Skill).delete()
    session.query(Profile).delete()
    session.commit()


def target_is_empty(session) -> bool:
    return (
        session.query(Profile).count() == 0
        and session.query(Skill).count() == 0
        and session.query(Project).count() == 0
        and session.query(Work).count() == 0
    )


def copy_table(session_dst, rows, model_cls):
    for row in rows:
        data = row.__dict__.copy()
        data.pop("_sa_instance_state", None)
        session_dst.add(model_cls(**data))


def reset_sequences(engine_dst):
    if engine_dst.dialect.name != "postgresql":
        return
    with engine_dst.begin() as conn:
        for table in ["profiles", "skills", "projects", "work"]:
            conn.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"(SELECT COALESCE(MAX(id), 0) FROM {table}), true)"
                )
            )


def main() -> int:
    sqlite_url = os.getenv("SQLITE_URL", "sqlite:///./meapi.db")
    target_url = os.getenv("TARGET_DATABASE_URL") or os.getenv("DATABASE_URL")

    if not target_url:
        print("Missing TARGET_DATABASE_URL or DATABASE_URL.")
        print_usage()
        return 1

    target_url = normalize_db_url(target_url)
    if target_url.startswith("sqlite"):
        print("TARGET_DATABASE_URL must point to Postgres, not SQLite.")
        return 1

    reset_flag = "--reset" in sys.argv

    engine_src = make_engine(sqlite_url)
    engine_dst = make_engine(target_url)

    Base.metadata.create_all(bind=engine_dst)

    SessionSrc = sessionmaker(bind=engine_src)
    SessionDst = sessionmaker(bind=engine_dst)

    src = SessionSrc()
    dst = SessionDst()

    try:
        if reset_flag:
            reset_target(dst)
        else:
            if not target_is_empty(dst):
                print("Target database is not empty.")
                print("Run with --reset to wipe target before copying.")
                return 1

        profiles = src.query(Profile).all()
        skills = src.query(Skill).all()
        projects = src.query(Project).all()
        work = src.query(Work).all()

        copy_table(dst, profiles, Profile)
        copy_table(dst, skills, Skill)
        copy_table(dst, projects, Project)
        copy_table(dst, work, Work)

        dst.commit()
        reset_sequences(engine_dst)

        print("Migration complete.")
        print(f"Profiles: {len(profiles)}")
        print(f"Skills: {len(skills)}")
        print(f"Projects: {len(projects)}")
        print(f"Work: {len(work)}")
        return 0
    finally:
        src.close()
        dst.close()


if __name__ == "__main__":
    raise SystemExit(main())
