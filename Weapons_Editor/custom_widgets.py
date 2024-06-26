import traceback
import math
import xml.etree.ElementTree as etree
from timeit import default_timer
from copy import copy
from math import sin, cos, atan2, radians
from itertools import chain

from PyQt5.QtGui import QMouseEvent, QWheelEvent, QPainter, QColor, QFont, QFontMetrics, QPolygon, QImage, QPixmap, QKeySequence
from PyQt5.QtWidgets import (QWidget, QListWidget, QListWidgetItem, QDialog, QMenu,
                            QMdiSubWindow, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QTextEdit, QAction, QShortcut)
from PyQt5.QtCore import QSize, pyqtSignal, QPoint, QRect
from PyQt5.QtCore import Qt

#weapons

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

#end of weapons

ENTITY_SIZE = 10

COLORS = {
    "cAirVehicle": QColor("yellow"),
    "cWaterVehicle": QColor(140,0,140),
    "cGroundVehicle": QColor(180, 50, 0),#QColor("brown"),
    "cTroop": QColor("blue"),
    "cMapZone": QColor("grey"),
    "cCamera": QColor("violet"),
    "cWaypoint": QColor("cyan"),
    "cSceneryCluster": QColor(90, 40, 40),
    "cBuilding": QColor(200,200,255),
    "cDestroyableObject": QColor("black"),
    "cPickupReflected": QColor(35,135,35),
    "cReflectedUnitGroup": QColor(255,255,255)
}

MAPZONECOLORS = {
    "ZONETYPE_MISSIONBOUNDARY": QColor("light green")
}
DEFAULT_ENTITY = QColor("black")
DEFAULT_MAPZONE = QColor("grey")
DEFAULT_SELECTED = QColor("red")
DEFAULT_ANGLE_MARKER = QColor("blue")

SHOW_TERRAIN_NO_TERRAIN = 0
SHOW_TERRAIN_REGULAR = 1
SHOW_TERRAIN_LIGHT = 2
SHOW_TERRAIN_FLAT = 3

