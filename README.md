# openta-blog
## Install project
-   ``git clone https://github.com/opentaproject/openta-blog.git sidecar ``

### create images
    - cd installs
      - cd blog
        - install
      - cd nginx
        - install
###  get kubernetes images running
    - k apply -f 0-storage-class.yaml
    - k apply -f 0-pv.yaml
    - k apply -f 5a-dbserver.yaml
    - k apply -f 6a-pgbouncer.yaml
    - k apply -f 6b-pgbouncer.yaml
    - k apply -f deployment.yaml