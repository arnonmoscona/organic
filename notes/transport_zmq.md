* Zmq socket -> uwrap message -> if control plane then route to appropriate controller object.
* If application plane then route body to the appropriate component.
* Zmq may drop messages, blocking new ones if socket buffer full.
