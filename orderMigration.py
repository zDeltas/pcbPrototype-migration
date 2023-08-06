import psycopg2.errors
from phpserialize import unserialize
from connection import cnx, conn, MD5
import uuid
import logging

logging.basicConfig(filename='orderMigration.log', level=logging.INFO,
                    format='%(levelname)s - %(message)s')

orders = []
informations = []


def get_value_asksend(t):
    if isinstance(t, tuple) and len(t) == 0:
        return "ASK"
    elif isinstance(t, tuple) and len(t) == 1:
        return "DONE"
    else:
        return "NONE"


class Fr4Other:
    def __init__(self, id, numcommande, doyouneed, doyougerb, datecode, datecodewhere, rohslogo, whererohlogo, ullogo,
                 whereullogo, smallesttracewidth, FinishedHoleDiameter, controlledimpedance, viainpad, platedholes,
                 sideplating, vcut, Countersunkholes, Edgebeveling, carbonprinting, peelablemask, viaplug, ipc, stencil,
                 thickness, padreduction):
        self.numcommande = numcommande
        self.doyouneed = doyouneed
        self.doyougerb = doyougerb
        self.datecode = datecode
        self.datecodewhere = datecodewhere
        self.rohslogo = rohslogo
        self.whererohlogo = whererohlogo
        self.ullogo = ullogo
        self.whereullogo = whereullogo
        self.smallesttracewidth = smallesttracewidth
        self.FinishedHoleDiameter = FinishedHoleDiameter
        self.controlledimpedance = controlledimpedance
        self.viainpad = viainpad
        self.platedholes = platedholes
        self.sideplating = sideplating
        self.vcut = vcut
        self.Countersunkholes = Countersunkholes
        self.Edgebeveling = Edgebeveling
        self.carbonprinting = carbonprinting
        self.peelablemask = peelablemask
        self.viaplug = viaplug
        self.ipc = ipc
        self.stencil = stencil
        self.thickness = thickness
        self.padreduction = padreduction


class BasicRequi:
    def __init__(self, id, numcommande, layer, pcb_thickness, tg, surface_treatment, solder_mask, screen_printing,
                 color_screen, external_copper, base_copper, innerlayer, buildup):
        self.numcommande = numcommande
        self.layer = layer
        self.pcb_thickness = pcb_thickness
        self.tg = tg
        self.surface_treatment = surface_treatment
        self.solder_mask = solder_mask
        self.screen_printing = screen_printing
        self.color_screen = color_screen
        self.external_copper = external_copper
        self.base_copper = base_copper
        self.innerlayer = innerlayer
        self.buildup = buildup


class Order:
    def __init__(self, typedelacommande, typecommande, refmembre, numcommande, partnumber, version, system, qte, pays,
                 livraison, reduction_delais, valeur_unitprice, valeur_nbofpanel, valeur_totalpcbprice,
                 valeur_shippingcost, valeur_totalpcbpriceaftercost, valeur_prixstencil, valeur_reception_date,
                 valeur_prod_date, la_langue, ladevice, producttime, temps_reduction_par_defaut, currency, documents,
                 date, statut, pao, messagecomplement, numerodelacommande):
        self.typedelacommande = typedelacommande
        self.typecommande = typecommande
        self.refmembre = refmembre
        self.numcommande = numcommande
        self.partnumber = partnumber
        self.version = version
        self.system = system
        self.qte = qte
        self.pays = pays
        self.livraison = livraison
        self.reduction_delais = reduction_delais
        self.valeur_unitprice = valeur_unitprice
        self.valeur_nbofpanel = valeur_nbofpanel
        self.valeur_totalpcbprice = valeur_totalpcbprice
        self.valeur_shippingcost = valeur_shippingcost
        self.valeur_totalpcbpriceaftercost = valeur_totalpcbpriceaftercost
        self.valeur_prixstencil = valeur_prixstencil
        self.valeur_reception_date = valeur_reception_date
        self.valeur_prod_date = valeur_prod_date
        self.la_langue = la_langue
        self.ladevice = ladevice
        self.producttime = producttime
        self.temps_reduction_par_defaut = temps_reduction_par_defaut
        self.currency = currency
        self.documents = documents
        self.date = date
        self.statut = statut
        self.pao = pao
        self.messagecomplement = messagecomplement
        self.numerodelacommande = numerodelacommande


def getOrders():
    query_members = "SELECT typedelacommande, typecommande, refmembre, numcommande, partnumber, version, \"system\", " \
                    "qte, pays, livraison, reduction_delais, valeur_unitprice, valeur_nbofpanel, valeur_totalpcbprice, " \
                    "valeur_shippingcost, valeur_totalpcbpriceaftercost, valeur_prixstencil, valeur_reception_date," \
                    " valeur_prod_date, la_langue, ladevise, producttime, temps_reduction_par_defaut, currency, " \
                    "documents, date, statut, pao, messagecomplement, numerodelacommande " \
                    "from commande"

    cursorMSQL.execute(query_members)

    results = cursorMSQL.fetchall()

    for row in results:
        order = Order(*row)
        orders.append(order)


