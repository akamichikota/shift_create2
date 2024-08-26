uvicorn app.main:app --reload

git tag -a v12345 -m "Phase 12345 completed"
git push origin v12345

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