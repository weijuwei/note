haproxy_install:
  pkg.installed:
    - names:
      - haproxy

/etc/haproxy/haproxy.cfg:
  file.managed:
    - source: salt://haproxy/files/haproxy.cfg.template
    - user: root
    - group: root
    - mode: 644
    - require:
       - pkg: haproxy_install

haproxy_service:
  service.running:
    - name: haproxy
    - reload: True
    - require:
      - pkg: haproxy_install
    - watch:
      - file: /etc/haproxy/haproxy.cfg
