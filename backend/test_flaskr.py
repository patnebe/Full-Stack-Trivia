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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

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

    def test_success_post_new_question(self):
        """A request to post a new question with all required parameters should return a 200 status code"""

        endpoint = '/v1/questions'
        payload = {"question": "'What was Cassius Clay known as?'", "answer": "Muhammad Ali",
                   "category": 1, "difficulty": 4}

        response_object = self.client().post(endpoint, json=payload)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)
        pass

    def test_400_failure_post_new_question(self):
        """A request to post a new question with an incomplete payload should return a 400 status code"""

        endpoint = '/v1/questions'
        payload = {"question": "", "answer": "",
                   "category": None}

        response_object = self.client().post(endpoint, json=payload)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 400)
        pass

    def test_success_get_questions_based_on_category(self):
        """A request to this endpoint should return only questions which fall within the specified category. 

        This test will be done for all categories and should take O(nm) time where n is the number of categories and m is the number of questions for a given category.

        As the number of questions grow this test might need to be refactored to reduced its time complexity."""

        categories = Category.query.all()
        list_of_categories = [category.format() for category in categories]

        for item in list_of_categories:
            category_id = item['id']
            category_name = item['type']

            endpoint = f"/v1/categories/{category_id}/questions"

            response_object = self.client().get(endpoint)
            response_data = json.loads(response_object.get_data())

            self.assertEqual(response_object.status_code, 200)

            self.assertTrue(response_data['category'])
            self.assertEqual(response_data['category'], category_name)

            self.assertTrue(response_data['success'])

            self.assertTrue(response_data['questions'])
            self.assertEqual(type(response_data['questions']), list)

            returned_questions = response_data['questions']

            for question in returned_questions:
                self.assertEqual(question['category'], category_name)

            self.assertTrue(response_data['total_questions'])
            self.assertEqual(type(response_data['total_questions']), int)

        pass

    def test_404_get_questions_based_on_category(self):
        """A request to get questions from a non-existent category should return a 404"""

        category_id = 9999
        endpoint = f"/v1/categories/{category_id}/questions"

        response_object = self.client().get(endpoint)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 404)
        pass

    # Complete the three tests below
    def test_success_get_questions_based_on_search_term(self):
        """A request to get questions by search term should return all questions which contain the search term as a substring in a case-insensitive manner"""

        # search for question in db,
        # ensure that the number of questions from the db match the number of questions in returned by the

        response_object = self.client().get()
        response_data = json.loads(response_object.get_data())

        pass

    def test_404get_questions_based_on_search_term(self):
        """A request to get questions by search term should return 404 if there is no string which contains the search term as a substring"""

        response_object = self.client().get()
        response_data = json.loads(response_object.get_data())
        pass

    def test_success_get_questions_to_play_quiz(self):
        """"""
        payload = {}

        response_object = self.client().post('', json=payload)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)

        if type(response_data['question']) is dict:
            self.assertTrue(response_data['question'])
            self.assertTrue(response_data['answer'])
            self.assertTrue(response_data['category'])
            self.assertTrue(response_data['difficulty'])
        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
