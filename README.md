# sysbench-mongodb-loop
A wrapper to run [sysbench-mongodb](https://github.com/tmcallaghan/sysbench-mongodb) forever and initiate sharding

See https://github.com/tmcallaghan/sysbench-mongodb for more on sysbench-mongodb

## Build
The project builds into a CentOS 7 compatible RPM

1. Ensure 'rpm-build', 'java-1.8.0-openjdk', 'java-1.8.0-openjdk-devel' and 'curl' are installed
2. Run 'make'
3. Get rpm file from 'rpmbuild/RPMS/x86_64/*.rpm'
