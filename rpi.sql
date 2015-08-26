CREATE TABLE bbscores (
	"Date" text,
	"Team" text,
	"Opponent" text,
	"Team Score" Integer,
	"Opponent Score" Integer,
	"Location" text,
	"Team Margin" Integer,
	"Team Result" text,
	"Team Location" text,
	"Team Avg Scoring Margin" Float,
	"Opponent Average Scoring Margin" Float);

CREATE TABLE rpi (
	TeamID	Integer PRIMARY KEY AUTOINCREMENT,
	Team	text NOT NULL,
	NumGames Integer,
	NumWins Integer,
	ONumGames Integer,
	ONumWins Integer,
	OONumGames Integer,
	OONumWins Integer);

create index bbscores_team_idx on bbscores(team);
create index bbscores_opp_idx on bbscores(opponent);
create index rpi_team_idx on rpi(team);