import logging
import re
import uuid

import mysql
import psycopg2.errors

from connection import cnx, conn

logging.basicConfig(filename='orderMigrationIms.log', level=logging.INFO,
                    format='%(levelname)s - %(message)s')

orders = []
informations = []


def get_value_asksend(t):
    if isinstance(t, tuple) and len(t) == 1:
        return "DONE"
    else:
        return 'NONE'


class Fr4Dimension:
    def __init__(self, id, numcommande, panel, unit, unit_length, unit_width, paneltype, typeallpcb, varioostype,
                 panel_lenght_allpcb, panel_width_allpcb, allpcbxout_allpcb, panel_allpcb,
                 panel_varioos_lenght, panel_varioos_width, differentpcb_type, allpcbxout_varioos,
                 panelpopup_unit_X, panelpopup_unit_Y, panelpopup_nbpcb_X, panelpopup_nbpcb_Y,
                 panelpopup_border_top, panelpopup_border_bottom, panelpopup_border_right,
                 panelpopup_border_left, popup_panel_separationX, popup_panel_separationY,
                 panelpopup_spacing_X, panelpopup_spacing_Y, allpcbxout_popup, panel_popup_X, panel_popup_Y,
                 panel_popup_nbPCB):
        self.id = id
        self.numcommande = numcommande
        self.panel = self.treatmentPanel(numcommande, panel)
        self.unit = self.treatmentUnit(numcommande, unit)
        self.unit_length = self.treatmentUnitLength(numcommande, unit_length)
        self.unit_width = self.treatmentUnitWidth(numcommande, unit_width)
        self.paneltype = self.treatmentPaneltype(numcommande, paneltype)
        self.typeallpcb = self.treatmentTypeallpcb(numcommande, typeallpcb)
        self.varioostype = self.treatmentVarioostype(numcommande, varioostype)
        self.panel_lenght_allpcb = self.treatmentPanelLenghtAllpcb(numcommande, panel_lenght_allpcb)
        self.panel_width_allpcb = self.treatmentPanelWidthAllpcb(numcommande, panel_width_allpcb)
        self.allpcbxout_allpcb = self.treatmentAllpcbxoutAllpcb(numcommande, allpcbxout_allpcb)
        self.panel_allpcb = self.treatmentPanelAllpcb(numcommande, panel_allpcb)
        self.panel_varioos_lenght = self.treatmentPanelVarioosLenght(numcommande, panel_varioos_lenght)
        self.panel_varioos_width = self.treatmentPanelVarioosWidth(numcommande, panel_varioos_width)
        self.differentpcb_type = self.treatmentDifferentpcbType(numcommande, differentpcb_type)
        self.allpcbxout_varioos = self.treatmentAllpcbxoutVarioos(numcommande, allpcbxout_varioos)
        self.panelpopup_unit_X = self.treatmentPanelpopupUnitX(numcommande, panelpopup_unit_X)
        self.panelpopup_unit_Y = self.treatmentPanelpopupUnitY(numcommande, panelpopup_unit_Y)
        self.panelpopup_nbpcb_X = self.treatmentPanelpopupNbpcbX(numcommande, panelpopup_nbpcb_X)
        self.panelpopup_nbpcb_Y = self.treatmentPanelpopupNbpcbY(numcommande, panelpopup_nbpcb_Y)
        self.panelpopup_border_top = self.treatmentPanelpopupBorderTop(numcommande, panelpopup_border_top)
        self.panelpopup_border_bottom = self.treatmentPanelpopupBorderBottom(numcommande, panelpopup_border_bottom)
        self.panelpopup_border_right = self.treatmentPanelpopupBorderRight(numcommande, panelpopup_border_right)
        self.panelpopup_border_left = self.treatmentPanelpopupBorderLeft(numcommande, panelpopup_border_left)
        self.popup_panel_separationX = self.treatmentPopupPanelSeparationX(numcommande, popup_panel_separationX)
        self.popup_panel_separationY = self.treatmentPopupPanelSeparationY(numcommande, popup_panel_separationY)
        self.panelpopup_spacing_X = self.treatmentPanelpopupSpacingX(numcommande, panelpopup_spacing_X)
        self.panelpopup_spacing_Y = self.treatmentPanelpopupSpacingY(numcommande, panelpopup_spacing_Y)
        self.allpcbxout_popup = self.treatmentAllpcbxoutPopup(numcommande, allpcbxout_popup)
        self.panel_popup_X = self.treatmentPanelPopupX(numcommande, panel_popup_X)
        self.panel_popup_Y = self.treatmentPanelPopupY(numcommande, panel_popup_Y)
        self.panel_popup_nbPCB = self.treatmentPanelPopupNbPcb(numcommande, panel_popup_nbPCB)

    def treatmentPanel(self, numcommande, panel):
        return panel

    def treatmentUnit(self, numcommande, unit):
        return unit

    def treatmentUnitLength(self, numcommande, unit_length):
        return unit_length

    def treatmentUnitWidth(self, numcommande, unit_width):
        return unit_width

    def treatmentPaneltype(self, numcommande, paneltype):
        match paneltype:
            case "unit":
                return "UNIT"
            case "panel":
                return "MULTI"
            case "varioos":
                return "VARIOUS"
            case "VariousPCB":
                return "VARIOUS"
            case "AllPCBsidentical":
                return "MULTI"
            case _:
                raise ValueError("[treatmentPaneltype] - " + str(numcommande) + " value : " + str(paneltype))

    def treatmentTypeallpcb(self, numcommande, typeallpcb):
        match typeallpcb:
            case "advanced_design":
                return "YES"
            case "basicpanel":
                return "NO"
            case _:
                return None

    def treatmentVarioostype(self, numcommande, varioostype):
        match varioostype:
            case "paneldesigncustomer":
                return "YES"
            case "paneldesignmadeby":
                return "NO"
            case 1:
                return "YES"
            case _:
                return None

    def treatmentPanelLenghtAllpcb(self, numcommande, panel_lenght_allpcb):
        return panel_lenght_allpcb

    def treatmentPanelWidthAllpcb(self, numcommande, panel_width_allpcb):
        return panel_width_allpcb

    def treatmentAllpcbxoutAllpcb(self, numcommande, allpcbxout_allpcb):
        match allpcbxout_allpcb:
            case "Yes":
                return "YES"
            case "No":
                return "NO"
            case "":
                return "NO"
            case _:
                raise ValueError(
                    "[treatmentAllpcbxoutAllpcb] - " + str(numcommande) + " value : " + str(allpcbxout_allpcb))

    def treatmentPanelAllpcb(self, numcommande, panel_allpcb):
        return panel_allpcb

    def treatmentPanelVarioosLenght(self, numcommande, panel_varioos_lenght):
        return panel_varioos_lenght

    def treatmentPanelVarioosWidth(self, numcommande, panel_varioos_width):
        return panel_varioos_width

    def treatmentDifferentpcbType(self, numcommande, differentpcb_type):
        return differentpcb_type

    def treatmentAllpcbxoutVarioos(self, numcommande, allpcbxout_varioos):
        return allpcbxout_varioos

    def treatmentPanelpopupUnitX(self, numcommande, panelpopup_unit_X):
        return panelpopup_unit_X

    def treatmentPanelpopupUnitY(self, numcommande, panelpopup_unit_Y):
        return panelpopup_unit_Y

    def treatmentPanelpopupNbpcbX(self, numcommande, panelpopup_nbpcb_X):
        return panelpopup_nbpcb_X

    def treatmentPanelpopupNbpcbY(self, numcommande, panelpopup_nbpcb_Y):
        return panelpopup_nbpcb_Y

    def treatmentPanelpopupBorderTop(self, numcommande, panelpopup_border_top):
        if panelpopup_border_top == '':
            return '0'
        else:
            return panelpopup_border_top

    def treatmentPanelpopupBorderBottom(self, numcommande, panelpopup_border_bottom):
        if panelpopup_border_bottom == '':
            return '0'
        else:
            return panelpopup_border_bottom

    def treatmentPanelpopupBorderRight(self, numcommande, panelpopup_border_right):
        if panelpopup_border_right == '':
            return '0'
        else:
            return panelpopup_border_right

    def treatmentPanelpopupBorderLeft(self, numcommande, panelpopup_border_left):
        if panelpopup_border_left == '':
            return '0'
        else:
            return panelpopup_border_left

    def treatmentPopupPanelSeparationX(self, numcommande, popup_panel_separationX):
        match popup_panel_separationX:
            case "V-cut":
                return "V_CUT"
            case "Routing":
                return "ROUTING"
            case "Route + stamp holes":
                return "ROUTING_STAMP_HOLE"
            case "Routing_stamp_hole":
                return "ROUTING_STAMP_HOLE"
            case _:
                return "NO_SEPERATION"

    def treatmentPopupPanelSeparationY(self, numcommande, popup_panel_separationY):
        match popup_panel_separationY:
            case "V-cut":
                return "V_CUT"
            case "Routing":
                return "ROUTING"
            case "Route + stamp holes":
                return "ROUTING_STAMP_HOLE"
            case "Routing_stamp_hole":
                return "ROUTING_STAMP_HOLE"
            case _:
                return "NO_SEPERATION"

    def treatmentPanelpopupSpacingX(self, numcommande, panelpopup_spacing_X):
        if panelpopup_spacing_X == '':
            return '0'
        else:
            return panelpopup_spacing_X

    def treatmentPanelpopupSpacingY(self, numcommande, panelpopup_spacing_Y):
        if panelpopup_spacing_Y == '':
            return '0'
        else:
            return panelpopup_spacing_Y

    def treatmentAllpcbxoutPopup(self, numcommande, allpcbxout_popup):
        return allpcbxout_popup

    def treatmentPanelPopupX(self, numcommande, panel_popup_X):
        return panel_popup_X

    def treatmentPanelPopupY(self, numcommande, panel_popup_Y):
        return panel_popup_Y

    def treatmentPanelPopupNbPcb(self, numcommande, panel_popup_nbPCB):
        return panel_popup_nbPCB


