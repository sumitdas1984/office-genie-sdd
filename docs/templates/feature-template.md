# Feature Issue Skeleton Template

## Title 
*{{FEATURE_NAME}}*

> Feature name should be relevant and clear in verb-noun format (e.g., "Integrate Authentication Service", "Federated Context Catalogue: Assessment and Scope")

---

## Issue Body Template

### Description
This feature enables the MiDAS platform to *{{primary capability/integration/functionality}}*. *{{Explain the specific problem being solved and the value proposition}}*. The goal is to *{{desired outcome and benefit to the platform/users}}*.

> Clearly describe the purpose and value of the feature to be created. What is it meant to accomplish? What problem does it solve? Why is it important?

---

### Scope
- **Core Implementation**: [Define the main functionality, workflows, or system components to be implemented]
- **Integration Points**: [Specify how this feature integrates with existing MiDAS subsystems (orchestration, agent, LLM layer, etc.)]
- **Configuration & Management**: [Define administrative tools, settings, and management interfaces required]
- **Security & Governance**: [Outline security measures, authentication, authorization, and compliance requirements]
- **Performance & Monitoring**: [Specify performance requirements, monitoring, and observability features]
- **Developer Experience**: [Define tools, APIs, and interfaces for developers to use this feature]
- **Data Handling**: [Describe data models, storage, retrieval, and processing requirements]
- **Error Handling & Resilience**: [Define failure modes, recovery mechanisms, and graceful degradation]

> Define the boundaries and major components of the feature to be created.
**Note**: The scope section should be concise yet comprehensive, presented as clear bullet points without subheadings. Aim for 4 to 10 key points that cover all relevant aspects of the feature.

---

### Acceptance Criteria

- [ ] **Connectivity**: [System connects to external services/components]
- [ ] **Authentication**: [Proper authentication mechanisms are enforced]
- [ ] **Functionality**: [Main feature works as specified]
- [ ] **Performance**: [Latency and throughput requirements are met]
- [ ] **Admin Interface**: [Feature is configurable and manageable by admins]
- [ ] **Monitoring**: [System health and status monitoring is available]
- [ ] **Security**: [Security requirements are implemented (TLS, data protection, etc.)]
- [ ] **Access Control**: [Proper permissions and access controls are enforced]
- [ ] **Audit & Logging**: [Usage logs and audit trails are captured]
- [ ] **Reporting**: [Usage statistics and metrics are available]
- [ ] **Developer Tools**: [Developer-facing tools and documentation are provided]
- [ ] **Error Handling**: [Graceful failure handling and fallback mechanisms work]
- [ ] **Code Coverage**: [Test cases achieve required code coverage threshold of more than 95%]
- [ ] **Block and Flow Diagrams**: [Architecture, block, and flow diagrams are updated and documented if required]

> List relevant specific, testable, measurable outcomes for the feature to be created.

---

## Usage Instructions

### For Feature Creation Agent:
1. Replace all `{{ }}` placeholders with specific content
2. Ensure each acceptance criterion is measurable and testable
3. Cross-reference with existing features for consistency
4. Apply appropriate labels and assignees

### Section Guidelines:

**Description**: 
- Start with "This feature enables the MiDAS platform to..."
- Clearly state the problem being solved
- Explain the value proposition
- Define the desired outcome

**Scope**: 
- Be comprehensive, realistic and less verbose
- Clearly list all aspects in bullet points. No subsections 
- Reference existing system components
- Consider all architectural layers

**Acceptance Criteria**: 
- Use checkboxes for trackability
- Make each criterion specific and measurable
- Include both functional and non-functional requirements
- Consider security, performance, and usability aspects

---

> **Note:** The `{{specific_relevant_content}}` syntax indicates placeholders that should be replaced with specific, contextual content when creating feature issues. Each placeholder represents a required field that must be customized for the particular feature being implemented. No other section should be there other than Description, Scope and Acceptance criteria. No subsections in any of the mentioned sections, just bullet points in scope and checkboxes in acceptance criteria.