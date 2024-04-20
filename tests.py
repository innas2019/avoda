from datetime import datetime, timezone
import random
import unittest
from avoda import create_app, db
from avoda.models import Role, Posts, Refs
#для запуска тестов: python -m unittest   

class PostCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):

        db.session.remove()
        self.app_context.pop()

    def test_add_posts(self):
        now = datetime.now(timezone.utc)
        rand_phone = ""
        for x in range(3):
            rand_phone = rand_phone + str(random.randint(10, 99))
        p = Posts(
            created=now,
            updated=now,
            name="test " + rand_phone,
            place="test",
            phone=rand_phone,
            text="test__posts",
        )
        db.session.add(p)
        db.session.commit()
        res = db.session.execute(
            db.select(Posts).where(Posts.phone == rand_phone)
        ).scalar()

        self.assertIsNotNone(res, "ошибка добавления записи")

    def test_refs(self):
        refs=["levels","occupations","places","documents","conditions"]
        for k in refs:
            res = db.session.execute(db.select(Refs).where(Refs.name == k)).scalars()
            self.assertTrue(len(res.all())>0,k+" справочник не заполнен")
        

    def test_create_refs(self):
        res = db.session.execute(db.select(Refs).where(Refs.name == "levels")).scalars()
        list = res.all()
        if len(list) == 0:
            p1 = Refs(name="levels", value="начальный")
            p2 = Refs(name="levels", value="хороший")
            db.session.add_all([p1, p2])
        
        res = db.session.execute(db.select(Refs).where(Refs.name == "places")).scalars()
        list = res.all()
        if len(list) == 0:
            p3 = Refs(name="places", value="Тель-Авив")
            p4 = Refs(name="places", value="Хайфа")
            db.session.add_all([p3, p4])
        
        res = db.session.execute(
            db.select(Refs).where(Refs.name == "occupations")
        ).scalars()
        list = res.all()
        if len(list) == 0:
            p5 = Refs(name="occupations", value="стройка")
            p6 = Refs(name="occupations", value="завод")
            db.session.add_all([p5, p6])
        
        res = db.session.execute(
            db.select(Refs).where(Refs.name == "documents")
        ).scalars()
        list = res.all()
        if len(list) == 0:
            p7 = Refs(name="documents", value="ТЗ")
            p8 = Refs(name="documents", value="права")
            db.session.add_all([p7, p8])

        res = db.session.execute(
            db.select(Refs).where(Refs.name == "conditions")
        ).scalars()
        list = res.all()
        if len(list) == 0:
            p9 = Refs(name="conditions", value="полная")
            p10 = Refs(name="conditions", value="частичная")
            db.session.add_all([p9, p10])
             
        db.session.commit()
        res = db.session.execute(db.select(Refs)).scalars()
        list = res.all()
        self.assertTrue(len(list) > 9, "ошибка добавления справочников")

    def test_create_roles(self):

        res = db.session.execute(
            db.select(Role).where(Role.name == "adminisrators")
        ).scalar()
        if res is None:
            r1 = Role(name="adminisrators")
            db.session.add(r1)

        res = db.session.execute(
            db.select(Role).where(Role.name == "create_post")
        ).scalar()
        if res is None:
            r2 = Role(name="create_post")
            db.session.add(r2)
        db.session.commit()

        res = db.session.execute(db.select(Role)).scalars()
        self.assertTrue(len(res.all()) == 2, "ошибка добавления ролей")


if __name__ == "__main__":
    unittest.main(verbosity=2)
