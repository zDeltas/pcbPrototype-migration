import logging

import mysql
import psycopg2.errors

from connection import cnx, conn

logging.basicConfig(filename='migrateTrackingNumber.log', level=logging.INFO,
                    format='%(levelname)s - %(message)s')

commandeSuiviList = []
informations = []


class CommandeSuivi:
    def __init__(self, numcommande, date_exp, num_track, type):
        self.numcommande = numcommande
        self.date_exp = date_exp
        self.num_track = num_track
        self.type = type


def getTracking():
    query_members = "SELECT numcommande, date_exp, num_track, type " \
                    "from commande_suivi"

    cursorMSQL.execute(query_members)
    results = cursorMSQL.fetchall()

    for row in results:
        try:
            commandeSuivi = CommandeSuivi(*row)
            commandeSuiviList.append(commandeSuivi)
        except ValueError as e:
            logging.error("[ValueError] - " + str(row[0]) + " " + str(e))


def setTracking():
    good = 0
    error = 0
    total = 0

    insert_tracking = "UPDATE history SET tracking_number = %s WHERE order_number = %s"


    for commandeSuivi in commandeSuiviList:
        print(str(total) + "/" + str(len(commandeSuivi)) + " - " + str(commandeSuivi.numcommande))

        try:
            insert_tracking_values = (commandeSuivi.num_track, commandeSuivi.numcommande)
            cursorPG.execute(insert_tracking, insert_tracking_values)
            conn.commit()
            good += 1

        except ValueError as e:
            logging.error("[ValueError] - " + str(commandeSuivi.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        except TypeError as e:
            logging.error("[TypeError] - " + str(commandeSuivi.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        except psycopg2.errors.SyntaxError as e:
            logging.error("[StringDataRightTruncation] - " + str(commandeSuivi.numcommande), exc_info=False)
            conn.rollback()
            error += 1
        except psycopg2.errors.StringDataRightTruncation as e:
            logging.error("[StringDataRightTruncation] - " + str(commandeSuivi.numcommande) + " " + e.pgerror.replace("\n", ""))
            conn.rollback()
            error += 1
        except psycopg2.errors.InFailedSqlTransaction as e:
            logging.error("[InFailedSqlTransaction] - " + str(commandeSuivi.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        except mysql.connector.errors.InternalError as e:
            logging.error("[mysql-InternalError] - " + str(commandeSuivi.numcommande))
            conn.rollback()
            error += 1
        except psycopg2.errors.InvalidDatetimeFormat as e:
            logging.error("[InvalidDatetimeFormat] - " + str(commandeSuivi.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        except psycopg2.errors.UniqueViolation as e:
            logging.error("[UniqueViolation] - " + str(commandeSuivi.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        total += 1

    logging.info(
        "error: " + str(error) + " / " + " good: " + str(good) + " total: " + str(total))


if __name__ == '__main__':
    cursorMSQL = cnx.cursor()
    cursorPG = conn.cursor()

    # MySQL
    getTracking()

    # PostgreSQL
    setTracking()

    cnx.close()
    conn.close()
