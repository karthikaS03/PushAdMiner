# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# NOTE: DO *NOT* EDIT THIS FILE.  IT IS GENERATED.
# PLEASE UPDATE Dockerfile.txt INSTEAD OF THIS FILE
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
FROM ubuntu:bionic-20181204
#FROM node:8-slim

LABEL authors="Selenium <selenium-developers@googlegroups.com>"

#================================================
# Customize sources for apt-get
#================================================
RUN  echo "deb http://archive.ubuntu.com/ubuntu bionic main universe\n" > /etc/apt/sources.list \
  && echo "deb http://archive.ubuntu.com/ubuntu bionic-updates main universe\n" >> /etc/apt/sources.list \
  && echo "deb http://security.ubuntu.com/ubuntu bionic-security main universe\n" >> /etc/apt/sources.list

# No interactive frontend during docker build
ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true

#========================
# Miscellaneous packages
# Includes minimal runtime used for executing non GUI Java programs
#========================
RUN apt-get -qqy update \
  && apt-get -qqy --no-install-recommends install \
    bzip2 \
    ca-certificates \
    openjdk-8-jre-headless \
    tzdata \
    sudo \
    unzip \
    wget \
    jq \
    curl \
    supervisor \
    gnupg2 \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
  && sed -i 's/securerandom\.source=file:\/dev\/random/securerandom\.source=file:\/dev\/urandom/' ./usr/lib/jvm/java-8-openjdk-amd64/jre/lib/security/java.security

#===================
# Timezone settings
# Possible alternative: https://github.com/docker/docker/issues/3359#issuecomment-32150214
#===================
ENV TZ "UTC"
RUN echo "${TZ}" > /etc/timezone \
  && dpkg-reconfigure --frontend noninteractive tzdata



#=====================
# Node installation
#=====================

# RUN groupadd --gid 1000 node \
#   && useradd --uid 1000 --gid node --shell /bin/bash --create-home node

ENV NODE_VERSION 8.15.1

RUN buildDeps='xz-utils' \
    && ARCH= && dpkgArch="$(dpkg --print-architecture)" \
    && case "${dpkgArch##*-}" in \
      amd64) ARCH='x64';; \
      ppc64el) ARCH='ppc64le';; \
      s390x) ARCH='s390x';; \
      arm64) ARCH='arm64';; \
      armhf) ARCH='armv7l';; \
      i386) ARCH='x86';; \
      *) echo "unsupported architecture"; exit 1 ;; \
    esac \
    && set -ex \
    && apt-get update && apt-get install -y ca-certificates curl wget gnupg dirmngr $buildDeps --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && for key in \
      94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
      FD3A5288F042B6850C66B31F09FE44734EB7990E \
      71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
      DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
      C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
      B9AE9905FFD7803F25714661B63B535A4C206CA9 \
      77984A986EBC2AA786BC0F66B01FBB92821C587A \
      8FCCA13FEF1D0C2E91008E09770F7A9A5AE15600 \
      4ED778F539E3634C779C87C6D7062848A1AB005C \
      A48C2BEE680E841632CD4E44F07496B3EB3C1762 \
      B9E2F5981AA6E0CD28160D9FF13993A75599653C \
    ; do \
      gpg --batch --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys "$key" || \
      gpg --batch --keyserver hkp://ipv4.pool.sks-keyservers.net --recv-keys "$key" || \
      gpg --batch --keyserver hkp://pgp.mit.edu:80 --recv-keys "$key" ; \
    done \
    && curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-$ARCH.tar.xz" \
    && curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
    && gpg --batch --decrypt --output SHASUMS256.txt SHASUMS256.txt.asc \
    && grep " node-v$NODE_VERSION-linux-$ARCH.tar.xz\$" SHASUMS256.txt | sha256sum -c - \
    && tar -xJf "node-v$NODE_VERSION-linux-$ARCH.tar.xz" -C /usr/local --strip-components=1 --no-same-owner \
    && rm "node-v$NODE_VERSION-linux-$ARCH.tar.xz" SHASUMS256.txt.asc SHASUMS256.txt \
    && apt-get purge -y --auto-remove $buildDeps \
    && ln -s /usr/local/bin/node /usr/local/bin/nodejs

ENV YARN_VERSION 1.12.3

