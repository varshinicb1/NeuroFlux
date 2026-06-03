// NeuroFlux Palace electromagnetics mesh handoff
SetFactory("OpenCASCADE");
r_out = 0.05512500;
r_in = 0.03197250;
axial = 0.01323000;
Cylinder(1) = {0, 0, -axial/2, 0, 0, axial, r_out};
Cylinder(2) = {0, 0, -axial/2, 0, 0, axial, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
Physical Volume("domain") = {1};
