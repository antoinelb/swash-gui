# Workflow Diagram

## Complete Simulation Workflow

```mermaid
graph TD
    A[YAML Configuration] --> B[Pydantic Validation]
    B --> C[Hash Generation]
    C --> D[Template Rendering]
    D --> E[Auxiliary File Generation]
    E --> F[SWASH Execution]
    F --> G[Output Files]
    G --> H[Analysis Processing]
    H --> I[Visualization]
    
    subgraph "Configuration Stage"
        A
        B
        C
    end
    
    subgraph "File Generation"
        D
        E
    end
    
    subgraph "Simulation"
        F
        G
    end
    
    subgraph "Post-Processing"
        H
        I
    end
```

## Detailed File Flow

```mermaid
graph LR
    subgraph "Input Files"
        A[config.yml]
        B[templates/INPUT]
    end
    
    subgraph "Generated Files"
        C[INPUT]
        D[bathymetry.txt]
        E[porosity.txt]
        F[structure_height.txt]
        G[vegetation_density.txt]
    end
    
    subgraph "SWASH Outputs"
        H[wg01.txt]
        I[wg02.txt]
        J[final_state.mat]
        K[PRINT]
    end
    
    subgraph "Analysis Outputs"
        L[data.csv]
        M[plots.png]
        N[data.json]
    end
    
    A --> C
    B --> C
    A --> D
    A --> E
    A --> F
    A --> G
    
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> L
    I --> L
    J --> L
    
    L --> M
    L --> N
```

## Configuration Processing

```mermaid
graph TD
    A[Raw YAML] --> B{Valid Syntax?}
    B -->|No| C[YAML Error]
    B -->|Yes| D[Pydantic Models]
    D --> E{Valid Parameters?}
    E -->|No| F[Validation Error]
    E -->|Yes| G[Hash Calculation]
    G --> H[Configuration Object]
    
    H --> I[Grid Config]
    H --> J[Water Config]
    H --> K[Breakwater Config]
    H --> L[Vegetation Config]
    H --> M[Numeric Config]
    
    I --> N[Template Context]
    J --> N
    K --> N
    L --> N
    M --> N
```

## Template Rendering Process

```mermaid
graph LR
    A[Config Object] --> B[Jinja2 Template]
    B --> C{Breakwater Enabled?}
    C -->|Yes| D[Include Breakwater Section]
    C -->|No| E[Skip Breakwater Section]
    
    D --> F{Vegetation Enabled?}
    E --> F
    F -->|Yes| G[Include Vegetation Section]
    F -->|No| H[Skip Vegetation Section]
    
    G --> I[Generate Wave Gauges]
    H --> I
    I --> J[Calculate Duration]
    J --> K[Rendered INPUT File]
```

## SWASH Execution Flow

```mermaid
graph TD
    A[INPUT File] --> B[SWASH Process]
    B --> C[Grid Setup]
    C --> D[Read Bathymetry]
    D --> E{Breakwater?}
    E -->|Yes| F[Read Porosity & Structure]
    E -->|No| G[Wave Generation]
    F --> H{Vegetation?}
    H -->|Yes| I[Read Vegetation Density]
    H -->|No| G
    I --> G
    G --> J[Time Integration]
    J --> K{Converged?}
    K -->|No| L[Next Time Step]
    L --> J
    K -->|Yes| M[Output Results]
    M --> N[STOP]
```

## Analysis Pipeline

```mermaid
graph TD
    A[Wave Gauge Files] --> B[Read Time Series]
    B --> C[Extract Metadata]
    C --> D[Combine Data]
    D --> E[Calculate Statistics]
    E --> F[Generate Plots]
    F --> G[Save Outputs]
    
    subgraph "Data Processing"
        B
        C
        D
    end
    
    subgraph "Visualization"
        E
        F
        G
    end
    
    H[CONFIG] --> C
    I[INPUT] --> C
```

