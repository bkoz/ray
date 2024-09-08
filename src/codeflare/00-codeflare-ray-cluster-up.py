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
    token = "sha256~yFtgUCzFWyPCXLBMVisZ7gBc4_taXWh9cd8Rhx3h2q0",
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
    num_workers=2,
    worker_cpu_requests='250m',
    worker_cpu_limits=1,
    worker_memory_requests=4,
    worker_memory_limits=4,
    # image="", # Optional Field 
    write_to_file=False, # When enabled Ray Cluster yaml files are written to /HOME/.codeflare/resources 
    # local_queue="local-queue-name" # Specify the local queue manually
    namespace="ray"
))


# Next, we want to bring our cluster up, so we call the `up()` function below to submit our Ray Cluster onto the queue, and begin the process of obtaining our resource cluster.

# In[6]:


# Bring up the cluster
cluster.up()


# Now, we want to check on the status of our resource cluster, and wait until it is finally ready for use.

# In[7]:


cluster.status()


# In[8]:


cluster.wait_ready()


# In[9]:


cluster.status()


# Let's quickly verify that the specs of the cluster are as expected.

# In[11]:


cluster.details()

print(cluster.cluster_uri())
print(cluster.cluster_dashboard_uri())

# Finally, we bring our resource cluster down and release/terminate the associated resources, bringing everything back to the way it was before our cluster was brought up.

# In[12]:

sleep_time = 120
print(f'Sleeping for {sleep_time} seconds.')
time.sleep(sleep_time)

cluster.down()


# In[13]:


auth.logout()


# In[ ]:




