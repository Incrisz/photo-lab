sudo apt update && sudo apt install -y wireguard-tools



## on boyh machines, generate a private and public key pair for each machine:
mkdir -p ~/photo-lab-wg
(
  umask 077
  set -o noclobber
  wg genkey > ~/photo-lab-wg/private.key
) && wg pubkey < ~/photo-lab-wg/private.key

## setup ec2
install -d -m 700 /etc/wireguard
install -m 600 "$HOME/photo-lab-wg/private.key" /etc/wireguard/wg-photo.key

/usr/bin/wg set wg-photo listen-port 51820 \
  private-key /etc/wireguard/wg-photo.key \
  peer 'wHkvsLCdPHxI8yWYvm5xHt2iR5giOF5Uv1UJW407qQ8=' \
  allowed-ips 10.77.88.2/32

/usr/bin/wg show wg-photo

wg show wg-photo

## setup laptop
sudo ip link add wg-photo type wireguard
sudo ip addr add 10.77.88.2/24 dev wg-photo
sudo wg set wg-photo \
  private-key "$HOME/photo-lab-wg/private.key" \
  peer 'Rxddxp0SMIvU4TFNqy6Ysu6PpOx43saOqvVPx0tmLRo=' \
  allowed-ips 10.77.88.1/32 \
  endpoint 18.130.209.39:51820 \
  persistent-keepalive 25
sudo ip link set wg-photo up

ping -c 3 -W 2 10.77.88.1
sudo wg show wg-photo latest-handshakes

## run on laptop to test connection to ec2
ping -c 3 -W 2 10.77.88.1
sudo wg show wg-photo