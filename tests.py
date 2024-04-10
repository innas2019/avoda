from datetime import datetime, timezone
import random
import unittest
from avoda import create_app, db
from avoda.models import Users, Posts



class PostCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):

        db.session.remove()
        self.app_context.pop()

    def test_posts(self):
        now = datetime.now(timezone.utc)
        rand_phone = ""
        for x in range(3):
            rand_phone = rand_phone + str(random.randint(10, 99))
        p1 = Posts(
            created=now,
            updated=now,
            name="test " + rand_phone,
            place="test",
            phone=rand_phone,
            text="test__posts",
        )
        db.session.add(p1)
        db.session.commit()
        res = db.session.execute(
            db.select(Posts).where(Posts.phone == rand_phone)
        ).scalar()

        self.assertIsNotNone(res,"ошибка добавления записи")


if __name__ == "__main__":
    unittest.main(verbosity=2)
