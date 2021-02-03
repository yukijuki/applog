from flask import request, session, redirect, jsonify, render_template, Response, url_for, abort, flash
from app import app, db, storage
from app.function import session_verify
from werkzeug.utils import secure_filename
from PIL import Image
import uuid, datetime, json


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


@app.route("/screen", methods=["GET"])
def screen():
    

    # "screen_id": screen_id,
    # "project_name": project_name,
    # "screen_name": screen_name,
    # "screen_category": screen_category,
    # "log":

    #check session
    project_name = session.get('project_name')
    if project_name == "paypay":
        pass
    else:
        flash("現在テストユーザーしか使えません")
        return redirect(url_for('project'))

    try:        
        data = db.child("screen").get()
        print(data.each())
        if data.each() is None:
            render_all_screens = ""

        else:
            render_all_screens = []
            for screen in data.each():

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

@app.route("/screen/<screen_id>", methods=["GET", "POST"])
def log(screen_id):

    #check session
    project_name = session.get('project_name')
    if project_name == "paypay":
        pass
    else:
        flash("現在テストユーザーしか使えません")
        return redirect(url_for('project'))

    # check if other screen
    if screen_id == "project":
        return redirect(url_for('project'))
    elif screen_id == "screen":
        return redirect(url_for('screen'))
    elif screen_id == "upload":
        return redirect(url_for('upload'))

    if request.method == "POST":
        data = request.get_json()
        screen_id = data.pop("screen_id")
        data["log_id"] = str(uuid.uuid4())
        print("screen_id", screen_id)

        db.child("screen/"+screen_id+"/log").push(data)
        return Response(response=json.dumps(data), status=200)

    data = db.child("screen/"+screen_id+"/log").get().val() 
    if data is None:
        logs = []
    else:
        logs = dict(data).values()
    print(logs)

    image = storage.child("image/"+screen_id).get_url(None)

    return render_template('log.html',logs = logs, image=image, screen_id=screen_id)


@app.route("/upload", methods=["GET", "POST"])
def upload():

    #check session
    project_name = session.get('project_name')
    if project_name == "paypay":
        pass
    else:
        flash("現在テストユーザーしか使えません")
        return redirect(url_for('project'))

    if request.method == "POST":
        print("check")
        if request.form:
            data = request.form
            screen_id = str(uuid.uuid4())
            project_name = "paypay"
            screen_name = data["screen_name"]
            screen_category = data["screen_category"]
            image = request.files["screen_image_name"]
            image.filename = screen_id
            log = []

            d = datetime.datetime.now()
            created_at = json.dumps({"unixtime":d.timestamp()})
            updated_at = created_at


            screen = {
                "screen_id": screen_id,
                "project_name": project_name,
                "screen_name": screen_name,
                "screen_category": screen_category,
                "created_at": created_at,
                "updated_at": updated_at,
                "log": []
            }

            db.child("screen/"+screen_id).set(screen)
            storage.child("image/"+screen_id).put(image)

            flash("新しいスクリーンが追加されました")

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