RUN set -ex \
  && for key in \
    6A010C5166006599AA17F08146C2130DFD2497F5 \
  ; do \
    gpg --batch --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys "$key" || \
    gpg --batch --keyserver hkp://ipv4.pool.sks-keyservers.net --recv-keys "$key" || \
    gpg --batch --keyserver hkp://pgp.mit.edu:80 --recv-keys "$key" ; \
  done \
  && curl -fsSLO --compressed "https://yarnpkg.com/downloads/$YARN_VERSION/yarn-v$YARN_VERSION.tar.gz" \
  && curl -fsSLO --compressed "https://yarnpkg.com/downloads/$YARN_VERSION/yarn-v$YARN_VERSION.tar.gz.asc" \
  && gpg --batch --verify yarn-v$YARN_VERSION.tar.gz.asc yarn-v$YARN_VERSION.tar.gz \
  && mkdir -p /opt \
  && tar -xzf yarn-v$YARN_VERSION.tar.gz -C /opt/ \
  && ln -s /opt/yarn-v$YARN_VERSION/bin/yarn /usr/local/bin/yarn \
  && ln -s /opt/yarn-v$YARN_VERSION/bin/yarnpkg /usr/local/bin/yarnpkg \
  && rm yarn-v$YARN_VERSION.tar.gz.asc yarn-v$YARN_VERSION.tar.gz

CMD [ "node" ]

RUN apt-get update && \
apt-get install -yq gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 \
libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst  \
ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget && \
wget https://github.com/Yelp/dumb-init/releases/download/v1.2.1/dumb-init_1.2.1_amd64.deb && \
dpkg -i dumb-init_*.deb && rm -f dumb-init_*.deb && \
apt-get clean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

RUN yarn global add puppeteer@1.8.0 && yarn cache clean

RUN apt-get update && apt-get install imagemagick -y

ENV NODE_PATH="/usr/local/share/.config/yarn/global/node_modules:${NODE_PATH}"

COPY ./lib /usr/local/share/.config/yarn/global/node_modules/puppeteer/lib 
#RUN groupadd -r pptruser && useradd -r -g pptruser -G audio,video pptruser

# Set language to UTF8
ENV LANG="C.UTF-8"


#========================================
# Add normal user with passwordless sudo
#========================================
RUN useradd pptruser \
         --shell /bin/bash  \
         --create-home \
  && usermod -a -G sudo pptruser \
  && echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
  && echo 'pptruser:secret' | chpasswd
ENV HOME=/home/pptruser

#=======================================
# Create shared / common bin directory
#=======================================
RUN  mkdir -p /opt/bin 

# Add user so we don't need --no-sandbox.
RUN mkdir /home/pptruser/screenshots \
  && mkdir /home/pptruser/chromium \
  && mkdir /home/pptruser/resources \
  && mkdir /home/pptruser/logs \
  && mkdir /home/pptruser/app \
	&& mkdir -p /home/pptruser/Downloads \
    && chown -R pptruser:pptruser /home/pptruser \
    && chown -R pptruser:pptruser /usr/local/share/.config/yarn/global/node_modules \
    && chown -R pptruser:pptruser /home/pptruser/screenshots \
    && chown -R pptruser:pptruser /home/pptruser/app \
    && chown -R pptruser:pptruser /home/pptruser/resources \
    && chown -R pptruser:pptruser /home/pptruser/chromium \
    && chown -R pptruser:pptruser /home/pptruser/logs



#======================================
# Add Grid check script
#======================================
#COPY check-grid.sh entry_point.sh /opt/bin/
# RUN chmod +x /opt/bin/check-grid.sh

COPY entry_point.sh /opt/bin/

#======================================
# Add Supervisor configuration file
#======================================
COPY supervisord.conf /etc
RUN  mkdir -p /var/run/supervisor /var/log/supervisor \
  && chmod -R 777 /var/run/supervisor /var/log/supervisor /etc/passwd \
  && chgrp -R 0 ${HOME} /var/run/supervisor /var/log/supervisor \
  && chmod -R g=u ${HOME} /var/run/supervisor /var/log/supervisor

#==========
# Selenium & relaxing permissions for OpenShift and other non-sudo environments
#==========
# RUN  mkdir -p /opt/selenium /var/run/supervisor /var/log/supervisor \
#   && touch /opt/selenium/config.json \
#   && chmod -R 777 /opt/selenium /var/run/supervisor /var/log/supervisor /etc/passwd \
#   && wget --no-verbose https://selenium-release.storage.googleapis.com/3.141/selenium-server-standalone-3.141.59.jar \
#     -O /opt/selenium/selenium-server-standalone.jar \
#   && chgrp -R 0 /opt/selenium ${HOME} /var/run/supervisor /var/log/supervisor \
#   && chmod -R g=u /opt/selenium ${HOME} /var/run/supervisor /var/log/supervisor


