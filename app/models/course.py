from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructor: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    thumbnail: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    level: Mapped[str] = mapped_column(String(40), nullable=False, default="입문")
    duration: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0)
