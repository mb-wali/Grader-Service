from registry import VersionSpecifier, register_handler
from handlers.base_handler import GraderBaseHandler, authorize
from orm.takepart import Role, Scope


@register_handler(path=r"\/permissions\/?", version_specifier=VersionSpecifier.ALL)
class PermissionHandler(GraderBaseHandler):
    @authorize([Scope.student, Scope.tutor, Scope.instructor])
    async def get(self):
        response = []
        role: Role
        for role in self.user.roles:
            response.append(
                {"lecture_code": role.lecture.code, "scope": role.role.value}
            )
        self.write_json(response)
