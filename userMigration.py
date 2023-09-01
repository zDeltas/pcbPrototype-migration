import psycopg2.errors
from phpserialize import unserialize
from connection import cnx, conn, MD5
import uuid
import logging

logging.basicConfig(filename='userMigration.log', level=logging.INFO,
                    format='%(levelname)s - %(message)s')

members = []
informations = []


class User:
    def __init__(self, ref, nomsociete, nom, prenom, adresse, cp, ville, pays, tel, email, passe,
                 date, statut, nomprenom1, ship_adress, ship_zip, ship_city, ship_country,
                 contact_mail, contact_nom, account_mail, account_nom, pcb_mail, pcb_nom, clientok):
        self.ref = ref
        self.nomsociete = nomsociete
        self.nom = nom
        self.prenom = prenom
        self.adresse = adresse
        self.cp = cp
        self.ville = ville
        self.pays = pays
        self.tel = tel
        self.email = email
        self.passe = passe
        self.date = date
        self.statut = statut
        self.nomprenom1 = nomprenom1
        self.ship_adress = ship_adress
        self.ship_zip = ship_zip
        self.ship_city = ship_city
        self.ship_country = ship_country
        self.contact_mail = contact_mail
        self.contact_nom = contact_nom
        self.account_mail = account_mail
        self.account_nom = account_nom
        self.pcb_mail = pcb_mail
        self.pcb_nom = pcb_nom
        self.clientok = clientok
        self.rename()

    def rename(self):
        self.ship_adress = self.ship_adress.replace("\'", "'")


class AchatTechnicien:
    def __init__(self, nom, prenom, email, tel):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.tel = tel


class LivraisonFacturation:
    def __init__(self, societe, adresse, null, cp, ville, pays, nom, prenom, email, tel):
        self.societe = societe
        self.adresse = adresse
        self.cp = cp
        self.ville = ville
        self.pays = pays
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.tel = tel


class Info:
    def __init__(self, ref, achat, technicien, livraison, facture):
        self.ref = ref
        self.achat = achat
        self.technicien = technicien
        self.livraison = livraison
        self.facture = facture


def getMembers():
    query_members = "SELECT ref, nomsociete, nom, prenom, adresse, cp, ville, pays, tel, email, " \
                    "passe, date, statut, nomprenom1, ship_adress, ship_zip, ship_city, ship_country, " \
                    "contact_mail, contact_nom, account_mail, account_nom,pcb_mail, pcb_nom, clientok " \
                    "from membres"

    cursorMSQL.execute(query_members)

    results = cursorMSQL.fetchall()

    for row in results:
        user = User(*row)
        members.append(user)


def getInfo():
    query_info = "SELECT ref, information " \
                 "from info"

    cursorMSQL.execute(query_info)

    results = cursorMSQL.fetchall()

    for row in results:
        try:
            information = unserialize(row[1].encode())

            achat = AchatTechnicien(*[v.decode() for v in list(information[b'achat'].values())])
            technicien = AchatTechnicien(*[v.decode() for v in list(information[b'technicien'].values())])
            livraison = LivraisonFacturation(*[v.decode() for v in list(information[b'livraison'].values())])
            facturation = LivraisonFacturation(*[v.decode() for v in list(information[b'facturation'].values())])

            user_information = Info(row[0], achat, technicien, livraison, facturation)
            informations.append(user_information)
        except ValueError:
            logging.error("[ValueError]" + str(row[1].encode()), exc_info=False)


def setUser():
    good = 0
    error = 0
    total = 0

    insert_user = "INSERT INTO \"user\"(id, name, firstname, email, phone, old_password, ref, password) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"

    insert_additional = "INSERT INTO additional(id, company_name, address, zip_code, city, country, create_at, " \
                        "payment_term) " \
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"

    insert_user_additional = "INSERT INTO user_additional(user_id, additional_id)" \
                             "VALUES (%s, %s);"

    for user in members:
        try:
            uuid_user = str(uuid.uuid4())
            uuid_additional = str(uuid.uuid4())

            user_values_ = (uuid_user, user.nom, user.prenom, user.email, user.tel, user.passe, user.ref, "")
            cursorPG.execute(insert_user, user_values_)

            term = "PAYMENT_IN_ADVANCE"

            if user.statut != 0:
                term = "NET_30_DAYS"

            additional_values_ = (uuid_additional, user.nomsociete, user.adresse, user.cp,
                                  user.ville, user.pays, user.date, term)
            cursorPG.execute(insert_additional, additional_values_)

            user_additional_values_ = (uuid_user, uuid_additional)
            cursorPG.execute(insert_user_additional, user_additional_values_)

            conn.commit()
            good += 1
        except psycopg2.errors.SyntaxError as e:
            logging.error(user.ref, exc_info=False)
            conn.rollback()
            error += 1
        except psycopg2.errors.StringDataRightTruncation as e:
            logging.error("[StringDataRightTruncation] - " + user.ref + " " + e.pgerror.replace("\n", ""))
            conn.rollback()
            error += 1
        except psycopg2.errors.InFailedSqlTransaction as e:
            logging.error("[InFailedSqlTransaction] - " + user.ref + " " + e.pgerror.replace("\n", ""))
            logging.warning("[user_values_] - " + str(user_values_))
            logging.warning("[additional_values_] - " + str(additional_values_))
            logging.warning("[user_additional_values_] - " + str(user_additional_values_) + "\n")
            conn.rollback()
            error += 1
        total += 1
    logging.info("[setUser] - error: " + str(error) + " / " + " good: " + str(good) + " total: " + str(total))


