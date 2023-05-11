keepalived_install:
  file.managed:
    - name: /apps/keepalived-2.0.10.tar.gz
    - source: salt://keepalived/files/keepalived-2.0.10.tar.gz
    - user: root
    - group: root
    - mode: 644
  cmd.run:
    - name: cd /apps && tar xf keepalived-2.0.10.tar.gz && cd keepalived-2.0.10 && ./configure --prefix=/apps/keepalived && make && make install && mkdir /etc/keepalived && systemctl daemon-reload
    - require:
      - file: keepalived_install
    - unless: test -d /apps/keepalived

keepalived_config_file:
  file.managed:
    - name: /etc/keepalived/keepalived.conf
    - source: salt://keepalived/files/keepalived.conf.template
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - role: {{ salt['pillar.get']('role_id') }}
    - vir_id: {{ salt['pillar.get']('vir_id') }}
    - pri_id: {{ salt['pillar.get']('pri_id') }}

keepalived_start:
  service.running:
    - name: keepalived
    - reload: True
    - watch:
      - file: /etc/keepalived/keepalived.conf
