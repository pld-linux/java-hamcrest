# TODO:
# - use more system packages? (jarjar, lib/integration/*)
# - build javadoc (now it fails)
# - does not build with gcj.
#
# Conditional build:
%bcond_without	javadoc		# build javadoc
%bcond_with	tests		# build and run tests (tests are broken)
%bcond_with	binary		# do not compile .jars from source use bundled ones
%bcond_with	bootstrap	# break BR loop (java-junit, java-qdox)

%if %{with bootstrap}
%define		with_binary	1
%undefine	with_tests
%undefine	with_javadoc
%endif

%define		rel	2
%define		srcname	hamcrest
Summary:	Hamcrest - a library of matchers
Summary(pl.UTF-8):	Hamcrest - biblioteka klas dopasowujących
Name:		java-hamcrest
Version:	1.2
Release:	%{bootstrap_release %rel}
License:	BSD
Group:		Libraries/Java
Source0:	http://hamcrest.googlecode.com/files/%{srcname}-%{version}.tgz
# Source0-md5:	b4bd43f44d082d77daf7ec564d304cdf
Patch0:		%{srcname}-nosrc.patch
Patch1:		javadoc-build.patch
URL:		http://code.google.com/p/hamcrest/
%if %{without binary}
BuildRequires:	ant >= 1.6
%{?with_tests:BuildRequires:	ant-junit >= 1.6}
%{?with_tests:BuildRequires:	java-junit}
BuildRequires:	java-qdox
BuildRequires:	jdk
%endif
BuildRequires:	jpackage-utils
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.557
Requires:	java-qdox
Requires:	jpackage-utils
Obsoletes:	hamcrest
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
Obsoletes:	hamcrest-javadoc

%description javadoc
Javadoc manual for hamcrest.

%description javadoc -l pl.UTF-8
Dokumentacja javadoc do hamcresta.

%package source
Summary:	Source code of hamcrest
Summary(pl.UTF-8):	Kod źródłowy biblioteki hamcrest
Group:		Documentation
Requires:	jpackage-utils >= 1.7.5-2

%description source
Source code of hamcrest.

%description source -l pl.UTF-8
Kod źródłowy biblioteki hamcrest.

%prep
%setup -q -n %{srcname}-%{version}
%patch -P0 -p0
%patch -P1 -p0

%{__rm} lib/integration/junit-*.jar
%{__rm} lib/generator/qdox-*.jar

%if %{without binary}
%{__rm} *.jar
%endif

# TODO: add new property (with this default value) do be override with -D
# TODO: add build.properties support to build.xml
%{__sed} -i -e 's,lib/generator/qdox-1.6.1.jar,${qdox.jar},g' build.xml

%build
export JAVA_HOME="%{java_home}"

%if %{with binary}
install -d build
cp -af *.jar build
%else
qdox_jar=$(find-jar qdox)
CLASSPATH=$qdox_jar
cat <<EOF > build.properties
qdox.jar=$qdox_jar
EOF

%ant core generator library integration \
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

# source
%jar cf %{srcname}.src.jar -C build/temp/hamcrest-library/generated-code .
%jar uf %{srcname}.src.jar -C build/temp/hamcrest-core/generated-code .
for I in examples integration library generator core; do
	%jar uf %{srcname}.src.jar -C hamcrest-$I/src/main/java .
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_javadir}

for f in core generator integration library; do
	cp -a build/hamcrest-$f-%{version}.jar $RPM_BUILD_ROOT%{_javadir}
	ln -sf hamcrest-$f-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/hamcrest-$f.jar
done

%if %{with javadoc}
# javadoc
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
cp -a build/javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
ln -s %{srcname}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{srcname} # ghost symlink
%endif

#source
install -d $RPM_BUILD_ROOT%{_javasrcdir}
cp -a %{srcname}.src.jar $RPM_BUILD_ROOT%{_javasrcdir}/%{srcname}.src.jar

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
ln -nfs %{srcname}-%{version} %{_javadocdir}/%{srcname}

%files
%defattr(644,root,root,755)
%doc CHANGES.txt LICENSE.txt README.txt
%{_javadir}/hamcrest-core-%{version}.jar
%{_javadir}/hamcrest-core.jar
%{_javadir}/hamcrest-generator-%{version}.jar
%{_javadir}/hamcrest-generator.jar
%{_javadir}/hamcrest-integration-%{version}.jar
%{_javadir}/hamcrest-integration.jar
%{_javadir}/hamcrest-library-%{version}.jar
%{_javadir}/hamcrest-library.jar

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{srcname}-%{version}
%ghost %{_javadocdir}/%{srcname}
%endif

%files source
%defattr(644,root,root,755)
%{_javasrcdir}/%{srcname}.src.jar
