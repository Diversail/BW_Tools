import traceback
import xml.etree.ElementTree as etree

from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QKeySequence
from PyQt5.QtWidgets import (QWidget, QListWidget, QListWidgetItem,
                            QMdiSubWindow, QVBoxLayout, QPushButton, QTextEdit, QAction, QShortcut)
from PyQt5.QtCore import QSize, pyqtSignal, Qt

soldier_display = ["SEATDISPLAY_SOLDER_HEADONLY","SEATDISPLAY_SOLDER_INVISIBLE","SEATDISPLAY_SOLDER_TOSHOULDERS",
    "SEATDISPLAY_SOLDER_STANDING","SEATDISPLAY_SOLDER_SITTING"]

flag_data1 = {
    "24":"SearchLight",
    "70":"Solar_Fighter",
    "80":"Strato_Xyl",
    "82":"Und_Gunship/Strato_WF",
    "86":"Fighter",
    "88":"Gunship_Und",
    "90":"Anti_Air_V",
    "98":"Gunship_X/TT",
    "114":"Gunship_WF",
    "118":"Xyl_Batt/TT_Fighter",
    "120":"Tank_1shot",
    "122":"WF_Anti",
    "126":"Tank_2shot",
    "216":"Machine_Gunner",
    "248":"Machine_Nest",
    "344":"Xyl_Bunker",
    "352":"Bazooka/Und_Anti_Air",
    "448":"Flame/self_Anti_Air",
    "480":"Assault/Grunt/Anti_Air",
    "592":"WF_Arti",
    "624":"X_Arti",
    "992":"Gernade",
    "4160":"Bomber"
    }

display_string = {
    "0":"-",
    "-1":"None",
    "72":"FIGHTER",
    "73":"TRANSPORT COPTER",
    "74":"GUNSHIP",
    "75":"SPY BALLOON",
    "76":"BOMBER",
    "77":"STRATO DESTROYER",
    "78":"RADAR ARRAY",
    "79":"AMMO DUMP",
    "80":"LISTENING POST",
    "81":"TARGET DUMMY",
    "82":"ANTI-AIR TOWER",
    "83":"GUN TOWER",
    "84":"SENTRY",
    "85":"WATCHTOWER",
    "86":"EXTRACTION TOWER",
    "87":"MG BUNKER",
    "88":"MG TOWER",
    "89":"MG NEST",
    "90":"SEARCHLIGHTS",
    "91":"PILLBOX",
    "92":"OBELISK",
    "93":"CENOTAPH",
    "94":"CENOTAPH FORCE FIELD",
    "95":"CENOTAPH MAIN",
    "96":"HEAVY TANK",
    "97":"LIGHT TANK",
    "98":"HEAVY RECON",
    "99":"LIGHT RECON",
    "100":"ANTI-AIR",
    "101":"ARTILLERY",
    "102":"BATTLESTATION",
    "103":"TRANSPORT",
    "104":"BAZOOKA",
    "105":"RIFLE",
    "106":"FLAME",
    "107":"ASSAULT",
    "108":"MISSILE",
    "109":"MORTAR",
    "110":"Spy",
    "111":"ACK-ACK",
    "112":"ROCKET",
    "113":"MINIGUN",
    "114":"ACID GAS",
    "115":"GRENADE",
    "116":"CAPTURE POINT",
    "117":"BARREL",
    "118":"VLAD'S EFFIGY",
    "119":"MUNITIONS DUMP",
    "120":"PLASMA"}