def setUserInformationBilling():
    good = 0
    error = 0
    total = 0

    select_user_id = "select id from \"user\" where ref = %s;"

    insert_billing = "INSERT INTO user_billing(id, company_name, address, zip_code, city, country, name, firstname, " \
                     "email, phone) " \
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    insert_user_billing = "INSERT INTO user_user_billing (user_id, user_billing_id)" \
                          "VALUES (%s, %s);"

    for information in informations:
        try:
            information_values_ = (information.ref,)
            cursorPG.execute(select_user_id, information_values_)
            uuid_user = cursorPG.fetchone()
            if len(uuid_user) > 1:
                raise ValueError()

            uuid_billing = str(uuid.uuid4())

            insert_billing_values_ = (
                uuid_billing, information.facture.societe, information.facture.adresse, information.facture.cp,
                information.facture.ville, information.facture.pays, information.facture.nom,
                information.facture.prenom, information.facture.email, information.facture.tel)

            cursorPG.execute(insert_billing, insert_billing_values_)

            insert_user_billing_values_ = (uuid_user[0], uuid_billing)
            cursorPG.execute(insert_user_billing, insert_user_billing_values_)

            conn.commit()
            good += 1

        except ValueError:
            logging.error(information.ref + " corresponding to " + str(uuid_user))

        except psycopg2.errors.SyntaxError as e:
            logging.error(information.ref, exc_info=False)
            conn.rollback()
            error += 1
        except psycopg2.errors.StringDataRightTruncation as e:
            logging.error("[StringDataRightTruncation] - " + information.ref + " " + e.pgerror.replace("\n", ""))
            conn.rollback()
            error += 1
        except psycopg2.errors.InFailedSqlTransaction as e:
            conn.rollback()
            error += 1
        total += 1
    logging.info(
        "[setUserInformationBilling] - error: " + str(error) + " / " + " good: " + str(good) + " total: " + str(total))


def setUserInformationShipping():
    good = 0
    error = 0
    total = 0

    select_user_id = "select id from \"user\" where ref = %s;"

    insert_shipping = "INSERT INTO user_shipping(id, company_name, address, zip_code, city, country, name, firstname, email, phone) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    insert_user_shipping = "INSERT INTO user_user_shipping (user_id, user_shipping_id)" \
                           "VALUES (%s, %s);"

    for information in informations:
        try:
            information_values_ = (information.ref,)
            cursorPG.execute(select_user_id, information_values_)
            uuid_user = cursorPG.fetchone()
            if len(uuid_user) > 1:
                raise ValueError()

            uuid_shipping = str(uuid.uuid4())

            insert_shipping_values_ = (
                uuid_shipping, information.livraison.societe, information.livraison.adresse, information.livraison.cp,
                information.livraison.ville, information.livraison.pays, information.livraison.nom,
                information.livraison.prenom, information.livraison.email, information.livraison.tel)

            cursorPG.execute(insert_shipping, insert_shipping_values_)

            insert_user_shipping_values_ = (uuid_user[0], uuid_shipping)
            cursorPG.execute(insert_user_shipping, insert_user_shipping_values_)

            conn.commit()
            good += 1

        except ValueError:
            logging.error(information.ref + " corresponding to " + str(uuid_user))
            conn.rollback()
            error += 1
        except psycopg2.errors.SyntaxError as e:
            logging.error(information.ref, exc_info=False)
            conn.rollback()
            error += 1
        except psycopg2.errors.StringDataRightTruncation as e:
            logging.error("[StringDataRightTruncation] - " + information.ref + " " + e.pgerror.replace("\n", ""))
            conn.rollback()
            error += 1
        except psycopg2.errors.InFailedSqlTransaction as e:
            conn.rollback()
            error += 1
        total += 1
    logging.info(
        "[setUserInformationShipping] - error: " + str(error) + " / " + " good: " + str(good) + " total: " + str(total))


