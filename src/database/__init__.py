from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL
from loguru import logger

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        """Khởi tạo database engine và session"""
        self.engine = create_engine(DATABASE_URL, echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
        logger.info(f"Database initialized with URL: {DATABASE_URL}")
    
    def create_tables(self):
        """Tạo tất cả các bảng trong database"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def get_session(self):
        """Tạo và trả về một database session"""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Xóa tất cả các bảng (sử dụng cẩn thận!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")

# Global database instance
db_manager = DatabaseManager()

# Helper function for init_db
def init_db():
    """Initialize database and create tables"""
    db_manager.create_tables()
    logger.info("Database initialized")

# Import repositories
from src.database.repository import UserRepository, InvoiceRepository

# Export all
__all__ = [
    'Base',
    'DatabaseManager',
    'db_manager',
    'init_db',
    'UserRepository',
    'InvoiceRepository'
]
