# RenewAI — System Architecture (Flowchart Style)

This document visualizes the end-to-end data and logic flow of the RenewAI platform, from the backend data foundation to the final multi-channel customer engagement.

## 📊 System Flowchart

```mermaid
flowchart TD
    %% Styling and Branding
    classDef foundation fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px,color:#333;
    classDef intelligence fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#0d47a1;
    classDef communication fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#f57f17;
    classDef humanLayer fill:#f1f8e9,stroke:#689f38,stroke-width:2px,color:#1b5e20;
    classDef external fill:#fafafa,stroke:#bdbdbd,stroke-dasharray: 5 5;

    %% Data Foundation Pillar
    subgraph DataFoundation ["1. EXTERNAL DATA & STORAGE"]
        DB[("RenewAI Database<br/>(SQLite/WAL)")]:::foundation
        CRM["CRM & Policy Systems"]:::external
    end

    %% Orchestration & Intelligence Pillar
    subgraph IntelligenceHub ["2. THE AI ORCHESTRATION BRAIN"]
        Orch["Renewal Orchestrator<br/>(State Machine)"]:::intelligence
        Gemini{"Gemini 2.5 Flash<br/>(NLU & NLG)"}:::intelligence
        RAG["Objection Library<br/>(ChromaDB RAG)"]:::intelligence
        Audit["Audit Log Tracer<br/>(PII Masking)"]:::foundation
    end

    %% Engagement Pillar
    subgraph MultiChannel ["3. OMNI-CHANNEL ENGAGEMENT"]
        Email["Email Service"]:::communication
        WhatsApp["WhatsApp API"]:::communication
        Voice["Voice AI<br/>(ElevenLabs)"]:::communication
    end

    %% Human Layer Pillar
    subgraph HumanExpertise ["4. HUMAN-IN-THE-LOOP (HIL)"]
        Dashboard["Specialist Workbench"]:::humanLayer
        Briefing["AI Briefing Notes"]:::humanLayer
    end

    %% Relationships and Data Flow
    CRM -- "Policy Data Sync" --> DB
    DB <--> Orch
    Orch <--> Gemini
    Gemini <--> RAG
    
    Orch -- "Auto-Reminder" --> MultiChannel
    MultiChannel -- "Customer Interaction" --> Orch
    
    Orch -- "High-Value/Distress Escalation" --> Briefing
    Briefing --> Dashboard
    
    MultiChannel -.-> Audit
    Orch -.-> Audit
    
    click Dashboard "file:///home/labuser/Renew%20ai%2006/frontend.html" "Open Dashboard"
```

## 📋 Architectural Layers

### 1. External Data & Storage
The foundation of RenewAI. It synchronizes with legacy CRMs to maintain a "Single Source of Truth" for policy dates, premiums, and customer segments in a secure, high-performance SQLite database.

### 2. The AI Orchestration Brain
The core logic engine. It uses a **Deterministic State Machine** to manage the renewal lifecycle and **Gemini 2.5 Flash** for understanding complex customer intents. The **RAG layer** ensures every response is legally compliant and grounded in vetted insurance facts.

### 3. Omni-Channel Engagement
A multi-modal communication layer. Depending on the customer's "Risk Score" and "Response History," the system dynamically switches between Email, WhatsApp, and low-latency AI Voice calls.

### 4. Human-In-The-Loop (HIL)
The synergy between AI and Human Specialists. When the AI detects "Distress" (emotional hardship) or high-complexity cases, it immediately blocks automated outreach and transfers the file to a human relationship manager with a comprehensive **AI Briefing Note**.

---

> [!TIP]
> This flowchart is designed for stakeholders to understand the "Decision Path" of the autonomous agent. For a technical deep-dive, refer to the [Technical Design Spec](file:///home/labuser/Renew%20ai%2006/DESIGN_SPEC.md).
