FROM php:8.2-apache

# تفعيل mod_rewrite
RUN a2enmod rewrite

# السماح بالـ .htaccess
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# تثبيت curl
RUN apt-get update && apt-get install -y \
        libcurl4-openssl-dev \
        unzip \
    && docker-php-ext-install curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# نسخ الملفات
COPY . /var/www/html/

# الملف الافتراضي
RUN echo "DirectoryIndex index.php index.html" > /etc/apache2/conf-available/dir.conf \
    && a2enconf dir

# صلاحيات
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
