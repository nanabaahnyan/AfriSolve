```Mermaid
graph TD
    subgraph SystemBoundary[AfriSolve Hub - Poster Functions]
        UC1[Register & Submit Ghana Card]
        UC2[Post a New Problem]
        UC3[Assess Project Cost with Developer]
        UC4[Pay 20% Down Payment via Paystack]
        UC5[Chat with Developer in Problem Room]
        UC6[Monitor Progress Milestones 0-100%]
        UC7[Sign Off on Completion]
        UC8[Receive Forfeited Funds if Developer Quits]
    end

    Poster([Problem Poster]) --> UC1
    Poster --> UC2
    Poster --> UC3
    Poster --> UC4
    Poster --> UC5
    Poster --> UC6
    Poster --> UC7
    Poster --> UC8
```