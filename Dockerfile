FROM php:8.2-apache

# تفعيل mod_rewrite
RUN a2enmod rewrite

# السماح بالـ .htaccess
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# نسخ كل الملفات
COPY . /var/www/html/

# جعل bot.php الملف الافتراضي
RUN echo "DirectoryIndex bot.php index.php index.html" > /etc/apache2/conf-available/dir.conf \
    && a2enconf dir

# صلاحيات
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
