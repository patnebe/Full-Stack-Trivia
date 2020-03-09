import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.username = os.getenv('TRIVIA_USERNAME')
        self.password = os.getenv('PASSWORD')
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.username, self.password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_success_get_categories(self):
        """A get request to the /v1/categories endpoint should return all available categories"""

        endpoint = '/v1/categories'
        response_object = self.client().get(endpoint)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['categories'])
        self.assertTrue(response_data['number_of_categories'])
        self.assertEqual(type(response_data['categories']), list)
        self.assertEqual(type(response_data['number_of_categories']), int)

    def test_success_get_paginated_questions(self):
        """A get request to the /v1/questions endpoint should return a list of questions, number of total questions, current category, categories."""

        endpoint = '/v1/questions'
        response_object = self.client().get(endpoint)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)
        self.assertTrue(response_data['success'])

        self.assertTrue(response_data['questions'])
        self.assertEqual(type(response_data['questions']), list)

        self.assertTrue(response_data['total_questions'])
        self.assertEqual(type(response_data['total_questions']), int)

        self.assertTrue(response_data['categories'])
        self.assertEqual(type(response_data['categories']), list)
        pass

    def test_404_get_paginated_questions(self):
        """A request for a non existent question should return a 404"""

        endpoint = '/v1/questions?page=10000'
        response_object = self.client().get(endpoint)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 404)
        pass

    def test_success_delete_question_based_on_id(self):
        """A request to delete a given question with the specified id should return a 200 status code and should delete the question from the database"""

        question_id = 2
        endpoint = f"/v1/questions/{question_id}"

        response_object = self.client().delete(endpoint)
        response_data = json.loads(response_object.get_data())

        same_question_gotten_from_db = Question.query.get(question_id)

        self.assertEqual(response_object.status_code, 200)
        self.assertEqual(same_question_gotten_from_db, None)
        pass

    def test_404_delete_non_existent_question(self):
        """A request to delete a question with a non-existent id should return a 404 status code"""
        question_id = 999999
        endpoint = f"/v1/questions/{question_id}"

        response_object = self.client().delete(endpoint)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 404)
        pass

    # def test_success_post_new_question(self):
    #     """"""

    #     response_object = self.client().get('')
    #     response_data = json.loads(response_object.get_data())
    #     pass

    # def test_success_get_questions_based_on_category(self):
    #     """"""

    #     response_object = self.client().get('')
    #     response_data = json.loads(response_object.get_data())
    #     pass

    # def test_success_get_questions_based_on_search_term(self):
    #     """"""

    #     response_object = self.client().get('')
    #     response_data = json.loads(response_object.get_data())
    #     pass

    # def test_success_get_questions_to_play_quiz(self):
    #     """"""

    #     response_object = self.client().get('')
    #     response_data = json.loads(response_object.get_data())
    #     pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
