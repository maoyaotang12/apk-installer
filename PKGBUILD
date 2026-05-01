# Maintainer: MaoYaoTang <maoyaotang@163.com>

pkgname=apk-installer-kde
pkgver=1.0.0
pkgrel=1
pkgdesc="KDE 桌面图形化 APK 安装器，支持右键APK直接安装"
arch=('any')
url="https://github.com/yourname/apk-installer-kde"
license=('MIT')
depends=('android-tools' 'python' 'python-pyqt6')
source=(kde_apk_installer.py
         ${pkgname%-kde}.desktop
         'android.svg')
sha256sums=('b4dce1e1f4e1fe08b9bc14d0ee8bd7a85302bca02d27bc57ea0fb531f6cd7d2b'
            '947a8d37bbc2d7488aa4918ce8ca7365cb6eebf1643c7ffe43118cb7175b4933'
            '1ed41f9183a4ae028aebc01caf3014abc7bf9fe6a564d541479ea0172515a7f8')

package() {
    # 安装主程序到 /usr/bin
    install -Dm755 "${srcdir}/kde_apk_installer.py" "${pkgdir}/usr/bin/apk-installer"

    # 安装桌面文件 关联APK右键
    install -Dm644 "${srcdir}/apk-installer.desktop" \
        "${pkgdir}/usr/share/applications/apk-installer.desktop"
    install -Dm644  ${srcdir}/android.svg ${pkgdir}/usr/share/pixmaps/apk-installer.svg
}
