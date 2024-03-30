#entity_set_val -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bw_gui_prototype.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

import traceback
import itertools
import gzip
import re
from copy import copy, deepcopy
import os
from os import path
from timeit import default_timer
from math import atan2, degrees, radians, sin, cos
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QRect, QMetaObject, QCoreApplication, QPoint,Qt
from PyQt5.QtWidgets import (QWidget, QMainWindow, QFileDialog, QStackedLayout,QDialog,
                             QSpacerItem, QLabel, QListWidget, QFormLayout,QPushButton,
                             QSizePolicy, QVBoxLayout, QHBoxLayout,QScrollArea, QDockWidget,
                             QComboBox, QGridLayout, QMenuBar, QMenu, QAction, QApplication,
                             QStatusBar, QLineEdit)
'''from PyQt5.QtWidgets import (QWidget, QMainWindow, QFileDialog,
                             QSpacerItem, QLabel, QPushButton, QSizePolicy, QVBoxLayout,
                             QHBoxLayout,QScrollArea, QGridLayout, QFormLayout, QStackedLayout,
                             QMenuBar, QMenu, QAction, QApplication, QStatusBar, QLineEdit)
'''
from PyQt5.QtGui import QMouseEvent
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

from res_tools.bw_archive_base import BWArchiveBase

from lib.bw_read_xml import BattWarsLevel, BattWarsObject
from custom_widgets import (BWEntityEntry, BWEntityListWidget, BWMapViewer, BWPassengerWindow, BWEntityXMLEditor, MenuDontClose,
                            catch_exception,display_string,flag_data2, flag_data1, target_data2,
                            soldier_display, Allegiance_List, test_data, test_data2, dam_list1, dam_list2, bullet_flags_o, bullet_flags2,target_data_o,
                            SHOW_TERRAIN_LIGHT, SHOW_TERRAIN_FLAT, SHOW_TERRAIN_NO_TERRAIN, SHOW_TERRAIN_REGULAR)


from lib.helper_functions import (calc_zoom_in_factor, calc_zoom_out_factor,
                                  get_default_path, set_default_path, update_mapscreen,
                                  bw_coords_to_image_coords, image_coords_to_bw_coords,
                                  entity_get_army, entity_get_icon_type, entity_get_model,
                                  object_set_position, object_get_position, get_position_attribute, get_type,
                                  parse_bruce,parse_terrain_to_image, get_water_height,
                                  get_key,get_value,entity_set_list,entity_set_list2,
                                  entity_set_val)
