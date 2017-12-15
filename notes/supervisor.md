* Local processes under a supervisor
* Supervisor may spawn new child component containers up to a limit. By default the limit is twice the processor count.
* Supervisors may order idle containers to shut down.
* Supervisor detects zombies by pinging on control plane and timing out on pongs in single threaded control loop.
* Supervisors are invisible to the component network.
* Supervisor may be extended with strategy plugins:
- zombie detection response
- ‎logging plugin
* One supervisor per local machine is the norm, but not enforced.
* Supervisors do not participate in discovery and are not discoverable.
* Supervisors do not need to be restarted when components are added, removed, or redeployed.
- Instead they periodically scan the components sub directory to detect changes.
- May need a deployment lock file or supervisor components shutdown messages to prevent spawning while deploying and to cleanly shut down running components before deployment.
- Maybe allow supervisor process to be recycled without killing children.
* supervisor may need to distinguish a suicide from other types of container exists
