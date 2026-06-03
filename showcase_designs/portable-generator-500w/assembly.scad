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
  translate([0, 0, -0.00650000])
    ring(0.08268750, 0.04795875, 0.00694575);
color("#b66a2c")
  translate([0, 0, 0.00000000])
    ring(0.08103375, 0.04891793, 0.01984500);
for (i = [0:19]) {
  angle = 360 * i / 20;
  color((i % 2 == 0) ? "#1f77b4" : "#d62728")
    rotate([0, 0, angle])
      translate([0.06532313, 0, -0.00125000])
        magnet_block(
          0.02986673,
          0.01477574,
          0.00400000
        );
}
