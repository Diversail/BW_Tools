# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bw_gui_prototype.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!
import traceback
import itertools
import gzip
from copy import copy, deepcopy
import os
from os import path
#from timeit import default_timer
#from math import atan2, degrees, radians, sin, cos

from PyQt5.QtCore import QSize, QRect, QMetaObject, QCoreApplication, QPoint
from PyQt5.QtWidgets import (QWidget, QMainWindow, QFileDialog, QTabWidget,
                             QSpacerItem, QLabel, QListWidget, QFormLayout,QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QDockWidget, QComboBox, QGridLayout, QMenuBar, QMenu, QAction, QApplication, QStatusBar, QLineEdit)
from PyQt5.QtGui import QMouseEvent
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

from lib.bw_read_xml import BattWarsLevel, BattWarsObject
from lib.custom_widgets import (BWEntityEntry, BWEntityListWidget, flag_data2, flag_data1, target_data2, BWEntityXMLEditor,
                            catch_exception, soldier_display, Allegiance_List, test_data, test_data2, dam_list1, dam_list2, bullet_flags_o, bullet_flags2,target_data_o)


from lib.helper_functions import (get_default_path, set_default_path, update_mapscreen,
                                  entity_get_army, entity_set_val,entity_get_icon_type, entity_get_model,
                                  object_get_seat,get_position_attribute,get_type,get_num,
                                  get_key, get_value,entity_set_list,entity_set_list2)

BW_LEVEL = "BW level files (*_level.xml *_level.xml.gz)"
BW_COMPRESSED_LEVEL = "BW compressed level files (*_level.xml.gz)"

class EditorMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.retranslateUi(self)

        self.level = None
        path = get_default_path()
        if path is None:
            self.default_path = ""
        else:
            self.default_path = path

        self.dragging = False
        self.last_x = None
        self.last_y = None
        self.dragged_time = None
        self.deleting_item = False # Hack for preventing focusing on next item after deleting the previous one

        self.moving = False

        self.model_dict = {}
        self.game_type = 0
        self.timestamp = 0
        self.setup = 0
        self.bulllist2 = []
        self.bulllist = []
        self.bullnum = 0
        self.extra = 0
        self.bullet = 0
        self.entity = 0
        self.model = 0
        self.flags = 0
        self.pref = 0
        self.ammo = 0
        self.obj_typing = 0
        self.seat_table = []

        self.resetting = False
        self.current_entity = None
        self.entity_list_widget.currentItemChanged.connect(self.action_listwidget_change_selection) 
        self.button_edit_xml.pressed.connect(self.action_open_xml_editor)
        self.bullet_l.editingFinished.connect(self.action_change_bullet)
        self.flags_l.editingFinished.connect(self.action_change_flags)
        self.flags_L.currentIndexChanged.connect(self.action_change_flag_box)
        self.pref_L.currentIndexChanged.connect(self.action_change_pref_box)
        self.pref_l.editingFinished.connect(self.action_change_pref)
        self.ammo_l.editingFinished.connect(self.action_change_ammo)
        self.bull_flag.editingFinished.connect(self.action_change_bull_flag)
        self.bull_L.currentIndexChanged.connect(self.action_change_bull_flag_box)
        self.bull_model.currentIndexChanged.connect(self.action_change_bull_model)
        self.bull_dam.currentIndexChanged.connect(self.action_change_bull_dam)
        self.bull_dam2.editingFinished.connect(self.action_change_bull_dam2)

        self.accel.editingFinished.connect(self.action_accel)
        self.drag.editingFinished.connect(self.action_drag)
        self.turnspeed.editingFinished.connect(self.action_turnspeed)
        self.ttm.editingFinished.connect(self.action_ttm)
        self.lifetime.editingFinished.connect(self.action_lifetime)
        self.bounce.editingFinished.connect(self.action_bounce)
        
        self.base_flags.editingFinished.connect(self.action_change_base_flags)
        self.range.editingFinished.connect(self.action_change_range)
        self.dam_list.currentIndexChanged.connect(self.action_dam_list)
        self.health.editingFinished.connect(self.action_health)
        self.reload.editingFinished.connect(self.action_change_reload)
        self.vel.editingFinished.connect(self.action_change_vel)
        self.label_3.activated[str].connect(self.action_change_alleg)
        self.label_2.activated[str].connect(self.action_open_table)
        self.displaying.activated[str].connect(self.action_change_display)
        self.button_edit_base_xml.pressed.connect(self.action_open_weapons_editor)
        self.button_edit_bullet_xml.pressed.connect(self.action_edit_bullet_xml)
        self.button_homing.pressed.connect(self.action_homing)

        status = self.statusbar


        self.xmlobject_textbox = BWEntityXMLEditor()
        self.xmlobject_textbox.button_xml_savetext.pressed.connect(self.xmleditor_action_save_object_xml)
        self.xmlobject_textbox.triggered.connect(self.action_open_xml_editor_unlimited)


        self.basexmlobject_textbox = BWEntityXMLEditor(windowtype="XML Base Object")
        self.basexmlobject_textbox.button_xml_savetext.pressed.connect(self.xmleditor_action_save_base_object_xml)
        self.basexmlobject_textbox.triggered.connect(self.action_open_xml_editor_unlimited)

        self.types_visible = {}
        self.terrain_image = None

        status.showMessage("Ready")

        self.xml_windows = {}
        print("We are now ready!")

    def reset(self):
        self.resetting = True
        self.statusbar.clearMessage()
        self.dragged_time = None
        self.moving = False
        self.dragging = False
        self.last_x = None
        self.last_y = None
        self.dragged_time = None

        self.moving = False

        self.entity_list_widget.clearSelection()
        self.entity_list_widget.clear()


        for window in (self.xmlobject_textbox, self.basexmlobject_textbox):
            window.close()
            window.reset()

        for id in self.xml_windows:
            self.destroy_xml_editor(id)

        self.resetting = False

        print("reset done")

    def destroy_xml_editor(self, id):
        pass

    @catch_exception
    def open_xml_editor(self, objectid, offsetx=0, offsety=0):
        selected = objectid
        if self.level is not None and selected in self.level.obj_map:
            print("XML_EDITOR")
            delete = []
            for objid, window in self.xml_windows.items():
                if not window.isVisible() and objid != selected:
                    window.destroy()
                    delete.append(objid)
            for objid in delete:
                del self.xml_windows[objid]

            if selected == self.basexmlobject_textbox.entity or selected == self.xmlobject_textbox.entity:
                pass # No need to make a new window
            elif selected in self.xml_windows and self.xml_windows[selected].isVisible():
                self.xml_windows[selected].activateWindow()
                self.xml_windows[selected].update()

            else:
                xml_window = BWEntityXMLEditor()

                def xmleditor_save_object_unlimited():
                    self.statusbar.showMessage("Saving object changes...")
                    try:
                        xmlnode = xml_window.get_content()
                        #assert self.bw_map_screen.current_entity == self.basexmlobject_textbox.entity
                        assert xml_window.entity == xmlnode.get("id")  # Disallow changing the id of the base object

                        self.level.remove_object(xmlnode.get("id"))
                        self.level.add_object(xmlnode)

                        self.statusbar.showMessage("Saved base object {0} as {1}".format(
                            xml_window.entity, self.level.obj_map[xmlnode.get("id")].name))
                    except:
                        self.statusbar.showMessage("Saving object failed")
                        traceback.print_exc()

                xml_window.button_xml_savetext.pressed.connect(xmleditor_save_object_unlimited)
                xml_window.triggered.connect(self.action_open_xml_editor_unlimited)


                obj = self.level.obj_map[selected]
                xml_window.set_title(obj.name)

                xml_window.set_content(obj._xml_node)
                #xml_window.move(QPoint(xml_editor_owner.pos().x()+20, xml_editor_owner.pos().y()+20))
                xml_window.move(QPoint(offsetx, offsety))

                xml_window.show()
                xml_window.update()
                self.xml_windows[selected] = xml_window



    @catch_exception
    def action_open_xml_editor_unlimited(self, xml_editor_owner):
        selected = xml_editor_owner.textbox_xml.textCursor().selectedText()
        self.open_xml_editor(selected,
                             offsetx=xml_editor_owner.pos().x()+20,
                             offsety=xml_editor_owner.pos().y()+20)

    @catch_exception
    def action_open_basexml_editor(self):
        """
        if not self.basexmlobject_textbox.isVisible():
            self.basexmlobject_textbox.destroy()
            self.basexmlobject_textbox = BWEntityXMLEditor(windowtype="XML Base Object")
            self.basexmlobject_textbox.button_xml_savetext.pressed.connect(self.xmleditor_action_save_base_object_xml)
            self.basexmlobject_textbox.triggered.connect(self.action_open_xml_editor_unlimited)
            self.basexmlobject_textbox.show()

        self.basexmlobject_textbox.activateWindow()"""
        if self.level is not None and self.current_entity is not None:
            identifier = 0
            obj = self.level.obj_map[self.current_entity]
            if obj.has_attr("mBase"):
                baseobj = self.level.obj_map[obj.get_attr_value("mBase")]
                identifier = 1
            else:
                pass
            if identifier == 1:
                self.open_xml_editor(baseobj.id)

    def xmleditor_action_save_base_object_xml(self):
        self.statusbar.showMessage("Saving base object changes...")
        try:
            xmlnode = self.basexmlobject_textbox.get_content()
            #assert self.bw_map_screen.current_entity == self.basexmlobject_textbox.entity
            assert self.basexmlobject_textbox.entity == xmlnode.get("id")  # Disallow changing the id of the base object

            self.level.remove_object(xmlnode.get("id"))
            self.level.add_object(xmlnode)

            self.statusbar.showMessage("Saved base object {0} as {1}".format(
                self.basexmlobject_textbox.entity, self.level.obj_map[xmlnode.get("id")].name))
        except:
            self.statusbar.showMessage("Saving base object failed")
            traceback.print_exc()

    def action_open_xml_editor(self):
        """
        if not self.xmlobject_textbox.isVisible():
            self.xmlobject_textbox.destroy()
            self.xmlobject_textbox = BWEntityXMLEditor()
            self.xmlobject_textbox.button_xml_savetext.pressed.connect(self.xmleditor_action_save_object_xml)
            self.xmlobject_textbox.triggered.connect(self.action_open_xml_editor_unlimited)
            self.xmlobject_textbox.show()

        self.xmlobject_textbox.activateWindow()"""
        if self.level is not None and self.current_entity is not None:
            entityobj = self.level.obj_map[self.current_entity]
            self.open_xml_editor(objectid=entityobj.id)

            #update_mapscreen(self.bw_map_screen, self.level.obj_map[entityobj.id])
            #self.bw_map_screen.update()

        """self.xmlobject_textbox.set_title(entityobj.id)

            self.xmlobject_textbox.set_content(entityobj._xml_node)

            self.xmlobject_textbox.update()"""
    def action_open_weapons_editor(self):
        if self.level is not None and self.current_entity is not None:
            entityobj = self.level.obj_map[self.label_2.currentText()]
            self.open_xml_editor(entityobj.id,100,100)

    def action_edit_bullet_xml(self):
        if self.level is not None and self.current_entity is not None:
            entityobj = self.level.obj_map[self.bullet_l.text()]
            self.open_xml_editor(entityobj.id, 200,200)
    def action_change_alleg(self):
        entity_set_val(self.level, self.current_entity,"mArmy",self.label_3.currentText())

    def action_change_bullet(self):
        entity_set_val(self.level, self.label_2.currentText(),"BulletType",self.bullet_l.text())

    def action_change_flags(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            entity_set_val(self.level, self.label_2.currentText(),"Flags",self.flags_l.text())
            if self.flags_l.text() in flag_data:
                seat = flag_data[self.flags_l.text()]
            else:
                seat = ""
            self.flags_L.setItemText(0,seat)
            self.flags_L.setCurrentIndex(0)

    def action_change_flag_box(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            self.extra = self.flags_L.currentText()
            seat = get_key(self.flags_L.currentText(),flag_data)
            if seat == None or seat == 0:
                seat = self.flags_l.text()
            else:
                self.flags_l.setText(seat)
                self.flags_L.setItemText(0,self.extra)
                entity_set_val(self.level, self.label_2.currentText(),"Flags",self.flags_l.text())

    def action_change_pref_box(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            self.extra = self.pref_L.currentText()
            seat = get_key(self.pref_L.currentText(),target_data)
            if seat == None or seat == 0:
                seat = self.pref_l.text()
            else:
                print("seat is %s" % seat)
                self.pref_l.setText(seat)
                self.pref_L.setItemText(0,self.extra)
                entity_set_val(self.level, self.label_2.currentText(),"PreferredTargetType",self.pref_l.text())

    def action_change_pref(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            entity_set_val(self.level, self.label_2.currentText(),"PreferredTargetType",self.pref_l.text())
            if self.pref_l.text() in target_data:
                seat = target_data[self.pref_l.text()]
            else:
                seat = ""
            self.pref_L.setItemText(0,seat)
            self.pref_L.setCurrentIndex(0)

    def action_change_ammo(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            entity_set_val(self.level, self.label_2.currentText(),"MaxAmmoInClip",self.ammo_l.text())

    def action_change_bull_flag(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            entity_set_val(self.level, self.bullet,"mObjFlags",self.bull_flag.text())
            if self.bull_flag.text() in bullet_flags:
                seat = bullet_flags[self.bull_flag.text()]
            else:
                seat = ""
            print("just bull flag")
            self.bull_L.setItemText(0,seat)
            self.bull_L.setCurrentIndex(0)

    def action_change_bull_flag_box(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            self.extra = self.bull_L.currentText()
            seat = get_key(self.bull_L.currentText(),bullet_flags)
            if seat == None or seat == 0:
                seat = self.bull_flag.text()
            else:
                self.bull_flag.setText(seat)
                self.bull_L.setItemText(0,self.extra)
                entity_set_val(self.level, self.bullet,"mObjFlags",self.bull_flag.text())

    def action_change_bull_model(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            seat = get_value(self.bull_model.currentText(),self.model_dict)
            if seat != 0:
                entity_set_val(self.level, self.bullet,"mModel",seat)


    def action_change_reload(self):
        entity_set_val(self.level, self.label_2.currentText(),"ReloadTime",self.reload.text())

    def action_change_range(self):
        entity_set_val(self.level, self.label_2.currentText(),"MaxRange",self.range.text())

    def action_health(self):
        entity_set_val(self.level, self.entity,"mMaxHealth",self.health.text())

    def action_change_vel(self):
        print("setting Vel")
        entity_set_list(self.level, self.label_2.currentText(),"LaunchVec",self.vel.text(),2)

    def action_change_bull_dam(self):
        if self.label_2.currentText() != "":
            obj = self.level.obj_map[self.label_2.currentText()]
            self.bullnum = self.bull_dam.currentIndex()
            self.dam_list.setCurrentIndex(0)
            self.bull_dam2.setText(self.bulllist[self.bullnum])
            #entity_set_val(self.level, self.bullet,"mDamageAmount",self.bull_dam2.text())
        
    def action_change_bull_dam2(self):
        entity_set_list2(self.level, self.bullet,"mDamageAmount",self.bull_dam2.text(),self.bullnum)
        self.bulllist[self.bullnum] = self.bull_dam2.text()

    def action_change_base_flags(self):
        entity_set_val(self.level, self.entity,"mUnitFlags",self.base_flags.text())
        
    def action_accel(self):
        entity_set_val(self.level, self.bullet,"mAccel",self.accel.text())

    def action_drag(self):
        entity_set_val(self.level, self.bullet,"mDrag",self.drag.text())

    def action_turnspeed(self):
        entity_set_val(self.level, self.bullet,"mTurnSpeed",self.turnspeed.text())

    def action_ttm(self):
        entity_set_val(self.level, self.bullet,"mTimeToMaxTurnSpeed",self.ttm.text())
        #self.help.setText("Time to max turning speed")

    def action_lifetime(self):
        entity_set_val(self.level, self.bullet,"mMaxLifeTime",self.lifetime.text())
        #self.help.setText("Bullet lifetime is useful for homing projec\ntiles")

    def action_bounce(self):
        entity_set_val(self.level, self.bullet,"mBounceFactor",self.bounce.text())
        #self.help.setText("Bounce Factor is normally .6666")

    def action_dam_list(self):
        if self.setup == 0:
            if self.label_2.currentText() != "" and self.dam_list.currentIndex() != 0:
                obj = self.level.obj_map[self.label_2.currentText()]
                d = self.bull_dam.currentIndex()
                self.bull_dam.setItemText(d,self.dam_list.currentText())
                entity_set_list2(self.level, self.bullet,"mDamageType",self.dam_list.currentText(),d)
                self.bulllist2[d] = self.dam_list.currentText()

    def action_change_display(self):
        print('open')
        mod = self.displaying.currentText()
        print(mod)
        if mod != "":
            obj = self.level.obj_map[self.current_entity]
            if obj.has_attr("mSeatData"):
                dumped = obj.get_attr_elements("mSeatData")
                seat = self.level.obj_map[dumped[self.label_2.currentIndex()]]
                if seat.has_attr("DisplayType"):
                    entity_set_val(self.level, dumped[self.label_2.currentIndex()],"DisplayType",mod)
                    val = self.label_2.currentIndex()
                    self.seat_table[val] = mod
                    self.displaying.setItemText(0,mod)
                    print('success!')

    def action_open_table(self):
        if self.timestamp != os.path.getmtime(self.default_path):
            print('EEEEEEEEECCCK!!!!!!!')
            self.help.setText("The Level File has been modified!\n(Probably by Notepad++)")
        self.clear_functions()
        if self.label_2.currentText() == "":
            print('No Weapon!')
        else:
            if len(self.seat_table) > 0:
                val = self.label_2.currentIndex()
                self.displaying.setItemText(0,self.seat_table[val])
            obj = self.level.obj_map[self.label_2.currentText()]
            if obj.return_type("cAdvancedWeaponBase"):
                self.indicator.setText("Advanced_Weapons_Base")
            if obj.has_attr("BulletType"):
                self.bullet = format(obj.get_attr_value("BulletType"))
                self.bullet_l.setText(self.bullet)
                seat = self.level.obj_map[self.bullet]
                if seat.has_attr("mObjFlags"):
                    self.bull_flag.setText(seat.get_attr_value("mObjFlags"))
                    nexts = bullet_flags.get(self.bull_flag.text(), None)
                    if nexts != None:
                        self.bull_L.setCurrentIndex(0)
                        self.bull_L.setItemText(0,format(nexts))
                if seat.has_attr("mModel"):
                    typ = seat.get_attr_value("mModel")
                    if typ == "0":
                        self.bull_model.setCurrentIndex(0)
                    else:
                        self.model = self.level.obj_map[typ]
                        if self.model.has_attr("mName"):
                            typ = self.model.get_attr_value("mName")
                            f = self.bull_model.findText(typ)
                            if f == -1:
                                self.bull_model.setCurrentIndex(0)
                            else:
                                self.bull_model.setCurrentIndex(f)
                if seat.has_attr("mAccel"):
                    self.accel.setText(seat.get_attr_value("mAccel"))
                if seat.has_attr("mDrag"):
                    self.drag.setText(seat.get_attr_value("mDrag"))
                if seat.has_attr("mTurnSpeed"):
                    self.turnspeed.setText(seat.get_attr_value("mTurnSpeed"))
                if seat.has_attr("mTimeToMaxTurnSpeed"):
                    self.ttm.setText(seat.get_attr_value("mTimeToMaxTurnSpeed"))
                if seat.has_attr("mMaxLifeTime"):
                    self.lifetime.setText(seat.get_attr_value("mMaxLifeTime"))
                if seat.has_attr("mBounceFactor"):
                    self.bounce.setText(seat.get_attr_value("mBounceFactor"))
                if seat.has_attr("mDamageAmount"):
                    self.bulllist = seat.get_attr_elements("mDamageAmount")
                    self.bull_dam2.setText(self.bulllist[self.bullnum])
                if seat.has_attr("mDamageType"):
                    self.bulllist2 = seat.get_attr_elements("mDamageType")
                    for i in self.bulllist2:
                        self.bull_dam.addItem(i)
            if obj.has_attr("Flags"):
                self.flags = format(obj.get_attr_value("Flags"))
                self.flags_l.setText(self.flags)
                seat = flag_data.get(self.flags_l.text(), None)
                self.flags_L.setCurrentIndex(0)
                if seat != None:
                    self.flags_L.setItemText(0,format(seat))
                else:
                    flag_data.update({self.flags: self.label_5.text()+self.label_3.currentText()})
                    self.flags_L.addItem(flag_data[self.flags])
                    self.flags_L.setItemText(0,format(self.label_5.text()))
                    seat2 = test_data.get(self.flags_l.text(), None)
                    if seat2 == None:
                        test_data.update({self.flags: self.label_5.text()+self.label_3.currentText()})
            if obj.has_attr("PreferredTargetType"):
                self.pref = format(obj.get_attr_value("PreferredTargetType"))
                self.pref_l.setText(self.pref)
                seat = target_data.get(self.pref_l.text(), None)
                if seat != None:
                    self.pref_L.setCurrentIndex(0)
                    self.pref_L.setItemText(0,format(seat))
            if obj.has_attr("MaxAmmoInClip"):
                self.ammo = format(obj.get_attr_value("MaxAmmoInClip"))
                self.ammo_l.setText(self.ammo)
            if obj.has_attr("MaxRange"):
                self.range.setText(obj.get_attr_value("MaxRange"))
            if obj.has_attr("ReloadTime"):
                self.reload.setText(obj.get_attr_value("ReloadTime"))
            if obj.has_attr("LaunchVec"):
                matrix = [x for x in obj.get_attr_value("LaunchVec").split(",")]
                self.vel.setText(matrix[2])
                #entity_set_list(self.level, self.label_2.currentText(),"LaunchVec",self.vel.text(),2)

    def action_homing(self):
        if self.label_2.currentText() != "":
            '''import json
            file = open("writing_file.txt","w")
            file.write(json.dumps(test_data))
            file.close()'''
            obj = self.level.obj_map[self.label_2.currentText()]
            print(self.obj_typing)
            go_go = 1
            self.bullet_flagging = "0"
            self.dragging = "0"
            self.turn_speed = "0"
            self.Time_to_Max = "0.350000"
            if self.obj_typing == "sTroopBase":
                self.bullet_flagging = "987"
                self.turn_speed = "0.785398"
            elif self.obj_typing == "cGroundVehicleBase":
                self.bullet_flagging = "907"
                self.turn_speed = "0.785398"
            elif self.obj_typing == "cBuildingImpBase":
                self.bullet_flagging = "907"
                self.turn_speed = "0.785398"
            elif self.obj_typing == "sAirVehicleBase":
                self.bullet_flagging = "971"
                self.turn_speed = "0.785398"
            elif self.obj_typing == "cWaterVehicleBase":
                self.bullet_flagging = "907"
                self.turn_speed = "0.785398"
            else:
                print("INCORRECT OBJECT")
                go_go = 0
            if go_go == 1:
                if obj.has_attr("PreferredTargetType"):
                    self.pref_l.setStyleSheet("border-style: solid;"
                        "border-width: 2px;"
                        "border-color: #089404;")
                seat = self.level.obj_map[format(obj.get_attr_value("BulletType"))]
                if seat.has_attr("mTurnSpeed"):
                    self.turnspeed.setText(self.turn_speed)
                    entity_set_val(self.level, self.bullet,"mTurnSpeed",self.turnspeed.text())
                    self.turnspeed.setStyleSheet("border-style: solid;"
                        "border-width: 2px;"
                        "border-color: #FA8072;")
                if seat.has_attr("mTimeToMaxTurnSpeed"):
                    self.ttm.setStyleSheet("border-style: solid;"
                        "border-width: 2px;"
                        "border-color: #089404;")
                if seat.has_attr("mDrag"):
                    self.drag.setStyleSheet("border-style: solid;"
                        "border-width: 2px;"
                        "border-color: #089404;")
                if seat.has_attr("mAccel"):
                    self.accel.setStyleSheet("border-style: solid;"
                        "border-width: 2px;"
                        "border-color: #089404;")
                if seat.has_attr("mMaxLifeTime"):
                    self.lifetime.setStyleSheet("border-style: solid;"
                        "border-width: 2px;"
                        "border-color: #089404;")
                if seat.has_attr("mObjFlags"):
                    self.bull_flag.setText(self.bullet_flagging)
                    entity_set_val(self.level, self.bullet,"mObjFlags",self.bull_flag.text())
                    if self.bullet_flagging in bullet_flags:
                        self.bull_L.setItemText(0,bullet_flags[self.bullet_flagging])
                        self.bull_L.setCurrentIndex(0)
                    self.bull_flag.setStyleSheet("border-style: solid;"
                        "border-width: 2px;"
                        "border-color: #FA8072;")


    def xmleditor_action_save_object_xml(self):
        self.statusbar.showMessage("Saving object changes...")
        try:
            xmlnode = self.xmlobject_textbox.get_content()
            #assert self.bw_map_screen.current_entity == self.xmlobject_textbox.entity
            assert self.xmlobject_textbox.entity == xmlnode.get("id") or xmlnode.get("id") not in self.level.obj_map


            if self.xmlobject_textbox.entity != xmlnode.get("id"):
                #obj = self.level.obj_map[xmlnode.get("id")]
                self.level.remove_object(self.xmlobject_textbox.entity)
                print("adding", xmlnode.get("id"), xmlnode.get("id") in self.level.obj_map )
                self.level.add_object(xmlnode)

                pos = self.get_entity_item_pos(self.xmlobject_textbox.entity)
                item = self.entity_list_widget.takeItem(pos)
                self.entity_list_widget.removeItemWidget(item)
                self.add_item_sorted(xmlnode.get("id"))

                self.bw_map_screen.rename_entity(self.xmlobject_textbox.entity, xmlnode.get("id"))
                assert xmlnode.get("id") in self.level.obj_map
                self.xmlobject_textbox.entity = xmlnode.get("id")
                self.xmlobject_textbox.set_title(xmlnode.get("id"))

            else:
                self.level.remove_object(xmlnode.get("id"))
                self.level.add_object(xmlnode)

            update_mapscreen(self.bw_map_screen, self.level.obj_map[xmlnode.get("id")])

            self.statusbar.showMessage("Saved object {0} as {1}".format(
                self.xmlobject_textbox.entity, self.level.obj_map[xmlnode.get("id")].name))
            self.bw_map_screen.update()

        except:
            self.statusbar.showMessage("Saving object failed")
            traceback.print_exc()

    def add_item_sorted(self, entity):
        max_count = self.entity_list_widget.count()
        entityobj = self.level.obj_map[entity]
        index = 0
        entity_item = BWEntityEntry(entity, "{0}[{1}]".format(entity, entityobj.type))

        # Similar to loading a level, we add the entity in a sorted way by
        # creating this string and comparing it for every item in the list.
        entity_string = get_type(entityobj.type)+entityobj.type+entityobj.id

        inserted = False

        for i in range(max_count):
            curritem = self.entity_list_widget.item(i)
            currobj = self.level.obj_map[curritem.xml_ref]
            currstring = get_type(currobj.type)+currobj.type+currobj.id

            # The list is already sorted, so if we find an item bigger than
            # the one we are inserting, we know the position we have to insert the item in.
            # String comparison should be alpabetically.
            if currstring > entity_string:
                self.entity_list_widget.insertItem(i, entity_item)
                inserted = True
                break

        # If we couldn't insert the item, i.e. there are no items at all
        # or all items are smaller than the item we add, we just add it at the end.
        if not inserted:
            self.entity_list_widget.addItem(entity_item)

    def get_entity_item_pos(self, entityid):
        for i in range(self.entity_list_widget.count()):
            item = self.entity_list_widget.item(i)

            if item.xml_ref == entityid:
                return i

        return None

    def load_misc(self):
        global flag_data, bullet_flags, target_data
        Allegiance_List = []
        self.label_3.clear()
        self.bull_model.clear()
        self.label_3.addItem("")
        self.flags_L.clear()
        self.dam_list.clear()
        self.bull_L.clear()
        self.pref_L.clear()
        self.bull_L.addItem("")
        self.flags_L.addItem("")
        self.dam_list.addItem("")
        self.pref_L.addItem("")
        bullet_flags = bullet_flags_o
        target_data = target_data_o
        print("Game Type %s"%self.game_type)
        for i in dam_list1:
            self.dam_list.addItem(i)
        if self.game_type == 2:
            for i in dam_list2:
                self.dam_list.addItem(i)
            for i in target_data2:
                print(i)
                print(target_data2[i])
                target_data.update({i: target_data2[i]})
            flag_data = flag_data2
            for i in bullet_flags2:
                bullet_flags.update({i: bullet_flags2[i]})
        elif self.game_type == 1:
            flag_data = flag_data1
        for i in flag_data:
            self.flags_L.addItem(flag_data[i])
        for i in target_data:
            self.pref_L.addItem(target_data[i])
        for i in bullet_flags:
            self.bull_L.addItem(bullet_flags[i])

    def button_load_level(self):
        try:
            self.setup = 1
            print("ok", self.default_path)
            self.xmlPath = ""
            filepath, choosentype = QFileDialog.getOpenFileName(
                self, "Open File",
                self.default_path,
                BW_LEVEL+";;"+BW_COMPRESSED_LEVEL+";;All files (*)")
            if filepath:
                print("resetting")
                self.reset()
                self.clear_functions()
                print("done")
                print("chosen type:",choosentype)

                # Some BW levels are clear XML files, some are compressed with GZIP
                # We decide between the two either based on user choice or end of filepath
                if choosentype == BW_COMPRESSED_LEVEL or filepath.endswith(".gz"):
                    print("OPENING AS COMPRESSED")
                    file_open = gzip.open
                    self.game_type = 2
                else:
                    file_open = open
                    self.game_type = 1
                self.load_misc()
                self.timestamp = os.path.getmtime(filepath)
                with file_open(filepath, "rb") as f:
                    try:
                        self.level = BattWarsLevel(f)
                        self.default_path = filepath
                        set_default_path(filepath)
                        for obj_id, obj in sorted(self.level.obj_map.items(),
                                                  key=lambda x: get_type(x[1].type)+x[1].type+x[1].id):
                            if obj.has_attr("mArmy") or obj.has_attr("mWeaponLoads"):
                                if obj.has_attr("mArmy"):
                                    seat = format(obj.get_attr_value("mArmy"))
                                    if seat != None and seat not in Allegiance_List:
                                        Allegiance_List.append(seat)
                                        self.label_3.addItem(seat)
                                item = BWEntityEntry(obj_id, "{0}[{1}]".format(obj_id, obj.type))
                                self.entity_list_widget.addItem(item)
                            if obj.return_type("cNodeHierarchyResource"):
                                print(obj.get_attr_value("mName"))
                            if obj.return_type("sProjectileBase"):
                                seat = obj.get_attr_value("mModel")
                                if seat != "0":
                                    second = seat
                                    seat = self.level.obj_map[obj.get_attr_value("mModel")]
                                    if seat.has_attr("mName"):
                                        main = seat.get_attr_value("mName")
                                        if main not in self.model_dict:
                                            self.model_dict[main] = second
                        self.bull_model.addItem("")
                        self.bull_model.addItems(self.model_dict.keys())
                        print("ok")
                        path_parts = path.split(filepath)
                        self.setWindowTitle("BW-MapEdit - {0}".format(path_parts[-1]))
                        self.setup = 0

                    except Exception as error:
                        print("error", error)
                        traceback.print_exc()
        except Exception as er:
            print("errrorrr", er)
            traceback.print_exc()
        print("loaded")
    def button_save_level(self):
        if self.level is not None:
            filepath, choosentype = QFileDialog.getSaveFileName(
                self, "Save File",
                self.default_path,
                BW_LEVEL+";;"+BW_COMPRESSED_LEVEL+";;All files (*)")
            print(filepath, "saved")

            if filepath:
                # Simiar to load level
                if choosentype == BW_COMPRESSED_LEVEL or filepath.endswith(".gz"):
                    file_open = gzip.open
                else:
                    file_open = open
                try:
                    with file_open(filepath, "wb") as f:
                        self.level._tree.write(f)
                except Exception as error:
                    print("COULDN'T SAVE:", error)
                    traceback.print_exc()

                self.default_path = filepath
        else:
            pass # no level loaded, do nothing
    def clear_functions(self):
        self.displaying.setItemText(0,"")
        self.displaying.setCurrentIndex(0)
        self.accel.clear()
        self.drag.clear()
        self.turnspeed.clear()
        self.ttm.clear()
        self.lifetime.clear()
        self.bounce.clear()
        self.pref_l.clear()
        self.flags_l.clear()
        self.bullet_l.clear()
        self.ammo_l.clear()
        self.bull_flag.clear()
        self.range.clear()
        self.reload.clear()
        self.vel.clear()
        self.bull_model.setItemText(0,"")
        self.bull_model.setCurrentIndex(0)
        self.pref_L.setItemText(0,"")
        self.flags_L.setItemText(0,"")
        self.bull_L.setItemText(0,"")
        self.bull_dam.clear()
        self.bull_dam2.clear()
        self.bulllist = []
        self.bulllist2 = []
        self.indicator.clear()
        self.pref_l.setStyleSheet("border-width: 0px;")
        self.drag.setStyleSheet("border-width: 0px;")
        self.accel.setStyleSheet("border-width: 0px;")
        self.lifetime.setStyleSheet("border-width: 0px;")
        self.turnspeed.setStyleSheet("border-width: 0px;")
        self.ttm.setStyleSheet("border-width: 0px;")
        self.bull_flag.setStyleSheet("border-width: 0px;")
        
        
    def set_entity_text(self, entityid):
        try:
            #self.clear_functions()
            self.obj_typing = 0
            seat = 0
            go_go = 0
            self.seat_table = []
            self.label_2.clear()
            self.health.clear()
            self.entity = entityid
            obj = self.level.obj_map[entityid]
            if obj.has_attr("mBase"):
                base = self.level.obj_map[obj.get_attr_value("mBase")]
                self.label_object_id.setText("{0}\n[{1}]\nBase: {2}\n[{3}]".format(
                    entityid, obj.type, base.id, base.type))
            else:
                self.label_object_id.setText("{0}[{1}]".format(entityid, obj.type))
            self.label_model_name.setText("Model: {0}".format(entity_get_model(self.level, entityid)))
            self.label_3.setItemText(0,format(entity_get_army(self.level, entityid)))
            self.label_3.setCurrentIndex(0)
            self.obj_typing = obj.type
            if not obj.has_attr("mPassenger"):
                self.label_5.setText(format(entity_get_icon_type(self.level, entityid,self.game_type)))
            if obj.has_attr("mWeaponLoads"):
                go_go = 0
                seat = obj.get_attr_value("mWeaponLoads")
                if seat != "0":
                    self.label_2.addItem(seat)
                    alter_obj = self.level.obj_map[seat]
                    go_go = 1

            if obj.has_attr("mPlayerWeaponLoads"):
                go_go = 0
                seat = obj.get_attr_value("mPlayerWeaponLoads")
                if seat != "0":
                    self.label_2.addItem(seat)
                    alter_obj = self.level.obj_map[seat]
                    go_go = 1
            if obj.has_attr("mMaxHealth"):
                self.health.setText(obj.get_attr_value("mMaxHealth"))

            if obj.has_attr("mUnitFlags"):
                self.base_flags.setText(obj.get_attr_value("mUnitFlags"))
                
            if obj.has_attr("mSeatData"):
                go_go = 0
                for seat in obj.get_attr_elements("mSeatData"):
                    if seat != "0":
                        alter_obj = self.level.obj_map[seat]
                        if alter_obj.has_attr("WeaponType"):
                            m = format(alter_obj.get_attr_value("WeaponType"))
                            if m != "0":
                                go_go = 1
                                self.label_2.addItem(m)
                                #self.displaying.addItem(format(alter_obj.get_attr_value("DisplayType")))
                                self.seat_table.append(format(alter_obj.get_attr_value("DisplayType")))

            if go_go == 1:
                rum = format(self.label_2.currentText())
                self.action_open_table()
            else:
                print('not viable')
                self.clear_functions()
        except:
            traceback.print_exc()

    def action_listwidget_change_selection(self, current, previous):
        if not self.resetting and current is not None:
            print("hi", current.text(), current.xml_ref)
            self.current_entity = current.xml_ref
            self.set_entity_text(current.xml_ref)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(420, 760)
        MainWindow.setMinimumSize(QSize(720, 560))
        MainWindow.setWindowTitle("BW-MapEdit")


        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.indicator = QLabel(self.centralwidget)
        self.indicator.setObjectName("indicator")
        self.indicator.setText("")
        
        self.bullet_l = QLineEdit(self.centralwidget)
        self.bullet_l.setObjectName("Bullet")
        self.bullet_l.setPlaceholderText("None")

        self.flags_l = QLineEdit(self.centralwidget)
        self.flags_l.setObjectName("Flag")
        self.flags_l.setPlaceholderText("None")

        self.pref_l = QLineEdit(self.centralwidget)
        self.pref_l.setObjectName("Pref")
        self.pref_l.setPlaceholderText("None")

        self.ammo_l = QLineEdit(self.centralwidget)
        self.ammo_l.setObjectName("Ammo")
        self.ammo_l.setPlaceholderText("None")

        self.range = QLineEdit(self.centralwidget)
        self.range.setObjectName("range")
        self.range.setPlaceholderText("None")

        self.reload = QLineEdit(self.centralwidget)
        self.reload.setObjectName("reload")
        self.reload.setPlaceholderText("None")

        self.vel = QLineEdit(self.centralwidget)
        self.vel.setObjectName("vel")
        self.vel.setPlaceholderText("None")
        
        self.bull_flag = QLineEdit(self.centralwidget)
        self.bull_flag.setObjectName("bull")
        self.bull_flag.setPlaceholderText("None")

        self.bull_model = QComboBox(self.centralwidget)
        self.bull_model.setObjectName("bull_model")
        #self.bull_model.setPlaceholderText("None")

        self.bull_dam = QComboBox(self.centralwidget)
        self.bull_dam.setObjectName("bull_dam")
        self.bull_dam.addItem("")

        self.base_flags = QLineEdit(self.centralwidget)
        self.base_flags.setObjectName("base_flags")
        self.base_flags.setPlaceholderText("None")

        self.bull_dam2 = QLineEdit(self.centralwidget)
        self.bull_dam2.setObjectName("bull_dam2")
        self.bull_dam2.setPlaceholderText("None")

        self.dam_list = QComboBox(self.centralwidget)
        self.dam_list.setObjectName("dam_list")
        self.dam_list.addItem("")


        self.pref_L = QComboBox(self.centralwidget)
        self.pref_L.setObjectName("pref_L")

        self.flags_L = QComboBox(self.centralwidget)
        self.flags_L.setObjectName("flags_L")

        self.flags_L.addItem("")

        self.bull_L = QComboBox(self.centralwidget)
        self.bull_L.setObjectName("bull_L")
        self.bull_L.addItem("")

        self.label_2 = QComboBox(self.centralwidget)
        self.label_2.setObjectName("label_2")

        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.label_5.setText("Icon Type")

        self.health = QLineEdit(self.centralwidget)
        self.health.setObjectName("health")
        self.health.setPlaceholderText("None")

        self.label_object_id = QLabel(self.centralwidget)
        self.label_object_id.setObjectName("label_object_id")
        self.label_object_id.setText("Base")
        
        self.label_model_name = QLabel(self.centralwidget)
        self.label_model_name.setObjectName("label_model_name")
        self.label_model_name.setText("Model")

        self.dud = QLabel(self.centralwidget)
        self.dud.setObjectName("dud")

        self.accel = QLineEdit(self.centralwidget)
        self.accel.setObjectName("accel")
        self.accel.setPlaceholderText("None")

        self.drag = QLineEdit(self.centralwidget)
        self.drag.setObjectName("drag")
        self.drag.setPlaceholderText("None")

        self.turnspeed = QLineEdit(self.centralwidget)
        self.turnspeed.setObjectName("turnspeed")
        self.turnspeed.setPlaceholderText("None")

        self.ttm = QLineEdit(self.centralwidget)
        self.ttm.setObjectName("ttm")
        self.ttm.setPlaceholderText("None")

        self.lifetime = QLineEdit(self.centralwidget)
        self.lifetime.setObjectName("lifetime")
        self.lifetime.setPlaceholderText("None")

        self.bounce = QLineEdit(self.centralwidget)
        self.bounce.setObjectName("bounce")
        self.bounce.setPlaceholderText("None")

        self.help = QLabel(self.centralwidget)
        self.help.setObjectName("help")

        self.spacerItem1 = QSpacerItem(10, 160, QSizePolicy.Expanding,   QSizePolicy.Minimum)
        self.spacerItem2 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        for label in (self.label_object_id, self.label_model_name,self.label_5):
            label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)


        self.test = QWidget(self.centralwidget)
        self.test.setMaximumSize(QSize(250, 1200))
        self.testlay = QVBoxLayout(self.test)
        self.testlay.setObjectName("testlay")
        self.testlay.addItem(self.spacerItem1)
        self.testlay.addWidget(self.bull_L)
        self.testlay.addWidget(self.dam_list)
        self.testlay.addWidget(self.help)

        self.tab1 = QWidget(self.centralwidget)
        self.tab2 = QWidget(self.centralwidget)
        layout = QFormLayout(self.tab1)
        lay2 = QFormLayout(self.tab2)
        lay2.addRow(self.flags_L)
        lay2.addRow(self.pref_L)
        lay2.addRow(self.indicator)
        lay2.addRow(self.test)

        layout.addRow("Flags",self.flags_l)
        layout.addRow("Target Type",self.pref_l)
        layout.addRow("Max Ammo",self.ammo_l)
        layout.addRow("Range",self.range)
        layout.addRow("Reload",self.reload)
        layout.addRow("Velocity",self.vel)
        layout.addRow(self.dud)
        layout.addRow("Bullet ID",self.bullet_l)
        layout.addRow("Bullet Model",self.bull_model)
        layout.addRow("Bullet Flags",self.bull_flag)
        layout.addRow("Damage",self.bull_dam)
        layout.addRow("Damage2",self.bull_dam2)

        layout.addRow("Accel",self.accel)
        layout.addRow("Drag",self.drag)
        layout.addRow("Turn Speed",self.turnspeed)
        layout.addRow("TtMTS",self.ttm)
        layout.addRow("Bullet Lifetime",self.lifetime)
        layout.addRow("Bounce",self.bounce)
        self.tab1.setLayout(layout)
        self.tab2.setLayout(lay2)
        self.horizontalLayout.addWidget(self.tab1)
        self.horizontalLayout.addWidget(self.tab2)
        
        self.vertLayoutWidget = QWidget(self.centralwidget)
        self.vertLayoutWidget.setMaximumSize(QSize(250, 1200))
        self.verticalLayout = QVBoxLayout(self.vertLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label_3 = QComboBox(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.label_3.addItem("")
        for i in range(0, len(Allegiance_List)):
            self.label_3.addItem(Allegiance_List[i])

        self.displaying = QComboBox(self.centralwidget)
        self.displaying.setObjectName("displaying")
        self.displaying.addItem("")
        for i in soldier_display:
            self.displaying.addItem(i)

        self.button_edit_xml = QPushButton(self.centralwidget)
        self.button_edit_xml.setObjectName("button_edit_xml")
        self.button_edit_xml.setText("Edit Object XML")

        self.button_edit_base_xml = QPushButton(self.centralwidget)
        self.button_edit_base_xml.setObjectName("saver")
        self.button_edit_base_xml.setText("Edit Weapons XML")

        self.button_edit_bullet_xml = QPushButton(self.centralwidget)
        self.button_edit_bullet_xml.setObjectName("bullet_xml")
        self.button_edit_bullet_xml.setText("Edit Bullet XML")

        self.button_homing = QPushButton(self.centralwidget)
        self.button_homing.setObjectName("homing")
        self.button_homing.setText("Homing")

        
        self.gridLayout = QFormLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.addRow(self.label_2)
        self.gridLayout.addRow(self.label_3)
        self.gridLayout.addRow(self.displaying)
        self.gridLayout.addRow(self.button_edit_xml)
        self.gridLayout.addRow(self.button_edit_base_xml)
        self.gridLayout.addRow(self.button_edit_bullet_xml)
        self.gridLayout.addRow(self.button_homing)
        self.gridLayout.addRow("Health",self.health)
        self.gridLayout.addRow("Base Flags",self.base_flags)
        self.gridLayout.addRow(self.label_object_id)
        self.gridLayout.addRow(self.label_model_name)
        self.gridLayout.addRow(self.label_5)


        self.verticalLayout.addLayout(self.gridLayout)

        spacerItem1 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout.addWidget(self.vertLayoutWidget)

        self.entity_list_widget = BWEntityListWidget(self.centralwidget)
        self.entity_list_widget.setMaximumSize(QSize(200, 16777215))
        self.entity_list_widget.setObjectName("entity_list_widget")
        self.horizontalLayout.addWidget(self.entity_list_widget)

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 820, 29))
        self.menubar.setObjectName("menubar")
        self.file_menu = QMenu(self.menubar)
        self.file_menu.setObjectName("menuLoad")



        self.file_load_action = QAction("Load", self)
        self.file_load_action.triggered.connect(self.button_load_level)
        self.file_menu.addAction(self.file_load_action)
        self.file_save_action = QAction("Save", self)
        self.file_save_action.triggered.connect(self.button_save_level)
        self.file_menu.addAction(self.file_save_action)

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.file_menu.menuAction())

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        self.file_menu.setTitle(_translate("MainWindow", "File"))

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)


    bw_gui = EditorMainWindow()

    bw_gui.show()
    err_code = app.exec()
    traceback.print_exc()
    sys.exit(err_code)
