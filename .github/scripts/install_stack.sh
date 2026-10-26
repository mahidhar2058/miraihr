#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
LOCK_FILE="$ROOT_DIR/deployment/dependencies.lock.json"
BENCH_DIR="${RUNNER_TEMP:?RUNNER_TEMP is required}/miraihr-bench"
SITE_NAME="${SITE_NAME:-ci.localhost}"
ARTIFACT_DIR="$ROOT_DIR/artifacts"
mkdir -p "$ARTIFACT_DIR"
FRAPPE_ADMIN_PASSWORD="$(openssl rand -hex 24)"
export FRAPPE_ADMIN_PASSWORD
printf 'Generated a unique disposable site administrator password for this run.\n' \
	> "$ARTIFACT_DIR/credential-generation.txt"

run_logged() {
	local name="$1"
	shift
	"$@" 2>&1 | tee -a "$ARTIFACT_DIR/${name}.log"
}

lock_value() {
	jq -er --arg app "$1" --arg key "$2" \
		'.applications[] | select(.name == $app) | .[$key]' "$LOCK_FILE"
}

lock_bootstrap_ref() {
	jq -er --arg app "$1" \
		'.applications[] | select(.name == $app) | (.bootstrap_ref // .ref)' "$LOCK_FILE"
}

checkout_locked_app() {
	local name="$1"
	local path="$BENCH_DIR/apps/$name"
	local expected
	expected="$(lock_value "$name" commit)"
	if [[ ! -d "$path/.git" ]]; then
		echo "Expected Bench source checkout at $path" >&2
		return 1
	fi
	local remote
	remote="$(git -C "$path" remote | head -n 1)"
	if [[ -z "$remote" ]]; then
		echo "$name: Bench checkout has no Git remote from which to fetch locked commit $expected" >&2
		return 1
	fi
	git -C "$path" fetch --quiet --depth=1 "$remote" "$expected"
	git -C "$path" checkout --quiet --detach "$expected"
	local actual
	actual="$(git -C "$path" rev-parse HEAD)"
	if [[ "$actual" != "$expected" ]]; then
		echo "$name: expected $expected, got $actual" >&2
		return 1
	fi
	printf '%s %s\n' "$name" "$actual" | tee -a "$ARTIFACT_DIR/installed-revisions.txt"
}

get_app_at_ref() {
	local name="$1"
	local repo
	local ref
	repo="$(lock_value "$name" repository)"
	ref="$(lock_bootstrap_ref "$name")"
	bench get-app --branch "$ref" --skip-assets "$repo"
	checkout_locked_app "$name"
}

echo "Bench version: $(bench --version)"
echo "Python version: $(python --version)"
echo "Node version: $(node --version)"

FRAPPE_REPO="$(lock_value frappe repository)"
FRAPPE_REF="$(lock_value frappe ref)"
FRAPPE_SHA="$(lock_value frappe commit)"

run_logged frappe-init bench init \
	--frappe-path "$FRAPPE_REPO" \
	--frappe-branch "$FRAPPE_REF" \
	--python "$(command -v python)" \
	--skip-assets \
	--no-procfile \
	--no-backups \
	"$BENCH_DIR"

checkout_locked_app frappe

cd "$BENCH_DIR"
for app in erpnext hrms india_payroll telephony helpdesk payments lms; do
	run_logged "get-${app}" get_app_at_ref "$app"
done

CORE_PATH="$BENCH_DIR/apps/miraihr_core"
ln -s "$ROOT_DIR/apps/miraihr_core" "$CORE_PATH"
printf '%s\n' miraihr_core >> "$BENCH_DIR/sites/apps.txt"
"$BENCH_DIR/env/bin/pip" install --quiet --editable "$CORE_PATH"

run_logged setup-requirements bench setup requirements
run_logged build-assets bench build

bench set-config -g db_host 127.0.0.1
bench set-config -gp db_port 3306
bench set-config -g redis_cache redis://127.0.0.1:6379
bench set-config -g redis_queue redis://127.0.0.1:6379
bench set-config -g redis_socketio redis://127.0.0.1:6379
bench set-config -gp socketio_port 9000

