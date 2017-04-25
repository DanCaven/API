from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
import os

client = MongoClient("mongodb://API:Hd0917Fk@ds117251.mlab.com:17251/heroku_nrsd7fql")
db = client.school

app = Flask(__name__)

@app.route("/test")
def test():
    return client.database_names()

@app.route("/NewUser")
def newUser():
    info = request.args
    user = info.get("user")
    result = db.school.find_one({"user":user})
    if result != None:
        return "username already present"
    word = info.get("word")
    result =  db.school.insert_one({"user":user,"word":word,"classes":[]})
    return result

@app.route("/login")
def login():
    info = request.args
    user = info.get("user")
    print(user)
    result = db.school.find_one({"user":user})
    if result == None:
        return "username not present"
    word = info.get("pass")
    print(result)
    if result["word"] == word:
        return "verified"


@app.route("/api/Agenda/upload/<tpe>")
def add(tpe):
    if tpe == "class":
        result = db.school.find_one({"code":request.args.get("code")})
        if result != None:
            return jsonify("present")
        info = request.args
        code = info.get("code").lower()
        prof = info.get("prof").lower()
        time =  info.get("time").lower()
        name = info.get("name").lower()
        clss = { "code":code,
        "name":name,
        "professor":prof,
        "time":time,
        "assignments":{}
        }
        print(clss)
        result = db.school.insert_one(clss)
        print(result)
        return "confirm"
    elif tpe == "assignments":
        print("in")
        info = request.args
        code = info.get("code").lower()
        name = info.get("name").lower()
        due = info.get("due").lower()
        points = info.get("points").lower()
        topics = info.get("topics").lower()
        cursor = db.school.find_one({"code":code})
        if 1==2:
            return "never"   ##  need to find a way to check if assignment is already present
        #     return cursor["assignments"][name]
        else:
            packet = {
                 "due":due,
                 "points":points,
                 "flags":[],
                 "topics":topics
                 }
            print(packet)
            result = db.school.update(
            {"code":code},
            {"$set": {
                    "assignments."+name:packet
                },
            }
            )
            print(result)
        return "doen"
    else:
        return "invlaid"




@app.route("/api/Agenda/flag")
def flag():
    info = request.args
    code = info.get("code").lower()
    flag = info.get("flag").lower()
    name = info.get("name").lower()
    #print(info)
    result = db.school.find_one({"code":code})
    print((result))
    assignments = result["assignments"]
    for assignment in assignments:
        print(assignment)
        if assignment == name:
            #print(len(result["assignments"][assignment]["flags"]))
            if len(result["assignments"][assignment]["flags"]) > 4:
                result = db.school.update(
                {"code":code},
                {"$unset":{"assignments."+name:""}}
                )
                print(result)
                return "removed"
            else:
                result = db.school.update(
                {"code":code},
                {"$addToSet": {"assignments."+name+".flags":flag}}
                )
                print(result)
                return jsonify("added")
    return "not present"

@app.route("/api/Agenda/get/<tpe>")
def retrieve(tpe):
    if tpe == "class":
        info = request.args
        name = info.get("name")
        name = str(name).lower()
        print(name)
        cursor = db.school.find_one({"code":name})
        print(cursor)
        # if type(cursor) == None:
        #     return dumps("empty set")
        return dumps(cursor)
    elif tpe == "assignment":
        info = request.args
        code = info.get("code")
        name = info.get("name")
        assignments = school[code]["assignments"]
        try:
            info = cursor["info"]
        except:
            print("here")
            return jsonify({"info":"not present"})
        for assignment in assignments:
            if assignment["name"] == name:
                 return jsonify(assignment)
            else:
                return "assignment not in class"
    else:
        return "code not found"

################################################################################
#################################User Interface#################################
################################################################################


# @app.route("/login", methods=["GET","POST"])
# def login():
#     if "log" in request.args:
#         info = (request.form)
#         user = info['user']
#         if user in data and data[user]["pass"] == info['pass']:
#             return redirect(url_for('profile', username = "dan"))
#     return render_template("login.html")
#
# @app.route("/profile")
# def profile():
#     user = request.args.get("username")
#     return render_template("profile.html", user=user, classes=data[user]['classes'])
#
# @app.route("/classes")
# def classes():
#     clss = request.args.get("clss")
#     url = "http://localhost:5000/api/Agenda/get/class"
#     querystring = {"code":clss}
#     packet = requests.request("GET", url, params=querystring)
#     return packet
#

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
