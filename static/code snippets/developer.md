```Mermaid
graph TD
    subgraph SystemBoundary[AfriSolve Hub - Developer Functions]
        UC1[Register & Submit Ghana Card]
        UC2[Browse Open Problems Board]
        UC3[Request to Solve a Problem]
        UC4[Create / Manage a Team]
        UC5[Assess Project Cost with Poster]
        UC6[Pay 20% Down Payment via Paystack]
        UC7[Update Progress Milestones 0-100%]
        UC8[Chat with Poster & Admin]
        UC9[Receive Forfeited Funds if Poster Quits]
    end

    Developer([Developer / Team]) --> UC1
    Developer --> UC2
    Developer --> UC3
    Developer --> UC4
    Developer --> UC5
    Developer --> UC6
    Developer --> UC7
    Developer --> UC8
    Developer --> UC9

```