class Fr4Other:
    def __init__(self, id, numcommande, stencilmodal, doyougerb, datecode, datecodewhere, rohslogo, whererohlogo,
                 ullogo, whereullogo, stencil, thickness, padreduction):
        self.id = id
        self.numcommande = self.treatmentNumcommande(numcommande, numcommande)
        self.doyouneed = self.treatmentDoyouneed(stencilmodal, numcommande)
        self.doyougerb = self.treatmentDoyougerb(doyougerb, numcommande)
        self.datecode = self.treatmentDatecode(datecode, numcommande)
        self.datecodewhere = self.treatmentDatecodewhere(datecodewhere, datecode, numcommande)
        self.rohslogo = self.treatmentRohslogo(rohslogo, numcommande)
        self.whererohlogo = self.treatmentWhererohlogo(whererohlogo, rohslogo, numcommande)
        self.ullogo = self.treatmentUllogo(ullogo, numcommande)
        self.whereullogo = self.treatmentWhereullogo(whereullogo, ullogo, numcommande)
        self.smallesttracewidth = None
        self.FinishedHoleDiameter = None
        self.controlledimpedance = None
        self.viainpad = None
        self.platedholes = None
        self.sideplating = None
        self.vcut = None
        self.countersunkholes = None
        self.edgebeveling = None
        self.carbonprinting = None
        self.peelablemask = None
        self.viaplug = None
        self.ipc = None
        self.stencil = self.treatmentStencil(stencil, numcommande)
        self.thickness = self.treatmentThickneess(thickness, numcommande)
        self.padreduction = self.treatmentPadreduction(padreduction, numcommande)

    def treatmentThickneess(self, thickness, numcommande):
        return thickness.replace("µm", "")

    def treatmentNumcommande(self, numcommande, tes):
        return numcommande

    def treatmentDoyouneed(self, doyouneed, numcommande):
        match doyouneed:
            case "yes":
                return "YES"
            case "Yes":
                return "YES"
            case "":
                return "NO"
            case _:
                raise ValueError("[treatmentDoyouneed] - " + str(numcommande) + " value : " + str(doyouneed))

    def treatmentDoyougerb(self, doyougerb, numcommande):
        match doyougerb:
            case "yes":
                return "YES"
            case "Yes":
                return "YES"
            case "":
                return "NO"
            case _:
                raise ValueError("[treatmentDoyougerb] - " + str(numcommande) + " value : " + str(doyougerb))

    def treatmentDatecode(self, datecode, numcommande):
        match datecode:
            case "Solder mask":
                return "SOLDER_MASK"
            case "Solder mark":
                return "SOLDER_MASK"
            case "Screen Printing":
                return "SCREEN_PRINTING"
            case "Copper":
                return "COPPER"
            case "No":
                return "NO"
            case _:
                raise ValueError("[treatmentDatecode] - " + str(numcommande) + " value : " + str(datecode))

    def treatmentDatecodewhere(self, datecodewhere, datecode, numcommande):
        if datecode == "No":
            return None

        match datecodewhere:
            case "Top":
                return "TOP"
            case "Bottom":
                return "BOTTOM"
            case _:
                raise ValueError("[treatmentDatecodewhere] - " + str(numcommande) + " value : " + str(datecodewhere))

    def treatmentRohslogo(self, rohslogo, numcommande):
        match rohslogo:
            case "Solder mask":
                return "SOLDER_MASK"
            case "Screen Printing":
                return "SCREEN_PRINTING"
            case "Copper":
                return "COPPER"
            case "No":
                return "NO"
            case _:
                raise ValueError("[treatmentDatecode] - " + str(numcommande) + " value : " + str(rohslogo))

    def treatmentWhererohlogo(self, whererohlogo, rohslogo, numcommande):
        if rohslogo == "No":
            return None

        match whererohlogo:
            case "Top":
                return "TOP"
            case "Bottom":
                return "BOTTOM"
            case _:
                raise ValueError("[treatmentDatecodewhere] - " + str(numcommande) + " value : " + str(whererohlogo))

    def treatmentUllogo(self, ullogo, numcommande):
        match ullogo:
            case "Solder mask":
                return "SOLDER_MASK"
            case "Screen Printing":
                return "SCREEN_PRINTING"
            case "Copper":
                return "COPPER"
            case "No":
                return "NO"
            case _:
                raise ValueError("[treatmentDatecode] - " + str(numcommande) + " value : " + str(ullogo))

    def treatmentWhereullogo(self, whereullogo, ullogo, numcommande):
        if ullogo == "No":
            return None

        match whereullogo:
            case "Top":
                return "TOP"
            case "Bottom":
                return "BOTTOM"
            case _:
                raise ValueError("[treatmentDatecodewhere] - " + str(numcommande) + " value : " + str(whereullogo))

    def treatmentStencil(self, stencil, numcommande):
        match stencil:
            case "No":
                return "NO"
            case "Bottom":
                return "BOTTOM"
            case "Top":
                return "TOP"
            case "TopETBottom":
                return "TOP_AND_BOTTOM"
            case _:
                raise ValueError("[treatmentStencil] - " + str(numcommande) + " value : " + str(stencil))

    def treatmentPadreduction(self, padreduction, numcommande):
        match padreduction:
            case "yes":
                return "YES"
            case "no":
                return "NO"
            case _:
                raise ValueError("[treatmentPadreduction] - " + str(numcommande) + " value : " + str(padreduction))


