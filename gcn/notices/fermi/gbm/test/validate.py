#!/usr/bin/python3
import os.path
from sys import argv
#from urllib.parse import urlsplit
from collections import namedtuple, Sequence
import json
from jsonschema import validate, Draft202012Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
import unittest

from fermi_gbm_fields import FIELD_DEFS_BY_NOTICE

class TestFermiGBMSchema(unittest.TestCase):

   NOTICES_TYPE_TO_INDEX = { 110:0, 111:1, 112:2, 115:3, 131:4 }

   NOTICE_NAMES = {
      110: ("ALERT" , "FERMI_GBM_ALERT" ),
      111: ("FLIGHT", "FERMI_GBM_FLIGHT_POS"),
      112: ("GROUND", "FERMI_GBM_GROUND_POS"),
      115: ("FINAL" , "FERMI_GBM_FINAL_POS" ),
      131: ("SUBTHR", "FERMI_GBM_SUBTHRESHOLD"),
      }

   NOTICE_FILENAMES = {
      110: ("FermiGBMAlert.schema.json"),
      111: (""),
      112: (""),
      115: (""),
      131: (""),
      }

   FIELD_COUNTS = {
      # Unused/Used
      110:(99,23),
      111:(82,40),
      112:(84,38),
      115:(89,33),
      131:(88,34),
   }

   FDEFS = []

   DEFAULT_GOOD_CLASSIFICATIONS = []
   DEFAULT_BAD_CLASSIFICATIONS = []

   DEFAULT_GOOD_VALS_BY_FIELD_TYPE = dict(
         int = [-1, 0, 1, 2],
         INT_GZ=[0.1, 1.2], 
         float=[-0.5, 0.0, 3.14],
         FLOAT_01=[0.68, 0.0, 1.0],
         FLOAT_GZ = [1.2],
         FLOAT_RA = [120.3, 0.00],
         FLOAT_DEC = [-23.4, -90.0, 0.0, 90.0],
         FLOAT_ZEN = [90.8, 0.0, 180.0],
         bool=[True, False], 
         str=["somehtext"],

         NOTICE_TYPE=None,
         CLASSIFICATION=DEFAULT_GOOD_CLASSIFICATIONS,
         )


   DEFAULT_BAD_VALS_BY_FIELD_TYPE = dict(
         int=[0.5, True, False, "sometext"],
         INT_GZ=[-5, 0, True, False, "sometext"],
         float=[True, False, "sometext"],
         FLOAT_01=[-0.2, 1.2, True, False, "sometext"],
         FLOAT_GZ=[-1.4, 0.0, True, False, "sometext"],
         FLOAT_RA=[-10.1, 360.0, 370.3, True, False, "sometext"],
         FLOAT_DEC=[-90.5, 90.2, True, False, "sometext"],
         FLOAT_ZEN=[-0.1, 180.5, True, False, "sometext"],
         bool=[0, 1, 0.5, "sometext"],
         str=[0, 1, 0.5, True, False, "sometext"],

         NOTICE_TYPE=None,
         CLASSIFICATION=DEFAULT_GOOD_CLASSIFICATIONS,
         )

   class FieldDefs(namedtuple("_FieldDefs", "field_name core_schema notice_type notice_index notice_name field_type field_dim enums default_value good_values bad_values".split())):

      def __new__(cls, notice_type, notice_index, notice_name, field_name, core_schema, notice_flags, other_defs):
         fdefs = [field_name, core_schema, notice_type, notice_index, notice_name]
         
         if notice_flags is None or other_defs is None or not notice_flags[notice_index]:
            default_value = None if other_defs is None else other_defs
            other_defs = (len(cls._fields) - len(fdefs)) * [None]
            other_defs[-3] = default_value
            fdefs += other_defs
         else:
            fdefs += other_defs
            field_type = other_defs[0]
            if field_type == "NOTICE_TYPE":
               full_name = TestFermiGBMSchema.NOTICE_NAMES[notice_type][1]
               fdefs[-2] = [full_name]
               fdefs[-1] = [s for ss in TestFermiGBMSchema.NOTICE_NAMES.values() for s in ss if s != full_name]
         return super().__new__(cls, *fdefs)
         

   NOTICE_TYPE = None
   SCHEMA_DIR = ".."
   doc = None
   min_doc = None

   @staticmethod
   def retrieve_local_schema(uri):
      u = uri.replace("https://gcn.nasa.gov/schema/main", "../../../../..")
      print(uri, "->", u)
      with open(u) as f:
         s = f.read()

      s = json.loads(s)
      s = Resource.from_contents(s)
      return s

   @property
   def NOTICE_INDEX(self):
      return self.NOTICES_TYPE_TO_INDEX[ self.NOTICE_TYPE]

   @property
   def NOTICE_NAME(self):
      return self.NOTICE_NAMES[ self.NOTICE_TYPE][0]

   @property
   def NOTICE_FULL_NAME(self):
      return self.NOTICE_NAMES[ self.NOTICE_TYPE][1]

   @property
   def SCHEMA_FILENAME(self):
      return self.NOTICE_FILENAMES[ self.NOTICE_TYPE]

   @property
   def SCHEMA_PATH(self):
      return os.path.join(self.SCHEMA_DIR, self.SCHEMA_FILENAME)

   @property
   def EXPECTED_SCHEMA_FIELD_COUNT(self):
      return self.FIELD_COUNTS[ self.NOTICE_TYPE][1]

   @property
   def EXPECTED_UNUSED_FIELD_COUNT(self):
      return self.FIELD_COUNTS[ self.NOTICE_TYPE][0]


   def setUp(self):
      with open(self.SCHEMA_PATH) as f:
         s = f.read()
      self.schema = json.loads(s)
      self.schema_registry = Registry(retrieve=TestFermiGBMSchema.retrieve_local_schema)
      self.doc_validator = Draft202012Validator(schema=self.schema, registry=self.schema_registry)

      self.FDEFS = [ self.FieldDefs(
            self.NOTICE_TYPE, self.NOTICE_INDEX, self.NOTICE_NAME, 
            *a
            ) for a in FIELD_DEFS_BY_NOTICE
            ]


   @staticmethod
   def asseq(obj):
      return [obj] if isinstance(obj, str) or not isinstance(obj, Sequence) else obj

   def good_vals(self, fdefs, no_array=False):
      if fdefs.field_type is None:
         yield fdefs.default_value
         return

      n = fdefs.field_dim
      if not no_array and n > 0:
         a, j, v = n * [None], -1, None
         for i,v in enumerate(self.good_vals(fdefs, no_array=True)):
            j = i % n
            a[j] = v
            if j + 1 == n:
               yield a
               j = -1

         if j >= 0:
            j += 1
            a[j:n] = (n - j) * [v]
            yield a

      else:
         
         if fdefs.field_type == "NOTICE_TYPE":
            val_sets = [ self.NOTICE_FULL_NAME ]
         elif fdefs.field_type == "CLASSIFICATION":
            val_sets = [None]
         elif fdefs.enums:
            val_sets = [fdefs.enums]
         else:
            val_sets = [fdefs.good_values, self.DEFAULT_GOOD_VALS_BY_FIELD_TYPE[fdefs.field_type] ]

         for vset in val_sets:
            if vset is None:
               continue

            for v in self.asseq(vset):
               yield v

   def bad_fvalues_from_fdefs(fdefs):
      badarrs = []
      ftype, fdim, fenum, fdefault, badvals = fdefs
      N = 3
      D = 4 if fdim is None else fdim
      if ftype != "int":
         badvals.append(1)
         badvals += [ n*[1] for n in range(N) if n != D ]
      else:
         fval = 1

      if fdim is None and fdim != 0:
         badvals += [ [] ]

      return fval

   @staticmethod
   def add_field_to_doc(doc, fname, fval):
      if fname in doc.keys():
         raise Exception(f"{fname} repeated")
      doc[fname] = fval

   def new_good_doc(self, with_optionals):
      doc = {}
      for fdefs in self.FDEFS:
         if fdefs.field_type is None:
            continue

         if not with_optionals and fdefs.default_value is not None:
            continue

         v = self.good_vals(fdefs).__next__()
         self.add_field_to_doc(doc, fdefs.field_name, v)

      self.doc_validator.validate(doc)
      return doc
       

   def assertNotRequiredException(self, e, field_name):
      self.assertIsInstance(e, ValidationError)
      s = f"should not be valid under {{'required': ['{field_name}']}}"
      self.assertTrue(e.message.strip().endswith(s))

   def assertUnevaluatedPropertyException(self, e, field_name):
      self.assertIsInstance(e, ValidationError)
      s = f"Unevaluated properties are not allowed ('{field_name}' was unexpected)"
      self.assertTrue(e.message.strip().endswith(s))

      
   def test_all_optional_fields(self):
      doc = self.new_good_doc(with_optionals=True)
      print(f"\nSample {self.NOTICE_NAME} notice.  All optional fields included.  Values are not representative.")
      print(json.dumps(doc))


   def test_no_optional_fields(self):
      doc = self.new_good_doc(with_optionals=False)
      print(f"\nSample {self.NOTICE_NAME} notice.  None of the optional fields are included.  Values are not representative.")
      print(json.dumps(doc))

   def test_excluded_fields(self):
      doc = self.new_good_doc(with_optionals=True)
      for fdefs in self.FDEFS:
         if fdefs.field_type is not None:
            continue

         if fdefs.core_schema != "Localization":
            continue

         v = self.good_vals(fdefs).__next__()
         self.add_field_to_doc(doc, fdefs.field_name, v)
         try:
            self.doc_validator.validate(doc)
         except ValidationError as e:
            self.assertUnevaluatedPropertyException(e, fdefs.field_name)
            #self.assertNotRequiredException(e, fdefs.field_name)
         
         doc.pop(fdefs.field_name)
         

if __name__ == "__main__":
   my_schema = "../schema.json"
   my_schema = os.path.abspath(my_schema)
   
   TestFermiGBMSchema.NOTICE_TYPE = 110
   unittest.main()
   print("Valid")
