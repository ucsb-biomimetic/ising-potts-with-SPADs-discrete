import numpy
import imageio

#height from point source to SiPM plane, mm
h = 40

#map pixel pitch, mm
pt = 0.1

map_size = 610
intensity_map = numpy.zeros([map_size, map_size])

center = int(map_size/2.)

for i in range(map_size):
	for j in range(map_size):
		#calc unitless intensity, based on two things:
		#--intensity decreases based on distance from point source (still in spherical coordinates)
		#--intensity also decreases due to illumination hitting surface at an oblique angle

		#in mm
		dist_from_center = ( ((i-center)*pt)**2 + ((j-center)*pt)**2 )**0.5

		#in mm
		light_r = (dist_from_center**2 + h**2)**0.5

		#arbitrary intensity: light spreads out over the surface of a sphere as it eminates, so intensity drops as the square of radius
		I = 1./(light_r**2)

		#derating due to angle of light: 
		#equal to cos(angle), but we already have the triangle, not the angle, so we can just use a ratio:
		I = I*h/light_r

		intensity_map[i, j] = I


# we want intensity * mask should yield a constant, so:
mask = numpy.ones([map_size, map_size])
mask = mask/intensity_map

#scale to 0 to 255 range:
intensity_map = intensity_map/numpy.max(intensity_map)*255

imageio.imwrite("intensity_map.png", intensity_map.astype(numpy.uint8))

#for the mask, cannot shift to zero scale.
#brightest spots should be corners; should scale them to be full brightness.
#center will be darkest and should be scaled to match corner scaling, but should not be fully masked out
mask = mask/numpy.max(mask)*255

imageio.imwrite("illumination_mask_%i.png"%h, mask.astype(numpy.uint8))