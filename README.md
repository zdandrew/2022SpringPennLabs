# Penn Labs Backend Challenge - Andrew Zhang

Original Backend Challenge Completed
Bonus Challenges Completed: 
   - Frontend/Full stack
   - scraping, club comments
   - login/logout/signup

How to set up. Navigate into project directory, 'npm install', 'python bootstrap.py', then 'flask run'.

Note about Frontend: Everything except 'add new club', 'favorite club', 'modify club' is integrated into UI. These were left out because the implementation for tags greatly complicates the form creation. In order to test these routes, you must log in through POSTMAN. Logging in through the UI, then using POSTMAN for the POST routes will result in access denied due to not being logged in. Use the dropdown in the top-right corner to navigate.

Log-in information: Username: 'josh@gmail.com', password: n/a, just fill in username and submit to log in. Or you can create your own through the register page.
POST: http://127.0.0.1:5000/login form data: (email, josh@gmail.com), (password, n/a)

FILE STRUCTURE:
Templates: Contains all the HTML used to set up the frontend
app.py: Contains all the routes used.
bootstrap.py: Contains the functions used for populating the database, and web-scraping
models.py: Contains the code for database structure.

MODELS.PY: 4 classes - Club, Tag, User, Comment
   due to the nature of these routes, many-to-many relationship were needed to  maximize query efficiency. This applies to clubs and tags, clubs and users, clubs and comments.

APP.PY ROUTES: '*' means implemented in frontend

   GET USER PROFILE *
   @app.route('/api/find_user', methods=['GET']) - Returns all users and info.
   @app.route('/api/find_specific_user', methods=['GET', 'POST']) - Returns specific user
      takes 'name' as a form and returns corresponding user.
      example: key=name, value=josh

   SEARCH CLUBS *
   @app.route('/api/clubs', methods=['GET', 'POST']) - Returns all clubs
   @app.route('/api/find_specific_club', methods=['GET', 'POST']) - Returns clubs matching search
      takes 'search' as a form and returns corresponding clubs.

   ADD NEW CLUB - MUST BE LOGGED IN (not in frontend)
   @app.route('/api/clubs', methods=['GET', 'POST']) - Adds a new club 
   Request Body Payload example json: 
         {
            "code": "codingclubcode",
            "name": "Code Club",
            "description": "We do code",
            "tags": ["Programming", "Coding", "Technology", "Undergraduate"]
         }

   FAVORITE A CLUB - MUST BE LOGGED IN (not in frontend)
   @app.route('/api/<club>/favorite/<name>', methods=['GET', 'POST']) - favorites a club
      enter the club's id/code for <club> and user's id for <name>
      example route: '/api/penn-memes/favorite/josh'

   MODIFY A CLUB - MUST BE LOGGED IN (not in frontend)
   @app.route('/api/clubs/<id>', methods=['PATCH']) - Modifies a club by changing fields to the input
      <id> denotes the club id.
      example route: '/api/clubs/locustlabs'
      Request Body Payload examples json:
         {
            "name": "Locust Labs New Name",
            "description": "Locust Labs new description right here",
            "tags": ["Undergraduate", "TestTagFeature", "SuperFunTime"]
         }
   
   SHOW NUMBER OF CLUBS FOR EACH TAG * 
   @app.route('/api/tag_count') - returns the counts for every tag in json format.

BONUS CHALLENGES

   APP.PY BONUS ROUTES

      ANONYMOUS CLUB COMMENTING SYSTEM - MUST BE LOGGED IN* 
      @app.route('/api/add_comment', methods=['GET', 'POST'])
         takes 'description' as a form. The comments are anonymous as no author is recorded

      LOGIN/LOGOUT/REGISTER
      @app.route('/logged_in') - directs to page after logging in.
      @app.route("/login", methods=["POST", "GET"]) - login page, takes form data
      @app.route("/", methods=['GET', 'POST'])  - register page, takes form data
      @app.route("/logout", methods=["POST", "GET"]) - logout page
         Users created in bootstrap.py do not require passwords, others all do.
         Passwords stored as hash.

   BOOTSTRAP.PY WEB-SCRAPER
      scrape_load_data()
         scrapes and loads club page into database

   FRONTEND
      All templates are found in 'templates' folder