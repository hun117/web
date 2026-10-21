from pydantic import BaseModel, ConfigDict


class CourseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    instructor: str
    category: str
    price: int
    thumbnail: str
    level: str
    duration: str
    rating: float
    is_enrolled: bool = False


class CourseList(BaseModel):
    items: list[CourseSummary]
    total: int
