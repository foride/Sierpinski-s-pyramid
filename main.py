import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Constants for clarity
INITIAL_TRANSLATION = (0.0, -0.5, -5)
ROTATION_SPEED_PYRAMID = 0.5

pyramidVertices = (
    (0, 0, 0),
    (2, 0, 0),
    (1, 0, math.sqrt(3)),
    (1, math.sqrt(26) / 3, 2 / 3)
)

edges = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
)

colors = (
    (0, 0, 1),  # Dark Blue
    (0, 0.5, 1),  # Medium Blue
    (0, 1, 1),  # Cyan
    (0.5, 0.5, 1),  # Light Blue
    (0.7, 0.7, 1),  # Lighter Blue
    (0.3, 0.3, 1)  # Another Blue Shade
)

surfaces = (
    (0, 1, 2),
    (0, 2, 3),
    (0, 1, 3),
    (1, 2, 3)
)

ground_vertices = (
    (-4000, 0, 5000),
    (4000, 0, 4000),
    (-4000, 0, -4000),
    (4000, 0, -4000)
)


# Function to draw the ground using OpenGL quads
def ground():
    # Begin drawing quads (four-sided polygons)
    glBegin(GL_QUADS)

    # Loop through each vertex in ground_vertices
    for vertex in ground_vertices:
        # Set the color for the ground (blue color)
        glColor3fv((0, 0, 1))

        # Specify a vertex for the quad
        glVertex3fv(vertex)

    # End drawing quads
    glEnd()


# Function to calculate the midpoint between two points in 3D space
def midpoint(p1, p2):
    # Calculate the average coordinates for x, y, and z
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2


# Function to calculate midpoints of edges in a tetrahedron
def sub_tetrahedrons(vertices):
    # Calculate midpoints for each edge in the tetrahedron
    midpoints = [midpoint(vertices[edge[0]], vertices[edge[1]]) for edge in edges]

    # Return a list of four smaller tetrahedrons with their vertices
    return [
        (vertices[0], midpoints[0], midpoints[1], midpoints[2]),
        (vertices[1], midpoints[0], midpoints[3], midpoints[4]),
        (vertices[2], midpoints[1], midpoints[3], midpoints[5]),
        (vertices[3], midpoints[2], midpoints[4], midpoints[5])
    ]


# Function to draw a tetrahedron with optional wall coloring
def tetrahedron(vertices, check):
    # Begin drawing lines for the tetrahedron edges
    glBegin(GL_LINES)

    # Loop through each edge in the tetrahedron
    for edge in edges:
        # Loop through each vertex in the edge
        for vertex in edge:
            # Set the color for the tetrahedron edges (dark gray)
            glColor3fv((0.2, 0.2, 0.2))

            # Specify a vertex for the line
            glVertex3fv(vertices[vertex])

    # End drawing lines
    glEnd()

    # If check is 1, draw the walls of the tetrahedron
    if check == 1:
        # Begin drawing triangles for the tetrahedron walls
        glBegin(GL_TRIANGLES)

        # Loop through each surface in the tetrahedron
        for surface in surfaces:
            # Loop through each vertex in the surface
            for i, vertex in enumerate(surface):
                # Set the color for the tetrahedron walls using predefined colors
                glColor3f(colors[i][0], colors[i][1], colors[i][2])

                # Specify a vertex for the triangle
                glVertex3fv(vertices[vertex])

        # End drawing triangles
        glEnd()


# Function to recursively draw a Sierpiński pyramid
def sierpinski(vertices, depth, texture_status):
    # Base case: if depth is 0, draw a tetrahedron
    if depth == 0:
        tetrahedron(vertices, texture_status)
        return

    # Calculate midpoints to create four smaller tetrahedrons
    tetrahedrons = sub_tetrahedrons(vertices)

    # Recursively draw each of the smaller tetrahedrons
    for tetra in tetrahedrons:
        sierpinski(tetra, depth - 1, texture_status)


# Function to set up lighting properties
def light(light_color):
    # Set the direction and properties of the light source (GL_LIGHT0)
    light_direction = (-1, -1, -1, 0)
    glLightfv(GL_LIGHT0, GL_POSITION, light_direction)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)
    glLightfv(GL_LIGHT0, GL_POSITION, light_color)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_color)

    # Enable coloring of materials based on ambient and diffuse components
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)


# Function to draw a textured sphere
def sphere(radius, slices, stacks):
    # Create a new quadric object
    quad = gluNewQuadric()

    # Enable texture mapping for the quadric object
    gluQuadricTexture(quad, GL_TRUE)

    # Draw a sphere using the quadric object with specified parameters
    gluSphere(quad, radius, slices, stacks)

    # Delete the quadric object to free up resources
    gluDeleteQuadric(quad)


