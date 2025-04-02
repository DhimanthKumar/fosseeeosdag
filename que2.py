from OCC.Core.gp import gp_Vec, gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Display.SimpleGui import init_display
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from math import pi, sin
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism

# === Define Constants ===
TOTAL_HEIGHT = 12200.0
PLATE_X_LENGTH = 300.0
COLUMN_LENGTH = TOTAL_HEIGHT - 2 * PLATE_X_LENGTH
I_SECTION_WIDTH = 100.0
I_SECTION_DEPTH = 200.0
PLATE_Y_WIDTH = 430.0
PLATE_Z_THICK = 10.0
FLANGE_THICKNESS = 10.0
WEB_THICKNESS = 6.0
I_SECTION_TRANSLATION_Y = 350.0
PLATE_TRANSLATION_X = TOTAL_HEIGHT - 3*PLATE_X_LENGTH
VERTICAL_LACES_GAP = 450
HORIZONTAL_WIDTH = 100
LACE_height = HORIZONTAL_WIDTH /(sin(pi/4))
LACE_THICKNESS = 8.0
LACE_HEIGHT = 200
I_SECTION_OUTER_WIDTH=450
PLATE_Y_TRANS=(I_SECTION_OUTER_WIDTH-PLATE_Y_WIDTH)/2
LACE_WIDTH=430
def create_i_section(length, width, depth, flange_thickness, web_thickness):
    web_height = depth - 2 * flange_thickness
    bottom_flange = BRepPrimAPI_MakeBox(length, width, flange_thickness).Shape()
    top_flange = BRepPrimAPI_MakeBox(length, width, flange_thickness).Shape()
    trsf_top = gp_Trsf()
    trsf_top.SetTranslation(gp_Vec(0, 0, depth - flange_thickness))
    top_flange_transform = BRepBuilderAPI_Transform(top_flange, trsf_top, True).Shape()
    web_box = BRepPrimAPI_MakeBox(length, web_thickness, web_height).Shape()
    trsf_web = gp_Trsf()
    trsf_web.SetTranslation(gp_Vec(0, (width - web_thickness) / 2, flange_thickness))
    web_transform = BRepBuilderAPI_Transform(web_box, trsf_web, True).Shape()
    i_section_solid = BRepAlgoAPI_Fuse(bottom_flange, top_flange_transform).Shape()
    i_section_solid = BRepAlgoAPI_Fuse(i_section_solid, web_transform).Shape()
    return i_section_solid


def create_plate(plate_length, plate_width, plate_thickness):
    return BRepPrimAPI_MakeBox(plate_length, plate_width, plate_thickness).Shape()


def create_lace(p1, p2, p3, p4):
    polygon = BRepBuilderAPI_MakePolygon()
    for pt in [p1, p2, p3, p4]:
        polygon.Add(pt)
    polygon.Close()
    face = BRepBuilderAPI_MakeFace(polygon.Wire()).Shape()
    extrusion_vector = gp_Vec(0, 0, LACE_THICKNESS)
    return BRepPrimAPI_MakePrism(face, extrusion_vector).Shape()


