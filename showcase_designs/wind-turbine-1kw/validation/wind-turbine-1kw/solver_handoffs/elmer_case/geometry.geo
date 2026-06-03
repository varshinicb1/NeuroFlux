// NeuroFlux Elmer FEM AFPM handoff geometry
SetFactory("OpenCASCADE");
r_out = 0.17000000;
r_in = 0.11220000;
axial = 0.04080000;
Cylinder(1) = {0, 0, -axial/2, 0, 0, axial, r_out};
Cylinder(2) = {0, 0, -axial/2, 0, 0, axial, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
machine_boundary[] = Boundary{ Volume{1}; };
Physical Volume(1) = {1};
Physical Surface(2) = {machine_boundary[]};
Mesh.SaveAll = 1;
Mesh.CharacteristicLengthMax = 0.00722500;