display_string2 = {
    "0":"None",
    "-1":"None",
    "72":"Fighter",
    "73":"T-Copter",
    "74":"Gunship",
    "75":"Spy-Balloon",
    "76":"Bomber",
    "79":"Tent",
    "80":"Listening-Post",
    "81":"Target-Dummies",
    "83":"AA_Tower(Decor)",
    "87":"Bunker",
    "88":"MG_Tower",
    "89":"MG_Nest",
    "90":"Searchlight",
    "91":"PillBox",
    "92":"Obelisk",
    "93":"Cenotaph",
    "96":"Heavy_Tank",
    "97":"Light_Tank",
    "98":"HRecon",
    "99":"LRecon",
    "100":"Anti-Air-Vehicle",
    "101":"Artillery",
    "102":"Battlestation",
    "103":"APC",
    "104":"Bazooka",
    "105":"Grunt",
    "106":"Vet_Flame",
    "107":"Vet_HMG",
    "108":"Vet_Anti-Air",
    "109":"Vet_Mortar",
    "110":"Spy",
    "111":"XYL_Anti-Air",
    "112":"XYL_Bazooka",
    "334":"MP_Dock",
    "363":"Cutscene_T-Copter",
    "391":"MP_HQ/Capture_Point",
    "395":"Dynamite",
    "401":"Capture_Point?",
    "401":"Capture_Point?",
    "417":"Ammo_Dump",
    "420":"AA_Tower",
    "439":"Gun_Turret",
    "440":"HQ",
    "444":"RPG_Tower",
    "446":"Missile_Battery",
    "446":"",
    "573":"Vet_Bazooka",
    "574":"Grunt",
    "575":"Vet_Flame",
    "576":"Vet_HMG",
    "577":"Vet_Anti-Air",
    "578":"Vet_Grenade",
    "581":"XYL_Vet_Grenade",
    "594":"Light_Tank",
    "594":"Light_Tank",
    "596":"Anti-Air_Vehicle",
    "597":"Artillery",
    "610":"T-Copter",
    "611":"Gunship",
    "613":"Bomber",
    "624":"Battleship",
    "625":"Frigate",
    "627":"Submarine",
    "628":"Dreadnaught",
    "637":"MG_Tower",
    "638":"MG_Nest",
    "637":"MG_Tower"}


flag_data2 = {
    "88":"(2)Secondary_BS",
    "96":"(2)TT_Bomber",
    "98":"(2)TT/XY_Gunship/Sub",
    "114":"(2)WF/SE_Gunship",
    "120":"(2)Tank_1shell",
    "126":"(2)Heavy_Tank",
    "216":"(2)Machine_Gunner",
    "240":"(2)Artillery",
    "248":"(2)Gun_Turret",
    "254":"(2)TT_BS",
    "472":"(2)RPG_Tower",
    "480":"(2)Anti_Air/Gernade/S_Bazooka",
    "344":"(2)Neutral_RPG_Tower",
    "352":"(2)Bazooka",
    "608":"(2)Strato_Destroyer",
    "4120":"(2)Searchlight",
    "4160":"(2)AI_Bomber",
    "4192":"(2)Bomber",
    "8280":"(2)XY_Gun_Turret",
    "8408":"(2)Grunts/Air_Transport",
    "8414":"(2)Sub_Machine_Gun",
    "8440":"(2)MG_Tower/MG_Nest",
    "8446":"(2)TT_Anti_Air_Tower",
    "8640":"(2)Flame",
    "8672":"(2)Grunts/Assault",
    "25056":"(2)S_HMG",
    "33216":"(2)S_Anti_Air",
    "41440":"(2)S_Grunt",
    "266490":"(2)SE_Battleship",
    "28794":"(2)SEA_Gunner",
    "28922":"(2)Anti_Air_Tower",
    "32838":"(2)UE_Fighter",
    "36950":"(2)WF_Fighter",
    "32854":"(2)TT/AI_Fighter",
    "32858":"(2)XY_Anti_Air_Vehicle",
    "32890":"(2)TT_Anti_Air_Vehicle",
    "36986":"(2)SE_Anti_Air_Vehicle",
    "397562":"(2)AI_Battleship",
    "41208":"(2)SE_Recon",
    "119496":"(2)XY_Depth_Charge",
    "119528":"(2)Depth_Charge",
    "131326":"(2)XY_Battlestation"
    }
