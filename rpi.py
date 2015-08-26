import sqlite3 as sql
import argparse
from operator import itemgetter

class Team:
	def __init__(self, teamname):
		self.teamname = teamname

	def set_win_pct(self, con, num_wins, num_games):
		sql = ("insert into rpi (Team, NumWins, NumGames) " +
		       "values (?, ?, ?)")
		cur = con.cursor()

		try:
			cur.execute(sql, (self.teamname, num_wins, num_games))
		except:
			print("error executing " + sql)
		con.commit()

	def update_opp_opp_win_pct(self, con, num_wins, num_games):
		sql1 = ("update rpi set OONumGames = ? where Team = ?")
		sql2 = ("update rpi set OONumWins = ? where Team = ?")
		cur = con.cursor()

		try:
			cur.execute(sql1, (num_games, self.teamname))
		except:
			print("error executing " + sql1)
		try:
			cur.execute(sql2, (num_wins, self.teamname))
		except:
			print("error executing " + sql2)
		con.commit()

	def update_opp_win_pct(self, con, num_wins, num_games):
		sql1 = ("update rpi set ONumGames = ? where Team = ?")
		sql2 = ("update rpi set ONumWins = ? where Team = ?")
		cur = con.cursor()

		try:
			cur.execute(sql1, (num_games, self.teamname))
		except:
			print("error executing " + sql1)
		try:
			cur.execute(sql2, (num_wins, self.teamname))
		except:
			print("error executing " + sql2)
		con.commit()

	def get_opp_win_count(self, con, opp):
		num_games = 0
		num_wins = 0
		sql = ("select [Team Result] from bbscores where team " +
		       "= ? and opponent = ?")
		cur = con.cursor()

		cur.execute(sql, (self.teamname, opp))
		rows = cur.fetchall()
		for row in rows:
			num_games += 1
			result = row["Team Result"]
			if result == 'Win':
				num_wins += 1
		return (num_games, num_wins)

	def set_opp_opp_win_pct(self, con):
		i = 0
		win_pct = 0.0
		num_games = 0
		sum_wins = 0
		sum_games = 0
		sql = ("select Team, NumGames, NumWins from rpi where team " +
			"in (select distinct opponent as opp from bbscores " +
			"where team in (select distinct opponent from " +
			"bbscores where team = ?))")
		cur = con.cursor()

		cur.execute(sql, (self.teamname,))
		cur.execute(sql, (self.teamname,))
		rows = cur.fetchall()
		for row in rows:
			i += 1
			num_wins = row["NumWins"]
			num_games = row["NumGames"]
			opp = row["Team"]
			win_pct = num_wins / num_games
			sum_wins += num_wins
			sum_games += num_games
			ind_games, ind_wins = self.get_opp_win_count(con, opp)
			sum_games -= ind_games
			sum_wins -= ind_wins
		win_pct = sum_wins / sum_games if (sum_games > 0) else 0
		self.update_opp_opp_win_pct(con, sum_wins, sum_games)
		#print("Team Name: " + self.teamname + ", Opp Opp WinPct: " +
		#      str(win_pct))

	def set_opp_win_pct(self, con):
		i = 0
		win_pct = 0.0
		num_games = 0
		sum_wins = 0
		sum_games = 0
		sql = ("select Team, NumGames, NumWins from rpi where team " +
			"in (select distinct opponent as opp from bbscores " +
			"where team = ?)")
		cur = con.cursor()

		cur.execute(sql, (self.teamname,))
		rows = cur.fetchall()
		for row in rows:
			i += 1
			num_wins = row["NumWins"]
			num_games = row["NumGames"]
			opp = row["Team"]
			win_pct = num_wins / num_games
			sum_wins += num_wins
			sum_games += num_games
			ind_games, ind_wins = self.get_opp_win_count(con, opp)
			sum_games -= ind_games
			sum_wins -= ind_wins
		win_pct = float(sum_wins) / float(sum_games) if (sum_games > 0) else 0
		self.update_opp_win_pct(con, sum_wins, sum_games)
		# print("Team Name: " + self.teamname + ", Opp WinPct: " +
		#      str(win_pct))

def set_rpi(con, top_n):
	sql = ("select team, NumGames, NumWins, ONumGames, " +
	       "ONumWins, OONumGames, OONumWins from rpi")
	cur = con.cursor()
	i = 0

	li_rpi = []
	cur.execute(sql)
	rows = cur.fetchall()
	for row in rows:
		team = row["Team"]
		num_wins = float(row["NumWins"])
		num_games = float(row["NumGames"])
		onum_wins = float(row["ONumWins"])
		onum_games = float(row["ONumGames"])
		oonum_wins = float(row["OONumWins"])
		oonum_games = float(row["OONumGames"])
		rpi = (0.25 * (num_wins / num_games) +
		      0.50 * (onum_wins / onum_games) +
		      0.25 * (oonum_wins / oonum_games))
		li_rpi.append((team, rpi))

	li_rpi_sorted = sorted(li_rpi, reverse=True, key=itemgetter(1))
	for item in li_rpi_sorted:
		i += 1
		if top_n != 0 and i > top_n:
			break
		print("Rank: " + str(i) + ", Team Name: " + item[0] + ", RPI: " +
		      format(item[1], '.4f') )

if __name__ == '__main__':
	i = 0;
	con = sql.connect('rpi.db')
	con.row_factory = sql.Row
	cur = con.cursor()
	sql_cleanup1 = ('delete from rpi');
	sql_cleanup2 = ("Update sqlite_sequence set seq = 0 where "
			+ "name = 'rpi'");
	sql = ('select team, count(opponent) as num_opp from bbscores ' +
	       'group by team')
	parser = argparse.ArgumentParser()
	parser.add_argument('-s', '--show', dest='show', action='store_true',
			    help='show calculated rpi')
	parser.add_argument('-c', '--calc', dest='calc', action='store_true',
			    help='calculate rpi again from bbscores table')
	parser.add_argument('-n', '--top_n', dest='top_n', default=0,
			    help='how many rpis to show')
	args = parser.parse_args()

	if (args.calc):
		cur.execute(sql_cleanup1)
		cur.execute(sql_cleanup2)
		cur.execute(sql)
		rows = cur.fetchall()
		for row in rows:
			team = str(row["team"])
			num_opp = row["num_opp"]
			sql = ("select count(*) as count from bbscores where "
			       "[team result] = 'Win' and team = ?")
			cur.execute(sql, [team])
			rows2 = cur.fetchall()
			for row2 in rows2:
				count = row2[0]
			win_pct = count / num_opp if (num_opp > 0) else 0
			# print("Team Name: " + team + ", Games Played: " + str(num_opp) +
			#		" Num Wins: " + str(count) + " win pct: " +
			#		format(100.0 * win_pct, '.2f') + "%")
			myteam = Team(team)
			myteam.set_win_pct(con, count, num_opp)

		sql = ('select distinct team from rpi');
		cur.execute(sql)
		rows = cur.fetchall()
		for row in rows:
			i += 1
			if ((i % 50) == 0):
				print('Processed ' + str(i) + ' Teams')
			team = str(row["team"])
			myteam = Team(team)
			myteam.set_opp_win_pct(con)
			myteam.set_opp_opp_win_pct(con)

	print('Setting RPI Values')
	set_rpi(con, int(args.top_n))

	if con:
		con.close()