#===================================================
# Run the following commands as non-privileged user
#===================================================
USER pptruser


CMD ["/opt/bin/entry_point.sh"]

USER root

#==============
# Xvfb
#==============
RUN apt-get update -qqy \
  && apt-get -qqy install \
    xvfb \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

#==============================
# Locale and encoding settings
#==============================
ENV LANG_WHICH en
ENV LANG_WHERE US
ENV ENCODING UTF-8
ENV LANGUAGE ${LANG_WHICH}_${LANG_WHERE}.${ENCODING}
ENV LANG ${LANGUAGE}
# Layer size: small: ~9 MB
# Layer size: small: ~9 MB MB (with --no-install-recommends)
RUN apt-get -qqy update \
  && apt-get -qqy --no-install-recommends install \
    language-pack-en \
    tzdata \
    locales \
  && locale-gen ${LANGUAGE} \
  && dpkg-reconfigure --frontend noninteractive locales \
  && apt-get -qyy autoremove \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get -qyy clean

#================
# Font libraries
#================
# libfontconfig            ~1 MB
# libfreetype6             ~1 MB
# xfonts-cyrillic          ~2 MB
# xfonts-scalable          ~2 MB
# fonts-liberation         ~3 MB
# fonts-ipafont-gothic     ~13 MB
# fonts-wqy-zenhei         ~17 MB
# fonts-tlwg-loma-otf      ~300 KB
# ttf-ubuntu-font-family   ~5 MB
#   Ubuntu Font Family, sans-serif typeface hinted for clarity
# Removed packages:
# xfonts-100dpi            ~6 MB
# xfonts-75dpi             ~6 MB
# Regarding fonts-liberation see:
#  https://github.com/SeleniumHQ/docker-selenium/issues/383#issuecomment-278367069
# Layer size: small: 36.28 MB (with --no-install-recommends)
# Layer size: small: 36.28 MB
RUN apt-get -qqy update \
  && apt-get -qqy --no-install-recommends install \
    libfontconfig \
    libfreetype6 \
    xfonts-cyrillic \
    xfonts-scalable \
    fonts-liberation \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-tlwg-loma-otf \
    ttf-ubuntu-font-family \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get -qyy clean

#===================================================
# Run the following commands as non-privileged user
#===================================================


USER pptruser

# #==============================
# # Scripts to run XVFB
# #==============================
COPY start-xvfb.sh \
      /opt/bin/

# #============================
# # Some configuration options
# #============================
# ENV SCREEN_WIDTH 1360
# ENV SCREEN_HEIGHT 1020
# ENV SCREEN_DEPTH 24
# ENV DISPLAY :99.0
# ENV START_XVFB true


#==============================
# Scripts to run Selenium Node and XVFB
# #==============================
# COPY start-selenium-node.sh \
#       start-xvfb.sh \
#       /opt/bin/


#============================
# Some configuration options
#============================
ENV SCREEN_WIDTH 1360
ENV SCREEN_HEIGHT 1020
ENV SCREEN_DEPTH 24
ENV DISPLAY :99.0
ENV START_XVFB true

#========================
# Selenium Configuration
#========================
# # As integer, maps to "maxInstances"
# ENV NODE_MAX_INSTANCES 1
# # As integer, maps to "maxSession"
# ENV NODE_MAX_SESSION 1
# # As address, maps to "host"
# ENV NODE_HOST 0.0.0.0
# # As integer, maps to "port"
# ENV NODE_PORT 5555
# # In milliseconds, maps to "registerCycle"
# ENV NODE_REGISTER_CYCLE 5000
# # In milliseconds, maps to "nodePolling"
# ENV NODE_POLLING 5000
# # In milliseconds, maps to "unregisterIfStillDownAfter"
# ENV NODE_UNREGISTER_IF_STILL_DOWN_AFTER 60000
# # As integer, maps to "downPollingLimit"
# ENV NODE_DOWN_POLLING_LIMIT 2
# # As string, maps to "applicationName"
# ENV NODE_APPLICATION_NAME ""
# # Debug
# ENV GRID_DEBUG false


