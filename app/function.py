from flask import session, flash, redirect, url_for

def session_verify():
    project_name = session.get('project_name')
    if project_name == "paypay":
        pass
    else:
        flash("現在テストユーザーしか使えません")
        return redirect(url_for('project'))

        