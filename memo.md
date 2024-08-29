uvicorn app.main:app --reload

git tag -a v123456 -m "Phase 123456 completed"
git push origin v123456

データベース構造
+-----------------+          +---------------------+
|   Employee      |          |   ShiftRequest      |
+-----------------+          +---------------------+
| id (PK)         |<-------->| id (PK)             |
| name            |          | employee_id (FK)    |
| weekly_shifts   |          | date                |
+-----------------+          | start_time          |
                             | end_time            |
                             +---------------------+


Alembicなどのマイグレーションツールを使用