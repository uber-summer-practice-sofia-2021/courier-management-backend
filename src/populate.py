from flaskr import db
from flaskr.database.models import *

db.session.add(Courier("7f4dc6b6-f8ba-477b-8b21-25446c9c72b3", "example@email.com"))
db.session.add(
    Courier(
        "6e491824-572f-4148-b806-9fa302776ed3",
        "xample@email.com",
        "John Doe",
        10.0,
        2.4,
        3.5,
        1.2,
        ["dangerous"],
    )
)
db.session.add(
    Courier(
        "b1e5ec81-b29f-4686-a875-3f78564ff3b3",
        "xample@email.com",
        "John Doe",
        5.0,
        2.4,
        3.5,
        1.2,
        ["dangerous", "fragile"],
    )
)

db.session.add(
    Trip(
        "b1e5ec81-b29f-4686-a875-3f78564ff3b3",
        "6e491824-572f-4148-b806-9fa302776ed3",
        "6e491824-572f-4148-b806-9fa302776ed3",
        23,
        "asd",
        "asd",
        "asd",
    )
)
db.session.add(
    Trip(
        "6e491824-572f-4148-b806-9fa302776ed3",
        "6e491824-572f-4148-b806-9fa302776ed3",
        "6e491824-572f-4148-b806-9fa302776ed3",
        23,
        "asd",
        "asd",
        "asd",
    )
)

db.session.commit()
