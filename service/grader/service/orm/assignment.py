from .base import Base, Serializable
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from grader.common.models import assignment


class Assignment(Base, Serializable):
    __tablename__ = "assignment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    lectid = Column(Integer, ForeignKey("lecture.id"))
    duedate = Column(DateTime, nullable=False)
    points = Column(Integer, nullable=True)
    status = Column(
        Enum("created", "released", "fetching", "fetched", "complete"),
        default="created",
    )

    lecture = relationship("Lecture", back_populates="assignments")
    files = relationship("File", back_populates="assignment")
    submissions = relationship("Submission", back_populates="assignment")

    @property
    def model(self) -> assignment.Assignment:
        assignment_model = assignment.Assignment(
            id=self.id, name=self.name, due_date=self.duedate, status=self.status
        )
        assignment_model.exercises = [ex.model for ex in self.files if ex.exercise]
        assignment_model.files = [f.model for f in self.files if not f.exercise]
        return assignment_model
