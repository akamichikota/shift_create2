uvicorn app.main:app --reload

git tag -a v12 -m "Phase 12 completed"
git push origin v12

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




