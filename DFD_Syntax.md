
# Data Flow Diagrams (DFD) - Mermaid.js Syntax

You can copy and paste the code blocks below into the [Mermaid Live Editor](https://mermaid.live/) to view the diagrams.

## DFD Level 0 (Context Diagram)
Overview of the system and external entities.

```mermaid
graph TD
    %% Entities
    Student[Student]
    Admin[Admin]

    %% System
    System((Student Enrollment System))

    %% Data Flows
    Student -- Credentials --> System
    System -- Dashboard/Courses --> Student
    Student -- Search/Filter --> System
    System -- Course Details --> Student
    Student -- Enrollment Request --> System
    System -- Enrollment Status --> Student
    Student -- Payment --> System
    System -- Receipt --> Student

    Admin -- Credentials --> System
    System -- Admin Dashboard --> Admin
    Admin -- Course Data --> System
    System -- Reports --> Admin
    Admin -- Student Data Management --> System
```

## DFD Level 1 (System Overview)
Breakdown of main system processes.

```mermaid
graph TD
    %% Entities
    Student[Student]
    Admin[Admin]

    %% Processes
    P1((1.0 Authentication))
    P2((2.0 Manage Courses))
    P3((3.0 View/Search Courses))
    P4((4.0 Enrollment & Payment))

    %% Data Stores
    D1[(User Database)]
    D2[(Course Database)]
    D3[(Enrollment Database)]

    %% Flows
    Student -->|Login details| P1
    Admin -->|Login details| P1
    P1 -->|Verify credentials| D1
    D1 -->|User Roles| P1
    P1 -->|Token/Session| Student
    P1 -->|Token/Session| Admin

    Admin -->|Add/Edit Course| P2
    P2 -->|Update Course Info| D2
    D2 -->|Course Data| P2

    Student -->|Filter Level/Stream| P3
    D2 -->|Fetch Courses| P3
    P3 -->|List of Courses| Student

    Student -->|Select Course| P4
    P4 -->|Check Availability| D2
    P4 -->|Save Enrollment| D3
    D3 -->|Confirm Status| P4
    P4 -->|Receipt/Confirmation| Student
    
    Admin -->|View Reports| P4
    D3 -->|Enrollment Data| P4
```

## DFD Level 2 (Detailed Enrollment Process)
Detailed flow for the Enrollment process (Process 4.0).

```mermaid
graph TD
    %% Entities
    Student[Student]

    %% Sub-Processes of Enrollment
    P4_1((4.1 Validate Eligibility))
    P4_2((4.2 Check Seat Availability))
    P4_3((4.3 Process Payment))
    P4_4((4.4 Update Records))

    %% Data Stores
    D2[(Course Database)]
    D3[(Enrollment Database)]

    %% Flows from Level 1
    Student -->|Request Enrollment| P4_1
    
    %% Internal Flows
    P4_1 -->|Valid| P4_2
    P4_2 -->|Check Seats| D2
    D2 -->|Seats Available| P4_2
    
    P4_2 -->|Proceed to Pay| P4_3
    
    Student -->|Payment Details| P4_3
    P4_3 -->|Payment Success| P4_4
    
    P4_4 -->|Create Record| D3
    P4_4 -->|Decrease Seat Count| D2
    
    P4_4 -->|Enrollment Success Email| Student
```
