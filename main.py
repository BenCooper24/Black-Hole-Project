# main.py

# Import necessary modules
import numpy as np
import pygame
from camera import Camera

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 200, 150
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black Hole Simulation")

# Set up clock for controlling frame rate
clock = pygame.time.Clock()
camera = Camera()

# Scene parameters
BH_RADIUS = 1.5  
DISK_INNER_RADIUS = 5.0
DISK_OUTER_RADIUS = 8.0


#
def intersect_sphere(ro, rd, radius):
    """ 

    Check for intersection between ray and sphere

    Inputs: ray origin (ro), ray direction (rd), sphere radius

    Outputs: distance to intersection or None if no intersection


    """

    # Solve |ro + t*rd|^2 = radius^2
    # Coefficients of quadratic equation
    b = 2 * np.dot(ro, rd)
    c = np.dot(ro, ro) - radius * radius
    # Discriminant
    disc = b * b - 4 * c

    # No intersection if discriminant is negative
    if disc < 0:
        return None

    # Compute intersection distances
    sqrt_disc = np.sqrt(disc)

    # Return the nearest positive intersection
    t0 = (-b - sqrt_disc) / 2
    t1 = (-b + sqrt_disc) / 2

    # Check for valid intersections
    if t0 > 1e-6:
        return t0
    if t1 > 1e-6:
        return t1

    # No valid intersection
    return None


# Check for intersection between ray and disk
def intersect_disk(ro, rd, r_inner, r_outer):

    """ 

    Check for intersection between ray and accretion disk

    Inputs: ray origin (ro), ray direction (rd), inner and outer radius of disk

    Outputs: distance to intersection or None if no intersection


    """

    # Avoid division by zero
    if abs(rd[1]) < 1e-6:
        return None

    # Compute t where ray intersects the plane y=0
    t = -ro[1] / rd[1]
    if t < 1e-6:
        return None

    # Compute intersection with the plane y=0
    p = ro + t * rd
    r = np.sqrt(p[0]*p[0] + p[2]*p[2])
    if r_inner <= r <= r_outer:
        return t

    # No intersection
    return None


# Shading function for the disk
def shade_disk(point):

    """ 

    Simple shading function for the disk

    Inputs: intersection point (3D numpy array)

    Outputs: color (RGB tuple)


    """

    r = np.sqrt(point[0]*point[0] + point[2]*point[2])

    # Map r in [DISK_INNER, DISK_OUTER] to color gradient
    u = (r - DISK_INNER_RADIUS) / (DISK_OUTER_RADIUS - DISK_INNER_RADIUS)
    u = np.clip(u, 0, 1)
    brightness = int(255 * (1 - 0.8 * u))

    # Warm color gradient from yellow to red
    return (brightness, int(brightness * 0.8), int(brightness * 0.3))


# Rendering function
def render(camera):

    """ 

    Render the scene from the camera's perspective

    Inputs: camera object

    Outputs: Return an (RH, RW, 3) numpy array representing the image


    """

    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    ro = camera.position()

    for y in range(HEIGHT):
        for x in range(WIDTH):

            # Get ray direction
            rd = camera.ray_direction(x, y, WIDTH, HEIGHT)
            
            # Check for intersections
            t_bh = intersect_sphere(ro, rd, BH_RADIUS)
            t_disk = intersect_disk(ro, rd, DISK_INNER_RADIUS, DISK_OUTER_RADIUS)

            # Decide what pixel sees
            if t_bh is not None and (t_disk is None or t_bh < t_disk):
                # Hit black hole - render black
                img[y, x] = (0, 0, 0)

            elif t_disk is not None:
                # Hit disk - shade accordingly
                hit = ro + t_disk * rd
                img[y, x] = shade_disk(hit)

            else:
                # Background color - dark blue
                img[y, x] = (25, 25, 45)

    return img


# Progressive renderer class
class ProgressiveRender:
    def __init__(self, HEIGHT, WIDTH):
        self.rw = WIDTH
        self.rh = HEIGHT
        self.frame = np.zeros((self.rh, self.rw, 3), dtype=np.uint8)
        self.next_row = 0
        self.active = True

    def start(self):
        self.next_row = 0
        self.active = True

    def step(self, camera, rows_per_frame):
        if not self.active:
            return

        ro = camera.position()

        for y in range(self.next_row, min(self.next_row + rows_per_frame, self.rh)):
            for x in range(self.rw):

                # Get ray direction
                rd = camera.ray_direction(x, y, self.rw, self.rh)

                # Check for intersections
                t_bh = intersect_sphere(ro, rd, BH_RADIUS)
                t_disk = intersect_disk(ro, rd, DISK_INNER_RADIUS, DISK_OUTER_RADIUS)

                # Decide what pixel sees
                if t_bh is not None and (t_disk is None or t_bh < t_disk):
                    # Hit black hole - render black
                    self.frame[y, x] = (0, 0, 0)

                elif t_disk is not None:
                    # Hit disk - shade accordingly
                    hit = ro + t_disk * rd
                    self.frame[y, x] = shade_disk(hit)

                else:
                    # Background color - dark blue
                    self.frame[y, x] = (25, 25, 45)

        self.next_row += rows_per_frame

        if self.next_row >= self.rh:
            self.active = False


renderer = ProgressiveRender(HEIGHT, WIDTH)
renderer.start()

            
# Main loop
running = True
while running:

    # Delta time in seconds
    dt = clock.tick(60) / 1000  

    # Event handling and game exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        camera.handle_event(event)

    # Update camera when camera is moved 
    if camera.consume_dirty():
        renderer.start()

    renderer.step(camera, 20)
    frame = renderer.frame 

    # Convert numpy array to Pygame surface and scale to screen size
    surf = pygame.surfarray.make_surface(np.transpose(frame, (1, 0, 2)))
    surf = pygame.transform.scale(surf, (WIDTH, HEIGHT))

    # Blit to screen
    screen.blit(surf, (0, 0))
    pygame.display.flip()


# Quit Pygame
pygame.quit()

    
