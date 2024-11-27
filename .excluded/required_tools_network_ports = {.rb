required_tools_network_ports = {
    # wireshark pur lire des fichiers
    "rustscan":      (modules.exec.tools_ext.rustscan_tool,       (resources_dir,                                 ip_address)),
}

required_tools_network_services = {
    "nmap":          (modules.exec.tools_ext.nmap_tool,           (resources_dir, url, current_user,              ip_address, os_user)),
    "enum4linux-ng": (modules.exec.tools_ext.enum4linux_ng_tool,  (resources_dir,                                 ip_address)),      
}

required_tools_web = {
    "vhosts":        (modules.exec.tools_ext.vhosts_tool,         (resources_dir, url,                            fuzzwordlistdns)),
    "sousdomaines":  (modules.exec.tools_ext.sousdomaines_tool,   (resources_dir, url,               domain_name, fuzzwordlistdns)),
    "feroxbuster":   (modules.exec.tools_ext.feroxbuster_tool,    (resources_dir, url,               domain_name, fuzzwordlistdir)),
    "hakrawler":     (modules.exec.tools_ext.hakrawler_tool,      (resources_dir, url )),
    "wafw00f":       (modules.exec.tools_ext.wafw00f_tool,        (resources_dir, url )),
    "whatweb":       (modules.exec.tools_ext.whatweb_tool,        (resources_dir, url )),
    "nikto":         (modules.exec.tools_ext.nikto_tool,          (resources_dir, url )),
    "wapiti":        (modules.exec.tools_ext.wapiti_tool,         (resources_dir, url )),
    "nuclei":        (modules.exec.tools_ext.nuclei_tool,         (resources_dir, url )),       
}

required_tools_web_advanced = {
    "download_urls": (modules.exec.tools_ext.download_urls_tool,  (      resources_dir, current_user)),
    # CMS https://github.com/wpscanteam/wpscan https://github.com/fgeek/pyfiscan
    # secret dans le code source https://github.com/Yelp/detect-secrets
    # "burp":          (tools_ext.burp_tool,           (url, resources_dir, current_user, groupname,              fuzzwordlistdns)),
    # hydra et john
    # sqli SQLMAP
    # "arjun":         (tools_ext.arjun_tool,          (url, resources_dir )),
    # "sstimap":       (tools_ext.sstimap_tool,        (url, resources_dir )),
    # "dalfox":        (tools_ext.dalfox_tool,         (url, resources_dir )),
    # humble pour les en têtes HTTP
    # Bypass-403
    # LFI https://github.com/mzfr/liffy
    # cors : https://github.com/s0md3v/Corsy
    # crlf https://github.com/Raghavd3v/CRLFsuite
    # CSRF/XSRF https://github.com/0xInfection/XSRFProbe
    # Command injection : https://github.com/commixproject/commix
    # SSRF SSRFmap https://github.com/swisskyrepo/SSRFmap
    # XSS Strike https://github.com/s0md3v/XSStrike
    # cookeflask décodeur
    # go-jwt-cracker
    # FUXPLOIDER
    # UPLOAD_BYPASS V2
    # CRLFUZZ
    # bfac https://github.com/mazen160/bfac pour les backups
    # PDF info https://github.com/py-pdf/pypdf

}

required_tools_os_linux = {
    #"linpeas":       (tools_ext.burp_tool,           (url, resources_dir, current_user, groupname,              fuzzwordlistdns)),
    # linpeas https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS
    # pwncat https://github.com/calebstewart/pwncat/tree/master
    # revshellgen https://github.com/t0thkr1s/revshellgen à valider avant
    # https://github.com/t3l3machus/Villain
    #  pspy
}

    ###############
    # candidat :
    # PHP Cookie Stealer
    # stagano : zteghide ztegseek