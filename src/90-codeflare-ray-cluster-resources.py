#!/usr/bin/env python
# coding: utf-8

# In this notebook, we will go through the basics of using the SDK to:
#  - Spin up a Ray cluster with our desired resources
#  - View the status and specs of our Ray cluster
#  - Take down the Ray cluster when finished

# In[1]:

import time

# get_ipython().system('pip install codeflare-sdk==0.19.1 -q')


# In[2]:


# Import pieces from codeflare-sdk
from codeflare_sdk import Cluster, ClusterConfiguration, TokenAuthentication


# In[10]:


# Create authentication object for user permissions
# IF unused, SDK will automatically check for default kubeconfig, then in-cluster config
# KubeConfigFileAuthentication can also be used to specify kubeconfig path manually
auth = TokenAuthentication(
    token = "sha256~MlaBwkFwiKTdxfZYBlJsCZQUHN60kcmOCcsBU8v6WoQ",
    server = "https://api.ocp.sandbox2640.opentlc.com:6443",
    skip_tls=False
)
auth.login()


# Here, we want to define our cluster by specifying the resources we require for our batch workload. Below, we define our cluster object (which generates a corresponding RayCluster).
# 
# NOTE: 'quay.io/rhoai/ray:2.23.0-py39-cu121' is the default community image used by the CodeFlare SDK for creating a RayCluster resource. 
# If you have your own Ray image which suits your purposes, specify it in image field to override the default image.

# In[5]:


# Create and configure our cluster object
# The SDK will try to find the name of your default local queue based on the annotation "kueue.x-k8s.io/default-queue": "true" unless you specify the local queue manually below
cluster = Cluster(ClusterConfiguration(
    name='raytest', 
    head_cpus='500m',
    head_memory=2,
    head_extended_resource_requests={'nvidia.com/gpu':0}, # For GPU enabled workloads set the head_extended_resource_requests and worker_extended_resource_requests
    worker_extended_resource_requests={'nvidia.com/gpu':0},
    num_workers=1,
    worker_cpu_requests='250m',
    worker_cpu_limits=1,
    worker_memory_requests=4,
    worker_memory_limits=4,
    # image="", # Optional Field 
    write_to_file=False, # When enabled Ray Cluster yaml files are written to /HOME/.codeflare/resources 
    local_queue="local-queue-test", # Specify the local queue manually
    namespace="sandbox"
))


# Next, we want to bring our cluster up, so we call the `up()` function below to submit our Ray Cluster onto the queue, and begin the process of obtaining our resource cluster.

# In[6]:


# Bring up the cluster
cluster.up()


# Now, we want to check on the status of our resource cluster, and wait until it is finally ready for use.


cluster.wait_ready()


# In[9]:


cluster.status()


# Let's quickly verify that the specs of the cluster are as expected.

# In[11]:


cluster.details()

print(cluster.cluster_uri())
print(cluster.cluster_dashboard_uri())

# Finally, we bring our resource cluster down and release/terminate the associated resources, bringing everything back to the way it was before our cluster was brought up.

# Initialize the Job Submission Client
"""
The SDK will automatically gather the dashboard address and authenticate using the Ray Job Submission Client
"""
client = cluster.job_client

# Submit an example mnist job using the Job Submission Client
submission_id = client.submit_job(
    entrypoint="python -c import ray; ray.init(); print(ray.cluster_resources)",
    # runtime_env={"working_dir": "./","pip": "requirements.txt"},
)

print(submission_id)

# Get the job's status
client.get_job_status(submission_id)
# Get job related info
client.get_job_info(submission_id)
# List all existing jobs
client.list_jobs()
# Iterate through the logs of a job 
#async for lines in client.tail_job_logs(submission_id):
#   print(lines, end="") 
# Delete a job
# Can run client.stop_job(submission_id) first if job is still running
client.delete_job(submission_id)

cluster.down()


# In[13]:


auth.logout()


# In[ ]:




