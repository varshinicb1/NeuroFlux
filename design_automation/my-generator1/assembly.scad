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
  translate([0, 0, -0.00700000])
    ring(0.12500000, 0.07250000, 0.01050000);
color("#b66a2c")
  translate([0, 0, 0.00000000])
    ring(0.12250000, 0.07395000, 0.03000000);
for (i = [0:15]) {
  angle = 360 * i / 16;
  color((i % 2 == 0) ? "#1f77b4" : "#d62728")
    rotate([0, 0, angle])
      translate([0.09875000, 0, -0.00125000])
        magnet_block(
          0.04515000,
          0.02792090,
          0.00450000
        );
}