class Fiduciales:
    def __init__(self, id, shape, a_champ_x, a_champ_y, b_champ_x, b_champ_y, c_champ_x, c_champ_y, d_champ_x,
                 d_champ_y, numcommande):
        self.id = id
        self.numcommande = numcommande
        self.shape = self.treatmentShape(shape, numcommande)
        self.a_champ_x = a_champ_x
        self.a_champ_y = a_champ_y
        self.b_champ_x = b_champ_x
        self.b_champ_y = b_champ_y
        self.c_champ_x = c_champ_x
        self.c_champ_y = c_champ_y
        self.d_champ_x = d_champ_x
        self.d_champ_y = d_champ_y

    def treatmentShape(self, shape, numcommande):
        match shape:
            case "square_rectangle":
                return "SQUARE_RECTANGLE"
            case "circle_oval":
                return "CIRCLE_OVAL"
            case _:
                raise ValueError("[treatmentShape] - " + str(numcommande) + " value : " + str(shape))


class BasicRequi:
    def __init__(self, id, numcommande, layer, pcb_thickness, tg, surface_treatment, screen_printing,
                 color_screen, base_copper, solder_mask):
        self.id = id
        self.numcommande = numcommande
        self.layer = self.treatmentLayer(layer, numcommande)
        self.pcb_thickness = self.treatmentPcbThickness(pcb_thickness, numcommande)
        self.tg = self.treatmentTg(tg, numcommande)
        self.surface_treatment = self.treatmentSurfaceTreatment(surface_treatment, numcommande)
        self.solder_mask = self.treatmentSolderMask(solder_mask, numcommande)
        self.screen_printing = self.treatmentScreenPrinting(screen_printing, numcommande)
        self.color_screen = self.treatmentColorScreen(color_screen, numcommande)
        self.base_copper = self.treatmentBaseCopper(base_copper, numcommande)

    def treatmentLayer(self, layer, numcommande):
        match layer:
            case 0:
                return "0"
            case 1:
                return "1"
            case 2:
                return "2"
            case 4:
                return "4"
            case 6:
                return "6"
            case 8:
                return "8"
            case 10:
                return "10"
            case 12:
                return "12"
            case 14:
                return "14"
            case _:
                raise ValueError("[treatmentLayer] - " + str(numcommande) + " value : " + str(layer))

    def treatmentPcbThickness(self, pcb_thickness, numcommande):
        match pcb_thickness:
            case "0.8":
                return "0.8"
            case "1.0":
                return "1.0"
            case "1.2":
                return "1.2"
            case "1.4":
                return "1.4"
            case "1.6":
                return "1.6"
            case "1.8":
                return "1.8"
            case "2.0":
                return "2.0"
            case "2.4":
                return "2.4"
            case _:
                raise ValueError("[treatmentPcbThickness] - " + str(numcommande) + " value : " + str(pcb_thickness))

    def treatmentTg(self, tg, numcommande):
        match tg:
            case "1.0 W/M.K":
                return "1"
            case "2.0 W/M.K":
                return "2"
            case "3.0 W/M.K":
                return "3"
            case "4.0 W/M.K":
                return "4"
            case _:
                raise ValueError("[treatmentTg] - " + str(numcommande) + " value : " + str(tg))

    def treatmentSurfaceTreatment(self, surface_treatment, numcommande):
        match surface_treatment:
            case "HALLeadFree":
                return "HAL_LEAD_FREE"
            case "ENIG":
                return "ENIG"
            case "ImmSilver":
                return "IMMER_SILVER"
            case "OSP":
                return "OSP"
            case "ImmTin":
                return "IMMER_TIN"
            case "HALwithlead":
                return "HAL_WITH_LEAD"
            case "NI-Pa-Gold":
                return "NI_PA_GOLD"
            case "enepig":
                return "ENEPIG"
            case "nosurfacetreatment":
                return "NO_TREATMENT"
            case _:
                raise ValueError(
                    "[treatmentSurfaceTreatment] - " + str(numcommande) + " value : " + str(surface_treatment))

    def treatmentSolderMask(self, solderMask, numcommande):
        match solderMask:
            case "Green":
                return "GREEN"
            case "Blue":
                return "BLUE"
            case "Red":
                return "RED"
            case "White":
                return "WHITE"
            case "None":
                return "NONE"
            case "Black":
                return "HAL_WITH_LEAD"
            case "Black matte":
                return "BLACK_MAT"
            case "Black shinny":
                return "BLACK_SHINNY"
            case "Green Mat":
                return "GREEN_MAT"
            case _:
                raise ValueError("[treatmentSolderMask] - " + str(numcommande) + " value : " + str(solderMask))

    def treatmentScreenPrinting(self, screePrinting, numcommande):
        match screePrinting:
            case "No":
                return "NO"
            case "Top":
                return "TOP"
            case "Bottom":
                return "BOTTOM"
            case "Top & Bottom":
                return "TOP_AND_BOTTOM"
            case _:
                raise ValueError("[treatmentScreenPrinting] - " + str(numcommande) + " value : " + str(screePrinting))

    def treatmentColorScreen(self, colorScreen, numcommande):
        match colorScreen:
            case "Black":
                return "BLACK"
            case "White":
                return "WHITE"
            case "Red":
                return "RED"
            case "Yellow":
                return "YELLOW"
            case _:
                return None

    def treatmentExternalCopper(self, externalCopper, numcommande):
        match externalCopper:
            case "17/35":
                return "17/35"
            case "70/95":
                return "70/95"
            case "70/105":
                return "70/105"
            case "35/70":
                return "35/70"
            case "105/140":
                return "105/140"
            case "35/55":
                return "35/55"
            case "105/125":
                return "105/125"
            case _:
                return None

    def treatmentBaseCopper(self, baseCopper, numcommande):
        match baseCopper:
            case "35":
                return "35"
            case "70":
                return "70"
            case "105":
                return "105"
            case _:
                return None

    def treatmentInnerLayer(self, innerLayer, numcommande):
        match innerLayer:
            case "18":
                return "18"
            case "35":
                return "35"
            case "70":
                return "70"
            case "105":
                return "105"
            case "140":
                return "140"
            case _:
                return None

    def treatmentBuildup(self, buildup, numcommande):
        match buildup:
            case "Standard":
                return "NO"
            case "Follow spec provided":
                return "YES"
            case _:
                return None

    def treatmentSequence(self, sequence, numcommande):
        match sequence:
            case "twosequence":
                return 2
            case "onesequence":
                return 1
            case _:
                raise ValueError("[treatmentSequence] - " + str(numcommande) + " value : " + str(sequence))


