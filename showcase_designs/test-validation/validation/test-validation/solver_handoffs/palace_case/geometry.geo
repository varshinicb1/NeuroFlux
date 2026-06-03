// NeuroFlux Palace electromagnetics mesh handoff
SetFactory("OpenCASCADE");
r_out = 0.12160000;
r_in = 0.07539200;
axial = 0.02918400;
Cylinder(1) = {0, 0, -axial/2, 0, 0, axial, r_out};
Cylinder(2) = {0, 0, -axial/2, 0, 0, axial, r_in};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
Physical Volume("domain") = {1};
