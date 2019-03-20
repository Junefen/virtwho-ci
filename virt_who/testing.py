from virt_who import *
from virt_who.base import Base
from virt_who.register import Register
from virt_who.provision import Provision

class Testing(Provision):
    def ssh_host(self):
        host_ip = config.virtwho.host_ip
        host_user = config.virtwho.host_user
        host_passwd = config.virtwho.host_passwd
        ssh_host = {"host":host_ip,"username":host_user,"password":host_passwd}
        return ssh_host

    def ssh_guest(self):
        guest_ip = config.hypervisor.guest_ip 
        guest_user = config.hypervisor.guest_user 
        guest_passwd = config.hypervisor.guest_passwd 
        ssh_guest = {"host":guest_ip,"username":guest_user,"password":guest_passwd}
        return ssh_guest

    def get_hypervisor_config(self):
        hypervisor_type = config.hypervisor.type
        server = config.hypervisor.server
        username = config.hypervisor.server_username
        password = config.hypervisor.server_password
        ssh_user = config.hypervisor.server_ssh_user
        ssh_passwd = config.hypervisor.server_ssh_passwd
        guest_name = config.hypervisor.guest_name 
        if server is not None and "//" in server:
            server_ip = self.get_url_domain(server)
        else:
            server_ip = server
        ssh_hypervisor = {"host":server_ip,"username":username,"password":password}
        if "libvirt-remote" in hypervisor_type:
            self.ssh_no_passwd_access(self.ssh_host(), ssh_hypervisor)
        if "libvirt-local" in hypervisor_type:
            ssh_hypervisor = self.ssh_host()
        if "rhevm" in hypervisor_type or "vdsm" in hypervisor_type:
            ssh_hypervisor = {"host":server_ip,"username":ssh_user,"password":ssh_passwd}
            if "//" not in server:
                server = self.rhevm_admin_get(ssh_hypervisor)
        if "esx" in hypervisor_type:
            ssh_hypervisor = {"host":server_ip,"username":ssh_user,"password":ssh_passwd}
        configs = {
                'type':hypervisor_type,
                'server':server,
                'username':username,
                'password':password,
                'guest_name':guest_name,
                'ssh_hypervisor':ssh_hypervisor,}
        return configs

    def get_register_config(self):
        register_type = config.register.type
        server = config.register.server
        ssh_user = config.register.ssh_user
        ssh_passwd = config.register.ssh_passwd
        vdc = config.manifest.vdc
        vdc_bonus = config.manifest.vdc_bonus
        instance = config.manifest.instance
        limit = config.manifest.limit
        unlimit = config.manifest.unlimit
        if "stage" in register_type:
            api = "https://{0}/subscription".format(server)
            ssh_sat = ""
        if "satellite" in register_type:
            api = "https://{0}".format(server)
            ssh_sat = {"host": server,"username":ssh_user,"password":ssh_passwd}
        if not vdc:
            vdc = "RH00002"
        if not vdc_bonus:
            vdc_bonus = "RH00050"
        if not instance:
            instance = "RH00003"
        if not limit:
            limit = "RH00204"
        if not unlimit:
            unlimit = "RH00060"
        configs = {
                'type':register_type,
                'server':server,
                'username':config.register.admin_user,
                'password':config.register.admin_passwd,
                'owner':config.register.owner,
                'env':config.register.env,
                'ssh_user': ssh_user,
                'ssh_passwd':ssh_passwd,
                'api':api,
                'ssh_sat':ssh_sat,
                'vdc':vdc,
                'vdc_bonus':vdc_bonus,
                'instance':instance,
                'limit':limit,
                'unlimit':unlimit}
        return configs

    def get_hypervisor_hostname(self):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        guest_name = config['guest_name']
        if hypervisor_type == "esx":
            cert = self.vcenter_cert(config['server'], config['username'], config['password'])
            esx_host = self.vcenter_host_get(cert, ssh_hypervisor, guest_name)
            hostname = self.vcenter_hostname_get(cert, ssh_hypervisor, esx_host)
        elif hypervisor_type == "hyperv":
            hostname = self.hyperv_host_name(ssh_hypervisor)
        elif hypervisor_type == "xen":
            hostname = self.get_hostname(ssh_hypervisor)
        elif hypervisor_type == "rhevm":
            rhevm_shell, rhevm_shellrc = self.rhevm_shell_get(ssh_hypervisor)
            hostname = self.rhevm_host_name_by_guestname(ssh_hypervisor, rhevm_shell, guest_name)
        elif hypervisor_type == "vdsm":
            hostname = self.get_hostname(self.ssh_host())
        elif hypervisor_type == "libvirt-local":
            hostname = self.get_hostname(self.ssh_host())
        elif hypervisor_type == "libvirt-remote":
            hostname = self.get_hostname(ssh_hypervisor)
        else:
            hostname = "unsupport hypervisor type"
        return hostname

    def get_hypervisor_hostuuid(self):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        guest_name = config['guest_name']
        if hypervisor_type == "esx":
            cert = self.vcenter_cert(config['server'], config['username'], config['password'])
            esx_host = self.vcenter_host_get(cert, ssh_hypervisor, guest_name)
            uuid = self.vcenter_host_uuid(cert, ssh_hypervisor, esx_host)
        elif hypervisor_type == "hyperv":
            uuid = self.hyperv_host_uuid(ssh_hypervisor)
        elif hypervisor_type == "xen":
            uuid = self.xen_host_uuid(ssh_hypervisor)
        elif hypervisor_type == "rhevm" or hypervisor_type == "vdsm":
            rhevm_shell, rhevm_shellrc = self.rhevm_shell_get(ssh_hypervisor)
            uuid = self.rhevm_host_uuid_by_guestname(ssh_hypervisor, rhevm_shell, guest_name)
        elif hypervisor_type == "libvirt-local":
            uuid = self.libvirt_host_uuid(self.ssh_host())
        elif hypervisor_type == "libvirt-remote":
            uuid = self.libvirt_host_uuid(ssh_hypervisor)
        else:
            uuid = "unsupport hypervisor type"
        return uuid

    def get_hypervisor_hwuuid(self):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        guest_name = config['guest_name']
        if hypervisor_type == "esx":
            cert = self.vcenter_cert(config['server'], config['username'], config['password'])
            esx_host = self.vcenter_host_get(cert, ssh_hypervisor, guest_name)
            hwuuid = self.vcenter_host_hwuuid(cert, ssh_hypervisor, esx_host)
        elif hypervisor_type == "rhevm":
            rhevm_shell, rhevm_shellrc = self.rhevm_shell_get(ssh_hypervisor)
            host_uuid = self.rhevm_host_uuid_by_guestname(ssh_hypervisor, rhevm_shell, guest_name)
            hwuuid = self.rhevm_host_hwuuid_by_uuid(ssh_hypervisor, rhevm_shell, host_uuid)
        else:
            hwuuid = "unsupported hypervisor type"
        return hwuuid
        
    def get_hypervisor_guestuuid(self):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        guest_name = config['guest_name']
        if hypervisor_type == "esx":
            cert = self.vcenter_cert(config['server'], config['username'], config['password'])
            uuid = self.vcenter_guest_uuid(cert, ssh_hypervisor, guest_name)
        elif hypervisor_type == "hyperv":
            uuid = self.hyperv_guest_uuid(ssh_hypervisor, guest_name)
        elif hypervisor_type == "xen":
            uuid = self.xen_guest_uuid(ssh_hypervisor, guest_name)
        elif hypervisor_type == "rhevm" or hypervisor_type == "vdsm":
            rhevm_shell, rhevm_shellrc = self.rhevm_shell_get(ssh_hypervisor)
            uuid = self.rhevm_guest_uuid(ssh_hypervisor, rhevm_shell, guest_name)
        elif hypervisor_type == "libvirt-local":
            uuid = self.libvirt_guest_uuid(guest_name, self.ssh_host())
        elif hypervisor_type == "libvirt-remote":
            uuid = self.libvirt_guest_uuid(guest_name, ssh_hypervisor)
        else:
            uuid = "unsupport hypervisor type"
        return uuid

    def hypervisor_guest_start(self):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        guest_name = config['guest_name']
        if hypervisor_type == "esx":
            cert = self.vcenter_cert(config['server'], config['username'], config['password'])
            guest_ip = self.vcenter_guest_start(cert, ssh_hypervisor, guest_name)
        elif hypervisor_type == "hyperv":
            guest_ip = self.hyperv_guest_start(ssh_hypervisor, guest_name)
        elif hypervisor_type == "xen":
            guest_ip =  self.xen_guest_start(ssh_hypervisor, guest_name)
        elif hypervisor_type == "libvirt-local":
            guest_ip = self.libvirt_guest_start(guest_name, self.ssh_host())
        elif hypervisor_type == "libvirt-remote":
            guest_ip = self.libvirt_guest_start(guest_name, ssh_hypervisor)
        else:
            raise FailException("Unsupported to start guest for hypervisor_type:{0}".format(hypervisor_type))
        self.set_exported_param("GUEST_IP", guest_ip)
        logger.info("Successed to start guest for mode %s, guest ip: %s" % (hypervisor_type, guest_ip))

    def hypervisor_guest_stop(self):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        guest_name = config['guest_name']
        if hypervisor_type == "esx":
            cert = self.vcenter_cert(config['server'], config['username'], config['password'])
            self.vcenter_guest_stop(cert, ssh_hypervisor, guest_name)
        elif hypervisor_type == "hyperv":
            self.hyperv_guest_stop(ssh_hypervisor, guest_name)
        elif hypervisor_type == "xen":
            self.xen_guest_stop(ssh_hypervisor, guest_name)
        elif hypervisor_type == "libvirt-local":
            self.libvirt_guest_stop(guest_name, self.ssh_host())
        elif hypervisor_type == "libvirt-remote":
            self.libvirt_guest_stop(guest_name, ssh_hypervisor)
        else:
            raise FailException("Unsupported to stop guest for mode: {0}".format(hypervisor_type))
        logger.info("Successed to stop guest for mode {0}".format(hypervisor_type))

    def hypervisor_guest_suspend(self):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        guest_name = config['guest_name']
        if hypervisor_type == "esx":
            cert = self.vcenter_cert(config['server'], config['username'], config['password'])
            self.vcenter_guest_suspend(cert, ssh_hypervisor, guest_name)
        elif hypervisor_type == "hyperv":
            self.hyperv_guest_suspend(ssh_hypervisor, guest_name)
        elif hypervisor_type == "xen":
            self.xen_guest_suspend(ssh_hypervisor, guest_name)
        elif hypervisor_type == "libvirt-local":
            self.libvirt_guest_suspend(guest_name, self.ssh_host())
        elif hypervisor_type == "libvirt-remote":
            self.libvirt_guest_suspend(guest_name, ssh_hypervisor)
        else:
            raise FailException("Unsupported to suspend guest for mode: {0}".format(hypervisor_type))
        logger.info("Successed to suspend guest for mode {0}".format(hypervisor_type))

    def hypervisor_guest_resume(self):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        guest_name = config['guest_name']
        if hypervisor_type == "esx":
            cert = self.vcenter_cert(config['server'], config['username'], config['password'])
            self.vcenter_guest_resume(cert, ssh_hypervisor, guest_name)
        elif hypervisor_type == "hyperv":
            self.hyperv_guest_resume(ssh_hypervisor, guest_name)
        elif hypervisor_type == "xen":
            self.xen_guest_resume(ssh_hypervisor, guest_name)
        elif hypervisor_type == "libvirt-local":
            self.libvirt_guest_resume(guest_name, self.ssh_host())
        elif hypervisor_type == "libvirt-remote":
            self.libvirt_guest_resume(guest_name, ssh_hypervisor)
        else:
            raise FailException("Unsupported to resume guest for mode: {0}".format(hypervisor_type))
        logger.info("Successed to resume guest for mode {0}".format(hypervisor_type))

    def hypervisor_firewall_setup(self, action="on"):
        config = self.get_hypervisor_config()
        hypervisor_type = config['type']
        ssh_hypervisor = config['ssh_hypervisor']
        ssh_host = self.ssh_host()
        host = ssh_host['host']
        if ":" in host:
            var = host.split(':')
            host = var[0]
        if hypervisor_type == "rhevm" \
                or hypervisor_type == "libvirt-remote" \
                or hypervisor_type == "xen":
            if action == "off":
                cmd = "iptables -I INPUT -s {0} -j DROP".format(host)
            if action == "on":
                cmd = "iptables -D INPUT -s {0} -j DROP".format(host)
            ret, output = self.runcmd(cmd, ssh_hypervisor)
        if hypervisor_type == "esx" or hypervisor_type == "hyperv":
            if action == "off":
                cmd1 = "NetSh Advfirewall set allprofiles state on"
                cmd2 = r'netsh advfirewall firewall add rule name="BLOCKED IP" interface=any dir=in action=block remoteip={0}'.format(host)
            if action == "on":
                cmd1 = r'netsh advfirewall firewall delete rule name="BLOCKED IP" remoteip={0}'.format(host)
                cmd2 = "NetSh Advfirewall set allprofiles state off"
            ret, output = self.runcmd(cmd1, ssh_hypervisor)
            ret, output = self.runcmd(cmd2, ssh_hypervisor)

    #******************************************
    # virt-who config function
    #******************************************
    def vw_case_info(self, case_name, case_id=None):
        logger.info("+"*30)
        logger.info(case_name)
        if case_id:
            polarion_baseurl = "https://polarion.engineering.redhat.com/polarion/redirect/project"
            polarion_workitem = "%s/RedHatEnterpriseLinux7/workitem?id=%s" % (polarion_baseurl, case_id)
            logger.info(polarion_workitem)

    def vw_case_skip(self, skip_reason=None):
        try:
            self.skipTest(skip_reason)
        except Exception, SkipTest:
            logger.info(str(SkipTest))
            raise SkipTest
        finally:
            logger.info("Successed to skip case")

    def vw_case_result(self, results, notes=None):
        for key, value in results.items():
            if False in value:
                logger.error('Failed step: {0}'.format(key))
                print 'Failed step: {0}'.format(key)
        if notes is not None:
            for msg in notes:
                logger.warning(msg)
                print msg
        if any(False in res for res in results.values()):
            raise FailException("Failed to run case, please check the failed steps\n")
        else:
            logger.info("Successed to run case, all steps passed\n")

    def vw_case_init(self):
        hypervisor_config = self.get_hypervisor_config()
        register_config = self.get_register_config()
        hypervisor_type = hypervisor_config['type']
        ssh_hypervisor = hypervisor_config['ssh_hypervisor']
        register_type = register_config['type']
        if "vdsm" in hypervisor_type or "rhevm" in hypervisor_type:
            cmd = "ovirt-aaa-jdbc-tool user unlock admin"
            self.runcmd(cmd, ssh_hypervisor)
        if self.system_isregister(self.ssh_host(), register_type, register_config) is False:
            self.system_register(self.ssh_host(), register_type, register_config)
        if self.system_isregister(self.ssh_guest(), register_type, register_config) is False:
            self.system_register(self.ssh_guest(), register_type, register_config)
        if self.system_sku_unattach(self.ssh_host()) is False:
            self.system_register(self.ssh_host(), register_type, register_config)
        if self.system_sku_unattach(self.ssh_guest()) is False:
            self.system_register(self.ssh_guest(), register_type, register_config)
        self.vw_etc_conf_disable_all()
        self.vw_etc_sys_disable_all()
        self.vw_etc_d_delete_all()

    def vw_hypervisor_event(self, event):
        if event == "guest_suspend":
            self.hypervisor_guest_suspend()
        elif event == "guest_resume":
            self.hypervisor_guest_resume()
        elif event == "guest_stop":
            self.hypervisor_guest_stop()
        elif event == "guest_start":
            self.hypervisor_guest_start()
        else:
            raise FailException("Unsupported hypervisor event")

    def vw_etc_conf_disable_all(self):
        op_1 = '-e "/;/d"'
        op_2 = '-e "s|^[^#]|#&|g"'
        cmd = 'sed -i %s %s /etc/virt-who.conf' % (op_1, op_2)
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret != 0:
            raise FailException("Failed to disable all options in /etc/virt-who.conf")
        else:
            logger.info("Successed to disable all options in /etc/virt-who.conf")

    def vw_etc_sys_disable_all(self):
        op_1 = '-e "s|^[^#]|#&|g"'
        cmd = 'sed -i %s /etc/sysconfig/virt-who' % op_1
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret != 0:
            raise FailException("Failed to disable all modes in /etc/sysconfig/virt-who")
        else:
            logger.info("Successed to disable all options in /etc/sysconfig/virt-who")

    def vw_etc_d_delete_all(self):
        cmd = "rm -rf /etc/virt-who.d/*; rm -f /etc/virt-who.d/.*swp"
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret != 0:
            raise FailException("Failed to delete all files in /etc/virt-who.d/")
        else:
            logger.info("Successed to delete all files in /etc/virt-who.d/")

    def vw_etc_sys_mode_enable(self):
        filename = "/etc/sysconfig/virt-who"
        hypervisor_config = self.get_hypervisor_config()
        register_config = self.get_register_config()
        mode = hypervisor_config['type']
        server = hypervisor_config['server']
        username = hypervisor_config['username']
        password = hypervisor_config['password']
        owner = register_config['owner']
        env = register_config['env']
        mode = mode.upper()
        if mode == "LIBVIRT-REMOTE":
            mode = "LIBVIRT"
        if mode == "LIBVIRT-LOCAL":
            logger.info("libvirt local mode is default")
        elif mode == "VDSM":
            cmd = 'sed -i -e "s|.*VIRTWHO_VDSM=.*|VIRTWHO_VDSM=1|g" {0}'.format(filename)
            ret, output = self.runcmd(cmd, self.ssh_host())
        else:
            op_1 = '-e "s|.*{0}=.*|VIRTWHO_{0}=1|g"'.format(mode)
            op_2 = '-e "s|.*{0}_OWNER=.*|VIRTWHO_{0}_OWNER={1}|g"'.format(mode, owner)
            op_3 = '-e "s|.*{0}_ENV=.*|VIRTWHO_{0}_ENV={1}|g"'.format(mode, env) 
            op_4 = '-e "s|.*{0}_SERVER=.*|VIRTWHO_{0}_SERVER={1}|g"'.format(mode, server)
            op_5 = '-e "s|.*{0}_USERNAME=.*|VIRTWHO_{0}_USERNAME={1}|g"'.format(mode, username) 
            op_6 = '-e "s|.*{0}_PASSWORD=.*|VIRTWHO_{0}_PASSWORD={1}|g"'.format(mode, password)
            cmd = 'sed -i {0} {1} {2} {3} {4} {5} {6}'.format(op_1, op_2, op_3, op_4, op_5, op_6, filename)
            ret, output = self.runcmd(cmd, self.ssh_host())
            if ret != 0:
                raise FailException("Failed to enable mode {0} in /etc/sysconfig/virt-who".format(mode))
            else:
                logger.info("Successed to enable mode {0} in /etc/sysconfig/virt-who".format(mode))

    def vw_etc_d_mode_create(self, config_name, config_file):
        hypervisor_config = self.get_hypervisor_config()
        register_config = self.get_register_config()
        mode = hypervisor_config['type']
        server = hypervisor_config['server']
        username = hypervisor_config['username']
        password = hypervisor_config['password']
        owner = register_config['owner']
        env = register_config['env']
        mode = mode.lower()
        if mode == "libvirt-remote":
            mode = "libvirt"
        if mode == "libvirt-local":
            logger.info("local libvirt mode is default")
        elif mode == "vdsm":
            cmd = "echo -e '[{0}]\ntype={1}' > {2}".format(config_name, mode, config_file)
            ret, output = self.runcmd(cmd, self.ssh_host())
        else:
            cmd = ('cat <<EOF > {0}\n'
                    '[{1}]\n'
                    'type={2}\n'
                    'server={3}\n'
                    'username={4}\n'
                    'password={5}\n'
                    'owner={6}\n'
                    'env={7}\n'
                    'EOF'
                  ).format(config_file, config_name, mode, server, username, password, owner, env)
            ret, output = self.runcmd(cmd, self.ssh_host())
            if ret != 0:
                raise FailException("Failed to create config file {0}".format(config_file))
            else:
                logger.info("Successed to create config file {0}".format(config_file))

    def vw_fake_json_create(self, cli, json_file):
        self.vw_stop()
        cmd ="{0} -p -d > {1}".format(cli, json_file)
        ret, output = self.runcmd(cmd, self.ssh_host())
        ret, output = self.runcmd("cat {0}".format(json_file), self.ssh_host())
        logger.info(output)
        if "guestId" not in output:
            raise FailException("Failed to create json data: {0}".format(json_file))
        logger.info("Successed to create json data: {0}".format(json_file))

    def vw_fake_conf_create(self, conf_file, json_file, is_hypervisor=True):
        register_config = self.get_register_config()
        owner = register_config['owner']
        env = register_config['env']
        cmd = ('cat <<EOF > {0}\n'
                '[fake]\n'
                'type=fake\n'
                'file={1}\n'
                'is_hypervisor={2}\n'
                'owner={3}\n'
                'env={4}\n'
                'EOF'
              ).format(conf_file, json_file, is_hypervisor, owner, env)
        ret, output = self.runcmd(cmd, self.ssh_host())
        ret, output = self.runcmd("ls {0}".format(conf_file), self.ssh_host())
        if ret != 0 :
            raise FailException("Failed to create fake config file: {0}".format(conf_file))
        logger.info("Successed to create fake config file: {0}".format(conf_file))

    def vw_option_update_name(self, option, rename, filename):
        option = self.shell_escape_char(option)
        rename = self.shell_escape_char(rename)
        cmd = 'sed -i "s|^%s|%s|g" %s' % (option, rename, filename)
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret == 0:
            logger.info("Successed to update option name %s to %s" % (option, rename))
        else:
            raise FailException("Failed to update option name %s to %s" % (option, rename))

    def vw_option_update_value(self, option, value, filename):
        option = self.shell_escape_char(option)
        value = self.shell_escape_char(value)
        cmd = 'sed -i "s|^%s.*|%s=%s|g" %s' % (option, option, value, filename)
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret == 0:
            logger.info("Successed to set option %s value to %s" % (option, value))
        else:
            raise FailException("Failed to set option %s value to %s" % (option, value))

    def vw_option_enable(self, option, filename):
        option = self.shell_escape_char(option)
        op_1 = '-e "s|^#%s$|%s|g"' % (option, option)
        op_2 = '-e "s|^#%s=|%s=|g"' % (option, option)
        op_3 = '-e "s|^# %s$|%s|g"' % (option, option)
        op_4 = '-e "s|^# %s=|%s=|g"' % (option, option)
        cmd = 'sed -i %s %s %s %s %s' % (op_1, op_2, op_3, op_4, filename)
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret == 0:
            logger.info("Successed to enable option %s" % option)
        else:
            raise FailException("Failed to enable option %s" % option)

    def vw_option_disable(self, option, filename):
        option = self.shell_escape_char(option)
        cmd = 'sed -i "s|^%s|#%s|g" %s' % (option, option, filename) 
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret == 0:
            logger.info("Successed to disable option %s" % option)
        else:
            raise FailException("Failed to disable option %s" % option)

    def vw_option_add(self, option, value, filename):
        cmd = 'echo "%s=%s" >> %s' % (option, value, filename)
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret == 0:
            logger.info("Successed to add option %s=%s" % (option, value))
        else:
            raise FailException("Failed to add option %s=%s" % (option, value))

    def vw_option_del(self, option, filename):
        option = self.shell_escape_char(option)
        cmd = 'sed -i "/^%s/d" %s; sed -i "/^#%s/d" %s' % (option, filename, option, filename)
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret == 0:
            logger.info("Successed to delete option %s" % option)
        else:
            raise FailException("Failed to delete option %s" % option)

    def vw_option_get(self, option, filename):
        cmd = "grep -v '^#' %s |grep ^%s" % (filename, option)
        ret, output = self.runcmd(cmd, self.ssh_host())
        if ret == 0 and option in output:
            value = output.split('=')[1].strip()
            return value
        else:
            raise FailException("No this option or option is not enabled")

    def vw_cli_base(self):
        hypervisor_config = self.get_hypervisor_config()
        register_config = self.get_register_config()
        mode = hypervisor_config['type']
        server = hypervisor_config['server']
        username = hypervisor_config['username']
        password = hypervisor_config['password']
        owner = register_config['owner']
        env = register_config['env']
        mode = mode.lower()
        if mode == "libvirt-remote":
            mode = "libvirt"
        if mode == "libvirt-local" or mode == "" or mode is None: 
            cmd = "virt-who "
        elif mode == "vdsm":
            cmd = "virt-who --vdsm "
        else:
            op_1 = "--{0}".format(mode)
            op_2 = "--{0}-owner={1}".format(mode, owner)
            op_3 = "--{0}-env={1}".format(mode, env)
            op_4 = "--{0}-server={1}".format(mode, server)
            op_5 = "--{0}-username={1}".format(mode, username)
            op_6 = "--{0}-password={1}".format(mode, password)
            cmd = "virt-who {0} {1} {2} {3} {4} {5}".format(op_1, op_2, op_3, op_4, op_5, op_6)
        return cmd

    def vw_cli_base_update(self, cmd, pattern, new_str):
        pattern = r"%s?(?= )" % pattern
        cmd = re.sub(pattern, new_str, cmd)
        return cmd

    def vw_service_status(self):
        ret, output = self.run_service(self.ssh_host(), "virt-who", "status")
        if output is not None and output != "":
            if "is stopped" in output or "Active: inactive (dead)" in output:
                status = "stopped"
            elif "is running" in output or "Active: active (running)" in output:
                status = "running"
            else:
                status = "unknown"
            logger.info("virt-who status is: %s" % status)
            return status
        else:
            raise FailException("Failed to check virt-who status")

    def vw_async_log(self, data, rhsm_output):
        orgs = re.findall(r"Host-to-guest mapping being sent to '(.*?)'", rhsm_output)
        if len(orgs) > 0: 
            data['orgs'] = orgs
            org_data = dict()
            for org in orgs:
                key = "Host-to-guest mapping being sent to '%s'" % org
                rex = re.compile(r'(?<=: ){.*?}\n+(?=201|$)', re.S)
                mapping_info = rex.findall(rhsm_output)[-1]
                try:
                    mapping_info = json.loads(mapping_info.replace('\n', ''), strict=False)
                except:
                    logger.warning("Failed to run json.loads for rhsm.log")
                    return data
                hypervisors = mapping_info['hypervisors']
                org_data["hypervisor_num"] = len(hypervisors)
                for item in hypervisors:
                    hypervisorId =  item['hypervisorId']['hypervisorId']
                    if item.has_key('name'):
                        hypervisor_name =  item['name']
                    else:
                        hypervisor_name = ""
                    facts = dict()
                    facts['name'] = hypervisor_name
                    facts['type'] = item['facts']['hypervisor.type']
                    facts['version'] = item['facts']['hypervisor.version']
                    facts['socket'] = item['facts']['cpu.cpu_socket(s)']
                    guests = list()
                    for guest in item['guestIds']:
                        guestId = guest['guestId']
                        guests.append(guestId)
                        attr = dict()
                        attr['guest_hypervisor'] = hypervisorId
                        attr['state'] = guest['state']
                        attr['active'] = guest['attributes']['active']
                        attr['type'] = guest['attributes']['virtWhoType']
                        org_data[guestId] = attr
                    facts['guests'] = guests
                    org_data[hypervisorId] = facts
                data[org] = org_data
        return data

    def vw_unasync_log(self, data, rhsm_output):
        orgs = re.findall(r"Host-to-guest mapping being sent to '(.*?)'", rhsm_output)
        if len(orgs) > 0: 
            data['orgs'] = orgs
            org_data = dict()
            for org in orgs:
                key = "Host-to-guest mapping being sent to '%s'" % org
                rex = re.compile(r'(?<=: ){.*?}\n+(?=201|$)', re.S)
                mapping_info = rex.findall(rhsm_output)[-1]
                try:
                    mapping_info = json.loads(mapping_info.replace('\n', ''), strict=False)
                except:
                    logger.warning("json.loads failed: %s" % mapping_info)
                    return data
                org_data['hypervisor_num'] = len(mapping_info.keys())
                for hypervisor_id, hypervisors_data in mapping_info.items():
                    facts = dict()
                    guests = list()
                    for guest in hypervisors_data:
                        guestId = guest['guestId']
                        guests.append(guestId)
                        attr = dict()
                        attr['guest_hypervisor'] = hypervisor_id
                        attr['state'] = guest['state']
                        attr['active'] = guest['attributes']['active']
                        attr['type'] = guest['attributes']['virtWhoType']
                        org_data[guestId] = attr
                    facts['guests'] = guests
                    org_data[hypervisor_id] = facts
                data[org] = org_data
        return data

    def vw_local_mode_log(self, data, rhsm_output):
        key = "Domain info:"
        rex = re.compile(r'(?<=Domain info: )\[.*?\]\n+(?=201|$)', re.S)
        mapping_info = rex.findall(rhsm_output)[-1]
        try:
            mapping_info = json.loads(mapping_info.replace('\n', ''), strict=False)
        except:
            logger.warning("json.loads failed: %s" % mapping_info)
            return data
        for item in mapping_info:
            guestId = item['guestId']
            attr = dict()
            attr['state'] = item['state']
            attr['active'] = item['attributes']['active']
            attr['type'] = item['attributes']['virtWhoType']
            data[guestId] = attr
        return data

    def vw_log_analyzer(self, data, tty_output, rhsm_output):
        if "virtwho.main DEBUG" in rhsm_output and \
                ("Domain info:" in rhsm_output or "Host-to-guest mapping being sent to" in rhsm_output):
            res = re.findall(r"reporter_id='(.*?)'", rhsm_output)
            if len(res) > 0:
                reporter_id = res[0].strip()
                data['reporter_id'] = reporter_id
            res = re.findall(r"Starting infinite loop with(.*?)seconds interval", rhsm_output)
            if len(res) > 0: 
                interval_time = res[0].strip()
                data['interval_time'] = int(interval_time)
            if "Domain info:" in rhsm_output:
                data = self.vw_local_mode_log(data, rhsm_output)
            res = re.findall(r"Server has capability '(.*?)'", rhsm_output)
            if len(res) > 0:
                is_async = res[0].strip()
                data['is_async'] = is_async
                data = self.vw_async_log(data, rhsm_output)
            else:
                data['is_async'] = "not_async"
                data = self.vw_unasync_log(data, rhsm_output)
        return data

    def vw_callback_loop_num(self):
        key= ""; loop_num = 0
        cmd = "grep 'Report for config' /var/log/rhsm/rhsm.log |grep 'placing in datastore' | head -1"
        ret, output = self.runcmd(cmd, self.ssh_host(), desc="virt-who placing number check")
        keys = re.findall(r'Report for config "(.*?)"', output)
        if output is not None and output != "" and len(keys) > 0:
            key = "Report for config \"%s\" gathered, placing in datastore" % keys[0]
            cmd = "grep '%s' /var/log/rhsm/rhsm.log | wc -l" % key
            ret, output = self.runcmd(cmd, self.ssh_host(), desc="virt-who placing number check")
            if output is not None or output != "":
                loop_num = int(output)-1
        return key, loop_num

    def vw_callback_loop_time(self):
        loop_time = -1
        key, loop_num = self.vw_callback_loop_num()
        if loop_num != 0:
            cmd = "grep '%s' /var/log/rhsm/rhsm.log | head -2" % key
            ret, output = self.runcmd(cmd, self.ssh_host(), desc="virt-who placing number check")
            output = output.split('\n')
            if len(output) > 0:
                d1 = re.findall(r"\d{2}:\d{2}:\d{2}", output[0])[0]
                d2 = re.findall(r"\d{2}:\d{2}:\d{2}", output[1])[0]
                h,m,s = d1.strip().split(":")
                s1 = int(h) * 3600 + int(m) * 60 + int(s)
                h,m,s = d2.strip().split(":")
                s2 = int(h) * 3600 + int(m) * 60 + int(s)
                loop_time = s2-s1
        return loop_time

    def vw_rhsm_modes_check(self, rhsm_output):
        env_mode = config.hypervisor.type
        rhsm_modes = re.findall(r'Using configuration.*\("(.*?)" mode\)', rhsm_output)
        if len(rhsm_modes) == 0:
            return env_mode
        elif len(rhsm_modes) == 1 and "fake" in rhsm_modes:
            return env_mode
        elif len(rhsm_modes) == 1 and "libvirt" in rhsm_modes and 'Using libvirt url: ""' in rhsm_output:
            return "libvirt-local"
        elif len(rhsm_modes) == 1 and "vdsm" in rhsm_modes and "vdsm" in env_mode:
            return "vdsm"
        elif len(rhsm_modes) == 2 and "vdsm" in rhsm_modes[0] and "vdsm" in rhsm_modes[1] and "vdsm" in env_mode:
            return "vdsm"
        else:
            return "mix"

    def vw_callback_send_num(self):
        register_config = self.get_register_config()
        register_type = register_config['type']
        cmd = "cat /var/log/rhsm/rhsm.log"
        ret, rhsm_output = self.runcmd(cmd, self.ssh_host(), debug=False)
        if rhsm_output is None or rhsm_output == "":
            ret1, output1 = self.runcmd("ls /var/log/rhsm/virtwho/rhsm.log", self.ssh_host())
            ret2, output2 = self.runcmd("ls /var/log/rhsm/virtwho/virtwho.log", self.ssh_host())
            ret3, output3 = self.runcmd("ls /var/log/rhsm/virtwho.destination_*.log", self.ssh_host())
            if ret1 == 0:
                cmd = "cat {0}".format(output1)
            elif ret2 == 0:
                cmd = "cat {0}".format(output2)
            elif ret3 == 0:
                cmd = "cat {0}".format(output3)
            ret, rhsm_output = self.runcmd(cmd, self.ssh_host(), debug=False)
        mode_type = self.vw_rhsm_modes_check(rhsm_output)
        if "0 hypervisors and 0 guests found" in rhsm_output:
            logger.warning("virt-who send terminated because '0 hypervisors and 0 guests found'")
            msg = "0 hypervisors and 0 guests found"
        elif "virtwho.main DEBUG" in rhsm_output or "rhsm.connection DEBUG" in rhsm_output:
            if "satellite" in register_type:
                if mode_type == "libvirt-local" or mode_type == "vdsm":
                    msg = r'Response: status=200, request="PUT /rhsm/consumers'
                else:
                    msg = r'Response: status=200, request="POST /rhsm/hypervisors'
            if "stage" in register_type:
                if mode_type == "libvirt-local" or mode_type == "vdsm":
                    msg = r'Response: status=20.*requestUuid.*request="PUT /subscription/consumers'
                else:
                    msg = r'Response: status=20.*requestUuid.*request="POST /subscription/hypervisors'
        else:
            if mode_type == "libvirt-local" or mode_type == "vdsm":
                msg = r"Sending update in guests lists for config"
            else:
                msg = r"Sending updated Host-to-guest mapping to"
        res = re.findall(msg, rhsm_output, re.I)
        return len(res)

    def vw_callback_error_num(self):
        error_num = 0 
        error_list = list()
        cmd = 'grep "\[.*ERROR.*\]" /var/log/rhsm/rhsm.log |sort'
        ret, output = self.runcmd(cmd, self.ssh_host())
        if output is not None and output != "":
            error_list = output.strip().split('\n')
            error_num = len(error_list)
        return error_num, error_list

    def vw_callback_thread_num(self):
        thread_num = 0
        cmd = "ps -ef | grep virt-who -i | grep -v grep |wc -l"
        ret, output = self.runcmd(cmd, self.ssh_host())
        if output is not None and output != "":
            thread_num = int(output.strip())
        return thread_num

    def vw_callback_429_check(self):
        cmd = 'grep "status=429" /var/log/rhsm/rhsm.log |sort'
        ret, output = self.runcmd(cmd, self.ssh_host())
        if output is not None and output != "":
            return "yes"
        else:
            return "no"

    def vw_callback_pending_job(self):
        register_config = self.get_register_config()
        register_type = register_config['type']
        pending_job = list()
        if "stage" in register_type:
            cmd = "cat /var/log/rhsm/rhsm.log"
            ret, rhsm_output = self.runcmd(cmd, self.ssh_host(),debug=False)
            pending_job = re.findall(r"Job (.*?) not finished", rhsm_output)
        return pending_job

    def vw_thread_callback(self):
        pending_job = list()
        is_429 = self.vw_callback_429_check()
        error_num, error_list = self.vw_callback_error_num()
        thread_num = self.vw_callback_thread_num()
        key, loop_num = self.vw_callback_loop_num()
        loop_time = self.vw_callback_loop_time()
        send_num = self.vw_callback_send_num()
        if send_num > 0:
            pending_job = self.vw_callback_pending_job()
        logger.info("pending_job: %s, is_429: %s, loop_num: %s, loop_time: %s, send_num: %s, error_num: %s, thread_num: %s" \
                % (len(pending_job), is_429, loop_num, loop_time, send_num, error_num, thread_num))
        return pending_job, is_429, loop_num, loop_time, send_num, error_num, error_list, thread_num

    def vw_thread_timeout(self, t1, queue, timeout, exp_send, exp_loopnum, oneshot, event, exp_error):
        if event is not None:
            time.sleep(60)
            self.vw_hypervisor_event(event)
        while(t1.is_alive()):
            time.sleep(3)
        while True:
            time.sleep(6)
            ret, output = self.runcmd("ls /var/log/rhsm/", self.ssh_host())
            if ret == 0 and output is not None and output !="" \
                    and "Unable to connect to" not in output \
                    and "No such file or directory" not in output:
                break
        start=time.clock()
        while True:
            time.sleep(5)
            end=time.clock()
            spend_time = int((end-start)*10)
            pending_job, is_429, loop_num, loop_time, send_num, error_num, error_list, thread_num = self.vw_thread_callback()
            if is_429 == "yes":
                logger.info("virt-who is terminated by 429 status")
                break
            if thread_num == 0:
                logger.info("virt-who is terminated by pid exit")
                break
            if error_num != 0 and exp_error is False:
                logger.info("virt-who is terminated by error msg")
                break
            if spend_time >= timeout:
                logger.info("virt-who is terminated by timeout(10m)")
                break
            if oneshot is False:
                if send_num >= exp_send and loop_num >= exp_loopnum:
                    logger.info("virt-who is terminated by expected_send and expected_loop ready")
                    break
        data = dict()
        data['pending_job'] = pending_job
        data['is_429'] = is_429
        data['thread_num'] = thread_num
        data['error_num'] = error_num
        data['error_list'] = error_list
        data['send_num'] = send_num
        data['loop_num'] = loop_num
        data['loop_time'] = loop_time
        self.vw_stop()
        cmd = "cat /var/log/rhsm/rhsm.log"
        ret, rhsm_output = self.runcmd(cmd, self.ssh_host())
        queue.put(("rhsm_output", rhsm_output, data))

    def vw_thread_run(self, t1, queue, cli):
        while(t1.is_alive()):
            time.sleep(3)
        if cli is not None:
            logger.info("Start to run virt-who by cli: %s" % cli)
            ret, tty_output = self.runcmd(cli, self.ssh_host())
        else:
            logger.info("Start to run virt-who by service")
            ret, tty_output = self.run_service(self.ssh_host(), "virt-who", "start")
        queue.put(("tty_output", tty_output))

    def vw_thread_clean(self):
        self.vw_stop()
        cmd = "rm -rf /var/log/rhsm/*"
        ret, output = self.runcmd(cmd, self.ssh_host())

    def vw_start_thread(self, cli, timeout, exp_send, exp_loopnum, oneshot, event, exp_error):
        queue = Queue.Queue()
        results = list()
        threads = list()
        t1 = threading.Thread(target=self.vw_thread_clean, args=( ))
        threads.append(t1)
        t2 = threading.Thread(target=self.vw_thread_run, args=(t1, queue, cli))
        threads.append(t2)
        t3 = threading.Thread(target=self.vw_thread_timeout, args=(t1, queue, timeout, exp_send, exp_loopnum, oneshot, event, exp_error))
        threads.append(t3)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        while not queue.empty():
            results.append(queue.get())
        for item in results:
            if item[0] == "tty_output":
                tty_output = item[1]
            if item[0] == "rhsm_output":
                rhsm_output = item[1]
                data = item[2]
        return data, tty_output, rhsm_output

    def vw_start(self, cli=None, timeout=100, exp_send=1, exp_loopnum=0, oneshot=False, event=None, web_check=True, exp_error=False):
        for i in range(3):
            data, tty_output, rhsm_output = self.vw_start_thread(cli, timeout, exp_send, exp_loopnum, oneshot, event, exp_error)
            if data['is_429'] == "yes":
                wait_time = 60*(i+3)
                logger.warning("429 code found, try again after %s seconds..." % wait_time)
                time.sleep(wait_time)
            elif len(data['pending_job']) > 0:
                wait_time = 60*(i+1)
                logger.warning("Job is not finished, cancel it and try again after %s seconds..." % wait_time)
                self.vw_pending_job_cancel(data['pending_job'])
                time.sleep(wait_time)
            elif len(re.findall('RemoteServerException: Server error attempting a GET.*returned status 500', rhsm_output, re.I)) > 0:
                logger.warning("RemoteServerException return 500 code, restart virt-who again after 60s")
                time.sleep(60)
            else:
                logger.info("Finished to start virt-who and return log")
                data = self.vw_log_analyzer(data, tty_output, rhsm_output)
                if web_check and data['error_num'] == 0 and data['send_num'] > 0:
                    if self.vw_web_host_exist():
                        return data, tty_output, rhsm_output
                    else:
                        logger.warning("Mapping info is not sent to website, restart virt-who again after 15s")
                        time.sleep(15)
                else:
                    return data, tty_output, rhsm_output
        if data['is_429'] == "yes":
            raise FailException("Failed to due to 429 code, please check")
        elif len(data['pending_job']) > 0:
            raise FailException("Failed to due to not finished job, please check")
        else:
            logger.warning("Exception to run virt-who, please check")
            return data, tty_output, rhsm_output

    def vw_stop(self):
        ret, output = self.run_service(self.ssh_host(), "virt-who", "stop")
        if self.kill_pid_by_name(self.ssh_host(), "virt-who"):
            logger.info("Succeeded to stop and clean virt-who process")
        else:
            raise FailException("Failed to stop and clean virt-who process")

    def vw_rhsm_associate(self, data, host_uuid, guest_uuid):
        hypervisor_config = self.get_hypervisor_config()
        register_config = self.get_register_config()
        mode = hypervisor_config['type']
        owner = register_config['owner']
        if "libvirt-local" in mode or "vdsm" in mode:
            if data.has_key(guest_uuid):
                logger.info("Succeeded to check the associated info by rhsm.log")
                return True
            else:
                logger.error("Faild to check the associated info by rhsm.log")
                return False
        else:
            if data[owner].has_key(guest_uuid) and host_uuid in data[owner][guest_uuid]['guest_hypervisor']:
                logger.info("Succeeded to check the associated info by rhsm.log")
                return True
            else:
                logger.error("Faild to check the associated info by rhsm.log")
                return False

    def vw_encrypted(self, password, option=None):
        if option is None or option == "":
            attrs = ["Password:|%s" % password]
            ret, output = self.run_expect(self.ssh_host(), "virt-who-password", attrs)
            if ret == 0 and output is not None:
                encrypted_value = output.split('\n')[-1].strip()
                logger.info("Succeeded to get encrypted_password without option: %s" % encrypted_value)
                return encrypted_value
            else: raise FailException("Failed to run virt-who-password")
        else:
            cmd = "virt-who-password %s %s > /tmp/vw.log" % (option, password)
            ret, output = self.runcmd(cmd, self.ssh_host(), desc="virt-who-password to encrypted")
            if ret == 0:
                ret, output = self.runcmd("cat /tmp/vw.log", self.ssh_host())
                if output is not None and output != "":
                    encrypted_value  = output.strip()
                    logger.info("Succeeded to get encrypted_password with %s option: %s" % (option,encrypted_value))
                    return encrypted_value
                else: raise FailException("Failed to run virt-who-password")
            else: raise FailException("Failed to run virt-who-password")
    
    def vw_pending_job_cancel(self, job_ids):
        register_config = self.get_register_config()
        register_type = register_config['type']
        if "stage" in register_type:
            self.stage_job_delete(self.ssh_host(), register_config, job_ids)
        if "satellite" in register_type:
            logger.warning("not support to delete job currently")

    def vw_web_host_delete(self, host_name, host_uuid):
        register_config = self.get_register_config()
        register_type = register_config['type']
        if "stage" in register_type:
            self.stage_consumer_delete(self.ssh_host(), register_config, host_name, host_uuid)
        elif "satellite" in register_type:
            self.satellite_host_delete(self.ssh_host(), register_config, host_name, host_uuid)
        else:
            raise FailException("Unkonwn server type for web host delete")

    def vw_web_attach(self, host_name, host_uuid, pool_id, quantity=1):
        register_config = self.get_register_config()
        register_type = register_config['type']
        if "stage" in register_type:
            self.stage_consumer_attach(self.ssh_host(), register_config, host_name, host_uuid, pool_id)
        elif "satellite" in register_type:
            self.satellite_host_attach(self.ssh_host(), register_config, host_name, host_uuid, pool_id, quantity)
        else:
            raise FailException("Unkonwn server type for web attach")

    def vw_web_unattach(self, host_name, host_uuid):
        register_config = self.get_register_config()
        register_type = register_config['type']
        if "stage" in register_type:
            self.stage_consumer_unattach(self.ssh_host(), register_config, host_name, host_uuid)
        elif "satellite" in register_type:
            self.satellite_host_unattach(self.ssh_host(), register_config, host_name, host_uuid)
        else:
            raise FailException("Unkonwn server type for web unattach")

    def vw_web_associate(self, host_name, host_uuid, guest_name, guest_uuid):
        register_config = self.get_register_config()
        register_type = register_config['type']
        if "stage" in register_type:
            return self. stage_consumer_associate(self.ssh_host(), register_config, host_name, host_uuid, guest_uuid)
        elif "satellite" in register_type:
            return self.satellite_host_associate(self.ssh_host(), register_config, host_name, host_uuid, guest_name, guest_uuid)
        else:
            raise FailException("Unkonwn server type for web associate")

    def vw_web_registered_id(self, host_name, host_uuid):
        register_config = self.get_register_config()
        register_type = register_config['type']
        if "stage" in register_type:
            registered_id = self.stage_consumer_uuid(self.ssh_host(), register_config, host_name, host_uuid)
        if "satellite" in register_type:
            registered_id = self.satellite_host_id(self.ssh_host(), register_config, host_name, host_uuid)
        if registered_id is None or registered_id == "" or registered_id is False:
            return False
        else:
            return True

    def vw_web_host_exist(self):
        keys = {'key1':'hypervisorId', 'key2':'name'}
        hypervisorId_list = list()
        name_list = list()
        for key, value in sorted(keys.items(),key=lambda item:item[0]):
            cmd = "grep '\"%s\": \"' /var/log/rhsm/* -r" % value
            ret, output = self.runcmd(cmd, self.ssh_host(), debug=False)
            if output.strip() is not None and output.strip() != "":
                lines = output.strip().split('\n')
                if len(lines) > 0:
                    for line in lines:
                        res = re.findall(r'"%s": "(.*?)"' % value, line)
                        if len(res) > 0 and key == "key1":
                                hypervisorId_list.append(res[-1])
                        if len(res) > 0 and key == "key2":
                                name_list.append(res[-1])
        if len(hypervisorId_list) > 0 and len(name_list) > 0:
            dictionary = dict(zip(name_list, hypervisorId_list))
            for name, uuid in dictionary.items():
                if self.vw_web_registered_id(name, uuid) is False:
                    return False
        if len(hypervisorId_list) > 0 and len(name_list) == 0:
            for hypervisorId in hypervisorId_list:
                if self.vw_web_registered_id(hypervisorId, hypervisorId) is False:
                    return False
        if len(hypervisorId_list) == 0 and len(name_list) > 0:
            for name in name_list:
                if self.vw_web_registered_id(name, name) is False:
                    return False
        return True

    def vw_msg_search(self, output, msg, exp_exist=True):
        res = re.findall(msg, output, re.I)
        num = len(res)
        if num > 0 and exp_exist is True:
            logger.info("Succeeded to search, expected msg(%s) is exist(%s)" %(msg, num))
            return True
        if num > 0 and exp_exist is False:
            logger.error("Failed to search, unexpected msg(%s) is exist(%s)" %(msg, num))
            return False
        if num == 0 and exp_exist is True:
            logger.error("Failed to search, expected msg(%s) is not exist(%s)" %(msg, num))
            return False
        if num == 0 and exp_exist is False:
            logger.info("Succeeded to search, unexpected msg(%s) is not exist(%s)" %(msg, num))
            return True

    def msg_validation(self, output, msg_list, exp_exist=True):
        matched_list = list()
        for msg in msg_list:
            is_matched = ""
            if "|" in msg:
                keys = msg.split("|")
                for key in keys:
                    if len(re.findall(key, output, re.I)) > 0:
                        logger.info("Found msg: %s" % key)
                        is_matched = "Yes"
            else:
                if len(re.findall(msg, output, re.I)) > 0:
                    logger.info("Found msg: %s" % msg)
                    is_matched = "Yes"
            if is_matched == "Yes":
                matched_list.append("Yes")
            else:
                matched_list.append("No")
        if "No" in matched_list and exp_exist is True:
            logger.error("Failed to search, expected msg(%s) is not exist" % msg_list)
            return False
        if "No" in matched_list and exp_exist is False:
            logger.info("Succeeded to search, unexpected msg(%s) is not exist" % msg_list)
            return True
        if "No" not in matched_list and "Yes" in matched_list and exp_exist is True:
            logger.info("Succeeded to search, expected msg(%s) is exist" % msg_list)
            return True
        if "No" not in matched_list and "Yes" in matched_list and exp_exist is False:
            logger.error("Failed to search, unexpected msg(%s) is exist" % msg_list)
            return False

    def op_normal_value(self, data, exp_error=None, exp_thread=None, exp_send=None, \
            exp_interval=None, exp_loopnum=None, exp_looptime=None):
        '''validate thread number'''
        if exp_thread is not None:
            if data['thread_num'] == exp_thread:
                logger.info("virtwho thread number(%s) is expected" % data['thread_num'])
            else:
                logger.error("virtwho thread number(%s) is not expected" % data['thread_num'])
                return False
        '''validate error number'''
        if exp_error is not None:
            if "|" in str(exp_error):
                if str(data['error_num']) in exp_error.split('|'):
                    logger.info("virtwho error number(%s) is expected" % data['error_num'])
                else:
                    logger.error("virtwho error number(%s) is not expected" % data['error_num'])
                    return False
            elif str(exp_error) == "nonzero" or str(exp_error) == "nz":
                if str(data['error_num']) == 0:
                    logger.error("virtwho error number(%s) is not expected" % data['error_num'])
                    return False
                else:
                    logger.info("virtwho error number(%s) is expected" % data['error_num'])
            else:
                if str(data['error_num']) == str(exp_error):
                    logger.info("virtwho error number(%s) is expected" % data['error_num'])
                else:
                    logger.error("virtwho error number(%s) is not expected" % data['error_num'])
                    return False
        '''validate send number'''
        if exp_send is not None:
            if data['send_num'] == exp_send:
                logger.info("virtwho send number(%s) is expected" % data['send_num'])
            else:
                logger.error("virtwho send number(%s) is not expected" % data['send_num'])
                return False
        '''validate interval time'''
        if exp_interval is not None:
            if data['interval_time'] == exp_interval:
                logger.info("virtwho interval time(%s) is expected" % data['interval_time'])
            else:
                logger.error("virtwho interval time(%s) is not expected" % data['interval_time'])
                return False
        '''validate loop number'''
        if exp_loopnum is not None:
            if data['loop_num'] == exp_loopnum:
                logger.info("virtwho loop number(%s) is expected" % data['loop_num'])
            else:
                logger.error("virtwho loop number(%s) is not expected" % data['loop_num'])
                return False
        '''validate loop time'''
        if exp_looptime is not None:
            loop_time = data['loop_time']
            if loop_time > exp_looptime+20 or loop_time < exp_looptime-20:
                logger.error("virtwho loop time(%s) is not expected" % loop_time)
                return False
            else:
                logger.info("virtwho loop time(%s) is expected" % loop_time)
        logger.info("Finished to validate all the expected options")
        return True

    #*********************************************
    # Performance Function
    #*********************************************
    def perf_env_init(self, mode):
        server_type, server_ip, owner, env = self.vw_server_info()
        if self.system_isregister(self.ssh_host(), server_type, server_ip, mode) is False:
            self.vw_sub_register(self.ssh_host())
        if self.system_sku_unattach(self.ssh_host()) is False:
            self.vw_sub_register(self.ssh_host())
        self.vw_etc_conf_disable_all()
        self.vw_etc_sys_disable_all()
        self.vw_etc_d_delete_all()

    def perf_cpu_check(self, t1):
        while(t1.is_alive()):
            time.sleep(2)
            cmd = "ps -ef | grep virt-who -i | grep -v grep | awk '{print $2}'"
            ret, output = self.runcmd(cmd, self.ssh_host(), desc="check virt-who pid")
            if ret == 0 and output is not None and output !="":
                pids = output.strip().split('\n')
                for pid in pids:
                    cmd = "ps -p %s" %pid +" -o %cpu,%mem,pid,cmd |tail -n+2"
                    ret, output = self.runcmd(cmd, self.ssh_host(), desc="check pid's cpu and memory")
                    if ret == 0 and output.split():
                        logger.info(output)

    def perf_virtwho_start(self, interval=None, oneshot=False, debug=True):
        virtwho_conf = "/etc/virt-who.conf"
        self.vw_option_enable("[global]", virtwho_conf)
        self.vw_option_enable("debug", virtwho_conf)
        if oneshot is True:
            self.vw_option_disable("interval", virtwho_conf)
            self.vw_option_enable("oneshot", virtwho_conf)
            self.vw_option_update_value("oneshot", 'True', virtwho_conf)
            if debug is True:
                self.vw_option_update_value("debug", 'True', virtwho_conf)
            else:
                self.vw_option_update_value("debug", 'False', virtwho_conf)
            data, tty_output, rhsm_output = self.vw_start(exp_send=1, oneshot=True)
            res = self.op_normal_value(data, exp_error=0, exp_thread=0, exp_send=1)
            start_line = rhsm_output.splitlines()[0]
            end_line = rhsm_output.splitlines()[-1]
            d1 = re.findall(r"\d{2}:\d{2}:\d{2}", start_line)[0]
            d2 = re.findall(r"\d{2}:\d{2}:\d{2}", end_line)[0]
            h,m,s = d1.strip().split(":")
            s1 = int(h) * 3600 + int(m) * 60 + int(s)
            h,m,s = d2.strip().split(":")
            s2 = int(h) * 3600 + int(m) * 60 + int(s)
            oneshot_time = s2-s1
            logger.info("[Time] of oneshot: %s seconds" % oneshot_time)
        else:
            self.vw_option_disable("oneshot", virtwho_conf)
            self.vw_option_enable("interval", virtwho_conf)
            self.vw_option_update_value("interval", str(interval), virtwho_conf)
            if debug is True:
                self.vw_option_update_value("debug", 'True', virtwho_conf)
            else:
                self.vw_option_update_value("debug", 'False', virtwho_conf)
            data, tty_output, rhsm_output = self.vw_start(timeout=1200, exp_send=1, exp_loopnum=3)
            res = self.op_normal_value(data, exp_error=0, exp_thread=1, exp_send=1, exp_interval=interval, exp_loopnum=3, exp_looptime=interval)
            for line in rhsm_output.splitlines():
                if "Starting infinite loop with" in line:
                    logger.info(line)
            for line in rhsm_output.splitlines():
                if "No data to send" in line:
                    logger.info(line)
        for line in rhsm_output.splitlines():
            if "Sending updated Host-to-guest mapping to" in line:
                    logger.info(line)

    def perf_vms_add(self, mode, start, end):
        if mode == "esx":
            self.esx_vms_add(start, end)
        if mode == "rhevm":
            self.rhevm_vms_add(start, end)

    def perf_vms_del(self, mode):
        if mode == "esx":
            self.esx_vms_del()
        if mode == "rhevm":
            self.rhevm_vms_del()

    def perf_vms_check(self, mode):
        if mode == "esx":
            vm_num = len(self.esx_vms_list())
        elif mode == "rhevm":
            vm_num = len(self.rhevm_vms_list())
        else:
            vm_num = 0
        if vm_num < 900:
            new_vm = (900-vm_num)/5
            logger.info("Only %s guests ready, will add %s new guests" % (vm_num, 900-vm_num))
            self.perf_vms_add(mode, 1, new_vm+1)
        logger.info("%s guests are ready for testing" % len(self.esx_vms_list()))
