#
# Conditional build:
%bcond_without	blas		# OpenBLAS/CBLAS for neural network acceleration
%bcond_without	hyperscan	# Hyperscan/Vectorscan fast regexp processing
%bcond_without	jemalloc	# jemalloc allocator
%bcond_without	system_xxhash	# system xxhash instead of bundled
%bcond_without	system_zstd	# system zstd instead of bundled
#
Summary:	Fast, free and open-source spam filtering system
Summary(pl.UTF-8):	Szybki, wolny system filtrowania spamu
Name:		rspamd
Version:	4.0.0
Release:	0.1
License:	Apache v2.0
Group:		Networking/Daemons
Source0:	https://github.com/rspamd/rspamd/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	cf16e0556c82b7ba749a8035517e8353
Source1:	%{name}.tmpfiles
Source2:	%{name}.init
Source3:	%{name}.sysconfig
URL:		https://rspamd.com
BuildRequires:	cmake >= 3.15
BuildRequires:	glib2-devel >= 1:2.28
BuildRequires:	libarchive-devel >= 3.0.0
BuildRequires:	libicu-devel
BuildRequires:	libsodium-devel >= 1.0.0
BuildRequires:	libstdc++-devel >= 6:10
BuildRequires:	luajit-devel
BuildRequires:	openssl-devel
BuildRequires:	pcre2-8-devel
BuildRequires:	perl-base
BuildRequires:	pkgconfig
BuildRequires:	ragel
BuildRequires:	rpmbuild(macros) >= 1.644
BuildRequires:	sqlite3-devel
BuildRequires:	zlib-devel
%{?with_blas:BuildRequires:	cblas-devel}
%{?with_blas:BuildRequires:	lapack-devel}
%{?with_hyperscan:BuildRequires:	vectorscan-devel}
%{?with_jemalloc:BuildRequires:	jemalloc-devel}
%{?with_system_xxhash:BuildRequires:	xxHash-devel}
%{?with_system_zstd:BuildRequires:	zstd-devel}
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	glib2 >= 1:2.28
Requires:	rc-scripts
Suggests:	redis-server
Provides:	group(rspamd)
Provides:	user(rspamd)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libdir		%{_prefix}/lib/%{name}

%description
Rspamd is a fast, free and open-source spam filtering system. It can
be integrated with any MTA and provides advanced spam filtering
through multiple analysis methods including statistical, regexp-based,
and custom Lua rules.

Key features:
- event driven architecture allowing to process many messages at a time
- flexible syntax of rules allowing to write rules in Lua language
- advanced machine learning based statistical module
- a lot of plugins and rules shipped with rspamd distribution
- web interface for configuration and monitoring
- highly optimized mail processing

%description -l pl.UTF-8
Rspamd to szybki, wolny system filtrowania spamu. Może być
zintegrowany z dowolnym MTA i zapewnia zaawansowane filtrowanie spamu
poprzez wiele metod analizy, w tym statystyczne, oparte na wyrażeniach
regularnych i niestandardowe reguły Lua.

%prep
%setup -q

%{__sed} -i -e '1s,/usr/bin/env perl,/usr/bin/perl,' utils/rspamd_stats.pl utils/mapstats.pl

%build
install -d build
cd build
CFLAGS="%{rpmcflags}%{?with_jemalloc: -DJEMALLOC_MANGLE}"
CXXFLAGS="%{rpmcxxflags}%{?with_jemalloc: -DJEMALLOC_MANGLE}"
export CFLAGS CXXFLAGS
%cmake \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCONFDIR=%{_sysconfdir}/%{name} \
	-DDBDIR=/var/lib/%{name} \
	%{?with_blas:-DENABLE_BLAS=ON} \
	%{?with_hyperscan:-DENABLE_HYPERSCAN=ON} \
	%{?with_jemalloc:-DENABLE_JEMALLOC=ON} \
	-DENABLE_LUAJIT=ON \
	-DENABLE_PCRE2=ON \
	-DENABLE_SNOWBALL=ON \
	-DINSTALL_WEBUI=ON \
	-DLOGDIR=/var/log/%{name} \
	-DMANDIR=%{_mandir} \
	-DNO_SHARED=ON \
	-DRSPAMD_LIBDIR=%{_libdir} \
	-DRUNDIR=/var/run/%{name} \
	%{?with_system_xxhash:-DSYSTEM_XXHASH=ON} \
	%{?with_system_zstd:-DSYSTEM_ZSTD=ON} \
	-DWANT_SYSTEMD_UNITS=OFF \
	..

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d,tmpfiles.d} \
	$RPM_BUILD_ROOT/var/{lib,log,run}/%{name}

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

