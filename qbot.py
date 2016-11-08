__author__ = 'Travis'



import win32gui
import time
import pywintypes
import numpy
import sys
import win32com
import win32con
import MySQLdb as db

#db connection settings
HOST = "107.180.0.230"
PORT = 3306
USER = "qbot"
PASSWORD = "ADf23%12"
DB = "UBS"

BOT_NAME = 'Showdown!'
BOT_CHANNEL = 'Showdown'
WM_GETTEXT = 13
WM_SETTEXT = 12

def find_br_chat():
    windows = []
    br_windows = []
    win32gui.EnumWindows(lambda hwnd, resultList: resultList.append(hwnd), windows)
    for w in windows:
        title = win32gui.GetWindowText(w)
        if 'BR Chat - ByteRyder' in title:
            br_windows.append(w)

    print len(br_windows), 'BR Chat instances found'
    print 'Handles(s)', br_windows
    return br_windows

def find_bot_br(br_handles):
    for w in br_handles:
        channels = get_c(w)
        for c in channels:
            if BOT_CHANNEL in c_name(c):
                return w

def get_c(br_instance):
    childlist = []
    channels = []
    win32gui.EnumChildWindows(br_instance,lambda br_instance,oldlist: oldlist.append(br_instance), childlist )
    for w in childlist:
        if 'BRChildClass' in win32gui.GetClassName(w):
            channels.append(w)
            #print win32gui.GetClassName(w) , win32gui.GetWindowText(w), w
    return channels

def c_name(c_instance):
    return win32gui.GetWindowText(c_instance)

def find_bot_c(channels):
    for w in channels:
        if BOT_CHANNEL in w[0]:
            return channels.index(w)
    return -1

def get_c_read_handles(c_instance):
    childlist = []
    win32gui.EnumChildWindows(c_instance,lambda c_instance,oldlist: oldlist.append(c_instance), childlist )
    for w in childlist:
        if 'RichEdit20A' in win32gui.GetClassName(w):
            return w

def get_c_write_handles(c_instance):
    childlist = []
    win32gui.EnumChildWindows(c_instance,lambda c_instance,oldlist: oldlist.append(c_instance), childlist )
    for w in childlist:
        if 'Edit' == win32gui.GetClassName(w):
            return w

def read_channel(c_instance):
    buf_size = 1 + win32gui.SendMessage(c_instance[2], win32con.WM_GETTEXTLENGTH, 0, 0)
    buffer = win32gui.PyMakeBuffer(buf_size)
    win32gui.SendMessage(c_instance[2], win32con.WM_GETTEXT, buf_size, buffer)
    return buffer[:buf_size]

def write_channel(c_instance,text):
    buf_size = len(text)
    win32gui.SendMessage(c_instance[3], win32con.WM_SETTEXT, buf_size, text)
    win32gui.PostMessage(c_instance[3], win32con.WM_CHAR, win32con.VK_RETURN, 0);

def parse_raw(text):
    raw = text
    sentences = []
    while True:
        found = raw.find('\r\n[')
        if found >= 0:
            sentences.append(raw[:raw.find('\r\n[')])
            raw = raw[raw.find('\r\n[')+2:]
        else:
            sentences.append(raw[:len(raw)-3])
            break
    return sentences
def db_connect():
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("SELECT * from player Limit 0,1")
        result = dbhandler.fetchall()
        for item in result:
            #print item
            print 'db connected'
        connection.close()
    except Exception as e:
        print e

    #finally:


def db_register(name):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select count(1) from player where LOWER(player_name) = %s", (name.lower(),) )
        result = dbhandler.fetchall()
        for item in result:
            if item[0] < 1:
                dbhandler.execute("INSERT INTO `player`( `player_name`) VALUES (%s)", (name,))
                result2 = dbhandler.fetchall()
               
                for item2 in result2:
                    print item2
                print 'DB: Player registered'
                connection.commit()
                return 1;
            else:
                print 'Player already exists!'
                return 0;

    except Exception as e:
        print e
        return 0

    #finally:


