from database import SessionLocal
from models import Profile, Skill, Project, Work

db = SessionLocal()

# ================= PROFILE =================
profile = db.query(Profile).first()

if not profile:
    profile = Profile(
        name="K V Dheeraj Reddy",
        email="dheerajsmile236@gmail.com",
        education="B.Tech in Engineering Physics at IIT Mandi",
        github="https://github.com/Dracula-5",
        linkedin="https://www.linkedin.com/in/k-v-dheeraj-reddy-727075303/",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

# ================= SKILLS =================
def get_or_create_skill(name, proficiency):
    skill = db.query(Skill).filter(
        Skill.name == name,
        Skill.profile_id == profile.id
    ).first()

    if not skill:
        skill = Skill(
            name=name,
            proficiency=proficiency,
            profile_id=profile.id
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)

    return skill


python = get_or_create_skill("Python", "Advanced")
fastapi = get_or_create_skill("FastAPI", "Medium")
sql = get_or_create_skill("SQL", "Medium")
docker = get_or_create_skill("Docker", "Beginner")
llm = get_or_create_skill("LLM", "Beginner")


# ================= PROJECTS =================
title = "Sample Project"
description = "This is a sample project description"
link = "https://example.com"

project = Project(
    title=title,
    description=description,
    links={"link": link},
    profile_id=profile.id
)
db.add(project)
db.commit()

# ================= WORK =================
work = Work(
    company="Example Company",
    role="Software Engineer",
    start_date="2023-01",
    end_date=None,
    description="Built APIs and internal tooling.",
    profile_id=profile.id
)
db.add(work)
db.commit()

db.close()
print(" Database seeded successfully")
