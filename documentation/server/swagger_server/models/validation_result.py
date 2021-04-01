# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.validation_result_validation_errors import ValidationResultValidationErrors  # noqa: F401,E501
from swagger_server import util


class ValidationResult(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, status: str=None, validation_errors: List[ValidationResultValidationErrors]=None):  # noqa: E501
        """ValidationResult - a model defined in Swagger

        :param status: The status of this ValidationResult.  # noqa: E501
        :type status: str
        :param validation_errors: The validation_errors of this ValidationResult.  # noqa: E501
        :type validation_errors: List[ValidationResultValidationErrors]
        """
        self.swagger_types = {
            'status': str,
            'validation_errors': List[ValidationResultValidationErrors]
        }

        self.attribute_map = {
            'status': 'status',
            'validation_errors': 'validation_errors'
        }
        self._status = status
        self._validation_errors = validation_errors

    @classmethod
    def from_dict(cls, dikt) -> 'ValidationResult':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ValidationResult of this ValidationResult.  # noqa: E501
        :rtype: ValidationResult
        """
        return util.deserialize_model(dikt, cls)

    @property
    def status(self) -> str:
        """Gets the status of this ValidationResult.


        :return: The status of this ValidationResult.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status: str):
        """Sets the status of this ValidationResult.


        :param status: The status of this ValidationResult.
        :type status: str
        """
        allowed_values = ["passed", "failed"]  # noqa: E501
        if status not in allowed_values:
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"
                .format(status, allowed_values)
            )

        self._status = status

    @property
    def validation_errors(self) -> List[ValidationResultValidationErrors]:
        """Gets the validation_errors of this ValidationResult.


        :return: The validation_errors of this ValidationResult.
        :rtype: List[ValidationResultValidationErrors]
        """
        return self._validation_errors

    @validation_errors.setter
    def validation_errors(self, validation_errors: List[ValidationResultValidationErrors]):
        """Sets the validation_errors of this ValidationResult.


        :param validation_errors: The validation_errors of this ValidationResult.
        :type validation_errors: List[ValidationResultValidationErrors]
        """

        self._validation_errors = validation_errors
