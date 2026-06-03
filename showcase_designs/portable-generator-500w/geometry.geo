// NeuroFlux AFPM parametric geometry for Gmsh handoff.
SetFactory("OpenCASCADE");
r_in = 0.04795875;
r_out = 0.08268750;
stator_thickness = 0.01984500;
magnet_thickness = 0.00400000;
air_gap = 0.00250000;
pole_count = 20;
slot_count = 60;
Cylinder(1) = {0, 0, -stator_thickness/2, 0, 0, stator_thickness, r_out};
Cylinder(2) = {0, 0, -stator_thickness/2, 0, 0, stator_thickness, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
Physical Volume("stator_active_region") = {1};
Mesh.CharacteristicLengthMin = 0.00125000;
Mesh.CharacteristicLengthMax = 0.00694575;