## Error Handling Flow

```mermaid
graph TD
    A[User Input] --> B{Configuration Valid?}
    B -->|No| C[Show Validation Error]
    B -->|Yes| D[Generate Files]
    D --> E{SWASH Executable Found?}
    E -->|No| F[Installation Error]
    E -->|Yes| G[Run SWASH]
    G --> H{Simulation Successful?}
    H -->|No| I[Check PRINT File]
    H -->|Yes| J[Process Outputs]
    J --> K{Analysis Successful?}
    K -->|No| L[Check Output Files]
    K -->|Yes| M[Complete]
    
    C --> N[Fix Configuration]
    F --> O[Install SWASH]
    I --> P[Fix Parameters]
    L --> Q[Check File Permissions]
    
    N --> A
    O --> A
    P --> A
    Q --> A
```

## CLI Command Flow

```mermaid
graph LR
    A[swg create] --> B[Generate Template Config]
    C[swg run] --> D[Execute Simulation]
    E[swg analyze] --> F[Process Results]
    G[swg dashboard] --> H[Launch Web UI]
    I[swg clean] --> J[Remove Orphaned Sims]
    
    B --> K[config.yml]
    D --> L[simulation directory]
    F --> M[plots & data]
    H --> N[http://localhost:8000]
    J --> O[cleaned directories]
```

## Data Transformation Chain

```mermaid
graph TD
    A[YAML Parameters] --> B[Python Objects]
    B --> C[Jinja2 Variables]
    C --> D[SWASH Commands]
    D --> E[Numerical Arrays]
    E --> F[Output Files]
    F --> G[CSV Data]
    G --> H[Statistical Summaries]
    H --> I[Visualizations]
    
    style A fill:#e1f5fe
    style I fill:#f3e5f5
```

## Physical Process Representation

```mermaid
graph LR
    A[Incident Waves] --> B[Shoaling]
    B --> C[Breakwater Interaction]
    C --> D[Wave Breaking]
    D --> E[Transmission]
    E --> F[Setup & Runup]
    
    C --> G[Reflection]
    G --> H[Standing Waves]
    
    C --> I[Porous Flow]
    I --> J[Energy Dissipation]
    
    F --> K[Overtopping]
    
    subgraph "Vegetation Effects"
        L[Drag Forces]
        M[Flow Resistance]
        N[Additional Dissipation]
    end
    
    C --> L
    L --> M
    M --> N
    N --> E
```

## File Dependencies

```mermaid
graph TD
    A[config.yml] --> B[INPUT]
    A --> C[bathymetry.txt]
    A --> D[porosity.txt]
    A --> E[structure_height.txt]
    A --> F[vegetation_density.txt]
    
    B --> G[SWASH]
    C --> G
    D --> G
    E --> G
    F --> G
    
    G --> H[wg*.txt]
    G --> I[final_state.mat]
    G --> J[PRINT]
    
    H --> K[analysis.py]
    I --> K
    A --> K
    
    K --> L[data.csv]
    K --> M[plots.png]
    K --> N[data.json]
    
    style A fill:#ffeb3b
    style G fill:#4caf50
    style K fill:#2196f3
```

## Simulation States

```mermaid
stateDiagram-v2
    [*] --> ConfigCreated
    ConfigCreated --> Validated
    Validated --> FilesGenerated
    FilesGenerated --> SWASHRunning
    SWASHRunning --> SWASHCompleted
    SWASHRunning --> SWASHFailed
    SWASHCompleted --> AnalysisRunning
    AnalysisRunning --> Complete
    AnalysisRunning --> AnalysisFailed
    
    SWASHFailed --> [*]
    AnalysisFailed --> [*]
    Complete --> [*]
    
    ConfigCreated --> ConfigError
    Validated --> ValidationError
    FilesGenerated --> FileError
    
    ConfigError --> [*]
    ValidationError --> [*]
    FileError --> [*]
```