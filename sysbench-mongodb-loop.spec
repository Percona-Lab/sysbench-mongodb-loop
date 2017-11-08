%define run_user	nobody
%define run_group	nobody
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
Prefix:		/opt

Requires:	java-1.8.0-openjdk
BuildRequires:	java-1.8.0-openjdk java-1.8.0-openjdk-devel


%description
A wrapper to run sysbench-mongodb forever


%build
cp -dpR %{SOURCE2} sysbench-mongodb
cd sysbench-mongodb
rm -rf .git .gitignore

# Build the classes
curl -Lo mongo-java-driver-%{java_driver}.jar %{java_driver_url}
export CLASSPATH=mongo-java-driver-%{java_driver}.jar:$CLASSPATH
javac -cp $CLASSPATH:$PWD/src src/jmongosysbenchload.java
javac -cp $CLASSPATH:$PWD/src src/jmongosysbenchexecute.java

# Stop run.simple.bash from compiling the tool with javac
sed -i -e /^javac/d run.simple.bash


%install
mkdir -p %{buildroot}/usr/lib/systemd/system %{buildroot}%{prefix}/%{name}/{logs,tmp}

mv -f sysbench-mongodb %{buildroot}%{prefix}/%{name}/sysbench-mongodb

install %{SOURCE0} %{buildroot}%{prefix}/%{name}/%{name}.sh

%{__cat} <<EOF >>%{buildroot}%{prefix}/%{name}/config.sh
DELETE_DATABASE=true
KEEP_OUTPUT=false
SHARD_DATABASE=false
ADMIN_USERNAME=none
ADMIN_PASSWORD=none
ITER_SLEEP=60

BASE_DIR=%{prefix}/%{name}
SYSBENCH_MONGODB_DIR=\$BASE_DIR/sysbench-mongodb
SYSBENCH_MONGODB_LOG=\$BASE_DIR/logs/sysbench-mongodb.log
SYSBENCH_MONGODB_CONFIG=\$SYSBENCH_MONGODB_DIR/config.bash
SYSBENCH_MONOGDB_JAVA_DRIVER=\$SYSBENCH_MONGODB_DIR/mongo-java-driver-%{java_driver}.jar
EOF

%{__cat} <<EOF >>%{buildroot}/usr/lib/systemd/system/%{name}.service
[Unit]
Description=sysbench-mongodb
After=time-sync.target network.target

[Service]
Type=forking
User=%{run_user}
Group=%{run_group}
PermissionsStartOnly=true
EnvironmentFile=%{prefix}/%{name}/config.sh
ExecStart=/usr/bin/env bash -c "%{prefix}/%{name}/sysbench-mongodb-loop.sh & echo \$! >%{prefix}/%{name}/tmp/sysbench-mongodb-loop.pid; disown \$!"
PIDFile=%{prefix}/%{name}/tmp/sysbench-mongodb-loop.pid

[Install]
WantedBy=multi-user.target
EOF


%files
%config %{prefix}/%{name}/config.sh
%{prefix}/%{name}/%{name}.sh
/usr/lib/systemd/system/%{name}.service
%config %{prefix}/%{name}/sysbench-mongodb/config.bash
%{prefix}/%{name}/sysbench-mongodb/mongo-java-driver-%{java_driver}.jar
%{prefix}/%{name}/sysbench-mongodb/run.simple.bash
%{prefix}/%{name}/sysbench-mongodb/src/*
%{prefix}/%{name}/sysbench-mongodb/README.md
%{prefix}/%{name}/sysbench-mongodb/TODO


%post
/usr/bin/systemctl daemon-reload

[ ! -d "%{prefix}/%{name}/logs" ] && mkdir -p %{prefix}/%{name}/logs
[ ! -d "%{prefix}/%{name}/tmp" ] && mkdir -p %{prefix}/%{name}/tmp

chown -R %{run_user}:%{run_group} %{prefix}/%{name}

%preun
/usr/bin/systemctl disable %{name} 2>/dev/null || true
/usr/bin/systemctl stop %{name} 2>/dev/null || true


%postun
/usr/bin/systemctl daemon-reload


%changelog
