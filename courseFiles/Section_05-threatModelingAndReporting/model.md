### Minimal DFD – Juice Shop (training version)

```mermaid
flowchart LR
  subgraph User_Browser[User Browser]
    U[Customer]:::actor
    LS[(LocalStorage:<br/>JWT/Cart)]:::store
  end

  subgraph Internet_Boundary[Trust Boundary: Internet]
  end

  subgraph App_Net[App Network]
    API[Juice Shop App (Angular+Node/Express)]:::process
    DB[(SQLite DB)]:::store
    Mail[(Email/SMS provider)]:::ext
  end

  U -- HTTP(S) / REST & SPA --> API
  U <-- HTML/JS/CSS -- API
  API <-- SQL --> DB
  API -- Outbound SMTP/API --> Mail
  U <---> LS

  classDef actor fill:#eef,stroke:#447;
  classDef process fill:#efe,stroke:#474;
  classDef store fill:#ffe,stroke:#774;
  classDef ext fill:#fef,stroke:#744;

```
