
from database import Base, engine
from database import create_tables
from models import PDFChunk, Message  

if __name__ == "__main__":
    create_tables()


Base.metadata.create_all(bind=engine)
