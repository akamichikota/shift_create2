uvicorn app.main:app --reload

git tag -a v12345678 -m "Phase 12345678 completed"
git push origin v12345678

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


○これから実装すること
C枠作って、それの時間帯を変える
A枠B枠C枠の時間帯をフロントエンドで変更できるようにする
熟練者と初心者のロジックを作る