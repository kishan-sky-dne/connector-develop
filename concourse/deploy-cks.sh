#!/bin/bash
# Common CKS deployment script for all environments
# Called by Concourse tasks with environment-specific parameters
#
# Required environment variables:
# - ENVIRONMENT (develop/test/stage/production)
# - NAMESPACE (k8s namespace)
# - KUBECONFIG_CONTENT (kubeconfig as string)
# - All secret/config parameters (83+ variables)

set -euo pipefail

echo "=========================================="
echo "Deploying Connectors to CKS (${ENVIRONMENT})"
echo "Namespace: ${NAMESPACE}"
echo "=========================================="

###########################################
# Install Tools
###########################################

yum install -y tar gzip git wget jq unzip gettext

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && mv kubectl /usr/local/bin/

# Install kubelogin for OIDC
curl -L https://github.com/Azure/kubelogin/releases/latest/download/kubelogin-linux-amd64.zip -o kubelogin.zip
unzip kubelogin.zip
mv bin/linux_amd64/kubelogin /usr/local/bin/
chmod +x /usr/local/bin/kubelogin

###########################################
# Configure Kubeconfig
###########################################

echo "Configuring kubeconfig..."
echo "$KUBECONFIG_CONTENT" > /tmp/kubeconfig
echo "--- /tmp/kubeconfig ---"
cat /tmp/kubeconfig
export KUBECONFIG=/tmp/kubeconfig
chmod 600 /tmp/kubeconfig

###########################################
# Test Kubernetes Access
###########################################

echo "Testing kubectl access..."
cat /tmp/kubeconfig
kubectl config get-contexts > /tmp/get-contect
cat /tmp/get-contect
if ! kubectl get pods -n ${NAMESPACE} 2>&1; then
  echo "ERROR: Cannot access namespace ${NAMESPACE}"
  kubectl version --client
  exit 1
fi
echo "✓ Connected to CKS cluster"

###########################################
# Load Environment Variables
###########################################

echo "Loading environment-specific variables..."

ENV_FILE="dev"
case "${ENVIRONMENT}" in
  develop) ENV_FILE="dev" ;;
  test) ENV_FILE="test" ;;
  stage) ENV_FILE="stage" ;;
  production) ENV_FILE="prod" ;;
esac

source environments/${ENV_FILE}.env

# Ensure hostname matches target datacenter for this run.
case "${DATACENTER}" in
  onx)
    HOSTNAME="${HOSTNAME/.shared.sce./.shared.onx.}"
    ;;
  sce)
    HOSTNAME="${HOSTNAME/.shared.onx./.shared.sce.}"
    ;;
  *)
    echo "ERROR: Unsupported DATACENTER '${DATACENTER}' (expected onx or sce)"
    exit 1
    ;;
esac

export NAMESPACE ENVIRONMENT IMAGE_REGISTRY IMAGE_NAME IMAGE_TAG
export REPLICAS HPA_MIN_REPLICAS HPA_MAX_REPLICAS
export CPU_REQUEST CPU_LIMIT MEMORY_REQUEST MEMORY_LIMIT HOSTNAME

echo "✓ Environment variables loaded"

###########################################
# Create Secrets and ConfigMap
###########################################

echo "Creating Kubernetes Secrets and ConfigMap..."

# Create temp files for RSA keys
echo "$CONNECTORS_RSA_PRIVATE_KEY" > /tmp/rsa_private.key
echo "$CONNECTORS_RSA_PUBLIC_KEY" > /tmp/rsa_public.key

# Apply secret manifest
echo "  → Creating application secrets..."
envsubst < manifests/secret.yaml | kubectl apply -f -

# Add RSA keys to the secret
echo "  → Adding RSA keys..."
kubectl get secret connectors-secrets -n ${NAMESPACE} -o json | \
jq --arg pk "$(cat /tmp/rsa_private.key | base64 | tr -d '\n')" \
   --arg pub "$(cat /tmp/rsa_public.key | base64 | tr -d '\n')" \
   '.data.rsa_private_key = $pk | .data.rsa_public_key = $pub' | \