def db_approve(name):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select player_id from player where LOWER(player_name) = %s", (name.lower() ,))
        result = dbhandler.fetchall()
        for item in result:
            if item[0] > 0:
                dbhandler.execute("UPDATE `player` SET approved=1 WHERE player_id=%s", (str(item[0]),))
                connection.commit()
                print 'DB: approved player'
                #connection.commit()
                return 1
        connection.close()
        print 'db: cannot approve, no player found or does not need'
        return 0

    except Exception as e:
        print e
        return 0

    #finally:


def db_pending():
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select player.player_name from player where approved = 0")
        result2 = dbhandler.fetchall()
        connection.close()
        output = ' &b&iPending Approval: &p'
        for item in result2:
            output = output + item[0] + ",  "
                    #print item2

        print 'DB: pending list aquireds'
                #connection.commit()
        return output;
    except Exception as e:
        print e
        return ""

    #finally:
        #connection.close()

def db_checkuser(name):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select count(1),player.ref,player.captain,approved,email_flag from player where LOWER(player_name) = %s", (name.lower(),))
        result = dbhandler.fetchall()
        connection.close()
        for item in result:
            if item[0] < 1:
                #dbhandler.execute("INSERT INTO `player`( `player_name`) VALUES ('" + name + "')")
                #result2 = dbhandler.fetchall()
                #for item2 in result2:
                #    print item2
                print 'DB: user not registered'
                #connection.commit()
                return 0;
            else:
                #print 'Player already exists!'
                if item[1] == 1:
                    print 'DB: user ref'
                    return 2
                if item[3] == 0:
                    print 'DB: user needs approved'
                    return -1
                #if item[4] == 0;
                    #print 'DB: user needs contact info'
                    #write_channel(channels[index],'&b&i' + name + '&p, we need your email !contact email@address.com')
                    #return -1
                
                return 1;

    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()

def db_myteam(name):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select team_id from player where LOWER(player_name) = %s", (name.lower(),) )
        result = dbhandler.fetchall()
        for item in result:
            if item[0] > 0:
                dbhandler.execute("select player.player_name, team.team_name, player.team_id, team.division, team.W, team.L, team.open from player inner join team on player.team_id = team.team_id where team.team_id = %s", (str(item[0]),) )
                result2 = dbhandler.fetchall()
                connection.close()
                #Enrollment
                output = " &bid: &r" + str(result2[0][2]) + "   &p&bSquad: &p&l" + result2[0][1] + " &p(&g" + str(result2[0][4]) + "&p // &r" + str(result2[0][5]) +  "&p // 0)  (&o&iDiv: &p" + result2[0][3] + ")    &p&bMembers&p&b: &p"
                for item2 in result2:
                    output = output + item2[0] + " "
                    #print item2
                if(result2[0][6] == 1):
                    output = output + " (&i&gOpen&p&i/Closed&p)"
                else:
                    output = output + " (&iOpen&p/&rClosed&p)"
                print 'DB: aquired team_id, team_name, player names'
                #connection.commit()
                return output;
            else:
                print 'db: no team found'
                return "";

    except Exception as e:
        print e
        return ""

    #finally:
        #connection.close()

def db_createteam(name,teamname):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select team_id, player_id from player where LOWER(player_name) = %s", (name.lower(),))
        result = dbhandler.fetchall()
        for item in result:
            if item[0] == 0:
                dbhandler.execute("INSERT INTO `team`( `team_name`, `player1`) VALUES (%s,%s )" , (teamname,str(item[1]),))
                result2 = dbhandler.fetchall()
                #output = "&bTeam-" + str(item[0]) + ": &p&l" + teamname + " &p&bMembers: &p&o " + name
                for item2 in result2:
                    print item2
                print 'DB: team created'
                connection.commit()

                dbhandler.execute("select team_id from team where team_name = %s", (teamname,))
                result3 = dbhandler.fetchall()
                dbhandler.execute("UPDATE `player` SET `team_id`=%s, captain = 1 WHERE player_id=%s",(str(result3[0][0]),str(item[1]),))
                connection.commit()
                connection.close()
                print 'DB: player team_id updated'
                return 1;
            else:
                print 'db: cannot create team, player already on one'
                return 0;

    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()