def generate_lace_points(start_height, end_height, vertical_laces_gap, lace_height, i_sec_width, horizontal_width):
    arr = []
    currentend = start_height + vertical_laces_gap
    currentstart = start_height
    LACE_START_Y=(I_SECTION_OUTER_WIDTH-LACE_WIDTH)/2
    LACE_END_Y=(I_SECTION_OUTER_WIDTH-LACE_WIDTH)/2 + LACE_WIDTH
    print(horizontal_width)
    while currentend < end_height:
        p1 = gp_Pnt(currentstart, LACE_START_Y, -LACE_THICKNESS)
        p2 = gp_Pnt(currentstart + lace_height, LACE_START_Y, -LACE_THICKNESS)
        p3 = gp_Pnt(currentend, LACE_END_Y, -LACE_THICKNESS)
        p4 = gp_Pnt(currentend - lace_height, LACE_END_Y, -LACE_THICKNESS)
        arr.append((p1, p2, p3, p4))
        p1 = gp_Pnt(currentstart, LACE_END_Y, LACE_HEIGHT)
        p2 = gp_Pnt(currentstart + lace_height, LACE_END_Y, LACE_HEIGHT)
        p3 = gp_Pnt(currentend, LACE_START_Y, LACE_HEIGHT)
        p4 = gp_Pnt(currentend - lace_height, LACE_START_Y, LACE_HEIGHT)
        arr.append((p1, p2, p3, p4))
        if currentend + horizontal_width < end_height:
            p1 = gp_Pnt(currentend, LACE_START_Y, -LACE_THICKNESS)
            p2 = gp_Pnt(currentend + horizontal_width, LACE_START_Y, -LACE_THICKNESS)
            p3 = gp_Pnt(currentend + horizontal_width, LACE_END_Y, -LACE_THICKNESS)
            p4 = gp_Pnt(currentend, LACE_END_Y, -LACE_THICKNESS)
            arr.append((p1, p2, p3, p4))
            p1 = gp_Pnt(currentend, LACE_START_Y, LACE_HEIGHT)
            p2 = gp_Pnt(currentend + horizontal_width, LACE_START_Y, LACE_HEIGHT)
            p3 = gp_Pnt(currentend + horizontal_width, LACE_END_Y, LACE_HEIGHT)
            p4 = gp_Pnt(currentend, LACE_END_Y, LACE_HEIGHT)
            arr.append((p1, p2, p3, p4))
        currentstart = currentend + horizontal_width
        currentend = currentstart + vertical_laces_gap
    return [create_lace(*points) for points in arr]


def translate_plate(plate, x, y, z):
    trsf_plate = gp_Trsf()
    trsf_plate.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(plate, trsf_plate, True).Shape()


i_section_1 = create_i_section(COLUMN_LENGTH, I_SECTION_WIDTH, I_SECTION_DEPTH, FLANGE_THICKNESS, WEB_THICKNESS)
i_section_2 = create_i_section(COLUMN_LENGTH, I_SECTION_WIDTH, I_SECTION_DEPTH, FLANGE_THICKNESS, WEB_THICKNESS)
trsf = gp_Trsf()
trsf.SetTranslation(gp_Vec(0, I_SECTION_TRANSLATION_Y, 0))
i_section_2_transformed = BRepBuilderAPI_Transform(i_section_2, trsf, True).Shape()
plate_shape = create_plate(PLATE_X_LENGTH, PLATE_Y_WIDTH, PLATE_Z_THICK)

bottom_plate_front = translate_plate(plate_shape, 0, PLATE_Y_TRANS, -PLATE_Z_THICK)
bottom_plate_back = translate_plate(plate_shape, 0, PLATE_Y_TRANS, I_SECTION_DEPTH)
top_plate_front = translate_plate(plate_shape, PLATE_TRANSLATION_X, PLATE_Y_TRANS, -PLATE_Z_THICK)
top_plate_back = translate_plate(plate_shape, PLATE_TRANSLATION_X, PLATE_Y_TRANS, I_SECTION_DEPTH)

solids = generate_lace_points(PLATE_X_LENGTH, TOTAL_HEIGHT-3*PLATE_X_LENGTH, VERTICAL_LACES_GAP, LACE_height, 450, HORIZONTAL_WIDTH)

# === Visualization ===
display, start_display, _, _ = init_display()
white = Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB)
brown = Quantity_Color(0.59, 0.29, 0, Quantity_TOC_RGB)
display.View.SetBackgroundColor(white)
display.DisplayShape(i_section_1, update=True, color=brown)
display.DisplayShape(i_section_2_transformed, update=True, color=brown)
display.DisplayShape(bottom_plate_front, update=True, color=brown)
display.DisplayShape(bottom_plate_back, update=True, color=brown)
display.DisplayShape(top_plate_front, update=True, color=brown)
display.DisplayShape(top_plate_back, update=True, color=brown)
for solid in solids:
    display.DisplayShape(solid, update=True, color=brown)
display.FitAll()
start_display()
