%% K8s deployment flow for `connectors/concourse`
flowchart LR
  subgraph ConcoursePipeline[connectors/concourse]
    P1[pipeline-develop.yml\n(pipeline triggers)]
    P2[deploy-cks.yml / deploy-cks.sh\n(task -> script)]
  end

  subgraph DeployScript[deploy-cks.sh]
    D1[Configure kubeconfig (KUBECONFIG_CONTENT)]
    D2[Create Secrets (manifests/secret.yaml)]
    D3[Create ConfigMap (connectors-config)]
    D4[Apply deployment/service/gateway (manifests/*.yaml)]
  end

  subgraph Manifests[connectors/concourse/manifests]
    M1[secret.yaml]
    M2[deployment.yaml]
    M3[gateway.yaml]
    M4[registry-secret.yaml]
  end

  subgraph Kubernetes[CKS Cluster / Namespace]
    K1[Namespace (dne-develop/test/stage/prod)]
    K2[Secrets (connectors-secrets)]
    K3[ConfigMap (connectors-config)]
    K4[Deployment / Service / HPA / PDB / HTTPRoute]
  end

  P1 --> P2
  P2 --> D1
  P2 --> D2
  P2 --> D3
  P2 --> D4
  D1 -->|uses| Kube[Kubeconfig targets clusters]
  D2 --> M1
  D3 --> M2
  D4 --> M3
  M1 -->|kubectl apply| K2
  M2 -->|kubectl apply| K4
  M3 -->|kubectl apply| K4
  M4 -->|kubectl apply| K2
  K2 --> K4
  K3 --> K4

  subgraph SecretsSource[Secrets & Vars]
    S1[Concourse vars (develop-secrets)]
    S2[AWS Secrets Manager / Vault]
  end

  S1 --> P1
  S1 --> P2
  S2 --> S1

  classDef box fill:#f8f9fa,stroke:#333,stroke-width:1px;
  class ConcoursePipeline,DeployScript,Manifests,Kubernetes,SecretsSource box;
