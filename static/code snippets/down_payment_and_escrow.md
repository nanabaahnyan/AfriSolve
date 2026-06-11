```Mermaid
flowchart TD
    A[Admin approves developer/team] --> B[Both parties agree on total project cost]
    B --> C[System generates 20% payment links for poster & developer]
    C --> D{Both pay via Paystack?}
    D -->|No, one party fails to pay| E[Project not started. No escrow held]
    D -->|Yes| F[Paystack webhook confirms both payments]
    F --> G[Funds held in platform escrow account]
    G --> H[Project status = 'In Progress']
    H --> I{What happens next?}
    I -->|Developer abandons| J[Admin transfers developer's 20% to poster]
    I -->|Poster cancels| K[Admin transfers poster's 20% to developer]
    I -->|Both complete successfully| L[Admin releases both 20% back to respective parties]
    I -->|Dispute| M[Admin reviews chat & progress, decides outcome]
```