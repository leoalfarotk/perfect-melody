FROM php:7.4-fpm

RUN rm /etc/apt/preferences.d/no-debian-php && \
 apt-get update -y && apt-get install -y libpng-dev libxml2-dev libzip-dev unzip

RUN docker-php-ext-install pdo_mysql \
&& docker-php-ext-install json gd zip soap dom

RUN pecl install xdebug-2.9.6 && docker-php-ext-enable xdebug
RUN echo 'xdebug.remote_port=9000' >> /usr/local/etc/php/php.ini
RUN echo 'xdebug.remote_enable=1' >> /usr/local/etc/php/php.ini
RUN echo 'xdebug.remote_connect_back=1' >> /usr/local/etc/php/php.ini
RUN echo 'memory_limit=1024M' >> /usr/local/etc/php/php.ini
RUN echo 'upload_max_filesize=100M' >> /usr/local/etc/php/php.ini
RUN echo 'post_max_size=100M' >> /usr/local/etc/php/php.ini

RUN apt-get install -y git
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Replace shell with bash so we can source files
#RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Set debconf to run non-interactively
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install base dependencies
RUN apt-get update && apt-get install -y -q --no-install-recommends \
        apt-transport-https \
        build-essential \
	libssl-dev \
        curl \
        git \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update -y && apt-get -y install python3.7 python3-distutils libsndfile1 python3-venv python3-dev
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.7 get-pip.py && rm get-pip.py