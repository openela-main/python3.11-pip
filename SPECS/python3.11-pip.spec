%global __python3 /usr/bin/python3.11
%global python3_pkgversion 3.11

%bcond_with tests

%global srcname pip
%global base_version 22.3.1
%global upstream_version %{base_version}%{?prerel}
%global python_wheel_name %{srcname}-%{upstream_version}-py3-none-any.whl

%global bashcompdir %(pkg-config --variable=completionsdir bash-completion 2>/dev/null)

Name:           python%{python3_pkgversion}-%{srcname}
Version:        %{base_version}%{?prerel:~%{prerel}}
Release:        4%{?dist}.1
Summary:        A tool for installing and managing Python packages

# We bundle a lot of libraries with pip, which itself is under MIT license.
# Here is the list of the libraries with corresponding licenses:

# appdirs: MIT
# certifi: MPLv2.0
# chardet: LGPLv2
# colorama: BSD
# CacheControl: ASL 2.0
# distlib: Python
# distro: ASL 2.0
# html5lib: MIT
# idna: BSD
# ipaddress: Python
# msgpack: ASL 2.0
# packaging: ASL 2.0 or BSD
# pep517: MIT
# progress: ISC
# pygments: BSD
# pyparsing: MIT
# requests: ASL 2.0
# resolvelib: ISC
# rich: MIT
# setuptools: MIT
# six: MIT
# tenacity: ASL 2.0
# tomli: MIT
# typing-extensions: Python
# urllib3: MIT
# webencodings: BSD

License:        MIT and Python and ASL 2.0 and BSD and ISC and LGPLv2 and MPLv2.0 and (ASL 2.0 or BSD)
URL:            https://pip.pypa.io/
Source0:        https://github.com/pypa/pip/archive/%{upstream_version}/%{srcname}-%{upstream_version}.tar.gz
BuildArch:      noarch

# Prevent removing of the system packages installed under /usr/lib
# when pip install -U is executed.
# https://bugzilla.redhat.com/show_bug.cgi?id=1550368#c24
# Could be replaced with https://www.python.org/dev/peps/pep-0668/
Patch0:         remove-existing-dist-only-if-path-conflicts.patch

# Use the system level root certificate instead of the one bundled in certifi
# https://bugzilla.redhat.com/show_bug.cgi?id=1655253
# The same patch is a part of the RPM-packaged python-certifi
Patch1:         dummy-certifi.patch

# Don't warn the user about pip._internal.main() entrypoint
# In Fedora, we use that in ensurepip and users cannot do anything about it,
# this warning is juts moot. Also, the warning breaks CPython test suite.
Patch2:         nowarn-pip._internal.main.patch

# Don't warn the user about packaging's LegacyVersion being deprecated.
# (This also breaks Python's test suite when warnings are treated as errors.)
# Upstream issue: https://github.com/pypa/packaging/issues/368
Patch3:         no-version-warning.patch

# CVE-2007-4559, PEP-721, PEP-706: Use tarfile.data_filter for extracting
# - Minimal downstream-only patch, to be replaced by upstream solution
#   proposed in https://github.com/pypa/pip/pull/12214
# - Test patch submitted upstream in the above pull request
# - Patch for vendored distlib, accepted upstream:
#   https://github.com/pypa/distlib/pull/201
Patch4:         cve-2007-4559-tarfile.patch

# Downstream only patch
# Users might have local installations of pip from using
# `pip install --user --upgrade pip` on older/newer versions.
# If they do that and they run `pip` or  `pip3`, the one from /usr/bin is used.
# However that's the one from this RPM package and the import in there might
# fail (it tries to import from ~/.local, but older or newer pip is there with
# a bit different API).
# We add this patch as a dirty workaround to make /usr/bin/pip* work with
# both pip10+ (from this RPM) and older or newer (19.3+) pip (from whatever).
# A proper fix is to put ~/.local/bin in front of /usr/bin in the PATH,
# however others are against that and we cannot change it for existing
# installs/user homes anyway.
# https://bugzilla.redhat.com/show_bug.cgi?id=1569488
# https://bugzilla.redhat.com/show_bug.cgi?id=1571650
# https://bugzilla.redhat.com/show_bug.cgi?id=1767212
# WARNING: /usr/bin/pip* are entrypoints, this cannot be applied in %%prep!
# %%patch10 doesn't work outside of %%prep, so we add it as a source
# Note that since pip 20, old main() import paths are preserved for backwards
# compatibility: https://github.com/pypa/pip/issues/7498
# Meaning we don't need to update any of the older pips to support 20+
# We also don't need to update Pythons to use new import path in ensurepip
Source10:        pip-allow-different-versions.patch


