import numpy as np
from PIL import Image

# Scene parameters
width, height = 500, 500
camera_position = np.array([0., 0, -1.])  #
light_position = np.array([0., .7, -10.])  #
ambient_color = np.array([0.1, 0.1, 0.1])
depth_max = 5  # Maximum number of light reflections


# Define an intersection function for a sphere
def sphere_intersect(rayO, rayD, sphereS, sphereR):
    # O: ray origin, D: ray direction, S: sphere center, R: sphere radius
    L = sphereS - rayO
    tca = np.dot(L, rayD)
    if tca < 0: return np.inf  # Intersection is behind the origin
    d2 = np.dot(L, L) - tca ** 2
    if d2 > sphereR ** 2: return np.inf  # Ray misses the sphere
    thc = np.sqrt(sphereR ** 2 - d2)
    t0 = tca - thc  # distance to the first intersection
    t1 = tca + thc  # distance to the second intersection
    if t0 < 0:
        return t1  # Return second intersection if first is behind camera
    else:
        return t0


# Find the first point of intersection with the scene
def trace_ray(rayO, rayD, scene):
    t_min = np.inf
    nearest_object = None
    for obj in scene:
        t = sphere_intersect(rayO, rayD, obj['position'], obj['radius'])
        if t < t_min:
            t_min = t
            nearest_object = obj
    return nearest_object, t_min


def applyMatrix(vertices, transformation_matrix):
    """
    Applies a 4x4 homogeneous transformation matrix to a set of 3D vertices.

    Args:
        vertices (np.array): An Nx3 array of (x, y, z) coordinates.
        transformation_matrix (np.array): A 4x4 homogeneous transformation matrix.

    Returns:
        np.array: An Nx3 array of transformed (x', y', z') coordinates.
    """
    # Convert vertices to homogeneous coordinates (Nx4, with w=1)
    # The snippet notes that vertices should be treated as column vectors
    # for matrix multiplication, so we transpose.
    vertices_h = np.hstack((vertices, np.ones((vertices.shape[0], 1))))  # Nx4

    # Apply the transformation: M @ V_h^T, then transpose back to row-major
    transformed_vertices_h = (transformation_matrix @ vertices_h.T).T  # Nx4

    # Convert back to Euclidean coordinates (divide by w, then remove w column)
    # The last element should be 1 after a standard affine transformation,
    # but division by w handles perspective transformations as well.
    transformed_vertices = transformed_vertices_h[:, :3] / transformed_vertices_h[:, 3, np.newaxis]

    return transformed_vertices


startWidth, endWidth = 0, 500
startWorld, endWorld = -1, 1
scale = float(endWorld - startWorld) / (endWidth - startWidth)
print(scale)
tmx = np.array([
    [scale, 0, 0, -1.0],
    [0, scale, 0, -1.0],
    [0, 0, 1, 0.0],
    [0, 0, 0, 1.0]
])
#new added code
#new position for pixels (x,y,z)
pixel_positions = np.array([
    [50, 450, 0.5], #red sphere
    [450, 50, 0.5], #green sphere
    [250, 250, 0.5], # blue sphere
])

# pass through the transformation matrix
world_coords = applyMatrix(pixel_positions, tmx)

# Scene objects: spheres (position, radius, color, material properties)
scene = [
    {'position': world_coords[0], 'radius': 0.25, 'color': np.array([1., 0., 0.]), 'reflection': 0.5},
    {'position': world_coords[1], 'radius': 0.25, 'color': np.array([0., 1., 0.]), 'reflection': 0.8},
    {'position': world_coords[2], 'radius': 0.25, 'color': np.array([0., 0., 1.]), 'reflection': 0.1},
    {'position': np.array([0., -10, 0.]), 'radius': 200., 'color': np.array([0.8, 0.8, 0.8]), 'reflection': 0.1}
    # Ground
]

pos1 = np.array([[250, 250, 2.]])

vertices = np.array([
    [0, 0, 0], [75, 0, 0], [0, 50, 0], [0, 0, 10],
    [50, 50, 0], [75, 0, 0], [0, 50, 10], [50, 50, 10]
])

# Rendering loop
image = np.zeros((height, width, 3))
for i, y in enumerate(np.linspace(-1., 1., height)):
    for j, x in enumerate(np.linspace(-1., 1., width)):
        # Ray direction from camera through the pixel
        pixel_pos = np.array([x, y, 0])
        ray_direction = pixel_pos - camera_position
        ray_direction /= np.linalg.norm(ray_direction)  # Normalize the direction vector

        color = np.zeros(3)
        reflection = 1.
        rayO, rayD = camera_position, ray_direction

        for depth in range(depth_max):
            nearest_object, t_min = trace_ray(rayO, rayD, scene)
            if nearest_object is None:
                break  # Ray missed all objects

            # Point of intersection
            M = rayO + rayD * t_min
            # Normal at the intersection point
            N = M - nearest_object['position']
            N /= np.linalg.norm(N)

            # Direction from intersection point to light
            L = light_position - M
            L /= np.linalg.norm(L)

            # Shadow check: cast a ray from the intersection to the light
            # Add a small offset to the origin of the shadow ray to avoid self-intersection
            # shadow_rayO = M + N * .0001
            # shadow_obj, shadow_t = trace_ray(shadow_rayO, L, scene)
            # is_shadowed = shadow_obj is not None and shadow_t < np.linalg.norm(light_position - M)

            # Lambert shading (diffuse)
            # if not is_shadowed:
            # Max of 0 to avoid negative light values
            dot_product = max(np.dot(N, L), 0)
            color += reflection * nearest_object['color'] * dot_product
            # else:
            # Add ambient light even in shadow
            #    color += reflection * ambient_color * nearest_object['color']

            # Update for reflection ray
            reflection *= nearest_object['reflection']
            rayO = M + N * .0001  # Move origin slightly along normal
            # Reflection formula: R = V - 2 * (V . N) * N, where V is the incoming ray direction (or -D)
            # here we use D as already pointing away from camera.
            rayD = rayD - 2 * np.dot(rayD, N) * N
            rayD /= np.linalg.norm(rayD)  # Normalize again

        image[i, j] = np.clip(color, 0., 1.)  # Clip color values to [0, 1]

# Save the image
image = (image * 255).astype(np.uint8)
img = Image.fromarray(image, 'RGB')
img.show()
# img.save("python_raytracing_output.png")
print("Image saved as python_raytracing_output.png")