run_logged create-site bench new-site "$SITE_NAME" \
	--admin-password "${FRAPPE_ADMIN_PASSWORD:?FRAPPE_ADMIN_PASSWORD is required}" \
	--db-root-username root \
	--db-root-password "${MARIADB_ROOT_PASSWORD:?MARIADB_ROOT_PASSWORD is required}" \
	--mariadb-user-host-login-scope='%'
bench use "$SITE_NAME"

for app in erpnext hrms india_payroll telephony helpdesk payments lms miraihr_core; do
	run_logged "install-${app}" bench --site "$SITE_NAME" install-app "$app"
done

run_logged migrate bench --site "$SITE_NAME" migrate
run_logged versions bench version --format plain

"$BENCH_DIR/env/bin/pip" install --quiet pip-licenses==5.0.0
export BENCH_PATH
export SITE_NAME
export ARTIFACT_DIR
BENCH_PATH="$BENCH_DIR" "$BENCH_DIR/env/bin/python" \
	"$ROOT_DIR/.github/scripts/validate_site.py" \
	2>&1 | tee "$ARTIFACT_DIR/site-smoke.log"

bench serve --port 8000 --noreload > "$ARTIFACT_DIR/bench-serve.log" 2>&1 &
WEB_PID=$!
trap 'kill "$WEB_PID" 2>/dev/null || true' EXIT
for attempt in $(seq 1 60); do
	if curl --silent --fail --header "Host: $SITE_NAME" \
		http://127.0.0.1:8000/login \
		--output "$ARTIFACT_DIR/login.html"; then
		break
	fi
	sleep 2
done
if [[ ! -s "$ARTIFACT_DIR/login.html" ]]; then
	echo "Frappe login route did not return a non-empty page." >&2
	exit 1
fi
grep -Fq 'MiraiHR' "$ARTIFACT_DIR/login.html"
grep -Fq '/assets/miraihr_core/images/miraihr-mark.svg' "$ARTIFACT_DIR/login.html"

curl --silent --show-error --fail \
	--header "Host: $SITE_NAME" \
	--dump-header "$ARTIFACT_DIR/logo-headers.txt" \
	--output "$ARTIFACT_DIR/miraihr-mark.svg" \
	http://127.0.0.1:8000/assets/miraihr_core/images/miraihr-mark.svg
grep -Eiq '^content-type: image/svg\+xml' "$ARTIFACT_DIR/logo-headers.txt"
grep -Fq '<svg' "$ARTIFACT_DIR/miraihr-mark.svg"

curl --silent --show-error --fail \
	--header "Host: $SITE_NAME" \
	--output "$ARTIFACT_DIR/miraihr.css" \
	http://127.0.0.1:8000/assets/miraihr_core/css/miraihr.css
grep -Eq '\.navbar-brand \.app-logo|\.page-card-head \.app-logo' \
	"$ARTIFACT_DIR/miraihr.css"

THEME_URL="$(jq -er '.native_branding.theme_url' "$ARTIFACT_DIR/site-branding-smoke.json")"
curl --silent --show-error --fail \
	--header "Host: $SITE_NAME" \
	--output "$ARTIFACT_DIR/miraihr-website-theme.css" \
	"http://127.0.0.1:8000${THEME_URL}"
grep -Fq '#168b83' "$ARTIFACT_DIR/miraihr-website-theme.css"
kill "$WEB_PID"
wait "$WEB_PID" 2>/dev/null || true
trap - EXIT

TEST_RESULTS="$ARTIFACT_DIR/app-test-results.tsv"
: > "$TEST_RESULTS"
TEST_FAILURE_COUNT=0
for app in frappe erpnext hrms india_payroll telephony helpdesk payments lms miraihr_core; do
	if run_logged "tests-${app}" bench --site "$SITE_NAME" run-tests --app "$app"; then
		printf '%s\tPASS\n' "$app" >> "$TEST_RESULTS"
	else
		printf '%s\tFAIL\n' "$app" >> "$TEST_RESULTS"
		TEST_FAILURE_COUNT=$((TEST_FAILURE_COUNT + 1))
	fi
