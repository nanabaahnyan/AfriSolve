```Mermaid
sequenceDiagram
    participant Poster as Poster (Browser)
    participant Dev as Developer (Browser)
    participant Admin as Admin (Browser)
    participant Django as Django Channels
    participant Redis as Redis (Channel Layer)
    participant DB as Database

    Poster->>Django: Connect to WebSocket (room: problem_123)
    Dev->>Django: Connect to WebSocket
    Admin->>Django: Connect to WebSocket

    Poster->>Django: Send message "Hello, team"
    Django->>Redis: Publish message to room problem_123
    Redis->>Django: Distribute to subscribers
    Django->>Dev: Deliver message
    Django->>Admin: Deliver message
    Django->>DB: Store message with timestamp

    Dev->>Django: Send file attachment
    Django->>CloudStorage: Upload file
    CloudStorage-->>Django: return file URL
    Django->>Redis: Publish file URL
    Redis->>Django: Distribute
    Django->>Poster: Show attachment

```