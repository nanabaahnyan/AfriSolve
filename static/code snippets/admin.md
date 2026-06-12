```Mermaid
graph TD
    subgraph SystemBoundary[AfriSolve Hub - Admin Functions]
        UC1[View Ghana Card Verification Queue]
        UC2[Approve / Reject Ghana Card Submissions]
        UC3[View Developer Application Queue]
        UC4[Approve / Reject Developer Assignments]
        UC5[View All Per-Problem Chat Rooms]
        UC6[Manage Escrow – Release / Forfeit Funds]
        UC7[Resolve Disputes using Chat Logs & Progress]
        UC8[View Analytics & Reports]
        UC9[Generate Project Agreement PDFs]
    end

    Admin([Admin]) --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9

```