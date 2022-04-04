import datetime
import json
import os.path
import subprocess

from grader_service.handlers.handler_utils import parse_ids
from grader_service.orm import Lecture
from grader_service.orm.user import User
import tornado
from grader_service.api.models.submission import Submission as SubmissionModel
from grader_service.orm.assignment import Assignment
from grader_service.orm.base import DeleteState
from grader_service.orm.submission import Submission
from grader_service.orm.takepart import Role, Scope
from grader_service.registry import VersionSpecifier, register_handler
from sqlalchemy.sql.expression import func
from tornado.web import HTTPError
from grader_convert.gradebook.models import GradeBookModel

from grader_service.handlers.base_handler import GraderBaseHandler, authorize


def tuple_to_submission(t):
    s = Submission()
    (
        s.id,
        s.auto_status,
        s.manual_status,
        s.score,
        s.username,
        s.assignid,
        s.commit_hash,
        s.feedback_available,
        s.logs,
        s.date,
    ) = t
    return s


@register_handler(
    path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/submissions\/?",
    version_specifier=VersionSpecifier.ALL,
)
class SubmissionHandler(GraderBaseHandler):
    @authorize([Scope.student, Scope.tutor, Scope.instructor])
    async def get(self, lecture_id: int, assignment_id: int):
        """Return the submissions of an assignment

        Two query parameter: latest, instructor-version

        latest: only get the latest submissions of users
        instructor-version: if true, get the submissions of all users in lecture
                            if false, get own submissions

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        :raises HTTPError: throws err if user is not authorized or the assignment was not found
        """
        lecture_id, assignment_id = parse_ids(lecture_id, assignment_id)
        self.validate_parameters("latest", "instructor-version")
        latest = self.get_argument("latest", None) == "true"
        instructor_version = self.get_argument("instructor-version", None) == "true"

        role: Role = self.get_role(lecture_id)
        if instructor_version and role.role < Scope.tutor:
            self.error_message = "Unauthorized"
            raise HTTPError(403)
        assignment = self.get_assignment(lecture_id, assignment_id)

        if instructor_version:
            if latest:
                submissions = (
                    self.session.query(
                        Submission.id,
                        Submission.auto_status,
                        Submission.manual_status,
                        Submission.score,
                        Submission.username,
                        Submission.assignid,
                        Submission.commit_hash,
                        Submission.feedback_available,
                        Submission.logs,
                        func.max(Submission.date),
                    )
                        .filter(Submission.assignid == assignment_id)
                        .group_by(Submission.username)
                        .all()
                )
                submissions = [tuple_to_submission(t) for t in submissions]
            else:
                submissions = assignment.submissions
        else:
            if latest:
                submissions = (
                    self.session.query(
                        Submission.id,
                        Submission.auto_status,
                        Submission.manual_status,
                        Submission.score,
                        Submission.username,
                        Submission.assignid,
                        Submission.commit_hash,
                        Submission.feedback_available,
                        Submission.logs,
                        func.max(Submission.date),
                    )
                        .filter(
                        Submission.assignid == assignment_id,
                        Submission.username == role.username,
                    )
                        .group_by(Submission.username)
                        .all()
                )
                submissions = [tuple_to_submission(t) for t in submissions]
            else:
                submissions = (
                    self.session.query(
                        Submission
                    )
                        .filter(
                        Submission.assignid == assignment_id,
                        Submission.username == role.username,
                    )
                        .all()
                )

        self.write_json(submissions)

    async def post(self, lecture_id: int, assignment_id: int):
        """Create submission based on commit hash.

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        :raises HTTPError: throws err if user is not authorized or the assignment was not found
        """
        lecture_id, assignment_id = parse_ids(lecture_id, assignment_id)
        self.validate_parameters()
        body = tornado.escape.json_decode(self.request.body)
        sub_model = SubmissionModel.from_dict(body)

        assignment = self.get_assignment(lecture_id, assignment_id)

        submission = Submission()
        submission.assignid = assignment.id
        submission.date = datetime.datetime.utcnow()
        submission.username = self.user.name
        submission.feedback_available = False

        if assignment.duedate is not None and submission.date > assignment.duedate:
            self.write({"message": "Cannot submit assignment: Past due date!"})
            self.write_error(400)

        git_repo_path = self.construct_git_dir(repo_type=assignment.type, lecture=assignment.lecture,
                                               assignment=assignment)
        if git_repo_path is None or not os.path.exists(git_repo_path):
            raise HTTPError(404)

        try:
            subprocess.run(["git", "branch", "main", "--contains", sub_model.commit_hash], cwd=git_repo_path)
        except subprocess.CalledProcessError:
            raise HTTPError(404)

        submission.commit_hash = sub_model.commit_hash
        submission.auto_status = "not_graded"
        submission.manual_status = "not_graded"

        self.session.add(submission)
        self.session.commit()
        self.write_json(submission)


