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
| FR-09          | Verified posters SHALL be able to create a problem with:<br>title, category, detailed description, location/area,<br>business impact (optional), and file attachments. |
| FR-10          | The system SHALL display a public "Open Problems"<br>board showing only unassigned problems. |
| FR-11          | The system SHALL allow filtering of open problems by<br>category, date, and location. |
| FR-12          | Once a developer/team is approved by an admin, the<br>problem status SHALL change to "Assigned / Locked"<br>and become read-only to the public. |
| FR-13          | Locked problems SHALL remain fully visible (with chat<br>and progress) to the assigned developer, poster, and<br>admin only. |

### 3.3 Developer & Team Management

| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-14          | Verified developers SHALL be able to click "Request to<br>Solve" on any open problem, submitting estimated<br>duration and a short proposal. |
| FR-15          | Developers SHALL be able to create a team (team name,<br>description) and invite other verified developers by<br>email/username. |
| FR-16          | Invited developers SHALL receive a notification and can<br>accept/decline. |
| FR-17          | A team leader SHALL apply to a problem on behalf of the<br>entire team. |
| FR-18          | Admin SHALL review individual or team applications and<br>either approve or reject. |
| FR-19          | Upon approval, the problem SHALL be locked to that<br>developer/team, and the start date recorded. |

### 3.4 Project Cost Assessment & Escrow Down Payment (Paystack)
| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-20          | After admin approval, the system SHALL present a<br>"Project Cost Assessment" form to both poster and<br>developer (separately or jointly). |
| FR-21          | Both parties SHALL agree on a total project cost (in GHS)<br>via the platform. |
| FR-22          | The system SHALL calculate 20% of the agreed total for<br>the poster and 20% for the developer. |
| FR-23          | The system SHALL generate a Paystack payment<br>inline checkout for each party. |
| FR-24          | The system SHALL only change problem status to "In<br>Progress / Deposits Confirmed" once both payments are<br>successfully received via Paystack webhook. |
| FR-25          | The system SHALL generate a downloadable PDF Project<br>Agreement (using WeasyPrint) outlining total cost,<br>timeline, deliverables, and forfeiture terms. Both parties<br>MUST digitally agree (checkbox) before payment |
| FR-26          | If the developer quits or abandons: the developer's 20%<br>SHALL be transferred to the poster (admin initiates<br>Paystack Transfer). |
| FR-27          | If the poster quits or cancels: the poster's 20% SHALL be<br>transferred to the developer. |
| FR-28          | The platform MAY deduct a 2-5% escrow management<br>fee from each down payment before holding or releasing<br>funds. |

### 3.5 Progress Tracking (0% – 100%)
| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-29          | The assigned developer/team SHALL update progress<br>using a selector: 0% (Accepted), 30% (Initial Dev), 50%<br>(Mid-point), 80% (Near completion), 100% (Delivered). |
| FR-30          | Each progress update SHALL require a short note and<br>may include an optional file upload. |
| FR-31          | The poster SHALL receive an in-app and email<br>notification on every milestone update. |
| FR-32          | At 100%, the poster SHALL confirm delivery/sign-off. |
| FR-33          | Upon sign-off, the system SHALL notify admin to release<br>escrowed funds back to both parties (or apply to final<br>settlement). |

### 3.6 Per-Problem Real-Time Chat System
| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-34          | Each assigned problem SHALL have a dedicated chat<br>room accessible only to poster, assigned developer(s),<br>and admin(s). |
| FR-35          | Chat SHALL support real-time messaging using Django<br>Channels + WebSockets. |
| FR-36          | Chat SHALL support file attachments (images, code<br>snippets, documents). |
| FR-37          | The system SHALL store full chat history in the database<br>for dispute resolution. |
| FR-38          | Admins SHALL be able to view and communicate in any chat room at any time. |

