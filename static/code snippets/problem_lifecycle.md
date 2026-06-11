```Mermaid
flowchart LR
    A[Poster submits problem] --> B[Problem appears on Open Board]
    B --> C[Developer/team applies]
    C --> D{Admin approves?}
    D -->|No| E[Problem remains open]
    D -->|Yes| F[Problem locked to developer/team]
    F --> G[Cost assessment & down payments]
    G --> H[Developer updates progress 0% → 30% → 50% → 80% → 100%]
    H --> I[Poster confirms delivery]
    I --> J[Admin releases escrow / applies to final payment]
    J --> K[Project completed]
```