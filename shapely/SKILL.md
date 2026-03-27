---
name: shapely
description: Use when working with 2D vector geometry in Python — creating, manipulating, measuring, querying spatial relationships, or performing set operations on points, lines, and polygons using Shapely
---

# Shapely

Python library for manipulation and analysis of planar geometric objects, based on the GEOS library.

- **Repository**: https://github.com/shapely/shapely
- **Documentation**: https://shapely.readthedocs.io/
- **PyPI**: https://pypi.org/project/shapely/
- **License**: BSD-3-Clause
- **Requirements**: Python >= 3.11, GEOS >= 3.10, NumPy >= 1.23

## Geometry Types

| Type | Class | Description |
|------|-------|-------------|
| Point | `shapely.Point` | Single coordinate (x, y [, z [, m]]) |
| LineString | `shapely.LineString` | Ordered sequence of 2+ points |
| LinearRing | `shapely.LinearRing` | Closed, simple LineString |
| Polygon | `shapely.Polygon` | Exterior ring + optional holes |
| MultiPoint | `shapely.MultiPoint` | Collection of Points |
| MultiLineString | `shapely.MultiLineString` | Collection of LineStrings |
| MultiPolygon | `shapely.MultiPolygon` | Collection of Polygons |
| GeometryCollection | `shapely.GeometryCollection` | Heterogeneous collection |

Z coordinates are **ignored for all spatial analysis** — operations are performed in the x-y plane only.

## Dual API Pattern

Shapely provides two APIs. Prefer the **function-based API** for arrays and performance; use the **OOP API** for scalar convenience.

### Function-based (vectorized, NumPy ufunc)

All functions release the GIL during GEOS execution, support NumPy broadcasting, and handle arrays natively.

```python
import shapely
import numpy as np

geoms = np.array([shapely.Point(0, 0), shapely.Point(1, 1)])
shapely.area(geoms)                    # array of floats
shapely.contains(polygon, geoms)       # array of bools
shapely.buffer(geoms, 1.0)            # array of polygons
shapely.distance(geoms, other)        # array of distances
```

### OOP (method-based, scalar)

```python
from shapely import Point, Polygon

p = Point(0, 0)
poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
p.buffer(10)
p.distance(Point(1, 1))
poly.area                  # property
poly.contains(p)
poly.intersection(other)
```

### Operator overloading

```python
geom1 & geom2    # intersection
geom1 | geom2    # union
geom1 - geom2    # difference
geom1 ^ geom2    # symmetric_difference
```

## Geometry Creation

### From coordinates (OOP)

```python
from shapely import Point, LineString, LinearRing, Polygon
from shapely import MultiPoint, MultiLineString, MultiPolygon, GeometryCollection

Point(0, 0)
Point(0, 0, 5)                                    # 3D
LineString([(0, 0), (1, 1), (2, 0)])
LinearRing([(0, 0), (1, 0), (1, 1), (0, 0)])      # must be closed
Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])         # auto-closes shell
Polygon(shell_coords, [hole1_coords, hole2_coords])
MultiPoint([(0, 0), (1, 1)])
MultiLineString([[(0, 0), (1, 1)], [(2, 2), (3, 3)]])
MultiPolygon([poly1, poly2])
GeometryCollection([point, line, poly])
```

### From coordinates (vectorized)

```python
import shapely

shapely.points([[0, 1], [2, 3]])                  # array of Points
shapely.points(0, 1)                               # scalar Point
shapely.linestrings([[[0, 0], [1, 1]], [[2, 2], [3, 3]]])
shapely.linearrings([[0, 0], [1, 0], [1, 1]])     # auto-closes
shapely.polygons(shell, holes=[hole1, hole2])
shapely.box(xmin, ymin, xmax, ymax)               # rectangle(s)
shapely.multipoints([pt1, pt2])
shapely.multilinestrings(...)
shapely.multipolygons(...)
shapely.geometrycollections(...)
```

### From serialization formats

```python
# WKT
shapely.from_wkt("POINT (0 0)")
shapely.to_wkt(geom, rounding_precision=6, trim=True)

# WKB
shapely.from_wkb(b'\x01\x01...')
shapely.to_wkb(geom, hex=False, flavor="extended")

# GeoJSON
shapely.from_geojson('{"type":"Point","coordinates":[0,0]}')
shapely.to_geojson(geom, indent=None)

# GeoArrow ragged arrays
shapely.from_ragged_array(geometry_type, coords, offsets)
shapely.to_ragged_array(geometries)
```

### From/to GeoJSON-like dict (`__geo_interface__`)

