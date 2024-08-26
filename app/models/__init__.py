from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./data/shift.db"

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのインポート
from .employee import Employee
from .shift import ShiftRequest

# テーブル作成
# Base.metadata.drop_all(bind=engine)  # 既存のテーブルを削除
Base.metadata.create_all(bind=engine)  # 新しいテーブルを作成

# デバッグ用ログ出力
inspector = inspect(engine)
print("Tables after creation:")
print(inspector.get_table_names())

# データベースセッションの取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()