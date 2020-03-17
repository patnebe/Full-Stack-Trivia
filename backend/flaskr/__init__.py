import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

from marshmallow import Schema, fields, ValidationError

# A global variable stating how many questions to be returned per page during pagination
QUESTIONS_PER_PAGE = 10


def get_categories():
    """
    A helper function which returns a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category.

    Args: 
        None

    Returns:
            A hash table of categories where each key:value pair represents the category id and the category type respectively.
    """
    categories = Category.query.all()

    hash_table_of_categories = {}

    for category in categories:
        hash_table_of_categories[category.id] = category.type

    return hash_table_of_categories


def get_paginated_questions():
    """
    A helper function which makes a paginated query to the Question table and returns the apropriate number of questions.

    Args:
        None

    Returns:
        questions: A list of objects which are instances of the 'Question' class/data model.
    """
    start = request.args.get('page', 1, type=int)

    questions = Question.query.paginate(
        start, QUESTIONS_PER_PAGE, False).items

    return questions


class question_schema(Schema):
    """
    A marshmallow schema which validates the JSON payload accompanying POST requests to create new trivia questions.

    See https://marshmallow.readthedocs.io/en/stable/ for more info.
    """
    question = fields.String()
    answer = fields.String()
    category = fields.Int()
    difficulty = fields.Int()


