from OCC.Core.gp import gp_Vec, gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Display.SimpleGui import init_display
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from math import pi,sin
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism


def create_i_section(length, width, depth, flange_thickness, web_thickness):
    """
    Create an I-section CAD model with the specified dimensions.
    
    Parameters:
      - length: Extrusion length (X-direction)
      - width:  Flange width (Y-direction)
      - depth:  Cross-sectional height (Z-direction)
      - flange_thickness: thickness of the top and bottom flanges
      - web_thickness:    thickness of the web
    """
    web_height = depth - 2 * flange_thickness

    # Bottom flange
    bottom_flange = BRepPrimAPI_MakeBox(length, width, flange_thickness).Shape()

    # Top flange (translated upward)
    top_flange = BRepPrimAPI_MakeBox(length, width, flange_thickness).Shape()
    trsf_top = gp_Trsf()
    trsf_top.SetTranslation(gp_Vec(0, 0, depth - flange_thickness))
    top_flange_transform = BRepBuilderAPI_Transform(top_flange, trsf_top, True).Shape()

    # Web (positioned between flanges)
    web_box = BRepPrimAPI_MakeBox(length, web_thickness, web_height).Shape()
    trsf_web = gp_Trsf()
    trsf_web.SetTranslation(gp_Vec(0, (width - web_thickness) / 2, flange_thickness))
    web_transform = BRepBuilderAPI_Transform(web_box, trsf_web, True).Shape()

    # Fuse flanges + web
    i_section_solid = BRepAlgoAPI_Fuse(bottom_flange, top_flange_transform).Shape()
    i_section_solid = BRepAlgoAPI_Fuse(i_section_solid, web_transform).Shape()

    return i_section_solid

def create_plate(plate_length, plate_width, plate_thickness):
    """
    Create a rectangular plate along the X-axis:
      X = plate_length, Y = plate_width, Z = plate_thickness.
    """
    plate = BRepPrimAPI_MakeBox(plate_length, plate_width, plate_thickness).Shape()
    return plate

def create_lace(p1,p2,p3,p4):
    """
    Given points create a polygon , Then make a prism with thickness out of it
    """
    # First, translate the plate.
    
    polygon = BRepBuilderAPI_MakePolygon()
    polygon.Add(p1)
    polygon.Add(p2)
    polygon.Add(p3)
    polygon.Add(p4)
    polygon.Close() 
    face = BRepBuilderAPI_MakeFace(polygon.Wire()).Shape()
    thickness = 8.0
    extrusion_vector = gp_Vec(0, 0, thickness)
    solid = BRepPrimAPI_MakePrism(face, extrusion_vector).Shape()
    return solid
def generate_lace_points(start_height , end_height, vertical_laces_gap , 
                         lace_width , i_sec_width , horizontal_width ):
    arr=[]
    currentend=start_height+vertical_laces_gap
    currentstart=start_height
    
    while currentend<end_height:
        p1=gp_Pnt(currentstart,0,0)
        p2=gp_Pnt(currentstart+lace_width,0,0)
        p3=gp_Pnt(currentend,i_sec_width,0)
        p4=gp_Pnt(currentend-lace_width,i_sec_width,0)
        arr.append((p1,p2,p3,p4))
        p1=gp_Pnt(currentstart,i_sec_width,192)
        p2=gp_Pnt(currentstart+lace_width,i_sec_width,192)
        p3=gp_Pnt(currentend,0,192)
        p4=gp_Pnt(currentend-lace_width,0,192)
        arr.append((p1,p2,p3,p4))
        #horizontal bar
        if currentend+horizontal_width<end_height:
            p1=gp_Pnt(currentend,0,0)
            p2=gp_Pnt(currentend+horizontal_width,0,0)
            p3=gp_Pnt(currentend+horizontal_width,i_sec_width,0)
            p4=gp_Pnt(currentend,i_sec_width,0)
            arr.append((p1,p2,p3,p4))
            p1=gp_Pnt(currentend,0,192)
            p2=gp_Pnt(currentend+horizontal_width,0,192)
            p3=gp_Pnt(currentend+horizontal_width,i_sec_width,192)
            p4=gp_Pnt(currentend,i_sec_width,192)
            arr.append((p1,p2,p3,p4))
            
        currentstart=currentend+horizontal_width
        currentend=currentstart+vertical_laces_gap
    arr2=[]
    for points in arr:
        solid = create_lace(points[0],points[1],points[2],points[3])
        arr2.append(solid)
    # for points in arr:
    #     for i, pt in enumerate(points, start=1):
    #         print(f"Point {i}: X = {pt.X()}, Y = {pt.Y()}, Z = {pt.Z()}")
    return arr2
