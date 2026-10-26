"""Integration regression for India Payroll issue #134 at the pinned app revisions."""

from erpnext.setup.doctype.employee.test_employee import make_employee
from frappe.utils import flt
from hrms.payroll.doctype.salary_slip.test_salary_slip import make_salary_component
from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip
from hrms.payroll.doctype.salary_structure.test_salary_structure import (
	create_salary_structure_assignment,
	make_salary_structure,
)
from hrms.tests.utils import HRMSTestSuite

from india_payroll.india_payroll.esi import (
	EMPLOYEE_ESI_RATE,
	ESI_EMPLOYER_COMPONENT,
	EMPLOYER_ESI_RATE,
)
from india_payroll.install import create_esi_components

_BASIC_COMPONENT = "MiraiHR Issue 134 Basic"
_EARNINGS = [
	{
		"salary_component": _BASIC_COMPONENT,
		"abbr": "MHI134",
		"formula": "base",
		"type": "Earning",
		"amount_based_on_formula": 1,
		"depends_on_payment_days": 1,
	}
]
_MONTHLY_BASE = 19_167.0


class TestIndiaPayrollIssue134(HRMSTestSuite):
	@HRMSTestSuite.change_settings("Payroll Settings", {"enable_esic": 1})
	def test_employer_esi_uses_paid_wages_after_recalculation(self):
		"""One unpaid day from 24 must not restore the full-month employer ESI row."""
		create_esi_components()
		make_salary_component(_EARNINGS, False, ["_Test Company"])

		employee = make_employee("miraihr_issue_134@example.invalid", company="_Test Company")
		structure = make_salary_structure(
			"MiraiHR Issue 134 Salary Structure",
			"Monthly",
			company="_Test Company",
			currency="INR",
			earnings=_EARNINGS,
			deductions=[],
		)
		create_salary_structure_assignment(
			employee,
			structure.name,
			from_date="2026-04-01",
			company="_Test Company",
			base=_MONTHLY_BASE,
			currency="INR",
		)

		slip = make_salary_slip(
			structure.name,
			employee=employee,
			posting_date="2026-04-01",
		)
		slip.start_date = "2026-04-01"
		slip.end_date = "2026-04-30"
		slip.insert()

		# Match issue #134: ₹19,167 monthly wage; 23 paid days of 24 working days.
		slip.total_working_days = 24
		slip.payment_days = 23
		slip.calculate_net_pay()

		self.assertAlmostEqual(slip.gross_pay, 18_368.38, places=2)
		employee_esi = [
			row for row in slip.deductions if row.salary_component == "Employee State Insurance"
		]
		self.assertEqual(len(employee_esi), 1)
		self.assertAlmostEqual(employee_esi[0].amount, flt(slip.gross_pay * EMPLOYEE_ESI_RATE, 2), places=2)

		employer_esi = [
			row
			for row in slip.employer_contributions
			if row.salary_component == ESI_EMPLOYER_COMPONENT
		]
		self.assertEqual(len(employer_esi), 1)
		self.assertAlmostEqual(
			employer_esi[0].amount,
			flt(slip.gross_pay * EMPLOYER_ESI_RATE, 2),
			places=2,
			msg="Employer ESI must use paid wages, not the full-month Salary Structure amount",
		)
