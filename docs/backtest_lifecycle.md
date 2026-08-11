```mermaid
stateDiagram-v2

    [*] --> PENDING

    PENDING --> RUNNING

    RUNNING --> COMPLETED
    RUNNING --> FAILED

    COMPLETED --> [*]
    FAILED --> [*]
```