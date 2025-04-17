#
Summary:	Spam filter to replace spamassassin
Name:		rspamd
Version:	3.11.1
Release:	1
License:	Apache v2.0
Group:		Applications
Source0:	https://github.com/vstakhov/rspamd/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	b9dbae75d993d990fb30d1221f2befa4
Source1:	%{name}.tmpfiles
Source2:	%{name}.init
Source3:	%{name}.sysconfig
URL:		https://rspamd.com
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
BuildRequires:	cmake
BuildRequires:	glib2-devel
BuildRequires:	lapack-devel
BuildRequires:	libarchive-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	libicu-devel
BuildRequires:	libmagic-devel
BuildRequires:	libsodium-devel
BuildRequires:	libunwind-devel
BuildRequires:	lua51-devel
BuildRequires:	luajit-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	ragel
BuildRequires:	sqlite3-devel
Requires:	rc-scripts
Provides:	group(rspamd)
Provides:	user(rspamd)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# debugsource package fails
%define         _enable_debug_packages 0

%description
Rspamd is a complex spam filter that allows to estimate messages by
many rules, statistical data and custom services like URL black lists.
Each message is estimated by rspamd and got so called 'spam score'.
According to spam score and user's settings rspamd send recommended
action for this message to MTA. Rspamd has own unique features among
spam filters:

- event driven architecture allowing to process many messages at a
  time
- flexible syntax of rules allowing to write rules in lua language
- a lot of plugins and rules shipped with rspamd distribution
- highly optimized mail processing
- advanced statistic All these features allow rspamd to process
  messages fast and make good results in spam filtering.

%prep
%setup -q

%build
install -d build
cd build
%{__cmake} \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCONFDIR=%{_sysconfdir}/%{name} \
	-DLIBDIR=%{_libdir} \
	..

%{__make}
cd ..
%{__sed} -i -e '1s,/usr/bin/env perl,/usr/bin/perl,' utils/rspamd_stats.pl

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{_sysconfdir}/%{name}/{local.d,override.d}} \
        $RPM_BUILD_ROOT/var/log/%{name} \
        $RPM_BUILD_ROOT/var/run/%{name}

install -d $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d
cp -p %SOURCE1 $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/%{name}.conf
cp -p %SOURCE2 $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p %SOURCE3 $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 294 %{name}
%useradd -u 294 -d /var/lib/%{name} -g %{name} -c "rspamd User" %{name}

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%post
/sbin/ldconfig
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog LICENSE.md README.md
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{_sysconfdir}/tmpfiles.d/rspamd.conf
%attr(755,root,root) %{_bindir}/rspam*
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/local.d
%{_sysconfdir}/%{name}/local.d/*.example
%dir %{_sysconfdir}/%{name}/override.d
%{_sysconfdir}/%{name}/override.d/*.example
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/actions.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/cgp.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/common.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/composites.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/groups.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/lang_detection.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/logging.inc
%dir %{_sysconfdir}/%{name}/lua.local.d
%{_sysconfdir}/%{name}/lua.local.d/*.example
%dir %{_sysconfdir}/%{name}/maps.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/dmarc_whitelist.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/exe_clickbait.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/maillist.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/mid.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/mime_types.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/redirectors.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/spf_dkim_whitelist.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maps.d/surbl-whitelist.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/metrics.conf
%dir %{_sysconfdir}/%{name}/modules.local.d
%{_sysconfdir}/%{name}/modules.local.d/*.example
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/modules.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/options.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/rspamd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/settings.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/statistic.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-controller.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-fuzzy.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-normal.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/worker-proxy.inc
%dir %{_sysconfdir}/%{name}/modules.d/
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/modules.d/*.conf
%dir %{_sysconfdir}/%{name}/scores.d/
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/scores.d/*.conf
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/effective_tld_names.dat
%dir %{_datadir}/%{name}/languages/
%{_datadir}/%{name}/languages/*.json
%{_datadir}/%{name}/languages/stop_words
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
%dir %{_datadir}/%{name}/lualib/plugins
%{_datadir}/%{name}/lualib/plugins/*.lua
%dir %{_datadir}/%{name}/lualib/redis_scripts
%{_datadir}/%{name}/lualib/redis_scripts/*.lua
%dir %{_datadir}/%{name}/lualib/rspamadm
%{_datadir}/%{name}/lualib/rspamadm/*.lua
%dir %{_datadir}/%{name}/plugins
%{_datadir}/%{name}/plugins/*.lua
%dir %{_datadir}/%{name}/rules
%{_datadir}/%{name}/rules/*.lua
%dir %{_datadir}/%{name}/rules/regexp
%{_datadir}/%{name}/rules/regexp/*.lua
%dir %{_datadir}/%{name}/rules/controller
%{_datadir}/%{name}/rules/controller/*.lua
%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*
%attr(755,root,root) %{_libdir}/*.so
%{_mandir}/man1/rspamadm.1*
%{_mandir}/man1/rspamc.1*
%{_mandir}/man8/rspamd.8*
%dir %attr(750,root,logs) /var/log/%{name}
%dir /var/run/%{name}

%changelog
* Wed May 15 2013 PLD Linux Team <feedback@pld-linux.org>
- For complete changelog see:	http://git.pld-linux.org/?p=packages/rspamd.git;a=log
