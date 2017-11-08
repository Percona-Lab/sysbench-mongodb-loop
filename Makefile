all: rpm

rpm: *.sh *.spec
	mkdir rpmbuild 2>/dev/null || true
	rpmbuild -D '_topdir $(PWD)/rpmbuild' -D '_sourcedir $(PWD)' -bb sysbench-mongodb-loop.spec

clean:
	rm -rf rpmbuild 2>/dev/null || true