```python
from shapely.geometry import shape, mapping

geom = shape({"type": "Point", "coordinates": [0, 0]})
d = mapping(geom)  # {"type": "Point", "coordinates": (0.0, 0.0)}
```

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

## Validation

```python
shapely.is_valid(geom)
shapely.is_valid_reason(geom)
shapely.make_valid(geom, method="linework")   # or "structure"
```

## Prepared Geometry

Caches spatial index for repeated predicate tests against the same geometry.

```python
shapely.prepare(geom)            # in-place, returns True if newly prepared
shapely.destroy_prepared(geom)   # free cache
shapely.is_prepared(geom)
```

## Missing Values

`None` represents missing geometries. Consistent behavior:
- Predicates return `False`
- Measurements return `nan`
- Constructive operations return `None`

Use `shapely.is_missing(obj)` to check, distinct from `shapely.is_empty(geom)`.

## Important Caveats

1. **Z ignored in analysis**: All spatial operations work in x-y plane only. Geometries with different z values may still intersect or be equal.

2. **`contains` excludes boundary**: `contains(line, endpoint)` is `False`. Use `covers()` or `intersects()` if you need boundary inclusion.

3. **`set_coordinates` modifies in-place**: Copy geometry first with `.copy()` if originals must be preserved.

4. **`clip_by_rect` may produce invalid output**: The fast clip is not guaranteed to yield valid topology.

5. **WKB drops LinearRing**: LinearRings become LineStrings during WKB serialization.

6. **`to_geojson` drops Z**: Third dimension is silently discarded; LinearRing outputs as `null`.

7. **OOP vs function `buffer` defaults differ**: `Point(0,0).buffer(1)` uses `quad_segs=16`; `shapely.buffer(Point(0,0), 1)` uses `quad_segs=8`.

8. **`set_precision` changes vertex order**: Returned geometry is in "mild canonical form" — vertex order should not be relied upon.

9. **NaN coordinates**: Creating geometries with NaN/Inf is allowed by default. Use `handle_nan='error'` or `handle_nan='skip'` in creation functions to control this.

10. **Prepared state not preserved**: After any operation producing a new geometry, `prepare()` must be called again.

11. **GEOS version gates**: `concave_hull`, `constrained_delaunay_triangles`, `remove_repeated_points` require GEOS >= 3.11. `coverage_simplify`, `has_m`, `get_m` require GEOS >= 3.12.

## Common Patterns

### Point-in-polygon test for many points
```python
from shapely import STRtree, points

pts = points(np.random.rand(10000, 2))
tree = STRtree(pts)
idx = tree.query(polygon, predicate="intersects")
inside_points = pts[idx]
```

### Batch union of many polygons
```python
result = shapely.union_all(polygon_array)
```

### Coordinate projection (e.g., with pyproj)
```python
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

def project(coords):
    x, y = transformer.transform(coords[:, 0], coords[:, 1])
    return np.column_stack([x, y])

projected = shapely.transform(geom, project)
```

### Extract all coordinates from mixed geometries
```python
coords = shapely.get_coordinates(geom_array, include_z=False)
# coords shape: (N, 2)
```

### Spatial join pattern
```python
tree = STRtree(right_geoms)
left_idx, right_idx = tree.query(left_geoms, predicate="intersects")
# left_idx[i] and right_idx[i] are paired matches
```

## Package Structure

```
shapely/
├── __init__.py              # Top-level re-exports
├── geometry/                # OOP geometry classes
│   ├── base.py              # BaseGeometry (all methods/properties)
│   ├── point.py, linestring.py, polygon.py
│   ├── multipoint.py, multilinestring.py, multipolygon.py
│   ├── collection.py        # GeometryCollection
│   └── geo.py               # shape(), mapping(), box()
├── constructive.py          # buffer, simplify, hull, etc.
├── predicates.py            # contains, intersects, etc.
├── set_operations.py        # union, intersection, difference, etc.
├── measurement.py           # area, length, distance, bounds
├── creation.py              # points(), linestrings(), polygons(), box()
├── coordinates.py           # transform, get/set_coordinates
├── io.py                    # from/to WKT, WKB, GeoJSON
├── strtree.py               # STRtree spatial index
├── linear.py                # line_interpolate_point, line_merge, etc.
├── affinity.py              # rotate, scale, skew, translate
├── validation.py            # make_valid
├── prepared.py              # PreparedGeometry
├── ops.py                   # Legacy: split, nearest_points, etc.
├── algorithms/              # polylabel, oriented_envelope fallback
└── plotting.py              # Matplotlib helpers (experimental)
```
