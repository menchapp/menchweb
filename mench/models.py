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
  rfp_key = ndb.StringProperty()
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

class Rfp(ndb.Model):
  user = ndb.StringProperty()
  title = ndb.StringProperty()
  subtitle = ndb.StringProperty()
  prize = ndb.IntegerProperty()
  endDate = ndb.DateProperty()
  details = ndb.StringProperty()
  terms = ndb.StringProperty()
  intendedUse = ndb.StringProperty()
  duration = ndb.StringProperty()
  territory = ndb.StringProperty()
  exclusivity = ndb.StringProperty()
  hashtag = ndb.StringProperty()
    
  def to_dict(self):
    result = super(Rfp, self).to_dict()
    result['id'] = self.key.id()
    return result  