test_data = {}
test_data2 = [] #
target_data_o = {
    "3":"(U)HMG/Infrantry",
    "64":"(U)S_Bazooka",
    "67":"Super_Ground_Vehicles/(2)Ships",
    "128":"(U)Searchlight/Air_Vehicles",
    "131":"Air_Vehicles",
    "259":"Infrantry",
    "267":"General_Purpose",
    "323":"Ground_Vehicles",
    "387":"(U)HMG/General_Purpose",
    "1155":"Super_Air_Vehicles",
    "4194819":"(U)Gernade",
    "2147483715":"(U)UW_Air_Vehicles"
    }

target_data2 = {
    "256":"(2)Player_Flame/HMG",
    "320":"(2)Shelled_Vehicle",
    "451":"(2)(U)Machine_Guns"
    }
    

dam_list1 = ["DAMAGE_SMALLBULLET","DAMAGE_LARGEBULLET", "DAMAGE_ARMOURPIERCING",
            "DAMAGE_IMPACT","DAMAGE_EXPLOSIVE","DAMAGE_FIRE","DAMAGE_CRUSHING",
            "DAMAGE_PRECALCULATED","DAMAGE_HEALING","DAMAGE_REPAIR","DAMAGE_BIGBOMB",
            "DAMAGE_CUSTOM_1","DAMAGE_CUSTOM_2","DAMAGE_NO_DAMAGE"]

dam_list2 = ["DAMAGE_SHIP_0","DAMAGE_SHIP_1","DAMAGE_SHIP_2","DAMAGE_SHIP_3","DAMAGE_GENERIC_0","DAMAGE_ANTIAIR",
            "DAMAGE_GENERIC_1","DAMAGE_GENERIC_2","DAMAGE_GENERIC_3","DAMAGE_GENERIC_4","DAMAGE_GENERIC_5",
            "DAMAGE_GENERIC_6","DAMAGE_GENERIC_7","DAMAGE_GENERIC_8","DAMAGE_GENERIC_9"]
bullet_flags_o = {
    "0":"HMG/Machine_Nest",
    "4":"Bazooka/Tank/UN_Anti_Air",
    "32":"Flame/Searchlight",
    "140":"Bomber",
    "206":"WF/UN_GS/(2)TT/SE_GS",
    "512":"Grunt",
    "718":"Gunship",
    "907":"Anti_Air_Vehicle",
    "971":"Fighter/(2)AI_Bomber",
    "987":"Anti_Air_Vet",
    "4744":"Gernade/Artillery"
    }

bullet_flags2 = {
    "134":"(2)RPG_Tower",
    "260":"(2)XY_BS_RPG/H_Tank/SE_H_Tank/L_Tank",
    "268":"(2)TT_LTank_Cannon",
    "396":"(2)Strato_Bombs/B_Ship_RPG",
    "648":"(2)AA_Tower/B_Ship_AA",
    "772":"(2)WF_Heavy_Tank/Bunker_Shell",
    "1540":"(2)TT_Heavy_Tank",
    "4864":"(2)BS_Cannon",
    "5000":"(2)SE_Artillery",
    "5002":"(2)B_Ship_Cannon",
    "262540":"(2)Bomber"
    }
    
Allegiance_List = []