class quiz_request_schema(Schema):
    """
    A marshmallow schema which validates the JSON payload accompanying POST requests to get the next question during the trivia quiz.

    See https://marshmallow.readthedocs.io/en/stable/ for more info.
    """
    previous_questions = fields.List(fields.Int())
    quiz_category = fields.Dict(keys=fields.String(), values=fields.Inferred())


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/v1/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        """
        Returns the response object after modifying it to add Access-Control headers after each request
        """
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    @app.route('/v1/categories')
    def get_available_categories():
        """
        Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category

        Methods: ['GET']

        Request Parameters: None

        Returns: A JSON object which includes a key, categories, that contains an object of id: category_string key:value pairs. 

        Sample response: {
            "success": true,
            "categories": {
                '1' : "Science",
                '2' : "Art",
                '3' : "Geography",
                '4' : "History",
                '5' : "Entertainment",
                '6' : "Sports"
            },
            "number_of_categories": 6
        }
        """
        try:
            categories = get_categories()

            response_object = {
                "success": True,
                "categories": categories,
                "number_of_categories": len(categories)
            }

            return jsonify(response_object)

        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    @app.route('/v1/questions')
    def get_all_questions():
        """
        Fetches a list of questions in which each question is represented by a dictionary. 

        Methods: ['GET']

        Request Parameters: (Optional, default is 1) An integer representing the starting page, where each page contains a given number (defined as a global variable in the app) of number questions.

        Returns: A JSON object which includes a key, questions, that points to a list of dictionaries representing different questions. 

        Sample response: {
            "success": true,
            "questions": [
                {
                    "id": 1,
                    "question": "Who built this API?",
                    "answer": "Dev-Nebe",
                    "category": 1,
                    "difficulty": 2
                },
                {
                    "id": 2,
                    "question": "What programming language was this API built in?",
                    "answer": "Python",
                    "category": 1,
                    "difficulty": 2
                }]
            "total_questions": 2,
            "categories": {
                '1' : "Science",
                '2' : "Art",
                '3' : "Geography",
                '4' : "History",
                '5' : "Entertainment",
                '6' : "Sports"
            },
            "current_category": None
        }
        """
        try:
            questions = get_paginated_questions()

            list_of_formatted_questions = []

            if len(questions) == 0:
                return not_found(404)

            for question in questions:
                list_of_formatted_questions.append(question.format())
            list_of_formatted_questions

            response_object = {
                "success": True,
                "questions": list_of_formatted_questions,
                "total_questions": len(list_of_formatted_questions),
                "categories": get_categories(),
                "current_category": None
            }

            return jsonify(response_object)

        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    @app.route('/v1/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        Deletes a question with the specified ID. 

        Methods: ['DELETE']

        Request Parameters: None

        Returns: A JSON object which includes a key - message - indicating that the question was deleted successfully. 

        Sample response: {
            "success": true,
            "message": "The question with ID: 1 was successfully deleted"
        }
        """
        try:
            question_to_be_deleted = Question.query.get(question_id)

            if question_to_be_deleted is None:
                return not_found(404)

            db.session.delete(question_to_be_deleted)
            db.session.commit()

            response_object = {
                "success": True,
                "message": f"The question with ID: {question_id} was successfully deleted."
            }

            return jsonify(response_object)

        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    @app.route('/v1/questions', methods=['POST'])
    def post_new_question():
        """
        Stores a new question in the database.

        Methods: ['POST']

        Request Parameters: None

        Request Data: A JSON object containing the following keys - question, answer, category, and difficulty. The values associated with these keys should be of type string, string, int, and int respectively.

        Sample request data: {
            "question": "What was Cassius Clay known as?",
            "answer": "Muhammad Ali",
            "category": 1,
            "difficulty": 4
        } 

        Returns: A JSON object which includes a key - message - indicating that the question was successfully added to the database. 

        Sample response: {
            "success": true,
            "message": "The question: 'What was Cassius Clay known as?' was successfully added to the Trivia"
        }
        """
        try:
            request_payload = request.get_json()
            # This next line validates the the properties of the JSON input and raises a ValidationError exception if the input data is not properly formatted.
            input_is_valid = question_schema().load(request_payload)

            question = request_payload['question']
            answer = request_payload['answer']
            category = request_payload['category']
            difficulty = request_payload['difficulty']

            question_to_be_inserted = Question(
                question=question, answer=answer, category=category, difficulty=difficulty)

            db.session.add(question_to_be_inserted)
            db.session.commit()

            response_object = {
                "success": True,
                "message": f"The question: '{question}' has been added to the Trivia"
            }

            return jsonify(response_object)

        except ValidationError as err:
            print(err.messages)
            return bad_request(404)

        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    @app.route('/v1/questions/search', methods=['POST'])
    def search_questions():
        """
        Searches for a question in the database.

        Methods: ['POST']

        Request Parameters: None

        Request Data: A JSON object containing a single key: value pair. The key is 'searchTerm' and the value contains the search_query

        Sample request data: {
            "searchTerm": "soccer"
        } 

        Returns: A JSON object which includes a key - questions - that points to a list of questions where each question is represented by a dictionary. 

        Sample response: {
            'success': True,
            'questions': [
                {
                    'id': 10,
                    'question': 'Which is the only team to play in every soccer World Cup tournament?',
                    'answer': 'Brazil',
                    'category': 6,
                    'difficulty': 3
                },
                {
                    'id': 11,
                    'question': 'Which country won the first ever soccer World Cup in 1930?',
                    'answer': 'Uruguay',
                    'category': 6,
                    'difficulty': 4
                }
            ],
            'current_category': None,
            'total_questions': 2
        }
        """
        try:
            request_payload = request.get_json()
            search_query = request_payload['searchTerm']

            search_results = Question.query.filter(
                Question.question.ilike(f"%{search_query}%")).all()

            if len(search_results) is 0:
                return not_found(404)

            list_of_search_results = [question.format()
                                      for question in search_results]

            response_object = {
                "success": True,
                "questions": list_of_search_results,
                "current_category": None,
                "total_questions": len(list_of_search_results)
            }

            return jsonify(response_object)

        except:
            db.session.rollback()
            print(sys.exc_info())
            abort(500)

        finally:
            db.session.close()

    @app.route('/v1/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        """
        Returns a list of all the questions available for a given category.

        Methods: ['GET']

        Request Parameters: None

        Returns: A JSON object which includes a key - questions - that points to a list of questions for the requested category. Each question is represented by a dictionary. 

        Sample response: {
            'success': True,
            'questions': [
                {
                    'id': 10,
                    'question': 'Which is the only team to play in every soccer World Cup tournament?',
                    'answer': 'Brazil',
                    'category': 6,
                    'difficulty': 3
                }
            ],
            'total_questions': 1,
            'current_category': 6
        }
        """
        try:
            current_category = Category.query.get(category_id)

            if current_category is None:
                return not_found(404)

            current_category = current_category.format()

            relevant_questions = Question.query.filter(
                Question.category == category_id).all()

            questions_for_currrent_category = [
                question.format() for question in relevant_questions]

            response_object = {
                "success": True,
                "questions": questions_for_currrent_category,
                "total_questions": len(questions_for_currrent_category),
                "current_category": current_category['type']
            }

            return jsonify(response_object)

        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    @app.route('/v1/quizzes', methods=['POST'])
    def get_questions_for_quiz():
        """
        Returns a random question for the quiz, within the given category, that is not contained in the list of previous questions.

        Methods: ['POST']

        Request Parameters: None

        Request Data: A JSON object containing the following keys - previous_questions, quiz_category. The values associated with these keys should be a list of question IDs and an integer representing the current category, respectively.

        Sample request data: {
            "previous_questions": [1,18,5],
            "quiz_category": 1,
        } 

        Returns: A JSON object which includes a key - questions - that points to a list of questions for the requested category. Each question is represented by a dictionary. 

        Sample response: {
            'success': True,
            'question': [
                {
                    'id': 10,
                    'question': 'Which is the only team to play in every soccer World Cup tournament?',
                    'answer': 'Brazil',
                    'category': 6,
                    'difficulty': 3
                }
            ]
        }
        """
        try:
            request_payload = request.get_json()
            input_is_valid = quiz_request_schema().load(request_payload)

            previous_questions = request_payload['previous_questions']
            quiz_category = request_payload['quiz_category']['id']

            # find out how to exclude queries from db
            question_query = Question.query.filter(
                Question.category == quiz_category)

            for prev_question in previous_questions:
                question_query = question_query.filter(
                    Question.id != prev_question)

            filtered_questions = question_query.all()
            list_of_filtered_questions = [
                question.format() for question in filtered_questions]

            next_question = None

            number_of_questions = len(list_of_filtered_questions)

            if number_of_questions > 0:
                next_question = list_of_filtered_questions[random.randint(
                    0, number_of_questions-1)]

            response_object = {
                "success": True,
                "question": next_question
            }

            return jsonify(response_object)

        except ValidationError:
            abort(400)

        except:
            db.session.rollback()
            print(sys.exc_info())
            abort(500)

        finally:
            db.session.close()

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": 400,
            "message": "Bad request.",
            "success": False
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": 404,
            "message": "The requested resource does not exist.",
            "success": False
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "error": 422,
            "message": "The request is unprocessable.",
            "success": False
        }), 422

    @app.errorhandler(500)
    def internal_serval_error(error):
        return jsonify({
            "error": 500,
            "message": "Something went wrong on the server.",
            "success": False
        })
        pass

    return app
