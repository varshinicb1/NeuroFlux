// NeuroFlux Palace electromagnetics mesh handoff
SetFactory("OpenCASCADE");
r_out = 0.13125000;
r_in = 0.07612500;
axial = 0.03150000;
Cylinder(1) = {0, 0, -axial/2, 0, 0, axial, r_out};
Cylinder(2) = {0, 0, -axial/2, 0, 0, axial, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
Physical Volume("domain") = {1};