@register_handler(
    path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/submissions\/(?P<submission_id>\d*)\/?",
    version_specifier=VersionSpecifier.ALL,
)
class SubmissionObjectHandler(GraderBaseHandler):
    @authorize([Scope.tutor, Scope.instructor])
    async def get(self, lecture_id: int, assignment_id: int, submission_id: int):
        """Returns a specific submission

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        :param submission_id: id of the submission
        :type submission_id: int
        """
        lecture_id, assignment_id, submission_id = parse_ids(
            lecture_id, assignment_id, submission_id
        )
        submission = self.get_submission(lecture_id, assignment_id, submission_id)
        self.write_json(submission)

    @authorize([Scope.tutor, Scope.instructor])
    async def put(self, lecture_id: int, assignment_id: int, submission_id: int):
        """Updates a specific submission

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        :param submission_id: id of the submission
        :type submission_id: int
        """
        lecture_id, assignment_id, submission_id = parse_ids(
            lecture_id, assignment_id, submission_id
        )
        body = tornado.escape.json_decode(self.request.body)
        sub_model = SubmissionModel.from_dict(body)
        sub = self.get_submission(lecture_id, assignment_id, submission_id)
        sub.date = sub_model.submitted_at
        sub.assignid = assignment_id
        sub.username = self.user.name
        sub.auto_status = sub_model.auto_status
        sub.manual_status = sub_model.manual_status
        sub.feedback_available = sub_model.feedback_available or False
        self.session.commit()
        self.write_json(sub)


@register_handler(
    path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/submissions\/(?P<submission_id>\d*)\/properties\/?",
    version_specifier=VersionSpecifier.ALL,
)
class SubmissionPropertiesHandler(GraderBaseHandler):
    @authorize([Scope.tutor, Scope.instructor])
    async def get(self, lecture_id: int, assignment_id: int, submission_id: int):
        """
        Returns the properties of a submission

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        :param submission_id: id of the submission
        :type submission_id: int
        :raises HTTPError: throws err if the submission or their properties are not found
        """
        lecture_id, assignment_id, submission_id = parse_ids(
            lecture_id, assignment_id, submission_id
        )
        submission = self.get_submission(lecture_id, assignment_id, submission_id)
        if submission.properties is not None:
            self.write(submission.properties)
        else:
            self.error_message = "Not Found!"
            raise HTTPError(404)

    @authorize([Scope.tutor, Scope.instructor])
    async def put(self, lecture_id: int, assignment_id: int, submission_id: int):
        """
        Updates the properties of a submission

        :param lecture_id: id of the lecture
        :type lecture_id: int
        :param assignment_id: id of the assignment
        :type assignment_id: int
        :param submission_id: id of the submission
        :type submission_id: int
        :raises HTTPError: throws err if the submission are not found
        """
        lecture_id, assignment_id, submission_id = parse_ids(
            lecture_id, assignment_id, submission_id
        )
        submission = self.get_submission(lecture_id, assignment_id, submission_id)
        properties_string: str = self.request.body.decode("utf-8")
        try:
            score = GradeBookModel.from_dict(json.loads(properties_string)).score
        except:
            self.error_message = "Cannot parse properties file!"
            raise HTTPError(400)
        submission.score = score
        submission.properties = properties_string
        self.session.commit()
        self.write_json(submission)
