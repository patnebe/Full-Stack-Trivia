import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

from marshmallow import Schema, fields, ValidationError

QUESTIONS_PER_PAGE = 10


def get_categories():
    categories = db.session.query(Category.type).all()

    list_of_categories = []

    for category in categories:
        list_of_categories.append(category[0])

    return list_of_categories


class question_schema(Schema):
    question = fields.String()
    answer = fields.String()
    category = fields.Int()
    difficulty = fields.Int()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/v1/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    """
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    """

    @app.route('/v1/categories')
    def get_available_categories():
        try:
            list_of_categories = get_categories()

            response_object = {
                "success": True,
                "categories": list_of_categories,
                "number_of_categories": len(list_of_categories)
            }

            return jsonify(response_object)

        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    """
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    """

    @app.route('/v1/questions')
    def get_all_questions():
        def get_paginated_questions():
            start = request.args.get('page', 1, type=int)

            questions = Question.query.paginate(
                start, QUESTIONS_PER_PAGE, False).items

            return questions

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

    """
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    """

    @app.route('/v1/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

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

    """
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab. 
    """
    @app.route('/v1/questions', methods=['POST'])
    def post_new_question():

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
                "message": f"The question: {question} has been stored in the database."
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

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/v1/questions/search', methods=['POST'])
    def search_questions():
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

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/v1/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
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

    # # """
    # # @TODO:
    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.

    # TEST: In the "Play" tab, after a user selects "All" or a category,
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.
    # """
    # @app.route('/v1/quizzes', methods=['POST'])
    # def get_questions_for_quiz():
    #     # get required details in JSON format
    #     pass

    """
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    """
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
