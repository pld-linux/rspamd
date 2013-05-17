#
Summary:	Spam filter to replace spamassassin
Name:		rspamd
Version:	0.5.4
Release:	0.3
License:	BSD-like
Group:		Applications
Source0:	https://bitbucket.org/vstakhov/rspamd/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	b5f18a2098de9b6931a9d40c60c83fcd
Source1:	%{name}.tmpfiles
Source2:    %{name}.init
Source3:    %{name}.sysconfig
URL:		https://bitbucket.org/vstakhov/rspamd/wiki/Home
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRequires:	cmake
BuildRequires:	glib2-devel
BuildRequires:	gmime-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	lua-devel
BuildRequires:	pcre-devel
BuildRequires:	sqlite3-devel
Provides:	group(rspamd)
Provides:	user(rspamd)
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
%{__cmake} -DCMAKE_INSTALL_PREFIX=%{_prefix} -DETC_PREFIX=%{_sysconfdir} -DLIBDIR=%{_libdir} .
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}

install -d $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d
install %SOURCE1 $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/%{name}.conf
install %SOURCE2 $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %SOURCE3 $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT%{_sysconfdir}/rspamd/2tld.inc{.orig,}

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
%doc ChangeLog README
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{_sysconfdir}/tmpfiles.d/rspamd.conf
%attr(755,root,root) %{_bindir}/rspam*
%{_sysconfdir}/rspamd.xml.sample
%dir /etc/rspamd
%{_sysconfdir}/rspamd/2tld.inc
%dir /etc/rspamd/lua
%{_sysconfdir}/rspamd/lua/rspamd.classifiers.lua
%{_sysconfdir}/rspamd/lua/rspamd.lua
%dir /etc/rspamd/lua/regexp
%{_sysconfdir}/rspamd/lua/regexp/drugs.lua
%{_sysconfdir}/rspamd/lua/regexp/fraud.lua
%{_sysconfdir}/rspamd/lua/regexp/headers.lua
%{_sysconfdir}/rspamd/lua/regexp/lotto.lua
%dir /etc/rspamd/plugins
%dir /etc/rspamd/plugins/lua
%{_sysconfdir}/rspamd/plugins/lua/emails.lua
%{_sysconfdir}/rspamd/plugins/lua/forged_recipients.lua
%{_sysconfdir}/rspamd/plugins/lua/ip_score.lua
%{_sysconfdir}/rspamd/plugins/lua/maillist.lua
%{_sysconfdir}/rspamd/plugins/lua/multimap.lua
%{_sysconfdir}/rspamd/plugins/lua/once_received.lua
%{_sysconfdir}/rspamd/plugins/lua/phishing.lua
%{_sysconfdir}/rspamd/plugins/lua/ratelimit.lua
%{_sysconfdir}/rspamd/plugins/lua/received_rbl.lua
%{_sysconfdir}/rspamd/plugins/lua/trie.lua
%{_sysconfdir}/rspamd/plugins/lua/whitelist.lua
%{_sysconfdir}/rspamd/surbl-whitelist.inc
# %{_includedir}/rspamd/librspamdclient.h
%attr(755,root,root) %{_libdir}/*.so
%attr(755,root,root) %{_libdir}/*.so.%{version}
# %{_prefix}/lib/rspamd/librspamdclient_static.a
%{_mandir}/man1/rspamc.1*
%{_mandir}/man8/rspamd.8*

%changelog
* Wed May 15 2013 PLD Linux Team <feedback@pld-linux.org>
- For complete changelog see: http://git.pld-linux.org/?p=packages/rspamd.git;a=log

