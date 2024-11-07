from datetime import datetime
import sqlite3

def initDB():
    # Подключаемся к базе данных (создаст файл базы, если его нет)
    conn = sqlite3.connect("Database.db")

    # Создаем объект курсора для выполнения SQL-запросов
    cursor = conn.cursor()

    def table_exists(conn, table_name):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE (type='table' or type = 'view') AND name=?
        """, (table_name,))
        result = cursor.fetchone()
        return result is not None

    if(table_exists(conn, 'gameInfo') is False):
        cursor.execute("""
        CREATE TABLE "gameInfo" (
          "mID" text(10) NOT NULL,
          "nameTeam1" TEXT(100),
          "nameTeam2" TEXT(100),
          "idTeam1" TEXT(10),
          "idTeam2" TEXT(10),
          "idYear" TEXT(10),
          "urlCountry" TEXT(150),
          "nameCountry" TEXT(20),
          "dateCreate" DATE,
          PRIMARY KEY ("mID")
        )
        """)
    # Создаем таблицу
    #cursor.execute("""
    #DROP TABLE IF EXISTS "stalkPlayerInGame"
    #""")
    if (table_exists(conn, 'stalkPlayerInGame') is False):
        cursor.execute("""
        CREATE TABLE "stalkPlayerInGame" (
          "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          "idUser" TEXT(100) NOT NULL,
          "mID" TEXT(10) NOT NULL,
          "idPlayer" TEXT(10) NOT NULL,
          "numberPlayer" TEXT(10) NOT NULL,
          "urlCountry" TEXT(150),
          "nameCountry" TEXT(20),
          "teamCom" TEXT(20),
          "dateCreate" DATE
        )
        """)
    if (table_exists(conn, 'playerInfo') is False):
        cursor.execute("""
        CREATE TABLE "playerInfo" (
          "mID" TEXT(10) NOT NULL,
          "idPlayer" TEXT(10) NOT NULL,
          "numberPlayer" TEXT(10) NOT NULL,
          "namePlayer" TEXT(150),
          "nameCountry" TEXT(20),
          "teamCom" TEXT(20),
          "dateCreate" DATE
        )
        """)
    if (table_exists(conn, 'vStalkList') is False):
        cursor.execute("""
        CREATE VIEW vStalkList AS SELECT
            g.nameTeam1,
            g.nameTeam2,
            g.nameCountry,
            p.numberPlayer,
            p.namePlayer,
            s.teamCom,
            s.idUser,
            s.id 
        FROM
            stalkPlayerInGame s
            JOIN playerInfo p ON s.mID = p.mID 
            AND s.teamCom = p.teamCom 
            AND p.numberPlayer = s.numberPlayer
            JOIN gameInfo g ON g.mID = p.mID
        """)



def add_match_info(objectInfoMatch):
    mID = objectInfoMatch.get("mID", "")
    nameTeam1 = objectInfoMatch.get("nameTeam1", "")
    nameTeam2 = objectInfoMatch.get("nameTeam2", "")
    idTeam1 = objectInfoMatch.get("idTeam1", "")
    idTeam2 = objectInfoMatch.get("idTeam2", "")
    idYear = objectInfoMatch.get("idYear", "")
    urlCountry = objectInfoMatch.get("urlCountry", "")
    nameCountry = objectInfoMatch.get("nameCountry", "")
    dateCreate = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    conn = sqlite3.connect("Database.db")
    cursor = conn.cursor()
    exist = get_record_DB('gameInfo', mID)
    try:
        if (exist is None):
            cursor.execute("""
                INSERT INTO gameInfo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mID, nameTeam1, nameTeam2, idTeam1, idTeam2, idYear, urlCountry, nameCountry, dateCreate))
            conn.commit()
    except:
        pass

def add_stalk_info(objectInfoStalk):
    idUser = objectInfoStalk.get("idUser", "")
    mID = objectInfoStalk.get("mID", "")
    idPlayer = objectInfoStalk.get("nameTeam2", "")
    numberPlayer = objectInfoStalk.get("numberPlayer", "")
    urlCountry = objectInfoStalk.get("urlCountry", "")
    nameCountry = objectInfoStalk.get("nameCountry", "")
    teamCom = objectInfoStalk.get("teamCom", "")
    dateCreate = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM stalkPlayerInGame  where mID = '{mID}' and idUser = '{idUser}' and numberPlayer = '{numberPlayer}' and teamCom = '{teamCom}'")
    exists = cursor.fetchone()  # Получаем все строки
    if (exists is not None):
        return "уже отслеживается вами!"


    cursor.execute("""        
        INSERT INTO stalkPlayerInGame ( "idUser", "mID", "idPlayer", "numberPlayer", "urlCountry", "nameCountry", "teamCom", "dateCreate" )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (idUser, mID, idPlayer, numberPlayer, urlCountry, nameCountry, teamCom, dateCreate))
    conn.commit()
    return ""

def add_playerInfo_DB(playerInfo):
    mID = playerInfo.get("mID", "")
    idPlayer = playerInfo.get("idPlayer", "")
    numberPlayer = playerInfo.get("numberPlayer", "")
    namePlayer = playerInfo.get("namePlayer", "")
    nameCountry = playerInfo.get("nameCountry", "")
    teamCom = playerInfo.get("teamCom", "")
    dateCreate = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT * FROM playerInfo  where mID = '{mID}' and numberPlayer = '{numberPlayer}' and teamCom = '{teamCom}'")
    exists = cursor.fetchone()  # Получаем все строки
    if (exists is not None):
        return "уже есть в базе!"

    cursor.execute("""
            INSERT INTO playerInfo VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (mID, idPlayer, numberPlayer, namePlayer, nameCountry, teamCom, dateCreate))
    conn.commit()  # Получаем все строки

def get_record_DB(table, id):
    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}  where mID = '{id}'")
    data = cursor.fetchone()  # Получаем все строки
    return data
def get_playerInfo_DB(mId, numberPlayer, teamCom):
    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM playerInfo where mID = '{mId}' and numberPlayer = '{numberPlayer}' and teamCom = '{teamCom}'")
    data = cursor.fetchone()  # Получаем все строки

    return data
def del_record_DB(table, id):
    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"delete from {table} where mID = '{id}'")
    conn.commit()
    return True
def del_stalk_player(mID, numberPlayer, usrID, teamCom):
    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"delete from stalkPlayerInGame where mID = '{mID}' and numberPlayer = '{numberPlayer}' and idUser = '{usrID}' and teamCom = '{teamCom}'")
    conn.commit()
    return True

def get_all_record_DB(table):
    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    data = cursor.fetchall()  # Получаем все строки

    return data
def get_all_stalk_DB(idUser):
    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM vStalkList where idUser = '{idUser}'")
    data = cursor.fetchall()  # Получаем все строки

    return data

def del_stalk_DB(id):
    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM vStalkList where id = '{id}'")
    data = cursor.fetchone()  # Получаем все строки
    cursor.execute(f"DELETE FROM stalkPlayerInGame where id = '{id}'")
    conn.commit()

    return data

