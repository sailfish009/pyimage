import sys
import os.path
import datetime
import dearpygui.dearpygui as dpg
import numpy as np
import pandas as pd
from PIL import Image

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PROGRAM_TITLE = 'Simple Image Viewer'
PROGRAM_W = 1000
PROGRAM_H = 900
WINDOW_TAG1 = "Main Window"
TEXTURE_TAG = 'image_texture'
IMAGE_TAG = 'image_plot'
LIST_TAG = 'file_list'
SCALE=0.7
IMAGE_SIZE = 999 
NEW_SIZE = IMAGE_SIZE*SCALE # 699

def load_image_data(file_path):
  if not os.path.isfile(file_path):
    return None
  try:
    image = Image.open(file_path).convert("RGBA")
  except Exception as e:
    return None
  image = image.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)
  flipped_image = image.transpose(method=Image.FLIP_TOP_BOTTOM)
  # image_data = np.array(image).flatten() / 255.0  # normal image
  image_data = np.array(flipped_image).flatten() / 255.0  # inverted
  return image_data

dpg.create_context()

RECT_COORDS = {"p1": [50.0, 50.0], "p2": [200.0, 200.0]}
RESIZE_ACTIVE = [True]
RESIZE_THRESHOLD = 10.0

def load_image_window(file_path):
  global TEXTURE_TAG, IMAGE_TAG, LIST_TAG, RECT_COORDS
  image_data = load_image_data(file_path)
  if image_data is not None:
    dpg.delete_item(TEXTURE_TAG)
    TEXTURE_TAG = dpg.generate_uuid()
    with dpg.texture_registry():
      dpg.add_static_texture(width=IMAGE_SIZE, height=IMAGE_SIZE, default_value=image_data, tag=TEXTURE_TAG)    

    dpg.delete_item(LIST_TAG)
    LIST_TAG = dpg.generate_uuid()
    dpg.delete_item(IMAGE_TAG)
    IMAGE_TAG = dpg.generate_uuid()

    with dpg.plot(parent=WINDOW_TAG1, height=NEW_SIZE, width=NEW_SIZE, tag=IMAGE_TAG):
      dpg.add_plot_axis(dpg.mvXAxis, tag="X Axis")
      with dpg.plot_axis(dpg.mvYAxis, tag="Y Axis", invert=True):
        dpg.add_image_series(TEXTURE_TAG, [0.0, 0.0], [IMAGE_SIZE, IMAGE_SIZE])
        dpg.add_draw_layer(parent=IMAGE_TAG, tag="plot_layer")
        with dpg.draw_layer(parent=IMAGE_TAG, tag="draw_rect"):
          dpg.draw_rectangle(RECT_COORDS["p1"], RECT_COORDS["p2"], color=[255, 0, 0, 255], thickness=2, tag="drag_rect")

    dpg.set_axis_limits("X Axis", 0, IMAGE_SIZE)
    dpg.set_axis_limits("Y Axis", 0, IMAGE_SIZE)
    files = ['_']
    files.extend([f for f in os.listdir('.') if os.path.isfile(f) and f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    dpg.add_listbox(files, parent=WINDOW_TAG1, pos=[NEW_SIZE+10,20], tag=LIST_TAG, width=300, num_items=41, callback=listbox_callback)


def listbox_callback(sender, app_data):
  print(f"sender is: {sender}")
  print(f"app_data is: {app_data}")
  load_image_window(app_data)

def update_rectangle(sender, app_data):
  mouse_pos = dpg.get_plot_mouse_pos()
  if  dpg.is_mouse_button_down(dpg.mvMouseButton_Left):
    if RESIZE_ACTIVE[0]: 
      dist = ((mouse_pos[0] - RECT_COORDS["p2"][0]) ** 2 + (mouse_pos[1] - RECT_COORDS["p2"][1]) ** 2) ** 0.5
      if dist < RESIZE_THRESHOLD :
        RECT_COORDS["p2"] = list(mouse_pos)
        dpg.configure_item("drag_rect", pmin=RECT_COORDS["p1"], pmax=RECT_COORDS["p2"])
    else:
      rect_x = abs(RECT_COORDS["p1"][0] - RECT_COORDS["p2"][0])
      rect_y = abs(RECT_COORDS["p1"][1] - RECT_COORDS["p2"][1])
      RECT_COORDS["p1"] = [mouse_pos[0], mouse_pos[1]]
      RECT_COORDS["p2"] = [mouse_pos[0]+rect_x, mouse_pos[1]+rect_y]
      dpg.configure_item("drag_rect", pmin=RECT_COORDS["p1"], pmax=RECT_COORDS["p2"])

with dpg.texture_registry(show=True):
  texture_data = []
  for i in range(0, IMAGE_SIZE * IMAGE_SIZE):
    texture_data.append(255 / 255)
    texture_data.append(255 / 255)
    texture_data.append(255 / 255)
    texture_data.append(255 / 255)
  dpg.add_static_texture(IMAGE_SIZE, IMAGE_SIZE, texture_data, tag=TEXTURE_TAG)
    
with dpg.handler_registry():
  dpg.add_mouse_down_handler(callback=update_rectangle, button=dpg.mvMouseButton_Left)

with dpg.window(tag=WINDOW_TAG1, pos=[0,0],width=PROGRAM_W, height=PROGRAM_H):
  with dpg.plot(height=NEW_SIZE, width=NEW_SIZE, tag=IMAGE_TAG):
    dpg.add_plot_axis(dpg.mvXAxis, tag="X Axis")
    with dpg.plot_axis(dpg.mvYAxis, tag="Y Axis", invert=True):
      dpg.add_image_series(TEXTURE_TAG, [0.0, 0.0], [IMAGE_SIZE, IMAGE_SIZE])
      dpg.add_draw_layer(parent=IMAGE_TAG, tag="plot_layer")
      with dpg.draw_layer(parent=IMAGE_TAG, tag="draw_rect"):
        dpg.draw_rectangle(RECT_COORDS["p1"], RECT_COORDS["p2"], color=[255, 0, 0, 255], thickness=2, tag="drag_rect")
            
  dpg.set_axis_limits("X Axis", 0, IMAGE_SIZE)
  dpg.set_axis_limits("Y Axis", 0, IMAGE_SIZE)
  files = ['_']
  files.extend([f for f in os.listdir('.') if os.path.isfile(f) and f.lower().endswith(('.png', '.jpg', '.jpeg'))])
  dpg.add_listbox(files, tag=LIST_TAG, pos=[NEW_SIZE+10,20], width=300, num_items=41, callback=listbox_callback)

dpg.create_viewport(title=PROGRAM_TITLE, x_pos=0, y_pos=0, width=PROGRAM_W, height=PROGRAM_H)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()