# Virtual provides for the packages bundled by pip.
# You can generate it with:
# %%{_rpmconfigdir}/pythonbundles.py --namespace 'python%%{1}dist' src/pip/_vendor/vendor.txt
%global bundled() %{expand:
Provides: bundled(python%{1}dist(cachecontrol)) = 0.12.11
Provides: bundled(python%{1}dist(certifi)) = 2022.9.24
Provides: bundled(python%{1}dist(chardet)) = 5
Provides: bundled(python%{1}dist(colorama)) = 0.4.5
Provides: bundled(python%{1}dist(distlib)) = 0.3.6
Provides: bundled(python%{1}dist(distro)) = 1.7
Provides: bundled(python%{1}dist(idna)) = 3.4
Provides: bundled(python%{1}dist(msgpack)) = 1.0.4
Provides: bundled(python%{1}dist(packaging)) = 21.3
Provides: bundled(python%{1}dist(pep517)) = 0.13
Provides: bundled(python%{1}dist(platformdirs)) = 2.5.2
Provides: bundled(python%{1}dist(pygments)) = 2.13
Provides: bundled(python%{1}dist(pyparsing)) = 3.0.9
Provides: bundled(python%{1}dist(requests)) = 2.28.1
Provides: bundled(python%{1}dist(resolvelib)) = 0.8.1
Provides: bundled(python%{1}dist(rich)) = 12.5.1
Provides: bundled(python%{1}dist(setuptools)) = 44
Provides: bundled(python%{1}dist(six)) = 1.16
Provides: bundled(python%{1}dist(tenacity)) = 8.1
Provides: bundled(python%{1}dist(tomli)) = 2.0.1
Provides: bundled(python%{1}dist(typing-extensions)) = 4.4
Provides: bundled(python%{1}dist(urllib3)) = 1.26.12
Provides: bundled(python%{1}dist(webencodings)) = 0.5.1
}

# Some manylinux1 wheels need libcrypt.so.1.
# Manylinux1, a common (as of 2019) platform tag for binary wheels, relies
# on a glibc version that included ancient crypto functions, which were
# moved to libxcrypt and then removed in:
#  https://fedoraproject.org/wiki/Changes/FullyRemoveDeprecatedAndUnsafeFunctionsFromLibcrypt
# The manylinux1 standard assumed glibc would keep ABI compatibility,
# but that's only the case if libcrypt.so.1 (libxcrypt-compat) is around.
# This should be solved in the next manylinux standard (but it may be
# a long time until manylinux1 is phased out).
# See: https://github.com/pypa/manylinux/issues/305
# Note that manylinux is only applicable to x86 (both 32 and 64 bits)
%global crypt_compat_recommends() %{expand:
Recommends: (libcrypt.so.1()(64bit) if python%{1}(x86-64))
Recommends: (libcrypt.so.1 if python%{1}(x86-32))
}

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-rpm-macros
# python3 bootstrap: this is rebuilt before the final build of python3, which
# adds the dependency on python3-rpm-generators, so we require it manually
# Note that the package prefix is always python3-, even if we build for 3.X
BuildRequires:  python3-rpm-generators
# We utilize the main Python's stack sphinx to build the manual pages
BuildRequires:  python3-sphinx
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  bash-completion
BuildRequires:  python%{python3_pkgversion}-wheel
BuildRequires:  ca-certificates
Requires:       ca-certificates

%if %{with tests}
BuildRequires:  /usr/bin/git
BuildRequires:  /usr/bin/hg
BuildRequires:  /usr/bin/bzr
BuildRequires:  /usr/bin/svn
BuildRequires:  python%{python3_pkgversion}-setuptools-wheel
BuildRequires:  python%{python3_pkgversion}-wheel-wheel
BuildRequires:  python%{python3_pkgversion}-cryptography
BuildRequires:  python%{python3_pkgversion}-mock
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-pretend
BuildRequires:  python%{python3_pkgversion}-freezegun
BuildRequires:  python%{python3_pkgversion}-scripttest
BuildRequires:  python%{python3_pkgversion}-virtualenv
BuildRequires:  python%{python3_pkgversion}-werkzeug
BuildRequires:  python%{python3_pkgversion}-pyyaml
BuildRequires:  python%{python3_pkgversion}-tomli-w
BuildRequires:  python%{python3_pkgversion}-installer
%endif


