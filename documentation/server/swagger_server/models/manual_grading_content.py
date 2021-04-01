# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.manual_grading_content_feedback_cells import ManualGradingContentFeedbackCells  # noqa: F401,E501
from swagger_server import util


class ManualGradingContent(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, id: int=None, feedback_cells: List[ManualGradingContentFeedbackCells]=None):  # noqa: E501
        """ManualGradingContent - a model defined in Swagger

        :param id: The id of this ManualGradingContent.  # noqa: E501
        :type id: int
        :param feedback_cells: The feedback_cells of this ManualGradingContent.  # noqa: E501
        :type feedback_cells: List[ManualGradingContentFeedbackCells]
        """
        self.swagger_types = {
            'id': int,
            'feedback_cells': List[ManualGradingContentFeedbackCells]
        }

        self.attribute_map = {
            'id': 'id',
            'feedback_cells': 'feedback_cells'
        }
        self._id = id
        self._feedback_cells = feedback_cells

    @classmethod
    def from_dict(cls, dikt) -> 'ManualGradingContent':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ManualGradingContent of this ManualGradingContent.  # noqa: E501
        :rtype: ManualGradingContent
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> int:
        """Gets the id of this ManualGradingContent.


        :return: The id of this ManualGradingContent.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """Sets the id of this ManualGradingContent.


        :param id: The id of this ManualGradingContent.
        :type id: int
        """

        self._id = id

    @property
    def feedback_cells(self) -> List[ManualGradingContentFeedbackCells]:
        """Gets the feedback_cells of this ManualGradingContent.


        :return: The feedback_cells of this ManualGradingContent.
        :rtype: List[ManualGradingContentFeedbackCells]
        """
        return self._feedback_cells

    @feedback_cells.setter
    def feedback_cells(self, feedback_cells: List[ManualGradingContentFeedbackCells]):
        """Sets the feedback_cells of this ManualGradingContent.


        :param feedback_cells: The feedback_cells of this ManualGradingContent.
        :type feedback_cells: List[ManualGradingContentFeedbackCells]
        """

        self._feedback_cells = feedback_cells
