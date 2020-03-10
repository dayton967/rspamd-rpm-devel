Name:             rspamd
Version:          2.3
Release:          4%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0 and LGPLv2+ and LGPLv3 and BSD and MIT and CC0 and zlib
URL:              https://www.rspamd.com/
Source0:          https://github.com/rspamd/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:          80-rspamd.preset
Source2:          rspamd.service
Source3:          rspamd.logrotate
Source4:          rspamd.sysusers
Patch0:           rspamd-secure-ssl-ciphers.patch
Patch1:           rspamd-replxx.patch

%if (0%{?rhel} == 7)
BuildRequires:    cmake3
%else
BuildRequires:    cmake
%endif
BuildRequires:    file-devel >= 2.28
BuildRequires:    glib2-devel
BuildRequires:    gmime-devel
%if (0%{?fedora} >=28 || 0%{?rhel} >= 7)
BuildRequires:    openblas-devel
Requires:         openblas
%endif
%if (0%{?fedora} >=28 || 0%{?rhel} > 7)
%ifarch x86_64
BuildRequires:    hyperscan-devel
%endif
%endif
BuildRequires:    libicu-devel
%ifnarch ppc64le ppc64 aarch64
BuildRequires:    pkgconfig(luajit)
%else
%ifarch aarch64
%if (0%{?fedora} >=28 || 0%{?rhel} > 7)
BuildRequires:    pkgconfig(luajit)
%else
BuildRequires:    pkgconfig(lua)
%endif
%else
BuildRequires:    pkgconfig(lua)
%endif
%endif
BuildRequires:    openssl-devel
BuildRequires:    pcre-devel
BuildRequires:    perl
BuildRequires:    perl-Digest-MD5
BuildRequires:    ragel
BuildRequires:    systemd
%{?systemd_requires}
Requires(pre):    shadow-utils
Requires:         logrotate
BuildRequires:    pkgconfig(zlib)
Requires:         pkgconfig(zlib)
BuildRequires:    pkgconfig(sqlite3)
Requires:         pkgconfig(sqlite3)
BuildRequires:    pkgconfig(libsodium) >= 1.0.0
Requires:         pkgconfig(libsodium) >= 1.0.0

# Bundled dependencies
# TODO: Add explicit bundled lib versions
# TODO: Check for bundled js libs
# TODO: Double-check Provides
# aho-corasick: LGPL-3.0
Provides: bundled(aho-corasick)
# cdb: Public Domain / CCO
Provides: bundled(cdb) = 1.1.0
# fpconv: Boost Software License - Version 1.0
Provides: bundled(fpconv)
# hiredis: BSD-3-Clause
Provides: bundled(hiredis) = 0.13.3
# kann: MIT
Provides: bundle(kann) = r536
# lc-btrie: BSD-3-Clause
Provides: bundled(lc-btrie)
# libev: BSD-2-Clause
Provides: bundled(libev) = 4.25
# libottery: CC0
Provides: bundled(libottery)
# librdns: BSD-2-Clause
Provides: bundled(librdns)
# libucl: BSD-2-Clause
Provides: bundled(libucl)
# lua-argparse: MIT
Provides: bundled(lua-argparse)
# lua-bit: MIT
Provides: bundled(lua-bit) = 1.0.2
# lua-fun: MIT
Provides: bundled(lua-fun)
# lua-lpeg: MIT
Provides: bundled(lua-lpeg) = 1.0
# lua-lupa: MIT
Provides: bundled(lua-lupa)
# lua-tablespace: MIT
Provides: bundled(lua-tablespace) = 2.0.0
# mumhash: MIT
Provides: bundled(7mumhash)
# ngx-http-parser: MIT
Provides: bundled(ngx-http-parser) = 2.2.0
# perl-Mozilla-PublicSuffix: MIT
Provides: bundled(perl-Mozilla-PublicSuffix)
# replxx: BSD-2-Clause
Provides: bundled(replxx) = 0.0.2
# snowball: BSD-3-Clause
Provides: bundled(snowball)
# t1ha: Zlib
Provides: bundled(t1ha)
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
%patch1 -p1
rm -rf centos
rm -rf debian
rm -rf docker
rm -rf freebsd

%build
# TODO: Investigate, do we want DEBIAN_BUILD=1? Any other improvements?
%if (0%{?rhel} == 7)
%cmake3 \
%else
%cmake \
%endif
  -DCONFDIR=%{_sysconfdir}/%{name} \
  -DMANDIR=%{_mandir} \
  -DDBDIR=%{_sharedstatedir}/%{name} \
  -DRUNDIR=%{_localstatedir}/run \
  -DWANT_SYSTEMD_UNITS=ON \
  -DSYSTEMDDIR=%{_unitdir} \
%ifarch ppc64le ppc64
  -DENABLE_LUAJIT=OFF \
%endif
  -DENABLE_HIREDIS=ON \
%ifarch x86_64
%if (0%{?fedora} >= 28 || 0%{?rhel} > 7)
  -DENABLE_HYPERSCAN=ON \
  -DHYPERSCAN_ROOT_DIR=/opt/hyperscan \
%endif
%if (0%{?rhel} == 7)
  -DCMAKE_C_OPT_FLAGS="-m32 -maes" \
%endif
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
install -dpm 0755 %{buildroot}%{_localstatedir}/log/%{name}
install -dpm 0755 %{buildroot}%{_sharedstatedir}/%{name}
install -Ddpm 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
install -Ddpm 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_libdir}/systemd/system-preset/80-rspamd.preset
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_unitdir}/rspamd.service
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/rspamd
install -Dpm 0644 LICENSE.md %{buildroot}%{_docdir}/licenses/LICENSE.md

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

