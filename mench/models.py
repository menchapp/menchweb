from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

# Create your models here.
class UserPhoto(ndb.Model):
  user = ndb.StringProperty()
  # blob_key = blobstore.BlobReferenceProperty()
  blob_key = ndb.BlobKeyProperty()

class RfpPhoto(ndb.Model):
  rfp_key = ndb.StringProperty()
  # blob_key = blobstore.BlobReferenceProperty()
  blob_key = ndb.BlobKeyProperty()

class Purchase(ndb.Model):
  rfp_id = ndb.StringProperty()
  submission_id = ndb.StringProperty()
  user_id = ndb.StringProperty()

class Submission(ndb.Model):
  rfp_key = ndb.StringProperty()
  user = ndb.StringProperty()
  # blob_key = blobstore.BlobReferenceProperty()
  blob_key = ndb.BlobKeyProperty()

  def to_dict(self):
    result = super(Submission, self).to_dict()
    result['id'] = self.key.id()
    return result

class Profile(ndb.Model):
  user = ndb.StringProperty()
  brand = ndb.StringProperty()
  name = ndb.StringProperty()
  email = ndb.StringProperty()
  phone = ndb.StringProperty()
  instagram = ndb.StringProperty()
  location = ndb.StringProperty()
  website = ndb.StringProperty()
  about = ndb.TextProperty()  

class Rfp(ndb.Model):
  user = ndb.StringProperty()
  userName = ndb.StringProperty()
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
    photo_query = RfpPhoto.query(RfpPhoto.rfp_key == str(self.key.id()))
    if photo_query.count() > 0:
      photo = photo_query.fetch()
      photo_url = images.get_serving_url(photo[0].to_dict()['blob_key'])
    else:
      photo_url = ""
    result['img'] = photo_url
    return result  
