# TODO:
# - use more system packages? (jarjar, lib/integration/*)
# - build javadoc (now it fails)
# - does not build with gcj.
#
# Conditional build:
%bcond_with	javadoc		# don't build javadoc
%bcond_without	tests		# don't build and run tests
%bcond_with 	binary		# do not compile .jars from source use bundled ones
%bcond_with	bootstrap	# break BR loop (java-junit, java-qdox)

%if "%{pld_release}" == "ti"
%bcond_without	java_sun	# build with gcj
%else
%bcond_without	java_sun	# build with java-sun
%endif

%if %{with bootstrap}
%define		with_binary	1
%endif

%define		srcname	hamcrest
%include	/usr/lib/rpm/macros.java
Summary:	Hamcrest - a library of matchers
Summary(pl.UTF-8):	Hamcrest - biblioteka klas dopasowujących
Name:		java-hamcrest
Version:	1.1
Release:	2%{?with_bootstrap:.bootstrap}
License:	BSD
Group:		Libraries/Java
Source0:	http://hamcrest.googlecode.com/files/%{srcname}-%{version}.tgz
# Source0-md5:	1bd4fd301c1a0dc748082378a59cb281
Source1:	http://hamcrest.googlecode.com/files/%{srcname}-text-%{version}.jar
# Source1-md5:	6267206d906192119a8e9770f7e2ed65
Patch0:		%{srcname}-nosrc.patch
URL:		http://code.google.com/p/hamcrest/
%if %{without binary}
%{!?with_java_sun:BuildRequires:	java-gcj-compat-devel}
%{?with_java_sun:BuildRequires:	java-sun >= 1.5}
%endif
BuildRequires:	ant >= 1.6
%{?with_tests:BuildRequires:	ant-junit >= 1.6}
%{?with_tests:BuildRequires:	java-junit}
BuildRequires:	java-qdox
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

rm -vf lib/integration/junit-*.jar
rm -vf lib/generator/qdox-*.jar

%if %{with binary}
# hamcrest-text somewhy missing in jar
cp -a %{SOURCE1} .
%else
rm -vf *.jar
%endif

# TODO: add new property (with this default value) do be override with -D
# TODO: add build.properties support to build.xml
%{__sed} -i -e 's,lib/generator/qdox-1.6.1.jar,${qdox.jar},g' build.xml

%build
export JAVA_HOME="%{java_home}"

qdox_jar=$(find-jar qdox)
CLASSPATH=$qdox_jar
cat <<EOF > build.properties
qdox.jar=$qdox_jar
EOF

%if %{with binary}
install -d build
cp -af *.jar build
%else
%ant core generator library text integration \
	-Dqdox.jar=$qdox_jar \
	-Dversion=%{version}
%endif

%if %{with javadoc}
# doesn't build
%ant javadoc \
	-Dqdox.jar=$qdox_jar \
	-Dversion=%{version}
%endif

%if %{with tests}
%ant unit-test \
	-Dqdox.jar=$qdox_jar \
	-Dversion=%{version}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_javadir}

for f in core generator integration library text; do
	cp -a build/hamcrest-$f-%{version}.jar $RPM_BUILD_ROOT%{_javadir}
	ln -sf hamcrest-$f-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/hamcrest-$f.jar
done

%if %{with javadoc}
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

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{srcname}-%{version}
%ghost %{_javadocdir}/%{srcname}
%endif
