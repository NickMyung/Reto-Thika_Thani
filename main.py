from flask import Flask


app = Flask(__name__)

@app.route('/app/v1/users')
def users_Action():
    print("Estoy aca")
    return "tu usuario" 

@app.route('/holiwis')
def holis_action():
    print("sipi")
    return "meu" 

app.run(debug = True)