class Order:
    def __init__(self, typedelacommande, typecommande, refmembre, numcommande, partnumber, version, system, qte, pays,
                 livraison, reduction_delais, valeur_unitprice, valeur_nbofpanel, valeur_totalpcbprice,
                 valeur_shippingcost, valeur_totalpcbpriceaftercost, valeur_prixstencil, valeur_reception_date,
                 valeur_prod_date, la_langue, ladevice, producttime, temps_reduction_par_defaut, currency, documents,
                 date, statut, pao, messagecomplement, numerodelacommande):
        self.typedelacommande = typedelacommande
        self.typecommande = self.treatmentTypeCommande(typecommande)
        self.refmembre = refmembre
        self.numcommande = numcommande
        self.partnumber = partnumber
        self.version = version
        self.system = system
        self.qte = qte
        self.pays = pays
        self.livraison = livraison
        self.reduction_delais = self.treatmentReductionDelais(numcommande, reduction_delais)
        self.valeur_unitprice = valeur_unitprice
        self.valeur_nbofpanel = valeur_nbofpanel
        self.valeur_totalpcbprice = valeur_totalpcbprice
        self.valeur_shippingcost = valeur_shippingcost
        self.valeur_totalpcbpriceaftercost = valeur_totalpcbpriceaftercost
        self.valeur_prixstencil = valeur_prixstencil
        self.valeur_reception_date = self.treatmentValeurDate(valeur_reception_date)
        self.valeur_prod_date = self.treatmentProdDate(valeur_prod_date)
        self.la_langue = la_langue
        self.ladevice = ladevice
        self.producttime = self.treatmentProductTime(numcommande, producttime)
        self.temps_reduction_par_defaut = temps_reduction_par_defaut
        self.currency = self.treatmentCurrency(numcommande, currency)
        self.documents = documents
        self.date = date
        self.statut = self.treatmentStatut(numcommande, statut)
        self.pao = pao
        self.messagecomplement = messagecomplement
        self.numerodelacommande = numerodelacommande

    def treatmentTypeCommande(self, numcommande):
        return 'IMS'

    def treatmentReductionDelais(self, numcommande, reduction_delais):
        if reduction_delais == "no":
            return 0

        if isinstance(int(reduction_delais), int):
            return reduction_delais

        raise ValueError("[treatmentReductionDelais] - " + str(numcommande) + " value : " + str(reduction_delais))

    def treatmentStatut(self, numcommande, statut):
        match statut:
            case 0:
                return "WAITING_PAYMENT"
            case 1:
                return "ENGINEERING_QUESTIONS"
            case 2:
                return "PRODUCTION"
            case 3:
                return "GOODS_FINISHED"
            case 4:
                return "WAITING_FOR_PAYMENT"
            case _:
                raise ValueError("[treatmentStatut] - " + str(numcommande) + " value : " + str(statut))

    def treatmentProductTime(self, numcommande, producttime):
        chiffres = re.findall(r'\d+', producttime)

        if chiffres:
            return int(chiffres[0])
        return -1

    def treatmentValeurDate(self, valeur_prod_date):
        if valeur_prod_date == '' or valeur_prod_date == 'n/a':
            return None
        return valeur_prod_date

    def treatmentCurrency(self, numcommande, currency):
        match currency:
            case "usd":
                return "USD"
            case "euro":
                return "EUR"
            case _:
                raise ValueError("[treatmentCurrency] - " + str(numcommande) + " value : " + str(currency))

    def treatmentProdDate(self, valeur_prod_date):
        if 'n/a' in valeur_prod_date:
            return None
        return valeur_prod_date