def setUserInformationEngineer():
    good = 0
    error = 0
    total = 0

    select_user_id = "select id from \"user\" where ref = %s;"

    insert_engineer = "INSERT INTO user_engineer(id, name, firstname, email, phone) " \
                      "VALUES (%s, %s, %s, %s, %s);"

    insert_user_engineer = "INSERT INTO user_user_engineer (user_id, user_engineer_id)" \
                           "VALUES (%s, %s);"

    for information in informations:
        try:
            information_values_ = (information.ref,)
            cursorPG.execute(select_user_id, information_values_)
            uuid_user = cursorPG.fetchone()
            if len(uuid_user) > 1:
                raise ValueError()

            uuid_engineer = str(uuid.uuid4())

            insert_engineer_values_ = (
                uuid_engineer, information.technicien.nom,
                information.technicien.prenom, information.technicien.email, information.technicien.tel)

            cursorPG.execute(insert_engineer, insert_engineer_values_)

            insert_user_engineer_values_ = (uuid_user[0], uuid_engineer)
            cursorPG.execute(insert_user_engineer, insert_user_engineer_values_)

            conn.commit()
            good += 1

        except ValueError:
            logging.error(information.ref + " corresponding to " + str(uuid_user))

        except psycopg2.errors.SyntaxError as e:
            logging.error(information.ref, exc_info=False)
            conn.rollback()
            error += 1
        except psycopg2.errors.StringDataRightTruncation as e:
            logging.error("[StringDataRightTruncation] - " + information.ref + " " + e.pgerror.replace("\n", ""))
            conn.rollback()
            error += 1
        except psycopg2.errors.InFailedSqlTransaction as e:
            conn.rollback()
            error += 1
        total += 1
    logging.info(
        "[setUserInformationEngineer] - error: " + str(error) + " / " + " good: " + str(good) + " total: " + str(total))


def setUserInformationPurchasingDepartment():
    good = 0
    error = 0
    total = 0

    select_user_id = "select id from \"user\" where ref = %s;"

    insert_purchasing_department = "INSERT INTO user_purchasing_department(id, name, firstname, email, phone) " \
                                   "VALUES (%s, %s, %s, %s, %s);"

    insert_user_purchasing_department = "INSERT INTO user_user_purchasing_department (user_id, user_purchasing_department_id)" \
                                        "VALUES (%s, %s);"

    for information in informations:
        try:
            information_values_ = (information.ref,)
            cursorPG.execute(select_user_id, information_values_)
            uuid_user = cursorPG.fetchone()
            if len(uuid_user) > 1:
                raise ValueError()

            uuid_purchasing_department = str(uuid.uuid4())

            insert_purchasing_department_values_ = (
                uuid_purchasing_department, information.achat.nom,
                information.achat.prenom, information.achat.email, information.achat.tel)

            cursorPG.execute(insert_purchasing_department, insert_purchasing_department_values_)

            insert_user_purchasing_department_values_ = (uuid_user[0], uuid_purchasing_department)
            cursorPG.execute(insert_user_purchasing_department, insert_user_purchasing_department_values_)

            conn.commit()
            good += 1

        except ValueError:
            logging.error(information.ref + " corresponding to " + str(uuid_user))

        except psycopg2.errors.SyntaxError as e:
            logging.error(information.ref, exc_info=False)
            conn.rollback()
            error += 1
        except psycopg2.errors.StringDataRightTruncation as e:
            logging.error("[StringDataRightTruncation] - " + information.ref + " " + e.pgerror.replace("\n", ""))
            conn.rollback()
            error += 1
        except psycopg2.errors.InFailedSqlTransaction as e:
            conn.rollback()
            error += 1
        total += 1
    logging.info(
        "[setUserInformationEngineer] - error: " + str(error) + " / " + " good: " + str(good) + " total: " + str(total))


if __name__ == '__main__':
    cursorMSQL = cnx.cursor()
    getMembers()
    getInfo()
    cnx.close()

    cursorPG = conn.cursor()
    setUser()
    setUserInformationBilling()
    setUserInformationShipping()
    setUserInformationEngineer()
    setUserInformationPurchasingDepartment()
    conn.close()
