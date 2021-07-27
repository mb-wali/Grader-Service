import logging
from grading_labextension.registry import register_handler
from grading_labextension.handlers.base_handler import ExtensionBaseHandler
from grading_labextension.services.git import GitError, GitService
from tornado.httpclient import HTTPError


@register_handler(
    path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/pull\/(?P<repo>\w*)\/?"
)
class PullHandler(ExtensionBaseHandler):
    async def get(self, lecture_id: int, assignment_id: int, repo: str):
        if repo not in {"user", "group", "source", "release"}:
            self.write_error(404)
        try:
            lecture = await self.request_service.request(
                "GET",
                f"{self.base_url}/lectures/{lecture_id}",
                header=self.grader_authentication_header,
            )
            assignment = await self.request_service.request(
                "GET",
                f"{self.base_url}/lectures/{lecture_id}/assignments/{assignment_id}",
                header=self.grader_authentication_header,
            )
        except HTTPError as e:
            self.set_status(e.code)
            self.write_error(e.code)
            return

        git_service = GitService(
            lecture_code=lecture["code"],
            assignment_name=assignment["name"],
            repo_type=repo,
            config=self.config,
            force_user_repo=True if repo=="release" else False
        )
        try:
            if not git_service.is_git():
                git_service.init()
                git_service.set_remote(f"grader-{repo}")
                git_service.set_author()
            git_service.pull(f"grader-{repo}", force=True)
            self.write("OK")
        except GitError as e:
            logging.getLogger(str(self.__class__)).error("GitError:\n" + e.error)
            self.write_error(400)


@register_handler(
    path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/push\/(?P<repo>\w*)\/?"
)
class PushHandler(ExtensionBaseHandler):
    async def put(self, lecture_id: int, assignment_id: int, repo: str):
        if repo not in {"user", "group", "source", "release"}:
            self.write_error(401)
        try:
            lecture = await self.request_service.request(
                "GET",
                f"{self.base_url}/lectures/{lecture_id}",
                header=self.grader_authentication_header,
            )
            assignment = await self.request_service.request(
                "GET",
                f"{self.base_url}/lectures/{lecture_id}/assignments/{assignment_id}",
                header=self.grader_authentication_header,
            )
        except HTTPError as e:
            self.set_status(e.code)
            self.write_error(e.code)
            return

        git_service = GitService(
            lecture_code=lecture["code"],
            assignment_name=assignment["name"],
            repo_type=repo,
            config=self.config,
        )
        try:
            if not git_service.is_git():
                git_service.init()
                git_service.set_remote(f"grader-{repo}")
                git_service.set_author()
                # TODO: create .gitignore file
        except GitError as e:
            logging.getLogger(str(self.__class__)).error("GitError:\n" + e.error)
            self.write_error(400)
            return
        try:
            git_service.commit()
        except GitError as e:
            logging.getLogger(str(self.__class__)).error("GitError:\n" + e.error)
        ## committing might fail because there is nothing to commit -> try to push regardless
        try:
            git_service.push(f"grader-{repo}", force=True)
        except GitError as e:
            logging.getLogger(str(self.__class__)).error("GitError:\n" + e.error)
            self.write_error(400)
            return
        self.write("OK")
