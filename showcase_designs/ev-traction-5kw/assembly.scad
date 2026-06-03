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
  translate([0, 0, -0.00722500])
    ring(0.13125000, 0.07612500, 0.01102500);
color("#b66a2c")
  translate([0, 0, 0.00000000])
    ring(0.12862500, 0.07764750, 0.03150000);
for (i = [0:15]) {
  angle = 360 * i / 16;
  color((i % 2 == 0) ? "#1f77b4" : "#d62728")
    rotate([0, 0, angle])
      translate([0.10368750, 0, -0.00125000])
        magnet_block(
          0.04740750,
          0.02931695,
          0.00472500
        );
}
