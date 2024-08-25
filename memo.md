uvicorn app.main:app --reload

git tag -a v1 -m "Phase 1 completed"
git push origin v1

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