# move example files to doc directory preserving structure
install -d examples
cd $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
find . -name '*.example' | while read f; do
	install -D -m 644 "$f" $OLDPWD/examples/"$f"
	%{__rm} "$f"
done
cd -

cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/tmpfiles.d/%{name}.conf
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 294 %{name}
%useradd -u 294 -d /var/lib/%{name} -g %{name} -c "rspamd User" -s /sbin/nologin %{name}

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%files
%defattr(644,root,root,755)
%doc LICENSE.md README.md examples
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
/etc/tmpfiles.d/%{name}.conf
%attr(755,root,root) %{_bindir}/rspamc-*
%{_bindir}/rspamc
%attr(755,root,root) %{_bindir}/rspamd-*
%{_bindir}/rspamd
%attr(755,root,root) %{_bindir}/rspamadm-*
%{_bindir}/rspamadm
%attr(755,root,root) %{_bindir}/rspamd_stats
%attr(755,root,root) %{_bindir}/mapstats

# config
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/rspamd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/actions.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/common.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/composites.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/groups.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/lang_detection.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/logging.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/metrics.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/modules.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/options.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/settings.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/statistic.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-controller.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-fuzzy.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-normal.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-proxy.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-hs_helper.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-hs_helper.inc

%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/override.d
%dir %{_sysconfdir}/%{name}/lua.local.d
%dir %{_sysconfdir}/%{name}/modules.local.d

%dir %{_sysconfdir}/%{name}/maps.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/*.inc

%dir %{_sysconfdir}/%{name}/modules.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/modules.d/*.conf

%dir %{_sysconfdir}/%{name}/scores.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/scores.d/*.conf

# private libraries
%dir %{_libdir}
%attr(755,root,root) %{_libdir}/librspamd-server.so
%attr(755,root,root) %{_libdir}/librspamd-actrie.so
%attr(755,root,root) %{_libdir}/librspamd-ev.so
%attr(755,root,root) %{_libdir}/librspamd-kann.so
%attr(755,root,root) %{_libdir}/librspamd-replxx.so

# data files
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/effective_tld_names.dat
%dir %{_datadir}/%{name}/languages
%{_datadir}/%{name}/languages/*.json
%{_datadir}/%{name}/languages/stop_words

# lua libraries
%dir %{_datadir}/%{name}/lualib
%{_datadir}/%{name}/lualib/*.lua
%dir %{_datadir}/%{name}/lualib/lua_content
%{_datadir}/%{name}/lualib/lua_content/*.lua
%dir %{_datadir}/%{name}/lualib/lua_ffi
%{_datadir}/%{name}/lualib/lua_ffi/*.lua
%dir %{_datadir}/%{name}/lualib/lua_magic
%{_datadir}/%{name}/lualib/lua_magic/*.lua
%dir %{_datadir}/%{name}/lualib/lua_scanners
%{_datadir}/%{name}/lualib/lua_scanners/*.lua
%dir %{_datadir}/%{name}/lualib/lua_selectors
%{_datadir}/%{name}/lualib/lua_selectors/*.lua
%dir %{_datadir}/%{name}/lualib/lua_shape
%{_datadir}/%{name}/lualib/lua_shape/*.lua
%dir %{_datadir}/%{name}/lualib/plugins
%{_datadir}/%{name}/lualib/plugins/*.lua
%dir %{_datadir}/%{name}/lualib/plugins/neural
%dir %{_datadir}/%{name}/lualib/plugins/neural/providers
%{_datadir}/%{name}/lualib/plugins/neural/providers/*.lua
%dir %{_datadir}/%{name}/lualib/redis_scripts
%{_datadir}/%{name}/lualib/redis_scripts/*.lua
%dir %{_datadir}/%{name}/lualib/rspamadm
%{_datadir}/%{name}/lualib/rspamadm/*.lua

# lua plugins
%dir %{_datadir}/%{name}/plugins
%{_datadir}/%{name}/plugins/*.lua

# rules
%dir %{_datadir}/%{name}/rules
%{_datadir}/%{name}/rules/*.lua
%dir %{_datadir}/%{name}/rules/regexp
%{_datadir}/%{name}/rules/regexp/*.lua
%dir %{_datadir}/%{name}/rules/controller
%{_datadir}/%{name}/rules/controller/*.lua

# web UI
%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*

# man pages
%{_mandir}/man1/rspamadm.1*
%{_mandir}/man1/rspamc.1*
%{_mandir}/man8/rspamd.8*

# runtime directories
%attr(750,rspamd,rspamd) %dir /var/lib/%{name}
%attr(750,rspamd,rspamd) %dir /var/log/%{name}
%attr(755,rspamd,rspamd) %dir /var/run/%{name}
