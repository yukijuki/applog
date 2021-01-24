from flask import request, session, redirect, send_from_directory, jsonify, render_template, make_response, url_for, abort, flash
from app import app, db
from app.function import session_verify

@app.route("/")
def index():
    return render_template("project.html")


@app.route("/project", methods=["GET", "POST"])
def project():
    if request.method == "POST":
        data = request.form
        if data["project_name"] == "paypay":
            session["project_name"] = data["project_name"]
            flash("ログイン")
            return redirect(url_for('screen'))

        else:
            flash("現在テストユーザーしか使えません")
            return redirect(url_for('project'))

    return render_template("project.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    session_verify()
    student = Student.query.filter_by(email=email).first()

    if  request.method == "POST":
        data = request.get_json()

        if data["password"] == "":
            data["password"] = student.password

        if data["name"] == '':
            data["name"] = student.name

        if data["industry"] == '':
            data["industry"] = student.industry

        student.password = data["password"]
        student.name = data["name"]
        student.industry = data["industry"]
        db.session.commit()
        flash("変更されました。")


        session["Industry"] = data["industry"]

        response = make_response(jsonify(data, 200))
        return response

    return render_template("profile.html", data = student)

@app.route("/screen", methods=["GET"])
def screen():
    session_verify()
    try:        
        """
        data = {
            "faculty" = "Str",
            "firm" = "Str",
            "industry" = "Str",
            "position": "Str",
            "lab" = "Str",
            "club" = "Str",
        }
        """
        data = db.child("screens").get()
        print(data.val())
        screens = [
            {
                "id": "1",
                "filename": "hey",
                "name": "screen1"

            }
        ]


    except ConnectionError:
        abort(404)
        flash("なんかバグった")

    return render_template("screen.html", screens = screens)

@app.route("/log/<id>", methods=["GET"])
def log(id):
    
    employee_data = {}
    try:        
        employee = Employee.query.filter_by(id=id).first()

        employee_data["id"] = employee.id
        employee_data["name"] = employee.name
        employee_data["filename"] = 'static/img-get/' + employee.filename
        employee_data["link"] = employee.link
        employee_data["faculty"] = employee.faculty
        employee_data["firm"] = employee.firm
        employee_data["industry"] = employee.industry
        employee_data["position"] = employee.position
        employee_data["lab"] = employee.lab
        employee_data["club"] = employee.club
        employee_data["ask_clicks"] = employee.ask_clicks
        
    except ConnectionError:
        abort(404)
        flash("なんかバグった")

    return render_template('log.html', file=employee_data)


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":
        print("chekc")
        if request.form:

            data = request.form
            image = request.files["image"]

            if image.filename == "":
                flash("Image must have a name")
                return redirect(request.url)
            
            if not allowed_image(image.filename):
                flash("PNG, JPG, JPEGを選んでください")
                return redirect(request.url)
            else:
                filename = secure_filename(image.filename)
                emp_file = Employee.query.filter_by(filename=filename).first()
                if emp_file:
                    flash("ファイル名を変更してください")
                    return redirect(request.url)

                image.save(os.path.join(app.config["UPLOAD_FOLDER"], image.filename))

                img = Image.open(os.path.join(app.config["UPLOAD_FOLDER"], image.filename))
                img = crop_max_square(img)
                img_resize_lanczos = img.resize((350, 350), Image.LANCZOS)
                img_resize_lanczos.save(os.path.join(app.config["GET_FOLDER"], image.filename))
                print(filename)

                employee = Employee(
                name = data["name"],
                filename = filename,
                link = data["link"],
                faculty = data["faculty"],
                firm = data["firm"],
                industry = data["industry"],
                position = data["position"],
                lab = data["lab"],
                club = data["club"],
                ask_clicks = 0
                )

                db.session.add(employee)
                db.session.commit()
                flash("Image saved")

            return redirect(request.url)
    return render_template("upload.html")


@app.route("/delete/<id>", methods=['POST', "GET", "DELETE"])
def employee_delete(id):
    email = session.get('Email')
    if email == "admin@gmail.com":
        print(email)
    else:
        flash("adminに入ってください")
        return redirect(url_for('register'))

    b = Employee.query.filter_by(id=id).first()
    db.session.delete(b)
    db.session.commit()
    flash("deleted")

    return render_template("admin.html")