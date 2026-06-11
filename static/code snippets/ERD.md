```Mermaid
erDiagram
    User {
        int id PK
        string email UK
        string password_hash
        string role
        string ghana_card_number UK
        string ghana_card_image_path
        boolean is_verified
        datetime created_at
    }

    Problem {
        int id PK
        int poster_id FK
        string title
        text description
        string category
        string location
        string status
        datetime posted_at
    }

    Team {
        int id PK
        string name
        int leader_id FK
    }

    TeamMember {
        int team_id FK
        int user_id FK
    }

    Application {
        int id PK
        int problem_id FK
        int applicant_id FK
        string status
        datetime applied_at
    }

    ProjectAgreement {
        int id PK
        int problem_id FK
        int total_cost_gHS
        int poster_20_percent
        int developer_20_percent
        datetime signed_at
    }

    EscrowTransaction {
        int id PK
        int agreement_id FK
        string party
        int amount
        string paystack_reference
        string status
    }

    ProgressUpdate {
        int id PK
        int problem_id FK
        int developer_id FK
        int milestone
        text notes
        string attachment_url
        datetime updated_at
    }

    ChatMessage {
        int id PK
        int problem_id FK
        int sender_id FK
        text message
        string file_url
        datetime sent_at
        boolean is_read
    }

    User ||--o{ Problem : posts
    User ||--o{ Application : submits
    User ||--o{ TeamMember : belongs_to
    User ||--o{ ChatMessage : writes
    User ||--o{ ProgressUpdate : makes
    User ||--o{ EscrowTransaction : pays

    Problem ||--o{ Application : receives
    Problem ||--|| ProjectAgreement : has
    Problem ||--o{ ChatMessage : contains
    Problem ||--o{ ProgressUpdate : tracks

    Team ||--o{ TeamMember : includes
    Team ||--o{ Application : applies_as

    EscrowTransaction ||--o{ PaystackWebhook : confirms
```