def db_leave(name):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select team_id, player_id from player where LOWER(player_name) = %s", (name.lower() ,))
        result = dbhandler.fetchall()
        for item in result:
            if item[0] > 0:
                dbhandler.execute("UPDATE `player` SET `team_id`=0, `captain`=0 WHERE player_id=%s", (str(item[1]),))
                connection.commit()
                print 'DB: player removed from team'
                dbhandler.execute("UPDATE `team` SET `division`='tbd', team.full = 0 WHERE team_id=%s", (str(item[0]),))
                connection.commit()
                connection.close()
                print 'DB: reset division'
                #connection.commit()
                return 1
            else:
                print 'db: cannot leave team, no team found'
                return 0

    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()

def db_join(name,id):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select team_id, player_id from player where LOWER(team_id) = %s", (id,))
        result = dbhandler.fetchall()
        for item in result:
            if item[0] > 0:
                dbhandler.execute("select count(*), team.team_id, team.open from player inner join team on player.team_id = team.team_id where team.team_id = %s", (item[0],))
                result2 = dbhandler.fetchall()
                if result2[0][0] < 4 and result2[0][2] == 1:
                    dbhandler.execute("UPDATE `player` SET `team_id`=%s WHERE LOWER(player_name)=%s", (id, name.lower(),))
                    connection.commit()
                    if result2[0][0] == 3:
                        dbhandler.execute("UPDATE `team` SET team.full=1, team.open = 0 WHERE LOWER(team_id)=%s", (id,))
                        connection.commit()
                        print 'DB: teams fullness updated'
                    print 'DB: player added to team'
                    return 1
                if (result2[0][0] < 4 and result2[0][2] == 0):
                    dbhandler.execute("select distinct count(1), invite.player_id, invite.team_id from invite inner join player on invite.player_id = player.player_id where (invite.team_id) = %s and lower(player.player_name) = %s", (str(id),name.lower(),))
                    result3 = dbhandler.fetchall()
                    for item2 in result3:
                        if item2[0] == 0:
                            return 0
                        if item2[0] > 0:
                            dbhandler.execute("UPDATE `player` SET `team_id`=%s WHERE LOWER(player_name)=%s", (id, name.lower(),))
                            connection.commit()
                            print 'DB: player added via invite'
                        if result2[0][0] == 3:
                            dbhandler.execute("UPDATE `team` SET team.full=1, team.open = 0 WHERE LOWER(team_id)=%s", (id,))
                            connection.commit()
                            print 'DB: team fullness updated'
                        return 1

                else:
                    print('DB: team full or closed')
                    return 0
                #connection.commit()
                return 1
            else:
                print 'db: cannot join team, no team found'
                return 0

    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()

def db_showinvites(name):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select distinct player.player_name, team.team_name, invite.team_id, player.team_id from player inner join invite on invite.player_id = player.player_id inner join team on team.team_id = invite.team_id where lower(player.player_name) = %s", (name.lower(),))
        result2 = dbhandler.fetchall()
        output = '  &i&b' + result2[0][0] + '&p(team=&r' + str(result2[0][3]) + '&p)    &bInvites: &p  '
        for item in result2:
            output = output + "&b&r" + str(item[2]) + "&p:&l&i" + item[1] + ',  '
        print 'DB: invite list aquired'
                #connection.commit()
        connection.close()
        return output;

    except Exception as e:
        print e
        return ""

    #finally:
        #connection.close()

def db_invite(name,name2):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select count(1),player.player_id, player.team_id from player where LOWER(player_name) = %s", (name.lower(),) )
        result = dbhandler.fetchall()
        for item in result:
            if item[0] > 0:
                dbhandler.execute("select count(1), player_id from player where lower(player_name) = %s", (name2.lower(),))
                result2 = dbhandler.fetchall()
                if result2[0][0] == 0:
                    return 0
                dbhandler.execute("INSERT INTO `invite`( `player_id`, `team_id`) VALUES (%s,%s)", (str(result2[0][1]), item[2],))
                result2 = dbhandler.fetchall()
                for item2 in result2:
                    print item2
                print 'DB: Player invited'
                connection.commit()
                return 1;
            else:
                print 'db: inviter has no team'
                return 0;
        return 0
    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()

