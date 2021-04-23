from grader.common.registry import register_handler
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from grader.common.models.assignment import Assignment
from grader.common.services.request import RequestService
import tornado

@register_handler(path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/?")
class AssignmentBaseHandler(APIHandler):
  requestservice = RequestService()
  def get(self, lecture_id: int):
    self.write(self.requestservice.request(method='GET',endpoint=self.request.path,body=''))


  def post(self, lecture_id: int):
    self.write(self.requestservice.request(method='POST',endpoint=self.request.path,body=''))


@register_handler(path=r"\/lectures\/(?P<lecture_id>\d*)\/assignments\/(?P<assignment_id>\d*)\/?")
class AssignmentObjectHandler(APIHandler):
  requestservice = RequestService()
  def put(self, lecture_id: int, assignment_id: int):
    pass 
  
  def get(self, lecture_id: int, assignment_id: int):
    self.write(self.requestservice.request(method='GET',endpoint=self.request.path,body=''))

  
  def delete(self, lecture_id: int, assignment_id: int):
    pass