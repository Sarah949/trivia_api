import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
API_URL  = "http://localhost:5000"

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/v1.0/*": {"origins": "*"}})
  #CORS(app)
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Controll-Allow-Headers',
                         'Content-Type, Authorization, true')
    response.headers.add('Access-Controll-Allow-Origin', "*")
    response.headers.add('Access-Controll-Allow-Methods',
                         'GET, PUT, POST, DELETE, OPTIONS')
    return response
  ''' 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categories_list = {}
    for category in categories:
      categories_list[category.id] = category.type

    if len(categories) == 0:
      return abort(404)

    return jsonify({
      'success': True,
      'categories': categories_list
    }) 
        
  
  '''

  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    if len(current_questions) == 0:
      abort(404)

    categories = Category.query.all()
    categories_list = {}
    for category in categories:
      categories_list[category.id] = category.type

    return jsonify({
      'success': True,
      'questions': current_questions,
      'totalQuestions': len(selection),
      'categories': categories_list,
      'currentCategory': 'ALL'
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])  
  def delete_question(question_id):
    
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question is None:
      abort(404)
    try:
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'totalQuestions': len(Question.query.all())
      })

    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)
    search = body.get('searchTerm', None)
    categories = Category.query.all()
    categories_list = {}
    for category in categories:
      categories_list[category.id] = category.type
    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        #selection = Book.query.order_by(Book.id).filter(or_(Book.title.ilike('%{}%'.format(search)), Book.author.ilike('%{}%'.format(search))))
        current_questions = paginate_questions(request, selection)
       

        return jsonify({
          'success': True,
          'questions': current_questions,
          'totalQuestions': len(selection.all()),
          'category': 'Entertainment'
        })
      else: 
        if new_question is None or new_answer is None:
          abort(400)

        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'totalQuestions': len(Question.query.all()),
          'category': 'Entertainment'
        }), 201

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search = body.get('searchTerm', None)
    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(
          Question.question.ilike('%{}%'.format(search)))
        #selection = Book.query.order_by(Book.id).filter(or_(Book.title.ilike('%{}%'.format(search)), Book.author.ilike('%{}%'.format(search))))
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'totalQuestions': len(selection.all()),
          'category': 'test'

        })
    except:
      abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  @cross_origin()
  def get_questions_by_category(category_id):
    
    category = Category.query.filter(Category.id == category_id).one_or_none()

    if category is None:
      abort(404)
    try:
      selection = Question.query.filter(Question.category == str(category_id)).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions': len(current_questions),
        'currentCategory': category.type
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    body = request.get_json()
    if not( 'quiz_category' in body and 'previous_questions' in body):
     abort(400)
    
    category = body.get('quiz_category') 
    previous_questions = body.get('previous_questions')
    try:
      if category['type'] == 'click':
        questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
      else:
        questions = Question.query.filter(
        Question.id.notin_(previous_questions)).filter_by(
        category= category['id']).all()
      #get a random question 
      random_question = questions[random.randrange(0, len(questions), 1)]
      return jsonify({
        'success': True,
        'question': random_question.format(),
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  
  @app.errorhandler(500)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "internal server error"
      }), 500
  return app

