#!/usr/bin/env bash
set -Eeuo pipefail

fail() {
	echo "PREFLIGHT FAILED: $*" >&2
	exit 1
}

require_command() {
	command -v "$1" >/dev/null 2>&1 || fail "required command '$1' is missing"
}

for command_name in python node corepack yarn redis-server redis-cli mariadb bench pkg-config dpkg-query git curl jq openssl; do
	require_command "$command_name"
done

python_version="$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
python -c 'import sys; sys.version_info[:2] == (3, 14) or sys.exit(1)' \
	|| fail "Python 3.14 is required, found $python_version"
echo "Python: $python_version"

node_version="$(node --version)"
[[ "$(node -p 'process.versions.node.split(".")[0]')" == "24" ]] \
	|| fail "Node.js 24 is required, found $node_version"
echo "Node.js: $node_version"

yarn_version="$(yarn --version)"
[[ "$yarn_version" == "1.22.22" ]] \
	|| fail "Yarn 1.22.22 is required, found $yarn_version"
echo "Yarn: $yarn_version"

redis_version="$(redis-server --version)" \
	|| fail "redis-server is required by Bench during bench init"
echo "Redis executable: $redis_version"
redis_ready=false
for attempt in $(seq 1 20); do
	if redis-cli -h 127.0.0.1 -p 6379 ping 2>/dev/null | grep -qx PONG; then
		redis_ready=true
		break
	fi
	sleep 1
done
[[ "$redis_ready" == "true" ]] \
	|| fail "Redis service at 127.0.0.1:6379 did not answer PING"

echo "MariaDB client: $(mariadb --version)"
bench_version="$(bench --version)" \
	|| fail "Frappe Bench CLI is unavailable"
[[ "$bench_version" == *"5.31.1"* ]] \
	|| fail "expected frappe-bench 5.31.1, found '$bench_version'"
bench_package_version="$(python -c 'from importlib.metadata import version; print(version("frappe-bench"))')" \
	|| fail "frappe-bench distribution metadata is unavailable"
[[ "$bench_package_version" == "5.31.1" ]] \
	|| fail "expected frappe-bench package 5.31.1, found '$bench_package_version'"
echo "Bench: $bench_version (package $bench_package_version)"

for package in \
	build-essential curl git jq libbz2-dev libcairo2-dev libffi-dev \
	libfontconfig1 libfreetype6-dev libjpeg-dev libkrb5-dev liblcms2-dev \
	libldap2-dev libmariadb-dev libmariadb-dev-compat libopenjp2-7-dev \
	libpq-dev libsasl2-dev libssl-dev libtiff-dev libwebp-dev libxml2-dev \
	libxslt1-dev mariadb-client openssl pkg-config python3-dev redis-server \
	redis-tools xvfb zlib1g-dev; do
	status="$(dpkg-query -W -f='${db:Status-Status}' "$package" 2>/dev/null || true)"
	[[ "$status" == "installed" ]] || fail "required system package '$package' is not installed"
done

pkg-config --exists libmariadb \
	|| fail "MariaDB development library is unavailable through pkg-config"
pkg-config --exists cairo \
	|| fail "Cairo development library is unavailable through pkg-config"
echo "System package and library preflight: PASS"
