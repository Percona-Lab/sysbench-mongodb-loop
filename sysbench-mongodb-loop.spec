%define	java_driver	2.13.0
%define java_driver_url	https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/%{java_driver}/mongo-java-driver-%{java_driver}.jar

Name:		sysbench-mongodb-loop
Version:	0.0.1
Release:	1%{?dist}
Summary:	A wrapper to run sysbench-mongodb forever

Group:		Software/Databases
License:	Apache License 2.0
URL:		https://github.com/Percona-Lab/sysbench-mongodb-loop
Source0:	sysbench-mongodb-loop.sh
Source1:	sysbench-mongodb-loop.service
Source2:        sysbench-mongodb
Source3:	https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/%{java_driver}/mongo-java-driver-%{java_driver}.jar


%description
A wrapper to run sysbench-mongodb forever


%install
mkdir -p %{buildroot}/usr/lib/systemd/system %{buildroot}/opt/%{name}/logs

install %{SOURCE0} %{buildroot}/opt/%{name}/%{name}.sh
install %{SOURCE1} %{buildroot}/usr/lib/systemd/system/%{name}.service
cp -dpR %{SOURCE2} %{buildroot}/opt/%{name}/sysbench-mongodb
rm -rf %{buildroot}/opt/%{name}/sysbench-mongodb/.git

curl -Lo %{buildroot}/opt/%{name}/sysbench-mongodb/mongo-java-driver-%{java_driver}.jar %{java_driver_url}


%files
/opt/%{name}/%{name}.sh
/usr/lib/systemd/system/%{name}.service
/opt/%{name}/sysbench-mongodb


%post
/usr/bin/systemctl daemon-reload


%preun
/usr/bin/systemctl disable %{name} 2>/dev/null || true
/usr/bin/systemctl stop %{name} 2>/dev/null || true


%postun
/usr/bin/systemctl daemon-reload


%changelog
