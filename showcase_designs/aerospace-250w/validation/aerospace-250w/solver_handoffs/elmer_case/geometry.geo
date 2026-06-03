// NeuroFlux Elmer FEM AFPM handoff geometry
SetFactory("OpenCASCADE");
r_out = 0.05512500;
r_in = 0.03197250;
axial = 0.01323000;
Cylinder(1) = {0, 0, -axial/2, 0, 0, axial, r_out};
Cylinder(2) = {0, 0, -axial/2, 0, 0, axial, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
machine_boundary[] = Boundary{ Volume{1}; };
Physical Volume(1) = {1};
Physical Surface(2) = {machine_boundary[]};
Mesh.SaveAll = 1;
Mesh.CharacteristicLengthMax = 0.00289406;
