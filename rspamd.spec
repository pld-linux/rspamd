#
Summary:	Spam filter to replace spamassassin
Name:		rspamd
Version:	1.7.8
Release:	1
License:	Apache v2.0
Group:		Applications
# Source0:	https://rspamd.com/downloads/%{name}-%{version}.tar.xz
Source0:	https://github.com/vstakhov/rspamd/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	a1d63d548e7067538c7dbb3e655fd5d6
Source1:	%{name}.tmpfiles
Source2:	%{name}.init
Source3:	%{name}.sysconfig
URL:		https://rspamd.com
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
BuildRequires:	cmake
BuildRequires:	glib2-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	libicu-devel
BuildRequires:	libmagic-devel
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

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{_sysconfdir}/%{name}/{local.d,override.d}}

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
%doc ChangeLog LICENSE README.md
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{_sysconfdir}/tmpfiles.d/rspamd.conf
%attr(755,root,root) %{_bindir}/rspam*
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/override.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/2tld.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/actions.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/cgp.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/common.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/composites.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/dmarc_whitelist.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/groups.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/logging.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/maillist.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/metrics.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/mid.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/mime_types.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/modules.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/options.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/redirectors.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/rspamd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/spf_dkim_whitelist.inc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/statistic.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/surbl-whitelist.inc
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
%dir %{_datadir}/%{name}/elastic/
%{_datadir}/%{name}/elastic/*.json
%dir %{_datadir}/%{name}/languages/
%{_datadir}/%{name}/languages/*.json
%dir %{_datadir}/%{name}/lib
%{_datadir}/%{name}/lib/ansicolors.lua
%{_datadir}/%{name}/lib/argparse.lua
%{_datadir}/%{name}/lib/fun.lua
%{_datadir}/%{name}/lib/global_functions.lua
%{_datadir}/%{name}/lib/lua_auth_results.lua
%{_datadir}/%{name}/lib/lua_cfg_transform.lua
%{_datadir}/%{name}/lib/lua_dkim_tools.lua
%{_datadir}/%{name}/lib/lua_maps.lua
%{_datadir}/%{name}/lib/lua_meta.lua
%{_datadir}/%{name}/lib/lua_nn.lua
%{_datadir}/%{name}/lib/lua_redis.lua
%{_datadir}/%{name}/lib/lua_squeeze_rules.lua
%{_datadir}/%{name}/lib/lua_stat.lua
%{_datadir}/%{name}/lib/lua_util.lua
%{_datadir}/%{name}/lib/moses.lua
%{_datadir}/%{name}/lib/plugins_stats.lua
%{_datadir}/%{name}/lib/rescore_utility.lua
%dir %{_datadir}/%{name}/lib/decisiontree
%{_datadir}/%{name}/lib/decisiontree/*.lua
%dir %{_datadir}/%{name}/lib/nn
%{_datadir}/%{name}/lib/nn/*.lua
%dir %{_datadir}/%{name}/lib/optim
%{_datadir}/%{name}/lib/optim/*.lua
%dir %{_datadir}/%{name}/lib/paths
%{_datadir}/%{name}/lib/paths/init.lua
%dir %{_datadir}/%{name}/lib/rspamadm
%{_datadir}/%{name}/lib/rspamadm/*.lua
%dir %{_datadir}/%{name}/lib/torch
%{_datadir}/%{name}/lib/torch/*.lua
%dir %{_datadir}/%{name}/lua
%{_datadir}/%{name}/lua/*.lua
%dir %{_datadir}/%{name}/rules
%{_datadir}/%{name}/rules/*.lua
%dir %{_datadir}/%{name}/rules/regexp
%{_datadir}/%{name}/rules/regexp/*.lua
%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*
%attr(755,root,root) %{_libdir}/*.so
%{_mandir}/man1/rspamadm.1*
%{_mandir}/man1/rspamc.1*
%{_mandir}/man8/rspamd.8*

%changelog
* Wed May 15 2013 PLD Linux Team <feedback@pld-linux.org>
- For complete changelog see:	http://git.pld-linux.org/?p=packages/rspamd.git;a=log

