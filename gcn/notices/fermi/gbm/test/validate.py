#!/usr/bin/python3
import os.path
from sys import argv
#from urllib.parse import urlsplit
import json
from jsonschema import validate, Draft202012Validator
from referencing import Registry, Resource
import unittest

from fermi_gbm_fields import FIELDS

def RETRIEVE_LOCAL_FILE(uri):
   #parsed = urlsplit(uri)
   u = uri.replace("https://gcn.nasa.gov/schema/main", "../../../../..")
   print(uri, "-->", u)
   with open(u) as f:
      s = f.read()

   s = json.loads(s)
   s = Resource.from_contents(s)
   return s

REGISTRY = Registry(retrieve=RETRIEVE_LOCAL_FILE)

def test_base(self, instance):
   def test_1(self):
      pass

   pass

class TestAlert(unittest.TestCase):
   def setUp(self):
      my_schema = "../alert.schema.json"
      my_schema = os.path.abspath(my_schema)

      with open(my_schema) as s:
         my_schema = s.read()
      my_schema = json.loads(my_schema)

      self.validator = Draft202012Validator(schema=my_schema, registry=REGISTRY)

   def test1(self):
      my_json = json.loads('{"TRIGGER_ALGORITHM": 15}')
      assertTrue(v.is_valid(my_json))


if __name__ == "__main__":
   my_schema = "../alert.schema.json"
   my_schema = os.path.abspath(my_schema)

   s = "{\n"
   s = [ f'  "{fld}":"1"' for fld,(nots,sch) in FIELDS.items() if nots[0] ]
   n = len(s)
   s = "\n".join(s)
   s = '{\n\n' + s + '\n\n}'
   print(s)
   exit(0)

   with open(my_schema) as s:
      my_schema = s.read()
   my_schema = json.loads(my_schema)
   print(my_schema)

   v = Draft202012Validator(schema=my_schema, registry=REGISTRY)

   #my_json = json.loads('{"filter": ["Hello world!"]}')
   my_json = json.loads('{"TRIGGER_ALGORITHM_NUMBER": 15, "mission":"AAAA"}')
   v.validate(instance=my_json)
   print("Valid")