# Following line fixes https://github.com/SeleniumHQ/docker-selenium/issues/87
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

# Creating base directory for Xvfb
RUN  sudo mkdir -p /tmp/.X11-unix && sudo chmod 1777 /tmp/.X11-unix

USER root


#RUN chmod +x /opt/bin/start-selenium-node.sh

RUN chmod +x /opt/bin/start-xvfb.sh

#============================================
# Google Chrome
#============================================
# can specify versions by CHROME_VERSION;
#  e.g. google-chrome-stable=53.0.2785.101-1
#       google-chrome-beta=53.0.2785.92-1
#       google-chrome-unstable=54.0.2840.14-1
#       latest (equivalent to google-chrome-stable)
#       google-chrome-beta  (pull latest beta)
#============================================
# ARG CHROME_VERSION="google-chrome-stable"
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
#   && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
#   && apt-get update -qqy \
#   && apt-get -qqy install \
#     ${CHROME_VERSION:-google-chrome-stable} \
#   && rm /etc/apt/sources.list.d/google-chrome.list \
#   && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# #=================================
# # Chrome Launch Script Wrapper
# #=================================
# COPY wrap_chrome_binary /opt/bin/wrap_chrome_binary
# RUN /opt/bin/wrap_chrome_binary

USER pptruser


#============================================
# Chrome webdriver
#============================================
# can specify versions by CHROME_DRIVER_VERSION
# Latest released version will be used by default
#============================================
# ARG CHROME_DRIVER_VERSION="73.0.3683.68"
# RUN CD_VERSION=$(echo $CHROME_DRIVER_VERSION) \
#   && echo "Using chromedriver version: "$CD_VERSION \
#   && wget --no-verbose -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CD_VERSION/chromedriver_linux64.zip \
#   && rm -rf /opt/selenium/chromedriver \
#   && unzip /tmp/chromedriver_linux64.zip -d /opt/selenium \
#   && rm /tmp/chromedriver_linux64.zip \
#   && mv /opt/selenium/chromedriver /opt/selenium/chromedriver-$CD_VERSION \
#   && chmod 755 /opt/selenium/chromedriver-$CD_VERSION \
#   && sudo ln -fs /opt/selenium/chromedriver-$CD_VERSION /usr/bin/chromedriver

# COPY generate_config /opt/bin/generate_config

# Generating a default config during build time
#RUN /opt/bin/generate_config > /opt/selenium/config.json


USER root

#=====
# VNC
#=====
RUN apt-get update -qqy \
  && apt-get -qqy install \
  x11vnc \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

#=========
# fluxbox
# A fast, lightweight and responsive window manager
#=========
RUN apt-get update -qqy \
  && apt-get -qqy install \
    fluxbox \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

USER pptruser

#==============================
# Generating the VNC password as pptruser
# So the service can be started with pptruser
#==============================

RUN mkdir -p ${HOME}/.vnc \
  && x11vnc -storepasswd secret ${HOME}/.vnc/passwd

#==========
# Relaxing permissions for OpenShift and other non-sudo environments
#==========
RUN sudo chmod -R 777 ${HOME} \
  && sudo chgrp -R 0 ${HOME} \
  && sudo chmod -R g=u ${HOME}

#==============================
# Scripts to run fluxbox and x11vnc
#==============================
COPY start-fluxbox.sh \
      start-vnc.sh \
      /opt/bin/


#====================================
# Scripts to run Selenium Standalone
#====================================
#COPY start-selenium-standalone.sh /opt/bin/start-selenium-standalone.sh


USER root

RUN chmod +x /opt/bin/start-fluxbox.sh
RUN chmod +x /opt/bin/start-vnc.sh

# Install chrome dependencies
COPY chrome_reqs.txt /tmp/chrome_reqs.txt
RUN apt-get install -y $(grep -vE "^\s*#" /tmp/chrome_reqs.txt  | tr "\n" " ")

# Install node dependencies
COPY node_reqs.txt /tmp/node_reqs.txt
RUN npm install $(grep -vE "^\s*#" /tmp/node_reqs.txt  | tr "\n" " ")


USER pptruser
# Copy chrome binary
ADD jsgraph /home/pptruser/chromium

#==============================
# Supervisor configuration file
#==============================
COPY display.conf /etc/supervisor/conf.d/

#COPY capture_page_load.js /home/pptruser/app

EXPOSE 4444
EXPOSE 5900


USER pptruser

WORKDIR /home/pptruser/app
