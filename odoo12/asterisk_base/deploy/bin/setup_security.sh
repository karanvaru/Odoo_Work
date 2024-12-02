#!/bin/sh

# 24 hours expire blacklist set
export TIMEOUT=86400
# Port to be filtered
PORTS=${SECURITY_FILTER_PORTS:-5060,5061}

# Create ipsets
ipset -q list blacklist > /dev/null || ipset create blacklist hash:net counters comment --timeout $TIMEOUT
ipset -q list whitelist > /dev/null || ipset create whitelist hash:net counters comment

# Create voip chain
iptables -nL voip > /dev/null 2>&1 || iptables -N voip
# Flush first
iptables -F voip
# White lists
iptables -A voip -m set --match-set whitelist src -j ACCEPT
# Black lists
iptables -A voip -m set --match-set blacklist src -j DROP
# Scanners
iptables -A voip -p udp -m udp -m string --string "VaxSIPUserAgent" --algo bm --to 65535 -j DROP
iptables -A voip -p udp -m udp -m string --string "friendly-scanner" --algo bm --to 65535 -j DROP
iptables -A voip -p udp -m udp -m string --string "sipvicious" --algo bm --to 65535 -j DROP
iptables -A voip -p udp -m udp -m string --string "sipcli" --algo bm --to 65535 -j DROP
# Finally accept
iptables -A voip -j ACCEPT

# Check if INPUT chain has voip rule
iptables -C INPUT -p udp -m multiport --dports $PORTS -j voip > /dev/null 2>&1 || iptables -I INPUT -p udp -m multiport --dports $PORTS -j voip