def db_contact(name,email):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select player_id from player where LOWER(player_name) = %s", (name.lower(),))
        result = dbhandler.fetchall()
        for item in result:
            if item[0] > 0:
                dbhandler.execute("UPDATE `player` SET player.email_flag = 1, player.email = %s WHERE player_id=%s", (email.lower(),str(item[0]),))
                connection.commit()
                print 'DB: email updated'
                return 1
            else:
                print 'db: cannot update email, no player found'
                return 0

    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()

def db_lock(name):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select team_id from player where LOWER(player_name) = %s", (name.lower(),))
        result = dbhandler.fetchall()
        for item in result:
            if item[0] > 0:
                dbhandler.execute("UPDATE `team` SET team.open = (team.open ^ 1) WHERE team_id=%s", (str(item[0]),))
                connection.commit()
                print 'DB: lock updated'
                connection.commit()
                return 1
            else:
                print 'db: cannot lock, no team found'
                return 0

    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()

def db_reflock(name,id):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select team_id from team where team_id = %s", (id,))
        result = dbhandler.fetchall()
        for item in result:
            if item[0] > 0:
                dbhandler.execute("UPDATE `team` SET team.open = (team.open ^ 1) WHERE team_id=%s", (str(item[0]),))
                connection.commit()
                print 'DB: lock updated'
                #connection.commit()
                return 1
            else:
                print 'db: cannot lock, no team found'
                return 0

    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()

def db_kick(name,name2):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select team_id,captain, ref from player where lower(player_name) = %s", (name.lower(),))
        result = dbhandler.fetchall()
        for item in result:
            if (item[0] > 0 and item[1] == 1) or item[2] == 1:
                dbhandler.execute("select team_id from player WHERE LOWER(player_name) = %s", (name2.lower(),) )
                result = dbhandler.fetchall()
                if result[0][0] == 0:
                    print 'DB: cannot kick, player has no team'
                    return 0;

                dbhandler.execute("UPDATE player SET team_id = 0 WHERE LOWER(player_name) = %s", (name2.lower(),) )
                connection.commit()
                dbhandler.execute("UPDATE team SET team.full=0, team.division = 'tbd' = 0 WHERE team_id = %s", (str(item[0]),) )
                connection.commit()
                if item[2] == 1:
                    print 'DB: player ref kicked'
                else:
                    print 'DB: player kicked'
                return 1
            else:
                print 'db: cannot kick, no captain or team found'
                return 0

    except Exception as e:
        print e
        return 0

    #finally:
        #connection.close()

def db_freeagents():
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select player.player_name from player where approved = 1 and team_id =0")
        result2 = dbhandler.fetchall()
        output = ' &b&iFree agents: &p: &l&i'
        for item in result2:
            output = output + item[0] + ",  "
                    #print item2

        print 'DB: pending list aquireds'
                #connection.commit()
        return output;

    except Exception as e:
        print e
        return ""

    #finally:
        #connection.close()

def db_list(param1):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select distinct team.team_id from team inner join player ON player.team_id = team.team_id where team.open = %s", (param1,))
        result = dbhandler.fetchall()
        count = len(result)
        counter = 1
        for item in result:
            if item[0] > 0:
                dbhandler = connection.cursor()
                dbhandler.execute("select player.player_name, team.team_name, player.team_id, team.division, team.W, team.L, team.open from player inner join team on player.team_id = team.team_id where team.team_id = %s", (str(item[0]),))
                result2 = dbhandler.fetchall()
                #Enrollment
                #output = " &bid: &r" + str(result2[0][2]) + "   &p&bSquad: &p&l" + result2[0][1] + " &p(&g" + str(result2[0][4]) + "&p // &r" + str(result2[0][5]) +  "&p // 0)  (&o&iDiv: &p" + result2[0][3] + ")    &p&bMembers&p&b: &p"
                output = "#" + str(counter) + " &bid: &r" + str(result2[0][2]) + "   &p&bSquad: &p&l" + result2[0][1] + " &p (&o&iDiv: &p" + result2[0][3] + ")    &p&bMembers&p&b: &p"
                for item2 in result2:
                    output = output + item2[0] + " "
                    #print item2
                #if(result2[0][6] == 1):
                #    output = output + " (&i&gOpen&p&i/Closed&p)"
                #else:
                #    output = output + " (&iOpen&p/&rClosed&p)"
                write_channel(channels[index],output)
                counter = counter + 1
                time.sleep(1.7)
                print 'DB: aquired team_id, team_name, player names'
                #connection.commit()
                #
            else:
                print 'db: no team found'
        if count == 0:
            write_channel(channels[index],"None.")
                #return 0;

    except Exception as e:
        print e