def getOrders():
    query_members = "SELECT typedelacommande, typecommande, refmembre, numcommande, partnumber, version, \"system\", " \
                    "qte, pays, livraison, reduction_delais, valeur_unitprice, valeur_nbofpanel, valeur_totalpcbprice, " \
                    "valeur_shippingcost, valeur_totalpcbpriceaftercost, valeur_prixstencil, valeur_reception_date," \
                    " valeur_prod_date, la_langue, ladevise, producttime, temps_reduction_par_defaut, currency, " \
                    "documents, date, statut, pao, messagecomplement, numerodelacommande " \
                    "from commande where date > '2023-05-01' and typecommande = 'SMI'"

    # "from commande where date > '2020-01-01' and typecommande = 'SMI'"

    cursorMSQL.execute(query_members)

    results = cursorMSQL.fetchall()

    for row in results:
        try:
            order = Order(*row)
            orders.append(order)
        except ValueError as e:
            logging.error("[ValueError] - " + str(row[3]) + " " + str(e))


def setOrders():
    good = 0
    error = 0
    total = 1

    select_user_id = "select id from \"user\" where ref = %s;"

    insert_order = "INSERT INTO \"order\" (order_number, user_id, created_at, product_at, delivery_at, part_number, version, " \
                   "status_order, material_type," \
                   "purchased_order, quantity, shipping_destination_id, reduce_prod_time_by, paste_mask_file, approve_gerber, stencil," \
                   "order_content_id, unit_sell, sell, cost, shipping_cost, stencil_cost, production_time, reorder_number, currency) " \
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    insert_history = "INSERT INTO history (order_number, user_id, created_at, product_at, delivery_at, part_number, version, status_order," \
                     "material_type, purchased_order, tracking_number, quantity, shipping_destination_id, reduce_prod_time_by," \
                     "paste_mask_file, approve_gerber, stencil, order_content_id, unit_sell, sell, cost, shipping_cost," \
                     "stencil_cost, production_time, reorder_number, currency) " \
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    insert_order_content = "INSERT INTO order_content (id, type_design, length, width, quantity_pcb_panel, cross_board, quantity_different_pcb_type," \
                           "is_design_by_customer, custom_panel_id, surface_treatment, solder_mask," \
                           "screen_printing_position, screen_printing_color, layers, pcb_thickness, glass_transition," \
                           "copper_thickness_base, trace," \
                           "finished_hole_size, impedance_control, plated_half_holes, via_in_pad, edge_side_plating, " \
                           "counter_sink_hole, edge_beveling, carbon_printing, peelable_mask, via_pluggling, ipc_class, " \
                           "jv_cut, serial_number, approvals, date_code, date_code_position, rohs_logo, rohs_logo_position, ul_logo," \
                           " ul_logo_position, smt_stencil_position, stencil_thickness, stencil_pad_reduction, paste_mask_file, approve_gerber, additional_comment)" \
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                           "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                           "%s, %s, %s, %s); "

    insert_custom_panel = "insert into custom_panel(id, pcb_width, pcb_length, number_pcb_x, number_pcb_y, " \
                          "separation_method_x, separation_method_y, right_border, left_border, top_border, " \
                          "bottom_border, spacing_x, spacing_y, fiducial_a, fiducial_b, fiducial_c, fiducial_d, shape) " \
                          "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    select_doyouneed_send = "select doyouneed_send from asksend_doyouneed where numcommande = %s;"
    select_teamgerb = "select teamgerb from asksend_gerb where numcommande = %s;"
    select_teamstencilask = "select teamstencilask from asksend_stencil where numcommande = %s;"

    select_smi_basic_requi = "select id, numcommande, layer, pcb_thickness, thermal, surface_treatment, " \
                             "screen_printing, color_screen, base_copper, soldermaskConnect " \
                             "from smi_basic_requi where numcommande = %s;"

    select_smi_other = "select id, numcommande, stencilmodal, doyougerb, datecode, datecodewhere, rohslogo, " \
                       "whererohlogo, ullogo, whereullogo, stencil, thickness, padreduction " \
                       "from smi_other where numcommande = %s;"

    select_smi_dimension = "select id, numcommande, panel, unit, unit_length, unit_width, paneltype, typeallpcb, varioostype," \
                           "panel_lenght_allpcb, panel_width_allpcb, allpcbxout_allpcb, panel_allpcb," \
                           "panel_varioos_lenght, panel_varioos_width, differentpcb_type, allpcbxout_varioos," \
                           "panelpopup_unit_X, panelpopup_unit_Y, panelpopup_nbpcb_X, panelpopup_nbpcb_Y," \
                           "panelpopup_border_top, panelpopup_border_bottom, panelpopup_border_right," \
                           "panelpopup_border_left, popup_panel_separationX, popup_panel_separationY," \
                           "panelpopup_spacing_X, panelpopup_spacing_Y, allpcbxout_popup, panel_popup_width, panel_popup_lenght, " \
                           "panel_popup_pcb " \
                           "from smi_dimension where numcommande = %s;"

    select_fiducial = "select id, shape, a_champ_x, a_champ_y, b_champ_x, b_champ_y, c_champ_x, c_champ_y, d_champ_x, d_champ_y, numcommande from fiduciales where numcommande = %s;"

    # print("Orders: " + str(len(orders)))

    for order in orders:
        print(str(total) + "/" + str(len(orders)) + " - " + str(order.numcommande))

        try:
            uuid_order_content = str(uuid.uuid4())
            uuid_custom_panel = str(uuid.uuid4())

            ref_values_ = (order.refmembre,)
            cursorPG.execute(select_user_id, ref_values_)
            uuid_user = cursorPG.fetchone()

            if uuid_user == None:
                raise ValueError("missing user")

            numcommand = (order.numcommande,)

            cursorMSQL.execute(select_smi_basic_requi, numcommand)
            select_smi_basic_requi_result = cursorMSQL.fetchall()

            if (len(select_smi_basic_requi_result) == 0):
                raise ValueError("BasicRequi missing")
            if (len(select_smi_basic_requi_result) > 1):
                select_smi_basic_requi_result = select_smi_basic_requi_result[-1]
            if (len(select_smi_basic_requi_result) == 1):
                select_smi_basic_requi_result = select_smi_basic_requi_result[0]
            basicRequi = BasicRequi(*select_smi_basic_requi_result)

            cursorMSQL.execute(select_smi_other, numcommand)
            select_smi_other_requi_result = cursorMSQL.fetchall()

            if (len(select_smi_other_requi_result) == 0):
                raise ValueError("Fr4Other missing")
            if (len(select_smi_other_requi_result) > 1):
                select_smi_other_requi_result = select_smi_other_requi_result[-1]
            if (len(select_smi_other_requi_result) == 1):
                select_smi_other_requi_result = select_smi_other_requi_result[0]
            fr4Other = Fr4Other(*select_smi_other_requi_result)

            cursorMSQL.execute(select_smi_dimension, numcommand)
            select_smi_dimension_result = cursorMSQL.fetchall()

            if (len(select_smi_dimension_result) == 0):
                raise ValueError("Fr4Dimension missing")
            if (len(select_smi_dimension_result) > 1):
                select_smi_dimension_result = select_smi_dimension_result[-1]
            if (len(select_smi_dimension_result) == 1):
                select_smi_dimension_result = select_smi_dimension_result[0]
            fr4Dimension = Fr4Dimension(*select_smi_dimension_result)

            quantity_pcb_panel = None

            if fr4Dimension.paneltype == "MULTI":
                cursorMSQL.execute(select_fiducial, numcommand)
                fiducial = cursorMSQL.fetchall()

                if (len(fiducial) == 0):
                    raise ValueError("Fr4Dimension missing")
                if (len(fiducial) > 1):
                    fiducial = fiducial[-1]
                if (len(fiducial) == 1):
                    fiducial = fiducial[0]
                fiducialResult = Fiduciales(*fiducial)

                insert_custom_panel_values_ = (
                    uuid_custom_panel, fr4Dimension.panelpopup_unit_X, fr4Dimension.panelpopup_unit_Y,
                    fr4Dimension.panelpopup_nbpcb_X, fr4Dimension.panelpopup_nbpcb_Y,
                    fr4Dimension.popup_panel_separationX, fr4Dimension.popup_panel_separationY,
                    fr4Dimension.panelpopup_border_right, fr4Dimension.panelpopup_border_left,
                    fr4Dimension.panelpopup_border_top, fr4Dimension.panelpopup_border_bottom,
                    fr4Dimension.panelpopup_spacing_X, fr4Dimension.panelpopup_spacing_Y,
                    str(fiducialResult.a_champ_x) + ";" + str(fiducialResult.a_champ_y),
                    str(fiducialResult.b_champ_x) + ";" + str(fiducialResult.b_champ_y),
                    str(fiducialResult.c_champ_x) + ";" + str(fiducialResult.c_champ_y),
                    str(fiducialResult.d_champ_x) + ";" + str(fiducialResult.d_champ_y),
                    fiducialResult.shape)
                cursorPG.execute(insert_custom_panel, insert_custom_panel_values_)
            else:
                uuid_custom_panel = None

            dimension_length = None
            dimension_width = None
            isDesignByCustomer = None
            xout = None
            quantity_different_pcb_type = None

            if fr4Dimension.paneltype == "MULTI":
                if fr4Dimension.typeallpcb == "YES":
                    dimension_length = fr4Dimension.panel_popup_Y
                    dimension_width = fr4Dimension.panel_popup_X
                    quantity_pcb_panel = fr4Dimension.panel_popup_nbPCB
                else:
                    dimension_length = fr4Dimension.panel_lenght_allpcb
                    dimension_width = fr4Dimension.panel_width_allpcb
                    quantity_pcb_panel = fr4Dimension.panel_allpcb
                isDesignByCustomer = fr4Dimension.typeallpcb
                xout = fr4Dimension.allpcbxout_allpcb

            if fr4Dimension.paneltype == "UNIT":
                dimension_length = fr4Dimension.unit_length
                dimension_width = fr4Dimension.unit_width

            if fr4Dimension.paneltype == "VARIOUS":
                dimension_length = fr4Dimension.panel_varioos_lenght
                dimension_width = fr4Dimension.panel_varioos_width
                isDesignByCustomer = fr4Dimension.varioostype
                xout = fr4Dimension.allpcbxout_allpcb
                quantity_different_pcb_type = fr4Dimension.differentpcb_type
                quantity_pcb_panel = fr4Dimension.allpcbxout_varioos

            if dimension_length == None or dimension_width == None:
                raise ValueError("Dimension length ou dimension width erreur")

            order_content_values_ = (
                uuid_order_content, fr4Dimension.paneltype, dimension_length,
                dimension_width,
                quantity_pcb_panel, xout,
                quantity_different_pcb_type,
                isDesignByCustomer, uuid_custom_panel, basicRequi.surface_treatment, basicRequi.solder_mask,
                basicRequi.screen_printing, basicRequi.color_screen, basicRequi.layer,
                basicRequi.pcb_thickness,
                basicRequi.tg,
                basicRequi.base_copper, fr4Other.smallesttracewidth,
                fr4Other.FinishedHoleDiameter, fr4Other.controlledimpedance, fr4Other.platedholes, fr4Other.viainpad,
                fr4Other.sideplating, fr4Other.countersunkholes, fr4Other.edgebeveling, fr4Other.carbonprinting,
                fr4Other.peelablemask, fr4Other.viaplug, fr4Other.ipc, fr4Other.vcut, 'NO', 'NO', fr4Other.datecode,
                fr4Other.datecodewhere, fr4Other.rohslogo, fr4Other.whererohlogo, fr4Other.ullogo, fr4Other.whereullogo,
                fr4Other.stencil, fr4Other.thickness, fr4Other.padreduction, fr4Other.doyouneed, fr4Other.doyougerb,
                order.messagecomplement)

            cursorPG.execute(insert_order_content, order_content_values_)

            select_doyouneed_send_results_value = 'NONE'
            if fr4Other.doyouneed == 'YES':
                select_doyouneed_send_results_value = "ASK"
                cursorMSQL.execute(select_doyouneed_send, numcommand)
                select_doyouneed_send_results = cursorMSQL.fetchone()
                if get_value_asksend(select_doyouneed_send_results) == 'DONE':
                    select_doyouneed_send_results_value = 'DONE'

            select_teamgerb_results_value = 'NONE'
            if fr4Other.doyougerb == 'YES':
                select_teamgerb_results_value = "ASK"
                cursorMSQL.execute(select_teamgerb, numcommand)
                select_teamgerb_results = cursorMSQL.fetchone()
                if get_value_asksend(select_teamgerb_results) == 'DONE':
                    select_teamgerb_results_value = 'DONE'

            select_teamstencilask_results_value = 'NONE'
            if fr4Other.stencil == 'YES':
                select_teamstencilask_results_value = "ASK"
                cursorMSQL.execute(select_teamstencilask, numcommand)
                select_teamstencilask_results = cursorMSQL.fetchone()
                if get_value_asksend(select_teamstencilask_results) == 'DONE':
                    select_teamstencilask_results_value = 'DONE'

            if order.statut == "GOODS_FINISHED":
                history_values_ = (
                    order.numcommande, uuid_user[0], order.date, order.valeur_prod_date, order.valeur_reception_date,
                    order.partnumber, order.version,
                    order.statut, order.typecommande,
                    order.pao, None, order.qte, order.pays, order.reduction_delais, select_doyouneed_send_results_value,
                    select_teamgerb_results_value, select_teamstencilask_results_value, uuid_order_content,
                    str(order.valeur_unitprice),
                    str(order.valeur_totalpcbpriceaftercost), str(order.valeur_totalpcbprice),
                    str(order.valeur_shippingcost),
                    str(order.valeur_prixstencil), order.producttime, order.numerodelacommande, order.currency)
                cursorPG.execute(insert_history, history_values_)
                conn.commit()
                good += 1

            else:
                order_values_ = (
                    order.numcommande, uuid_user[0], order.date, order.valeur_prod_date, order.valeur_reception_date,
                    order.partnumber,
                    order.version,
                    order.statut, order.typecommande,
                    order.pao, order.qte, order.pays, order.reduction_delais, select_doyouneed_send_results_value,
                    select_teamgerb_results_value, select_teamstencilask_results_value, uuid_order_content,
                    str(order.valeur_unitprice),
                    str(order.valeur_totalpcbpriceaftercost), str(order.valeur_totalpcbprice),
                    str(order.valeur_shippingcost),
                    str(order.valeur_prixstencil), order.producttime, order.numerodelacommande, order.currency)

                cursorPG.execute(insert_order, order_values_)
                conn.commit()
                good += 1

        except ValueError as e:
            logging.error("[ValueError] - " + str(order.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        except TypeError as e:
            logging.error("[TypeError] - " + str(order.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        except psycopg2.errors.SyntaxError as e:
            logging.error("[StringDataRightTruncation] - " + str(order.numcommande), exc_info=False)
            conn.rollback()
            error += 1
        except psycopg2.errors.StringDataRightTruncation as e:
            logging.error("[StringDataRightTruncation] - " + str(order.numcommande) + " " + e.pgerror.replace("\n", ""))
            conn.rollback()
            error += 1
        except psycopg2.errors.InFailedSqlTransaction as e:
            logging.error("[InFailedSqlTransaction] - " + str(order.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        except mysql.connector.errors.InternalError as e:
            logging.error("[mysql-InternalError] - " + str(order.numcommande))
            conn.rollback()
            error += 1
        except psycopg2.errors.InvalidDatetimeFormat as e:
            logging.error("[InvalidDatetimeFormat] - " + str(order.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        except psycopg2.errors.UniqueViolation as e:
            logging.error("[UniqueViolation] - " + str(order.numcommande) + " " + str(e))
            conn.rollback()
            error += 1
        total += 1

    logging.info(
        "error: " + str(error) + " / " + " good: " + str(good) + " total: " + str(total))


if __name__ == '__main__':
    cursorMSQL = cnx.cursor()
    cursorPG = conn.cursor()

    # MySQL
    getOrders()

    # PostgreSQL
    setOrders()

    cnx.close()
    conn.close()
