* Local processes under a governor
* Governor may spawn new child component containers up to a limit. By default the limit is twice the processor count.
* Governors may order idle containers to shut down.
* Governor detects zombies by pinging on control plane and timing out on pongs in single threaded control loop.
* Governors are invisible to the component network.
* Governor may be extended with strategy plugins:
- zombie detection response
- ‎logging plugin
* One governor per local machine is the norm, but not enforced.
* Governors do not participate in discovery and are not discoverable.
* Governors do not need to be restarted when components are added, removed, or redeployed.
- Instead they periodically scan the components sub directory to detect changes.
- May need a deployment lock file or governor components shutdown messages to prevent spawning while deploying and to cleanly shut down running components before deployment.
- Maybe allow governor process to be recycled without killing children.
* governor may need to distinguish a suicide from other types of container exists
