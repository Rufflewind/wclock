# Maintainer: Phil Ruffwind <rf@rufflewind.com>
pkgname=wclock-git
pkgver=latest
pkgrel=1
pkgdesc="Monotonic wall clock library"
arch=(i686 x86_64)
url=https://github.com/Rufflewind/wclock
license=(MIT)
depends=()
makedepends=(git)
source=($pkgname::git://github.com/Rufflewind/wclock)
sha256sums=(SKIP)

pkgver() (
    cd "$srcdir/$pkgname"
    if s=`git 2>/dev/null describe --long --tags`; then
        printf '%s' "$s" | sed 's/^v//;s/\([^-]*-\)g/r\1/;s/-/./g'
    else
        printf 'r%s.%s' "`git rev-list --count HEAD`" \
                        "`git rev-parse --short HEAD`"
    fi
)

build() {
    cd "$srcdir/$pkgname"
    ./configure
    make
}

package() {
    cd "$srcdir/$pkgname"
    mkdir -p "$pkgdir/usr/include"
    mkdir -p "$pkgdir/usr/lib"
    cp -a include/* "$pkgdir/usr/include"
    cp -a lib/* "$pkgdir/usr/lib"
}
