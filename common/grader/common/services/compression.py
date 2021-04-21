# this module will use gzip compression with a low compression level because gzip is significantly faster for compression with acceptable size and also for decompression.
# see: https://tukaani.org/lzma/benchmarks.html

import tarfile
import os
import os.path as osp
from grader.common.models.assignment import Assignment
from grader.common.models.lecture import Lecture
from grader.common.models.user import User
from grader.common.models.submission import Submission
from grader.common.models.rich_feedback import RichFeedback

from traitlets.config.configurable import Configurable
from traitlets.traitlets import Int, TraitError, Unicode, validate

class CompressionEngine(Configurable):

  compression_dir = Unicode('', help="The absolute path to the directory where the archives should be written.")
  compression_algo = Unicode('', help="The compression algorithm to use. Either: '', 'gz', 'bz' or 'xz'")
  compression_level = Int(2)
  
  def __init__(self, compression_dir: str, **kwargs):
    super().__init__(**kwargs)
    self.compression_dir = compression_dir  # the directory to put the compressed files
    self.compression_algo = "gz" # can be empty for no compression
    self.compression_level = 2  # has to be None is using no compression

  def create_archive(self, name: str, dir: str) -> str:
    file_name = osp.join(self.compression_dir["value"], name + self.extension)

    
    directory = osp.dirname(file_name)
    if not osp.exists(directory):
        os.makedirs(directory)

    dir = osp.abspath(dir)
    with tarfile.open(file_name, 'w:'+self.compression_algo['value']) as tar:
      tar.add(dir, arcname=osp.basename(dir))
    return file_name
  
  def read_archive(self, path: str) -> bytes:
    with open(path, "rb") as f:
      return f.read()

  def archive_assignment(self, lecture: Lecture, assignment: Assignment, dir: str) -> str:
    return self.create_archive("assignments/" + lecture.name + "/" + assignment.name, dir)

  def archive_submission(self, user: User, assignment: Assignment, submission: Submission, dir: str) -> str:
    return self.create_archive("submissions/" + user.id + "/" + assignment.name + "/" + submission.id, dir)

  def archive_feedback(self, user: User, assignment: Assignment, feedback: RichFeedback) -> str:
    return self.create_archive("feedback/" + user.id + "/" + assignment.name + "/" + feedback.id, dir)

  @property
  def extension(self):
    ext = ".tar"
    if self.compression_algo != "":
      ext += "." + self.compression_algo["value"]
    return ext

  
  @validate('compression_dir')
  def _validate_dir(self, proposal):
    path: str = proposal['value']
    if not osp.isabs(path):
      raise TraitError("The path is not absolute")
    if not osp.isdir(path):
      raise TraitError("The path has to be an existing directory")
    return proposal
  
  @validate('compression_algo')
  def _validate_algo(self, proposal):
    algo: str = proposal['value']
    if algo not in {'', 'gz', 'bz', 'xz'}:
      raise TraitError("Incorrect compression algorithm")
    return proposal

