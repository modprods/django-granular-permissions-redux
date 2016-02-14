from django import VERSION
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib import admin

from django.db.models import Q

import inspect

class MetaClass(type):
    def __new__(self, classname, classbases, classdict):
        try:
            frame = inspect.currentframe()
            frame = frame.f_back
            if frame.f_locals.has_key(classname):
                old_class = frame.f_locals.get(classname)
                for name,func in classdict.items():
                    if inspect.isfunction(func):
                        setattr(old_class, name, func)
                return old_class
            return type.__new__(self, classname, classbases, classdict)
        finally:
            del frame

class MetaObject(object):
    __metaclass__ = MetaClass
            
class User(MetaObject):
    def add_row_perm(self, instance, perm):
        if self.has_row_perm(instance, perm, True):
            return False
        permission = Permission()
        permission.content_object = instance
        permission.user = self
        permission.name = perm
        permission.save()
        return True
        
    def del_row_perm(self, instance, perm):
        if not self.has_row_perm(instance, perm, True):
            return False
        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(user=self, content_type__pk=content_type.id, object_id=instance.id, name=perm)
        objects.delete()
        return True
        
    def has_row_perm(self, instance, perm, only_me=False):
        if self.is_superuser:
            return True
        if not self.is_active:
            return False

        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(user=self, content_type__pk=content_type.id, object_id=instance.id, name=perm)
        if objects.count()>0:
            return True
            
        # check groups
        if not only_me:
            for group in self.groups.all():
                if group.has_row_perm(instance, perm):
                    return True
        return False
        
    def get_rows_with_permission(self, instance, perm):
        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(Q(user=self) | Q(group__in=self.groups.all()), content_type__pk=content_type.id, name=perm)
        return objects
        
            
class Group(MetaObject):
    def add_row_perm(self, instance, perm):
        if self.has_row_perm(instance, perm):
            return False
        permission = Permission()
        permission.content_object = instance
        permission.group = self
        permission.name = perm
        permission.save()
        return True
        
    def del_row_perm(self, instance, perm):
        if not self.has_row_perm(instance, perm):
            return False
        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(user=self, content_type__pk=content_type.id, object_id=instance.id, name=perm)
        objects.delete()
        return True
        
    def has_row_perm(self, instance, perm):
        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(group=self, content_type__pk=content_type.id, object_id=instance.id, name=perm)
        if objects.count()>0:
            return True
        else:
            return False
            
    def get_rows_with_permission(self, instance, perm):
        content_type = ContentType.objects.get_for_model(instance)
        objects = Permission.objects.filter(group=self, content_type__pk=content_type.id, name=perm)
        return objects
        
        
if VERSION[0]=='newforms-admin' or VERSION[0]>0:
    class Permission(models.Model):
        name = models.CharField(max_length=16)
        content_type = models.ForeignKey(ContentType, related_name="row_permissions")
        object_id = models.PositiveIntegerField()
        content_object = GenericForeignKey('content_type', 'object_id')
        user = models.ForeignKey(User, null=True)
        group = models.ForeignKey(Group, null=True)
        
        class Meta:
		app_label = 'django_granular_permissions'            
		verbose_name = 'permission'
            	verbose_name_plural = 'permissions'
            
            
    class PermissionAdmin(admin.ModelAdmin):
        model = Permission
        list_display = ('content_type', 'user', 'group', 'name')
        list_filter = ('name',)
        search_fields = ['object_id', 'content_type', 'user', 'group']
        raw_id_fields = ['user', 'group']
        
        def __unicode__(self):
            return u"%s | %s | %d | %s" % (self.content_type.app_label, self.content_type, self.object_id, self.name)
    
    admin.site.register(Permission, PermissionAdmin)
else:
    class Permission(models.Model):
        name = models.CharField(max_length=16)
        content_type = models.ForeignKey(ContentType, related_name="row_permissions")
        object_id = models.PositiveIntegerField()
        content_object = GenericForeignKey('content_type', 'object_id')
        user = models.ForeignKey(User, null=True, blank=True, raw_id_admin=True)
        group = models.ForeignKey(Group, null=True, blank=True, raw_id_admin=True)

        class Admin:
            list_display = ('content_type', 'user', 'group', 'name')
            list_filter = ('name',)
            search_fields = ['object_id', 'content_type', 'user', 'group']
        
        class Meta:
            app_label = 'django_granular_permissions'
            verbose_name = 'permission'
            verbose_name_plural = 'permissions'
        
        def __unicode__(self):
            return u"%s | %s | %d | %s" % (self.content_type.app_label, self.content_type, self.object_id, self.name)
 
