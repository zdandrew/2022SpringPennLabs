# Penn Labs Backend Challenge - Andrew Zhang

View in raw text for best formatting

Bonus Challenges Completed: 
   - Frontend (templates)
   - Scraping
   - Unit Tests
   - DevOps (Docker image)
   - Club comments
   - login/logout/signup

Set Up:
   navigate to project directory
   'npm install'
   'python bootstrap.py'
   'flask run'

Note about Frontend: Everything except 'add new club', 'favorite club', 'modify club' is integrated into UI. 

Log-in information: email: 'josh@gmail.com', password: 'test'. Or you can create your own through the register page. Must be logged-in to add comments or favorite clubs. Can create and update clubs without logging in.
POST: http://127.0.0.1:5000/login form data: (email, 'josh@gmail.com'), (password, 'test')

Swagger API Documentation is available at '/swagger-ui/'
@use_kwargs from flask-apispec requires refactoring some func signatures as it wasn't compatible. Due to the time constraint, I decided to document the api in the Readme and use Swagger as a supplement.
As a result, many lines including @doc, @use_kwargs, @marshal_with have been commented out.

## FILE STRUCTURE:
Templates: Contains all the HTML used to set up the frontend
app.py: Contains all the routes used.
bootstrap.py: Contains the functions used for populating the database, and web-scraping
models.py: Contains the code for database structure.
test_routes.py: Unit tests
Dockerfile, start_app_w_gunicorn.sh, requirements.txt: used for creating Docker Image

## MODELS.PY: 4 classes - Club, Tag, User, Comment
   Club & User: many to many relationship
   Club & Tag: many to many relationship
   Club & Comment: one to many relationship
   User & Comment: one to many relationship

## APP.PY ROUTES:

   @app.route('/api/users', methods=['GET']) - Gets all users and info.
   Status Codes:
      200: OK

   @app.route('/api/user/<name>', methods=['GET']) - Returns specific user with matching name
   Status Codes:
      200: OK
      404: user not found

   @app.route('/api/clubs', methods=['GET']) - Gets all clubs
   Status Codes:
      200: OK

   @app.route('/api/club', methods=['POST']) - Create new club
   Status Codes:
      201: created successfully
      409: club already exists
   Request Body Payload example json: 
   {
      "code": "codingclubcode",
      "name": "Code Club",
      "description": "We do code",
      "tags": ["Programming", "Coding", "Technology", "Undergraduate"]
   }

   @app.route('/api/club/<q>', methods=['GET']) - Gets clubs based on search term q
   Status Codes:
      200: OK
   
   @app.route('/api/club/<q>', methods=['PUT']) - Updates specific club with id q
   Status Codes:
      200: OK
      400: invalid payload
   Request body payload example json:
   {
      "name": "Locust Labs Newest Name",
      "description": "Locust Labs new description right here",
      "tags": ["Undergraduate", "TestTagFeature", "SuperFunTime"]
   }

   @app.route('/api/favorite/<club>/<name>', methods=['POST']) - favorites a club, must be logged in
      enter the club's id/code for <club> and user's id for <name>
      example route: '/api/favorite/penn-memes/josh
   Status Codes:
      401: unauthorized, must be logged in
      404: user does not exist
      404: club does not exist
      409: conflict, already favorited
      200: OK
   
   SHOW NUMBER OF CLUBS FOR EACH TAG * 
   @app.route('/api/tag_count') - returns the counts for every tag in json format.
   Status Codes:
      200: OK

## BONUS CHALLENGES

   ### APP.PY BONUS ROUTES (Comments and User Authentication)

   @app.route('/api/comments', methods=['GET']) - Gets all comments
   Status Codes:
      200: OK
   
   @app.route('/api/add_comment', methods=['POST']) - Creates a comment, must be logged in
   Status Codes:
      401: unauthorized, must be logged in
      404: club not found
      200: OK
   Request body payload json example:
   {
      "body": "postman comment",
      "email": "josh@gmail.com",
      "club_name": "Penn Memes Club"
   }

   LOGIN/LOGOUT/REGISTER
   @app.route('/logged_in') - directs to page after logging in.
   Status Codes:
      200: OK

   @app.route("/api/login", methods=["POST", "GET"]) - login page, takes json data
   Status Codes:
      401: wrong password or email not found
      200: OK
   Example json payload:
   {
      "email": "josh@gmail.com",
      "password": "test"
   }

   @app.route("/", methods=['GET', 'POST'])  - register page, takes form data to create new account
   Status Codes:
      409: name/email already in use
      400: passwords invalid/do not match
      200: OK

   @app.route("/logout", methods=["POST", "GET"]) - logout page
   Status Codes:
      200: OK

   ### BOOTSTRAP.PY WEB-SCRAPER
   scrape_load_data()
      scrapes and loads club page into database

   ### FRONTEND
   All templates are found in 'templates' folder

   ### Unit Tests
   Used Pytest library. Tested most important routes and cases.
   To Run:
      'python -m pytest'

   ### Docker/Gunicorn
   Created Docker Image and ran it successfully. To recreate, follow below steps:
   1. install Gunicorn: 
      'pip install gunicorn'
   2. run the app in gunicorn with 2 processes/instances, 2 threads each:
      'gunicorn app:app -w 2 --threads 2 -b 0.0.0.0:5000'
   3. build Docker image: 
      'docker build -t labs_image_2022 .'
   4. run app from Docker: 
      'docker run -p 5000:5000 labs_image_2022'
   5. check running images
      'docker ps'
   6. kill image
      'docker kill <id>'
   
   