kubectl apply -f -

rm -f /tmp/rsa_*.key

# Apply configmap using kubectl to avoid YAML escaping issues
echo "  → Creating configmap..."
kubectl create configmap connectors-config -n ${NAMESPACE} \
  --from-literal=CONNECTORS_API_GW_URL="$CONNECTORS_API_GW_URL" \
  --from-literal=CONNECTORS_AUDITNOW_TOPIC="$CONNECTORS_AUDITNOW_TOPIC" \
  --from-literal=CONNECTORS_AZURE_AD_AUTH_AUTHORITY="$CONNECTORS_AZURE_AD_AUTH_AUTHORITY" \
  --from-literal=CONNECTORS_AZURE_AD_AUTH_CLIENT_CREDENTIAL="$CONNECTORS_AZURE_AD_AUTH_CLIENT_CREDENTIAL" \
  --from-literal=CONNECTORS_AZURE_AD_AUTH_CLIENT_ID="$CONNECTORS_AZURE_AD_AUTH_CLIENT_ID" \
  --from-literal=CONNECTORS_AZURE_AD_AUTH_SCOPES="$CONNECTORS_AZURE_AD_AUTH_SCOPES" \
  --from-literal=CONNECTORS_CISCO_SMART_ACCOUNT_CLIENT_ID="$CONNECTORS_CISCO_SMART_ACCOUNT_CLIENT_ID" \
  --from-literal=CONNECTORS_CISCO_SMART_ACCOUNT_CLIENT_SECRET="$CONNECTORS_CISCO_SMART_ACCOUNT_CLIENT_SECRET" \
  --from-literal=CONNECTORS_CISCO_SMART_ACCOUNT_PASSWORD="$CONNECTORS_CISCO_SMART_ACCOUNT_PASSWORD" \
  --from-literal=CONNECTORS_CISCO_SMART_ACCOUNT_USERNAME="$CONNECTORS_CISCO_SMART_ACCOUNT_USERNAME" \
  --from-literal=CONNECTORS_ELASTICSEARCH_NODES="$CONNECTORS_ELASTICSEARCH_NODES" \
  --from-literal=CONNECTORS_ELASTICSEARCH_PASSWORD="$CONNECTORS_ELASTICSEARCH_PASSWORD" \
  --from-literal=CONNECTORS_ELASTICSEARCH_USERNAME="$CONNECTORS_ELASTICSEARCH_USERNAME" \
  --from-literal=CONNECTORS_GIT_TOKEN="$CONNECTORS_GIT_TOKEN" \
  --from-literal=CONNECTORS_HORIZON_ENDPOINT="$CONNECTORS_HORIZON_ENDPOINT" \
  --from-literal=CONNECTORS_INCA_BASE_URL="$CONNECTORS_INCA_BASE_URL" \
  --from-literal=CONNECTORS_INCA_GEA_URL="$CONNECTORS_INCA_GEA_URL" \
  --from-literal=CONNECTORS_INCA_NEXA_PASSWORD="$CONNECTORS_INCA_NEXA_PASSWORD" \
  --from-literal=CONNECTORS_INCA_NEXA_USERNAME="$CONNECTORS_INCA_NEXA_USERNAME" \
  --from-literal=CONNECTORS_INCA_PASSWORD="$CONNECTORS_INCA_PASSWORD" \
  --from-literal=CONNECTORS_INCA_USERNAME="$CONNECTORS_INCA_USERNAME" \
  --from-literal=CONNECTORS_ITSM_ASSIGNED_TO="$CONNECTORS_ITSM_ASSIGNED_TO" \
  --from-literal=CONNECTORS_ITSM_CHECK_DURATION="$CONNECTORS_ITSM_CHECK_DURATION" \
  --from-literal=CONNECTORS_ITSM_ETHERNETSEGMENT_CONFIG_GROUP="$CONNECTORS_ITSM_ETHERNETSEGMENT_CONFIG_GROUP" \
  --from-literal=CONNECTORS_ITSM_ETHERNETSEGMENT_PARENT_TICKET="$CONNECTORS_ITSM_ETHERNETSEGMENT_PARENT_TICKET" \
  --from-literal=CONNECTORS_ITSM_EVPN_CONFIG_GROUP="$CONNECTORS_ITSM_EVPN_CONFIG_GROUP" \
  --from-literal=CONNECTORS_ITSM_EVPN_PARENT_TICKET="$CONNECTORS_ITSM_EVPN_PARENT_TICKET" \
  --from-literal=CONNECTORS_ITSM_EXTERNAL_CONFIG_GROUP="$CONNECTORS_ITSM_EXTERNAL_CONFIG_GROUP" \
  --from-literal=CONNECTORS_ITSM_MANAGEMENTEVPN_CONFIG_GROUP="$CONNECTORS_ITSM_MANAGEMENTEVPN_CONFIG_GROUP" \
  --from-literal=CONNECTORS_ITSM_MANAGEMENTEVPN_PARENT_TICKET="$CONNECTORS_ITSM_MANAGEMENTEVPN_PARENT_TICKET" \
  --from-literal=CONNECTORS_ITSM_SUBSCRIBEREVPN_CONFIG_GROUP="$CONNECTORS_ITSM_SUBSCRIBEREVPN_CONFIG_GROUP" \
  --from-literal=CONNECTORS_ITSM_SUBSCRIBEREVPN_PARENT_TICKET="$CONNECTORS_ITSM_SUBSCRIBEREVPN_PARENT_TICKET" \
  --from-literal=CONNECTORS_ITSM_URL="$CONNECTORS_ITSM_URL" \
  --from-literal=CONNECTORS_KAFKA_BOOTSTRAP_SERVERS="$CONNECTORS_KAFKA_BOOTSTRAP_SERVERS" \
  --from-literal=CONNECTORS_KAFKA_SASL_PASSWORD="$CONNECTORS_KAFKA_SASL_PASSWORD" \
  --from-literal=CONNECTORS_KAFKA_SASL_PASSWORD_WRITE="$CONNECTORS_KAFKA_SASL_PASSWORD_WRITE" \
  --from-literal=CONNECTORS_KAFKA_SASL_USERNAME="$CONNECTORS_KAFKA_SASL_USERNAME" \
  --from-literal=CONNECTORS_KAFKA_SASL_USERNAME_WRITE="$CONNECTORS_KAFKA_SASL_USERNAME_WRITE" \
  --from-literal=CONNECTORS_MAILER_ALLOWED_DOMAINS="$CONNECTORS_MAILER_ALLOWED_DOMAINS" \
  --from-literal=CONNECTORS_MAILER_FEATURE_FLAG="$CONNECTORS_MAILER_FEATURE_FLAG" \
  --from-literal=CONNECTORS_MAILER_FROM_ADDRESS="$CONNECTORS_MAILER_FROM_ADDRESS" \
  --from-literal=CONNECTORS_MINIO_ACCESS_KEY="$CONNECTORS_MINIO_ACCESS_KEY" \
  --from-literal=CONNECTORS_MINIO_ENDPOINT="$CONNECTORS_MINIO_ENDPOINT" \
  --from-literal=CONNECTORS_MINIO_SECRET_KEY="$CONNECTORS_MINIO_SECRET_KEY" \
  --from-literal=CONNECTORS_MYSQLDB_DATABASE_NAME="$CONNECTORS_MYSQLDB_DATABASE_NAME" \
  --from-literal=CONNECTORS_MYSQLDB_HOST="$CONNECTORS_MYSQLDB_HOST" \
  --from-literal=CONNECTORS_MYSQLDB_PASSWORD="$CONNECTORS_MYSQLDB_PASSWORD" \
  --from-literal=CONNECTORS_MYSQLDB_PORT="$CONNECTORS_MYSQLDB_PORT" \
  --from-literal=CONNECTORS_MYSQLDB_USERNAME="$CONNECTORS_MYSQLDB_USERNAME" \
  --from-literal=CONNECTORS_OAUTH_URL="$CONNECTORS_OAUTH_URL" \
  --from-literal=CONNECTORS_OPTIONS_LOG_LEVEL="$CONNECTORS_OPTIONS_LOG_LEVEL" \
  --from-literal=CONNECTORS_OPTIONS_SPARK_CHECK_EXCEPTION="$CONNECTORS_OPTIONS_SPARK_CHECK_EXCEPTION" \
  --from-literal=CONNECTORS_ORDER_STATUS_TOPIC_MAPPER="$CONNECTORS_ORDER_STATUS_TOPIC_MAPPER" \
  --from-literal=CONNECTORS_ORDER_STATUS_URL="$CONNECTORS_ORDER_STATUS_URL" \
  --from-literal=CONNECTORS_PLANNET_ACCESS_TOKEN="$CONNECTORS_PLANNET_ACCESS_TOKEN" \
  --from-literal=CONNECTORS_PLANNET_BASE_URL="$CONNECTORS_PLANNET_BASE_URL" \
  --from-literal=CONNECTORS_POSTGRESDB_DATABASE_NAME="$CONNECTORS_POSTGRESDB_DATABASE_NAME" \
  --from-literal=CONNECTORS_POSTGRESDB_HOST="$CONNECTORS_POSTGRESDB_HOST" \
  --from-literal=CONNECTORS_POSTGRESDB_PASSWORD="$CONNECTORS_POSTGRESDB_PASSWORD" \
  --from-literal=CONNECTORS_POSTGRESDB_PORT="$CONNECTORS_POSTGRESDB_PORT" \
  --from-literal=CONNECTORS_POSTGRESDB_USERNAME="$CONNECTORS_POSTGRESDB_USERNAME" \
  --from-literal=CONNECTORS_RADIUS_BASE_URL="$CONNECTORS_RADIUS_BASE_URL" \
  --from-literal=CONNECTORS_RADIUS_PASSWORD="$CONNECTORS_RADIUS_PASSWORD" \
  --from-literal=CONNECTORS_RADIUS_SCOPE="$CONNECTORS_RADIUS_SCOPE" \
  --from-literal=CONNECTORS_RADIUS_USERNAME="$CONNECTORS_RADIUS_USERNAME" \
  --from-literal=CONNECTORS_SERVICEDB_PASSWORD="$CONNECTORS_SERVICEDB_PASSWORD" \
  --from-literal=CONNECTORS_SERVICEDB_USERNAME="$CONNECTORS_SERVICEDB_USERNAME" \
  --from-literal=CONNECTORS_SOFTWARE_LIFECYCLE_MANAGEMENT="$CONNECTORS_SOFTWARE_LIFECYCLE_MANAGEMENT" \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply registry credentials
echo "  → Creating registry credentials..."
envsubst < manifests/registry-secret.yaml | kubectl apply -f -

echo "✓ All secrets and ConfigMap created/updated"

###########################################
# Deploy Application
###########################################

echo "Deploying connectors application..."

echo "  → Applying Deployment, Service, PDB, HPA..."
envsubst < manifests/deployment.yaml | kubectl apply -f -

echo "  → Applying Gateway configuration..."
envsubst < manifests/gateway.yaml | kubectl apply -f -

echo "✓ All manifests applied"

###########################################
# Wait for Deployment
###########################################

echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/connectors --namespace=${NAMESPACE} --timeout=5m
echo "✓ Deployment is ready"

###########################################
# Validation
###########################################

echo "Validating deployment..."
kubectl get pods -n ${NAMESPACE} -l app=connectors -o wide
kubectl get svc -n ${NAMESPACE} connectors
kubectl get httproute -n ${NAMESPACE} connectors-route || echo "HTTPRoute validation skipped"

echo ""
echo "=========================================="
echo "✓ Deployment completed successfully!"
echo "=========================================="
echo "Application URL: https://${HOSTNAME}"
echo "=========================================="