# pip has to require explicit version of python that provides
# filters in tarfile module (fix for CVE-2007-4559).
Requires: python%{python3_pkgversion} >= 3.11.4-3


# This was previously required and we keep it recommended because a lot of
# sdists installed via pip will try to import setuptools.
# But pip doesn't actually require setuptools.
# It can install wheels without them and it can build wheels in isolation mode
# (using setuptools/flit/poetry/... installed from PyPI).
# Side note: pip bundles pkg_resources from setuptools for internal usage.
Recommends:     python%{python3_pkgversion}-setuptools

# Virtual provides for the packages bundled by pip:
%{bundled %{python3_pkgversion}}

%{crypt_compat_recommends %{python3_pkgversion}}

%description -n python%{python3_pkgversion}-%{srcname}
pip is a package management system used to install and manage software packages
written in Python. Many packages can be found in the Python Package Index
(PyPI). pip is a recursive acronym that can stand for either "Pip Installs
Packages" or "Pip Installs Python".

%package -n     %{python_wheel_pkg_prefix}-%{srcname}-wheel
Summary:        The pip wheel
Requires:       ca-certificates
# Older Python does not provide tarfile filters (fix for CVE-2007-4559).
Conflicts:      python%{python3_pkgversion} < 3.11.4-3

# Virtual provides for the packages bundled by pip:
%{bundled %{python3_pkgversion}}

%{crypt_compat_recommends %{python3_pkgversion}}

%description -n %{python_wheel_pkg_prefix}-%{srcname}-wheel
A Python wheel of pip to use with venv.

%prep
%autosetup -p1 -n %{srcname}-%{upstream_version}

