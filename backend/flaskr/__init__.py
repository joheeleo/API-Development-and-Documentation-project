import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginated_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    quizzes = [quiz.format() for quiz in questions]
    current_quizzes = quizzes[start:end]

    return current_quizzes
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def categories():
        return jsonify({
        'success': True,
        'categories': {category.id: category.type for category in  Category.query.all()}
        }), 200

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
    @app.route('/questions')
    def questions():
     
        # Implement pagniation
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        

        total_questions = [question.format() for question in Question.query.all()]
        paginated_questions = total_questions[start:end]
        
        if (len(paginated_questions)==0): abort(404) 
        return jsonify({
        'questions':paginated_questions,
        'totalQuestions': len(total_questions),
        'categories': {category.id: category.type for category in Category.query.all()},
        'currentCategory': None, 
        'success': True
        }), 200

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        Question.query.get_or_404(question_id).delete()
        
        return jsonify({'id':question_id, 'success': True}), 200

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions')
    def get_all_questions():
        """Route to display all questions"""
        questions = Question.query.order_by(Question.id).all()
        current_quizzes = paginated_questions(request, questions)

        data = Category.query.order_by(Category.id).all()
        categories = {}
        for category in data:
            categories[category.id] = category.type

        if len(current_quizzes) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_quizzes,
            'total_questions': Question.query.count(),
            'categories': categories,
            'current_category': None
        })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/results', methods=['POST'])
    def create_question():
        """Route to create a question"""
        data = request.get_json()

        question = data.get('question', None)
        answer = data.get('answer', None)
        category = data.get('category', None)
        difficulty = data.get('difficulty', None)
        searchTerm = data.get('searchTerm', None)
            
        try:
            if searchTerm:
                questions = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(searchTerm)))
                current_quizzes = paginated_questions(request, questions)

                return jsonify({
                    'success': True,
                    'questions': current_quizzes,
                    'total_questions': len(questions.all()),
                    'current_category': None
                })

            else:
                if not data['answer'] and not data['question'] and not data['category'] and not data['difficulty']:
                    abort(400)
                question = Question(
                    question=question, answer=answer, category=category, difficulty=difficulty)
                question.insert()

                return jsonify({
                    'success': True,
                    'question_id': question.id,
                    'questions': data,
                }), 201

        except:
            abort(422)

    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions')
    def questions_in_category(category_id):
        """Route to get questions per category"""
        question = Question.query.filter(Question.category == id).all()
        current_quizzes = paginated_questions(request, question)

        if question:
            try:
                data = Category.query.order_by(Category.id).all()
                categories = {}
                for category in data:
                    categories[category.id] = category.type

                return jsonify({
                    'success': True,
                    'questions': current_quizzes,
                    'total_questions': len(current_quizzes),
                    'current_category': id,
                    'categories': categories,
                })

            except Exception:
                abort(400)
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def random_question():

        previous_questions = request.get_json().get('previous_questions')
        quiz_category = request.get_json().get('quiz_category')

        if(previous_questions==None or quiz_category==None): abort(400)

        if(quiz_category['id'] == 0): 
            questions = Question.query.all()       
        else:  
            questions = Question.query.filter_by(category=quiz_category['id']).all() 


        if (len(previous_questions)==0): 
            return jsonify({'question': questions[random.randrange(0, len(questions), 1)].format(), 'success': True}), 200 
        
        if (len(questions)==len(previous_questions)): 
            return jsonify({'success': True}), 200

        
        question = None
        while(question==None):
            question = questions[random.randrange(0, len(questions), 1)]
            for id in previous_questions: 
                if (question.id == id):
                    question = None 
                    break 

        return jsonify({'question': question.format(), 'success': True}), 200 

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'Error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'Error': 404,
            'message': 'Resource Not Found'
        }), 404

    @app.errorhandler(422)
    def uprocessable(error):
        return jsonify({
            'success': False,
            'Error': 422,
            'message': 'Unable to process request'
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not allowed'
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

    return app

