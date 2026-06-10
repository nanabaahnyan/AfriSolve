# Software Requirement Specification (SRS) for AfriSolve Hub

### Connecting Problem Posters with Skilled Developers across Ghana

#### Version: 1.0
#### Date: June 10, 2026
#### Status: Draft

## Table of Contents
1. Introduction
    * 1.1 Purpose
    * 1.2 Document Conventions
    * 1.3 Intended Audience
    * 1.4 Project Scope
    * 1.5 References
2. Overall Description
    * 2.1 Product Perspctive
    * 2.2 Product Functions
    * 2.3 User Classes and Characteristics
    * 2.4 Operating Environment
    * 2.5 Design and Implementation Constraints
    * 2.6 Assumptions and Dependencies
3. System Features and Functional Requirements
    * 3.1 User Management and Ghana Card Verification
    * 3.2 Problem Management Lifecycle
    * 3.3 Developer and Team Management
    * 3.4 Project Cost Assessment and Escrow Down Payment (Paystack).
    * 3.5 Progress Tracking (0% - 100% Milestones).
    * 3.6 Per-Problem Real-Time Chat System
    * 3.7 Notification System
    * 3.8 Admin Dashboard and Escrow Management
4. External Interface Requirements
    * 4.1 User Interfaces
    * Payment Interface (Paystack).
    * 4.3 File Storage Interface
5. Non-Functional Requirements
    * 5.1 Performance
    * 5.2 Security & Data Privacy
    * 5.3 Reliability & Availability
    * 5.4 Usability & Accessibility
    * 5.5 Legal & Compliance (Ghana)
6. Other Requirements (Training, Future APIs)
7. Appendix A: Glossary
8. Escrow & Forfeiture Decision Matrix
<br><br>

## 1. Introduction
### 1.1 Purpose
This SRS defines the functional and non-functional requirements for AfriSolve Hub, a web-based marketplace that connects Ghanaians with everyday problems to skilled developers who build software solutions. The platform manages problem submission, developer/team selection, financial commitment via a 20% down payment escrow model (Paystack), progress tracking, and solution handover.

### 1.2 Document Conventions
The document follow these conventions

| Term           | Description                     |
|----------------|---------------------------------|
| SHALL          | Mandatory requirement           |
| SHOULD         | Recommended                     |
| MAY            | Optional for future scalability |

Requirements are characterized as follows:

| Requirement Number | Description                  |
|----------------|----------------------------------|
| FR-XX          | Functional requirement           |
| NFR-XX         | Non-Functional requirement       |

### 1.3 Intended Audience
| Stakeholder    | Role                                                                      |
|----------------|---------------------------------------------------------------------------|
| Panelist       |   Officials who will review and approve<br>the requirements               |
| Development team      | Who will design and implement the system                           |
| Problem Poster | Those researchers and individuals who has<br>software problems to be solved |

### 1.4 Project Scope
#### In Scope:
* User registration with mandatory Ghana Card upload and admin verification.
* Problem posting by verified users (title, description, category, attachments).
* Public "Open Problems" board.
* Developer/Team application to problems.
* Admin approval workflow for developer assignments.
* Project Cost Assessment (poster & developer mutually agree on total cost).
* Escrow Down Payment: 20% from poster + 20% from developer via Paystack.
* Progress tracking: 0%, 30%, 50%, 80%, 100% with notes.
* Per-problem real-time chat (Poster, Developer/Team, Admin).
* Forfeiture logic: If either party quits, their 20% transfers to the other party.
* Admin dashboard: User/problem/escrow/chat oversight.

#### Out of Scope
* Mobile native app (Flutter/React Native).
* Automated Ghana Card verification via NIA API (manual admin review in MVP).
* Public API for external problem sources.
* Advanced dispute resolution automation (admin-led in MVP).

### 1.5 References
* AfriSolve Hub Project Plan
* Paystack API Documentation

## 2. Overall Description
### 2.1 Product Perspective
AfriSolve Hub is a standalone web application built on Python Django (backend + templating frontend). It integrates with:
* Paystack for payments, escrow, and transfers.
* SendGrid for Email messages
* Cloudinary Spaces for file storage (Ghana Card images, attachments).

