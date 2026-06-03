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
    ring(0.05512500, 0.03197250, 0.00463050);
color("#b66a2c")
  translate([0, 0, 0.00000000])
    ring(0.05402250, 0.03261195, 0.01323000);
for (i = [0:7]) {
  angle = 360 * i / 8;
  color((i % 2 == 0) ? "#1f77b4" : "#d62728")
    rotate([0, 0, angle])
      translate([0.04354875, 0, -0.00125000])
        magnet_block(
          0.01991115,
          0.02462624,
          0.00400000
        );
}
