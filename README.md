# TinyOS
by Han-Gyeol Kim


# How to install Tinyos-2.1.2 on Ubuntu 

sudo apt-get install -y vim

1.Tinyos Reposity add
  sudo vim /etc/apt/sources.list 
  add under line
 deb http://tinyos.standford.edu/tinyos/dists/ubuntu lucid main
sudo apt-get update 

sudo chown username@username -R /opt/tinyos-2.1.2/

sudo chown username -R /opt/tinyos-2.1.2/

cd /opt/
sudo vim tinyos.sh# Here we setup the environment

```
    # variables needed by the tinyos 
    # make system

    export TOSROOT="<local-tinyos-path>"
    export TOSDIR="$TOSROOT/tos"
    export CLASSPATH=$CLASSPATH:$TOSROOT/support/sdk/java
    export MAKERULES="$TOSROOT/support/make/Makerules"
    export PYTHONPATH=$PYTHONPATH:$TOSROOT/support/sdk/python

    echo "setting up TinyOS on source path $TOSROOT"
```
sudo vim ~/.bashrc

-add bottom underline 

source /opt/tinyos-2.1.2/tinyos.sh

cd /opt/tinyos-2.1.2/support/sdk/java/

sudo tos-install-jni

make

make install

msp430-gcc --version
we need to version 4.5.3 over !

sudo apt-get autoremove --purge msp430*


gpg --keyserver keyserver.ubuntu.com --recv-keys 34EC655A
gpg -a --export 34EC655A | sudo apt-key add -

sudo vim /etc/apt/sources.list

add underline
deb http://tinyprod.net/repos/debian/squeeze main
deb http://tinyprod.net/repos/debian/msp430-46 main

sudo apt-get update

sudo apt-get install msp430-46 nesc tinyos-tools

sudo vim /opt/tinyos-2.1.2/tinyos.sh
export PATH=/opt/msp430-46/bin:$PATH (you have to add)

end...


# How to setting Vim for Nesc
if root
vim /root/.vim/vimrc
if user
sudo vim /usr/share/vim/vimrc

```
    set nu
    set lines=40 columns=100
    syntax enable
    colo torte
    set ruler
    syn on
    colorscheme default
    set ts=2
    
    au BufRead,BufNewFile *.nc set filetype=nesC
    au syntax nesC source /usr/share/vim/vim74/syntax/nc.vim (you need to copy the nc.vim)
```
# How to install Tinyos-2.1.2 on Cygwin
1.Download cygwin under site
https://cygwin.com/install.html

2.when the windows pops up to allow you to select what packages to install, be sure to select
```
    * rpm
    * make
    * perl
    * python
```
  * Extra package
``` * autoconf
    * automake
    * mingw64-x86_64-gcc-core 
    * mingw64-x86_64-gcc-g++ 
    * mingw64-i686-gcc-core 
    * mingw64-i686-gcc-g++ 
    * bison 
    * flex 
    * libiconv 
    * patch 
    * util-linux 
    * wget 
    * rpm-build 
    * rpm-devel 
    * rsync 
    * diffutils 
```
3.new Reposity
http://tinyos.stanford.edu/tinyos/dists/cygwin/

