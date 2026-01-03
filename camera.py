# camera.py

# Import necessary modules
import numpy as np
import pygame

class Camera:

    # Initialize the camera with default parameters
    def __init__(self):

        """

        Initialize camera parameters

        Inputs: none

        Outputs: none

        """

        # Camera polar coordinates
        self.radius = 50
        self.theta = 0
        self.phi = 0

        # Camera control parameters
        self.fov = np.radians(60)
        self.mouse_sensitivity = 0.005
        self.dragging = False


    # Handle mouse events for camera control
    def handle_event(self, event):

        """ 
        Handle mouse events to control camera orientation

        Inputs: event (pygame event)

        Outputs: none

        """

        # If mouse button pressed, start dragging
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.dragging = True
        
        # If mouse button released, stop dragging
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        # If mouse moved while dragging, update camera orientation
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx, dy = event.rel
            self.theta += dx * self.mouse_sensitivity
            self.phi -= dy * self.mouse_sensitivity
            self.phi = max(-np.pi/2, min(np.pi/2, self.phi))


    # Update the camera position based on time delta
    def update(self, dt):
        pass  


    # Get the Cartesian coordinates of the camera
    def position(self):

        """ 

        Convert spherical coordinates to Cartesian coordinates

        Inputs: none

        Outputs: numpy array of camera position [x, y, z]

        """
        
        # Convert spherical coordinates to Cartesian coordinates
        x = self.radius * np.cos(self.phi) * np.cos(self.theta)
        y = self.radius * np.sin(self.phi)
        z = self.radius * np.cos(self.phi) * np.sin(self.theta)

        # Return position as numpy array
        return np.array([x, y, z])


    # Draw camera information on the screen
    def draw(self, screen, width, height):

        """

        Draw camera position text on the screen

        Inputs: screen (pygame surface), width (int), height (int)

        Outputs: none

        """
        # Get camera position
        pos = self.position()

        # Render position text
        text = f"Camera pos: {pos.round(2)}"

        # Get font and render text
        font = pygame.font.SysFont(None, 24)
        img = font.render(text, True, (255, 255, 255))
        screen.blit(img, (10, 10))


    # Get camera basis vectors
    def basis_vectors(self):
        """

        Returns camera basis vectors: forward, right, up

        Inputs: none

        Outputs: forward, right, up vectors as numpy arrays

        """

        # Get camera position
        pos = self.position()

        # Compute forward vector looking at origin
        forward = -pos / np.linalg.norm(pos)

        # Compute right vector as cross product with world up
        world_up = np.array([0, 1, 0])
        right = np.cross(world_up, forward)
        right /= np.linalg.norm(right)

        # Compute up vector as cross product with forward and right
        up = np.cross(forward, right)

        # Return basis vectors
        return forward, right, up


    # Project a 3D point to 2D screen coordinates
    def project(self, point, screen_width, screen_height):

        """

        Project a 3D point to 2D screen coordinates

        Inputs: point (numpy array [x, y, z]), screen_width (int), screen_height (int)

        Outputs: (screen_x, screen_y) tuple or None if behind camera

        """

        # Get camera position and basis vectors
        cam_pos = self.position()
        forward, right, up = self.basis_vectors()

        # Transform point to camera space
        rel = point - cam_pos
        x_cam = np.dot(rel, right)
        y_cam = np.dot(rel, up)
        z_cam = np.dot(rel, forward)

        # If the point is behind the camera, return None
        if z_cam <= 0:
            return None

        # Perspective projection
        scale = 1 / np.tan(self.fov / 2)
        x_ndc = (x_cam / z_cam) * scale
        y_ndc = (y_cam / z_cam) * scale

        # Convert to screen coordinates
        screen_x = int((x_ndc + 1) * 0.5 * screen_width)
        screen_y = int((1 - y_ndc) * 0.5 * screen_height)

        # Return screen coordinates
        return screen_x, screen_y

    
    # Draw disk
    def draw_disk(self, screen, width, height):

        """

        Draw a simple accretion disk ring in the x–z plane.

        Inputs: screen (pygame surface), width (int), height (int)

        Outputs: none

        """

        # Disk parameters
        r_inner = 1.5
        r_outer = 3.0
        num_points = 200

        # Draw inner and outer rings
        for r in [r_inner, r_outer]:

            # Generate points around the circle
            points = []

            # Compute points on the circle with even spacing
            for i in range(num_points):
                angle = 2 * np.pi * i / num_points
                x = r * np.cos(angle)
                y = 0.0
                z = r * np.sin(angle)

                # Project points to screen
                p = self.project(np.array([x, y, z]), width, height)
                if p is not None:
                    points.append(p)

            # Draw the ring if enough points are visible
            if len(points) > 2:
                pygame.draw.lines(screen, (200, 120, 50), True, points, 2)
