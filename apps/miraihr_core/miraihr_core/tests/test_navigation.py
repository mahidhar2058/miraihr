import unittest

from miraihr_core.navigation import build_navigation


class TestBuildNavigation(unittest.TestCase):
	def test_employee_sees_employee_and_installed_integrations(self):
		cards = build_navigation(
			{"Employee"},
			{"frappe", "hrms", "helpdesk", "lms", "erpnext", "india_payroll"},
		)
		labels = {card["label"] for card in cards}
		self.assertIn("My Leave", labels)
		self.assertIn("Helpdesk", labels)
		self.assertIn("Learning", labels)
		self.assertNotIn("Employees", labels)
		self.assertNotIn("India Payroll", labels)

	def test_hr_sees_payroll_only_when_installed(self):
		without_payroll = build_navigation({"HR Manager"}, {"frappe", "hrms"})
		with_payroll = build_navigation(
			{"HR Manager"}, {"frappe", "hrms", "india_payroll"}
		)
		self.assertNotIn("India Payroll", {card["label"] for card in without_payroll})
		self.assertIn("India Payroll", {card["label"] for card in with_payroll})

	def test_unknown_roles_receive_no_navigation(self):
		self.assertEqual(build_navigation({"Guest"}, {"frappe", "erpnext", "helpdesk"}), [])

	def test_project_link_requires_erpnext_and_project_role(self):
		self.assertNotIn(
			"Projects",
			{card["label"] for card in build_navigation({"Employee"}, {"erpnext"})},
		)
		self.assertIn(
			"Projects",
			{card["label"] for card in build_navigation({"Projects User"}, {"erpnext"})},
		)


if __name__ == "__main__":
	unittest.main()
