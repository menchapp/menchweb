from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers

# Create your models here.
class UserPhoto(ndb.Model):
  user = ndb.StringProperty()
  # blob_key = blobstore.BlobReferenceProperty()
  blob_key = ndb.BlobKeyProperty()

# Create your models here.
class RfpPhoto(ndb.Model):
  user = ndb.StringProperty()
  # blob_key = blobstore.BlobReferenceProperty()
  blob_key = ndb.BlobKeyProperty()

class Profile(ndb.Model):
  user = ndb.StringProperty()
  brand = ndb.StringProperty()
  name = ndb.StringProperty()
  email = ndb.StringProperty()
  phone = ndb.StringProperty()
  instagram = ndb.StringProperty()
  location = ndb.StringProperty()
  about = ndb.TextProperty()  