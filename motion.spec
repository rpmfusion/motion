%global _lto_cflags %{nil}

Name:           motion
Version:        4.7.1
Release:        4%{?dist}
Summary:        A motion detection system

License:        GPL-2.0-or-later
URL:            https://motion-project.github.io/
Source0:        https://github.com/Motion-Project/motion/archive/release-%{version}.tar.gz#/%{name}-release-%{version}.tar.gz
Source1:        motion.service
Source2:        motion.tmpfiles
Source3:        motion.sysusers

BuildRequires:  libjpeg-devel
BuildRequires:  zlib-devel
BuildRequires:  ffmpeg-devel
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  systemd-units
BuildRequires:  libmicrohttpd-devel
BuildRequires:  libwebp-devel
BuildRequires:  gettext-devel
BuildRequires:  systemd-rpm-macros
%{?sysusers_requires_compat}
# libmysqlclient-dev (>= 5.5.17-4),
# libpq-dev,
# libsdl1.2-dev,
# libv4l-dev,

#This requires comes from the startup script, it will be there until motion supports libv4l calls in the code
Requires: libv4l
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description
Motion is a software motion detector. It grabs images from video4linux devices
and/or from webcams (such as the axis network cameras). Motion is the perfect
tool for keeping an eye on your property keeping only those images that are
interesting. Motion is strictly command line driven and can run as a daemon
with a rather small footprint. This version is built with ffmpeg support but
without MySQL and PostgreSQL support.

%prep
%autosetup -p1 -n %{name}-release-%{version}
autoreconf -fiv

%build
export AR=%{_bindir}/gcc-ar
export RANLIB=%{_bindir}/gcc-ranlib
export NM=%{_bindir}/gcc-nm
%configure \
    --without-optimizecpu \
    --with-ffmpeg \
    --without-mysql \
    --without-pgsql \
    --with-webp

%make_build V=1

%install
%make_install

#We rename the configuration files
mv %{buildroot}%{_sysconfdir}/%{name}/motion-dist.conf %{buildroot}%{_sysconfdir}/%{name}/motion.conf
mv %{buildroot}%{_sysconfdir}/%{name}/camera1-dist.conf %{buildroot}%{_sysconfdir}/%{name}/camera1.conf
mv %{buildroot}%{_sysconfdir}/%{name}/camera2-dist.conf %{buildroot}%{_sysconfdir}/%{name}/camera2.conf
mv %{buildroot}%{_sysconfdir}/%{name}/camera3-dist.conf %{buildroot}%{_sysconfdir}/%{name}/camera3.conf
mv %{buildroot}%{_sysconfdir}/%{name}/camera4-dist.conf %{buildroot}%{_sysconfdir}/%{name}/camera4.conf
#Delete doc directory
rm -rf %{buildroot}%{_datadir}/doc
#Fix path
sed -i 's|/usr/etc|/etc|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We change the PID file path to match the one in the startup script
sed -i 's|; pid_file value|pid_file /var/run/motion.pid|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We set the log file and target directory - logging is for 3.3 branch
sed -i 's|; log_file value|log_file /var/log/motion.log|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|; target_dir value|target_dir /var/motion|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We install our startup script
install -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
#We install tmpfiles configuration
install -D -m 0755 %{SOURCE2} %{buildroot}%{_tmpfilesdir}/%{name}.conf
#Setup user and group
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysusersdir}/%{name}.conf
#We remove versioned docs
rm -rf %{buildroot}%{_docdir}/%{name}-%{version}

%find_lang %{name}