def db_listtourney(param1):
    try:
        connection = db.Connection(host=HOST, port=PORT,
                                   user=USER, passwd=PASSWORD, db=DB)

        dbhandler = connection.cursor()
        dbhandler.execute("select distinct team.team_id, team.seed from team inner join player ON player.team_id = team.team_id where team.division = %s order by team.seed", (param1,))
        result = dbhandler.fetchall()
        count = len(result)
        counter = 1
        for item in result:
            if item[0] > 0:
                dbhandler = connection.cursor()
                dbhandler.execute("select player.player_name, team.team_name, player.team_id, team.division, team.W, team.L, team.open from player inner join team on player.team_id = team.team_id where team.team_id = %s", (str(item[0]),))
                result2 = dbhandler.fetchall()
                #Enrollment
                #output = " &bid: &r" + str(result2[0][2]) + "   &p&bSquad: &p&l" + result2[0][1] + " &p(&g" + str(result2[0][4]) + "&p // &r" + str(result2[0][5]) +  "&p // 0)  (&o&iDiv: &p" + result2[0][3] + ")    &p&bMembers&p&b: &p"
                output = "#" + str(counter) + " &bid: &r" + str(result2[0][2]) + "   &p&bSquad: &p&l" + result2[0][1] + " &p (&o&iDiv: &p" + result2[0][3] + ")    &p&bMembers&p&b: &p"
                for item2 in result2:
                    output = output + item2[0] + " "
                    #print item2
                #if(result2[0][6] == 1):
                #    output = output + " (&i&gOpen&p&i/Closed&p)"
                #else:
                #    output = output + " (&iOpen&p/&rClosed&p)"
                write_channel(channels[index],output)
                counter = counter + 1
                time.sleep(1.7)
                print 'DB: aquired team_id, team_name, player names'
                #connection.commit()
                #
            else:
                print 'db: no team found'
        if count == 0:
            write_channel(channels[index],"None.")
                #return 0;

    except Exception as e:
        print e



    #finally:
        #connection.close()

###################################################################################
##
## Begining of Main
##
###################################################################################


print '---------------------------------------------------'
br_handles = find_br_chat()
bot_handle = find_bot_br(br_handles)
channels = get_c(bot_handle)
channels = [(c_name(w),w,get_c_read_handles(w),get_c_write_handles(w)) for w in channels]
bot_c = find_bot_c(channels)
bot_c_full = channels[bot_c]

if bot_c >= 0:
    db_connect()
    print 'Bot connected'
    print 'Scanning chat...'
    print '---------------------------------------------------'


read_buffer = read_channel(channels[bot_c])
buffer_length = len(read_buffer)


