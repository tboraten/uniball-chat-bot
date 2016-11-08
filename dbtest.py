############################################################
#                                                          #
# mysql connection string test                             #
#                                                          #
#                                                          #
############################################################


import MySQLdb as db

HOST = "107.180.0.230"
PORT = 3306
USER = "qbot"
PASSWORD = "ASDF#D23d@!"
DB = "UBS"

try:
    connection = db.Connection(host=HOST, port=PORT,
                               user=USER, passwd=PASSWORD, db=DB)
    name = 'Q8ball'
    test = "select player.player_name, team.team_name from player inner join team on player.team_id = team.team_id where team.team_id = "

    dbhandler = connection.cursor()
    dbhandler.execute("select team_id from player where LOWER(player_name) = '" + name.lower() + "'")
    result = dbhandler.fetchall()
    for item in result:
        if item[0] > 0:
            test2 = test + str(item[0])
            dbhandler.execute(test2)
            result2 = dbhandler.fetchall()
            output = "Team: " + result2[0][1] + "Members: "
            for item2 in result2:
                output = output + item2[0] + " "
                print item2
            print 'DB: aquired team_id, team_name, player names'
            print output
           #connection.commit()

        else:
            print 'db: error aquiring team_id, team_name'


except Exception as e:
    print e

finally:
    connection.close()

