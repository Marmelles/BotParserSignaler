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
            SELECT name FROM sqlite_master WHERE type='table' AND name=?
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
          "idUser" TEXT(100) NOT NULL,
          "mID" TEXT(10) NOT NULL,
          "idPlayer" TEXT(10) NOT NULL,
          "numberPlayer" TEXT(10) NOT NULL,
          "urlCountry" TEXT(150),
          "nameCountry" TEXT(20),
          "dateCreate" DATE,
          PRIMARY KEY ("idUser")
        )
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
    if (exist is None):
        cursor.execute("""
            INSERT INTO gameInfo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (mID, nameTeam1, nameTeam2, idTeam1, idTeam2, idYear, urlCountry, nameCountry, dateCreate))
        conn.commit()
def add_stalk_info(objectInfoStalk):
    idUser = objectInfoStalk.get("idUser", "")
    mID = objectInfoStalk.get("mID", "")
    idPlayer = objectInfoStalk.get("nameTeam2", "")
    numberPlayer = objectInfoStalk.get("numberPlayer", "")
    urlCountry = objectInfoStalk.get("urlCountry", "")
    nameCountry = objectInfoStalk.get("nameCountry", "")
    dateCreate = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO stalkPlayerInGame VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (idUser, mID, idPlayer, numberPlayer, urlCountry, nameCountry, dateCreate))
    conn.commit()

def get_record_DB(table, id):
    conn = sqlite3.connect("Database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} where mID = '{id}'")
    data = cursor.fetchone()  # Получаем все строки

    return data


