// NeuroFlux manufacturable AFPM inspection assembly.
// Units: meters. Import into OpenSCAD, FreeCAD, or convert with openscad CLI.
$fn = 144;
module ring(outer_radius, inner_radius, thickness) {
  difference() {
    cylinder(h = thickness, r = outer_radius, center = true);
    cylinder(h = thickness * 1.2, r = inner_radius, center = true);
  }
}
module magnet_block(radial_width, arc_width, thickness) {
  cube([radial_width, arc_width, thickness], center = true);
}
color("#58616a")
  translate([0, 0, -0.01243600])
    ring(0.27600000, 0.16008000, 0.02318400);
color("#b66a2c")
  translate([0, 0, 0.00000000])
    ring(0.27048000, 0.16328160, 0.06624000);
for (i = [0:23]) {
  angle = 360 * i / 24;
  color((i % 2 == 0) ? "#1f77b4" : "#d62728")
    rotate([0, 0, angle])
      translate([0.21804000, 0, -0.00125000])
        magnet_block(
          0.09969120,
          0.04109957,
          0.00993600
        );
}
