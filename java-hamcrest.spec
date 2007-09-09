# TODO:
# - use more systen packages? (qdox, jarjar, lib/integration/*)
# - build javadoc (now it fails)
#
# Conditional build:
%bcond_without tests	# don't perform ant unit-test
#
%include	/usr/lib/rpm/macros.java
Summary:	Hamcrest - a library of matchers
Summary(pl.UTF-8):	Hamcrest - biblioteka klas dopasowujących
Name:		hamcrest
Version:	1.1
Release:	0.1
License:	BSD
Group:		Development/Languages/Java
Source0:	http://hamcrest.googlecode.com/files/%{name}-%{version}.tgz
# Source0-md5:	1bd4fd301c1a0dc748082378a59cb281
Patch0:		%{name}-nosrc.patch
URL:		http://code.google.com/p/hamcrest/
BuildRequires:	ant >= 1.6
%{?with_tests:BuildRequires:	ant-junit >= 1.6}
BuildRequires:	jdk >= 1.5
BuildRequires:	jpackage-utils
%{?with_tests:BuildRequires:	junit}
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.300
Requires:	jpackage-utils
BuildArch:	noarch
ExclusiveArch:	i586 i686 pentium3 pentium4 athlon %{x8664} noarch
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
%setup -q
%patch0 -p1

rm -f lib/integration/junit*

%build
export JAVA_HOME="%{java_home}"

%ant bigjar \
	-Dversion=%{version}

# doesn't build
#%ant javadoc \
#	-Dversion=%{version}

%if %{with tests}
%ant unit-test \
	-Dversion=%{version}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_javadir}

for f in all core generator integration library text ; do
	install build/hamcrest-${f}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}
	ln -sf hamcrest-${f}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/hamcrest-${f}.jar
done

# javadoc
#install -d $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
#cp -a dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
#ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
ln -nfs %{name}-%{version} %{_javadocdir}/%{name}

%files
%defattr(644,root,root,755)
%doc CHANGES.txt LICENSE.txt README.txt
%{_javadir}/hamcrest-all*.jar
%{_javadir}/hamcrest-core*.jar
%{_javadir}/hamcrest-generator*.jar
%{_javadir}/hamcrest-integration*.jar
%{_javadir}/hamcrest-library*.jar
%{_javadir}/hamcrest-text*.jar

#%files javadoc
#%defattr(644,root,root,755)
#%{_javadocdir}/%{name}-%{version}
#%ghost %{_javadocdir}/%{name}