while True:
    index = channels.index(bot_c_full)
    read_buffer = read_channel(channels[index])
    new_buffer = read_buffer[buffer_length-1:]
    buffer_length = len(read_buffer)
    if len(new_buffer) > 1:

        sentences = parse_raw(new_buffer)
        for w in sentences:
            print len(w) , ':' , channels[index][0] , ':' , w

        player_name = new_buffer[new_buffer.find('|] <')+4:new_buffer.find('>')]
        parse = new_buffer[new_buffer.find('> ')+2:]
        command = parse[: parse.find(' ')]
        arg_one = parse[len(command)+1:len(parse)-3]
        if(arg_one.find(' ') > 0):
            arg_one = arg_one[:arg_one.find(' ')]

        new_buffer = new_buffer.lower()

        #print len(new_buffer) , ':' , channels[index][0] , ':' , new_buffer[:len(new_buffer)-3]
        if player_name.lower() + '> !register\r\n' in new_buffer:
            print len('register Command') , ':' , channels[index][0] , ':' , '[*]' , 'register Command'
            #write_channel(channels[index],'&bregister&p Command' + ' ' + player_name)
            if(db_register(player_name) ==  1):
                 write_channel(channels[index],'&iSuccessfully registered..&p&b&iPending approval.')

        if player_name.lower() + '> !contact ' in new_buffer:
            print len('ref contact Command') , ':' , channels[index][0] , ':' , '[*]' , 'ref contact Command'
            if db_checkuser(player_name) == 2:
                if db_contact(player_name,arg_one):
                    write_channel(channels[index],'Contact updated.')

        if player_name.lower() + '> !approve ' in new_buffer:
            print len('approve Command') , ':' , channels[index][0] , ':' , '[*]' , 'approve Command'
            #write_channel(channels[index],'&bregister&p Command' + ' ' + player_name)
            if db_checkuser(player_name) == 2:
                if(db_checkuser(arg_one) == -1):
                    if db_approve(arg_one) ==  1:
                        write_channel(channels[index],'&i&b' + arg_one + '..&p&iApproved!.')
                else:
                    print 'db: user does not need approval'
            else:
                print 'db: cannot approve, not a ref'

        if player_name.lower() + '> !pending\r\n' in new_buffer:
            print len('pending Command') , ':' , channels[index][0] , ':' , '[*]' , 'pending Command'
            #write_channel(channels[index],'&bregister&p Command' + ' ' + player_name)
            if db_checkuser(player_name) == 2:
                write_channel(channels[index],db_pending())

        if player_name.lower() + '> !invite ' in new_buffer:
            print len('invites Command') , ':' , channels[index][0] , ':' , '[*]' , 'invites Command'
            #write_channel(channels[index],'&bregister&p Command' + ' ' + player_name)
            if db_checkuser(player_name):
                if(db_invite(player_name,arg_one)):
                    write_channel(channels[index],'&i' + arg_one + '...&binvited.')
                else:
                    write_channel(channels[index],'&i' + arg_one + '...&bmust be registered.')

        if player_name.lower() + '> !myinvites\r\n' in new_buffer:
            print len('myinvites Command') , ':' , channels[index][0] , ':' , '[*]' , 'myinvites Command'
            #write_channel(channels[index],'&bregister&p Command' + ' ' + player_name)
            if db_checkuser(player_name) > 0:
                text = ""
                text = db_showinvites(player_name)
                if len(text) > 0:
                    write_channel(channels[index],text)
                else:
                    write_channel(channels[index],'  &i..' + player_name + '&p...no invites :(')

#        if player_name.lower() + '> !join ' in new_buffer:
#            print len('join Command') , ':' , channels[index][0] , ':' , '[*]' , 'join Command'
#            if db_checkuser(player_name):
#                if db_join(player_name, (arg_one)):
#                    text = db_myteam(player_name)
#                    write_channel(channels[index],text)

#        if player_name.lower() + '> !leave\r\n' in new_buffer:
#            print len('leave Command') , ':' , channels[index][0] , ':' , '[*]' , 'leave Command'
#            if db_checkuser(player_name):
#                text = db_leave(player_name)
#                if(text > 0):
#                    write_channel(channels[index],'&i..buh bye..')
#                else:
#                    write_channel(channels[index],'&i..nothing to leave..')

