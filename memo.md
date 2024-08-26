uvicorn app.main:app --reload

git tag -a v1234 -m "Phase 1234 completed"
git push origin v1234

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

