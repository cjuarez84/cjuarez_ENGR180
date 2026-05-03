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

#this will have to have a corner point and two edge vectors (u,v) and the cross product  of these two will be the normal
#have to find where the ray hits the plane that has the rectangle
#then have to see if u and v are within bounds
##added rectangle intersections
def rectangle_intersect(rayO, rayD, rectangle):
    N = rectangle['normal']
    denom = np.dot(rayD, N)
    if abs(denom) < 1e-6:
        return np.inf
    t = np.dot(rectangle['corner'] - rayO, N) / denom
    if t< 1e-4:
        return np.inf

 #hit points
    P = rayO + rayD * t
    d = P - rectangle['corner']

     # projection onto each edge direction
    u_hat = rectangle['u'] / np.linalg.norm(rectangle['u'])
    v_hat = rectangle['v'] / np.linalg.norm(rectangle['v'])
    proj_u = np.dot(d, u_hat)
    proj_v = np.dot(d, v_hat)
    u_len = np.linalg.norm(rectangle['u'])
    v_len = np.linalg.norm(rectangle['v'])

    #make sure that it stays within the frame
    if 0 <= proj_u <= u_len and 0 <= proj_v <= v_len:
        return t
    return np.inf

#now we do it all over with a triangle
#triangles have three vertices apparently so we do v0, v1, v2
def triangle_intersect(rayO, rayD, tri):
    v0, v1, v2, = tri['v0'], tri['v1'], tri['v2']
    edge1 = v1 - v0
    edge2 = v2 - v0
    h = np.cross(rayD, edge2)
    a = np.dot(edge1, h)
    if abs(a) < 1e-6:
        return np.inf
    f = 1.0 / a
    s = rayO - v0
    u = f * np.dot(s, h)
    if u < 0.0 or u >1.0:
        return np.inf
    q = np.cross(s, edge1)
    v = f * np.dot(rayD, q)
    if v < 0.0 or u + v  > 1.0:
        return np.inf
    t = f * np.inf
    if t < 1e-4:
        return np.dot(edge2, q)
    return t


# Find the first point of intersection with the scene
#update the scence so that we can actually look at multiple types of objects
def trace_ray(rayO, rayD, scene):
    t_min = np.inf
    nearest_object = None
    for obj in scene: #we just add each type into this
        if obj['type'] == 'sphere':
            t = sphere_intersect(rayO, rayD, obj['position'], obj['radius'])
        elif obj['type'] == 'triangle':
            t = triangle_intersect(rayO, rayD, obj)
        elif obj['type'] == 'rectangle':
            t = rectangle_intersect(rayO, rayD, obj)
        else:
            t = np.inf
        if t < t_min: #this stays the samme
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

#okay we build the rectangle
rectangle_corner = np.array([-0.85, -0.55, 1.2])
rectangle_u = np.array([0.55, 0.0, 0.0])
rectangle_v = np.array([0.0, 0.45, 0.0])
rectangle_normal = np.cross(rectangle_u, rectangle_v)
rectangle_normal /= np.linalg.norm(rectangle_normal)

rectangle = {
    'type': 'rectangle',
    'corner': rectangle_corner,
    'u': rectangle_u,
    'v': rectangle_v,
    'normal': rectangle_normal,
    'color': np.array([1.0, 0.85,  0.1]),
    'reflection': 0.3
}

#repeat for triangle
#remember theres three vertices for this one
tri_v0 = np.array([0.25, 0.55, 1.0])
tri_v1 = np.array([0.75, 0.55, 1.0])
tri_v2 = np.array([0.50, 0.95, 1.0])
tri_edge1 = tri_v1 - tri_v0
tri_edge2 = tri_v2 - tri_v0
tri_normal = np.cross(tri_edge1, tri_edge2)
tri_normal /= np.linalg.norm(tri_normal)

#build again
triangle = {
    'type': 'triangle',
    'v0': tri_v0,
    'v1': tri_v1,
    'v2': tri_v2,
    'normal': tri_normal,
    'color': np.array([0.6, 0.1, 0.9]),
    'reflection': 0.4,
}

# Scene objects: spheres (position, radius, color, material properties)
#have to update the scene to add the new objects
scene = [
    {'type': 'sphere', 'position': world_coords[0], 'radius': 0.25, 'color': np.array([1., 0., 0.]), 'reflection': 0.5},
    {'type': 'sphere', 'position': world_coords[1], 'radius': 0.25, 'color': np.array([0., 1., 0.]), 'reflection': 0.8},
    {'type': 'sphere', 'position': world_coords[2], 'radius': 0.25, 'color': np.array([0., 0., 1.]), 'reflection': 0.1},
    {'type': 'sphere', 'position': np.array([0., -10, 0.]), 'radius': 200., 'color': np.array([0.8, 0.8, 0.8]), 'reflection': 0.1}, # Ground
    rectangle,
    triangle,
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
            # Normal at the intersection point has to be updated for the new objects
            if nearest_object['type'] == 'sphere':
                N = M - nearest_object['position']
                N /= np.linalg.norm(N)
            else:
                N = nearest_object['normal'].copy()
                if np.dot(N, rayD) > 0: #flip
                    N= -N

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