if __name__ == "__main__":
    # === 1) Define Overall Dimensions ===
    total_height    = 6100.0
    plate_x_length  = 300.0           # Each end plate occupies 300 mm in X.
    column_length   = total_height - 2 * plate_x_length  # = 5500 mm (clear I-section length)
    i_section_width = 100.0           # Y
    i_section_depth = 200.0           # Z

    # Plate dimensions (for end plates, for reference)
    plate_y_width   = 430.0
    plate_z_thick   = 10.0

    # I-section thickness parameters
    flange_thickness = 10.0
    web_thickness    = 6.0

    # === 2) Create I-sections (clear length = 5500 mm) ===
    i_section_1 = create_i_section(column_length,
                                   i_section_width,
                                   i_section_depth,
                                   flange_thickness,
                                   web_thickness)

    i_section_2 = create_i_section(column_length,
                                   i_section_width,
                                   i_section_depth,
                                   flange_thickness,
                                   web_thickness)

    # Each I-section is 100 mm wide, so if outer-to-outer is 450 mm,
    # we translate the second by (450 - 100) = 350 mm in Y.
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 350.0, 0))
    i_section_2_transformed = BRepBuilderAPI_Transform(i_section_2, trsf, True).Shape()

    # === 3) Create One Plate Shape (300 mm in X, 430 mm in Y, 10 mm in Z) ===
    plate_shape = create_plate(plate_x_length, plate_y_width, plate_z_thick)

    # === 4) Bottom Plates (two parallel plates) ===
    bottom_trsf_front = gp_Trsf()
    bottom_trsf_front.SetTranslation(gp_Vec(0, 10, 0))
    bottom_plate_front = BRepBuilderAPI_Transform(plate_shape, bottom_trsf_front, True).Shape()

    bottom_trsf_back = gp_Trsf()
    bottom_trsf_back.SetTranslation(gp_Vec(0, 10, 190))
    bottom_plate_back = BRepBuilderAPI_Transform(plate_shape, bottom_trsf_back, True).Shape()

    # === 5) Top Plates (two parallel plates) ===
    top_trsf_front = gp_Trsf()
    top_trsf_front.SetTranslation(gp_Vec(5200, 10, 0))
    top_plate_front = BRepBuilderAPI_Transform(plate_shape, top_trsf_front, True).Shape()

    top_trsf_back = gp_Trsf()
    top_trsf_back.SetTranslation(gp_Vec(5200, 10, 190))
    top_plate_back = BRepBuilderAPI_Transform(plate_shape, top_trsf_back, True).Shape()

    # solid = create_lace(p1,p2,p3,p4)
    #Create Lace
    solids = generate_lace_points(300,5200,450,70.71,450,100)

    
    
        # === 7) Visualization ===
    display, start_display, add_menu, add_function_to_menu = init_display()
    white = Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB)
    black = Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB)
    gray  = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB) 
    brown = Quantity_Color(0.59,0.29,0,Quantity_TOC_RGB)
    display.View.SetBackgroundColor(white)
    display.DisplayShape(i_section_1, update=True, color=brown)
    display.DisplayShape(i_section_2_transformed, update=True, color=brown)
    display.DisplayShape(bottom_plate_front, update=True, color=brown)
    display.DisplayShape(bottom_plate_back, update=True, color=brown)
    display.DisplayShape(top_plate_front, update=True, color=brown)
    display.DisplayShape(top_plate_back, update=True, color=brown)
    for solid in solids :
        display.DisplayShape(solid,update=True,color=brown)
    # display.DisplayShape(solid, update=True)
    
    # display.DisplayShape(lace1, update=True, color=black)

    display.FitAll()
    start_display()
