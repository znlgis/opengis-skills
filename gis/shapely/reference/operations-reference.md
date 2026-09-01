# Shapely Operations API Reference

Constructive operations, predicates, set operations, measurements, indexing and coordinate operations split from SKILL.md.

---

## Constructive Operations

All available as `shapely.<function>(geometry, ...)`.

| Function | Description |
|----------|-------------|
| `buffer(geom, distance, quad_segs=8, cap_style="round", join_style="round", mitre_limit=5.0, single_sided=False)` | Minkowski sum/difference with circle |
| `offset_curve(geom, distance, ...)` | Parallel curve at given distance |
| `centroid(geom)` | Geometric center |
| `point_on_surface(geom)` | Point guaranteed inside geometry |
| `boundary(geom)` | Topological boundary |
| `convex_hull(geom)` | Minimum convex enclosure |
| `concave_hull(geom, ratio)` | Concave enclosure (GEOS >= 3.11) |
| `envelope(geom)` | Axis-aligned bounding box |
| `oriented_envelope(geom)` | Minimum-area rotated rectangle |
| `minimum_bounding_circle(geom)` | Smallest enclosing circle |
| `simplify(geom, tolerance, preserve_topology=True)` | Douglas-Peucker simplification |
| `snap(geom, reference, tolerance)` | Snap vertices to reference |
| `segmentize(geom, max_segment_length)` | Densify by adding vertices |
| `reverse(geom)` | Reverse coordinate order |
| `normalize(geom)` | Canonical coordinate ordering |
| `make_valid(geom, method="linework")` | Repair invalid geometry |
| `build_area(geom)` | Polygonize from linework |
| `clip_by_rect(geom, xmin, ymin, xmax, ymax)` | Fast rectangle clip (may produce invalid output) |
| `delaunay_triangles(geom, tolerance=0.0, only_edges=False)` | Delaunay triangulation |
| `constrained_delaunay_triangles(geom)` | Constrained Delaunay (GEOS >= 3.11) |
| `voronoi_polygons(geom, tolerance=0.0, extend_to=None)` | Voronoi diagram |
| `polygonize(geometries)` | Create polygons from linework |
| `polygonize_full(geometries)` | Polygonize with dangles, cuts, invalids |
| `node(geom)` | Full noding of linear geometry |
| `remove_repeated_points(geom, tolerance=0.0)` | Remove duplicate vertices (GEOS >= 3.11) |
| `maximum_inscribed_circle(geom, tolerance=1.0)` | Largest inscribed circle |
| `minimum_width(geom)` | Minimum width line |
| `orient_polygons(geom, sign=1.0)` | Enforce ring orientation |

## Spatial Predicates

All return `bool` (or bool array). Available as `shapely.<function>(a, b)` or `a.<method>(b)`.

| Function | Description |
|----------|-------------|
| `contains(a, b)` | B entirely inside A (boundary excluded) |
| `contains_properly(a, b)` | B inside A with no shared boundary |
| `contains_xy(geom, x, y)` | Fast point-in-geometry test |
| `covered_by(a, b)` | No point of A outside B |
| `covers(a, b)` | No point of B outside A |
| `crosses(a, b)` | A and B spatially cross |
| `disjoint(a, b)` | No shared space |
| `dwithin(a, b, distance)` | Within given distance |
| `equals(a, b)` | Topologically equal |
| `equals_exact(a, b, tolerance)` | Structurally equal within tolerance |
| `intersects(a, b)` | Share any space |
| `intersects_xy(geom, x, y)` | Fast point-intersects test |
| `overlaps(a, b)` | Partial overlap, same dimension |
| `touches(a, b)` | Only boundaries touch |
| `within(a, b)` | A entirely inside B |
| `relate(a, b)` | DE-9IM intersection matrix string |
| `relate_pattern(a, b, pattern)` | Test DE-9IM pattern match |
| `is_valid(geom)` | Well-formed geometry |
| `is_valid_reason(geom)` | Description if invalid |
| `is_empty(geom)` | Empty geometry test |
| `is_simple(geom)` | No self-intersections |
| `is_ring(geom)` | Closed and simple |
| `is_closed(geom)` | First == last point |
| `is_ccw(geom)` | Counter-clockwise ring orientation |
| `has_z(geom)` / `has_m(geom)` | Dimension checks |

## Set-Theoretic Operations

