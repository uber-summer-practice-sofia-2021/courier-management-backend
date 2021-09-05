from flaskr import db
from flaskr.models import *

db.session.add(Courier("7f4dc6b6-f8ba-477b-8b21-25446c9c72b3", "example@email.com"))
db.session.add(Courier("6e491824-572f-4148-b806-9fa302776ed3", "xample@email.com", "John Doe", 2.4, 3.5, 1.2, ['dangerous']))
db.session.commit()