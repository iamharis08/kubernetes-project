# 🛡️ Secure PHI Platform on GKE Autopilot (Zero-Trust Demo)
# Project still in progress

## Project Overview

This project demonstrates a  secure, and highly observable microservices architecture built on **Google Kubernetes Engine (GKE) Autopilot**. The primary objective is to enforce **Zero-Trust networking** and **mTLS encryption** to meet stringent regulatory requirements like **HIPAA** (Health Insurance Portability and Accountability Act).

This application simulates a basic Personal Health Information (PHI) workflow, showing that data access is strictly limited to an authorized, encrypted path.

---

## 🚀 Implemented Architecture & Technologies

This application is built as a microservices chain, secured by a service mesh.

### Microservices Flow

The architecture strictly enforces a rigid, directional trust model:

$$\text{User} \xrightarrow[\text{HTTPS}]{\text{GKE Ingress}} \text{Frontend} \rightarrow \text{API Gateway} \xrightarrow[\text{mTLS, Egress Policy}]{\text{Layer 7}} \text{PHI Service} \xrightarrow[\text{mTLS, Egress Policy}]{\text{Layer 7}} \text{Audit Service}$$

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Compute** | GKE Autopilot | Managed Kubernetes with consumption-based billing; ensures high availability. |
| **Networking** | Kubernetes NetworkPolicy | **Layer 3/4 firewall enforcement** (Egress policies block public internet access). |
| **Security/mTLS** | Anthos Service Mesh (Istio) | **Automates mTLS encryption** for all internal service traffic, enforcing encryption in transit. |
| **Identity** | Workload Identity | Secure, granular access for pods to Google Cloud resources (Artifact Registry, etc.) via IAM. |
| **Runtime** | Python (FastAPI) | Lightweight, asynchronous backend services. |

---

## 🔒 Security & HIPAA Compliance Highlights

This architecture provides defense-in-depth, demonstrating crucial technical safeguards required for handling PHI.

| Compliance Layer | Feature Implemented | Security Proof Point |
| :--- | :--- | :--- |
| **Encryption in Transit (Internal)** | **Anthos Service Mesh (mTLS)** | All pod-to-pod communication is automatically encrypted via **Strict mTLS** (verified by sidecar readiness). |
| **Network Egress Control** | **Kubernetes NetworkPolicy** | **Strict Egress Firewall:** Pods are prevented from connecting to the public internet (HTTP/S/TCP), while only allowing specific internal service communication and necessary DNS/Control Plane traffic. |
| **Isolation** | **Private GKE Cluster** | All worker nodes and the Control Plane IP are internal, providing foundational isolation. |
| **Identity Management** | **Workload Identity** | Each service runs with its own, unique, auditable Google Identity (GSA). |
| **Audit Trail** | **Dedicated Audit Service** | A dedicated service logs all PHI access attempts, satisfying a core compliance requirement. |

---

## ⚙️ Setup and Deployment

### Prerequisites

1.  Google Cloud Project with Billing Enabled.
2.  Google Cloud CLI (`gcloud`), `kubectl`, and `docker` installed.
3.  Necessary APIs enabled (GKE, Artifact Registry, Anthos Service Mesh).

### 1. Deployment Commands

These commands assume your cluster is already created and configured with managed Anthos Service Mesh.

```bash
# 1. Label Namespace for Istio Sidecar Injection
kubectl label namespace default istio-injection=enabled --overwrite

# 2. Configure STRICT mTLS (Highest Security)
# NOTE: This should use v1beta1 API version in peer-authentication.yaml
kubectl apply -f peer-authentication.yaml

# 3. Deploy Kubernetes Service Accounts (Links to IAM)
kubectl apply -f service-accounts.yaml

# 4. Deploy Application Components (Pods must restart to get sidecar)
kubectl apply -f kubernetes-manifest.yaml

# 5. Apply the HIPAA-Compliant Network Policies
kubectl apply -f network-policy.yaml
