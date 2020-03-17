# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python). Python 3.7 is the recommended version for this project.

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM used for handling the lightweight sqlite database.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension used for handling cross origin requests from the frontend server.

## Database Setup

With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.

## API Documentation

```
Endpoints

GET '/v1/categories'
GET '/v1/questions'
DELETE '/v1/questions/<int:questions_id>'
POST '/v1/questions'
POST '/v1/questions/search'
GET '/v1/categories/<int:category_id>/questions'
POST '/V1/quizzes'


GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category

- Methods: ['GET']

- Request Parameters: None

- Returns: A JSON object which includes a key, categories, that contains an object of id: category_string key:value pairs.

- Sample response: {
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


GET '/v1/questions'
- Fetches a list of questions in which each question is represented by a dictionary.

- Request Parameters: (Optional, default is 1) An integer representing the starting page, where each page contains a given number (defined as a global variable in the app) of number questions.

- Returns: A JSON object which includes a key, questions, that points to a list of dictionaries representing different questions.

- Sample response: {
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


DELETE '/v1/questions/<int:questions_id>'
- Deletes a question with the specified ID.

- Request Parameters: None

- Returns: A JSON object which includes a key - message - indicating that the question was deleted successfully.

- Sample response: {
    "success": true,
    "message": "The question with ID: 1 was successfully deleted"
}


POST '/v1/questions'
- Stores a new question in the database.

- Request Parameters: None

- Request Data: A JSON object containing the following keys - question, answer, category, and difficulty. The values associated with these keys should be of type string, string, int, and int respectively.

- Sample request data: {
    "question": "What was Cassius Clay known as?",
    "answer": "Muhammad Ali",
    "category": 1,
    "difficulty": 4
}

- Returns: A JSON object which includes a key - message - indicating that the question was successfully added to the database.

- Sample response: {
    "success": true,
    "message": "The question: 'What was Cassius Clay known as?' was successfully added to the Trivia"
}


POST '/v1/questions/search'
- Searches for a question in the database.

- Methods: ['POST']

- Request Data: A JSON object containing a single key: value pair. The key is 'searchTerm' and the value contains the search_query

- Sample request data: {
    "searchTerm": "soccer"
}

- Returns: A JSON object which includes a key - questions - that points to a list of questions where each question is represented by a dictionary.

- Sample response: {
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


GET '/v1/categories/<int:category_id>/questions'
- Returns a list of all the questions available for a given category.

- Request Parameters: None

- Returns: A JSON object which includes a key - questions - that points to a list of questions for the requested category. Each question is represented by a dictionary.

- Sample response: {
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


POST '/V1/quizzes'
- Returns a random question for the quiz, within the given category, that is not contained in the list of previous questions.

- Request Parameters: None

- Request Data: A JSON object containing the following keys - previous_questions, quiz_category. The values associated with these keys should be a list of question IDs and an integer representing the current category, respectively.

- Sample request data: {
    "previous_questions": [1,18,5],
    "quiz_category": 1,
}

- Returns: A JSON object which includes a key - questions - that points to a list of questions for the requested category. Each question is represented by a dictionary.

- Sample response: {
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
```

## Testing

To run the tests, run

```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
