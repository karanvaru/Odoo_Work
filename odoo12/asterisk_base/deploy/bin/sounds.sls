extract_sounds_core_de:
  archive.extracted:
    - name: /var/lib/asterisk/sounds/de/
    - source: https://www.asterisksounds.org/sites/asterisksounds.org/files/sounds/de/download/asterisk-sounds-core-de-2.11.19.zip
    - user: asterisk
    - group: asterisk
    - skip_verify: true
    - enforce_toplevel: false

extract_sounds_extra_de:
  archive.extracted:
    - name: /var/lib/asterisk/sounds/de/
    - source: https://www.asterisksounds.org/sites/asterisksounds.org/files/sounds/de/download/asterisk-sounds-extra-de-2.11.19.zip
    - user: asterisk
    - group: asterisk
    - skip_verify: true
    - enforce_toplevel: false