done

PAYROLL_FIXTURE="$ROOT_DIR/apps/miraihr_core/miraihr_core/tests/test_india_payroll_issue_134.py"
PAYROLL_FIXTURE_STATUS="BLOCKED"
if [[ -f "$PAYROLL_FIXTURE" ]]; then
	if run_logged payroll-issue-134 bench --site "$SITE_NAME" run-tests \
		--module miraihr_core.tests.test_india_payroll_issue_134; then
		PAYROLL_FIXTURE_STATUS="PASS"
	else
		PAYROLL_FIXTURE_STATUS="FAIL"
	fi
	if [[ "$PAYROLL_FIXTURE_STATUS" == "PASS" ]]; then
		cat > "$ARTIFACT_DIR/payroll-issue-134-status.json" <<'JSON'
{
  "issue": "https://github.com/frappe/india-payroll/issues/134",
  "status": "PASS",
  "fixture": "apps/miraihr_core/miraihr_core/tests/test_india_payroll_issue_134.py",
  "expected": {
    "gross_pay_inr": 18368.38,
    "employee_esi_inr": 137.76,
    "employer_esi_inr": 596.97,
    "reported_overwritten_employer_esi_inr": 622.93
  }
}
JSON
	else
		cat > "$ARTIFACT_DIR/payroll-issue-134-status.json" <<'JSON'
{
  "issue": "https://github.com/frappe/india-payroll/issues/134",
  "status": "FAIL",
  "fixture": "apps/miraihr_core/miraihr_core/tests/test_india_payroll_issue_134.py",
  "reason": "The focused synthetic payroll regression command failed; see payroll-issue-134.log."
}
JSON
	fi
else
	TEST_FAILURE_COUNT=$((TEST_FAILURE_COUNT + 1))
	cat > "$ARTIFACT_DIR/payroll-issue-134-status.json" <<'JSON'
{
  "issue": "https://github.com/frappe/india-payroll/issues/134",
  "status": "BLOCKED",
  "reason": "No reviewed synthetic regression fixture is present in the repository. The upstream India Payroll suite is not proof that this issue is fixed."
}
JSON
fi
if [[ "$PAYROLL_FIXTURE_STATUS" == "FAIL" ]]; then
	TEST_FAILURE_COUNT=$((TEST_FAILURE_COUNT + 1))
fi

python - "$TEST_RESULTS" "$ARTIFACT_DIR/app-test-results.json" <<'PY'
import json
import sys
from pathlib import Path

records = []
for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    app, status = line.split("\t", 1)
    records.append({"app": app, "status": status})
Path(sys.argv[2]).write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
PY

"$BENCH_DIR/env/bin/pip-licenses" --format=json \
	> "$ARTIFACT_DIR/python-license-inventory.json"
"$BENCH_DIR/env/bin/pip" freeze \
	| grep -E '^[A-Za-z0-9_.-]+==' \
	> "$ARTIFACT_DIR/python-requirements-scan.txt"

if [[ "$TEST_FAILURE_COUNT" -gt 0 ]]; then
	if [[ "$PAYROLL_FIXTURE_STATUS" == "FAIL" ]]; then
		echo "${TEST_FAILURE_COUNT} application/regression test command(s) failed, including the focused issue #134 regression test; see app-test-results.json and payroll-issue-134-status.json." >&2
	elif [[ "$PAYROLL_FIXTURE_STATUS" == "BLOCKED" ]]; then
		echo "${TEST_FAILURE_COUNT} application/regression test command(s) failed or the focused issue #134 gate is blocked because its fixture is missing; see app-test-results.json and payroll-issue-134-status.json." >&2
	else
		echo "${TEST_FAILURE_COUNT} application test command(s) failed; see app-test-results.json." >&2
	fi
	exit 1
fi
echo "PASS: pinned upstream apps installed, migrated, and app test commands completed, including issue #134 regression fixture."