#Weapons data
BW_LEVEL = "BW level files (*_level.xml *_level.xml.gz)"
BW_COMPRESSED_LEVEL = "BW compressed level files (*_level.xml.gz)"
modual = 0


        
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

        self.resetting = False

        self.entity_list_widget.currentItemChanged.connect(self.action_listwidget_change_selection)
        self.button_zoom_in.pressed.connect(self.zoom_in)
        self.button_zoom_out.pressed.connect(self.zoom_out)
        self.button_remove_entity.pressed.connect(self.remove_position)
        self.button_move_entity.pressed.connect(self.move_entity)
        self.button_clone_entity.pressed.connect(self.action_clone_entity)
        self.button_show_passengers.pressed.connect(self.action_passenger_window)
        self.button_edit_xml.pressed.connect(self.action_open_xml_editor)
        self.button_edit_base_xml.pressed.connect(self.action_open_basexml_editor)
        self.lineedit_angle.editingFinished.connect(self.action_lineedit_changeangle)
        self.search.returnPressed.connect(self.action_search)


        self.bw_map_screen.mouse_clicked.connect(self.get_position)
        self.bw_map_screen.entity_clicked.connect(self.entity_position)
        self.bw_map_screen.mouse_dragged.connect(self.mouse_move)
        self.bw_map_screen.mouse_released.connect(self.mouse_release)
        self.bw_map_screen.mouse_wheel.connect(self.mouse_wheel_scroll_zoom)


        status = self.statusbar
        self.bw_map_screen.setMouseTracking(True)

        self.passenger_window = BWPassengerWindow()
        self.passenger_window.passengerlist.currentItemChanged.connect(self.passengerwindow_action_choose_entity)

        self.xmlobject_textbox = BWEntityXMLEditor()
        self.xmlobject_textbox.button_xml_savetext.pressed.connect(self.xmleditor_action_save_object_xml)
        self.xmlobject_textbox.triggered.connect(self.action_open_xml_editor_unlimited)


        self.basexmlobject_textbox = BWEntityXMLEditor(windowtype="XML Base Object")
        self.basexmlobject_textbox.button_xml_savetext.pressed.connect(self.xmleditor_action_save_base_object_xml)
        self.basexmlobject_textbox.triggered.connect(self.action_open_xml_editor_unlimited)

        self.types_visible = {}
        self.terrain_image = None

        #weapons functions

        self.model_dict = {}
        self.back_dict = {}
        self.full_model_dict = {}
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
        self.table_val = 0
        self.obj_typing = 0
        self.seat_table = []

        self.current_entity = None
        self.current_weapon = None
        self.entity_list_widget2.currentItemChanged.connect(self.action_listwidget_change_selection2) 
        self.button_edit_xml2.pressed.connect(self.action_open_xml_editor)
        self.bullet_l.editingFinished.connect(self.action_change_bullet)
        self.flags_l.editingFinished.connect(self.action_change_flags)
        self.flags_L.currentIndexChanged.connect(self.action_change_flag_box)
        self.pref_L.currentIndexChanged.connect(self.action_change_pref_box)
        self.pref_l.editingFinished.connect(self.action_change_pref)
        self.ammo_l.editingFinished.connect(self.action_change_ammo)
        self.bull_flag.editingFinished.connect(self.action_change_bull_flag)
        self.bull_L.currentIndexChanged.connect(self.action_change_bull_flag_box)
        self.bull_model.currentIndexChanged.connect(self.action_change_bull_model)
        #self.backpack.currentIndexChanged.connect(self.action_change_backpack)
        self.full_model.currentIndexChanged.connect(self.action_change_full_model)
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
        self.button_edit_weap_xml.pressed.connect(self.action_open_weapons_editor)
        self.button_edit_bullet_xml.pressed.connect(self.action_edit_bullet_xml)
        self.button_homing.pressed.connect(self.action_homing)

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
        self.current_entity = None
        self.current_weapon = None

        self.moving = False

        self.entity_list_widget.clearSelection()
        self.entity_list_widget.clear()

        self.entity_list_widget2.clearSelection()
        self.entity_list_widget2.clear()

        self.bw_map_screen.reset()
        self.clear_visibility_toggles()

        for window in (self.passenger_window, self.xmlobject_textbox, self.basexmlobject_textbox):
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

                        #self.level.remove_object(xmlnode.get("id"))
                        #self.level.add_object(xmlnode)
                        self.level.save_object(xmlnode.get("id"),xmlnode)

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
        if self.level is not None and self.bw_map_screen.current_entity is not None:
            obj = self.level.obj_map[self.bw_map_screen.current_entity]
            if not obj.has_attr("mBase"):
                pass
            else:
                baseobj = self.level.obj_map[obj.get_attr_value("mBase")]
                #self.basexmlobject_textbox.set_title(baseobj.id)
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

    def action_open_xml_editor(self): #Need to modify this for Weapons
        global modual
        if modual == 0:
            if self.level is not None and self.bw_map_screen.current_entity is not None:
                entityobj = self.level.obj_map[self.bw_map_screen.current_entity]
                self.open_xml_editor(objectid=entityobj.id)

                update_mapscreen(self.bw_map_screen, self.level.obj_map[entityobj.id])
                self.bw_map_screen.update()
        else:
            if self.level is not None and self.current_weapon is not None:
                entityobj = self.level.obj_map[self.current_weapon]
                self.open_xml_editor(objectid=entityobj.id)

    def xmleditor_action_save_object_xml(self):
        input()
        self.statusbar.showMessage("Saving object changes...")
        try:
            xmlnode = self.xmlobject_textbox.get_content()
            #assert self.bw_map_screen.current_entity == self.xmlobject_textbox.entity
            assert self.xmlobject_textbox.entity == xmlnode.get("id") or xmlnode.get("id") not in self.level.obj_map

            if self.passenger_window.isVisible():
                self.passenger_window.close()

            if self.xmlobject_textbox.entity != xmlnode.get("id"): #changing the ID
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

    def action_clone_entity(self):
        entities = []
        if self.bw_map_screen.current_entity is not None:
            entities.append(self.bw_map_screen.current_entity)
        elif len(self.bw_map_screen.selected_entities) > 0:
            entities.extend(self.bw_map_screen.selected_entities.keys())

        if len(entities) > 0:
            dont_clone = {}
            for entity in entities:
                obj = self.level.obj_map[entity]
                if obj.has_attr("mPassenger"):
                    passengers = obj.get_attr_elements("mPassenger")
                    for passenger in passengers:
                        if passenger != "0":
                            dont_clone[passenger] = True
            select = []
            for entity in entities:
                if entity in dont_clone:
                    continue

                obj = self.level.obj_map[entity]

                xml_node = deepcopy(obj._xml_node)
                try:
                    cloned_id = self.level.generate_unique_id(entity)
                    xml_node.set("id", cloned_id)
                    self.level.add_object(xml_node)

                    bw_x, bw_y, angle = object_get_position(self.level, cloned_id)
                    x, y = bw_coords_to_image_coords(bw_x, bw_y)

                    self.add_item_sorted(cloned_id)

                    self.bw_map_screen.add_entity(x, y, cloned_id, obj.type)

                    clonedobj = self.level.obj_map[cloned_id]
                    select.append(cloned_id)
                    update_mapscreen(self.bw_map_screen, clonedobj)
                    if clonedobj.has_attr("mPassenger"):
                        orig_x = bw_x
                        orig_y = bw_y
                        passengers = clonedobj.get_attr_elements("mPassenger")

                        passengers_added = []

                        for i, passenger in enumerate(passengers):
                            if passenger != "0":
                                obj = self.level.obj_map[passenger]
                                xml_node = deepcopy(obj._xml_node)

                                clonedpassenger_id = self.level.generate_unique_id(passenger)
                                xml_node.set("id", clonedpassenger_id)
                                #print("orig passenger: {0}, new passenger: {1}, alreadyexists: {2}".format(
                                #    passenger, clonedpassenger_id, clonedpassenger_id in self.level.obj_map
                                #))
                                #print(type(passenger), type(clonedpassenger_id))

                                self.level.add_object(xml_node)
                                #x, y = object_get_position(self.level, newid)
                                x = orig_x + (i+1)*8
                                y = orig_y + (i+1)*8
                                #print(orig_x, orig_y, x, y)
                                object_set_position(self.level, clonedpassenger_id, x, y)
                                x, y = bw_coords_to_image_coords(x, y)

                                self.add_item_sorted(clonedpassenger_id)
                                self.bw_map_screen.add_entity(x, y, clonedpassenger_id, obj.type)
                                update_mapscreen(self.bw_map_screen, self.level.obj_map[clonedpassenger_id])
                                passengers_added.append(passenger)
                                clonedobj.set_attr_value("mPassenger", clonedpassenger_id, i)
                                select.append(clonedpassenger_id)
                        #print("passengers added:", passengers_added)
                    self.bw_map_screen.selected_entities = {}
                    if len(select) == 1:
                        ent = select[0]
                        self.set_entity_text(ent)
                        self.bw_map_screen.choose_entity(ent)
                    else:
                        for ent in select:
                            self.bw_map_screen.selected_entities[ent] = True
                        self.set_entity_text_multiple(self.bw_map_screen.selected_entities)
                    self.bw_map_screen.update()
                except:
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

    #weapons functions

    def action_open_weapons_editor(self):
        if self.level is not None and self.current_weapon is not None and self.label_2.currentText() != "":
            entityobj = self.level.obj_map[self.label_2.currentText()]
            self.open_xml_editor(entityobj.id,100,100)

    def action_edit_bullet_xml(self):
        if self.level is not None and self.current_weapon is not None and self.label_2.currentText() != "":
            entityobj = self.level.obj_map[self.bullet_l.text()]
            self.open_xml_editor(entityobj.id, 200,200)
    def action_change_alleg(self):
        entity_set_val(self.level, self.current_weapon,"mArmy",self.label_3.currentText())

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
            print('seating %s' % seat)
            entity_set_val(self.level, self.bullet,"mModel",seat)

    '''def action_change_backpack(self):
        if self.setup == 0 and self.label_2.currentText() != "":
            seat = get_value(self.backpack.currentText(),self.back_dict)
            entity_set_val(self.level, self.entity,"mBkPackModel",seat)'''


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
        if self.label_2.currentText() != "" and self.setup == 0:
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

    def action_lifetime(self):
        entity_set_val(self.level, self.bullet,"mMaxLifeTime",self.lifetime.text())

    def action_bounce(self):
        entity_set_val(self.level, self.bullet,"mBounceFactor",self.bounce.text())

    def action_dam_list(self):
        if self.setup == 0:
            if self.label_2.currentText() != "" and self.dam_list.currentIndex() != 0:
                obj = self.level.obj_map[self.label_2.currentText()]
                d = self.bull_dam.currentIndex()
                self.bull_dam.setItemText(d,self.dam_list.currentText())
                entity_set_list2(self.level, self.bullet,"mDamageType",self.dam_list.currentText(),d)
                self.bulllist2[d] = self.dam_list.currentText()

    def action_change_display(self):
        mod = self.displaying.currentText()
        print(mod)
        if mod != "":
            obj = self.level.obj_map[self.current_weapon]
            if obj.has_attr("mSeatData"):
                dumped = obj.get_attr_elements("mSeatData")
                seat = self.level.obj_map[dumped[self.label_2.currentIndex()]]
                if seat.has_attr("DisplayType"):
                    entity_set_val(self.level, dumped[self.label_2.currentIndex()],"DisplayType",mod)
                    val = self.label_2.currentIndex()
                    self.seat_table[val] = mod
                    self.displaying.setItemText(0,mod)

    def action_change_full_model(self):
        if self.setup == 0:
            mod = self.full_model.currentText()
            if mod != "":
                obj = self.level.obj_map[self.current_weapon]
                if obj.has_attr("mpModel"):
                    seat = get_value(self.full_model.currentText(),self.full_model_dict)
                    print('seating %s' % seat)
                    entity_set_val(self.level, self.current_weapon,"mpModel",seat)
                    '''dumped = obj.get_attr_value("mpModel")
                    seat = self.level.obj_map[dumped]
                    if seat.has_attr("mName"):
                        seat = get_value(self.full_model.currentText(),self.full_model_dict)
                        print('seating %s' % seat)
                        entity_set_val(self.level, dumped,"mName",seat)
                        val = self.label_2.currentIndex()
                        self.seat_table[val] = mod
                        self.displaying.setItemText(0,mod)
                        print('phhhew!')
                        print('changed weapons model!')'''

    def action_open_table(self):
        '''if self.timestamp != os.path.getmtime(self.default_path):
            print('EEEEEEEEECCCK!!!!!!!')
            dlg = QDialog(self)
            dlg.setWindowTitle('Info') 
            dlg.exec()'''
        self.clear_functions()
        if self.label_2.currentText() == "":
            print('No Weapon!')
        else:
            try:
                self.setup = 1
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
            except:
                print('Error in code')
            if obj.has_attr("Flags"):
                self.flags = format(obj.get_attr_value("Flags"))
                self.flags_l.setText(self.flags)
                seat = flag_data.get(self.flags_l.text(), None)
                self.flags_L.setCurrentIndex(0)
                if seat != None:
                    self.flags_L.setItemText(0,format(seat))
                else:
                    flag_data.update({self.flags: self.icon_type.text()+self.label_3.currentText()})
                    self.flags_L.addItem(flag_data[self.flags])
                    self.flags_L.setItemText(0,format(self.icon_type.text()))
                    seat2 = test_data.get(self.flags_l.text(), None)
                    if seat2 == None:
                        test_data.update({self.flags: self.icon_type.text()+self.label_3.currentText()})
            '''if obj.has_attr("mBkPackModel"):
                seat = format(obj.get_attr_value("mBkPackModel"))
                self.backpack.setCurrentIndex(0)
                if seat == 0:
                    print('no backpack')
                else:
                    flag_data.update({self.flags: self.label_5.text()+self.label_3.currentText()})
                    self.flags_L.addItem(flag_data[self.flags])
                    self.flags_L.setItemText(0,format(self.label_5.text()))
                    seat2 = self.back_dict.get(str(self.backpack.currentText()), None)
                    if seat2 == None:
                        self.backpack.setCurrentIndex(seat2)'''
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
            self.setup = 0

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
    def clear_functions(self):
        self.setup = 1
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
        self.pref_L.setCurrentIndex(0)
        self.flags_L.setItemText(0,"")
        self.flags_L.setCurrentIndex(0)
        self.bull_L.setItemText(0,"")
        self.bull_L.setCurrentIndex(0)
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
        self.setup = 0

    def load_misc(self):
        global flag_data, bullet_flags, target_data
        Allegiance_List = []
        self.label_3.clear()
        self.label_2.clear()
        self.bull_model.clear()
        #self.backpack.clear()
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
















            

    def get_entity_item_pos(self, entityid):
        for i in range(self.entity_list_widget.count()):
            item = self.entity_list_widget.item(i)

            if item.xml_ref == entityid:
                return i

        return None

    def action_passenger_window(self):
        #if self.passenger_window.isVisible()
        print("window is visible: ", self.passenger_window.isVisible())
        #self.passenger_window.reset()

        if not self.passenger_window.isVisible():
            self.passenger_window.destroy()
            self.passenger_window = BWPassengerWindow()
            self.passenger_window.passengerlist.currentItemChanged.connect(self.passengerwindow_action_choose_entity)
            self.passenger_window.show()

        self.passenger_window.activateWindow()
        if self.bw_map_screen.current_entity is not None:
            self.passenger_window.reset()
            entityobj = self.level.obj_map[self.bw_map_screen.current_entity]
            self.passenger_window.set_title(entityobj.id)
            if entityobj.has_attr("mPassenger"):
                for i, passenger in enumerate(entityobj.get_attr_elements("mPassenger")):
                    if passenger in self.level.obj_map:
                        passengerobj = self.level.obj_map[passenger]
                        list_item_name = "{0}[{1}]".format(passenger, passengerobj.type)
                    elif passenger == "0":
                        list_item_name = "{0}<none>".format(passenger)
                    else:
                        list_item_name = "{0}<missing>".format(passenger)
                    self.passenger_window.add_passenger(list_item_name, passenger)
            self.passenger_window.update()

    def passengerwindow_action_choose_entity(self, current, previous):
        try:
            if current is not None and current.xml_ref in self.level.obj_map:
                self.set_entity_text(current.xml_ref)
                self.bw_map_screen.choose_entity(current.xml_ref)
            elif current is not None:
                self.statusbar.showMessage("No such entity: {0}".format(current.xml_ref), 1000*2)
        except:
            traceback.print_exc()

    def move_entity(self):
        if not self.dragging:
            if not self.moving:
                self.moving = True
                currtext = self.button_move_entity.text()
                self.button_move_entity.setText("Stop [Move Entity]")
            else:
                self.moving = False

                currtext = "Move Entity"
                self.button_move_entity.setText(currtext)

    def button_load_level(self):
        try:
            print("ok", self.default_path)
            self.xmlPath = ""
            filepath, choosentype = QFileDialog.getOpenFileName(
                self, "Open File",
                self.default_path,
                BW_LEVEL+";;"+BW_COMPRESSED_LEVEL+";;All files (*)")
            print("doooone")
            if filepath:
                print("resetting")
                self.reset()
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
                print('Loading Objects')
                self.timestamp = os.path.getmtime(filepath)
                with file_open(filepath, "rb") as f:
                    try:
                        self.level = BattWarsLevel(f)
                        self.default_path = filepath
                        set_default_path(filepath)
                        self.setup_visibility_toggles()

                        for obj_id, obj in sorted(self.level.obj_map.items(),
                                                  key=lambda x: get_type(x[1].type)+x[1].type+x[1].id):
                            if obj.has_attr("mArmy") or obj.has_attr("mWeaponLoads"):
                                if obj.has_attr("mArmy"):
                                    seat = format(obj.get_attr_value("mArmy"))
                                    if seat != None and seat not in Allegiance_List:
                                        Allegiance_List.append(seat)
                                        self.label_3.addItem(seat)
                                if obj.has_attr("mpModel"):
                                    seat = format(obj.get_attr_value("mpModel"))
                                    if seat != "0":
                                        second = seat
                                        seat = self.level.obj_map[seat]
                                        if seat.has_attr("mName"):
                                            main = seat.get_attr_value("mName")
                                            if main not in self.full_model_dict:
                                                self.full_model_dict[main] = second
                                if obj.has_attr("mBkPackModel"):
                                    seat = format(obj.get_attr_value("mBkPackModel"))
                                    if seat != "0":
                                        second = seat
                                        seat = self.level.obj_map[seat]
                                        if seat.has_attr("mName"):
                                            main = seat.get_attr_value("mName")
                                            if main not in self.back_dict:
                                                self.back_dict[main] = second
                                if obj.has_attr("mDisplayNameStringID"):
                                    seat = format(obj.get_attr_value("mDisplayNameStringID"))
                                    if seat != "0":
                                        second = get_value(seat,display_string)
                                        if second == "0":
                                            print(seat)
                                            print('New item!!!!!!!!!!!!!!!')
                                item = BWEntityEntry(obj_id, "{0}[{1}]".format(obj_id, obj.type))
                                self.entity_list_widget2.addItem(item)
                            if obj.return_type("cNodeHierarchyResource"):
                                #print(obj.get_attr_value("mName"))
                                pass
                            if obj.return_type("sProjectileBase"):
                                seat = obj.get_attr_value("mModel")
                                if seat != "0":
                                    try:
                                        second = seat
                                        seat = self.level.obj_map[seat]
                                        if seat.has_attr("mName"):
                                            main = seat.get_attr_value("mName")
                                            if main not in self.model_dict:
                                                self.model_dict[main] = second
                                    except:
                                        print('Error loading model data')
                            if get_position_attribute(obj) is None:
                                continue
                            #if not obj.has_attr("Mat"):
                            #    continue
                            x, y, angle = object_get_position(self.level, obj_id)
                            assert type(x) != str
                            x, y = bw_coords_to_image_coords(x, y)

                            item = BWEntityEntry(obj_id, "{0}[{1}]".format(obj_id, obj.type))
                            self.entity_list_widget.addItem(item)

                            self.bw_map_screen.add_entity(x, y, obj_id, obj.type, update=False)
                            #if obj.type == "cMapZone":
                            update_mapscreen(self.bw_map_screen, obj)
                        self.bull_model.addItem("")
                        self.bull_model.addItems(self.model_dict.keys())
                        self.full_model.addItems(self.full_model_dict.keys())
                        #self.backpack.addItems(self.back_dict.keys())
                        print("ok")
                        path_parts = path.split(filepath)
                        #print("doing", obj_id)

                        print("ok")
                        self.bw_map_screen.update()
                        path_parts = path.split(filepath)
                        self.default_directory = path_parts[0]
                        self.leveling = path_parts[1]
                        self.setWindowTitle("BW-MapEdit - {0}".format(path_parts[-1]))
                        if self.autload.isChecked():
                            print('loading terrain')
                            self.button_terrain_autoload_action()
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

    def entity_position(self, event, entity):
        try:
            # Make it possible to select objects in move mode, but don't make it too easy to lose
            # a selection.
            if not (self.moving and len(self.bw_map_screen.selected_entities) > 1):
                print("got entity:",entity, self.bw_map_screen.entities[entity][2])
                print(entity_get_model(self.level, entity))
                self.set_entity_text(entity)
                self.bw_map_screen.choose_entity(entity)
                pos = self.get_entity_item_pos(entity)
                print("searching:",pos)
                try:
                    self.entity_list_widget.select_item(pos)
                except:
                    traceback.print_exc()
                self.bw_map_screen.selected_entities = {}

                self.bw_map_screen.update()

        except:
            traceback.print_exc()

    def remove_position(self):
        #self.bw_map_screen.entities.pop()
        try:
            # Remove the entity from the map, the list widget and the level data
            self.deleting_item = True
            entities = []
            if self.bw_map_screen.current_entity is not None:
                entities.append(self.bw_map_screen.current_entity)
            elif len(self.bw_map_screen.selected_entities) > 0:
                entities.extend(self.bw_map_screen.selected_entities.keys())
                self.bw_map_screen.selected_entities = {}
                self.set_entity_text_multiple(self.bw_map_screen.selected_entities)
            if len(entities) > 0:
                for entity in entities:
                    pos = self.get_entity_item_pos(entity)
                    item = self.entity_list_widget.takeItem(pos)
                    assert item.xml_ref == entity
                    #self.entity_list_widget.clearSelection()
                    self.entity_list_widget.clearFocus()
                    self.entity_list_widget.removeItemWidget(item)
                    self.level.remove_object(entity)
                    self.bw_map_screen.remove_entity(entity)

                self.bw_map_screen.update()
        except:
            traceback.print_exc()
            raise

    #@catch_exception
    def get_position(self, event):
        self.dragging = True
        self.last_x = event.x()
        self.last_y = event.y()
        self.dragged_time = default_timer()

        mouse_x = event.x()/self.bw_map_screen.zoom_factor
        mouse_y = event.y()/self.bw_map_screen.zoom_factor

        if event.buttons() == QtCore.Qt.LeftButton:

            if not self.moving:
                self.bw_map_screen.set_selectionbox_start((event.x(), event.y()))
            else:
                if self.bw_map_screen.current_entity is not None:
                    newx, newy = image_coords_to_bw_coords(mouse_x, mouse_y)
                    object_set_position(self.level, self.bw_map_screen.current_entity,
                                        newx, newy)
                    self.bw_map_screen.move_entity(self.bw_map_screen.current_entity,
                                                   mouse_x, mouse_y)
                    self.set_entity_text(self.bw_map_screen.current_entity)

                    update_mapscreen(self.bw_map_screen, self.level.obj_map[self.bw_map_screen.current_entity])

                elif len(self.bw_map_screen.selected_entities) > 0:
                    for entity in self.bw_map_screen.selected_entities:
                        first_entity = entity
                        break
                    #first_entity = self.bw_map_screen.selected_entities.keys()[0]
                    x, y, entitytype, metadata = self.bw_map_screen.entities[first_entity]
                    startx = endx = x
                    starty = endy = y

                    for entity in self.bw_map_screen.selected_entities:
                        x, y, dontneed, dontneed = self.bw_map_screen.entities[entity]
                        if x < startx:
                            startx = x
                        if x > endx:
                            endx = x
                        if y < starty:
                            starty = y
                        if y > endy:
                            endy = y
                    middle_x = (startx+endx) / 2
                    middle_y = (starty+endy) / 2

                    delta_x = mouse_x - middle_x
                    delta_y = mouse_y - middle_y

                    for entity in self.bw_map_screen.selected_entities:
                        x, y, dontneed, dontneed = self.bw_map_screen.entities[entity]

                        newx, newy = image_coords_to_bw_coords(x+delta_x, y+delta_y)
                        object_set_position(self.level, entity,
                                            newx, newy)
                        self.bw_map_screen.move_entity(entity,
                                                       x+delta_x, y+delta_y)
                        #self.set_entity_text(self.bw_map_screen.current_entity)

                        update_mapscreen(self.bw_map_screen, self.level.obj_map[entity])

            self.bw_map_screen.update()

    @catch_exception
    def mouse_move(self, event):
        x, y = image_coords_to_bw_coords(event.x()/self.bw_map_screen.zoom_factor,
                                         event.y()/self.bw_map_screen.zoom_factor)
        self.statusbar.showMessage("x: {0} y: {1}".format(round(x, 5), round(y, 5)))

        if self.dragging and default_timer() - self.dragged_time > 0.1:
            if event.buttons() == QtCore.Qt.RightButton:
                delta_x = (event.x()-self.last_x)/8
                delta_y = (event.y()-self.last_y)/8
                #print("hi",event.x(), event.y())

                vertbar = self.scrollArea.verticalScrollBar()
                horizbar = self.scrollArea.horizontalScrollBar()

                vertbar.setSliderPosition(vertbar.value()-delta_y)
                horizbar.setSliderPosition(horizbar.value()-delta_x)

            elif event.buttons() == QtCore.Qt.LeftButton:
                self.bw_map_screen.set_selectionbox_end((event.x(), event.y()))
                if len(self.bw_map_screen.selected_entities) == 1:
                    for xy in self.bw_map_screen.selected_entities:
                        xy = xy
                    if self.current_entity != xy or self.bw_map_screen.current_entity is None:
                        self.current_entity = xy
                        self.select_entity(xy)
                else:
                    self.bw_map_screen.choose_entity(None)
                    if len(self.bw_map_screen.selected_entities) > 0 or self.bw_map_screen.current_entity is None:
                        self.set_entity_text_multiple(self.bw_map_screen.selected_entities)
                self.bw_map_screen.update()

    def select_entity(self,entity):
        self.set_entity_text(entity)
        self.bw_map_screen.choose_entity(entity)
        pos = self.get_entity_item_pos(entity)
        try:
            self.entity_list_widget.select_item(pos)
        except:
            traceback.print_exc()
        self.bw_map_screen.selected_entities = {}

        self.bw_map_screen.update()
    def mouse_release(self, event):
        self.dragging = False
        if self.bw_map_screen.selectionbox_end is not None:
            self.bw_map_screen.clear_selection_box()
            self.bw_map_screen.update()


    def set_entity_text_multiple(self, entities):
        self.label_object_id.setText("{0} objects selected".format(len(entities)))
        MAX = 15
        listentities = [self.level.obj_map[x].name for x in sorted(entities.keys())][0:MAX]
        listentities.sort()
        if len(entities) > MAX:
            listentities.append("... and {0} more".format(len(entities) - len(listentities)))
        self.label_position.setText("\n".join(listentities[:5]))
        self.label_model_name.setText("\n".join(listentities[5:10]))
        self.label_4.setText("\n".join(listentities[10:]))#15]))
        self.label_5.setText("")#("\n".join(listentities[12:16]))

    def set_entity_text(self, entityid):
        global modual
        if modual == 0:
            try:
                obj = self.level.obj_map[entityid]
                if obj.has_attr("mBase"):
                    base = self.level.obj_map[obj.get_attr_value("mBase")]
                    self.label_object_id.setText("{0}\n[{1}]\nBase: {2}\n[{3}]".format(
                        entityid, obj.type, base.id, base.type))
                else:
                    self.label_object_id.setText("{0}\n[{1}]".format(entityid, obj.type))
                self.label_model_name.setText("Model: {0}".format(entity_get_model(self.level, entityid)))
                x, y, angle = object_get_position(self.level, entityid)
                self.label_position.setText("x: {0}\ny: {1}".format(x, y))
                self.lineedit_angle.setText(str(round(angle,2)))
                self.label_4.setText("Army: {0}".format(entity_get_army(self.level, entityid)))
                if not obj.has_attr("mPassenger"):
                    self.label_5.setText("Icon Type: \n{0}".format(entity_get_icon_type(self.level, entityid)))
                else:

                    passengers = 0
                    for passenger in obj.get_attr_elements("mPassenger"):
                        if passenger != "0":
                            passengers += 1
                    self.label_5.setText("Icon Type: \n{0}\n\nPassengers: {1}".format(
                        entity_get_icon_type(self.level, entityid), passengers))
            except:
                traceback.print_exc()
        else:
            try:
                self.clear_functions()
                self.obj_typing = 0
                seat = 0
                go_go = 0
                self.seat_table = []
                self.label_2.clear()
                self.health.clear()
                self.entity = entityid
                self.full_model.setItemText(0,"")
                self.full_model.setCurrentIndex(0)
                #self.backpack.setItemText(0,"")
                #self.backpack.setCurrentIndex(0)
                obj = self.level.obj_map[entityid]
                if obj.has_attr("mBase"):
                    base = self.level.obj_map[obj.get_attr_value("mBase")]
                    self.label_object_id2.setText("{0}\n[{1}]\nBase: {2}\n[{3}]".format(
                        entityid, obj.type, base.id, base.type))
                else:
                    self.label_object_id2.setText("{0}[{1}]".format(entityid, obj.type))
                self.label_model_name2.setText("Model: {0}".format(entity_get_model(self.level, entityid)))
                seat = obj.get_attr_value("mDisplayNameStringID")
                seat = display_string.get(seat, seat)
                self.string_name.setText("String: {0}".format(seat))
                #seat = obj.get_attr_value("mDisplayFullNameStringID")
                #seat = display_string.get(seat, seat)
                #self.string_name2.setText("String: {0}".format(seat))
                self.label_3.setItemText(0,format(obj.get_attr_value("mArmy")))
                self.label_3.setCurrentIndex(0)
                self.obj_typing = obj.type
                if not obj.has_attr("mPassenger"):
                    test = entity_get_icon_type(self.level, entityid,self.game_type)
                    print(test)
                    self.icon_type.setText(format(test))
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

                if obj.has_attr("mpModel"):
                    typ = obj.get_attr_value("mpModel")
                    if typ == "0":
                        self.full_model.setCurrentIndex(0)
                    else:
                        self.model = self.level.obj_map[typ]
                        if self.model.has_attr("mName"):
                            typ = self.model.get_attr_value("mName")
                            f = self.full_model.findText(typ)
                            if f == -1:
                                self.full_model.setCurrentIndex(0)
                            else:
                                self.full_model.setCurrentIndex(f)

                '''if obj.has_attr("mBkPackModel"):
                    typ = obj.get_attr_value("mBkPackModel")
                    if typ == "0":
                        self.backpack.setCurrentIndex(0)
                    else:
                        self.back_mod = self.level.obj_map[typ]
                        if self.back_mod.has_attr("mName"):
                            typ = self.back_mod.get_attr_value("mName")
                            f = self.backpack.findText(typ)
                            if f == -1:
                                self.backpack.setCurrentIndex(0)
                            else:
                                self.backpack.setCurrentIndex(f)'''

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
                print('not viable')
                traceback.print_exc()

    def action_listwidget_change_selection2(self, current, previous):
        if not self.resetting and current is not None:
            self.setup = 1
            print("hi", current.text(), current.xml_ref)
            self.current_weapon = current.xml_ref
            self.set_entity_text(current.xml_ref)
                
    def action_listwidget_change_selection(self, current, previous):
        #QtWidgets.QListWidgetItem.
        if not self.resetting and current is not None:
            print("hi", current.text(), current.xml_ref)

            self.set_entity_text(current.xml_ref)
            self.bw_map_screen.choose_entity(current.xml_ref)

            posx, posy, typename, metadata = self.bw_map_screen.entities[current.xml_ref]
            zf = self.bw_map_screen.zoom_factor
            try:
                if not self.deleting_item:
                    x_margin = min(100, 50*zf)
                    y_margin = min(100, 50*zf)
                    self.scrollArea.ensureVisible(int(posx*zf), int(posy*zf),
                                                  xMargin=int(x_margin), yMargin=int(y_margin))
                else:
                    self.deleting_item = False
            except:
                traceback.print_exc()

    def zoom_out(self, noslider=False):

        horizbar = self.scrollArea.horizontalScrollBar()
        vertbar = self.scrollArea.verticalScrollBar()

        if horizbar.maximum() > 0:
            widthratio = horizbar.value()/horizbar.maximum()
        else:
            widthratio = 0

        if vertbar.maximum() > 0:
            heightratio = vertbar.value()/vertbar.maximum()
        else:
            heightratio = 0

        #oldzf = self.bw_map_screen.zoom_factor / (0.1+1)
        #diff = oldzf - self.bw_map_screen.zoom_factor
        zf = self.bw_map_screen.zoom_factor
        self.bw_map_screen.zoom(calc_zoom_out_factor(zf))#diff)

        #
        if not noslider:
            horizbar.setSliderPosition(int(horizbar.maximum()*widthratio))
            vertbar.setSliderPosition(int(vertbar.maximum()*heightratio))
            self.bw_map_screen.update()

        self.statusbar.showMessage("Zoom: {0}x".format(self.bw_map_screen.zoom_factor))

    def zoom_in(self, noslider=False):
        horizbar = self.scrollArea.horizontalScrollBar()
        vertbar = self.scrollArea.verticalScrollBar()

        if horizbar.maximum() > 0:
            widthratio = horizbar.value()/horizbar.maximum()
        else:
            widthratio = 0

        if vertbar.maximum() > 0:
            heightratio = vertbar.value()/vertbar.maximum()
        else:
            heightratio = 0

        zf = self.bw_map_screen.zoom_factor
        self.bw_map_screen.zoom(calc_zoom_in_factor(zf))#zf)

        #
        if not noslider:
            horizbar.setSliderPosition(int(horizbar.maximum()*widthratio))
            vertbar.setSliderPosition(int(vertbar.maximum()*heightratio))
            self.bw_map_screen.update()
        self.statusbar.showMessage("Zoom: {0}x".format(self.bw_map_screen.zoom_factor))

    @catch_exception
    def mouse_wheel_scroll_zoom(self, wheel_event):

        wheel_delta = wheel_event.angleDelta().y()
        zf = self.bw_map_screen.zoom_factor
        norm_x = wheel_event.x()/zf
        norm_y = wheel_event.y()/zf
        if wheel_delta > 0:
            if zf <= 10:
                self.zoom_in(True)

                zf = self.bw_map_screen.zoom_factor

                xmargin = self.scrollArea.viewport().width()//2 - 200
                ymargin = self.scrollArea.viewport().height()//2 - 200
                self.scrollArea.ensureVisible(int(norm_x*zf), int(norm_y*zf), int(xmargin), int(ymargin))
                self.bw_map_screen.update()
            else:
                self.zoom_in()
        elif wheel_delta < 0:
            self.zoom_out()



    def action_lineedit_changeangle(self):
        if not self.resetting and self.bw_map_screen.current_entity is not None:
            current = self.bw_map_screen.current_entity
            currx, curry, angle = object_get_position(self.level, current)

            newangle = self.lineedit_angle.text().strip()
            print(newangle, newangle.isdecimal())
            try:
                angle = float(newangle)
                object_set_position(self.level, current, currx, curry, angle=angle)
                currentobj = self.level.obj_map[current]
                update_mapscreen(self.bw_map_screen, currentobj)
                self.bw_map_screen.update()
            except:
                traceback.print_exc()

    def action_search(self):
        if not self.resetting:
            searchans = self.search.text().strip()
            print('searching')
            try:
                for x in range(self.entity_list_widget.count()-1):
                    if self.entity_list_widget.item(x).xml_ref == searchans:
                        self.current_entity = searchans
                        self.set_entity_text(searchans)
                        self.bw_map_screen.current_entity = searchans
                        self.bw_map_screen.choose_entity(searchans)
                        pl= self.entity_list_widget.findItems(searchans,QtCore.Qt.MatchContains)
                        self.entity_list_widget.setCurrentItem(pl[0])
                        break
                self.search.clear()
                    
            except:
                traceback.print_exc()
                
    def button_weapon(self):
        global modual
        if self.stackedLayout.currentIndex() == 0:
            self.stackedLayout.setCurrentIndex(1)
            modual = 1
            if self.bw_map_screen.current_entity != None:
                obj = self.level.obj_map[self.bw_map_screen.current_entity]
                if obj.has_attr("mBase"):
                    base = obj.get_attr_value("mBase")
                pl = self.entity_list_widget2.findItems(base,QtCore.Qt.MatchContains)
                if len(pl) > 0:
                    self.entity_list_widget2.setCurrentItem(pl[0])
        else:
            self.stackedLayout.setCurrentIndex(0)
            modual = 0

    def button_weapon2(self):
        type_list = []
        type_list2 = []
        print(len(self.level.obj_map))
        try:
            
            for xy in self.level.obj_map:
                obj = self.level.obj_map[xy]
                #print(obj.type)
                if obj.type not in type_list:
                    type_list.append(obj.type)
                    type_list2.append(0)
                    
                for i in range(0,len(type_list)):
                    if type_list[i] == obj.type:
                        type_list2[i]+=1
     
            for i in range(0,len(type_list)):
                print(type_list2[i]," : ",type_list[i])
            print("Entities : ",self.entity_list_widget.count())
            self.bw_map_screen
            #print(type_list2)
        
        except:
            traceback.print_exc()      
            
                
        
    def button_terrain_load_action(self):
        try:
            print("ok", self.default_path)
            filepath, choosentype = QFileDialog.getOpenFileName(
                self, "Open File",
                self.default_path,
                "BW terrain files (*.out *out.gz);;All files (*)")
            print("doooone")
            if filepath:
                if filepath.endswith(".gz"):
                    file_open = gzip.open
                else:
                    file_open = open
                print(filepath)
                with file_open(filepath, "rb") as f:
                    try:
                        terrain = BWArchiveBase(f)
                        if self.level is not None:
                            waterheight = get_water_height(self.level)
                        else:
                            waterheight = None

                        image, light_image,image_flat = parse_terrain_to_image(terrain, waterheight)
                        self.bw_map_screen.set_terrain(image, light_image,image_flat)
                    except:
                        traceback.print_exc()
        except:
            traceback.print_exc()

    def button_terrain_autoload_action(self):
        contents = os.listdir(self.default_directory)
        for xy in contents:
            if ".out" in xy:
                answer = xy.split(".out",1)[0]
                question = self.leveling.split("_Level.",1)[0]
                if answer == question:
                    self.default_path = self.default_directory +"/" + xy   
                    if self.default_path.endswith(".gz"):
                        add = "res.gz"
                        file_open = gzip.open
                    else:
                        add = "res"
                        file_open = open
                    filepath = self.default_path
                    print(filepath)
                    try:
                        with file_open(filepath, "rb") as f:
                            try:
                                terrain = BWArchiveBase(f)
                                if self.level is not None:
                                    waterheight = get_water_height(self.level)
                                    print(waterheight)
                                else:
                                    waterheight = None

                                image, light_image, flat_image = parse_terrain_to_image(terrain, waterheight)
                                self.bw_map_screen.set_terrain(image, light_image,flat_image)
                                break
                            except:
                                traceback.print_exc()
                    except:
                        traceback.print_exc()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(820, 760)
        MainWindow.setMinimumSize(QSize(720, 560))
        MainWindow.setWindowTitle("BW-MapEdit")
        #MainWindow.setWindowTitle("Nep-Nep")

        

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.page1 = QWidget()
        self.page2 = QWidget()

        self.test = QWidget(self.centralwidget)
        self.test.setMaximumSize(QSize(250, 1200))
        self.testlay = QVBoxLayout(self.test)
        self.testlay.setObjectName("testlay")

        # Create the stacked layout
        self.stackedLayout = QStackedLayout(self.centralwidget)
        
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.horizontalLayout2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout2.setObjectName("horizontalLayout")

        self.horz_test = QWidget()
        self.horz_test.setLayout(self.horizontalLayout2)
        self.htest = QWidget()
        self.htest.setLayout(self.horizontalLayout)

        #self.stackedLayout.addWidget(self.page1)
        #self.stackedLayout.addWidget(self.page2)
        #self.centralwidget.setLayout(self.stackedLayout)
        #self.htest = QWidget()
        #self.htest.setLayout(self.horizontalLayout)
        #self.stackedLayout.addWidget(self.htest)
        self.stackedLayout.addWidget(self.htest)
        self.stackedLayout.addWidget(self.horz_test)
        self.centralwidget.setLayout(self.stackedLayout)

        #Did it!
        


        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)

        self.bw_map_screen = BWMapViewer(self.centralwidget)
        self.scrollArea.setWidget(self.bw_map_screen)
        self.horizontalLayout.addWidget(self.scrollArea)

        #self.horizontalLayout.addWidget(self.bw_map_screen)

        self.entity_list_widget = BWEntityListWidget(self.centralwidget)
        self.entity_list_widget.setMaximumSize(QSize(300, 16777215))
        self.entity_list_widget.setObjectName("entity_list_widget")
        self.horizontalLayout.addWidget(self.entity_list_widget)

        spacerItem = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontalLayout.addItem(spacerItem)

        self.vertLayoutWidget = QWidget(self.centralwidget)
        self.vertLayoutWidget.setMaximumSize(QSize(250, 1200))
        self.verticalLayout = QVBoxLayout(self.vertLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        #self.verticalLayout.
        self.button_clone_entity = QPushButton(self.centralwidget)
        self.button_clone_entity.setObjectName("button_clone_entity")
        self.verticalLayout.addWidget(self.button_clone_entity)

        self.button_remove_entity = QPushButton(self.centralwidget)
        self.button_remove_entity.setObjectName("button_remove_entity")
        self.verticalLayout.addWidget(self.button_remove_entity)

        self.button_move_entity = QPushButton(self.centralwidget)
        self.button_move_entity.setObjectName("button_move_entity")
        self.verticalLayout.addWidget(self.button_move_entity)

        self.button_show_passengers = QPushButton(self.centralwidget)
        self.button_show_passengers.setObjectName("button_move_entity")
        self.verticalLayout.addWidget(self.button_show_passengers)

        #weapons 2nd table

        
        # Create the first page

        #WEAPONS

        '''self.page1 = QWidget()
        self.page1Layout = QFormLayout()
        self.page1Layout.addRow("Name:", QLineEdit())
        self.page1Layout.addRow("Address:", QLineEdit())
        self.page1.setLayout(self.page1Layout)

        self.backpack = QComboBox(self.centralwidget)
        self.backpack.setObjectName("bull_dam")
        self.backpack.setToolTip("The infrantry's backpack")

        self.pg2hor = QHBoxLayout(self.centralwidget)
        self.pg2hor.setObjectName("pg2h")
        self.pg2horz = QWidget()
        self.pg2horz.setLayout(self.pg2hor)
        self.pg2hor.addWidget(self.page1)
        self.pg2hor.addWidget(self.backpack)
        # Add the combo box and the stacked layout to the top-level layout'''

        #self.stackedLayout.addWidget(self.pg2horz)

        #self.horizontalLayout.addLayout(self.stackedLayout) # two layers, centralwidget and acentralwidget
        #self.stackedLayout.addWidget(self.acentralwidget)

        self.indicator = QLabel(self.centralwidget)
        self.indicator.setObjectName("indicator")
        self.indicator.setText("")
        
        self.bullet_l = QLineEdit(self.centralwidget)
        self.bullet_l.setObjectName("Bullet")
        self.bullet_l.setToolTip("Just the ID for the bullet")
        self.bullet_l.setPlaceholderText("None")

        self.flags_l = QLineEdit(self.centralwidget)
        self.flags_l.setObjectName("Flag")
        self.flags_l.setToolTip("This is the general flags of the weapon, not the bullet flags\nnot sure exactly the purpose it serves yet")
        self.flags_l.setPlaceholderText("None")

        self.pref_l = QLineEdit(self.centralwidget)
        self.pref_l.setObjectName("Pref")
        self.pref_l.setToolTip("The target type that the weapons will prefer\nthis is used to determine what homing weapons will target")
        self.pref_l.setPlaceholderText("None")

        self.ammo_l = QLineEdit(self.centralwidget)
        self.ammo_l.setObjectName("Ammo")
        self.ammo_l.setToolTip("number of cartridges in the weapon")
        self.ammo_l.setPlaceholderText("None")

        self.range = QLineEdit(self.centralwidget)
        self.range.setObjectName("range")
        self.range.setToolTip("The range at which a unit can be targeted (?)")
        self.range.setPlaceholderText("None")

        self.reload = QLineEdit(self.centralwidget)
        self.reload.setObjectName("reload")
        self.reload.setToolTip("Plainly obvious")
        self.reload.setPlaceholderText("None")

        self.vel = QLineEdit(self.centralwidget)
        self.vel.setObjectName("vel")
        self.vel.setToolTip("The starting speed of the bullet")
        self.vel.setPlaceholderText("None")
        
        self.bull_flag = QLineEdit(self.centralwidget)
        self.bull_flag.setObjectName("bull")
        self.bull_flag.setToolTip("This affects how the bullet travels\ngunship missiles, bombs,bullets\nthis value is also necessary for homing")
        self.bull_flag.setPlaceholderText("None")

        self.bull_model = QComboBox(self.centralwidget)
        self.bull_model.setObjectName("bull_model")
        self.bull_flag.setToolTip("The model of the projectile")
        #self.bull_model.setPlaceholderText("None")

        self.bull_dam = QComboBox(self.centralwidget)
        self.bull_dam.setObjectName("bull_dam")
        self.bull_dam.setToolTip("What type of damage is dealt (can have up to four types)")
        self.bull_dam.addItem("")

        self.base_flags = QLineEdit(self.centralwidget)
        self.base_flags.setObjectName("base_flags")
        self.base_flags.setToolTip("Base Flags of the Unit")
        self.base_flags.setPlaceholderText("None")

        self.bull_dam2 = QLineEdit(self.centralwidget)
        self.bull_dam2.setObjectName("bull_dam2")
        self.bull_dam2.setToolTip("How much damage is dealt by the weapon IN the DAMAGE category")
        self.bull_dam2.setPlaceholderText("None")

        self.dam_list = QComboBox(self.centralwidget)
        self.dam_list.setObjectName("dam_list")
        self.dam_list.setToolTip("Changes the type of DAMAGE")
        self.dam_list.addItem("")


        self.pref_L = QComboBox(self.centralwidget)
        self.pref_L.setObjectName("pref_L")
        self.pref_L.setToolTip("The target type that the weapons will prefer\nthis is used to determine what homing weapons will target\n(2) refers to BW2")


        self.flags_L = QComboBox(self.centralwidget)
        self.flags_L.setObjectName("flags_L")
        self.flags_L.setToolTip("This is the general flags of the weapon, not the bullet flags\nnot sure exactly the purpose it serves yet")


        self.flags_L.addItem("")

        self.bull_L = QComboBox(self.centralwidget)
        self.bull_L.setObjectName("bull_L")
        self.bull_L.setToolTip("This affects how the bullet travels\ngunship missiles, bombs, bullets\nThis value is also necessary for homing")
        self.bull_L.addItem("")

        self.label_2 = QComboBox(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.label_2.setToolTip("The list of weapons of the unit\nFor infrantry the 2nd one is the player weapon")

        self.icon_type = QLabel(self.centralwidget)
        self.icon_type.setObjectName("label_5")
        self.icon_type.setText("Icon Type")

        self.health = QLineEdit(self.centralwidget)
        self.health.setObjectName("health")
        self.health.setToolTip("Health of the Unit")
        self.health.setPlaceholderText("None")

        self.label_object_id2 = QLabel(self.centralwidget)
        self.label_object_id2.setObjectName("label_object_id")
        self.label_object_id2.setText("Base")
        
        self.label_model_name2 = QLabel(self.centralwidget)
        self.label_model_name2.setObjectName("label_model_name")
        self.label_model_name2.setText("Model")

        self.string_name = QLabel(self.centralwidget)
        self.string_name.setObjectName("string_name")
        self.string_name.setText("String")

        self.string_name2 = QLabel(self.centralwidget)
        self.string_name2.setObjectName("string_name2")
        self.string_name2.setText("String2")

        self.dud = QLabel(self.centralwidget)
        self.dud.setObjectName("dud")

        self.accel = QLineEdit(self.centralwidget)
        self.accel.setObjectName("accel")
        self.accel.setToolTip("How fast the projectile accerlerates")
        self.accel.setPlaceholderText("None")

        self.drag = QLineEdit(self.centralwidget)
        self.drag.setObjectName("drag")
        self.drag.setToolTip("Inertia of the object\nresistance to acceleration")
        self.drag.setPlaceholderText("None")

        self.turnspeed = QLineEdit(self.centralwidget)
        self.turnspeed.setObjectName("turnspeed")
        self.turnspeed.setToolTip("How fast the homing projectile can change direction")
        self.turnspeed.setPlaceholderText("None")

        self.ttm = QLineEdit(self.centralwidget)
        self.ttm.setObjectName("ttm")
        self.ttm.setToolTip("The time until the homing\nprojectile starts turning")
        self.ttm.setPlaceholderText("None")

        self.lifetime = QLineEdit(self.centralwidget)
        self.lifetime.setObjectName("lifetime")
        self.lifetime.setToolTip("How long the projectile will last before vanishing")
        self.lifetime.setPlaceholderText("None")

        self.bounce = QLineEdit(self.centralwidget)
        self.bounce.setObjectName("bounce")
        self.bounce.setToolTip("Not sure yet")
        self.bounce.setPlaceholderText("None")


        self.spacerItem1 = QSpacerItem(10, 160, QSizePolicy.Expanding,   QSizePolicy.Minimum)
        self.spacerItem2 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        for label in (self.label_object_id2, self.label_model_name2,self.string_name,self.string_name2,self.icon_type):
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)


        #self.test = QWidget(self.centralwidget) way up there
        #self.test.setMaximumSize(QSize(250, 1200))
        #self.testlay = QVBoxLayout(self.test)
        #self.testlay.setObjectName("testlay")
        self.testlay.addItem(self.spacerItem1)
        self.testlay.addWidget(self.bull_L)
        self.testlay.addWidget(self.dam_list)

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
        self.horizontalLayout2.addWidget(self.tab1)
        self.horizontalLayout2.addWidget(self.tab2)
        
        self.vertLayoutWidget2 = QWidget(self.centralwidget)
        self.vertLayoutWidget2.setMaximumSize(QSize(250, 1200))
        self.verticalLayout2 = QVBoxLayout(self.vertLayoutWidget2)
        self.verticalLayout2.setObjectName("verticalLayout")

        self.label_3 = QComboBox(self.centralwidget)
        self.label_3.setObjectName("Allegiance")
        self.label_3.setToolTip("The faction the unit belongs to")
        self.label_3.addItem("")
        for i in range(0, len(Allegiance_List)):
            self.label_3.addItem(Allegiance_List[i])

        self.displaying = QComboBox(self.centralwidget)
        self.displaying.setObjectName("displaying")
        self.displaying.setToolTip("(For vehicles) how the grunt will be seen,\nstanding, sitting, etc")
        self.displaying.addItem("")
        for i in soldier_display:
            self.displaying.addItem(i)

        self.full_model = QComboBox(self.centralwidget)
        self.full_model.setObjectName("full_model")
        self.full_model.setToolTip("The model of the unit")
        self.full_model.addItem("")

        self.button_edit_xml2 = QPushButton(self.centralwidget)
        self.button_edit_xml2.setObjectName("button_edit_xml")
        self.button_edit_xml2.setText("Edit Object XML")

        self.button_edit_weap_xml = QPushButton(self.centralwidget)
        self.button_edit_weap_xml.setObjectName("saver")
        self.button_edit_weap_xml.setText("Edit Weapons XML")

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
        self.gridLayout.addRow(self.full_model)
        self.gridLayout.addRow(self.button_edit_xml2)
        self.gridLayout.addRow(self.button_edit_weap_xml)
        self.gridLayout.addRow(self.button_edit_bullet_xml)
        self.gridLayout.addRow(self.button_homing)
        self.gridLayout.addRow("Health",self.health)
        self.gridLayout.addRow("Base Flags",self.base_flags)
        self.gridLayout.addRow(self.label_object_id2)
        self.gridLayout.addRow(self.label_model_name2)
        self.gridLayout.addRow(self.icon_type)
        self.gridLayout.addRow(self.string_name)
        self.gridLayout.addRow(self.string_name2)


        self.verticalLayout2.addLayout(self.gridLayout)

        spacerItem1 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout2.addItem(spacerItem1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.verticalLayout2.addLayout(self.verticalLayout_2)
        self.horizontalLayout2.addWidget(self.vertLayoutWidget2)

        self.entity_list_widget2 = BWEntityListWidget(self.centralwidget)
        self.entity_list_widget2.setMaximumSize(QSize(200, 16777215))
        self.entity_list_widget2.setObjectName("entity_list_widget")
        self.entity_list_widget2.setToolTip("The list of all entities with weapons/seat data")
        self.horizontalLayout2.addWidget(self.entity_list_widget2)

        #END OF WEAPONS
        
        '''self.page2Layout = QFormLayout()
        self.page2Layout.addRow("Name:", QLineEdit())
        self.page2Layout.addRow("Address:", QLineEdit())
        
        self.page1.setLayout(self.horizontalLayout)
        self.page2.setLayout(self.page2Layout)'''



        #end of weapons table
        
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.button_zoom_in = QPushButton(self.centralwidget)
        self.button_zoom_in.setObjectName("button_zoom_in")
        self.gridLayout.addWidget(self.button_zoom_in, 0, 0, 0, 1)

        self.button_zoom_out = QPushButton(self.centralwidget)
        self.button_zoom_out.setObjectName("button_zoom_out")
        self.gridLayout.addWidget(self.button_zoom_out, 0, 1, 0, 1)

        self.button_edit_xml = QPushButton(self.centralwidget)
        self.button_edit_xml.setObjectName("button_edit_xml")

        self.button_edit_base_xml = QPushButton(self.centralwidget)
        self.button_edit_base_xml.setObjectName("button_edit_base_xml")


        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.button_edit_xml)
        self.verticalLayout.addWidget(self.button_edit_base_xml)

        spacerItem1 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")


        self.lineedit_angle = QLineEdit(self.centralwidget)
        self.lineedit_angle.setObjectName("lineedit_angle")
        self.lineedit_angle.setPlaceholderText("Angle")

        self.search = QLineEdit(self.centralwidget)
        self.search.setObjectName("search")
        self.search.setPlaceholderText("Search")

        self.label_object_id = QLabel(self.centralwidget)
        self.label_object_id.setObjectName("label_object_id")
         #TextSelectableByCursor

        self.label_position = QLabel(self.centralwidget)
        self.label_position.setObjectName("label_position")

        self.label_model_name = QLabel(self.centralwidget)
        self.label_model_name.setObjectName("label_model_name")

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")

        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")

        for label in (self.label_object_id, self.label_position, self.label_model_name, self.label_4, self.label_5):
            label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.verticalLayout_2.addWidget(self.search)
        self.verticalLayout_2.addWidget(self.lineedit_angle)
        self.verticalLayout_2.addWidget(self.label_object_id)
        self.verticalLayout_2.addWidget(self.label_position)
        self.verticalLayout_2.addWidget(self.label_model_name)
        self.verticalLayout_2.addWidget(self.label_4)
        self.verticalLayout_2.addWidget(self.label_5)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout.addWidget(self.vertLayoutWidget)

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 820, 29))
        self.menubar.setObjectName("menubar")
        self.file_menu = QMenu(self.menubar)
        self.file_menu.setObjectName("menuLoad")

        #setMenuBar(self.menu)

        self.file_load_action = QAction("Load", self)
        self.file_load_action.triggered.connect(self.button_load_level)
        self.file_menu.addAction(self.file_load_action)
        self.file_save_action = QAction("Save", self)
        self.file_save_action.triggered.connect(self.button_save_level)
        self.file_menu.addAction(self.file_save_action)

        self.visibility_menu = MenuDontClose(self.menubar)#QMenu(self.menubar)
        self.visibility_menu.setObjectName("visibility")

        #self.visibility_menu.addAction(self.toggle_action)
        self.visibility_actions = []

        self.terrain_menu = QMenu(self.menubar)
        self.terrain_menu.setObjectName("terrain")

        self.terrain_load_action = QAction("Load Terrain", self)
        self.terrain_load_action.triggered.connect(self.button_terrain_load_action)
        self.terrain_menu.addAction(self.terrain_load_action)
        self.terrain_autoload_action = QAction("Autoload Terrain", self)
        self.terrain_autoload_action.triggered.connect(self.button_terrain_autoload_action)
        self.terrain_menu.addAction(self.terrain_autoload_action)
        self.terrain_display_actions = []
        self.autload = QAction("Autload", self)
        self.autload.setCheckable(True)
        self.autload.setChecked(True)
        self.terrain_menu.addAction(self.autload)
        self.setup_terrain_display_toggles()
        

        #self.menuLoad_2 = QMenu(self.menubar)
        #self.menuLoad_2.setObjectName("menuLoad_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.file_menu.menuAction())
        #self.menubar.addAction(self.menuLoad_2.menuAction())
        self.menubar.addAction(self.visibility_menu.menuAction())
        self.menubar.addAction(self.terrain_menu.menuAction())
        self.weaponize = QAction("Weaponize",self)
        self.menubar.addAction(self.weaponize)
        self.weaponize.triggered.connect(self.button_weapon)
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)


    def make_terrain_toggle(self, show_mode):
        def terraintoggle(toggled):
            print("I am", show_mode, "and I was pressed")
            if toggled is True:
                for action, toggle, mode in self.terrain_display_actions:
                    if mode != show_mode:
                        action.setChecked(False)
                self.bw_map_screen.set_show_terrain_mode(show_mode)
            elif toggled is False:
                self.bw_map_screen.set_show_terrain_mode(SHOW_TERRAIN_NO_TERRAIN)
            else:
                print("This shouldn't be possible", toggled, type(toggled))
            self.bw_map_screen.update()
        return terraintoggle

    def setup_terrain_display_toggles(self):
        for mode, name in ((SHOW_TERRAIN_REGULAR, "Show Heightmap"),
                            (SHOW_TERRAIN_LIGHT, "Show Lightmap"),
                           (SHOW_TERRAIN_FLAT, "Show Flatmap")):
            toggle = self.make_terrain_toggle(mode)
            toggle_action = QAction(name, self)
            toggle_action.setCheckable(True)
            if mode == SHOW_TERRAIN_REGULAR:
                toggle_action.setChecked(True)
            else:
                toggle_action.setChecked(False)
            toggle_action.triggered.connect(toggle)
            self.terrain_menu.addAction(toggle_action)
            self.terrain_display_actions.append((toggle_action, toggle, mode))

    def clear_terrain_toggles(self):
        try:
            for action, func, mode in self.terrain_display_actions:
                self.terrain_menu.removeAction(action)
            self.terrain_display_actions = []
        except:
            traceback.print_exc()

    def make_toggle_function(self, objtype):
        def toggle(toggled):
            print("i was pressed")
            my_type = copy(objtype)
            self.types_visible[my_type] = toggled
            self.bw_map_screen.set_visibility(self.types_visible)
            self.bw_map_screen.update()
        return toggle

    def setup_visibility_toggles(self):
        for objtype in sorted(self.level.objtypes_with_positions):

            toggle = self.make_toggle_function(objtype)


            toggle_action = QAction(copy(objtype), self)
            toggle_action.setCheckable(True)
            toggle_action.setChecked(True)
            toggle_action.triggered.connect(toggle)
            self.types_visible[objtype] = True

            self.visibility_menu.addAction(toggle_action)
            self.visibility_actions.append((toggle_action, toggle))

        toggle_all = QAction("Toggle All", self)
        toggle_all.triggered.connect(self.toggle_visiblity_all)

        self.visibility_menu.addAction(toggle_all)
        self.visibility_actions.append((toggle_all, self.toggle_visiblity_all))

    def toggle_visiblity_all(self):
        for action, func in self.visibility_actions:
            if action.isCheckable():
                objtype = action.text()
                toggle = self.types_visible[objtype]
                self.types_visible[objtype] = not toggle
                action.setChecked(not toggle)
                self.bw_map_screen.set_visibility(self.types_visible)
        self.bw_map_screen.update()

    def clear_visibility_toggles(self):
        try:
            for action, func in self.visibility_actions:
                self.visibility_menu.removeAction(action)
            self.visibility_actions = []
            self.types_visible = {}
        except:
            traceback.print_exc()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        self.button_clone_entity.setText(_translate("MainWindow", "Clone Entity"))
        self.button_remove_entity.setText(_translate("MainWindow", "Delete Entity"))
        self.button_move_entity.setText(_translate("MainWindow", "Move Entity"))
        self.button_zoom_in.setText(_translate("MainWindow", "Zoom In"))
        self.button_zoom_out.setText(_translate("MainWindow", "Zoom Out"))
        self.button_show_passengers.setText(_translate("MainWindow", "Show Passengers"))
        self.button_edit_xml.setText("Edit Object XML")
        self.button_edit_base_xml.setText("Edit Base Object XML")

        self.label_model_name.setText(_translate("MainWindow", "TextLabel1"))
        self.label_object_id.setText(_translate("MainWindow", "TextLabel2"))
        self.label_position.setText(_translate("MainWindow", "TextLabel3"))
        self.label_4.setText(_translate("MainWindow", "TextLabel4"))
        self.label_5.setText(_translate("MainWindow", "TextLabel5"))
        self.file_menu.setTitle(_translate("MainWindow", "File"))
        self.visibility_menu.setTitle(_translate("MainWindow", "Visibility"))
        self.terrain_menu.setTitle("Terrain")

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)


    bw_gui = EditorMainWindow()

    bw_gui.show()
    err_code = app.exec()
    #traceback.print_exc()
    sys.exit(err_code)
