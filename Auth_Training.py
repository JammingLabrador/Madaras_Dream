import sqlite3

def signup(form_email, form_password):
    conn = sqlite3.connect("email_password_repo.db")
    cursor = conn.cursor()

    a_okay = False
    email_good = False
    password_good = False
    password_has_nums = any(letter.isdigit() for letter in form_password)

    if form_email.endswith(("@gmail.com", "@outlook.com", "@yahoo.com")):
        email_good = True
    if len(form_password) > 5 and password_has_nums:
        password_good = True

    cursor.execute("select * from email_password")
    result = cursor.fetchall()
    for row in result:
        if form_email == row[1]:
            return a_okay

    if email_good and password_good:
        cursor.execute("insert into email_password (email, password) values (?, ?)", (form_email, form_password))
        conn.commit()
        conn.close()
        a_okay = True
        return a_okay

    return a_okay

def login(form_email, form_password):
    a_okay = False
    conn = sqlite3.connect("email_password_repo.db")
    cursor = conn.cursor()
    cursor.execute("select * from email_password where email = ? and password = ?", (form_email, form_password))
    result = cursor.fetchone()
    conn.close()

    if result != None:
        a_okay = True
        return a_okay

    return a_okay