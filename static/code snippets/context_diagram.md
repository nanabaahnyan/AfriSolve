```Mermaid
graph TD
    Poster[Problem Poster] -->|Posts problem, pays 20%, chats, signs off| AfriSolve
    Developer[Developer / Team] -->|Applies, pays 20%, updates progress, chats| AfriSolve
    Admin[Admin] -->|Verifies Ghana Card, approves dev, manages escrow, views chats| AfriSolve
    AfriSolve -->|Initiates payment, receives webhooks| Paystack[Paystack Gateway]
    AfriSolve -->|Sends email notifications| EmailServer[Email Service]
    AfriSolve -->|Stores files, images| CloudStorage[Cloudinary]

    style AfriSolve fill:#000,stroke:#333,stroke-width:4px

```