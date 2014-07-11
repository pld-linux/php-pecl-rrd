#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	rrd
Summary:	PHP Bindings for rrdtool
Name:		%{php_name}-pecl-%{modname}
Version:	1.1.3
Release:	2
License:	BSD
Group:		Development/Languages
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	bde6c50fa2aa39090ed22e574ac71c5a
URL:		http://pecl.php.net/package/rrd
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:5.3.2
BuildRequires:	rrdtool
BuildRequires:	rrdtool-devel >= 1.3.0
Obsoletes:	php-rrdtool < 1.2-9
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Procedural and simple OO wrapper for rrdtool - data logging and
graphing system for time series data.

%prep
%setup -qc
mv %{modname}-%{version}/* .

%build
phpize
%configure
%{__make}

%if %{with tests}
%{__php} --no-php-ini \
	--define extension=modules/%{modname}.so \
	--modules | grep %{modname}
%endif

%{__make} -C tests/data clean
%{__make} -C tests/data all
%{__make} test NO_INTERACTION=1 | tee rpmtests.log

if grep -q "FAILED TEST" rpmtests.log; then
	for t in tests/*diff; do
		echo "*** FAILED: $(basename $t .diff)"
		diff -u tests/$(basename $t .diff).exp tests/$(basename $t .diff).out || :
	done

	exit 1
fi

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc CREDITS LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
