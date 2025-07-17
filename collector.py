from kubernetes import client, config
from datetime import datetime
import csv
import os

# Load OpenShift in-cluster config
config.load_incluster_config()

v1 = client.CoreV1Api()
pods = v1.list_pod_for_all_namespaces(watch=False)

output_path = "/data/app_metrics.csv"
os.makedirs("/data", exist_ok=True)

with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "namespace", "pod", "container", "cpu_request", "cpu_limit",
        "mem_request", "mem_limit", "restarts", "age_days"
    ])

    for pod in pods.items:
        metadata = pod.metadata
        spec = pod.spec
        status = pod.status
        age_days = (datetime.now(metadata.creation_timestamp.tzinfo) - metadata.creation_timestamp).days
        restarts = sum([cs.restart_count for cs in (status.container_statuses or [])])

        for container in spec.containers:
            resources = container.resources
            cpu_req = resources.requests.get('cpu') if resources.requests else "N/A"
            cpu_lim = resources.limits.get('cpu') if resources.limits else "N/A"
            mem_req = resources.requests.get('memory') if resources.requests else "N/A"
            mem_lim = resources.limits.get('memory') if resources.limits else "N/A"

            writer.writerow([
                metadata.namespace, metadata.name, container.name,
                cpu_req, cpu_lim, mem_req, mem_lim, restarts, age_days
            ])

print(f"✅ Metrics written to {output_path}")