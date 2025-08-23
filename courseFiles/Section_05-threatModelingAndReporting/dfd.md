# Minimal DFD – Juice Shop (training)

**Elements**
- External Actor: Customer (browser)
- Process: Juice Shop (Angular SPA + Node/Express)
- Data Stores: SQLite (server), LocalStorage (browser)
- Trust Boundary: Browser ↔ Server (Internet)

**Flows**
1. Browser → Server: HTTP(S) requests (login, search, reviews)
2. Server ↔ DB: SQL queries
3. Browser ↔ LocalStorage: JWT/cart cached in browser

> Optional diagram (Mermaid). GitHub/VS Code will render this:

```mermaid
flowchart LR
  U[Customer (Browser)]:::actor -->|HTTP(S)| App[Juice Shop (Node/Angular)]:::proc
  App <-->|SQL| DB[(SQLite)]:::store
  U <--> LS[(LocalStorage / JWT)]:::store

  classDef actor fill:#eef,stroke:#447;
  classDef proc  fill:#efe,stroke:#474;
  classDef store fill:#ffe,stroke:#774;
