# TODO:
# - use more systen packages? (jarjar, lib/integration/*)
# - build javadoc (now it fails)
# - does not build with gcj.
#
# Conditional build:
%bcond_without tests	# don't perform ant unit-test
#
%if "%{pld_release}" == "ti"
%bcond_without	java_sun	# build with gcj
%else
%bcond_with	java_sun	# build with java-sun
%endif
#
%include	/usr/lib/rpm/macros.java

%define		srcname	hamcrest
Summary:	Hamcrest - a library of matchers
Summary(pl.UTF-8):	Hamcrest - biblioteka klas dopasowujących
Name:		java-hamcrest
Version:	1.1
Release:	1
License:	BSD
Group:		Libraries/Java
Source0:	http://hamcrest.googlecode.com/files/%{srcname}-%{version}.tgz
# Source0-md5:	1bd4fd301c1a0dc748082378a59cb281
Patch0:		%{srcname}-nosrc.patch
URL:		http://code.google.com/p/hamcrest/
BuildRequires:	ant >= 1.6
%{?with_tests:BuildRequires:	ant-junit >= 1.6}
%{!?with_java_sun:BuildRequires:	java-gcj-compat-devel}
%{?with_tests:BuildRequires:	java-junit}
BuildRequires:	java-qdox
%{?with_java_sun:BuildRequires:	java-sun >= 1.5}
BuildRequires:	jpackage-utils
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.300
Requires:	jpackage-utils
Requires:	java-qdox
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Hamcrest is a library of matchers, which can be combined in to create
flexible expressions of intent in tests.

%description -l pl.UTF-8
Hamcrest to biblioteka klas dopasowujących, które można łączyć w celu
utworzenia elastycznych wyrażeń do wykorzystania w testach.

%package javadoc
Summary:	Javadoc manual for hamcrest
Summary(pl.UTF-8):	Dokumentacja javadoc do hamcresta
Group:		Documentation
Requires:	jpackage-utils

%description javadoc
Javadoc manual for hamcrest.

%description javadoc -l pl.UTF-8
Dokumentacja javadoc do hamcresta.

%prep
%setup -q -n %{srcname}-%{version}
%patch0 -p1

rm -vf *.jar
rm -vf lib/integration/junit-*.jar
rm -vf lib/generator/qdox-*.jar

# TODO: add new property (with this default value) do be override with -D
# TODO: add build.properties support to build.xml
%{__sed} -i -e 's,lib/generator/qdox-1.6.1.jar,${qdox.jar},g' build.xml

%build
export JAVA_HOME="%{java_home}"

CLASSPATH=$(find-jar qdox)
cat <<EOF > build.properties
qdox.jar=$(find-jar qdox)
EOF

%ant core generator library text integration \
	-Dqdox.jar=$(find-jar qdox) \
	-Dversion=%{version}

%if 0
# doesn't build
%ant javadoc \
	-Dversion=%{version}
%endif

%if %{with tests}
%ant unit-test \
	-Dversion=%{version}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_javadir}

for f in core generator integration library text; do
	cp -a build/hamcrest-$f-%{version}.jar $RPM_BUILD_ROOT%{_javadir}
	ln -sf hamcrest-$f-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/hamcrest-$f.jar
done

%if 0
# javadoc
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
cp -a dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
ln -s %{srcname}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{srcname} # ghost symlink
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
ln -nfs %{srcname}-%{version} %{_javadocdir}/%{srcname}

%files
%defattr(644,root,root,755)
%doc CHANGES.txt LICENSE.txt README.txt
%{_javadir}/*.jar

%if 0
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{srcname}-%{version}
%ghost %{_javadocdir}/%{srcname}
%endif
