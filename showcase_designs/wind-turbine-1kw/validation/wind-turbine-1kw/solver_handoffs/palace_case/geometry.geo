// NeuroFlux Palace electromagnetics mesh handoff
SetFactory("OpenCASCADE");
r_out = 0.17000000;
r_in = 0.11220000;
axial = 0.04080000;
Cylinder(1) = {0, 0, -axial/2, 0, 0, axial, r_out};
Cylinder(2) = {0, 0, -axial/2, 0, 0, axial, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
Physical Volume("domain") = {1};
