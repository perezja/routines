# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: routine.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rroutine.proto\x12\x08routines\"3\n\x03Job\x12\x0b\n\x03wdl\x18\x01 \x01(\t\x12\r\n\x05input\x18\x02 \x01(\t\x12\x10\n\x08\x64\x61ta_dir\x18\x03 \x01(\t\":\n\x06Result\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.routines.Status\x12\x0e\n\x06outdir\x18\x02 \x01(\t\"a\n\x06Status\x12)\n\x04\x63ode\x18\x01 \x01(\x0e\x32\x1b.routines.Status.StatusCode\x12\x0b\n\x03msg\x18\x02 \x01(\t\"\x1f\n\nStatusCode\x12\x06\n\x02OK\x10\x00\x12\t\n\x05\x45RROR\x10\x01\x32\x37\n\x07Routine\x12,\n\x07\x45xecute\x12\r.routines.Job\x1a\x10.routines.Result\"\x00\x62\x06proto3')



_JOB = DESCRIPTOR.message_types_by_name['Job']
_RESULT = DESCRIPTOR.message_types_by_name['Result']
_STATUS = DESCRIPTOR.message_types_by_name['Status']
_STATUS_STATUSCODE = _STATUS.enum_types_by_name['StatusCode']
Job = _reflection.GeneratedProtocolMessageType('Job', (_message.Message,), {
  'DESCRIPTOR' : _JOB,
  '__module__' : 'routine_pb2'
  # @@protoc_insertion_point(class_scope:routines.Job)
  })
_sym_db.RegisterMessage(Job)

Result = _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), {
  'DESCRIPTOR' : _RESULT,
  '__module__' : 'routine_pb2'
  # @@protoc_insertion_point(class_scope:routines.Result)
  })
_sym_db.RegisterMessage(Result)

Status = _reflection.GeneratedProtocolMessageType('Status', (_message.Message,), {
  'DESCRIPTOR' : _STATUS,
  '__module__' : 'routine_pb2'
  # @@protoc_insertion_point(class_scope:routines.Status)
  })
_sym_db.RegisterMessage(Status)

_ROUTINE = DESCRIPTOR.services_by_name['Routine']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _JOB._serialized_start=27
  _JOB._serialized_end=78
  _RESULT._serialized_start=80
  _RESULT._serialized_end=138
  _STATUS._serialized_start=140
  _STATUS._serialized_end=237
  _STATUS_STATUSCODE._serialized_start=206
  _STATUS_STATUSCODE._serialized_end=237
  _ROUTINE._serialized_start=239
  _ROUTINE._serialized_end=294
# @@protoc_insertion_point(module_scope)
