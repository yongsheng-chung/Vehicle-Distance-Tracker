import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from decimal import Decimal, ROUND_UP, ROUND_DOWN

from helpers import apology, login_required, lookup, calculate_distance, convert_secs

# Configure application
app = Flask(__name__)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['DEBUG'] = True
app.config['TESTING'] = True
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///distance.db")

# Obtain API key in global
api_key = os.environ.get("API_KEY")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Check for user inputs
    if request.method == "POST":

        # Obtain origin and destination from html form
        origin = request.form.get("origin")
        destination = request.form.get("destination")
        travel_type = request.form.get("travel-type")
        date = request.form.get("date")
        same_day_return = request.form.get("same-day-return")

        # Print out checkbox value
        print(f"Same day return checkbox returns: {same_day_return}")

        # Check if origin and destination are submitted
        if not origin or not destination or not travel_type:
            flash("Missing origin or destination", "danger")
            return redirect("/")

        # Look up for place
        if lookup(origin) and lookup(destination):
            origin_info = lookup(origin)
            destination_info = lookup(destination)

            # # Test Places API calls
            # origin_address = origin_info["address"]
            origin = origin_info["name"]
            origin_place_id = origin_info["place_id"]
            destination = destination_info["name"]
            destination_place_id = destination_info["place_id"]

            # print(f"Address: {origin_address}")
            # print(f"Name: {origin_name}")
            # print(f"Place ID: {origin_place_id}")
            # print(f"Coordinates: {origin_latlng}")
            # print(f"Address: {destination_address}")
            # print(f"Name: {destination_name}")
            # print(f"Place ID: {destination_place_id}")
            # print(f"Coordinates: {destination_latlng}")

            # Calculate distance by parsing coordinates of origin and destination
            if calculate_distance(origin_info["place_id"], destination_info["place_id"]):

                # Test results
                travel_info = calculate_distance(origin_info["place_id"], destination_info["place_id"])

                # Store travel info
                distance = travel_info["distance"]["value"]
                duration = convert_secs(travel_info["duration"]["value"])

                # Store the travel info in database
                db.execute("INSERT INTO records (user_id, date, origin_name, origin_place_id, destination_name, destination_place_id, distance, duration, travel_type) \
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], date, origin, origin_place_id , destination, destination_place_id, distance, duration, travel_type)

                # If same day return is checked, store the travel info for return trip
                if same_day_return:
                    db.execute("INSERT INTO records (user_id, date, origin_name, origin_place_id, destination_name, destination_place_id, distance, duration, travel_type) \
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], date, destination, destination_place_id, origin, origin_place_id, distance, duration, travel_type)
                flash("Travel record added!", "success")
                return redirect("/")
            else:
                flash("Travel information not found", "danger")
                return apology("Travel info not retrieved")
        else:
            flash("Invalid address", "danger")
            return apology("Invalid address")
    else:
        return render_template("index.html", api_key=api_key)


@app.route("/dashboard")
@login_required
def dashboard():
    """Create a stacked bar chart on distance travelled across different dates"""
    # Create lists to store dates of work and personal travel
    personal_dates = []
    work_dates = []

    # Query for work related travels and append to lists
    work = db.execute("SELECT date, SUM(distance) AS distance FROM records WHERE user_id = ? AND travel_type = ? GROUP BY date", session["user_id"], "Work")
    for row in work:
        work_dates.append(row["date"])

    # Query for personal travel and append to list
    personal = db.execute("SELECT date, SUM(distance) AS distance FROM records WHERE user_id = ? AND travel_type = ? GROUP BY date", session["user_id"], "Personal")
    for row in personal:
        personal_dates.append(row["date"])

    # Merge two arrays of dates from personal and work travel
    dates = list(set(personal_dates + work_dates))

    # Query for sum of distances for personal travel and for work travel
    rows = db.execute("SELECT SUM(distance) as total_work FROM records WHERE user_id = ? AND travel_type = ?", session["user_id"], "Work")
    total_work = rows[0]["total_work"]/1000

    rows = db.execute("SELECT SUM(distance) as total_personal FROM records WHERE user_id = ? AND travel_type = ?", session["user_id"], "Personal")
    total_personal = rows[0]["total_personal"]/1000

    # Calculate percentage of work-related travel and personal travel
    total_distance = total_work + total_personal
    work_percentage = (total_work/total_distance) * 100
    personal_percentage = (total_personal/total_distance) * 100

    # Limit decimal places for percentages
    work_percentage = Decimal(work_percentage).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    personal_percentage = Decimal(personal_percentage).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    return render_template("dashboard.html", work=work, personal=personal, dates=dates, work_percentage=work_percentage, personal_percentage=personal_percentage)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Display travel history in table format"""
    """Query database for all travel records of user"""
    records = db.execute("SELECT rowid, date, origin_name, destination_name, distance, duration, travel_type FROM records WHERE user_id = ? ORDER BY date DESC", session["user_id"])

    return render_template("history.html", records=records)


@app.route("/delete/<int:rowid>")
@login_required
def delete(rowid):
    """Delete the row based on rowid given"""
    print(f"We are trying to delete { rowid }")
    db.execute("DELETE FROM records where user_id = ? AND rowid = ?", session["user_id"], rowid)
    flash("Travel record deleted!", "success")
    return redirect("/history")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Save form details as variables
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Username is required", "danger")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Password is required", "danger")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password", "danger")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash(f"Welcome back {username}!", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    flash("You have successfully log out!", "success")
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Check for correct inputs
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check for empty username or password
        if not username or not password or not confirmation:
            flash("Username or password required", "danger")
            return redirect("/register")

        # Check if passwords match
        if password != confirmation:
            flash("Password does not match!", "danger")
            return redirect("/register")

        # Check if username already exists
        users = db.execute("SELECT username FROM users WHERE username = ?", username)

        if len(users) == 1:
            flash("Username already exists", "danger")
            return redirect("/register")

        # Generate password hash
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

        # Insert user into database
        db.execute("INSERT INTO users(username, hash) values (?, ?)", username, hashed_password)
        flash("You have registered successfully!", "success")
        return redirect("/")
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)