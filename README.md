  
# VirIoT
![VirIoT](Extra/cloud-icon.png)

These are the instructions to quickly setup an instance of the VirIoT platform being developed
by the [Fed4IoT](https://fed4iot.org) EU-Japan project.

The VirIoT platform enables virtualization of IoT systems, formed by VirtualThings and brokers. 
That allows owners of IoT infrastructures to share them with many IoT application developers, 
which can simply rent the VirtualThings and the brokers their applications need.

The setup of this demo configuration was tested on Ubuntu 18.04. It's divided into two parts:  
1. Initial configuration, it's possible to setup the configuration either on Docker or Kubernetes. 
    * [Docker Deployment](Doc/Docker%20Depolyment.md): to setup the Docker based implementation.
    * [Kubernetes Deployment](Doc/Kubernetes%20Deployment.md): to setup the Kubernetes based implementation.
2. [CLI Usage Example](Doc/CLI%20Usage%20Example.md): shows the CLI usage.

# References
- Detti, A.; Nakazato, H.; Martínez Navarro, J.A.; Tropea, G.; Funari, L.; Petrucci, L.; Sánchez Segado, J.A.; Kanai, K. “VirIoT: A Cloud of Things That Offers IoT Infrastructures as a Service” in Sensors 2021, 21, 6546
- Andrea Detti, Giuseppe Tropea, Giulio Rossi, Juan A. Martinez, Antonio F. Skarmeta, and Hidenori Nakazato, “Virtual IoT Systems: Boosting IoT Innovation by Decoupling Things Providers and Applications Developers”, Proceedings of IEEE Global IoT Summit 2019, Aarhus, Denmark