def catch_exception(func):
    def handle(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
            #raise
    return handle


def rotate(corner_x, corner_y, center_x, center_y, angle):
    temp_x = corner_x-center_x
    temp_y = corner_y-center_y
    angle = radians(angle)

    rotated_x = temp_x*cos(angle) - temp_y*sin(angle)
    rotated_y = temp_x*sin(angle) + temp_y*cos(angle)
    #print(sin(radians(angle)))

    return QPoint(int(rotated_x+center_x), int(rotated_y+center_y))


class BWMapViewer(QWidget):
    mouse_clicked = pyqtSignal(QMouseEvent)
    entity_clicked = pyqtSignal(QMouseEvent, str)
    mouse_dragged = pyqtSignal(QMouseEvent)
    mouse_released = pyqtSignal(QMouseEvent)
    mouse_wheel = pyqtSignal(QWheelEvent)
    ENTITY_SIZE = ENTITY_SIZE



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._zoom_factor = 10

        self.SIZEX = 2048#1024
        self.SIZEY = 2048#1024


        self.setMinimumSize(QSize(self.SIZEX, self.SIZEY))
        self.setMaximumSize(QSize(self.SIZEX, self.SIZEY))
        self.setObjectName("bw_map_screen")


        self.point_x = 0
        self.point_y = 0
        self.polygon_cache = {}

        # This value is used for switching between several entities that overlap.
        self.next_selected_index = 0

        #self.entities = [(0,0, "abc")]
        self.entities = {}#{"abc": (0, 0)}
        self.current_entity = None
        self.selected_entities = {}
        self.visibility_toggle = {}

        self.terrain = None
        self.terrain_scaled = None
        self.terrain_buffer = QImage()

        self.p = QPainter()
        self.p2 = QPainter()
        self.show_terrain_mode = SHOW_TERRAIN_REGULAR

        self.selectionbox_start = None
        self.selectionbox_end = None

    def set_visibility(self, visibility):
        self.visibility_toggle = visibility

    def reset(self):
        del self.entities
        self.entities = {}
        self.current_entity = None

        self.point_x = self.point_y = 0

        self.next_selected_index = 0
        self._zoom_factor = 10
        del self.polygon_cache
        self.polygon_cache = {}
        self.visibility_toggle = {}

        self.SIZEX = 2048#1024
        self.SIZEY = 2048#1024

        self.setMinimumSize(QSize(self.SIZEX, self.SIZEY))
        self.setMaximumSize(QSize(self.SIZEX, self.SIZEY))

        self.terrain = None
        self.terrain_scaled = QImage()
        self.show_terrain_mode = SHOW_TERRAIN_REGULAR

    @property
    def zoom_factor(self):
        return self._zoom_factor/10.0

    def choose_entity(self, entityid):
        self.current_entity = entityid

        self.update()

    def set_show_terrain_mode(self, mode):
        if mode not in (SHOW_TERRAIN_NO_TERRAIN, SHOW_TERRAIN_REGULAR, SHOW_TERRAIN_LIGHT,SHOW_TERRAIN_FLAT):
            raise RuntimeError("No such mode:", mode)
        else:
            print("Terrain mode was", self.show_terrain_mode, "will be set to", mode)
            self.show_terrain_mode = mode

    def move_entity(self, entityid, x, y):
        # Update the position of an entity
        self.entities[entityid][0] = x
        self.entities[entityid][1] = y

    def add_entities(self, entities):
        for x, y, entityid, entitytype in entities:
            #self.entities.append((x, y, entityid))
            self.entities[entityid] = [x, y, entitytype, None]

    def remove_entity(self, entityid):
        # If the entity is selected, unselect it before deleting it.
        if self.current_entity is not None:
            if entityid == self.current_entity:
                self.current_entity = None

        del self.entities[entityid]

    def rename_entity(self, oldid, newid):
        # We do not allow renaming an entity to a different name that already exists
        assert newid == oldid or newid not in self.entities

        if newid != oldid:

            self.entities[newid] = copy(self.entities[oldid])
            if self.current_entity == oldid:
                self.current_entity = newid
            del self.entities[oldid]
            self.update()
        else:
            pass # Don't need to do anything if the old id is the same as the new id

    def add_entity(self, x, y, entityid, entitytype, update=True, metadata=None):
        #self.entities.append((x, y, random.randint(10, 50)))
        self.entities[entityid] = [x, y, entitytype, metadata]

        # In case lots of entities are added at once, update can be set to False to avoid
        # redrawing the widget too much.
        if update:
            self.update()

    def zoom(self, fac):
        if (self.zoom_factor + fac) > 0.1 and (self.zoom_factor + fac) <= 25:
            self._zoom_factor += int(fac*10)
            #self.zoom_factor = round(self.zoom_factor, 2)
            zf = self.zoom_factor
            self.setMinimumSize(QSize(int(self.SIZEX*zf), int(self.SIZEY*zf)))
            self.setMaximumSize(QSize(int(self.SIZEX*zf), int(self.SIZEY*zf)))

            #self.terrain_buffer = QImage()

            """if self.terrain is not None:
                if self.terrain_scaled is None:
                    self.terrain_scaled = self.terrain
                self.terrain_scaled = self.terrain_scaled.scaled(self.height(), self.width())"""

    def draw_entity(self, painter, x, y, size, zf, entityid, metadata):
        #print(x,y,size, type(x), type(y), type(size), metadata)
        if metadata is not None and "angle" in metadata and "angle2" in metadata:
            if entityid == self.current_entity:
                angle = metadata["angle"]
                angle2 = metadata["angle2"]
                x = int(x)
                y = int(y)

                center = QPoint(x,y)
                pen = painter.pen()
                prevwidth = pen.width()
                prevcolor = pen.color()
                pen.setColor(DEFAULT_ANGLE_MARKER)
                pen.setWidth(int(4))
                painter.setPen(pen)
                line1 = rotate(x, y-int(60*(zf/8.0)), x, y, angle)
                line2 = rotate(x, y-int(40*(zf/8.0)), x, y, angle2)

                painter.drawLine(center, line1)
                pen.setColor(prevcolor)
                pen.setWidth(prevwidth)
                painter.setPen(pen)
                painter.drawLine(center, line2)
        painter.drawRect(int(x-size//2), int(y-size//2), size, size)

    def draw_box(self, painter, x, y, size, zf, entityid, metadata, polycache):
        #painter.drawRect(x-size//2, y-size//2, size, size)
        if metadata is not None:
            width = metadata["width"]*zf
            length = metadata["length"]*zf
            #print("drawing")

            if (entityid not in polycache or
                        width != polycache[entityid][1] or length != polycache[entityid][2]
                        or x != polycache[entityid][3] or y != polycache[entityid][4]
                        or metadata["angle"] != polycache[entityid][5]):

                angle = metadata["angle"]
                p1 = rotate(x-width//2, y-length//2, x, y, angle)
                p2 = rotate(x-width//2, y+length//2, x, y, angle)#QPoint(x-width//2, y+length//2)
                p3 = rotate(x+width//2, y+length//2, x, y, angle)#QPoint(x+width//2, y+length//2)
                p4 = rotate(x+width//2, y-length//2, x, y, angle)#QPoint(x+width//2, y-length//2)
                polygon = QPolygon([p1, p2, p3, p4,
                                    p1])
                polycache[entityid] = [polygon, width, length, x, y, angle]
                pass
            else:
                pass
                polygon = polycache[entityid][0]


            #painter.rotate(45)
            radius = metadata["radius"]*zf
            if radius != 0.0:
                painter.drawArc(int(x-radius//2), int(y-radius//2), int(radius), int(radius), 0, 16*360)
            painter.drawPolyline(polygon)

            #painter.rotate(-45)

    def set_metadata(self, entityid, metadata):
        self.entities[entityid][3] = metadata

    def set_terrain(self, terrain, light_image,flat_image):
        self.terrain = QPixmap.fromImage(terrain)
        self.light_terrain = QPixmap.fromImage(light_image)
        self.flat_terrain = QPixmap.fromImage(flat_image)
        #self.terrain_scaled = self.terrain.scaled(self.height(), self.width())

    def get_pixel_brightness(self, event):
        image = self.image_label.pixmap().toImage()
        pixel_color = QColor(self.terrain.pixel(event.pos()))

        # Get brightness value (grayscale value)
        brightness = pixel_color.lightness()
        print("Brightness value at click point:", brightness)


    @catch_exception
    def paintEvent(self, event):
        start = default_timer()
        #print("painting")

        p = self.p
        p.begin(self)
        h = self.height()
        w = self.width()
        p.setBrush(QColor("white"))
        p.drawRect(0, 0, h-1, w-1)
        if (self.terrain is not None
                and self.show_terrain_mode in (SHOW_TERRAIN_REGULAR, SHOW_TERRAIN_LIGHT,SHOW_TERRAIN_FLAT)):
            #print("drawing image")
            #print(self.height(), self.width(), self.terrain.height(), self.terrain.width())

            exposedRect = event.rect()

            exp_rect_x = exposedRect.topLeft().x()
            exp_rect_y = exposedRect.topLeft().y()
            exp_rect_width = exposedRect.width()
            exp_rect_height = exposedRect.height()

            adjusted_startx = int((exp_rect_x / self.zoom_factor)/2)
            adjusted_starty = int((exp_rect_y / self.zoom_factor)/2)
            adjusted_width = int((exposedRect.width() / self.zoom_factor)/2)
            adjusted_height = int((exposedRect.height() / self.zoom_factor)/2)

            terrain_image = None
            print(self.show_terrain_mode)
            if self.show_terrain_mode == SHOW_TERRAIN_REGULAR:
                terrain_image = self.terrain
            elif self.show_terrain_mode == SHOW_TERRAIN_LIGHT:
                terrain_image = self.light_terrain
            elif self.show_terrain_mode == SHOW_TERRAIN_FLAT:
                terrain_image = self.flat_terrain

            p.drawPixmap(exposedRect.adjusted(-1, -1, 1, 1),
                         terrain_image,
                         QRect(adjusted_startx, adjusted_starty, adjusted_width, adjusted_height))

        if self.zoom_factor > 1:
            ENTITY_SIZE = int(self.ENTITY_SIZE * (1 + self.zoom_factor/10.0))
        else:
            ENTITY_SIZE = self.ENTITY_SIZE

        zf = self.zoom_factor
        current_entity = self.current_entity
        last_color = None
        #print("we are good")
        #try:
        drawbox = self.draw_box
        drawentity = self.draw_entity
        polycache = self.polygon_cache
        toggle = self.visibility_toggle
        draw_bound = event.rect().adjusted(-ENTITY_SIZE//2, -ENTITY_SIZE//2, ENTITY_SIZE//2, ENTITY_SIZE//2)
        #contains = draw_bound.contains
        selected_entities = self.selected_entities
        startx, starty = draw_bound.topLeft().x(), draw_bound.topLeft().y()
        endx, endy = startx+draw_bound.width(), starty+draw_bound.height()
        for entity, data in self.entities.items():
            x, y, entitytype, metadata = data
            x *= zf
            y *= zf

            if entitytype in toggle and toggle[entitytype] is False:
                continue

            if entitytype in COLORS:
                color = COLORS[entitytype]
            else:
                color = DEFAULT_ENTITY
            if last_color != color:
                p.setBrush(color)
                #p.setPen(QColor(color))
                last_color = color
            if current_entity != entity and entity not in selected_entities:
                #print(entitytype)
                if entitytype == "cMapZone":
                    mapzonetype = metadata["zonetype"]
                    if mapzonetype in MAPZONECOLORS:
                        color = MAPZONECOLORS[mapzonetype]
                    else:
                        color = DEFAULT_MAPZONE
                    drawentity(p, x, y, ENTITY_SIZE, zf, entity, metadata)

                    pen = p.pen()
                    pen.setColor(color)
                    origwidth = pen.width()
                    pen.setWidth(5)
                    p.setPen(pen)
                    drawbox(p, x, y, ENTITY_SIZE, zf, entity, metadata, polycache)
                    pen.setColor(DEFAULT_ENTITY)
                    pen.setWidth(origwidth)
                    p.setPen(pen)
                else:
                    #if True:#contains(x, y):
                    #if True:
                    if x >= startx and y >= starty and x <= endx and y <= endy:
                        drawentity(p, x, y, ENTITY_SIZE, zf, entity, metadata)

        # Draw the currently selected entity last so it is always above all other entities.
        for selected_entity in chain([self.current_entity], selected_entities.keys()):
            if selected_entity is None or selected_entity not in self.entities:
                continue
            x, y, entitytype, metadata = self.entities[selected_entity]
            x *= zf
            y *= zf



            if entitytype == "cMapZone":
                p.setBrush(QColor("red"))
                self.draw_entity(p, x, y, ENTITY_SIZE, zf,selected_entity, metadata)
                pen = p.pen()
                pen.setColor(DEFAULT_SELECTED)
                origwidth = pen.width()
                pen.setWidth(8)
                p.setPen(pen)
                self.draw_box(p, int(x), int(y), ENTITY_SIZE, zf, selected_entity, metadata, polycache)
                pen.setColor(DEFAULT_ENTITY)
                pen.setWidth(origwidth)
                p.setPen(pen)
            else:
                if x >= startx and y >= starty and x <= endx and y <= endy:
                    p.setBrush(QColor("red"))
                    self.draw_entity(p, x, y, ENTITY_SIZE, zf, selected_entity, metadata)

            p.setBrush(DEFAULT_ENTITY)

        if self.selectionbox_start is not None and self.selectionbox_end is not None:
            startpoint = QPoint(*self.selectionbox_start)
            endpoint = QPoint(*self.selectionbox_end)

            corner_horizontal = QPoint(self.selectionbox_end[0], self.selectionbox_start[1])
            corner_vertical = QPoint(self.selectionbox_start[0], self.selectionbox_end[1])
            selectionbox_polygon = QPolygon([startpoint, corner_horizontal, endpoint, corner_vertical,
                                            startpoint])
            p.drawPolyline(selectionbox_polygon)
        p.end()
        end = default_timer()


    def set_selection_box(self, start, end):
        self.selectionbox_start = start
        self.selectionbox_end = end

    def set_selectionbox_start(self, start):
        self.selectionbox_start = start
        #self.selected_entities = {}

    def set_selectionbox_end(self, end):
        self.selectionbox_end = end

        if self.selectionbox_start is not None and self.selectionbox_end is not None:
            selected = []
            self.selected_entities = {}
            startx = min(self.selectionbox_start[0], self.selectionbox_end[0])
            starty = min(self.selectionbox_start[1], self.selectionbox_end[1])
            endx = max(self.selectionbox_start[0], self.selectionbox_end[0])
            endy = max(self.selectionbox_start[1], self.selectionbox_end[1])

            for entity, data in self.entities.items():
                x, y, entitytype, metadata = data
                x *= self.zoom_factor
                y *= self.zoom_factor
                if entitytype not in self.visibility_toggle or self.visibility_toggle[entitytype] is True:
                    #print(startx, x, endx)
                    #print(starty, y, endy)
                    if startx < x < endx and starty < y < endy:
                        self.selected_entities[entity] = True

    def clear_selection_box(self):
        self.selectionbox_end = None
        self.selectionbox_start = None

    def mousePressEvent(self, event):
        #x,y = event.localPos()
        #if event.x() < self.height() and event.y() < self.width:

        print(event.x(), event.y())
        event_x, event_y = event.x(), event.y()
        hit = False
        search_start = default_timer()

        if self.zoom_factor > 1:
            ENTITY_SIZE = int(self.ENTITY_SIZE * (1 + self.zoom_factor/10.0))
        else:
            ENTITY_SIZE = self.ENTITY_SIZE

        if event.buttons() == Qt.LeftButton:
            entities_hit = []
            toggle = self.visibility_toggle
            for entity, data in self.entities.items():
                x, y, entitytype, metadata = data
                x *= self.zoom_factor
                y *= self.zoom_factor
                if entitytype in toggle and toggle[entitytype] is False:
                    continue
                if ((x + ENTITY_SIZE//2) > event_x > (x - ENTITY_SIZE//2)
                    and (y + ENTITY_SIZE//2) > event_y > (y - ENTITY_SIZE//2)):
                    #hit = True
                    entities_hit.append(entity)

            if len(entities_hit) > 0:
                if self.next_selected_index > (len(entities_hit) - 1):
                    self.next_selected_index = 0
                entity = entities_hit[self.next_selected_index]

                search_end = default_timer()
                self.next_selected_index = (self.next_selected_index+1) % len(entities_hit)
                self.entity_clicked.emit(event, entity)
            else:
                self.mouse_clicked.emit(event)
        else:
            self.mouse_clicked.emit(event)

    def mouseMoveEvent(self, event):
        self.mouse_dragged.emit(event)

    def mouseReleaseEvent(self, event):
        self.mouse_released.emit(event)

    def wheelEvent(self, event):
        self.mouse_wheel.emit(event)


class MenuDontClose(QMenu):
    def mouseReleaseEvent(self, e):
        try:
            action = self.activeAction()
            if action and action.isEnabled():
                action.trigger()
            else:
                QMenu.mouseReleaseEvent(self, e)
        except:
            traceback.print_exc()


class BWEntityEntry(QListWidgetItem):
    def __init__(self, xml_ref, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.xml_ref = xml_ref


class BWEntityListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def select_item(self, pos):
        #item = self.item(pos)
        self.setCurrentRow(pos)


class BWPassengerWindow(QMdiSubWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBaseSize(400, 400)

        self.centralwidget = QWidget(self)
        self.setWidget(self.centralwidget)

        layout = QHBoxLayout(self.centralwidget)
        self.passengerlist = QListWidget(self.centralwidget)
        layout.addWidget(self.passengerlist)
        self.setWindowTitle("Passengers")

    def reset(self):
        self.passengerlist.clearSelection()
        self.passengerlist.clear()

    def add_passenger(self, passenger_name, passenger_id):
        item = BWEntityEntry(passenger_id,
                             passenger_name)
        self.passengerlist.addItem(item)

    def set_title(self, entityname):
        self.setWindowTitle("Passengers - {0}".format(entityname))


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
