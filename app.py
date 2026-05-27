from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3



app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect('bookings.db')
    conn.execute("""
    CREATE TABLE IF NOT EXISTS bookings(
        username TEXT,
        email TEXT,
        phone TEXT,        
        event_name TEXT,
        date TEXT,
        venue TEXT,
        capacity INTEGER,
        service TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.close()


    # USERS
    conn = sqlite3.connect('users.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            email TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.close()

    # ADMIN
    conn = sqlite3.connect('admin.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin(
            email TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.close()

    # EVENTS
    conn = sqlite3.connect('events.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events(
            name TEXT,
            image TEXT
        )
    """)
    conn.close()



# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        db = 'admin.db' if role == 'admin' else 'users.db'
        table = 'admin' if role == 'admin' else 'users'
        try:
            conn = sqlite3.connect(db,timeout=10)
            conn.execute(f"INSERT INTO {table} (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            flash("Registration Successful!","success")
            return redirect('/login')

        except sqlite3.IntegrityError:
            flash("Email alredy exist! please enter different email","error")
        except sqlite3.operationalError as e:
            flash(f"Database Error:{e}")
        finally:
            conn.close()
    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        email= request.form['email']
        password = request.form['password']

        db = 'admin.db' if role == 'admin' else 'users.db'
        table = 'admin' if role == 'admin' else 'users'
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['email'] = email
            session['role'] = role



            if role == 'admin':
                return redirect('/admin_dashboard')
            else:
                return redirect('/user_dashboard')
        else:
            flash("Invalid Credentials!","error")

    return render_template("login.html")

# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin_dashboard')
def admin_dashboard():
    conn = sqlite3.connect('events.db')
    events = conn.execute("SELECT * FROM events").fetchall()
    conn.close()

    conn = sqlite3.connect('bookings.db')
    bookings = conn.execute("SELECT * FROM bookings").fetchall()
    conn.close()

    return render_template("admin_dashboard.html", events=events, bookings=bookings)

# ---------------- ADD EVENT ----------------
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        image = request.form['image']  # image filename

        conn = sqlite3.connect('events.db')
        conn.execute("INSERT INTO events (name,image) VALUES (?, ?)", (name, image))
        conn.commit()
        conn.close()

        flash("Event Added Successfully!")
        return redirect('/admin_dashboard')

    return render_template("add_event.html")

# ---------------- DELETE EVENT ----------------
@app.route('/delete_event/<int:id>')
def delete_event(id):
    conn = sqlite3.connect('events.db')
    conn.execute("DELETE FROM events WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash("Event Deleted!")
    return redirect('/admin_dashboard')

# ---------------- EDIT EVENT ----------------
@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    conn = sqlite3.connect('events.db')

    if request.method == 'POST':
        name = request.form['name']
        image = request.form['image']

        conn.execute("UPDATE events SET name=?, image=? WHERE id=?", (name, image, id))
        conn.commit()
        conn.close()

        flash("Event Updated!")
        return redirect('/admin_dashboard')

    event = conn.execute("SELECT * FROM events WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("edit_event.html", event=event)

# ---------------- USER DASHBOARD ----------------
@app.route('/user_dashboard')
def user_dashboard():
    conn = sqlite3.connect('events.db')
    events = conn.execute("SELECT * FROM events").fetchall()
    conn.close()

    return render_template("user_dashboard.html", events=events)
#----------------BOOK EVENT-------------------------------
@app.route('/book_event')
def book_event():
    event_name=request.args.get('event_name')
    return render_template("book_event.html", event_name=event_name)
#--------------SUBMIT BOOKING-------------------------------

@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    try:
        username = request.form.get('username')
        email=request.form.get('email')
        phone = request.form.get('phone')
        venue = request.form.get('venue')
        capacity = request.form.get('capacity')
        event_name = request.form.get('event_name')
        date=request.form.get('date')

        service=request.form.getlist('service')
        service_str = ", ".join(service)


        conn = sqlite3.connect('bookings.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO  bookings(username, email, phone, event_name, venue, capacity, date, service)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                    ''',(username, email, phone, event_name, venue, capacity, date, service_str))
        conn.commit()
        conn.close()
        flash("Booking Confirmed! ")
        return redirect('/user_dashboard')
    except Exception as e:
        return f"Error: {e}"


#-------delete booking--------------------
'''@app.route('delete_bookings/<int:id>')
def delete_bookings(id):
    if session.get('role') !='admin':
        return redirect('/login')
    conn=init_db()
    conn.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin_dashboard')'''

#-----------VIEW BOOKING------------------------------------------------------
@app.route('/view')
def view_bookings():
    conn=sqlite3.connect('bookings.db')
    data=conn.execute("SELECT * FROM bookings").fetchall()
    conn.close()
    return render_template("view.html", bookings=data)


#-----veiw--------
@app.route('/view')
def view_page():
    return render_template('view.html')

#--------user profile----------
import sqlite3
def get_db():
    conn=sqlite3.connect('bookings.db')
    conn.row_factory=sqlite3.Row
    return conn

@app.route('/user_profile')
def user_profile():
    if 'email' not in session:
        return redirect('/login')
    conn=get_db()
    user=conn.execute(
        "SELECT username,email,phone FROM bookings WHERE email=?",
                (session['email'],)).fetchone()
    bookings=conn.execute(
            "SELECT * FROM bookings WHERE email=?",
            (session['email'],)
        ).fetchall()

    return render_template('user_profile.html', user=user, bookings=bookings)






#------edit booking-------
@app.route('/edit_booking/<email>',methods=['GET', 'POST'])
def edit_booking(email):

    conn = sqlite3.connect('bookings.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # UPDATE BOOKING
    if request.method == 'POST':

        event_name = request.form['event_name']
        date = request.form['date']
        venue = request.form['venue']
        capacity = request.form['capacity']
        service = request.form['service']

        cur.execute("""
            UPDATE bookings
            SET event_name=?,
                date=?,
                venue=?,
                capacity=?,
                service=?
            WHERE email=?
        """, (
            event_name,
            date,
            venue,
            capacity,
            service,
            email
        ))

        conn.commit()
        conn.close()

        flash("Booking Updated!", "success")

        return redirect('/user_profile')

    # FETCH BOOKING
    cur.execute(
        "SELECT * FROM bookings WHERE email=?",
        (email,)
    )

    booking = cur.fetchone()

    conn.close()

    return render_template(
        'edit_booking.html',
        booking=booking
    )


# ----------------Logout----------------
@app.route('/logout')
def logout():
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)