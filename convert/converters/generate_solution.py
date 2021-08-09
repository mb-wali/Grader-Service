import os
import re
from textwrap import dedent

from traitlets import List, Bool, default

from .base import BaseConverter, GraderConvertException
from preprocessors import (
    IncludeHeaderFooter,
    LockCells,
    SaveCells,
    ClearOutput,
    ClearMarkScheme,
    Execute,
)
from traitlets.config.loader import Config
from typing import Any


class GenerateSolution(BaseConverter):

    create_assignment = Bool(
        True,
        help=dedent(
            """
            Whether to create the assignment at runtime if it does not
            already exist.
            """
        )
    ).tag(config=True)

    @default("permissions")
    def _permissions_default(self) -> int:
        return 664 if self.coursedir.groupshared else 644

    @property
    def _input_directory(self) -> str:
        return self.coursedir.source_directory

    @property
    def _output_directory(self):
        return self.coursedir.solution_directory

    preprocessors = List([
        IncludeHeaderFooter,
        LockCells,
        ClearOutput,
        ClearMarkScheme,
        Execute
    ])
    # NB: ClearHiddenTests must come after ComputeChecksums and SaveCells.
    # ComputerChecksums must come again after ClearHiddenTests.

    def __init__(self, **kwargs: Any) -> None:
        super(GenerateSolution, self).__init__(coursedir=None, **kwargs)

    def init_assignment(self, assignment_id: str, student_id: str) -> None:
        super(GenerateSolution, self).init_directories(assignment_id, student_id)
        with Gradebook(self.coursedir.db_url, self.coursedir.course_id) as gb:
            try:
                gb.find_assignment(assignment_id)
            except MissingEntry:
                msg = "No assignment with ID '%s' exists in the database" % assignment_id
                self.log.error(msg)
                raise GraderConvertException(msg)

    def start(self) -> None:
        old_student_id = self.coursedir.student_id
        self.coursedir.student_id = '.'
        try:
            super(GenerateSolution, self).start()
        finally:
            self.coursedir.student_id = old_student_id
