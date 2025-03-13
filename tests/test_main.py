import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.model import DB

TEST_DB_URL = "postgresql://postgres:123@localhost:5432/test_db"

engine = create_engine(TEST_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DB.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        DB.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db_session = SessionLocal()

        def override_get_db():
            try:
                yield self.db_session
            finally:
                self.db_session.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        self.db_session.close()

    def test_create_roll(self):
        response1 = self.client.post("/rolls/create",
                                     json={"length": 100, "weight": 20})
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.json(), {
            "length": 100,
            "weight": 20,
            "id": 1,
            "added_date": "2025-03-13",
            "removed_date": None})

        response2 = self.client.post("/rolls/create",
                                     json={"length": 10, "weight": 1})
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json(), {
            "length": 10,
            "weight": 1,
            "id": 2,
            "added_date": "2025-03-13",
            "removed_date": None})

    def test_delete_roll(self):
        roll_id = 2
        response = self.client.delete(f"/rolls/delete/{roll_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "length": 10,
            "weight": 1,
            "id": 2,
            "added_date": "2025-03-13",
            "removed_date": None})
