// NeuroFlux Elmer FEM AFPM handoff geometry
SetFactory("OpenCASCADE");
r_out = 0.12500000;
r_in = 0.07250000;
axial = 0.03000000;
Cylinder(1) = {0, 0, -axial/2, 0, 0, axial, r_out};
Cylinder(2) = {0, 0, -axial/2, 0, 0, axial, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
machine_boundary[] = Boundary{ Volume{1}; };
Physical Volume(1) = {1};
Physical Surface(2) = {machine_boundary[]};
Mesh.SaveAll = 1;
Mesh.CharacteristicLengthMax = 0.00656250;
