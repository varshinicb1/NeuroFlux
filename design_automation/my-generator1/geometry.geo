// NeuroFlux AFPM parametric geometry for Gmsh handoff.
SetFactory("OpenCASCADE");
r_in = 0.07250000;
r_out = 0.12500000;
stator_thickness = 0.03000000;
magnet_thickness = 0.00450000;
air_gap = 0.00250000;
pole_count = 16;
slot_count = 48;
Cylinder(1) = {0, 0, -stator_thickness/2, 0, 0, stator_thickness, r_out};
Cylinder(2) = {0, 0, -stator_thickness/2, 0, 0, stator_thickness, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
Physical Volume("stator_active_region") = {1};
Mesh.CharacteristicLengthMin = 0.00125000;
Mesh.CharacteristicLengthMax = 0.01050000;
