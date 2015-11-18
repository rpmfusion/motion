
# TODO:
#  - /run/motion can be managed with RuntimeDirectory=motion in motion.service,
#    instead of tmpfiles snippet
#
# Motion seems pretty dead upstream.  In the meantime, this is most "alive" fork:
# https://github.com/sackmotion/motion
# It can be useful as a source to steal a patch or two.
#
# Mageia uses Mr-Dave fork: https://github.com/Mr-Dave/motion
# http://ftp.uni-erlangen.de/mirrors/Mageia/distrib/cauldron/SRPMS/core/release/motion-3.4.0-0.20151003git.1.mga6.src.rpm
#
# Notes from previous packages, Steven Moix:
# v+
# the version shipped in Fedora Fedora is the SVN trunk (future 3.3.0 version).
# From an SVN export in a "motion-3.3.0" directory here is
# what I usually do to create the new source package for Fedora:
# svn export http://www.lavrsen.dk/svn/motion/trunk/ motion-3.3.0
# tar -pczf motion-3.3.0.tar.gz motion-3.3.0/
#v-

%global nextver 3.3.0
Name:           motion
Version:        %{nextver}.trunkREV561
Release:        1%{?dist}
Summary:        A motion detection system

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://www.lavrsen.dk/twiki/bin/view/Motion/WebHome
Source0:        http://prdownloads.sourceforge.net/%{name}/%{name}-%{nextver}.tar.gz
Source1:        motion.service
Source2:        motion.tmpfiles
Patch1:         motion-0002-there-is-no-bin-service-in-Fedora-use-systemctl.patch
Patch2:         motion-version.patch

BuildRequires:  libjpeg-devel zlib-devel ffmpeg-devel
Buildrequires:  pkgconfig(sqlite3)
BuildRequires:  autoconf automake libtool
BuildRequires:  systemd-units
#This requires comes from the startup script, it will be there until motion supports libv4l calls in the code
Requires: libv4l
Requires(pre):    shadow-utils
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
%setup -q -n %{name}-%{nextver}
%patch1 -p1
autoreconf
%patch2 -p1 -b .version

%build
#export PKG_CONFIG_LIBDIR="%{_libdir}/ffmpeg-compat/pkgconfig"
%configure --sysconfdir=%{_sysconfdir}/%{name} \
    --without-optimizecpu --with-ffmpeg --without-mysql --without-pgsql

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
#Rename docdir
mv %{buildroot}/%{_docdir}/%{name}-%{nextver} %{buildroot}/%{_docdir}/%{name}
#We rename the configuration file
mv %{buildroot}%{_sysconfdir}/%{name}/motion-dist.conf %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We move the logrotate configuration
mkdir %{buildroot}%{_sysconfdir}/logrotate.d
mv %{_builddir}/%{name}-%{nextver}/motion.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/motion
#We run as motion:video user, reflect that in logrotate config
sed -i 's|create 0600 root root|create 0600 motion video|g' %{buildroot}%{_sysconfdir}/logrotate.d/motion
#We change the PID file path to match the one in the startup script
sed -i 's|/var/run/motion/motion.pid|/var/run/motion.pid|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We remove SQL directives in the configuration file, as we don't use them
sed -i 's|sql_log_image|; sql_log_image|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|sql_log_snapshot|; sql_log_snapshot|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|sql_log_mpeg|; sql_log_mpeg|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|sql_log_timelapse|; sql_log_timelapse|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|sql_query|; sql_query|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We set the log file and target directory - logging is for 3.3 branch
sed -i 's|;logfile /tmp/motion.log|logfile /var/log/motion.log|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|target_dir /usr/local/apache2/htdocs/cam1|target_dir /var/motion|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We install our startup script
install -D -m 0755 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
#We install tmpfiles configuration
install -D -m 0755 %{SOURCE2} %{buildroot}%{_tmpfilesdir}/%{name}.conf

%pre
getent passwd motion >/dev/null || \
    useradd -r -g video -d /run/motion -s /sbin/nologin \
    -c "motion detection system" motion
exit 0

%post
/usr/bin/systemd-tmpfiles --create %{_tmpfilesdir}/%{name}.conf
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%triggerun -- motion <  3.3.0-trunkREV557.8
# we never shipped /var/motion directory, but it was set as
# default target_dir in config file. Be nice to admin and migrate
# ownership at the same time as we switch to running as user
find /var/motion -user root -group root -exec chown motion:video '{}' ';'

%clean
rm -rf %{buildroot}

%files
#Permissions are bogus upstream, we need to be sure to set them here
%defattr (-,root,root,-)
%dir %{_sysconfdir}/%{name}
%dir %{_datadir}/%{name}-%{nextver}
%dir %{_datadir}/%{name}-%{nextver}/examples
%doc CHANGELOG COPYING CREDITS README motion_guide.html INSTALL
%attr(0644,root,root) %{_datadir}/%{name}-%{nextver}/examples/motion-dist.conf
%attr(0755,root,root) %{_datadir}/%{name}-%{nextver}/examples/motion.init-Debian
%attr(0755,root,root) %{_datadir}/%{name}-%{nextver}/examples/motion.init-FreeBSD.sh
%attr(0755,root,root) %{_datadir}/%{name}-%{nextver}/examples/motion.init-Fedora
%attr(0644,root,root) %{_datadir}/%{name}-%{nextver}/examples/thread1.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{nextver}/examples/thread2.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{nextver}/examples/thread3.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{nextver}/examples/thread4.conf
%attr(0644,root,root) %{_sysconfdir}/logrotate.d/motion
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/motion.conf
%attr(0755,root,root) %{_bindir}/motion
%attr(0644,root,root) %{_mandir}/man1/motion.1*
%attr(0755,root,root) %{_unitdir}/%{name}.service
%attr(0755,root,root) %{_tmpfilesdir}/%{name}.conf

%changelog
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

