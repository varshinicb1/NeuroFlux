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
  translate([0, 0, -0.00862000])
    ring(0.17000000, 0.11220000, 0.01428000);
color("#b66a2c")
  translate([0, 0, 0.00000000])
    ring(0.16660000, 0.11444400, 0.04080000);
for (i = [0:19]) {
  angle = 360 * i / 20;
  color((i % 2 == 0) ? "#1f77b4" : "#d62728")
    rotate([0, 0, angle])
      translate([0.14110000, 0, -0.00125000])
        magnet_block(
          0.04970800,
          0.03191607,
          0.00612000
        );
}