# this goes together with patch4
rm src/pip/_vendor/certifi/*.pem

# Remove unneeded doc dependencies
sed -i '/myst_parser/d;/sphinx_copybutton/d;/sphinx_inline_tabs/d;/sphinxcontrib.towncrier/d' docs/html/conf.py

# tests expect wheels in here
ln -s %{python_wheel_dir} tests/data/common_wheels

# Remove windows executable binaries
rm -v src/pip/_vendor/distlib/*.exe
sed -i '/\.exe/d' setup.py

%build
%py3_build_wheel

# Build the man pages
export PYTHONPATH=./src/
sphinx-build-3 -b man  docs/man  docs/build/man  -c docs/html

%install
# The following is similar to %%pyproject_install, but we don't have
# /usr/bin/pip yet, so we install using the wheel directly.
# (This is not standard wheel usage, but the pip wheel supports it -- see
#  pip/__main__.py)
%{python3} dist/%{python_wheel_name}/pip install \
    --root %{buildroot} \
    --no-deps \
    --disable-pip-version-check \
    --progress-bar off \
    --verbose \
    --ignore-installed \
    --no-warn-script-location \
    --no-index \
    --no-cache-dir \
    --find-links dist \
    'pip==%{upstream_version}'

# Install the man pages
pushd docs/build/man
install -d %{buildroot}%{_mandir}/man1
for MAN in *1; do
install -pm0644 $MAN %{buildroot}%{_mandir}/man1/${MAN/pip/pip%{python3_pkgversion}}
install -pm0644 $MAN %{buildroot}%{_mandir}/man1/${MAN/pip/pip-%{python3_pkgversion}}
done
popd

# before we ln -s anything, we apply Source10 patch to all pips:
for PIP in %{buildroot}%{_bindir}/pip*; do
  patch -p1 --no-backup-if-mismatch $PIP < %{SOURCE10}
done

mkdir -p %{buildroot}%{bashcompdir}
PYTHONPATH=%{buildroot}%{python3_sitelib} \
    %{buildroot}%{_bindir}/pip completion --bash \
    > %{buildroot}%{bashcompdir}/pip%{python3_pkgversion}

# Make bash completion apply to all the 5 symlinks we install
sed -i -e "s/^\\(complete.*\\) pip\$/\\1 pip{,-}%{python3_pkgversion}/" \
    -e s/_pip_completion/_pip%{python3_pkgversion}_completion/ \
    %{buildroot}%{bashcompdir}/pip%{python3_pkgversion}


# Provide symlinks to executables to comply with Fedora guidelines for Python
ln -s ./pip%{python3_pkgversion} %{buildroot}%{_bindir}/pip-%{python3_pkgversion}


# Make sure the INSTALLER is not pip and remove RECORD
# %%pyproject macros do this for all packages
echo rpm > %{buildroot}%{python3_sitelib}/pip-%{upstream_version}.dist-info/INSTALLER
rm %{buildroot}%{python3_sitelib}/pip-%{upstream_version}.dist-info/RECORD

mkdir -p %{buildroot}%{python_wheel_dir}
install -p dist/%{python_wheel_name} -t %{buildroot}%{python_wheel_dir}

# RHEL: Remove binaries conflicting with RHEL's main pip
rm %{buildroot}%{_bindir}/pip
rm %{buildroot}%{_bindir}/pip3


%check
# Verify bundled provides are up to date
%{_rpmconfigdir}/pythonbundles.py src/pip/_vendor/vendor.txt --namespace 'python%{python3_pkgversion}dist' \
    --compare-with '%{bundled %{python3_pkgversion}}'

%if %{with tests}
# Upstream tests
# bash completion tests only work from installed package
pytest_k='not completion'

# --deselect'ed tests are not compatible with the latest virtualenv
# These files contain almost 500 tests so we should enable them back
# as soon as pip will be compatible upstream
# https://github.com/pypa/pip/pull/8441
%pytest -m 'not network' -k "$(echo $pytest_k)" \
    --deselect tests/functional --deselect tests/lib/test_lib.py
%endif


%files -n python%{python3_pkgversion}-%{srcname}
%doc README.rst
%license %{python3_sitelib}/pip-%{upstream_version}.dist-info/LICENSE.txt
%{_mandir}/man1/pip%{python3_pkgversion}.*
%{_mandir}/man1/pip%{python3_pkgversion}-*.*
%{_mandir}/man1/pip-%{python3_pkgversion}.*
%{_mandir}/man1/pip-%{python3_pkgversion}-*.*
%{_bindir}/pip%{python3_pkgversion}
%{_bindir}/pip-%{python3_pkgversion}
%{python3_sitelib}/pip*
%dir %{bashcompdir}
%{bashcompdir}/pip%{python3_pkgversion}

%files -n %{python_wheel_pkg_prefix}-%{srcname}-wheel
%license LICENSE.txt
# we own the dir for simplicity
%dir %{python_wheel_dir}/
%{python_wheel_dir}/%{python_wheel_name}

%changelog
* Wed Feb 14 2024 Tomáš Hrnčiar <thrnciar@redhat.com> - 22.3.1-4.1
- Require Python with tarfile filters
Resolves: RHEL-25456

* Tue Aug 08 2023 Petr Viktorin <pviktori@redhat.com> - 22.3.1-4
- Use tarfile.data_filter for extracting (CVE-2007-4559, PEP-721, PEP-706)
Resolves: RHBZ#2218247

* Mon Mar 06 2023 Lumír Balhar <lbalhar@redhat.com> - 22.3.1-3
- Fix changelog to contain Fedora contributors
Resolves: RHEL-232

* Mon Jan 30 2023 Charalampos Stratakis <cstratak@redhat.com> - 22.3.1-2
- Add BuildRequires on python3.11-rpm-macros

* Wed Aug 03 2022 Charalampos Stratakis <cstratak@redhat.com> - 22.3.1-1
- Initial package
- Fedora contributions by:
    Bill Nottingham <notting@fedoraproject.org>
    Charalampos Stratakis <cstratak@redhat.com>
    David Malcolm <dmalcolm@redhat.com>
    Dennis Gilmore <dennis@ausil.us>
    Jon Ciesla <limburgher@gmail.com>
    Karolina Surma <ksurma@redhat.com>
    Kevin Fenzi <kevin@fedoraproject.org>
    Kevin Kofler <Kevin@tigcc.ticalc.org>
    Luke Macken <lmacken@redhat.com>
    Lumir Balhar <lbalhar@redhat.com>
    Marcel Plch <mplch@redhat.com>
    Matej Stuchlik <mstuchli@redhat.com>
    Michal Cyprian <m.cyprian@gmail.com>
    Miro Hrončok <miro@hroncok.cz>
    Orion Poplawski <orion@cora.nwra.com>
    Pádraig Brady <P@draigBrady.com>
    Peter Halliday <hoangelos@fedoraproject.org>
    Petr Viktorin <pviktori@redhat.com>
    Robert Kuska <rkuska@redhat.com>
    Slavek Kabrda <bkabrda@redhat.com>
    Tim Flink <tflink@fedoraproject.org>
    Tomáš Hrnčiar <thrnciar@redhat.com>
    Tomas Orsava <torsava@redhat.com>
    Toshio Kuratomi <toshio@fedoraproject.org>
    Ville Skyttä <ville.skytta@iki.fi>
