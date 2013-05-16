#
Summary:	Spam filter to replace spamassassin
Name:		rspamd
Version:	0.5.4
Release:	0.1
License:	BSD-like
Group:		Applications
Source0:	https://bitbucket.org/vstakhov/rspamd/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	b5f18a2098de9b6931a9d40c60c83fcd
Source1:	%{name}.tmpfiles
URL:		https://bitbucket.org/vstakhov/rspamd/wiki/Home
%if %{with initscript}
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
%endif
%if %{with systemd_service}
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun,postun):	systemd-units >= 38
Requires:	systemd-units >= 0.38
%endif
BuildRequires:	cmake
BuildRequires:	glib2-devel
BuildRequires:	gmime-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	lua-devel
BuildRequires:	pcre-devel
BuildRequires:	sqlite3-devel
#Provides:	group(foo)
#Provides:	user(foo)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# Executable provides rspamd_main, gmime and more
%define skip_post_check_so librspamd-mime.so.* librspamd-server.so.* librspamd-lua.so.*

%description
Rspamd is a complex spam filter that allows to estimate messages by
many rules, statistical data and custom services like URL black lists.
Each message is estimated by rspamd and got so called 'spam score'.
According to spam score and user's settings rspamd send recommended
action for this message to MTA. Rspamd has own unique features among
spam filters:

* event driven architecture allowing to process many messages at a
  time
* flexible syntax of rules allowing to write rules in lua language
* a lot of plugins and rules shipped with rspamd distribution
* highly optimized mail processing
* advanced statistic All these features allow rspamd to process 
  messages fast and make good results in spam filtering.

%prep
%setup -q

%build
%{__cmake} -DCMAKE_INSTALL_PREFIX=%{_prefix} .
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%if %{with initscript}
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}
%endif

install -d $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d
install %SOURCE1 $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/%{name}.conf

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
%pre
%groupadd -g xxx %{name}
%useradd -u xxx -d /var/lib/%{name} -g %{name} -c "XXX User" %{name}

%post

%preun

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi
%endif

%if %{with ldconfig}
%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig
%endif

%if %{with initscript}
%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%endif

%if %{with systemd_service}
%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_reload
%endif

%files
%defattr(644,root,root,755)
%doc ChangeLog README
%{_sysconfdir}/tmpfiles.d/rspamd.conf
%attr(755,root,root) %{_bindir}/rspamc
%attr(755,root,root) %{_bindir}/rspamc-0.5.4
%attr(755,root,root) %{_bindir}/rspamd
%attr(755,root,root) %{_bindir}/rspamd-0.5.4
#%attr(754,root,root) %{_prefix}/etc/rc.d/init.d/rspamd
%{_prefix}%{_sysconfdir}/rspamd.xml.sample
%{_prefix}%{_sysconfdir}/rspamd/2tld.inc
%{_prefix}%{_sysconfdir}/rspamd/2tld.inc.orig
%{_prefix}%{_sysconfdir}/rspamd/lua/regexp/drugs.lua
%{_prefix}%{_sysconfdir}/rspamd/lua/regexp/fraud.lua
%{_prefix}%{_sysconfdir}/rspamd/lua/regexp/headers.lua
%{_prefix}%{_sysconfdir}/rspamd/lua/regexp/lotto.lua
%{_prefix}%{_sysconfdir}/rspamd/lua/rspamd.classifiers.lua
%{_prefix}%{_sysconfdir}/rspamd/lua/rspamd.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/emails.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/forged_recipients.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/ip_score.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/maillist.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/multimap.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/once_received.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/phishing.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/ratelimit.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/received_rbl.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/trie.lua
%{_prefix}%{_sysconfdir}/rspamd/plugins/lua/whitelist.lua
%{_prefix}%{_sysconfdir}/rspamd/surbl-whitelist.inc
# %{_includedir}/rspamd/librspamdclient.h
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-cdb.so
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-cdb.so.0.5.4
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-json.so
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-json.so.0.5.4
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-lua.so
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-lua.so.0.5.4
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-mime.so
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-mime.so.0.5.4
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-server.so
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-server.so.0.5.4
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-util.so
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamd-util.so.0.5.4
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamdclient.so
%attr(755,root,root) %{_prefix}/lib/rspamd/librspamdclient.so.0.5.4
# %{_prefix}/lib/rspamd/librspamdclient_static.a
%{_mandir}/man1/rspamc.1*
%{_mandir}/man8/rspamd.8*

%if 0
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*
%attr(755,root,root) %{_bindir}/%{name}*
%{_datadir}/%{name}
%endif

# initscript and its config
%if %{with initscript}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%endif

%if %{with systemd_service}
%{systemdunitdir}/%{name}.service
%endif
%changelog
* Wed May 15 2013 PLD Linux Team <feedback@pld-linux.org>
- For complete changelog see: http://git.pld-linux.org/?p=packages/rspamd.git;a=log