# Function to draw a small textured sphere representing the light source
def light_sphere():
    # Save the current transformation matrix
    glPushMatrix()

    # Translate to the position (5.0, 5.0, 5.0)
    glTranslatef(5.0, 5.0, 5.0)

    # Scale down the sphere to a size of 0.1 in each dimension
    glScalef(0.1, 0.1, 0.1)

    # Draw a textured sphere with radius 1, using 30 slices and 30 stacks
    sphere(1, 30, 30)

    # Restore the previous transformation matrix
    glPopMatrix()


# Function to set up material properties for lighting
def set_light_properties():
    # Set the ambient material color for the front face of polygons
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])

    # Set the diffuse material color for the front face of polygons
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

    # Set the specular material color for the front face of polygons
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    # Set the shininess of the material (128 is a common value)
    glMaterialfv(GL_FRONT, GL_SHININESS, [128.0])


# Function to handle Pygame events and update the application state
def handle_events(rotation_status, texture_status, light_color, levels):
    # Iterate over each Pygame event
    for event in pygame.event.get():
        # Check if the event is a QUIT event (user closes the window)
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        # Check for mouse button down events (e.g., scrolling)
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Zoom in when scrolling up
            if event.button == 4:
                glTranslatef(0, 0, 1.0)
            # Zoom out when scrolling down
            if event.button == 5:
                glTranslatef(0, 0, -1.0)

        # Check for KEYDOWN events (e.g., arrow keys or other keys)
        if event.type == pygame.KEYDOWN:
            # Move upward when the UP arrow key is pressed
            if event.key == pygame.K_UP:
                glTranslatef(0, -0.5, 0)
            # Move downward when the DOWN arrow key is pressed
            if event.key == pygame.K_DOWN:
                glTranslatef(0, 0.5, 0)
            # Move leftward when the LEFT arrow key is pressed
            if event.key == pygame.K_LEFT:
                glTranslatef(0.5, 0, 0)
            # Move rightward when the RIGHT arrow key is pressed
            if event.key == pygame.K_RIGHT:
                glTranslatef(-0.5, 0, 0)

            # Toggles on/off rotation when the 'r' key is pressed
            if event.key == pygame.K_r:
                rotation_status = 1 - rotation_status

            # Toggles on/off textures when the 't' key is pressed
            if event.key == pygame.K_t:
                # Toggle texture only if the current level is less than 5
                if texture_status == 0 and levels < 5:
                    texture_status = 1
                else:
                    texture_status = 0



            # Set pyramid color to green and turn off directional light when the '8' key is pressed
            if event.key == pygame.K_8:
                light_color = [0.0, 1.0, 0.0, 1.0]

    return rotation_status, light_color, texture_status


# Main function to run the application
def main():
    # Initialize variables for rotation, texture, light color, and user input
    rotation_status = 1
    rotation_pyramid = 0
    texture_status = 1
    light_color = [1.0, 1.0, 1.0, 1.0]

    input_str = input("Enter the number of recursive depth of Sierpiński's Pyramid: ")

    try:
        levels = int(input_str)

        # Adjust texture status and levels based on user input
        if levels > 4:
            texture_status = 0
            levels = min(levels, 6)
    except ValueError:
        # Handle the case where the user enters an invalid numeric value
        print("Invalid input. Please enter a valid numeric value.")
        return

    # Initialize Pygame and OpenGL display
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Set up perspective projection and initial translation
    gluPerspective(70, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(*INITIAL_TRANSLATION)

    # Enable color material and depth testing
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    set_light_properties()

    # Main application loop
    while True:
        # Handle Pygame events and update application state
        rotation_status, light_color, texture_status = handle_events(rotation_status, texture_status, light_color,
                                                                     levels)

        light(light_color)

        # Clear the screen and set diffuse material color
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))

        # Update rotation of the pyramid
        rotation_pyramid += ROTATION_SPEED_PYRAMID if rotation_status == 1 else 0
        # Draw the ground and the Sierpiński pyramid

        glPushMatrix()
        glRotatef(rotation_pyramid, 0, 1, 0)
        sierpinski(pyramidVertices, levels, texture_status)
        glPopMatrix()

        ground()

        glPushMatrix()
        glTranslatef(0.0, -3.0, 0.0)  # Adjust the position of the sphere along the z-axis
        glRotatef(rotation_pyramid, 0, 1, 0)
        sphere(1.0, 30, 30)  # Set the radius and resolution
        light_sphere()
        glPopMatrix()

        # Update the display
        pygame.display.flip()
        pygame.time.wait(20)


# Run the main function if the script is executed
if __name__ == "__main__":
    main()
