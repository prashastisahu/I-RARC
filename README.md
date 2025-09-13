# I-RARC: Incremental Resource Assignment and Reconfiguration Model

## Overview

The I-RARC (Incremental Resource Assignment and Reconfiguration) model is an optimization framework designed to minimize connection disruptions during network reconfiguration while efficiently allocating network resources. This implementation uses CPLEX to solve the linear programming problem.

## Problem Description

When network topologies need to be reconfigured (e.g., adding new connections, changing routing), existing connections may need to be disrupted. The I-RARC model finds the optimal reconfiguration strategy that:

- **Minimizes the number of disrupted existing connections**
- **Efficiently allocates network slots** across all links
- **Maintains network resource constraints**
- **Creates an optimal Reconfiguration Dependency Diagram (RDD)**

## Model Formulation

### Decision Variables

1. **`disc_i`** (Binary): Whether existing connection `i` must be disrupted
2. **`e_ci_cj`** (Binary): Whether there's an edge from connection `j` to connection `i` in the RDD
3. **`rs_ci_cj_nl`** (Integer): Number of slots assigned to connection `j` from connection `i`'s slots in link `nl`
4. **`ns_cj_nl`** (Integer): Number of new slots assigned to connection `j` in link `nl`

### Objective Function

```
Minimize: Σ disc_i + m * Σ e_ci_cj
```

Where `m` is a small constant (0.0001) to break ties.

### Constraints

1. **Slot Conservation**: Total slots assigned to each connection equals its requirement
2. **Resource Limits**: Slots reassigned from existing connections don't exceed their capacity
3. **Available Capacity**: New slot assignments don't exceed available unoccupied slots
4. **RDD Edge Logic**: If slots are reassigned, corresponding RDD edges must be activated
5. **AHC Ordering**: Maintains proper ordering in the Reconfiguration Dependency Diagram

## Input Data Requirements

The model expects an Excel file with the following sheets:

### Sheet: 'IRARC'
- **Pre-config demands per link**: Existing connections per network link
- **Post-config demands per link**: All connections (existing + new) per network link

### Sheet: 'No of tributory slots required'
- **CBc**: Number of slots required by each connection

### Sheet: 'Links'
- **IP links E**: List of all network links

## License
This implementation is provided for academic and research purposes. CPLEX licensing terms apply separately.

## Authors

- Prashasti Sahu