#        if player_name.lower() + '> !squads\r\n' in new_buffer:
#            print len('listopen Command') , ':' , channels[index][0] , ':' , '[*]' , 'listopen Command'
#            if db_checkuser(player_name):
#                write_channel(channels[index],"&g&iOpen&p enrollment squads:")
#                db_list(1)
#                time.sleep(1.0)
#                write_channel(channels[index],"&r&iClosed/Private&p enrollment squads:")
#                db_list(0)

        if player_name.lower() + '> !squads\r\n' in new_buffer:
            print len('listopen Command') , ':' , channels[index][0] , ':' , '[*]' , 'listopen Command'
            if db_checkuser(player_name):
                write_channel(channels[index],"&g&iExpert&p Division:")
                db_listtourney('expert')
                time.sleep(1.0)
                write_channel(channels[index],"&r&iIntermediate&p Division:")
                db_listtourney('inter')


        
        if player_name.lower() + '> !listopen\r\n' in new_buffer:
            print len('listopen Command') , ':' , channels[index][0] , ':' , '[*]' , 'listopen Command'
            if db_checkuser(player_name):
                write_channel(channels[index],"&g&iOpen&p enrollment squads:")
                db_list(1)

        if player_name.lower() + '> !freeagents\r\n' in new_buffer:
            print len('freeagents Command') , ':' , channels[index][0] , ':' , '[*]' , 'freeagents Command'
            if db_checkuser(player_name):
                text = db_freeagents()
                write_channel(channels[index],text)


        if player_name.lower() + '> !listclosed\r\n' in new_buffer:
            print len('listclosed Command') , ':' , channels[index][0] , ':' , '[*]' , 'listclosed Command'

            if db_checkuser(player_name):
                write_channel(channels[index],"&r&iClosed/Private&p enrollment squads:")
                db_list(0)

        if player_name.lower() + '> !lock\r\n' in new_buffer:
            print len('lock Command') , ':' , channels[index][0] , ':' , '[*]' , 'lock Command'
            if db_lock(player_name):
                write_channel(channels[index],'Squad lock updated.')

        if player_name.lower() + '> !lock ' in new_buffer:
            print len('ref lock Command') , ':' , channels[index][0] , ':' , '[*]' , 'ref lock Command'
            if db_checkuser(player_name) == 2:
                if db_reflock(player_name,arg_one):
                    write_channel(channels[index],'Squad lock updated.')

#        if player_name.lower() + '> !kick ' in new_buffer:
#            print len('kick Command') , ':' , channels[index][0] , ':' , '[*]' , 'kick Command'
#            if db_checkuser(player_name) > 0:
#                if db_kick(player_name,arg_one):
#                    write_channel(channels[index],'&b&ibooom..&p' + arg_one + '&p player removed.' )

#        if player_name.lower() + '> !createsquad ' in new_buffer:
#            print len('createteam Command') , ':' , channels[index][0] , ':' , '[*]' , 'createteam Command : ' , arg_one
#            if db_checkuser(player_name):
#                if len(arg_one) < 24:
#                    text = db_createteam(player_name,arg_one)
#                    if(text > 0):
#                        text = db_myteam(player_name)
#                        write_channel(channels[index],text)


        if player_name.lower() + '> !mysquad\r\n' in new_buffer:
            print len('myteam Command') , ':' , channels[index][0] , ':' , '[*]' , 'myteam Command'
            if db_checkuser(player_name):
                text = db_myteam(player_name)
                if(text > 0):
                    write_channel(channels[index],text)
                else:
                    write_channel(channels[index],player_name + ' you need to join or create a squad.')


        if player_name.lower() + '> !rules\r\n' in new_buffer:
            print len('rules Command') , ':' , channels[index][0] , ':' , '[*]' , 'rules Command'
            write_channel(channels[index],"&bRules:&p http://www.ubshowdown.com/rules.php")

        if player_name.lower() + '> !schedule\r\n' in new_buffer:
            print len('rules Command') , ':' , channels[index][0] , ':' , '[*]' , 'rules Command'
            write_channel(channels[index],"&bSchedule:&p http://www.ubshowdown.com/schedule.php")

        if player_name.lower() + '> !help\r\n' in new_buffer:
            print len('help Command') , ':' , channels[index][0] , ':' , '[*]' , 'help Command'
            write_channel(channels[index],'&bCommands: &p!register, !createsquad &p&rsquad_name&p &b(No spaces in squad name)&p, !invite &p&gplayer_name&p, !kick &p&gplayer_name&p, !join &p&rsquad_id&p, !leave, !mysquad, &b!squads&p, !myinvites, !lock, !listopen, !listclosed, !freeagents, !rules, !schedule')
            #write_channel(channels[index],'&bCommands: &p!register, !createsquad &p<&rsquad_name&p>, !join &p<&rsquad_name&p>, !leave, !invite &p<&gplayer_name&p>, !kick &p<&gplayer_name&p>, !myteam, !myinvites, !showinvites &p<&rsquad_name&p>')

        #print len(new_buffer) , ':' , new_buffer

print channels

test = '<Q8ball> thats odly what i expected\r\n[21:04] <bizarre> sick mohawk\r\n\x00'





