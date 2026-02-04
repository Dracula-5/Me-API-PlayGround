# Database Schema

This project uses SQLAlchemy with a Postgres-compatible schema.

## profiles
- id (integer, PK)
- name (string, not null)
- email (string, not null, unique)
- education (string, not null)
- github (string, nullable)
- linkedin (string, nullable)

## skills
- id (integer, PK)
- name (string, not null)
- proficiency (string, not null)
- profile_id (integer, FK -> profiles.id)

## projects
- id (integer, PK)
- title (string, not null)
- description (string, not null)
- links (json, nullable)
- profile_id (integer, FK -> profiles.id)

## work
- id (integer, PK)
- company (string, not null)
- role (string, not null)
- start_date (string, not null)
- end_date (string, nullable)
- description (string, nullable)
- profile_id (integer, FK -> profiles.id)
