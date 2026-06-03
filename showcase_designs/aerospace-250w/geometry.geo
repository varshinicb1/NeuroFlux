// NeuroFlux AFPM parametric geometry for Gmsh handoff.
SetFactory("OpenCASCADE");
r_in = 0.03197250;
r_out = 0.05512500;
stator_thickness = 0.01323000;
magnet_thickness = 0.00400000;
air_gap = 0.00250000;
pole_count = 8;
slot_count = 24;
Cylinder(1) = {0, 0, -stator_thickness/2, 0, 0, stator_thickness, r_out};
Cylinder(2) = {0, 0, -stator_thickness/2, 0, 0, stator_thickness, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
Physical Volume("stator_active_region") = {1};
Mesh.CharacteristicLengthMin = 0.00125000;
Mesh.CharacteristicLengthMax = 0.00463050;
