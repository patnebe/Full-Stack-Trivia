import os
import unittest
import json
import random
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
        self.assertEqual(type(response_data['categories']), list)
        self.assertEqual(type(response_data['number_of_categories']), int)

    def test_success_get_paginated_questions(self):
        """A get request to the /v1/questions endpoint should return a list of questions, number of total questions, current category, categories."""

        endpoint = '/v1/questions'
        response_object = self.client().get(endpoint)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)
        self.assertTrue(response_data['success'])

        self.assertEqual(type(response_data['questions']), list)

        self.assertEqual(type(response_data['total_questions']), int)

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

        question_id = Question.query.first().format()['id']
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

            self.assertEqual(response_data['current_category'], category_name)

            self.assertTrue(response_data['success'])

            self.assertEqual(type(response_data['questions']), list)

            returned_questions = response_data['questions']

            for question in returned_questions:
                self.assertEqual(question['category'], category_id)

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

    def test_success_get_questions_based_on_search_term(self):
        """A request to get questions by search term should return all questions which contain the search term as a substring in a case-insensitive manner"""

        search_query = ""

        # construct search query from the first item in the database
        first_question = Question.query.first()

        # Checking for null values in the unlikely event that the database is empty
        if first_question is not None:
            first_question = first_question.format()['question']
            words_in_first_question = first_question.split()
            no_of_words = len(words_in_first_question)
            search_query = words_in_first_question[random.randint(
                0, no_of_words-1)]

        payload = {"searchTerm": search_query}
        endpoint = "/v1/questions/search"

        # make a search request to the endpoint
        response_object = self.client().post(endpoint, json=payload)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(type(response_data['questions']), list)
        self.assertEqual(response_object.status_code, 200)
        pass

    def test_404_get_questions_based_on_search_term(self):
        """A request to get questions by search term should return 404 if there is no string which contains the search term as a substring"""

        search_query = "iswlxxzcsrcgracazczl"
        payload = {"searchTerm": search_query}
        endpoint = "/v1/questions/search"

        response_object = self.client().post(endpoint, json=payload)

        self.assertEqual(response_object.status_code, 404)
        pass

    def test_success_get_questions_to_play_quiz(self):
        """A request to get the next question in the quiz should a return a random question, within the given category, which is not within the list of previous question"""

        # get a random category for the list of categories within the database
        categories = Category.query.all()
        list_of_categories = [category.format() for category in categories]
        no_of_categories = len(list_of_categories)

        category = list_of_categories[random.randint(
            0, no_of_categories-1)]['id']

        # create a list of previous questions from the given category
        query_result = Question.query.filter(
            Question.category == category).limit(5).all()
        list_of_previous_questions = [
            question.format()['question'] for question in query_result]

        payload = {"previous_questions": list_of_previous_questions,
                   "quiz_category": category}

        endpoint = '/v1/quizzes'

        response_object = self.client().post(endpoint, json=payload)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)

        question_from_endpoint = response_data['question']

        self.assertEqual(type(question_from_endpoint), dict)

        if type(question_from_endpoint) is dict:
            # make sure that the question returned is not in the list of previous questions
            for question in list_of_previous_questions:
                self.assertNotEqual(
                    question, question_from_endpoint['question'])
        pass

    def test_400_failure_get_questions_to_play_quiz(self):
        """A request to get the next question in the quiz should a return a 400 error if the parameters if the request payload is incomplete or wrongly formatted"""

        payload = {"previous_questions": [],
                   "quiz_category": "category"}

        endpoint = '/v1/quizzes'

        response_object = self.client().post(endpoint, json=payload)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 400)
        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
