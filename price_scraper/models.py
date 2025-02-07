"""
資料庫模型模組

定義資料庫表格結構和連線管理
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime
from contextlib import contextmanager
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 資料庫配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/price_scraper"
)

# 建立資料庫引擎
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# 建立 Session 工廠
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class TaskResult(Base):
    """
    爬蟲任務結果表
    
    儲存每個爬蟲任務的執行狀態和結果
    """
    
    __tablename__ = "task_results"

    id = Column(String, primary_key=True, comment="任務 ID")
    status = Column(String, nullable=False, comment="任務狀態")
    result = Column(JSON, nullable=True, comment="任務結果")
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        comment="建立時間"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新時間"
    )

    def __repr__(self):
        return f"<TaskResult(id={self.id}, status={self.status})>"

# 建立資料表
try:
    Base.metadata.create_all(bind=engine)
    logger.info("資料表建立成功")
except Exception as e:
    logger.error(f"建立資料表時發生錯誤: {str(e)}")

def get_db() -> Session:
    """
    取得資料庫連線
    
    Returns:
        SQLAlchemy Session 物件
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"建立資料庫連線時發生錯誤: {str(e)}")
        db.close()
        raise 