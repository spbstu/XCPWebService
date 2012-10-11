#-*- encoding: utf-8; -*-

__author__ = 'artzab'

from suds.client import Client
import logging

logging.basicConfig(level=logging.INFO)
testClient = Client('http://localhost:7789/?wsdl', cache=None)

#result = testClient.service.GetStudentsByGroup(u'ФПС Студенты "Дизайн" 1 Семестр')
result = testClient.service.GetUsersVM('62618835-6b9f-d4ae-1ade-bd8d624d7742')

print result