# Graph Visualizer Project

## Introduction
The Graph Visualizer is a dynamic tool designed to visualize knowledge graphs using D3.js. It is capable of rendering complex networks of interconnected entities such as objects, locations, organizations, and concepts, among others. This visualization aids in understanding relationships and groupings within a dataset.

## JSON Structure
The tool expects a Base64 encoded JSON string passed in the URL under the 'data' parameter. The JSON should have the following structure:

### Nodes Array
- **`id`**: Unique identifier for each node.
- **`type`**: Category of the entity (e.g., 'entity', 'location', 'organization', 'person', 'condition', etc.).
- **`group`**: Numerical field indicating the cluster to which the node belongs.

### Links Array
Defines relationships between nodes with the following fields:
- **`source`**: 'id' of the node where the relationship originates.
- **`target`**: 'id' of the node where the relationship is directed.
- **`label`**: Descriptive label indicating the nature of the relationship.
- **`strength`**: Numerical value (0.1 to 1.0) representing the strength of the relationship.
- **`rationale`**: Textual description indicating the rationale for the strength of each relationship.

### Groups Array
Indicates the rationale for the grouping with the following fields:
- **`group_id`**: The group number.
- **`rationale`**: Textual description of the similarities between the nodes in the group.

## Usage
1. Encode your structured JSON as a Base64 string.
2. Append the encoded string to the URL as the 'data' parameter.
3. Load the URL in a web browser to visualize the graph.

## Requirements
- Every node in 'nodes' must appear at least once in 'links' as either a 'source' or a 'target'.
- Every 'source' and 'target' in the Links array must correspond to an 'id' in the Nodes array.
- The JSON structure must strictly follow the described format for accurate visualization.

## Example
Below is an example of how the JSON structure should look before encoding:

```json
{
  "nodes": [
    {"id": "1", "type": "person", "group": 1},
    {"id": "2", "type": "organization", "group": 2}
  ],
  "links": [
    {"source": "1", "target": "2", "label": "member of", "strength": 0.8, "rationale": "Person 1 is an active member of Organization 2."}
  ],
  "groups": [
    {"group_id": 1, "rationale": "Individual entities."},
    {"group_id": 2, "rationale": "Organizational entities."}
  ]
}