| Function | Description |
|----------|-------------|
| `intersection(a, b, grid_size=None)` | Shared geometry |
| `intersection_all(geometries)` | N-way intersection |
| `union(a, b, grid_size=None)` | Merge two geometries |
| `union_all(geometries)` | N-way union |
| `difference(a, b, grid_size=None)` | A minus B |
| `symmetric_difference(a, b, grid_size=None)` | XOR of A and B |
| `coverage_union(a, b)` | Optimized union for non-overlapping polygons |
| `coverage_union_all(geometries)` | N-way coverage union |

All binary operations support optional `grid_size` for precision snapping.

## Measurements

| Function | Description |
|----------|-------------|
| `area(geom)` | Area of polygon(s) |
| `length(geom)` | Length of line / polygon perimeter |
| `distance(a, b)` | Minimum Cartesian distance |
| `hausdorff_distance(a, b, densify=None)` | Hausdorff distance |
| `frechet_distance(a, b, densify=None)` | Frechet distance |
| `bounds(geom)` | (minx, miny, maxx, maxy) per geometry |
| `total_bounds(geometries)` | Combined bounds of all geometries |
| `minimum_clearance(geom)` | Smallest move to invalidate |
| `minimum_bounding_radius(geom)` | Radius of minimum bounding circle |

## STRtree Spatial Index

```python
from shapely import STRtree

tree = STRtree(geometries, node_capacity=10)

# Bounding-box query — returns indices
idx = tree.query(geometry)                            # shape (n,)
idx = tree.query(geom_array)                          # shape (2, n)

# With predicate filter
idx = tree.query(geom, predicate="intersects")
# predicates: intersects, within, contains, overlaps, crosses,
#             touches, covers, covered_by, contains_properly, dwithin

# Distance-based query
idx = tree.query(geom, predicate="dwithin", distance=5.0)

# Nearest neighbor
idx = tree.nearest(geometry)                          # single nearest

# All nearest with options
result = tree.query_nearest(
    geometry,
    max_distance=10,
    return_distance=True,   # returns (indices, distances)
    exclusive=False,
    all_matches=True
)
```

## Geometry Accessors

```python
shapely.get_type_id(geom)                  # GeometryType enum int
shapely.get_dimensions(geom)               # 0=point, 1=line, 2=polygon
shapely.get_coordinate_dimension(geom)     # 2, 3, or 4
shapely.get_x(point)                       # x coordinate
shapely.get_y(point)                       # y coordinate
shapely.get_z(point)                       # z coordinate
shapely.get_num_points(linestring)
shapely.get_point(linestring, index)       # extract nth point
shapely.get_exterior_ring(polygon)
shapely.get_interior_ring(polygon, index)
shapely.get_num_interior_rings(polygon)
shapely.get_geometry(collection, index)
shapely.get_num_geometries(collection)
shapely.get_parts(geom, return_index=False)
shapely.get_rings(polygon, return_index=False)
shapely.get_coordinates(geom, include_z=False, return_index=False)
shapely.set_coordinates(geom, new_coords)  # modifies in-place!
shapely.count_coordinates(geom)
shapely.get_srid(geom) / shapely.set_srid(geom, srid)
shapely.get_precision(geom) / shapely.set_precision(geom, grid_size)
shapely.force_2d(geom) / shapely.force_3d(geom, z=0)
```

## Affine Transforms

```python
from shapely.affinity import affine_transform, rotate, scale, skew, translate

affine_transform(geom, [a, b, d, e, xoff, yoff])   # 2D 6-element matrix
affine_transform(geom, matrix_12)                    # 3D 12-element matrix
rotate(geom, angle, origin="center")                 # degrees CCW
scale(geom, xfact=1.0, yfact=1.0, zfact=1.0, origin="center")
skew(geom, xs=0, ys=0, origin="center")              # degrees
translate(geom, xoff=0.0, yoff=0.0, zoff=0.0)
```

## Coordinate Transforms

```python
# Vectorized transform (fixed coordinate count)
shapely.transform(geom, lambda coords: coords * 2)
shapely.transform(geom, func, include_z=True)

# Per-ring transform (may change coordinate count)
shapely.transform_coordseq(geom, func)
```

## Linear Referencing

```python
shapely.line_interpolate_point(line, distance, normalized=False)
shapely.line_locate_point(line, point, normalized=False)
shapely.line_merge(multilinestring, directed=False)
shapely.shared_paths(a, b)
shapely.shortest_line(a, b)
```