%pre
%sysusers_create_compat %{SOURCE3}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files -f %{name}.lang
%doc doc/CHANGELOG doc/CREDITS README.md doc/motion_guide.html doc/*.jpg doc/*.png
%license LICENSE
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf

%changelog
* Mon Feb 02 2026 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 4.7.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_44_Mass_Rebuild

* Wed Nov 05 2025 Leigh Scott <leigh123linux@gmail.com> - 4.7.1-3
- Rebuild for ffmpeg-8.0

* Sun Oct 12 2025 Sérgio Basto <sergio@serjux.com> - 4.7.1-2
- Use sysusers_create_compat

* Tue Oct 07 2025 Leigh Scott <leigh123linux@gmail.com> - 4.7.1-1
- Update to 4.7.1

* Sun Jul 27 2025 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 4.7.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Tue Jan 28 2025 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 4.7.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Mon Oct 14 2024 Leigh Scott <leigh123linux@gmail.com> - 4.7.0-2
- Rebuild for ffmpeg-7

* Tue Sep 17 2024 Leigh Scott <leigh123linux@gmail.com> - 4.7.0-1
- Update to 4.7.0

* Fri Aug 02 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 4.6.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Sun Feb 04 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 4.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Mon Nov 13 2023 Vasiliy N. Glazov <vascom2@gmail.com> - 4.6.0-1
- Update to 4.6.0

* Fri Aug 04 2023 Vasiliy N. Glazov <vascom2@gmail.com> - 4.5.1-4
- Fix Build with webp

* Wed Aug 02 2023 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 4.5.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Wed Mar 01 2023 Leigh Scott <leigh123linux@gmail.com> - 4.5.1-2
- Rebuild for new ffmpeg

* Tue Dec 20 2022 Vasiliy N. Glazov <vascom2@gmail.com> - 4.5.1-1
- Update to 4.5.1

* Sun Nov 20 2022 Sérgio Basto <sergio@serjux.com> - 4.5.0-1
- Update motion to 4.5.0

* Sun Aug 07 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 4.4.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Wed Feb 09 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 4.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Fri Nov 12 2021 Leigh Scott <leigh123linux@gmail.com> - 4.4.0-2
- Rebuilt for new ffmpeg snapshot

* Mon Oct 25 2021 Vasiliy N. Glazov <vascom2@gmail.com> - 4.4.0-1
- Update to 4.4.0

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 4.3.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed Feb 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 4.3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan  1 2021 Leigh Scott <leigh123linux@gmail.com> - 4.3.2-2
- Rebuilt for new ffmpeg snapshot

* Mon Oct 26 2020 Vasiliy N. Glazov <vascom2@gmail.com> - 4.3.2-1
- Update to 4.3.2

* Tue Aug 18 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 4.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Apr 13 2020 Vasiliy N. Glazov <vascom2@gmail.com> - 4.3.1-1
- Update to 4.3.1

* Sat Feb 22 2020 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 4.3.0-3
- Rebuild for ffmpeg-4.3 git

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 4.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Tue Jan 14 2020 Vasiliy N. Glazov <vascom2@gmail.com> - 4.3.0-1
- Update to 4.3.0

* Thu Nov 07 2019 Vasiliy N. Glazov <vascom2@gmail.com> - 4.2.2-4
- Enable LTO

* Wed Aug 07 2019 Leigh Scott <leigh123linux@gmail.com> - 4.2.2-3
- Rebuild for new ffmpeg version

* Fri Mar 22 2019 Vasiliy N. Glazov <vascom2@gmail.com> - 4.2.2-2
- Update to 4.2.2
- Enable Webp Support

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 4.1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Nov 13 2018 Antonio Trande <sagitter@fedoraproject.org> - 4.1.1-6
- Rebuild for ffmpeg-3.4.5 on el7

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 4.1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Mar 08 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 4.1.1-4
- Rebuilt for new ffmpeg snapshot

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 4.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 18 2018 Leigh Scott <leigh123linux@googlemail.com> - 4.1.1-2
- Rebuilt for ffmpeg-3.5 git

* Wed Jan 10 2018 Leigh Scott <leigh123linux@googlemail.com> - 4.1.1-1
- Update to 4.1.1 release
- Fix perms on motion.service (rfbz 4753)

* Fri Nov 24 2017 Leigh Scott <leigh123linux@googlemail.com> - 4.1-1
- Update to 4.1 release

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 4.0.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed May 17 2017 Leigh Scott <leigh123linux@googlemail.com> - 4.0.1-5
- Rebuild for ffmpeg update

* Sun May 07 2017 Sérgio Basto <sergio@serjux.com> - 4.0.1-4
- Patch from rfbz#4321 applied

* Sat Apr 29 2017 Leigh Scott <leigh123linux@googlemail.com> - 4.0.1-3
- Rebuild for ffmpeg update

* Mon Mar 20 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Mar 13 2017 Leigh Scott <leigh123linux@googlemail.com> - 4.0.1-1
- Update to 4.0.1 release
- Clean up spec file

* Sat Jul 30 2016 Julian Sikorski <belegdol@fedoraproject.org> - 3.3.0.trunkREV561-3
- Rebuilt for ffmpeg-3.1.1

* Sun Jul 17 2016 Leigh Scott <leigh123linux@googlemail.com> - 3.3.0.trunkREV561-2
- patch for ffmpeg-3

* Wed Nov 18 2015 Sérgio Basto <sergio@serjux.com> - 3.3.0.trunkREV561-1
- Update motion to runkREV561 .
- Use only ffmpeg-devel, drop ffmpeg-compat-devel.
- Use autoreconf to generate ./configure and patch configure with real version.
- Some spec clean ups.
- Drop upstreamed patch.

* Sun Dec 14 2014 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0.trunkREV557-10
- restore lost changes (should fix #3460):
  * Sat Jan 11 2014 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0-trunkREV557.9
  - use the same sources and BRs as F-19 (trunkREV557.11) branch (fixes #3106)
  - adjust for UnversionedDocdirs

* Sat Oct 11 2014 Sérgio Basto <sergio@serjux.com> - 3.3.0.trunkREV557-9
- Rebuild for new gcc https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild
- Change naming, NamingGuideline
  http://fedoraproject.org/wiki/Packaging:NamingGuidelines#Pre-Release_packages,
  since it is a forever pre-release. I adopt name version with pre-release tag, %{next_version}.trunkREV557
  The motivation: rpmdev-bumpspec wasn't working correctly

* Sat Apr 20 2013 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0-trunkREV557.8
- migrate from running as root to running as motion:video (fixes #1935)
- don't ship INSTALL file

* Fri Apr 19 2013 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0-trunkREV557.7
- re-introduce ffmpeg-compat-devel

* Fri Apr 19 2013 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0-trunkREV557.6
- drop changelog entries before 2012 from .spec; dates were wrong and build failed
- drop changelog entries before 2012 from .spec; dates were wrong and build failed

* Fri Apr 19 2013 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0-trunkREV557.5
- bump again; I hate CVS

* Fri Apr 19 2013 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0-trunkREV557.4
- add missing unit file and bump rel

* Fri Apr 19 2013 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0-trunkREV557.3
- migrate to systemd unit file

* Fri Apr 19 2013 Tomasz Torcz <ttorcz@fedoraproject.org> - 3.3.0-trunkREV557.2
 - synchronize with F-18 version:
   - patches for ARM compilation and newest ffmpeg
     (this undoes ffmpeg-compat support)
   - logrotate fixes

* Wed Mar 20 2013 Nicolas Chauvet <kwizart@gmail.com> - 3.3.0-trunkREV534.7
- Move to ffmpeg-compat support
- Add sqlite3

* Sun Mar 03 2013 Nicolas Chauvet <kwizart@gmail.com> - 3.3.0-trunkREV534.6
- Mass rebuilt for Fedora 19 Features

* Wed Jan 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 3.3.0-trunkREV534.5
- Rebuilt for ffmpeg

* Sat Nov 24 2012 Nicolas Chauvet <kwizart@gmail.com> - 3.3.0-trunkREV534.4
- Rebuilt for FFmpeg 1.0

* Tue Jun 26 2012 Nicolas Chauvet <kwizart@gmail.com> - 3.3.0-trunkREV534.3
- Rebuilt for FFmpeg

* Tue Feb 28 2012 Nicolas Chauvet <kwizart@gmail.com> - 3.3.0-trunkREV534.2
- Rebuilt for x264/FFmpeg

* Wed Jan 25 2012 Nicolas Chauvet <kwizart@gmail.com> - 3.3.0-trunkREV534.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

