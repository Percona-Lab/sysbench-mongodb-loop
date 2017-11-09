%define run_user	nobody
%define run_group	nobody
%define	java_driver	2.14.3
%define java_driver_url	https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/%{java_driver}/mongo-java-driver-%{java_driver}.jar

Name:		sysbench-mongodb-loop
Version:	0.0.1
Release:	1%{?dist}
Summary:	A wrapper to run sysbench-mongodb forever

Group:		Software/Databases
License:	Apache License 2.0
URL:		https://github.com/Percona-Lab/sysbench-mongodb-loop
Source0:        sysbench-mongodb
Source1:	sysbench-mongodb-loop.sh
Source2:        README.md
Prefix:		/opt

Requires:	java-1.8.0-openjdk
BuildRequires:	java-1.8.0-openjdk java-1.8.0-openjdk-devel


%description
A wrapper to run sysbench-mongodb forever


%package devel
Summary:	A wrapper to run sysbench-mongodb forever - Devel


%description devel
A wrapper to run sysbench-mongodb forever - Devel


%build
cp -dpR %{SOURCE0} sysbench-mongodb

curl -Lo mongo-java-driver-%{java_driver}.jar %{java_driver_url}

cd sysbench-mongodb
rm -rf .git .gitignore

# Build the classes
javac -cp ../mongo-java-driver-%{java_driver}.jar:$PWD/src src/jmongosysbenchload.java
javac -cp ../mongo-java-driver-%{java_driver}.jar:$PWD/src src/jmongosysbenchexecute.java

# Stop run.simple.bash from compiling the tool with javac
sed -i -e /^javac/d run.simple.bash


%install
mkdir -p %{buildroot}/usr/lib/systemd/system %{buildroot}%{prefix}/%{name}/{logs,tmp}

mv -f mongo-java-driver-%{java_driver}.jar %{buildroot}%{prefix}/%{name}/mongo-java-driver-%{java_driver}.jar
mv -f sysbench-mongodb %{buildroot}%{prefix}/%{name}/sysbench-mongodb

install %{SOURCE1} %{buildroot}%{prefix}/%{name}/%{name}.sh
install %{SOURCE2} %{buildroot}%{prefix}/%{name}/README.md

%{__cat} <<EOF >>%{buildroot}%{prefix}/%{name}/config.sh
KEEP_OUTPUT=false
SHARD_DATABASE=false
ADMIN_USERNAME=none
ADMIN_PASSWORD=none
ITER_SLEEP=60

BASE_DIR=%{prefix}/%{name}
SYSBENCH_MONGODB_LOG=\$BASE_DIR/logs/sysbench-mongodb.log
SYSBENCH_MONGODB_DIR=\$BASE_DIR/sysbench-mongodb
SYSBENCH_MONGODB_CONFIG=\$SYSBENCH_MONGODB_DIR/config.bash
SYSBENCH_MONOGDB_JAVA_DRIVER=\$BASE_DIR/mongo-java-driver-%{java_driver}.jar
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
ExecStart=/usr/bin/env bash -c "%{prefix}/%{name}/%{name}.sh & echo \$! >%{prefix}/%{name}/tmp/%{name}.pid; disown \$!"
PIDFile=%{prefix}/%{name}/tmp/%{name}.pid

[Install]
WantedBy=multi-user.target
EOF


%files
%doc %attr(0644, root, root) %{prefix}/%{name}/README.md
%config %{prefix}/%{name}/config.sh
%{prefix}/%{name}/%{name}.sh
/usr/lib/systemd/system/%{name}.service
%config %{prefix}/%{name}/sysbench-mongodb/config.bash
%{prefix}/%{name}/mongo-java-driver-%{java_driver}.jar
%{prefix}/%{name}/sysbench-mongodb/run.simple.bash
%{prefix}/%{name}/sysbench-mongodb/src/*.class
%{prefix}/%{name}/sysbench-mongodb/README.md
%{prefix}/%{name}/sysbench-mongodb/TODO


%files devel
%{prefix}/%{name}/sysbench-mongodb/src/*.java


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
