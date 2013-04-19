Name:           motion
Version:        3.3.0
Release:        trunkREV557.7%{?dist}
Summary:        A motion detection system

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://www.lavrsen.dk/twiki/bin/view/Motion/WebHome
Source0:        http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:        motion.service
Patch0:         motion-0001-emit-asm-emms-only-on-x86-and-amd64-arches.patch
Patch1:         motion-0002-there-is-no-bin-service-in-Fedora-use-systemctl.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libjpeg-devel ffmpeg-compat-devel zlib-devel
Buildrequires:  pkgconfig(sqlite3)
BuildRequires:  systemd-units
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
%setup -q
%patch0 -p1
%patch1 -p1

%build
export PKG_CONFIG_LIBDIR="%{_libdir}/ffmpeg-compat/pkgconfig"
%configure --sysconfdir=%{_sysconfdir}/%{name} --without-optimizecpu --with-ffmpeg --without-mysql --without-pgsql
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
#We rename the configuration file
mv %{buildroot}%{_sysconfdir}/%{name}/motion-dist.conf %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We move the logrotate configuration
mkdir %{buildroot}%{_sysconfdir}/logrotate.d
mv %{_builddir}/%{name}-%{version}/motion.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/motion
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

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%clean
rm -rf %{buildroot}

%files
#Permissions are bogus upstream, we need to be sure to set them here
%defattr (-,root,root,-)
%dir %{_sysconfdir}/%{name}
%dir %{_datadir}/%{name}-%{version}
%dir %{_datadir}/%{name}-%{version}/examples
%doc CHANGELOG COPYING CREDITS INSTALL README motion_guide.html
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/motion-dist.conf
%attr(0755,root,root) %{_datadir}/%{name}-%{version}/examples/motion.init-Debian
%attr(0755,root,root) %{_datadir}/%{name}-%{version}/examples/motion.init-FreeBSD.sh
%attr(0755,root,root) %{_datadir}/%{name}-%{version}/examples/motion.init-Fedora
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/thread1.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/thread2.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/thread3.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/thread4.conf
%attr(0644,root,root) %{_sysconfdir}/logrotate.d/motion
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/motion.conf
%attr(0755,root,root) %{_bindir}/motion
%attr(0644,root,root) %{_mandir}/man1/motion.1*
%attr(0755,root,root) %{_unitdir}/%{name}.service

%changelog
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

