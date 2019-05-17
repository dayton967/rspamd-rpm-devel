Name:             rspamd
Version:          1.9.3
Release:          7%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0 and LGPLv2+ and LGPLv3 and BSD and MIT and CC0 and zlib
URL:              https://www.rspamd.com/
Source0:          https://github.com/vstakhov/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:          80-rspamd.preset
Source2:          rspamd.service
Source3:          rspamd.logrotate
Source4:          rspamd.sysusers
Source5:          rspamd.logrotate.systemd
Source6:          rspamd.init
Patch0:           rspamd-secure-ssl-ciphers.patch

BuildRequires:    cmake, fann-devel, file-devel, glib2-devel
BuildRequires:    libaio-devel, libevent-devel, libicu-devel, openssl-devel
BuildRequires:    pcre-devel, ragel
BuildRequires:    sqlite-devel, zlib-devel
%if 0%{?el6}
BuildRequires:    perl
Requires(post):   chkconfig
Requires(preun):  chkconfig, initscripts
Requires(postun): initscripts
%else
BuildRequires:    perl-Digest-MD5
BuildRequires:    gmime-devel
BuildRequires:    systemd
%{?systemd_requires}
%endif
%if (0%{?fedora} >=28 || 0%{?rhel} > 7)
%ifarch x86_64
BuildRequires:    hyperscan-devel
%endif
BuildRequires:    libnsl2-devel
%endif
%ifnarch ppc64le ppc
BuildRequires:    luajit-devel
%else
BuildRequires:    lua-devel
%endif
Requires(pre):    shadow-utils
Requires:         logrotate
Requires:         zlib

# Bundled dependencies
# TODO: Add explicit bundled lib versions
# TODO: Check for bundled js libs
# TODO: Double-check Provides
# aho-corasick: LGPL-3.0
Provides: bundled(aho-corasick)
# cdb: Public Domain
Provides: bundled(cdb) = 1.1.0
# lc-btrie: BSD-3-Clause
Provides: bundled(lc-btrie)
# libottery: CC0
Provides: bundled(libottery)
# librdns: BSD-2-Clause
Provides: bundled(librdns)
# libucl: BSD-2-Clause
Provides: bundled(libucl)
# moses: MIT
Provides: bundled(moses)
# mumhash: MIT
Provides: bundled(mumhash)
# ngx-http-parser: MIT
Provides: bundled(ngx-http-parser) = 2.2.0
# snowball: BSD-3-Clause
Provides: bundled(snowball)
# t1ha: Zlib
Provides: bundled(t1ha)
# torch: Apache-2.0 or BSD-3-Clause
Provides: bundled(torch)
# hiredis: BSD-3-Clause
Provides: bundled(hiredis) = 0.13.3
# lgpl: LGPL-2.1
Provides: bundled(lgpl)
# linenoise: BSD-2-Clause
Provides: bundled(linenoise) = 1.0
# lua-lpeg: MIT
Provides: bundled(lpeg) = 1.0
# lua-fun: MIT
Provides: bundled(lua-fun)
# perl-Mozilla-PublicSuffix: MIT
Provides: bundled(perl-Mozilla-PublicSuffix)
# uthash: BSD
Provides: bundled(uthash) = 1.9.8
# xxhash: BSD
Provides: bundled(xxhash)
# zstd: BSD
Provides: bundled(zstd) = 1.3.1

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%setup -q
%patch0 -p1
rm -rf centos
rm -rf debian
rm -rf docker
rm -rf freebsd

%build
# TODO: Investigate, do we want DEBIAN_BUILD=1? Any other improvements?
%cmake \
  -DCONFDIR=%{_sysconfdir}/%{name} \
  -DMANDIR=%{_mandir} \
  -DDBDIR=%{_sharedstatedir}/%{name} \
  -DRUNDIR=%{_localstatedir}/run \
  -DWANT_SYSTEMD_UNITS=ON \
  -DSYSTEMDDIR=%{_unitdir} \
%ifarch ppc64le ppc64
  -DENABLE_LUAJIT=OFF \
  -DENABLE_TORCH=OFF \
%endif
  -DENABLE_HIREDIS=ON \
  -DENABLE_FANN=ON \
%if (0%{?fedora} >= 28 || 0%{?rhel} > 7)
  -DENABLE_HYPERSCAN=ON \
  -DHYPERSCAN_ROOT_DIR=/opt/hyperscan \
%endif
  -DLOGDIR=%{_localstatedir}/log/%{name} \
  -DPLUGINSDIR=%{_datadir}/%{name} \
  -DLIBDIR=%{_libdir}/%{name}/ \
  -DNO_SHARED=ON \
  -DDEBIAN_BUILD=1 \
  -DRSPAMD_USER=%{name} \
  -DRSPAMD_GROUP=%{name}
%make_build

%check
# TODO: Run Tests

%pre
%sysusers_create_package %{name} %{SOURCE4}

