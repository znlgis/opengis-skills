# GeoPipeAgent Skill

## What is GeoPipeAgent?

GeoPipeAgent is an AI-native GIS analysis pipeline framework. You (AI) can generate YAML pipeline files to perform GIS analysis tasks, and the framework will execute them and return structured JSON reports.

## How to Use

1. **Understand the task**: What GIS analysis does the user need?
2. **Choose steps**: Refer to `reference/steps-reference.md` for available steps
3. **Write YAML pipeline**: Generate a pipeline YAML following `reference/pipeline-schema.md`
4. **Execute**: Run `geopipe-agent run <pipeline.yaml>`
5. **Interpret results**: Parse the JSON execution report

## Quick Example

```yaml
pipeline:
  name: "Buffer Analysis"
  steps:
    - id: read
      use: io.read_vector
      params:
        path: "data/roads.shp"
    - id: buffer
      use: vector.buffer
      params:
        input: "$read"
        distance: 500
    - id: save
      use: io.write_vector
      params:
        input: "$buffer"
        path: "output/buffer_result.geojson"
  outputs:
    result: "$save"
```

## Key Concepts

- **Steps** are identified by `category.action` (e.g., `io.read_vector`, `vector.buffer`)
- **Step references** use `$step_id` (shorthand for `$step_id.output`) or `$step_id.attribute` (e.g., `$buffer.feature_count`)
- **Variables** use `${var_name}` syntax
- **IO steps** (io.*) read/write files directly; **analysis steps** use GIS backends

## Available Step Categories

- `io.*` — Data I/O (read/write vector and raster)
- `vector.*` — Vector analysis (buffer, clip, reproject, dissolve, simplify, query, overlay)
- `raster.*` — Raster analysis (reproject, clip, calc, stats, contour)
- `analysis.*` — Advanced analysis (voronoi, heatmap, interpolate, cluster)
- `network.*` — Network analysis (shortest_path, service_area, geocode)
- `qc.*` — Data quality check (geometry_validity, topology, attribute_completeness, attribute_domain, value_range, duplicate_check, crs_check, raster_nodata, raster_value_range, raster_resolution)

## QC (Quality Check) Steps

QC steps follow a **"Check and Passthrough"** pattern:
- Input data is passed through unchanged as `output`
- Issues are collected in `$step.issues` and problem features in `$step.issues_gdf`
- Multiple QC steps can be chained: `qc.check1 → qc.check2 → qc.check3`
- Pipeline reports include a `qc_summary` section aggregating all issues

## Files

- `reference/steps-reference.md` — Complete step parameter reference
- `reference/pipeline-schema.md` — YAML pipeline schema documentation
- `cookbook/` — Example pipeline YAML files
