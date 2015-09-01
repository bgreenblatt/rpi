from flask import Flask, request, url_for
from flask import render_template
import random
import sqlite3 as sql
from operator import itemgetter

app = Flask(__name__)
app.secret_key = 'This is really unique and secret'

class TeamRPI:
    def __init__(self):
        self.rank = 0
        self.team = ''
        self.rpi = ''

class TeamDetails:
    def __init__(self):
        self.team = ''
        self.tscore = ''
        self.oscore = ''
        self.date = ''
        self.result = ''

@app.route('/rpi/')
@app.route('/rpi/<name>')
def projects(name=None):
    dbPath = '/home/bgreenblatt/mysite/db/rpi.db'
    con = sql.connect(dbPath)
    query = ("select team, NumGames, NumWins, ONumGames, " +
           "ONumWins, OONumGames, OONumWins from rpi")
    cur = con.cursor()
    i = 0

    li_rpi = []
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
            team = row[0]
            num_games = float(row[1])
            num_wins = float(row[2])
            onum_games = float(row[3])
            onum_wins = float(row[4])
            oonum_games = float(row[5])
            oonum_wins = float(row[6])
            rpi = (0.25 * (num_wins / num_games) +
                  0.50 * (onum_wins / onum_games) +
                  0.25 * (oonum_wins / oonum_games))
            li_rpi.append((team, rpi))
    li_rpi_sorted = sorted(li_rpi, reverse=True, key=itemgetter(1))
    del li_rpi[:]
    for item in li_rpi_sorted:
        i = i + 1
        tr = TeamRPI()
        tr.team = item[0]
        tr.rpi = str(item[1])
        tr.rank = i
        li_rpi.append(tr)

    if con:
        con.close()
    return render_template('template.html', name='RPI for NCAA Basketball 2014', items=li_rpi)

@app.route('/')
def home_page():
    dbPath = '/home/bgreenblatt/mysite/db/rpi.db'
    con = sql.connect(dbPath)
    query = ("select team from rpi")
    cur = con.cursor()
    li = []
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        tr = TeamRPI()
        tr.team = row[0]
        li.append(tr)
    return render_template('home.html', actionname=url_for('team_details'),
        items=li, name='RPI Home Page')

@app.route('/team_details', methods=['POST'])
def team_details():
    team = request.form["team"]
    dbPath = '/home/bgreenblatt/mysite/db/rpi.db'
    con = sql.connect(dbPath)
    query = ("select team, NumGames, NumWins, ONumGames, " +
           "ONumWins, OONumGames, OONumWins from rpi " +
           "where team = ?")
    cur = con.cursor()
    cur.execute(query, [team])
    rows = cur.fetchall()
    for row in rows:
        num_games = float(row[1])
        num_wins = float(row[2])
        onum_games = float(row[3])
        onum_wins = float(row[4])
        oonum_games = float(row[5])
        oonum_wins = float(row[6])
        rpi = (0.25 * (num_wins / num_games) +
               0.50 * (onum_wins / onum_games) +
               0.25 * (oonum_wins / oonum_games))
    str_rpi = "%.4f" % rpi
    query = ("select Opponent, Date, [Team Score], [Opponent Score], " +
            "[Team Result] from bbscores where team = ?")
    li = []
    cur = con.cursor()
    cur.execute(query, [team])
    rows = cur.fetchall()
    for row in rows:
        td = TeamDetails()
        td.team = row[0]
        td.date = row[1]
        td.tscore = str(row[2])
        td.oscore = str(row[3])
        td.result = row[4]
        li.append(td)
    return render_template('team_details.html', items=li, team=team, rpi=str_rpi)

@app.route('/greet', methods=['POST'])
def greet():
    greeting = random.choice(["Hiya", "Hallo", "Hola", "Ola", "Salut", "Privet", "Konnichiwa", "Ni hao"])
    return """
        <p>%s, %s!</p>
        <p><a href="%s">Back to start</a></p>
        """ % (greeting, request.form["person"], url_for('hello_person'))