def catch_exception(func):
    def handle(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
            #raise
    return handle



class BWEntityEntry(QListWidgetItem):
    def __init__(self, xml_ref, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.xml_ref = xml_ref
    def choose_entity(self, entityid):
        self.current_entity = entityid


class BWEntityListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_entity = None

    def select_item(self, pos):
        #item = self.item(pos)
        self.setCurrentRow(pos)


class XMLTextEdit(QTextEdit):
    #mouse_clicked = pyqtSignal(QMouseEvent)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        """self.goto_id_action = QAction("Go To ID", self)
        self.goto_shortcut = QKeySequence(Qt.CTRL+Qt.Key_G)
        self.goto_id_action.setShortcut(self.goto_shortcut)
        self.goto_id_action.setShortcutContext(Qt.WidgetShortcut)"""

        #self.context_menu.exec(event.globalPos())
        #self.context_menu.destroy()


class ActionWithOwner(QAction):
    triggered_owner = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        self.action_owner = kwargs["action_owner"]
        del kwargs["action_owner"]

        super().__init__(*args, **kwargs)

        self.triggered.connect(self.triggered_with_owner)

    def triggered_with_owner(self):
        self.triggered_owner.emit(self.action_owner)





class BWEntityXMLEditor(QMdiSubWindow):
    triggered = pyqtSignal(object)
    closing = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        if "windowtype" in kwargs:
            self.windowname = kwargs["windowtype"]
            del kwargs["windowtype"]
        else:
            self.windowname = "XML Object"

        super().__init__(*args, **kwargs)

        self.resize(900, 500)
        self.setMinimumSize(QSize(300, 300))

        self.centralwidget = QWidget(self)
        self.setWidget(self.centralwidget)
        self.entity = None
        self.setWindowIcon(QIcon("icon.ico"));

        font = QFont()
        font.setFamily("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(10)


        self.dummywidget = QWidget(self)
        self.dummywidget.setMaximumSize(0,0)

        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.addWidget(self.dummywidget)


        self.goto_id_action = ActionWithOwner("Go To ID", self, action_owner=self)

        self.addAction(self.goto_id_action)

        self.goto_shortcut = QKeySequence(Qt.CTRL+Qt.Key_G)


        self.goto_id_action.setShortcut(self.goto_shortcut)
        #self.goto_id_action.setShortcutContext(Qt.WidgetShortcut)
        self.goto_id_action.setAutoRepeat(False)

        self.goto_id_action.triggered_owner.connect(self.open_new_window)

        self.textbox_xml = XMLTextEdit(self.centralwidget)
        self.button_xml_savetext = QPushButton(self.centralwidget)
        self.button_xml_savetext.setText("Save XML")
        self.button_xml_savetext.setMaximumWidth(400)
        self.textbox_xml.setLineWrapMode(QTextEdit.NoWrap)
        self.textbox_xml.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textbox_xml.customContextMenuRequested.connect(self.my_context_menu)

        metrics = QFontMetrics(font)
        self.textbox_xml.setTabStopWidth(4 * metrics.width(' '))
        self.textbox_xml.setFont(font)

        self.verticalLayout.addWidget(self.textbox_xml)
        self.verticalLayout.addWidget(self.button_xml_savetext)
        self.setWindowTitle(self.windowname)

    def set_content(self, xmlnode):
        try:
            self.textbox_xml.setText(etree.tostring(xmlnode, encoding="unicode"))
            self.entity = xmlnode.get("id")
        except:
            traceback.print_exc()

    def open_new_window(self, owner):
        #print("It was pressed!", owner)
        #print("selected:", owner.textbox_xml.textCursor().selectedText())

        self.triggered.emit(self)

    def my_context_menu(self, position):
        try:
            #print("Triggered!")
            #print(event.x(), event.y())
            #print(args)
            context_menu = self.textbox_xml.createStandardContextMenu()
            context_menu.addAction(self.goto_id_action)
            context_menu.exec(self.mapToGlobal(position))
            context_menu.destroy()
            del context_menu
            #self.context_menu.exec(event.globalPos())
            #return super().contextMenuEvent(event)
        except:
            traceback.print_exc()

    def get_content(self):
        try:
            content = self.textbox_xml.toPlainText()
            xmlnode = etree.fromstring(content)

            return xmlnode
        except:
            traceback.print_exc()

    def set_title(self, objectname):
        self.setWindowTitle("{0} - {1}".format(self.windowname, objectname))

    def reset(self):
        pass
