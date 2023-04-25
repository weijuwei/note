keepalived_install:
  file.managed:
    - name: /root/keepalived-2.0.10.tar.gz
    - source: salt://keepalived/files/keepalived-2.0.10.tar.gz
    - user: root
    - group: root
    - mode: 644
  cmd.run:
    - name: cd /root/ && tar xf keepalived-2.0.10.tar.gz && cd keepalived-2.0.10 && ./configure --prefix=/usr/local/keepalived && make && make install && mkdir /etc/keepalived && systemctl daemon-reload
    - require:
      - file: keepalived_install
    - unless: test -d /usr/local/keepalived

/etc/keepalived/keepalived.conf:
  file.managed:
    - source: salt://keepalived/files/keepalived.conf.template
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - role: {{salt['pillar.get']('role_id')}}
    - vir_id: {{salt['pillar.get']('vir_id')}}
    - pri_id: {{salt['pillar.get']('pri_id')}}

keepalived_service:
  service.running:
      - name: keepalived
      - reload: True
      - watch:
        - file: /etc/keepalived/keepalived.conf
