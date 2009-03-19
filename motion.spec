Name:           motion
Version:        3.2.11
Release:        3%{?dist}
Summary:        A motion detection system

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://motion.sourceforge.net/
Source0:        http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:        motion-initscript
Patch0:         ffmpeg-detection.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libjpeg-devel ffmpeg-devel zlib-devel
#Requires:       ffmpeg
Requires(post): chkconfig
Requires(preun): chkconfig initscripts
Requires(postun): initscripts

%description
Motion is a software motion detector. It grabs images from video4linux devices
and/or from webcams (such as the axis network cameras). Motion is the perfect
tool for keeping an eye on your property keeping only those images that are
interesting. Motion is strictly command line driven and can run as a daemon
with a rather small footprint. This version is built with ffmpeg support but
without MySQL and PostgreSQL support.

%prep
%setup -q
#ffmpeg detection patch in version 3.2.11. This is an upstream patch.
%patch0 -p0

%build
%configure --sysconfdir=%{_sysconfdir}/%{name} --without-optimizecpu --with-ffmpeg --without-mysql --without-pgsql 
#We convert 2 files to UTF-8, otherwise rpmlint complains
iconv -f iso8859-1 -t utf-8 CREDITS > CREDITS.conv && mv -f CREDITS.conv CREDITS
iconv -f iso8859-1 -t utf-8 CHANGELOG > CHANGELOG.conv && mv -f CHANGELOG.conv CHANGELOG
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
#We rename the configuration file
mv %{buildroot}%{_sysconfdir}/%{name}/motion-dist.conf %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We change the PID file path to match the one in the startup script
sed -i 's|/var/run/motion/motion.pid|/var/run/motion.pid|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We remove SQL directives in the configuration file, as we don't use them
sed -i 's|sql_log_image|; sql_log_image|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|sql_log_snapshot|; sql_log_snapshot|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|sql_log_mpeg|; sql_log_mpeg|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|sql_log_timelapse|; sql_log_timelapse|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
sed -i 's|sql_query|; sql_query|g' %{buildroot}%{_sysconfdir}/%{name}/motion.conf
#We install our startup script
install -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}

%post
#We add the motion init script to the services when installing
/sbin/chkconfig --add %{name}

%preun
#We stop the service and remove it from init scripts when erasing
if [ $1 = 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%postun
#We restart the service during an upgrade
if [ "$1" -ge "1" ] ; then
    /sbin/service %{name} condrestart >/dev/null 2>&1
fi

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
%attr(0755,root,root) %{_datadir}/%{name}-%{version}/examples/motion.init-RH
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/thread1.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/thread2.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/thread3.conf
%attr(0644,root,root) %{_datadir}/%{name}-%{version}/examples/thread4.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/motion.conf
%attr(0755,root,root) %{_bindir}/motion
%attr(0644,root,root) %{_mandir}/man1/motion.1*
%attr(0755,root,root) %{_initrddir}/%{name}

%changelog
* Wed Mar 18 2009 Steven Moix <steven.moix@axianet.ch> - 3.2.11-3
- Even more corrected init script thanks to Stewart Adam

* Sun Mar 15 2009 Steven Moix <steven.moix@axianet.ch> - 3.2.11-2
- Removed the ffmpeg requires
- Corrected the spec file
- New init script with a corrected start() function and LSB header support

* Tue Mar 03 2009 Steven Moix <steven.moix@axianet.ch> - 3.2.11-1
- Updated to Fedora 10 standard

* Sun Sep 18 2005 Kenneth Lavrsen <kenneth@lavrsen.dk> - 3.2.4-1
- Generic version of livna spec file replacing the old less optimal specfile.

* Thu Sep 15 2005 Dams <anvil[AT]livna.org> - 3.2.3-0.lvn.1
- Initial released based upon upstream spec file