### 2.2 Product Functions (High-Level)
1. Verified Identity: Ghana Card-based registration.
2. Problem Marketplace: Post, browse, apply, assign.
3. Financial Commitment: 20/20 down payment escrow.
4. Team Formation: Developers can create teams and apply as a unit.
5. Progress & Chat: Milestone tracking + real-time per-problem chat.
6. Admin Control: Escrow release, forfeiture, dispute resolution.

### 2.3 User Classes and Characteristics
| User Class     | Description                     | Needs                 |
|----------------|---------------------------------|------------------------------------------------|
| Problem Poster | Individual, business, or researcher<br>with a real-world problem.| Post problems, assess cost,<br>pay 20%, monitor progress, chat with dev.|
| Developer      | Skilled developer building portfolio/income. | Browse problems, apply, accept terms, pay 20%, update progress.|
| Team Leader    | Developer who creates a team. | Invite members, apply as team, manage progress, pay team's 20%. |
| Team Member    | 	Developer invited to a team. | View assigned problem, chat, upload files. |
| Admin          | Platform operator. | Verify Ghana Cards, approve developer assignments,<br>manage escrow, resolve disputes, view all chats.|

### 2.4 Operating Environment
* Web: Modern browsers (Chrome, Firefox, Safari, Edge) on desktop and mobile.
* Responsive: Works on smartphones, computers, and tablets.
* Connectivity: Works on low-bandwidth connections (progressive enhancement).
* Hosting: Render (Django + PostgreSQL + Redis).

### 2.5 Design and Implementation Constraints
* Must use Django templating engine.
* Must integrate Paystack for all monetary transactions.
* Must encrypt Ghana Card images and numbers at rest.
* Must support Ghana Cedis (GHS) only.
* Must have admin-mediated escrow release always.

### 2.6 Assumptions and Dependencies
* Paystack account is active and supports Transfers API and webhooks.
* Admins are available to verify Ghana Cards within 24-48 hours.
* Ghana Card images are legible and provided by users.
* Both parties understand the 20% forfeiture terms before paying.

## 3. System Features and Functional Requirements
### 3.1 User Management and Ghana Card Verification
| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-01          | The system SHALL allow users to register with email,<br>password, and role (Poster, Developer). |
| FR-02          | The system SHALL require Ghana Card number (format GHA-XXXXXXXXX-X)<br>and a photo upload of the front of the card during registration. |
| FR-03          | The system SHALL store Ghana Card number and image<br>encrypted with access restricted to admins. |
| FR-04          | The system SHALL set new accounts to "Pending<br>Verification" until an admin approves the Ghana Card. |
| FR-05          | The system SHALL prohibit pending users from posting<br>problems or applying for projects. |
| FR-06          | The system SHALL display a "Verified" badge on profiles of<br>approved users. |
| FR-07          | The system SHALL allow admins to reject a Ghana Card<br>submission with a reason (e.g., illegible). |
| FR-08          | 	The system SHALL prevent duplicate registrations using the<br>same Ghana Card number. |

### 3.2 Problem Management Lifecycle
| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-09          | The system SHALL allow users to register with email,<br>password, and role (Poster, Developer). |
| FR-10          | The system SHALL require Ghana Card number (format GHA-XXXXXXXXX-X)<br>and a photo upload of the front of the card during registration. |
| FR-11          | The system SHALL store Ghana Card number and image<br>encrypted with access restricted to admins. |
| FR-12          | The system SHALL set new accounts to "Pending<br>Verification" until an admin approves the Ghana Card. |
| FR-13          | The system SHALL prohibit pending users from posting<br>problems or applying for projects. |

### 3.3 Developer & Team Management

| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-01          | The system SHALL allow users to register with email,<br>password, and role (Poster, Developer). |
| FR-02          | The system SHALL require Ghana Card number (format GHA-XXXXXXXXX-X)<br>and a photo upload of the front of the card during registration. |
| FR-03          | The system SHALL store Ghana Card number and image<br>encrypted with access restricted to admins. |
| FR-04          | The system SHALL set new accounts to "Pending<br>Verification" until an admin approves the Ghana Card. |
| FR-05          | The system SHALL prohibit pending users from posting<br>problems or applying for projects. |
| FR-06          | The system SHALL display a "Verified" badge on profiles of<br>approved users. |
| FR-07          | The system SHALL allow admins to reject a Ghana Card<br>submission with a reason (e.g., illegible). |
| FR-08          | 	The system SHALL prevent duplicate registrations using the<br>same Ghana Card number. |