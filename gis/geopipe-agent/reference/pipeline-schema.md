# GeoPipeAgent Pipeline YAML Schema

## Top-level Structure

```yaml
pipeline:
  name: "Pipeline Name"            # Required: pipeline name
  description: "Description"       # Optional: pipeline description
  crs: "EPSG:4326"                # Optional: default CRS
  variables:                       # Optional: reusable variables
    var_name: value
  steps:                           # Required: list of steps
    - id: step_id                  # Required: unique step identifier [a-z0-9_-]
      use: category.action         # Required: step registry ID
      params:                      # Step-specific parameters
        key: value
      on_error: fail               # Optional: fail/skip/retry (default: fail)
      when: "$step_id.issues_count > 0"  # Optional: conditional execution
      backend: native_python           # Optional: specific backend to use
   outputs:                         # Optional: pipeline output declarations
     result: "$step_id.output"
```

## Reference Syntax

| Syntax | Description | Example |
|--------|-------------|---------|
| `$step_id` | Shorthand for `$step_id.output` | `$buffer` |
| `$step_id.output` | Reference step output | `$buffer.output` |
| `$step_id.stats` | Reference step stats | `$buffer.stats` |
| `$step_id.<key>` | Reference stats/metadata key | `$buffer.feature_count` |
| `${var_name}` | Variable substitution | `${input_path}` |

## Step ID Rules

- Only lowercase letters, digits, underscores, and hyphens: `[a-z0-9_-]`
- No dots (`.`) — dots are reserved for attribute access in references
- Must be unique within a pipeline

## Conditional Execution (``when``)

Steps can include a ``when`` expression to control execution:

```yaml
- id: fix-geometries
  use: qc.geometry_validity
  params:
    input: "$data"
    auto_fix: true
  when: "$check.issues_count > 0"
```

Supported syntax:
- Comparisons: ``$step.attr == value``, ``!=``, ``>``, ``<``, ``>=``, ``<=``
- Boolean operators: ``and``, ``or``, ``not``
- Variable substitution: ``${var_name}``
- Truthy check: ``$step_id.output`` (true if output is non-empty)

## Error Handling

Each step can specify `on_error`:
- `fail` (default): Stop pipeline execution
- `skip`: Skip this step, continue with next
- `retry`: Retry the step up to 3 times with backoff