### 3.7 Notification System
| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-39          | The system SHALL send in-app notifications (bell icon)<br>for: Ghana Card verification, problem assignment,<br>payment confirmations, progress updates, new chat messages. |
| FR-40          | The system SHALL send email notifications for all the<br>above (using Django email backend). |

### 3.8 Admin Dashboard & Escrow Management
| ID             | Requirement                      |
|----------------|----------------------------------|
| FR-41          | Admin dashboard SHALL display queues for: Ghana Card<br>verification, problem approvals, developer applications. |
| FR-42          | Admin SHALL have an "Escrow Management" section<br>showing all active deposits, down payment amounts, and status. |
| FR-43          | Admin SHALL be able to manually trigger Paystack<br>Transfer API to release forfeited funds to the remaining party. |
| FR-44          | Admin SHALL be able to view any problem's chat logs<br>and progress history. |
| FR-45          | Admin SHALL have access to analytics: problems by<br>region, completion rate, active developers, total escrow volume. |

## 4. External Interface Requirements
### 4.1 User Interfaces
* <br>Responsive Web:</br> Bootstrap 5, CSS, Javascript, Django templates.
* <br>Public Board:</br> Card-based layout with filter sidebar.
* <br>Dashboard (Poster/Developer):</br> List of assigned problems, progress bars, chat shortcut.
* <br>Admin Interface:</br> Django admin customized plus custom views for escrow.

### 4.2 Payment Interface (Paystack)
* Inline Checkout: Pop-up modal for card/mobile money.
* Webhooks: charge.success to confirm down payments.
* Transfer API: For forfeiture payouts from platform account to user.
* All amounts in GHS.

### 4.3 File Storage Interface
* Local filesystem for development.
* Cloudinary for production (Ghana Card images, problem attachments, chat files).

## 5. Non-Functional Requirements
### 5.1 Performance
| ID             | Requirement                      |
|----------------|----------------------------------|
| NFR-01          | Page load time SHALL be < 5 seconds on 3G connections. |
| NFR-02          |	Chat messages SHALL be delivered in < 1 second via WebSockets. |
| NFR-03          | The system SHALL support 100 concurrent users at start. |

### 5.2 Security & Data Privacy (Ghana Card)
| ID             | Requirement                      |
|----------------|----------------------------------|
| NFR-04          | Ghana Card numbers and images SHALL be encrypted. |
| NFR-05          |	Access to unencrypted Ghana Card data SHALL be<br>logged and restricted to superadmins only. |
| NFR-06          | All Paystack webhooks SHALL verify signature headers. |
| NFR-07          | The system SHALL enforce HTTPS everywhere. |
| NFR-08          | User passwords SHALL be hashed using Django's PBKDF2. |

### 5.3 Reliability & Availability
| ID             | Requirement                      |
|----------------|----------------------------------|
| NFR-09          | 99% uptime during business hours (8 AM – 9 PM GMT). |
| NFR-10          |	Daily database backups (PostgreSQL) stored off-site. |
| NFR-11          | Paystack webhooks SHALL be idempotent (no duplicate payment processing). |

### 5.4 Usability & Accessibility
| ID             | Requirement                      |
|----------------|----------------------------------|
| NFR-12          | Mobile-first responsive design. |
| NFR-13          |	All actions (pay, apply, update) give clear success/error feedback. |

### 5.5 Legal & Compliance (Ghana)
| ID             | Requirement                      |
|----------------|----------------------------------|
| NFR-14          | Terms of Service and Escrow Policy SHALL be prominently<br>displayed before down payment. |

## 6. Other Requirements
### 6.1 Training Requirements 
* Admin training manual (escrow management, dispute resolution).
* Video tutorials for posters/developers (Ghana Card upload, down payment flow).

### 6.2 Future API (Out of Scope for MVP)
* Public REST API for external problem sources (e.g., NGOs submitting problems).

## Glossary
| Term            | Definition                     |
|----------------|----------------------------------|
| Ghana Card         | National ID card of Ghana, used for KYC. |
