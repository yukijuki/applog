from flask import request, session, redirect, jsonify, render_template, Response, url_for, abort, flash
from app import app, db, storage
from app.function import session_verify
from werkzeug.utils import secure_filename
from PIL import Image
import uuid, datetime, json
import re


beta_project = [
    "paypay", "p2p", "prodops", "teppei", "o-24", "sample1", "sample2"
]

password = "Paypay01"

@app.route("/")
def index():
    return render_template("project.html")


@app.route("/project", methods=["GET", "POST"])
def project():

    session.pop('project_name', None)

    if request.method == "POST":
        data = request.form
        session["project_name"] = data["project_name"]
        flash("ログインしました")
        return redirect(url_for('screen'))

    return render_template("project.html")


@app.route("/screen", methods=["GET"])
def screen():

    #check session
    project_name = session.get('project_name')
    if project_name is None:
        flash("ログインしなおしてください")
        return redirect(url_for('project'))
    # if project_name in beta_project:
    #     pass
    # else:
    #     flash("現在テストユーザーしか使えません")
    #     return redirect(url_for('project'))
    
    searchbar = request.args.get('searchbar', '')

    if searchbar == "":
        try:        
            data = db.child(project_name).get()
            if data.each() is None:
                render_all_screen_sorted = ""

            else:
                render_all_screens = []
                for screen in data.each():
                    render_screen = {
                        "screen_id": screen.val()["screen_id"],
                        "screen_name": screen.val()["screen_name"],
                        "created_at": screen.val()["created_at"],
                        "screen_image_name": storage.child("image/"+screen.val()["screen_id"]).get_url(None)
                    }
                    render_all_screens.append(render_screen)
                
                render_all_screen_sorted = sorted(render_all_screens, key=lambda x:x['created_at'], reverse=True)

        except ConnectionError:
            abort(404)
            flash("Unexpected error contact applogseed@gmail.com")
    else:
        print(searchbar)
        try:        
            data = db.child(project_name).get()
            if data.each() is None:
                render_all_screen_sorted = ""

            else:
                render_all_screens = []
                for screen in data.each():
                    if re.search(searchbar, screen.val()["screen_name"], re.IGNORECASE):
                        render_screen = {
                            "screen_id": screen.val()["screen_id"],
                            "screen_name": screen.val()["screen_name"],
                            "created_at": screen.val()["created_at"],
                            "screen_image_name": storage.child("image/"+screen.val()["screen_id"]).get_url(None)
                        }
                        render_all_screens.append(render_screen)
                    
                render_all_screen_sorted = sorted(render_all_screens, key=lambda x:x['created_at'], reverse=True)

        except ConnectionError:
            abort(404)
            flash("Unexpected error contact applogseed@gmail.com")
        

    return render_template("screen.html", screens = render_all_screen_sorted)

@app.route("/screen/<screen_id>", methods=["GET", "POST"])
def log(screen_id):

    #no check session
    project_name = session.get('project_name')
    if project_name is None:
        return redirect(url_for('signin', screen_id=screen_id))

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

        d = datetime.datetime.now()
        data["created_at"] = json.dumps({"unixtime":d.timestamp()})

        db.child(project_name+"/"+screen_id+"/log").push(data)
        return Response(response=json.dumps(data), status=200)
        #redirect(request.url)

    render_logs = []
    data = db.child(project_name+"/"+screen_id+"/log").get().val() 
    if data is None:
        logs = []
    else:
        logs = db.child(project_name+"/"+screen_id+"/log").get()
        
        for log in logs.each():
            key = log.key()
            val = log.val()
            val["log_id"] = key

            if "log_cursor" not in val:
                val["log_cursor"] = {"x": 430, "y": 150}

            render_logs.append(val)

    image = storage.child("image/"+screen_id).get_url(None)

    render_logs_sorted = sorted(render_logs, key=lambda x:x['created_at'])

    count = 0
    render_logs_sorted_with_id = []
    for log in render_logs_sorted:      
        count = count + 1
        log["log_num"] = count
        render_logs_sorted_with_id.append(log)
    
    #get screen name and add it to the log
    screen_data = db.child(project_name+"/"+screen_id).get().val() 
    if screen_data is None:
        flash("違う人のプロジェクトに入ってしまったのでキックアウトします")
        session.pop('project_name', None)
        return redirect(url_for('project'))
    screen_name = screen_data["screen_name"]

    return render_template('log.html',logs = render_logs_sorted_with_id, image=image, screen_id=screen_id, screen_name=screen_name)


@app.route("/upload", methods=["GET", "POST"])
def upload():

    #check session
    project_name = session.get('project_name')
    if project_name is None:
        flash("ログインしなおしてください")
        return redirect(url_for('project'))
    print("project_name", project_name)

    if request.method == "POST":
        print("check")
        if request.form:
            data = request.form
            screen_id = str(uuid.uuid4())
            screen_name = data["screen_name"]
            #screen_category = data["screen_category"]
            image = request.files["screen_image_name"]
            image.filename = screen_id
            log = []

            d = datetime.datetime.now()
            created_at = json.dumps({"unixtime":d.timestamp()})


            screen = {
                "screen_id": screen_id,
                "screen_name": screen_name,
                # "screen_category": screen_category,
                "created_at": created_at,
                "log": []
            }

            db.child(project_name+"/"+screen_id).set(screen)
            storage.child("image/"+screen_id).put(image)

            flash("新しいスクリーンが追加されました")
            return redirect(url_for('screen'))

    return render_template("upload.html")

@app.route("/signin/<screen_id>", methods=["GET", "POST"])
def signin(screen_id):
    if request.method == "GET":
        flash("プロジェクト名を入力してください")
    if request.method == "POST":
        data = request.form
        session["project_name"] = data["project_name"]
        flash("ログインしました")
        print("test", screen_id)
        return redirect(url_for('log', screen_id=screen_id))
    
    return render_template("signin.html", screen_id=screen_id)



@app.route("/delete_log", methods=['POST'])
def delete_log():
    if request.method == "POST":
        project_name = session.get('project_name')
        data = request.get_json()
        screen_id = data["screen_id"]
        log_id = data["log_id"]
        print("log_id", log_id)
        print("screen_id", screen_id)
        db.child(project_name+"/"+screen_id+"/log/"+log_id).remove()
        return Response(response=json.dumps(data), status=200)

@app.route("/delete_screen", methods=['POST'])
def delete_screen():
    if request.method == "POST":
        project_name = session.get('project_name')
        data = request.get_json()
        screen_id = data["screen_id"]
        print("screen_id", screen_id)
        db.child(project_name+"/"+screen_id).remove()
        return Response(response=json.dumps(data), status=200)

@app.route("/update_log_cursor", methods=['POST'])
def update_log_cursor():
    if request.method == "POST":
        project_name = session.get('project_name')
        data = request.get_json()
        screen_id = data["screen_id"]
        log_id = data["log_id"]
        x = data["x"]
        y = data["y"]

        log_cursor = {
            "x": x,
            "y": y
        }

        db.child(project_name+"/"+screen_id+"/log/"+log_id+"/log_cursor").set(log_cursor)
        return Response(response=json.dumps(log_cursor), status=200)