%install
%{make_install} DESTDIR=%{buildroot} INSTALLDIRS=vendor
rm %{buildroot}%{_unitdir}/rspamd.service
%{__install} -dpm 0755 %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -dpm 0755 %{buildroot}%{_sharedstatedir}/%{name}
%{__install} -Ddpm 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
%{__install} -Ddpm 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/
%if 0%{?el6}
%{__install} -p -D -m 0755 %{SOURCE6} %{buildroot}%{_initrddir}/%{name}
%{__install} -d -p -m 0755 %{buildroot}%{_localstatedir}/run/rspamd
%else
%{__install} -Dpm 0644 %{SOURCE1} %{buildroot}%{_libdir}/systemd/system-preset/80-rspamd.preset
%{__install} -Dpm 0644 %{SOURCE2} %{buildroot}%{_unitdir}/rspamd.service
%endif
%if 0%{?el6}
%{__install} -Dpm 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/rspamd
%else
%{__install} -Dpm 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/rspamd
%endif
%{__install} -Dpm 0644 LICENSE.md %{buildroot}%{_docdir}/licenses/LICENSE.md

%post
%systemd_post rspamd.service

%preun
%systemd_preun rspamd.service

%postun
%systemd_postun_with_restart rspamd.service

%files
%license %{_docdir}/licenses/LICENSE.md
%{_bindir}/rspamadm
%{_bindir}/rspamc
%{_bindir}/rspamd
%{_bindir}/rspamd_stats

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/effective_tld_names.dat
%{_datadir}/%{name}/*.lua

%if (0%{?fedora} >=28 || 0%{?rhel} > 7)
%dir %{_datadir}/%{name}/{elastic,languages}
%{_datadir}/%{name}/{elastic,languages}/*.json
%else
%dir %{_datadir}/%{name}/elastic
%dir %{_datadir}/%{name}/languages
%{_datadir}/%{name}/elastic/*.json
%{_datadir}/%{name}/languages/*.json
%endif

%if (0%{?fedora} >=28 || 0%{?rhel} > 7)
%dir %{_datadir}/%{name}/{lua,lib,rules}
%{_datadir}/%{name}/{lua,lib,rules}/*.lua
%else
%dir %{_datadir}/%{name}/rules
%{_datadir}/%{name}/rules/*.lua
%endif

%if (0%{?fedora} >=28 || 0%{?rhel} > 7)
%dir %{_datadir}/%{name}/lualib/{decisiontree,nn,optim,paths,rspamadm,torch}
%{_datadir}/%{name}/lualib/{decisiontree,nn,optim,paths,rspamadm,torch,lua_ffi,lua_scanners}/*.lua
%{_datadir}/%{name}/lualib/*.lua
%else
%ifnarch ppc64 ppc64le
%dir %{_datadir}/%{name}/lualib/decisiontree
%dir %{_datadir}/%{name}/lualib/nn
%dir %{_datadir}/%{name}/lualib/optim
%dir %{_datadir}/%{name}/lualib/paths
%dir %{_datadir}/%{name}/lualib/torch
%{_datadir}/%{name}/lualib/decisiontree/*.lua
%{_datadir}/%{name}/lualib/nn/*.lua
%{_datadir}/%{name}/lualib/optim/*.lua
%{_datadir}/%{name}/lualib/paths/*.lua
%{_datadir}/%{name}/lualib/torch/*.lua
%endif
%dir %{_datadir}/%{name}/lualib/rspamadm
%{_datadir}/%{name}/lualib/rspamadm/*.lua
%{_datadir}/%{name}/lualib/lua_ffi/*.lua
%{_datadir}/%{name}/lualib/lua_scanners/*.lua
%{_datadir}/%{name}/lualib/*.lua
%endif

%{_datadir}/%{name}/languages/stop_words

%dir %{_datadir}/%{name}/rules/regexp
%{_datadir}/%{name}/rules/regexp/*.lua

%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%if 0%{?suse_version} || 0%{?fedora} || 0%{?el7}
%{_unitdir}/%{name}.service
%{_presetdir}/80-rspamd.preset
%endif
%if 0%{?el6}
%{_initrddir}/%{name}
%dir %{_localstatedir}/run/rspamd
%endif
%attr(-, rspamd, rspamd) %dir %{_localstatedir}/log/%{name}
%{_mandir}/man1/rspamadm.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man8/rspamd.*
%attr(-, rspamd, rspamd) %dir %{_sharedstatedir}/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/rspamd
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/*.inc

%if (0%{?fedora} >=28 || 0%{?rhel} > 7)
%dir %{_sysconfdir}/%{name}/{local,modules,override,scores}.d
%config(noreplace) %{_sysconfdir}/%{name}/{modules,scores}.d/*
%else
%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/modules.d
%dir %{_sysconfdir}/%{name}/override.d
%dir %{_sysconfdir}/%{name}/scores.d
%config(noreplace) %{_sysconfdir}/%{name}/modules.d/*
%config(noreplace) %{_sysconfdir}/%{name}/scores.d/*
%endif