%dir %{_datadir}/%{name}/elastic
%dir %{_datadir}/%{name}/languages
%dir %{_datadir}/%{name}/lualib
%dir %{_datadir}/%{name}/lualib/lua_content
%dir %{_datadir}/%{name}/lualib/lua_ffi
%dir %{_datadir}/%{name}/lualib/lua_magic
%dir %{_datadir}/%{name}/lualib/lua_scanners
%dir %{_datadir}/%{name}/lualib/lua_selectors
%dir %{_datadir}/%{name}/lualib/rspamadm
%dir %{_datadir}/%{name}/rules
%dir %{_datadir}/%{name}/rules/regexp
%dir %{_datadir}/%{name}/www

%{_datadir}/%{name}/elastic/*.json
%{_datadir}/%{name}/languages/*.json
%{_datadir}/%{name}/languages/stop_words
%{_datadir}/%{name}/lualib/*.lua
%{_datadir}/%{name}/lualib/lua_content/*.lua
%{_datadir}/%{name}/lualib/lua_ffi/*.lua
%{_datadir}/%{name}/lualib/lua_magic/*.lua
%{_datadir}/%{name}/lualib/lua_scanners/*.lua
%{_datadir}/%{name}/lualib/lua_selectors/*.lua
%{_datadir}/%{name}/lualib/rspamadm/*.lua
%{_datadir}/%{name}/rules/*.lua
%{_datadir}/%{name}/rules/regexp/*.lua
%{_datadir}/%{name}/www/*


%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%{_libdir}/systemd/system-preset/80-rspamd.preset
%attr(-, rspamd, rspamd) %dir %{_localstatedir}/log/%{name}
%{_mandir}/man1/rspamadm.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man8/rspamd.*
%attr(-, rspamd, rspamd) %dir %{_sharedstatedir}/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/rspamd
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/*.inc

%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/modules.d
%dir %{_sysconfdir}/%{name}/override.d
%dir %{_sysconfdir}/%{name}/scores.d
%dir %{_sysconfdir}/%{name}/maps.d
%config(noreplace) %{_sysconfdir}/%{name}/modules.d/*
%config(noreplace) %{_sysconfdir}/%{name}/scores.d/*
%config(noreplace) %{_sysconfdir}/%{name}/maps.d/*

%{_unitdir}/rspamd.service

%changelog
* Tue Mar 10 2020 Jason Robertson <copr@dden.ca> - 2.3-4
- Fixed bug in the contributed replxx code to allow compiling on Fedora 32+
- Readded the crypto patch

* Fri Feb 21 2020 Jason Robertson <copr@dden.ca> - 2.3-3
- Updated to 2.3 - https://github.com/rspamd/rspamd/releases/tag/2.3
- Version 2.2 was skipped as due to working out a bug with libottery for RHEL7 x86_64
- Removed crypto patch, as this prevented compilation, may re-add this in the future.
- New files added to rspamd - %{_datadir}/%{name}/lualib/lua_content/*.lua

* Wed Oct 30 2019 Jason Robertson <copr@dden.ca> - 2.1-12
- Updated to 2.1 - https://github.com/rspamd/rspamd/releases/tag/2.1

* Mon Oct 21 2019 Jason Robertson <copr@dden.ca> - 2.0-12
- Updated to 2.0 - https://github.com/rspamd/rspamd/releases/tag/2.0
- Added support for Libsodium
- Added support from openblas
- Removed Requirement for FANN, this was removed in rspamd 2.0
- Cleaned up the Bundled libraries list
- Cleanup the Requirements and removed unused requirements.

* Mon May 27 2019 Jason Robertson <copr@dden.ca> - 1.9.4-3
- Cleanup accounts when uninstalled
- Cleanup directories that do not get removed

* Sat May 25 2019 Jason Robertson <copr@dden.ca> - 1.9.4-2
- Updated for 1.9.4 release

* Fri May 17 2019 Jason Robertson <copr@dden.ca> - 1.9.3-5
- Updated for 1.9.3 release
- Added fedora ppc64le, these have had luajit and torch disabled.

* Sat May  4 2019 Jason Robertson <copr@dden.ca> - 1.9.2-1
- Updated for 1.9.2 release
- Make hyperscan-devel to only be for Fedora 28+ and RHEL8+
- Forked from https://copr.fedorainfracloud.org/coprs/lorbus/rspamd/

* Mon Oct 22 2018 Evan Klitzke <evan@eklitzke.org> - 1.8.1-1
- Update for 1.8.1 release
- Build now uses upstream ragel, not ragel-compat

* Fri May 18 2018 patrick@pichon.me - 1.7.4
- Updated for 1.7.4 release
- Make hyperscan-devel only for x86_64 architecure for which the package exist

* Sun Mar 25 2018 evan@eklitzke.org - 1.7.1-1
- Updated for 1.7.1 release

* Wed Feb 21 2018 Christian Glombek <christian.glombek@rwth-aachen.de> - 1.6.6-1
- RPM packaging for Rspamd in Fedora
- Add patch to use OpenSSL system profile cipher list
- Add license information and provides declarations for bundled libraries
- Forked from https://raw.githubusercontent.com/vstakhov/rspamd/b1717aafa379b007a093f16358acaf4b44fc03e2/centos/rspamd.spec

