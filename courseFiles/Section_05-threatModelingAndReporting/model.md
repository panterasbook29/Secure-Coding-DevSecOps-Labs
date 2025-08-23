
### Data Flow Diagram (DFD)

```mermaid
flowchart LR
  %% Trust Boundaries
  classDef boundary stroke-dasharray: 5 5,stroke:#999,stroke-width:2,fill:none;

  subgraph Internet
    U[User Browser]
  end
  class Internet boundary;

  subgraph DMZ[DMZ / Frontend]
    N[Nginx / TLS terminator]
  end
  class DMZ boundary;

  subgraph AppNet[App Network]
    S[Express App / API]
    DB[(Postgres)]
  end
  class AppNet boundary;

  subgraph ThirdParty[3rd Party]
    PAY[Payment Provider]
    MAIL[Email Service]
  end
  class ThirdParty boundary;

  %% Flows
  U -- HTTPS: creds/JWT --> N
  N -- internal HTTP --> S
  S -- SQL (credentials, orders) --> DB
  S -- HTTPS: card tokenization --> PAY
  PAY -- HTTPS webhook: payment status --> N
  N -- internal HTTP --> S
  S -- HTTPS: password reset email --> MAIL

  %% Notes
  note right of S:::note
    Issues JWT (HS256)
    Stores users/orders
    Rate limit TBD
  end

  classDef note fill:#f9f9f9,stroke:#bbb,color:#333;
