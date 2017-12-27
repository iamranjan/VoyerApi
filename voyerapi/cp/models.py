from django.db import models
from identity.models import User
from django.contrib.postgres.fields import JSONField
import uuid


# Create your models here.
#

class CPFirewall(models.Model):
    """
    Meta data associated with FW and used for management and configuration Top level object
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gw_name = models.CharField(max_length=40)
    management_url = models.CharField(max_length=256)
    package_name = models.CharField(max_length=60)
    layer_name = models.CharField(max_length=60)


class CPUser(models.Model):
    """
    User informated related to the FW and used for API management
    """
    firewall = models.ForeignKey(CPFirewall, related_name='user', on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    management_user = models.CharField(max_length=20, default="admin")
    management_password = models.CharField(max_length=20, default="admin123")


class CPPolicy(models.Model):
    """
    Blades enabled on the firewall
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firewall = models.ForeignKey(CPFirewall, related_name='blades', on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    fw = models.BooleanField(default=True)
    anti_bot = models.BooleanField(default=True)
    anti_virus = models.BooleanField(default=True)
    application_control = models.BooleanField(default=False)
    content_awareness = models.BooleanField(default=False)
    ips = models.BooleanField(default=True)
    threat_emulation = models.BooleanField(default=False)
    url_filtering = models.BooleanField(default=False)
    vpn = models.BooleanField(default=False)


class CPNetwork(models.Model):
    """
    Networks object in firewall
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firewall = models.ForeignKey(CPFirewall, related_name='networks', on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    subnet = models.CharField(max_length=60)
    subnet_mask = models.CharField(max_length=60)


class CPHost(models.Model):
    """
    Host Object in firewall
    """
    access_rule = models.ForeignKey(CPFirewall, default=uuid.uuid4, related_name='access_rule', on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firewall = models.ForeignKey(CPFirewall, related_name='hosts', on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    ip_address = models.CharField(max_length=60)


class CPGroup(models.Model):
    """
    Group Object in firewall
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firewall = models.ForeignKey(CPFirewall, related_name='groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    members = models.CharField(max_length=256)


class CPService(models.Model):
    """
    Group Object in firewall
    """
    firewall = models.ForeignKey(CPFirewall, related_name='service', on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=60)
    port = models.CharField(max_length=10)


class CPSecurityPolicy(models.Model):
    """
    Firewall Security Policy
    """


class CPAccessLayer(models.Model):
    """
    Firewall Security Policy
    """
    firewall = models.ForeignKey(CPFirewall, related_name='access_layers', on_delete=models.CASCADE)




class CPAccessRule(models.Model):
    """
    Access rules associated with give firewall
    """
    firewall = models.ForeignKey(CPFirewall, related_name='access_rules', on_delete=models.CASCADE)
    position = models.CharField(max_length=10, default="top")
    source = models.CharField(max_length=10, default="Any")
    destination = JSONField(default=dict())
    service = JSONField(default=dict())
    action = models.CharField(max_length=10, default="accept")
    track =models.CharField(max_length=10, default="log")



