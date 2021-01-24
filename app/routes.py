from flask import request, session, redirect, send_from_directory, jsonify, render_template, make_response, url_for, abort, flash
from app import app, db, storage
from app.function import session_verify
from werkzeug.utils import secure_filename
from PIL import Image
import uuid


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

# @app.route("/profile", methods=["GET", "POST"])
# def profile():
#     session_verify()
#     student = Student.query.filter_by(email=email).first()

#     if  request.method == "POST":
#         data = request.get_json()

#         if data["password"] == "":
#             data["password"] = student.password

#         if data["name"] == '':
#             data["name"] = student.name

#         if data["industry"] == '':
#             data["industry"] = student.industry

#         student.password = data["password"]
#         student.name = data["name"]
#         student.industry = data["industry"]
#         db.session.commit()
#         flash("変更されました。")


#         session["Industry"] = data["industry"]

#         response = make_response(jsonify(data, 200))
#         return response

#     return render_template("profile.html", data = student)

@app.route("/screen", methods=["GET"])
def screen():

    # "screen_id": screen_id,
    # "project_name": project_name,
    # "screen_name": screen_name,
    # "screen_category": screen_category,
    # "log":

    session_verify()
    try:        
        data = db.child("screen").get()
        render_all_screens = []

        for screen in data.each():
            print(screen.val())
            render_screen = {
                "screen_id": screen.val()["screen_id"],
                "screen_name": screen.val()["screen_name"],
                "screen_image_name": storage.child("image/"+screen.val()["screen_id"]).get_url(None)
            }
            render_all_screens.append(render_screen)

    except ConnectionError:
        abort(404)
        flash("なんかバグった")

    return render_template("screen.html", screens = render_all_screens)

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
            screen_id = str(uuid.uuid4())
            project_name = "paypay"
            screen_name = data["screen_name"]
            screen_category = data["screen_category"]
            image = request.files["screen_image_name"]
            image.filename = screen_id
            log = []

            screen = {
                "screen_id": screen_id,
                "project_name": project_name,
                "screen_name": screen_name,
                "screen_category": screen_category,
                "log": [

                    {
                        "log_id":"log_id",
                        "event_name": "event_name",
                        "event_category": "event_category",
                        "firebase_screen": "firebase_screen",
                        "event_action": "event_action",
                        "event_label": "event_label",
                        "event_label2": "event_label2",
                        "location_num": "location_num"
                    }

                ]
            }

            db.child("screen/"+screen_id).set(screen)
            storage.child("image/"+screen_id).put(image)
            
            # if not allowed_image(image.filename):
            #     flash("PNG, JPG, JPEGを選んでください")
            #     return redirect(request.url)
            # else:
            #     filename = secure_filename(image.filename)
            #     emp_file = Employee.query.filter_by(filename=filename).first()
            #     if emp_file:
            #         flash("ファイル名を変更してください")
            #         return redirect(request.url)

            flash("新しいスクリーンが追加されました")

            # render_template("upload.html") with parameter here
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