import os
import time
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from fastapi import Header

from database import SessionLocal, engine
from models import Base, Profile, Skill, Project, Work
from schemas import *
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin 123")   # simple on purpose (demo)
def verify_admin(x_api_key: str = Header(None)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_api_key
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
if CORS_ORIGINS == "*":
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],  # GET, POST, PATCH, DELETE, OPTIONS
    allow_headers=["*"],
)

# ---------------- RATE LIMIT (SIMPLE, IN-MEMORY) ----------------
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))  # requests
RATE_WINDOW = int(os.getenv("RATE_WINDOW", "60"))  # seconds
_rate_state: dict[str, dict[str, float]] = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if RATE_LIMIT <= 0 or RATE_WINDOW <= 0:
        return await call_next(request)

    client = request.client.host if request.client else "unknown"
    now = time.time()
    state = _rate_state.get(client)
    if not state or now - state["start"] > RATE_WINDOW:
        _rate_state[client] = {"start": now, "count": 1}
        return await call_next(request)

    if state["count"] >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    state["count"] += 1
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- PROFILE ----------------

@app.post("/profile", response_model=ProfileOut)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    if db.query(Profile).first():
        raise HTTPException(400, "Profile already exists")

    p = Profile(**profile.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/profile", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(404, "Create profile first")
    return profile


# 🔥 PATCH added (matches frontend)
@app.patch("/profile", response_model=ProfileOut)
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(404)

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)

    db.commit()
    db.refresh(profile)
    return profile


# ---------------- WORK ----------------

@app.post("/work", response_model=WorkOut)
def add_work(work: WorkCreate, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(400, "Create profile first")

    w = Work(
        company=work.company,
        role=work.role,
        start_date=work.start_date,
        end_date=work.end_date,
        description=work.description,
        profile_id=profile.id
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


@app.get("/work", response_model=List[WorkOut])
def get_work(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    return db.query(Work).offset(offset).limit(limit).all()


@app.put("/work/{work_id}", response_model=WorkOut)
def update_work(work_id: int, data: WorkUpdate, db: Session = Depends(get_db)):
    work = db.get(Work, work_id)
    if not work:
        raise HTTPException(404)

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(work, k, v)

    db.commit()
    db.refresh(work)
    return work


@app.delete("/work/{work_id}")
def delete_work(work_id: int, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    work = db.get(Work, work_id)
    if not work:
        raise HTTPException(404)

    db.delete(work)
    db.commit()
    return {"ok": True}


# ---------------- SKILLS ----------------

@app.post("/skills", response_model=SkillOut)
def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    user: str = Depends(verify_admin)   # if you have admin auth
):
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(400, "Create profile first")

    db_skill = Skill(
        name=skill.name,
        proficiency=skill.proficiency,
        profile_id=profile.id   # or however you link profile
    )

    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


@app.get("/skills", response_model=List[SkillOut])
def get_skills(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    return db.query(Skill).offset(offset).limit(limit).all()


@app.get("/skills/top", response_model=List[SkillOut])
def get_top_skills(limit: int = 5, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 50))
    return db.query(Skill).order_by(Skill.name.asc()).limit(limit).all()


@app.put("/skills/{skill_id}", response_model=SkillOut)
def update_skill(
    skill_id: int,
    data: SkillUpdate,
    db: Session = Depends(get_db)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(skill, key, value)

    db.commit()
    db.refresh(skill)
    return skill

@app.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(404)

    db.delete(skill)
    db.commit()
    return {"ok": True}


# ---------------- PROJECTS ----------------

@app.post("/projects", response_model=ProjectOut)
def add_project(project: ProjectCreate, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(400, "Create profile first")

    p = Project(
        title=project.title,
        description=project.description,
        links=project.links,      # 🔥 explicit
        profile_id=profile.id
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/projects", response_model=List[ProjectOut])
def get_projects(skill: str | None = None, limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Project)
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    if skill:
        query = (
            db.query(Project)
            .join(Profile, Project.profile_id == Profile.id)
            .join(Skill, Skill.profile_id == Profile.id)
            .filter(Skill.name.ilike(f"%{skill}%"))
            .distinct()
        )
    return query.offset(offset).limit(limit).all()


@app.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404)

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(project, k, v)

    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db),_: str = Depends(verify_admin)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404)

    db.delete(project)
    db.commit()
    return {"ok": True}


# ---------------- SEARCH ----------------

@app.get("/search", response_model=SearchResults)
def search(q: str, db: Session = Depends(get_db)):
    if not q:
        return {"skills": [], "projects": []}

    skills = db.query(Skill).filter(
        Skill.name.ilike(f"%{q}%")
    ).all()
    projects = db.query(Project).filter(
        (Project.title.ilike(f"%{q}%")) |
        (Project.description.ilike(f"%{q}%"))
    ).all()
    return {"skills": skills, "projects": projects}