def setOrders():
    select_user_id = "select id from \"user\" where ref = %s;"

    insert_order = "INSERT INTO order (order_number, user_id, create_at, delivery_at, part_number, version, " \
                   "status_order, material_type," \
                   "purchased_order, quantity, country, reduce_prod_time_by, paste_mask_file, approve_gerber, stencil," \
                   "order_content_id, unit_cost, total, cost, shipping_cost, stencil_cost, production_time) " \
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s %s, %s, %s);"

    insert_order_content = "insert into order_content (id, type_design, length, width, quantity_pcb_panel, cross_board, quantity_different_pcb_type," \
                           "is_design_by_customer, custom_panel_id, surface_treatment, solder_mask," \
                           "screen_printing_position, screen_printing_color, layers, thickness, glass_transition," \
                           "copper_thickness_base, copper_thickness_external, copper_thickness_internal, trace," \
                           "finished_hole_size, impedance_control, plated_half_holes, via_in_pad, edge_side_plating," \
                           "counter_sink_hole, edge_beveling, carbon_printing, peelable_mask, via_pluggling, ipc_class," \
                           "jv_cut, serial_number, approvals, date_code, date_code_position, rohs_logo," \
                           "rohs_logo_position, ul_logo, ul_logo_position, smt_stencil_position, stencil_thickness," \
                           "stencil_pad_reduction, paste_mask_file, approve_gerber, additional_comment)" \
                           "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                           "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                           "%s, %s, %s, %s); "

    select_doyouneed_send = "select doyouneed_send from asksend_doyouneed where numcommande = %s;"
    select_teamgerb = "select teamgerb from asksend_gerb where numcommande = %s;"
    select_teamstencilask = "select teamstencilask from asksend_stencil where numcommande = %s;"

    select_fr4_basic_requi = "select id, numcommande, layer, pcb_thickness, tg, surface_treatment, solder_mask, " \
                             "screen_printing, color_screen, external_copper, base_copper, innerlayer, buildup " \
                             "from fr4_basic_requi where numcommande = %s;"

    select_fr4_other = "select id, numcommande, doyouneed, doyougerb, datecode, datecodewhere, rohslogo, " \
                       "whererohlogo, ullogo, whereullogo, smallesttracewidth, FinishedHoleDiameter, " \
                       "controlledimpedance, viainpad, platedholes, sideplating, vcut, Countersunkholes, " \
                       "Edgebeveling, carbonprinting, peelablemask, viaplug, ipc, stencil, thickness, padreduction " \
                       "from fr4_other where numcommande = %s;"

    print(len(orders))

    for order in orders:
        try:
            uuid_order_content = str(uuid.uuid4())

            ref_values_ = (order.refmembre,)
            cursorPG.execute(select_user_id, ref_values_)
            uuid_user = cursorPG.fetchone()

            numcommand = (order.numcommande,)

            cursorMSQL.execute(select_fr4_basic_requi, numcommand)
            select_fr4_basic_requi_result = cursorMSQL.fetchone()

            basicRequi = BasicRequi(*select_fr4_basic_requi_result)

            cursorMSQL.execute(select_fr4_other, numcommand)
            select_fr4_other_requi_result = cursorMSQL.fetchone()

            fr4Other = Fr4Other(*select_fr4_other_requi_result)

            print(fr4Other.thickness)

            # order_content_values_ = (uuid_order_content, type_design, length, width, quantity_pcb_panel, cross_board,
            #                          quantity_different_pcb_type,
            #                          is_design_by_customer, None, basicRequi.surface_treatment, basicRequi.solder_mask,
            #                          basicRequi.screen_printing, basicRequi.color_screen, basicRequi.layer,
            #                          basicRequi.pcb_thickness,
            #                          basicRequi.tg,
            #                          basicRequi.base_copper, basicRequi.external_copper, basicRequi.innerlayer, fr4Other.smallesttracewidth,
            #                          fr4Other.FinishedHoleDiameter, fr4Other.controlledimpedance, fr4Other.platedholes, fr4Other.viainpad,
            #                          fr4Other.sideplating,
            #                          fr4Other.Countersunkholes, fr4Other.Edgebeveling, fr4Other.carbonprinting, fr4Other.peelablemask, fr4Other.viaplug,
            #                          fr4Other.ipc,
            #                          fr4Other.vcut, 'NO', 'NO', fr4Other.datecode, fr4Other.datecodewhere, fr4Other.rohslogo,
            #                          fr4Other.whererohlogo, fr4Other.ullogo, fr4Other.whereullogo, fr4Other.stencil,
            #                          fr4Other.thickness, fr4Other.padreduction, fr4Other.doyouneed, fr4Other.doyougerb, order.messagecomplement)


            cursorMSQL.execute(select_doyouneed_send, numcommand)
            select_doyouneed_send_results = cursorMSQL.fetchone()

            cursorMSQL.execute(select_teamgerb, numcommand)
            select_teamgerb_results = cursorMSQL.fetchone()

            cursorMSQL.execute(select_teamstencilask, numcommand)
            select_teamstencilask_results = cursorMSQL.fetchone()

            select_doyouneed_send_results_value = get_value_asksend(select_doyouneed_send_results)
            select_teamgerb_results_value = get_value_asksend(select_teamgerb_results)
            select_teamstencilask_results_value = get_value_asksend(select_teamstencilask_results)

            # order_values_ = (
            #     order.numcommande, uuid_user[0], order.date, order.livraison, order.partnumber, order.version,
            #     order.statut,
            #     order.typecommande, '',
            #     order.qte, order.pays, order.reduction_delais, select_doyouneed_send_results_value,
            #     select_teamgerb_results_value, select_teamstencilask_results_value, '', order.valeur_unitprice,
            #     order.valeur_totalpcbprice, order.valeur_totalpcbpriceaftercost, order.valeur_shippingcost,
            #     order.valeur_prixstencil, order.producttime)
            # cursorPG.execute(insert_order, order_values_)

        except ValueError:
            logging.error(order.refmembre + " corresponding to " + str(uuid_user))


if __name__ == '__main__':
    cursorMSQL = cnx.cursor()
    cursorPG = conn.cursor()

    # MySQL
    getOrders()

    # PostgreSQL
    setOrders()

    cnx.close()
    conn.close()
