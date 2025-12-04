# Agent Categories Guide

This document explains the different agent categories and when to use each one.

## Overview

Agents are organized into six main categories:

1. [Frontend](#frontend)
2. [Backend](#backend)
3. [DevOps](#devops)
4. [Documentation](#documentation)
5. [Business](#business)
6. [Fullstack](#fullstack)

## Frontend

### Description
Agents specialized in frontend development, UI/UX generation, and client-side technologies.

### Typical Responsibilities
- UI component generation
- Frontend code analysis
- Design system implementation
- Client-side optimization
- Accessibility auditing
- State management

### Technologies
- HTML, CSS, JavaScript/TypeScript
- React, Vue, Angular, Svelte
- CSS frameworks (Tailwind, Bootstrap)
- JSP, Thymeleaf
- UI libraries (shadcn/ui, Material-UI)

### Example Agents

#### jsp-generator-from-image
**Purpose:** Analyzes UI screenshots to generate complete JSP, CSS, and JavaScript files

**Use Cases:**
- Converting design mockups to JSP code
- Korean government/enterprise web applications
- Pixel-perfect UI implementation
- DataTables integration

**Tools:** All tools

**Example Invocation:**
```
Analyze this screenshot and generate JSP code following Korean government standards.
Include DataTables integration for the list view.
```

#### html-generator-from-image
**Purpose:** Generates HTML (Thymeleaf), CSS, and JavaScript from UI screenshots

**Use Cases:**
- Spring Boot application UI
- Thymeleaf template generation
- Responsive web design
- Korean enterprise applications

**Tools:** All tools

**Example Invocation:**
```
Generate Thymeleaf templates from this design mockup.
Use Spring Boot security context for user display.
```

#### figma-prompt-generator
**Purpose:** Generates comprehensive Figma Make prompt documents

**Use Cases:**
- Converting PRD to Figma prompts
- Design system documentation
- Sequential phase-by-phase design guidance
- shadcn/ui integration

**Tools:** All tools

**Example Invocation:**
```
Generate Figma Make prompts from this PRD.
Follow the Design Guide for color schemes and typography.
Create sequential prompts for 3 phases.
```

### When to Use Frontend Category

Choose frontend category when the agent:
- ✅ Works primarily with UI/UX code
- ✅ Generates or analyzes client-side code
- ✅ Deals with visual design or styling
- ✅ Focuses on browser-based technologies
- ❌ Requires server-side logic (use Backend or Fullstack)
- ❌ Handles infrastructure (use DevOps)

## Backend

### Description
Agents focused on server-side development, API design, and backend architecture.

### Typical Responsibilities
- API generation and analysis
- Database schema design
- Server-side logic implementation
- Authentication/authorization
- Backend optimization
- Microservices architecture

### Technologies
- Java, Spring Boot
- Node.js, Express, NestJS
- Python, Django, Flask
- Go, Rust
- SQL, NoSQL databases
- GraphQL, REST APIs

### Example Use Cases
- Generate REST API endpoints from OpenAPI spec
- Design database schema from requirements
- Implement authentication middleware
- Create GraphQL resolvers
- Optimize database queries
- Generate API documentation

### When to Use Backend Category

Choose backend category when the agent:
- ✅ Works with server-side code
- ✅ Generates or analyzes APIs
- ✅ Deals with databases
- ✅ Implements business logic
- ❌ Only handles UI (use Frontend)
- ❌ Manages infrastructure (use DevOps)

## DevOps

### Description
Agents for infrastructure automation, CI/CD, deployment, and operations.

### Typical Responsibilities
- CI/CD pipeline generation
- Infrastructure as Code (IaC)
- Deployment automation
- Monitoring and logging setup
- Container orchestration
- Cloud resource management

### Technologies
- Docker, Kubernetes
- Jenkins, GitHub Actions, GitLab CI
- Terraform, Ansible
- AWS, Azure, GCP
- Prometheus, Grafana
- Shell scripting, Python

### Example Use Cases
- Generate Dockerfile from application
- Create Kubernetes manifests
- Design CI/CD pipeline
- Generate Terraform modules
- Setup monitoring dashboards
- Implement deployment strategies

### When to Use DevOps Category

Choose DevOps category when the agent:
- ✅ Handles infrastructure
- ✅ Manages deployment processes
- ✅ Configures CI/CD pipelines
- ✅ Sets up monitoring/logging
- ❌ Writes application code (use Frontend/Backend)
- ❌ Creates documentation (use Documentation)

## Documentation

### Description
Agents specialized in generating and analyzing technical documentation.

### Typical Responsibilities
- Technical document generation
- Requirements analysis
- Documentation extraction
- API documentation
- User guides
- Architecture diagrams

### Technologies
- Markdown, AsciiDoc
- Mermaid diagrams
- OpenAPI/Swagger
- Korean document formats
- Government standards
- PDF generation

### Example Agents

#### rfp-analyzer
**Purpose:** Analyzes Korean government RFP documents

**Use Cases:**
- Extract requirements from RFP
- Identify evaluation criteria
- Parse project scope
- Understand constraints
- E-Government framework analysis

**Tools:** Read, Glob, Grep

**Example Invocation:**
```
Analyze this RFP document for a government procurement project.
Extract all functional requirements and evaluation criteria.
```

#### rfp-respondent
**Purpose:** Generates responses to RFP requirements

**Use Cases:**
- Create requirement-response pairs
- Follow government standards
- Technical proposal generation
- Compliance documentation

**Tools:** Read, Write, Grep

**Example Invocation:**
```
Generate responses for the requirements extracted from the RFP.
Follow Korean government technical proposal format.
```

#### trd-generator
**Purpose:** Generates Technical Requirements Documents

**Use Cases:**
- Create TRD from technology stack
- Recommend complementary tools
- Document architecture decisions
- Framework integration

**Tools:** Read, Write

**Example Invocation:**
```
Generate TRD for Next.js, React, Tailwind stack.
Recommend state management and testing tools.
```

### When to Use Documentation Category

Choose documentation category when the agent:
- ✅ Generates or analyzes documents
- ✅ Extracts information from specs
- ✅ Creates technical documentation
- ✅ Produces diagrams or schemas
- ❌ Writes application code (use Frontend/Backend)
- ❌ Handles infrastructure (use DevOps)

## Business

### Description
Agents for business analysis, project planning, and strategic documentation.

### Typical Responsibilities
- Business requirements analysis
- Project planning
- Strategic framework generation
- Process documentation
- Stakeholder analysis
- ROI calculation

### Technologies
- Business process modeling
- Project management frameworks
- Strategic planning tools
- Korean government SI standards
- Mermaid process diagrams

### Example Agents

#### promotion-strategy
**Purpose:** Generates strategic frameworks from project briefings

**Use Cases:**
- Extract strategic objectives
- Create tactical execution plans
- Generate implementation roadmaps
- Korean government SI projects

**Tools:** Read, Write, Grep

**Example Invocation:**
```
Analyze this project briefing and generate a strategic framework.
Include objectives, tactics, and implementation timeline.
```

#### project-analyzer
**Purpose:** Extracts key project information from briefings

**Use Cases:**
- Extract project name, agency, timeline
- Identify background and objectives
- Parse project scope
- Government procurement analysis

**Tools:** Read, Grep

**Example Invocation:**
```
Extract all key information from this project briefing document.
Organize by project metadata, background, objectives, and scope.
```

#### process-image-promptor
**Purpose:** Converts business processes to AI image prompts

**Use Cases:**
- Generate diagram prompts under 300 chars
- Business process visualization
- Flowchart generation
- Process documentation

**Tools:** Read, Write

**Example Invocation:**
```
Convert this complex business process into a concise prompt for text-to-image AI.
Focus on main flow and decision points.
```

### When to Use Business Category

Choose business category when the agent:
- ✅ Analyzes business requirements
- ✅ Creates strategic documents
- ✅ Generates project plans
- ✅ Handles business processes
- ❌ Writes code (use Frontend/Backend/Fullstack)
- ❌ Handles infrastructure (use DevOps)

## Fullstack

### Description
Agents that span both frontend and backend development.

### Typical Responsibilities
- Complete application generation
- Full-stack architecture design
- End-to-end feature implementation
- API and UI integration
- Authentication flows
- Database and frontend coordination

### Technologies
- Any combination of frontend and backend technologies
- ORMs and state management
- API integration
- Authentication systems
- Full application stacks (MEAN, MERN, etc.)

### Example Use Cases
- Generate complete CRUD application
- Implement authentication flow (frontend + backend)
- Create admin dashboard with API
- Build real-time chat application
- Design and implement microservice
- Generate full e-commerce feature

### When to Use Fullstack Category

Choose fullstack category when the agent:
- ✅ Works with both frontend and backend
- ✅ Implements end-to-end features
- ✅ Requires full-stack knowledge
- ✅ Integrates UI and API
- ❌ Only handles one side (use Frontend or Backend)
- ❌ Focuses on infrastructure (use DevOps)

## Category Selection Guide

### Decision Tree

```
Does it work with code?
├─ Yes → Continue
│   ├─ Frontend only?
│   │   └─ Yes → FRONTEND
│   ├─ Backend only?
│   │   └─ Yes → BACKEND
│   ├─ Both frontend and backend?
│   │   └─ Yes → FULLSTACK
│   └─ Infrastructure/deployment?
│       └─ Yes → DEVOPS
└─ No → Continue
    ├─ Analyzes/generates documents?
    │   └─ Yes → DOCUMENTATION
    └─ Business/strategy focus?
        └─ Yes → BUSINESS
```

### Quick Reference Table

| If the agent... | Category |
|----------------|----------|
| Generates UI components | Frontend |
| Analyzes React code | Frontend |
| Creates API endpoints | Backend |
| Designs database schema | Backend |
| Implements auth flow (UI + API) | Fullstack |
| Builds complete CRUD app | Fullstack |
| Creates Dockerfiles | DevOps |
| Sets up CI/CD pipeline | DevOps |
| Generates TRD | Documentation |
| Analyzes RFP | Documentation |
| Creates strategic plan | Business |
| Extracts project info | Business |

## Cross-Category Agents

### When Agents Fit Multiple Categories

Some agents might seem to fit multiple categories. Guidelines:

**Example: API Documentation Generator**
- Could be Backend (API-focused)
- Could be Documentation (generates docs)
- **Decision:** Choose Documentation (primary output is documentation)

**Example: Frontend Code Analyzer**
- Could be Frontend (analyzes frontend code)
- Could be Documentation (generates reports)
- **Decision:** Choose Frontend (primary domain is frontend)

**Example: Deployment Script Generator**
- Could be Backend (deploys backend apps)
- Could be DevOps (infrastructure-focused)
- **Decision:** Choose DevOps (primary domain is deployment)

### Rule of Thumb

Choose the category based on:
1. **Primary output:** What is the main artifact produced?
2. **Primary domain:** What expertise is most important?
3. **User perspective:** Where would users look for this?

## Category Conventions

### Naming Patterns

Each category has typical naming patterns:

**Frontend:**
- `*-generator-from-image`
- `*-component-analyzer`
- `*-ui-optimizer`

**Backend:**
- `*-api-generator`
- `*-schema-designer`
- `*-auth-implementer`

**DevOps:**
- `*-pipeline-creator`
- `*-deployment-automator`
- `*-infrastructure-manager`

**Documentation:**
- `*-analyzer`
- `*-generator` (for docs)
- `*-extractor`

**Business:**
- `*-strategy`
- `*-analyzer` (for business docs)
- `*-planner`

**Fullstack:**
- `*-app-generator`
- `*-feature-implementer`
- `*-stack-builder`

## Summary

### Key Points

1. **Frontend:** UI/UX, client-side, visual design
2. **Backend:** Server-side, APIs, databases, business logic
3. **DevOps:** Infrastructure, deployment, CI/CD, operations
4. **Documentation:** Technical docs, analysis, extraction
5. **Business:** Strategy, planning, business analysis
6. **Fullstack:** End-to-end, both frontend and backend

### Choosing the Right Category

Ask yourself:
- What is the primary output?
- What domain expertise is required?
- Where would users expect to find this?
- What is the main technology focus?

When in doubt, consider:
- Start with the most specific category
- Consider the primary user need
- Think about the main artifact produced
- Review similar existing agents

For more information:
- [Getting Started](getting-started.md)
- [Agent Development](agent-development.md)
- [Best Practices](best-practices.md)
